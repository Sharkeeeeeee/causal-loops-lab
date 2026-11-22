"""SPDX-License-Identifier: MIT. Numerical checks of the theorems in ctc/THEOREMS.md.

Each test checks one theorem on many random circuits, using classical enumeration of
histories as an independent route wherever possible.

Run from the repository root:  python -B ctc/tests/test_theorems.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import d_ctc_fixed_point, no_loop, p_ctc, partial_trace_operator_loop, partial_trace_state  # noqa: E402
from past_preserving import apply_kraus, past_preserving, past_preserving_kraus  # noqa: E402

ATOL = 1e-9
RNG = np.random.default_rng(2026)


def random_unitary(d):
    z = (RNG.normal(size=(d, d)) + 1j * RNG.normal(size=(d, d))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / abs(np.diag(r)))


def random_state(d):
    v = RNG.normal(size=(d, d)) + 1j * RNG.normal(size=(d, d))
    rho = v @ v.conj().T
    return rho / np.trace(rho).real


def random_permutation_circuit(d_cr, d_loop, record_message=False):
    """Classical reversible circuit as (U, f, g) with U|x,m> = |f(x,m), g(x,m)>.
    With record_message, the CR system gets an extra register r (dimension d_loop)
    and the final step copies the outgoing message into it: r -> r + m' (mod d_loop)."""
    perm = RNG.permutation(d_cr * d_loop)

    def base(x, m):
        out = perm[x * d_loop + m]
        return out // d_loop, out % d_loop

    if not record_message:
        f = lambda x, m: base(x, m)[0]  # noqa: E731
        g = lambda x, m: base(x, m)[1]  # noqa: E731
        dc = d_cr
    else:
        def f(x, m):
            a, r = divmod(x, d_loop)
            a2, m2 = base(a, m)
            return a2 * d_loop + (r + m2) % d_loop

        g = lambda x, m: base(x // d_loop, m)[1]  # noqa: E731
        dc = d_cr * d_loop
    U = np.zeros((dc * d_loop, dc * d_loop), complex)
    for x in range(dc):
        for m in range(d_loop):
            U[f(x, m) * d_loop + g(x, m), x * d_loop + m] = 1
    assert np.allclose(U.conj().T @ U, np.eye(len(U)))
    return U, f, g, dc


def consistent_messages(x, g, d_loop):
    return [m for m in range(d_loop) if g(x, m) == m]


def ket(i, d):
    v = np.zeros(d, complex)
    v[i] = 1
    return v


def projector(i, d):
    return np.outer(ket(i, d), ket(i, d))


def controlled_from_cr(V, Ws):
    """U = (V x 1) sum_k |k><k| x W_k : the CR system controls the loop, the loop never acts back."""
    d_cr, d_loop = len(Ws), len(Ws[0])
    ctrl = sum(np.kron(projector(k, d_cr), Ws[k]) for k in range(d_cr))
    return np.kron(V, np.eye(d_loop)) @ ctrl


def random_traceless_unitary(d):
    """Unitary with trace 0: W = Q diag(eigenvalues summing to 0) Q^dag."""
    if d == 2:
        phases = np.array([1, -1]) * np.exp(1j * RNG.uniform(0, 2 * np.pi))
    else:
        phases = np.exp(2j * np.pi * np.arange(d) / d) * np.exp(1j * RNG.uniform(0, 2 * np.pi))
    Q = random_unitary(d)
    return Q @ np.diag(phases) @ Q.conj().T


SIZES = [(2, 2), (4, 2), (2, 4), (4, 4), (8, 2)]


class Theorem0_NoSignalling(unittest.TestCase):
    """Past-preserving selection is a CPTP map, so it cannot signal in either direction."""

    def test_channel_and_no_signalling(self):
        for d_cr, d_loop in SIZES:
            for _ in range(4):
                U = random_unitary(d_cr * d_loop)
                basis = random_unitary(d_cr)
                kraus = past_preserving_kraus(U, d_cr, d_loop, basis)
                self.assertTrue(np.allclose(sum(K.conj().T @ K for K in kraus), np.eye(d_cr), atol=ATOL))
                rho = random_state(d_cr * 3)                     # Alice (d_cr) x Bob (3)
                out = apply_kraus(kraus, rho, d_partner=3)
                bob_before = np.einsum('aiaj->ij', rho.reshape(d_cr, 3, d_cr, 3))
                bob_after = np.einsum('aiaj->ij', out.reshape(d_cr, 3, d_cr, 3))
                self.assertTrue(np.allclose(bob_before, bob_after, atol=ATOL))


class Theorem1_Consistency(unittest.TestCase):
    """H1': in every recorded world only consistent histories occur when one exists; otherwise
    the loop sits at a Deutsch fixed point. The rule is defined for every input."""

    def test_amplitudes_count_consistent_histories(self):
        for d_cr, d_loop in SIZES:
            for _ in range(10):
                U, f, g, dc = random_permutation_circuit(d_cr, d_loop)
                C = partial_trace_operator_loop(U, dc, d_loop)
                for x in range(dc):
                    S = consistent_messages(x, g, d_loop)
                    expected = np.zeros(dc)
                    for m in S:
                        expected[f(x, m)] += 1
                    self.assertTrue(np.allclose(C[:, x], expected, atol=ATOL))   # <y|C|x> = N_xy (Lemma 1)

    def test_only_consistent_outcomes_occur(self):
        for d_cr, d_loop in SIZES:
            for _ in range(10):
                U, f, g, dc = random_permutation_circuit(d_cr, d_loop)
                for x in range(dc):
                    S = consistent_messages(x, g, d_loop)
                    out = past_preserving(U, projector(x, dc), dc, d_loop)
                    probs = np.diag(out).real
                    if S:
                        allowed = {f(x, m) for m in S}
                        for y in range(dc):
                            if y not in allowed:
                                self.assertLess(probs[y], ATOL)
                    else:
                        tau, _ = d_ctc_fixed_point(U, projector(x, dc), dc, d_loop)
                        joint = U @ np.kron(projector(x, dc), tau) @ U.conj().T
                        self.assertTrue(np.allclose(partial_trace_state(joint, dc, d_loop, 'loop'), tau,
                                                    atol=1e-8))
                    self.assertAlmostEqual(probs.sum(), 1.0, places=9)

    def test_defined_where_p_ctc_is_not(self):
        """Grandfather paradox with no failure channel: P-CTC is undefined, the rule is not."""
        U = np.zeros((4, 4), complex)
        for m in range(2):
            U[1 - m, m] = 1                # one CR state (index 0 of d_cr = 1 padded to 2), m -> NOT m
            U[2 + m, 2 + m] = 1
        rho = projector(0, 2)
        self.assertIsNone(p_ctc(U, rho, 2, 2)[0])
        out = past_preserving(U, rho, 2, 2)
        self.assertAlmostEqual(np.trace(out).real, 1.0, places=9)


class Theorem2_FutureNotPast(unittest.TestCase):
    """H2': world probabilities never change; inside each world the outcome distribution is the
    no-loop distribution conditioned on consistency (exactly, when the message is recorded)."""

    def test_past_probabilities_unchanged(self):
        for d_cr, d_loop in SIZES:
            for _ in range(5):
                U = random_unitary(d_cr * d_loop)
                p = RNG.dirichlet(np.ones(d_cr))
                kraus = past_preserving_kraus(U, d_cr, d_loop)
                for x in range(d_cr):
                    world = apply_kraus(kraus, p[x] * projector(x, d_cr))
                    self.assertAlmostEqual(np.trace(world).real, p[x], places=9)

    def test_conditioned_on_consistency_when_message_recorded(self):
        for d_cr, d_loop in SIZES:
            for _ in range(10):
                U, f, g, dc = random_permutation_circuit(d_cr, d_loop, record_message=True)
                for x in range(0, dc, d_loop):           # inputs with the record register at 0
                    S = consistent_messages(x, g, d_loop)
                    if not S:
                        continue
                    # independent route: enumerate histories with a uniformly random external message
                    p0_given_S = np.zeros(dc)
                    for m in S:
                        p0_given_S[f(x, m)] += 1 / len(S)
                    out = past_preserving(U, projector(x, dc), dc, d_loop)
                    self.assertTrue(np.allclose(np.diag(out).real, p0_given_S, atol=ATOL))
                    # and the unconditioned no-loop baseline from models.no_loop agrees with enumeration
                    base = no_loop(U, projector(x, dc), dc, d_loop, np.eye(d_loop) / d_loop)
                    p0 = np.zeros(dc)
                    for m in range(d_loop):
                        p0[f(x, m)] += 1 / d_loop
                    self.assertTrue(np.allclose(np.diag(base).real, p0, atol=ATOL))

    def test_general_amplitude_formula(self):
        """Without a record, P(y|x) = N_xy^2 / sum_y' N_xy'^2 (amplitude, not history, counting)."""
        for d_cr, d_loop in SIZES:
            for _ in range(10):
                U, f, g, dc = random_permutation_circuit(d_cr, d_loop)
                for x in range(dc):
                    S = consistent_messages(x, g, d_loop)
                    if not S:
                        continue
                    N = np.zeros(dc)
                    for m in S:
                        N[f(x, m)] += 1
                    out = past_preserving(U, projector(x, dc), dc, d_loop)
                    self.assertTrue(np.allclose(np.diag(out).real, N ** 2 / np.sum(N ** 2), atol=ATOL))


class Theorem3_CausalityRecovered(unittest.TestCase):
    """H3': if the loop never acts back on the CR system, the rule reproduces ordinary quantum
    mechanics for recorded inputs, including loops whose trace vanishes. P-CTC does not."""

    def cases(self):
        for d_cr, d_loop in SIZES:
            for _ in range(4):
                Ws = [random_unitary(d_loop) if RNG.random() < 0.5 else random_traceless_unitary(d_loop)
                      for _ in range(d_cr)]
                Ws[0] = random_traceless_unitary(d_loop)          # always include a paradox world
                yield d_cr, d_loop, random_unitary(d_cr), Ws

    def test_recorded_inputs_match_no_loop(self):
        for d_cr, d_loop, V, Ws in self.cases():
            U = controlled_from_cr(V, Ws)
            rho = np.diag(RNG.dirichlet(np.ones(d_cr))).astype(complex)
            ours = past_preserving(U, rho, d_cr, d_loop)
            for _ in range(3):
                ordinary = no_loop(U, rho, d_cr, d_loop, random_state(d_loop))
                self.assertTrue(np.allclose(ours, ordinary, atol=1e-8))

    def test_any_input_same_statistics_in_output_basis(self):
        for d_cr, d_loop, V, Ws in self.cases():
            U = controlled_from_cr(V, Ws)
            rho = random_state(d_cr)
            ours = V.conj().T @ past_preserving(U, rho, d_cr, d_loop) @ V
            ordinary = V.conj().T @ no_loop(U, rho, d_cr, d_loop, random_state(d_loop)) @ V
            self.assertTrue(np.allclose(np.diag(ours), np.diag(ordinary), atol=1e-8))

    def test_no_interaction_is_exactly_ordinary(self):
        """U = V x W, record basis = eigenbasis of rho: output V rho V^dag, even when Tr W = 0."""
        for d_cr, d_loop in SIZES:
            for traceless in (False, True):
                V = random_unitary(d_cr)
                W = random_traceless_unitary(d_loop) if traceless else random_unitary(d_loop)
                U = np.kron(V, W)
                rho = random_state(d_cr)
                _, eigvecs = np.linalg.eigh(rho)
                ours = past_preserving(U, rho, d_cr, d_loop, basis=eigvecs)
                self.assertTrue(np.allclose(ours, V @ rho @ V.conj().T, atol=1e-8))
                if traceless:
                    self.assertIsNone(p_ctc(U, rho, d_cr, d_loop)[0])

    def test_p_ctc_counterexample(self):
        """CR bit controls a NOT on the loop. The loop never touches the CR bit, yet P-CTC deletes
        the world a = 1. Past-preserving selection keeps it."""
        U = controlled_from_cr(np.eye(2), [np.eye(2), np.array([[0, 1], [1, 0]])])
        rho = np.diag([0.5, 0.5]).astype(complex)
        p_out, _ = p_ctc(U, rho, 2, 2)
        self.assertAlmostEqual(p_out[1, 1].real, 0.0, places=12)
        self.assertAlmostEqual(no_loop(U, rho, 2, 2, np.eye(2) / 2)[1, 1].real, 0.5, places=12)
        self.assertAlmostEqual(past_preserving(U, rho, 2, 2)[1, 1].real, 0.5, places=12)


if __name__ == '__main__':
    unittest.main(verbosity=1)
