"""SPDX-License-Identifier: MIT. Worlds from the state alone: checks for Theorem 7 in ctc/THEOREMS.md.

  Lemma 7.1  a rule that depends only on the state at the outside slice and never signals can
             depend on that state only through the input's reduced state rho_A (Uhlmann);
  Theorem 7  worlds = eigenvectors of rho_A (basis-averaged where the spectrum is degenerate).

It settles the weak-record choice of 4c (the eigenbasis rule) and covers interactions that read no
basis (the open premise of 4b). The pointer rule of Theorem 4 is the history-dependent alternative:
two preparations that end in the same global state can get different predictions.

Run from the repository root:  python -B ctc/tests/test_worlds.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from models import partial_trace_operator_loop  # noqa: E402
from past_preserving import apply_kraus, basis_containing, past_preserving_kraus  # noqa: E402
from records import pointer_basis, pointer_blocks, state_world_kraus, world_kraus, world_vectors  # noqa: E402
from test_readouts import alice_channel, embed, marginal, outside_measurement  # noqa: E402

RNG = np.random.default_rng(707)
ATOL = 1e-9
S = 1 / np.sqrt(2)
H = np.array([[S, S], [S, -S]], complex)
CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], complex)   # also the one_way loop
ERASER = np.diag([1, 1, 1, 1j]).astype(complex)
X_READ = np.kron(np.outer(H[:, 0], H[:, 0]), np.eye(2)) + np.kron(np.outer(H[:, 1], H[:, 1]), np.array([[0, 1], [1, 0]]))


def random_unitary(d):
    z = RNG.normal(size=(d, d)) + 1j * RNG.normal(size=(d, d))
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / abs(np.diag(r)))


def random_pure(d):
    v = RNG.normal(size=d) + 1j * RNG.normal(size=d)
    return v / np.linalg.norm(v)


def dm(v):
    return np.outer(v, v.conj())


def state_rule(U, d_cr, d_loop, rho, dims, **kw):
    """Apply the state-based rule to subsystem 0 of a joint state."""
    kraus = state_world_kraus(U, d_cr, d_loop, marginal(rho, dims, [0]), **kw)
    return alice_channel(kraus, rho, dims)


class StateCompleteness(unittest.TestCase):
    """Lemma 7.1: the same global state must get the same prediction."""

    def setUp(self):
        self.dims = [2, 2]
        self.z_history = dm(CNOT @ np.kron(H[:, 0], [1, 0]))                     # CNOT reads |+> in Z
        x = X_READ @ np.kron([1, 0], [1, 0])                                     # X-readout of |0>
        self.x_history = dm(np.kron(np.eye(2), H) @ x)                           # then Bob applies a Hadamard

    def test_two_histories_end_in_the_same_global_state(self):
        np.testing.assert_allclose(self.z_history, self.x_history, atol=ATOL)

    def test_pointer_rule_predicts_differently_for_the_same_state(self):
        z = marginal(alice_channel(past_preserving_kraus(CNOT, 2, 2, np.eye(2)), self.z_history, self.dims), self.dims, [0])
        x = marginal(alice_channel(past_preserving_kraus(CNOT, 2, 2, H), self.x_history, self.dims), self.dims, [0])
        self.assertAlmostEqual(z[0, 0].real, 0.5, delta=ATOL)                   # world a = 1 is a paradox world
        self.assertAlmostEqual(x[0, 0].real, 1.0, delta=ATOL)                   # both X worlds go to |0>

    def test_state_rule_predicts_the_same(self):
        a = state_rule(CNOT, 2, 2, self.z_history, self.dims)
        b = state_rule(CNOT, 2, 2, self.x_history, self.dims)
        np.testing.assert_allclose(a, b, atol=ATOL)

    def test_purifications_differ_only_by_an_outside_unitary(self):
        """Uhlmann: any two purifications of rho_A are related by a unitary on the outside, so a rule
        that told them apart would let the outside party signal by applying it."""
        for _ in range(5):
            psi = random_pure(6)                                                 # A (2) x outside (3)
            Vb = random_unitary(3)
            phi = np.kron(np.eye(2), Vb) @ psi
            np.testing.assert_allclose(marginal(dm(psi), [2, 3], [0]), marginal(dm(phi), [2, 3], [0]), atol=ATOL)
            U = random_unitary(4)
            a = marginal(state_rule(U, 2, 2, dm(psi), [2, 3]), [2, 3], [0])
            b = marginal(state_rule(U, 2, 2, dm(phi), [2, 3]), [2, 3], [0])
            np.testing.assert_allclose(a, b, atol=1e-6)


class NonReadoutInteractions(unittest.TestCase):
    """The open premise of 4b: interactions that read no basis."""

    def cases(self):
        for d_a, d_o in ((2, 2), (2, 3), (3, 2)):
            for _ in range(4):
                V = random_unitary(d_a * d_o)
                self.assertIsNone(pointer_basis(V, d_a, d_o))
                o = np.zeros(d_o, complex)
                o[0] = 1
                yield d_a, d_o, dm(V @ np.kron(random_pure(d_a), o)), random_unitary(d_a * 2)

    def test_no_signalling_in_either_direction(self):
        for d_a, d_o, rho, U in self.cases():
            dims = [d_a, d_o]
            out = state_rule(U, d_a, 2, rho, dims)
            np.testing.assert_allclose(marginal(out, dims, [1]), marginal(rho, dims, [1]), atol=1e-6)
            alice = marginal(out, dims, [0])
            for op in ('unitary', 'measure'):
                if op == 'unitary':
                    W = embed(random_unitary(d_o), [1], dims)
                    pre = W @ rho @ W.conj().T
                else:
                    pre = outside_measurement(rho, dims, 1, random_unitary(d_o))
                np.testing.assert_allclose(marginal(state_rule(U, d_a, 2, pre, dims), dims, [0]), alice, atol=1e-6)

    def test_pctc_on_whatever_a_holds_signals(self):
        """The 4b premise counterexample, now with a random interaction: P-CTC applied to A's part of
        the joint state changes the outside's statistics."""
        worst = 0
        for d_a, d_o, rho, U in self.cases():
            dims = [d_a, d_o]
            C = embed(partial_trace_operator_loop(U, d_a, 2), [0], dims)
            out = C @ rho @ C.conj().T
            out = out / np.trace(out).real
            worst = max(worst, np.abs(marginal(out, dims, [1]) - marginal(rho, dims, [1])).max())
        self.assertGreater(worst, 1e-2)


