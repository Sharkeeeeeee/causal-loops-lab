"""SPDX-License-Identifier: MIT. Is PPS the only rule? Checks for Theorem 6 in ctc/THEOREMS.md.

1. The conjecture of PERSPECTIVES.md 3.2 is false as stated: a "history counting" rule satisfies
   (a) CPTP, (b) unchanged record probabilities, (c) only consistent outcomes and (d) ordinary
   quantum mechanics when the loop does not act back, yet differs from PPS.
2. Theorem 6: inside a world, a rule of amplitude form psi -> L(U) psi / ||L(U) psi||, with L
   linear in U, compatible with ordinary evolution of the CR system before and after the loop,
   and invariant under relabelling the loop's states, must have L(U) = c Tr_loop U. The space of
   such L is computed numerically: it is one-dimensional, and it is spanned by the partial trace.
3. Each assumption is needed; the paradox-world fallback is the only freedom left.

Run from the repository root:  python -B ctc/tests/test_uniqueness.py
"""
from itertools import permutations
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import d_ctc, partial_trace_operator_loop  # noqa: E402
from past_preserving import apply_kraus, past_preserving_kraus  # noqa: E402

RNG = np.random.default_rng(606)
ATOL = 1e-9


def random_unitary(d):
    z = (RNG.normal(size=(d, d)) + 1j * RNG.normal(size=(d, d))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / abs(np.diag(r)))


def perm_unitary(perm):
    """Permutation matrix of a bijection on basis states: |i> -> |perm[i]>."""
    n = len(perm)
    P = np.zeros((n, n), complex)
    for i, j in enumerate(perm):
        P[j, i] = 1
    return P


def classical_circuit(f, g, d_cr, d_loop):
    """U|x, m> = |f(x,m), g(x,m)> as a matrix on CR (x) loop (CR first)."""
    perm = [f(x, m) * d_loop + g(x, m) for x in range(d_cr) for m in range(d_loop)]
    assert sorted(perm) == list(range(d_cr * d_loop)), 'not a bijection'
    return perm_unitary(perm)


def counts(U, d_cr, d_loop):
    """N[x, y] = number of consistent loop values in world x with CR output y (Lemma 1)."""
    N = np.zeros((d_cr, d_cr))
    for x in range(d_cr):
        for m in range(d_loop):
            col = U[:, x * d_loop + m]
            out = int(np.argmax(abs(col)))
            y, m_out = divmod(out, d_loop)
            if m_out == m:
                N[x, y] += 1
    return N


def history_counting_kraus(U, d_cr, d_loop):
    """The counterexample: world x outputs y with probability N_xy / sum_y N_xy (history counts,
    not squared amplitudes); in a world with no consistent history it falls back like PPS."""
    N = counts(U, d_cr, d_loop)
    kraus = []
    for x in range(d_cr):
        e = np.eye(d_cr)[:, x]
        if N[x].sum() == 0:
            sigma = d_ctc(U, np.outer(e, e), d_cr, d_loop)[0]
            lam, vecs = np.linalg.eigh((sigma + sigma.conj().T) / 2)
            kraus += [np.sqrt(v) * np.outer(s, e) for v, s in zip(lam, vecs.T) if v > 1e-12]
            continue
        for y in range(d_cr):
            if N[x, y]:
                kraus.append(np.sqrt(N[x, y] / N[x].sum()) * np.outer(np.eye(d_cr)[:, y], e))
    return kraus


def output_distribution(kraus, x, d_cr):
    e = np.eye(d_cr)[:, x]
    rho = apply_kraus(kraus, np.outer(e, e))
    return np.real(np.diag(rho))


def three_way_circuit():
    """CR bit, loop of two bits. In world x = 0 the loop values 0, 1, 2 are consistent; 0 and 1
    give CR output 0, value 2 gives output 1; value 3 is inconsistent."""
    table = {(0, 0): (0, 0), (0, 1): (0, 1), (0, 2): (1, 2), (0, 3): (1, 0),
             (1, 0): (0, 2), (1, 1): (0, 3), (1, 2): (1, 1), (1, 3): (1, 3)}
    return classical_circuit(lambda x, m: table[x, m][0], lambda x, m: table[x, m][1], 2, 4)


def random_bijection_circuit(d_cr, d_loop):
    perm = RNG.permutation(d_cr * d_loop)
    return perm_unitary(perm)


def channel_ok(kraus, d):
    return np.allclose(sum(K.conj().T @ K for K in kraus), np.eye(d), atol=ATOL)


