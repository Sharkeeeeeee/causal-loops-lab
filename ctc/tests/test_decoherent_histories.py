"""SPDX-License-Identifier: MIT. Theorem 4's records versus Gell-Mann and Hartle's generalized records (strong decoherence).

Gell-Mann and Hartle (arXiv:1905.05859): a set of histories (chains C_a of projections at successive times) is
strongly decoherent if C_a rho = R_a rho for mutually orthogonal projections R_a, the "generalized records" (present
data fully correlated with the past). Strong decoherence implies medium and weak decoherence, so the histories
get probabilities.

Run from the repository root:  python -B ctc/tests/test_decoherent_histories.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'timeless'))
from records import pointer_basis  # noqa: E402
from lightcone import alice_alone, bob_and_alice  # noqa: E402
from paw import apply  # noqa: E402

ATOL = 1e-10
X = np.array([[0, 1], [1, 0]], complex)


def random_unitary(rng, d):
    q, r = np.linalg.qr(rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d)))
    return q * (np.diag(r) / abs(np.diag(r)))


def proj(s, q, value):
    e = np.zeros(2, complex)
    e[value] = 1
    return lambda v: apply(np.outer(e, e), [s.ix(q)], s.n, v)


def heisenberg(s, f):
    """Apply f at the outside cut (all events not in J+(M)) to a final state: undo J+(M), apply, redo."""
    fut = [k for k in s.dyn if k in s.future(s.M)]

    def g(v):
        for k in reversed(fut):
            v = s.apply_event(k, v, inverse=True)
        v = f(v)
        for k in fut:
            v = s.apply_event(k, v)
        return v
    return g


def strong_decoherence_gap(s, history_qubit, inside, records):
    """max over k, y of || Q_y P_k(entry) psi - Q_y R_k psi ||, no-loop final state psi: P_k is the Z value of
    `history_qubit` where it enters the loop region, Q_y the Z value of `inside` at the end, R_k the joint Z value
    k of the record qubits at the end. Zero means strong decoherence with those records."""
    psi = s.final
    gap = 0.0
    for k in (0, 1):
        for y in (0, 1):
            lhs = proj(s, inside, y)(heisenberg(s, proj(s, history_qubit, k))(psi))
            rhs = proj(s, inside, y)(psi)
            for r in records:
                rhs = proj(s, r, k)(rhs)
            gap = max(gap, float(np.linalg.norm(lhs - rhs)))
    return gap


class ReadoutsAreStrongDecoherence(unittest.TestCase):
    def test_a_perfect_readout_gives_strong_decoherence_for_every_input(self):
        """V = sum_k |k><k| (x) W X^k reads A in the basis {|k>} with orthogonal records W|k>. Then
        (P_k (x) 1) V |psi, 0> = (1 (x) R_k) V |psi, 0> for every psi: strong decoherence that does not depend
        on the state, which is what makes PPS a fixed channel (Theorem 4). Lemma 2 finds the same basis."""
        rng = np.random.default_rng(3)
        for _ in range(10):
            B, W = random_unitary(rng, 2), random_unitary(rng, 2)
            P = [np.outer(B[:, k], B[:, k].conj()) for k in (0, 1)]
            V = sum(np.kron(P[k], W @ np.linalg.matrix_power(X, k)) for k in (0, 1))
            R = [W @ np.diag([1 - k, k]) @ W.conj().T for k in (0, 1)]
            found = pointer_basis(V, 2, 2)
            got = sorted((np.outer(found[:, j], found[:, j].conj()) for j in (0, 1)), key=lambda M: M[0, 0].real)
            want = sorted(P, key=lambda M: M[0, 0].real)
            for a, b in zip(got, want):
                np.testing.assert_allclose(a, b, atol=1e-8)
            for _ in range(5):
                psi = rng.normal(size=2) + 1j * rng.normal(size=2)
                out = V @ np.kron(psi / np.linalg.norm(psi), [1, 0])
                for k in (0, 1):
                    np.testing.assert_allclose(np.kron(P[k], np.eye(2)) @ out, np.kron(np.eye(2), R[k]) @ out, atol=ATOL)

    def test_a_weak_record_breaks_decoherence_by_its_overlap(self):
        """Record states with overlap c. Histories 'A was k (Z), later A reads y (X)': the off-diagonal element of
        the decoherence functional is c/4, real, so the set is not even weakly decoherent unless c = 0. In Gell-Mann
        and Hartle's terms the 'past world' k then has only an approximate probability."""
        for c in (0.0, 0.3, 0.7, 1.0):
            r0, r1 = np.array([1, 0], complex), np.array([c, np.sqrt(1 - c * c)], complex)
            psi = (np.kron([1, 0], r0) + np.kron([0, 1], r1)) / np.sqrt(2)
            Z = [np.kron(np.diag([1 - k, k]), np.eye(2)) for k in (0, 1)]
            plus = np.array([1, 1]) / np.sqrt(2)
            Py = np.kron(np.outer(plus, plus), np.eye(2))
            D = psi.conj() @ (Py @ Z[1]).conj().T @ (Py @ Z[0]) @ psi
            self.assertAlmostEqual(D.real, c / 4, delta=ATOL)
            self.assertAlmostEqual(D.imag, 0.0, delta=ATOL)


class RecordsInSpacetime(unittest.TestCase):
    def test_records_outside_the_future_cone_make_the_loop_histories_strongly_decohere(self):
        """bob_and_alice: 'a had Z value k where it entered the loop region, the log reads y at the end' strongly
        decoheres with Bob's record as generalized record. Bob's record lies outside J+(M), so it commutes with
        everything inside the region's future."""
        s = bob_and_alice('refusal')
        self.assertNotIn(s.records['rec_b'], s.future(s.M))
        self.assertLess(strong_decoherence_gap(s, 'a', 'log', ['rec_b']), ATOL)

    def test_gell_mann_hartle_also_accept_records_inside_the_future_cone(self):
        """Their records may sit at any later time. A copy made after the loop counts (alice_alone 'after'), and so
        does a's own final value, since refusal never changes a's Z (no copy at all). Both lie inside J+(M);
        protecting them is the 'influence' and 'all' definitions, which allow a backward signal or switch the loop
        off. With a loop, the generalized records must be restricted to the outside of J+(M)."""
        late = alice_alone('after')
        self.assertIn(late.records['rec'], late.future(late.M))
        self.assertLess(strong_decoherence_gap(late, 'a', 'log', ['rec']), ATOL)
        alone = alice_alone(None)
        self.assertLess(strong_decoherence_gap(alone, 'a', 'log', ['a']), ATOL)

    def test_no_record_no_strong_decoherence_with_outside_records(self):
        """Without any copy, no qubit other than a itself holds k: replacing the record by the log (the only other
        qubit the region writes) fails."""
        alone = alice_alone(None)
        self.assertGreater(strong_decoherence_gap(alone, 'a', 'log', ['log']), 0.1)


if __name__ == '__main__':
    unittest.main(verbosity=1)