class Limits(unittest.TestCase):
    def test_fresh_pure_input_gives_pctc(self):
        for _ in range(5):
            psi, U = random_pure(3), random_unitary(6)
            out = apply_kraus(state_world_kraus(U, 3, 2, dm(psi)), dm(psi))
            C = partial_trace_operator_loop(U, 3, 2)
            w = C @ psi
            np.testing.assert_allclose(out, dm(w / np.linalg.norm(w)), atol=1e-8)

    def test_perfect_readout_with_distinct_weights_equals_theorem_4(self):
        for _ in range(5):
            psi, U = random_pure(2), random_unitary(4)
            rho = dm(CNOT @ np.kron(psi, [1, 0]))
            a = state_rule(U, 2, 2, rho, [2, 2])
            b = alice_channel(past_preserving_kraus(U, 2, 2, pointer_basis(CNOT, 2, 2)), rho, [2, 2])
            np.testing.assert_allclose(a, b, atol=1e-8)

    def test_coarse_readout_with_distinct_block_weights_equals_4b(self):
        """Readout of a qutrit into blocks {0} vs {1, 2}: the eigenvectors are |0> and the projected state."""
        V = np.zeros((6, 6), complex)
        for k in range(3):
            flip = np.array([[0, 1], [1, 0]]) if k else np.eye(2)
            V[2 * k:2 * k + 2, 2 * k:2 * k + 2] = flip
        for _ in range(5):
            psi = random_pure(3)
            rho = dm(V @ np.kron(psi, [1, 0]))
            U = random_unitary(6)
            blocks = pointer_blocks(V, 3, 2)
            a = state_rule(U, 3, 2, rho, [3, 2])
            b = alice_channel(world_kraus(U, 3, 2, world_vectors(blocks, psi)), rho, [3, 2])
            np.testing.assert_allclose(a, b, atol=1e-8)

    def test_weak_records_follow_the_eigenbasis_row_of_4c(self):
        th = 2 * np.arcsin(np.sqrt(0.3))
        psi = np.array([np.cos(th / 2), np.sin(th / 2)], complex)
        expected = {1.0: 0.176, 0.995: 0.177, 0.825: 0.184, 0.540: 0.209, 0.0: 0.300}
        for c, p1 in expected.items():
            theta = 2 * np.arccos(c)
            cs, sn = np.cos(theta / 2), np.sin(theta / 2)
            V = np.kron(np.diag([1, 0]), np.eye(2)) + np.kron(np.diag([0, 1]), np.array([[cs, -sn], [sn, cs]]))
            rho = dm(V @ np.kron(psi, [1, 0]))
            got = marginal(state_rule(ERASER, 2, 2, rho, [2, 2]), [2, 2], [0])[1, 1].real
            self.assertAlmostEqual(got, p1, delta=1.5e-3)