class ConjectureAsStatedIsFalse(unittest.TestCase):
    def test_three_rules_three_answers(self):
        """World 0: PPS 4/5 (amplitudes add: 2|0> + |1>), history counting 2/3, D-CTC 3/4."""
        U = three_way_circuit()
        pps = output_distribution(past_preserving_kraus(U, 2, 4), 0, 2)
        hc = output_distribution(history_counting_kraus(U, 2, 4), 0, 2)
        e = np.eye(2)[:, 0]
        dctc = np.real(np.diag(d_ctc(U, np.outer(e, e), 2, 4)[0]))
        self.assertAlmostEqual(pps[0], 4 / 5, places=9)
        self.assertAlmostEqual(hc[0], 2 / 3, places=9)
        self.assertAlmostEqual(dctc[0], 3 / 4, places=6)

    def test_history_counting_meets_a_to_d_on_random_circuits(self):
        differs = 0
        for d_cr, d_loop, n in ((2, 2, 10), (4, 2, 10), (2, 6, 150), (3, 4, 150)):
            for _ in range(n):
                U = random_bijection_circuit(d_cr, d_loop)
                hc, pps = history_counting_kraus(U, d_cr, d_loop), past_preserving_kraus(U, d_cr, d_loop)
                # (a) linear, CPTP: hence no signalling (Theorem 0's argument)
                self.assertTrue(channel_ok(hc, d_cr))
                N = counts(U, d_cr, d_loop)
                for x in range(d_cr):
                    p = output_distribution(hc, x, d_cr)
                    # (b) the world keeps its weight: the rule is a channel applied inside world x
                    self.assertAlmostEqual(p.sum(), 1, places=9)
                    # (c) only outcomes of consistent histories, in worlds that have one
                    if N[x].sum():
                        self.assertTrue(np.all(p[N[x] == 0] < 1e-12))
                    if np.max(N[x]) > 1 and len(set(N[x][N[x] > 0])) > 1:
                        q = output_distribution(pps, x, d_cr)
                        differs += not np.allclose(p, q, atol=1e-9)
        self.assertGreater(differs, 0)

    def test_history_counting_recovers_ordinary_qm_when_the_loop_does_not_act_back(self):
        """(d): controlled form, the CR system controls the loop and is not affected by it."""
        for d_cr, d_loop in ((2, 2), (3, 2), (2, 3)):
            for _ in range(5):
                f = RNG.permutation(d_cr)
                shifts = RNG.integers(d_loop, size=d_cr)
                U = classical_circuit(lambda x, m: int(f[x]), lambda x, m: int((m + shifts[x]) % d_loop),
                                      d_cr, d_loop)
                hc = history_counting_kraus(U, d_cr, d_loop)
                for x in range(d_cr):
                    p = output_distribution(hc, x, d_cr)
                    self.assertAlmostEqual(p[f[x]], 1, places=9)


def vec_kron(A, B):
    """Matrix of X -> A X B on column-major vectors."""
    return np.kron(B.T, A)


def solution_space(d_cr, d_loop, cr_moves, loop_moves):
    """All linear L: B(CR (x) loop) -> B(CR) with L((W1 x 1) X (W2 x 1)) = W1 L(X) W2 for the given
    (W1, W2) and L((1 x V) X (1 x V^dag)) = L(X) for the given V. Returns a basis (as matrices M with
    vec L(X) = M vec X)."""
    D, dc2 = d_cr * d_loop, d_cr * d_cr
    I_l = np.eye(d_loop)
    rows = []
    for W1, W2 in cr_moves:
        K = vec_kron(np.kron(W1, I_l), np.kron(W2, I_l))
        K2 = vec_kron(W1, W2)
        rows.append(np.kron(K.T, np.eye(dc2)) - np.kron(np.eye(D * D), K2))
    for V in loop_moves:
        K = vec_kron(np.kron(np.eye(d_cr), V), np.kron(np.eye(d_cr), V.conj().T))
        rows.append(np.kron(K.T, np.eye(dc2)) - np.eye(dc2 * D * D))
    A = np.vstack(rows)
    _, s, vh = np.linalg.svd(A)
    null = vh[np.sum(s > 1e-8):].conj()
    return [n.reshape((dc2, D * D), order='F') for n in null]


def partial_trace_matrix(d_cr, d_loop):
    D = d_cr * d_loop
    M = np.zeros((d_cr * d_cr, D * D), complex)
    for j in range(D * D):
        X = np.zeros(D * D, complex)
        X[j] = 1
        M[:, j] = partial_trace_operator_loop(X.reshape((D, D), order='F'), d_cr, d_loop).reshape(-1, order='F')
    return M


