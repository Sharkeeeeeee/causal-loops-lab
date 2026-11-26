"""SPDX-License-Identifier: MIT. Theorem 3 for every U in which the loop does not affect A (THEOREMS.md, Theorem 3, Lemmas 3.1-3.2).

  Lemma 3.1  a unitary on A x L through which L cannot signal to A at all is a product V x W;
  Lemma 3.2  a unitary that never changes A's statistics in the basis {V|k>} is (V x 1) sum_k |k><k| x W_k,
             the controlled form of Theorem 3;
  inputs     with a product U, A is not an input of the loop and PPS leaves it alone, entanglement included;
             splitting it into worlds anyway would destroy that entanglement;
  caveats    (i) PPS treats the loop's own reading of A as a perfect record: joint observables that erase
             A's outside record see the difference; (ii) the controlled value must be recorded outside,
             or the loop selects it (P-CTC on a fresh input).

Run from the repository root:  python -B ctc/tests/test_theorem3_general.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from models import no_loop  # noqa: E402
from past_preserving import basis_containing, past_preserving_kraus  # noqa: E402
from records import operator_schmidt, state_world_kraus  # noqa: E402
from test_readouts import alice_channel, embed, marginal  # noqa: E402

RNG = np.random.default_rng(303)
ATOL = 1e-9
CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], complex)


def haar(d):
    z = RNG.normal(size=(d, d)) + 1j * RNG.normal(size=(d, d))
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / abs(np.diag(r)))


def pure_state(d):
    v = RNG.normal(size=d) + 1j * RNG.normal(size=d)
    v /= np.linalg.norm(v)
    return np.outer(v, v.conj())


def controlled(V, Ws):
    d = len(Ws)
    return np.kron(V, np.eye(Ws[0].shape[0])) @ sum(np.kron(np.outer(np.eye(d)[k], np.eye(d)[k]), W) for k, W in enumerate(Ws))


def a_output(U, rho, tau, d, n):
    return no_loop(U, rho, d, n, tau)


def signals_to_a(U, d, n, trials=4):
    """Largest change of A's output when the loop input changes."""
    worst = 0.0
    for _ in range(trials):
        rho = pure_state(d)
        worst = max(worst, float(np.abs(a_output(U, rho, pure_state(n), d, n) - a_output(U, rho, pure_state(n), d, n)).max()))
    return worst


class Lemma31NoSignallingMeansProduct(unittest.TestCase):
    def test_products_do_not_signal_and_everything_else_does(self):
        for d, n in ((2, 2), (2, 3), (3, 2)):
            P = np.kron(haar(d), haar(n))
            self.assertLess(signals_to_a(P, d, n), ATOL)
            self.assertEqual(len(operator_schmidt(P, d, n)[0]), 1)
            ctrl = controlled(haar(d), [haar(n) for _ in range(d)])
            self.assertGreater(signals_to_a(ctrl, d, n), 1e-3)     # phase kickback reaches A
            self.assertGreater(signals_to_a(haar(d * n), d, n), 1e-3)

    def test_heisenberg_form(self):
        """The proof's key step: for a product, U^dag (X x 1) U = (V^dag X V) x 1 for every X."""
        d, n = 3, 2
        V, W = haar(d), haar(n)
        U = np.kron(V, W)
        X = RNG.normal(size=(d, d)) + 1j * RNG.normal(size=(d, d))
        np.testing.assert_allclose(U.conj().T @ np.kron(X, np.eye(n)) @ U, np.kron(V.conj().T @ X @ V, np.eye(n)), atol=ATOL)


class Lemma32RecordPreservingMeansControlled(unittest.TestCase):
    def populations(self, U, rho, tau, V, d, n):
        out = a_output(U, rho, tau, d, n)
        return np.real(np.diag(V.conj().T @ out @ V))

    def test_controlled_form_never_changes_the_record(self):
        for d, n in ((2, 2), (3, 2), (2, 3)):
            V = haar(d)
            U = controlled(V, [haar(n) for _ in range(d)])
            for _ in range(4):
                rho, tau = pure_state(d), pure_state(n)
                np.testing.assert_allclose(self.populations(U, rho, tau, V, d, n), np.real(np.diag(rho)), atol=ATOL)

    def test_a_record_preserving_unitary_decomposes(self):
        """Recover the blocks W_k = (<k| V^dag x 1) U (|k> x 1) and rebuild U from them."""
        d, n = 3, 2
        V, Ws = haar(d), [haar(n) for _ in range(d)]
        U = controlled(V, Ws)
        T = (np.kron(V.conj().T, np.eye(n)) @ U).reshape(d, n, d, n)
        for j in range(d):
            for k in range(d):
                if j != k:
                    self.assertLess(np.abs(T[j, :, k, :]).max(), ATOL)
        np.testing.assert_allclose(controlled(V, [T[k, :, k, :] for k in range(d)]), U, atol=ATOL)

    def test_a_generic_unitary_changes_the_record_in_every_basis(self):
        d, n = 2, 2
        U = haar(d * n)
        for _ in range(5):
            V = haar(d)
            rho, tau = pure_state(d), pure_state(n)
            diff = np.abs(self.populations(U, rho, tau, V, d, n) - np.real(np.diag(V.conj().T @ rho @ V))).max()
            self.assertGreater(diff, 1e-4)