class DegenerateSpectra(unittest.TestCase):
    def test_bell_pair_into_the_one_way_loop(self):
        """Theorem 4's flagship case: CNOT reads |+> in Z, so rho_A = 1/2. The pointer rule keeps the
        a = 1 world (a paradox world) and gives P(a = 0) = 0.5; the state rule averages over all bases
        and every world goes to |0>: P(a = 0) = 1. Bob's statistics stay 0.5 either way."""
        rho = dm(CNOT @ np.kron(H[:, 0], [1, 0]))
        out = state_rule(CNOT, 2, 2, rho, [2, 2])
        self.assertAlmostEqual(marginal(out, [2, 2], [0])[0, 0].real, 1.0, delta=1e-9)
        np.testing.assert_allclose(marginal(out, [2, 2], [1]), np.eye(2) / 2, atol=1e-9)

    def test_basis_average_converges(self):
        rho = dm(CNOT @ np.kron(H[:, 0], [1, 0]))
        a = state_rule(ERASER, 2, 2, rho, [2, 2], n_bases=300)
        b = state_rule(ERASER, 2, 2, rho, [2, 2], n_bases=1500)
        self.assertLess(np.abs(a - b).max(), 2e-3)



class EarlierResultsUnderTheorem7(unittest.TestCase):
    """The recheck asked for in THEOREMS.md, Theorem 7: results first computed with the pointer rule on inputs
    whose reduced state is degenerate (Alice's a is half of |Phi+>)."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(HERE.parent / 'timeless'))
        global bob_and_alice, random_spacetimes, time_machine, lin, outside_deviation
        from lightcone import bob_and_alice, random_spacetimes  # noqa: F401
        from wormhole import time_machine  # noqa: F401
        import test_operation_linearity as lin  # noqa: F401
        from test_lightcone import outside_deviation  # noqa: F401

    def alice_and_bob(self, s, definition):
        h = s.history('pps', s.protected(definition))
        return s.prob(h, 'a'), s.prob(h, 'log'), s.prob(h, 'rec_b')

    def test_light_cone_and_wormhole_refusal_loop(self):
        """Bob's record stays 0.5 under both rules; Alice's side changes from (0.5, 0.25) to (2 ln 2 - 1, 1 - ln 2)."""
        for s in (bob_and_alice(loop='refusal'), time_machine(loop='refusal')):
            a4, log4, b4 = self.alice_and_bob(s, 'theorem4')
            a7, log7, b7 = self.alice_and_bob(s, 'theorem7')
            self.assertAlmostEqual(b4, 0.5, delta=1e-9)
            self.assertAlmostEqual(b7, 0.5, delta=1e-9)
            self.assertAlmostEqual(a4, 0.5, delta=1e-9)
            self.assertAlmostEqual(log4, 0.25, delta=1e-9)
            self.assertAlmostEqual(a7, 2 * np.log(2) - 1, delta=1e-3)
            self.assertAlmostEqual(log7, 1 - np.log(2), delta=1e-3)

    def test_theorem5_holds_under_the_state_rule(self):
        rng = np.random.default_rng(5)
        for s in random_spacetimes(1, 6):
            cuts = s.sample_cuts(rng, 2)
            ref = {c: s.red(s.history('no_loop', cuts=cuts), c, s.outside_future(c)) for c in cuts}
            self.assertLess(outside_deviation(s, s.history('pps', s.protected('theorem7'), cuts=cuts), ref, cuts), 1e-9)

    def linearity_gaps(self, p, notebook, n_bases=240, pairs=2):
        t = lin.LinearityInTheLoopsOperation()
        t.setUp()
        t.pairs, t.P = t.pairs[:pairs], p

        def out(s, rule, regs):
            hist = s.history(rule, s.theorem7_split(n_bases=n_bases)) if rule == 'pps' else s.history(rule)
            return s.red(hist, s.final_cut, regs)
        saved, lin.output = lin.output, out
        try:
            return t.mixture_gap('pps', notebook)
        finally:
            lin.output = saved

    def test_linearity_conclusions_survive_except_for_a_fair_recorded_coin(self):
        """Recorded coin with P(c = 0) = 0.3: linear (the residual is the basis-average discretization). Unrecorded
        coin: not linear. New: a recorded coin with P(c = 0) = 1/2 makes the inputs' spectrum fully degenerate, the
        state rule no longer splits on the coin, and linearity fails, a jump at p = 1/2."""
        self.assertLess(max(self.linearity_gaps(0.3, True)), 1e-3)
        self.assertGreater(min(self.linearity_gaps(0.3, False)), 1e-2)
        self.assertGreater(min(self.linearity_gaps(0.5, True)), 1e-2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