def monomial(d):
    return perm_unitary(RNG.permutation(d)) @ np.diag(np.exp(2j * np.pi * RNG.random(d)))


class Theorem6_SolutionSpace(unittest.TestCase):
    def cr_moves(self, d, k=4):
        return [(random_unitary(d), random_unitary(d)) for _ in range(k)]

    def test_unique_up_to_a_constant_and_equal_to_the_partial_trace(self):
        for d_cr, d_loop in ((2, 2), (2, 3), (3, 2)):
            sols = solution_space(d_cr, d_loop, self.cr_moves(d_cr),
                                  [random_unitary(d_loop) for _ in range(4)])
            self.assertEqual(len(sols), 1)
            T = partial_trace_matrix(d_cr, d_loop)
            c = np.vdot(T, sols[0]) / np.vdot(T, T)
            self.assertLess(np.max(abs(sols[0] - c * T)), 1e-9)

    def test_relabelling_by_permutations_and_phases_is_enough(self):
        sols = solution_space(2, 3, self.cr_moves(2), [monomial(3) for _ in range(5)])
        self.assertEqual(len(sols), 1)

    def test_permutations_alone_are_not_enough(self):
        """Classical relabellings leave a second solution, the all-ones functional on the loop."""
        perms = [perm_unitary(p) for p in permutations(range(3))]
        self.assertEqual(len(solution_space(2, 3, self.cr_moves(2), perms)), 2)

    def test_without_relabelling_invariance_any_loop_functional_works(self):
        self.assertEqual(len(solution_space(2, 3, self.cr_moves(2), [])), 9)

    def test_without_composition_the_space_is_large(self):
        self.assertGreater(len(solution_space(2, 2, [], [random_unitary(2) for _ in range(4)])), 1)


class Theorem6_Consequences(unittest.TestCase):
    def test_pps_is_invariant_under_loop_relabelling_and_composes(self):
        for _ in range(10):
            U, V, W1, W2 = random_unitary(6), random_unitary(3), random_unitary(2), random_unitary(2)
            C = partial_trace_operator_loop(U, 2, 3)
            I3 = np.eye(3)
            relabelled = np.kron(np.eye(2), V) @ U @ np.kron(np.eye(2), V.conj().T)
            self.assertTrue(np.allclose(partial_trace_operator_loop(relabelled, 2, 3), C, atol=ATOL))
            composed = np.kron(W1, I3) @ U @ np.kron(W2, I3)
            self.assertTrue(np.allclose(partial_trace_operator_loop(composed, 2, 3), W1 @ C @ W2, atol=ATOL))

    def test_history_counting_breaks_relabelling_invariance(self):
        """Relabelling the loop by a Hadamard turns the three-way circuit into one with interfering
        loop amplitudes; PPS is unchanged, history counting is not even defined there."""
        U = three_way_circuit()
        H = np.kron(np.array([[1, 1], [1, -1]]) / np.sqrt(2), np.array([[1, 1], [1, -1]]) / np.sqrt(2))
        R = np.kron(np.eye(2), H) @ U @ np.kron(np.eye(2), H.conj().T)
        self.assertTrue(np.allclose(partial_trace_operator_loop(R, 2, 4), partial_trace_operator_loop(U, 2, 4)))
        self.assertGreater(np.sum(abs(R) > 1e-9), 8)        # no longer a permutation of basis states

    def test_paradox_worlds_are_the_only_freedom(self):
        """Where C|k> = 0 the axioms say nothing: two different fallbacks both give valid channels
        that agree with PPS in every other world."""
        U = classical_circuit(lambda x, m: x, lambda x, m: (m + 1) % 2 if x == 0 else m, 2, 2)  # world 0: paradox
        C = partial_trace_operator_loop(U, 2, 2)
        self.assertLess(np.linalg.norm(C[:, 0]), 1e-12)
        pps = past_preserving_kraus(U, 2, 2)
        e0, e1 = np.eye(2)
        other = [np.outer(C[:, 1] / np.linalg.norm(C[:, 1]), e1)] + [np.sqrt(0.5) * np.outer(np.eye(2)[:, y], e0)
                                                                   for y in range(2)]
        for kraus in (pps, other):
            self.assertTrue(channel_ok(kraus, 2))
            self.assertTrue(np.allclose(output_distribution(kraus, 1, 2), output_distribution(pps, 1, 2)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