class InputsOfTheLoop(unittest.TestCase):
    """A half of a Bell pair next to a loop it never touches (U = V x W)."""

    def setUp(self):
        self.V, self.W = haar(2), haar(2)
        self.U = np.kron(self.V, self.W)
        bell = np.array([1, 0, 0, 1], complex) / np.sqrt(2)
        self.rho = np.outer(bell, bell.conj())                      # A, O (made by a CNOT: Z record)
        self.ideal = embed(self.V, [0], [2, 2]) @ self.rho @ embed(self.V, [0], [2, 2]).conj().T

    def test_not_an_input_means_untouched(self):
        """Operator Schmidt rank 1: A is not an input. The loop's inputs are then empty (d_cr = 1, the loop
        alone runs W): PPS on them is the trivial channel, and A just goes through V, Bell pair intact."""
        self.assertEqual(len(operator_schmidt(self.U, 2, 2)[0]), 1)
        trivial = past_preserving_kraus(self.W, 1, 2, np.eye(1))
        self.assertEqual(len(trivial), 1)
        self.assertAlmostEqual(abs(trivial[0][0, 0]), 1.0, delta=ATOL)
        out = embed(self.V, [0], [2, 2]) @ self.rho @ embed(self.V, [0], [2, 2]).conj().T * abs(trivial[0][0, 0]) ** 2
        np.testing.assert_allclose(out, self.ideal, atol=ATOL)

    def test_splitting_a_non_input_into_worlds_would_destroy_entanglement(self):
        bell_v = (embed(self.V, [0], [2, 2]) @ np.array([1, 0, 0, 1], complex)) / np.sqrt(2)
        fid = lambda r: float(np.real(np.vdot(bell_v, r @ bell_v)))  # noqa: E731
        pointer = alice_channel(past_preserving_kraus(self.U, 2, 2, np.eye(2)), self.rho, [2, 2])
        state = alice_channel(state_world_kraus(self.U, 2, 2, marginal(self.rho, [2, 2], [0])), self.rho, [2, 2])
        self.assertAlmostEqual(fid(self.ideal), 1.0, delta=ATOL)
        self.assertAlmostEqual(fid(pointer), 0.5, delta=ATOL)        # classical correlation only
        self.assertAlmostEqual(fid(state), 0.5, delta=1e-3)         # Werner state with p = 1/3: separable


class Caveats(unittest.TestCase):
    def test_the_loops_reading_is_treated_as_perfect(self):
        """A recorded in Z by Bob (CNOT); the loop reads A weakly in Z (W_0 = 1, W_1 = RY(0.4)).
        All Z-diagonal statistics agree with ordinary QM. The A-Bob coherence, seen only by undoing Bob's
        record, is multiplied by Tr(W_0 tau W_1^dag) in QM and set to 0 by PPS."""
        W1 = np.array([[np.cos(0.2), -np.sin(0.2)], [np.sin(0.2), np.cos(0.2)]], complex)
        U = controlled(np.eye(2), [np.eye(2, dtype=complex), W1])
        psi = np.array([np.sqrt(0.7), np.sqrt(0.3)], complex)
        v = CNOT @ np.kron(psi, [1, 0])
        rho = np.outer(v, v.conj())
        tau = np.diag([1, 0]).astype(complex)
        pps = alice_channel(past_preserving_kraus(U, 2, 2, np.eye(2)), rho, [2, 2])
        Ufull = embed(U, [0, 2], [2, 2, 2])
        qm = marginal(Ufull @ np.kron(rho, tau) @ Ufull.conj().T, [2, 2, 2], [0, 1])
        np.testing.assert_allclose(np.diag(pps), np.diag(qm), atol=ATOL)
        factor = np.trace(np.eye(2) @ tau @ W1.conj().T)
        self.assertAlmostEqual(qm[0, 3], rho[0, 3] * factor, delta=ATOL)
        self.assertAlmostEqual(abs(pps[0, 3]), 0.0, delta=ATOL)

    def test_an_unrecorded_control_is_selected(self):
        """A fresh |+> controls a NOT on the loop (the P-CTC counterexample). No outside record of A: the
        world is the fresh state, PPS = P-CTC, and P(a = 1) drops from 0.5 to 0. H3' needs the controlled
        value recorded outside the loop's future."""
        U = controlled(np.eye(2), [np.eye(2, dtype=complex), np.array([[0, 1], [1, 0]], complex)])
        plus = np.array([1, 1], complex) / np.sqrt(2)
        fresh = sum(K @ np.outer(plus, plus) @ K.conj().T for K in past_preserving_kraus(U, 2, 2, basis_containing(plus)))
        recorded = sum(K @ np.eye(2) / 2 @ K.conj().T for K in past_preserving_kraus(U, 2, 2, np.eye(2)))
        self.assertAlmostEqual(fresh[1, 1].real, 0.0, delta=ATOL)
        self.assertAlmostEqual(recorded[1, 1].real, 0.5, delta=ATOL)


if __name__ == '__main__':
    unittest.main(verbosity=1)
