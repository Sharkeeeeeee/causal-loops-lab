"""SPDX-License-Identifier: MIT. Theorem 4: the record basis from the interaction, and no-signalling.

Checks ctc/records.py and the statements of Theorem 4 in ctc/THEOREMS.md:
  - the pointer basis of an interaction is found from the interaction alone;
  - with that basis, past-preserving selection cannot signal in either direction, for random
    loops, random reading interactions and random operations by the outside party;
  - three ways of defining the past that do signal (counterexamples);
  - the basis matters for Alice's own predictions, not for signalling.

Run from the repository root:  python -B ctc/tests/test_records.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import partial_trace_operator_loop  # noqa: E402
from past_preserving import apply_kraus, past_preserving_kraus  # noqa: E402
from records import pointer_basis, reads, record_quality  # noqa: E402

RNG = np.random.default_rng(4)
ATOL = 1e-9
S = 1 / np.sqrt(2)
H = np.array([[S, S], [S, -S]], complex)
X = np.array([[0, 1], [1, 0]], complex)
CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], complex)
CZ = np.diag([1, 1, 1, -1]).astype(complex)
SWAP = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], complex)
ERASER = np.diag([1, 1, 1, 1j]).astype(complex)


def random_unitary(d):
    z = RNG.normal(size=(d, d)) + 1j * RNG.normal(size=(d, d))
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / abs(np.diag(r)))


def random_pure(d):
    v = RNG.normal(size=d) + 1j * RNG.normal(size=d)
    return v / np.linalg.norm(v)


def tr_a(rho, dA, dO):
    return np.einsum('aiaj->ij', rho.reshape(dA, dO, dA, dO))


def tr_o(rho, dA, dO):
    return np.einsum('iaja->ij', rho.reshape(dA, dO, dA, dO))


def is_same_basis(B1, B2):
    """Columns equal up to order and phases."""
    M = abs(B1.conj().T @ B2)
    return np.allclose(np.sort(M, axis=1)[:, -1], 1, atol=1e-7) and np.allclose(M.sum(axis=1), 1, atol=1e-6)


def shared_state(dA, dO, V, psi=None, o=None):
    psi = random_pure(dA) if psi is None else psi
    o = random_pure(dO) if o is None else o
    v = V @ np.kron(psi, o)
    return np.outer(v, v.conj())


class PointerBasis(unittest.TestCase):
    def test_known_interactions(self):
        Z = np.eye(2)
        self.assertTrue(is_same_basis(pointer_basis(CNOT, 2, 2), Z))
        self.assertTrue(is_same_basis(pointer_basis(CZ, 2, 2), Z))
        Hx = np.kron(H, np.eye(2))
        self.assertTrue(is_same_basis(pointer_basis(Hx @ CNOT @ Hx, 2, 2), H))     # reads the source in X

    def test_interactions_that_read_nothing(self):
        self.assertIsNone(pointer_basis(SWAP, 2, 2))                                  # exchange, not a readout
        self.assertIsNone(pointer_basis(np.kron(H, X), 2, 2))                         # no interaction
        self.assertIsNone(pointer_basis(random_unitary(4), 2, 2))                     # generic: no single basis

    def test_random_bases_are_recovered(self):
        for dA, dO in [(2, 2), (3, 2), (3, 3), (4, 2)]:
            for _ in range(5):
                B = random_unitary(dA)
                self.assertTrue(is_same_basis(pointer_basis(reads(B, dO, RNG), dA, dO), B))

    def test_partial_record_quality(self):
        t0 = np.array([1, 0], complex)
        for theta in (0.3, 1.2, np.pi):
            c, s = np.cos(theta / 2), np.sin(theta / 2)
            V = np.kron(np.diag([1, 0]), np.eye(2)) + np.kron(np.diag([0, 1]), np.array([[c, -s], [s, c]]))
            self.assertTrue(is_same_basis(pointer_basis(V, 2, 2), np.eye(2)))
            self.assertAlmostEqual(record_quality(V, 2, 2, t0), 1 - np.cos(theta / 2), delta=1e-9)


class Theorem4NoSignalling(unittest.TestCase):
    def test_random_loops_random_readouts_random_outside_operations(self):
        """Alice's input is correlated with an outside system O only through an interaction that reads
        it in a random basis B. PPS with the pointer basis of that interaction: Bob's marginal never
        changes (Alice -> Bob), and Bob's unitaries or measurements on O before the loop never change
        Alice's output (Bob -> Alice). P-CTC signals in the same setting."""
        p_ctc_changes = []
        for dA, dO in [(2, 2), (3, 2), (2, 3), (3, 3)]:
            for _ in range(6):
                U = random_unitary(2 * dA)
                V = reads(random_unitary(dA), dO, RNG)
                rho = shared_state(dA, dO, V)
                kraus = past_preserving_kraus(U, dA, 2, pointer_basis(V, dA, dO))
                out = apply_kraus(kraus, rho, dO)
                np.testing.assert_allclose(tr_a(out, dA, dO), tr_a(rho, dA, dO), atol=ATOL)
                W = np.kron(np.eye(dA), random_unitary(dO))
                rho_w = W @ rho @ W.conj().T
                np.testing.assert_allclose(tr_o(apply_kraus(kraus, rho_w, dO), dA, dO), tr_o(out, dA, dO), atol=ATOL)
                Bm = random_unitary(dO)
                rho_m = sum(np.kron(np.eye(dA), np.outer(Bm[:, j], Bm[:, j].conj())) @ rho
                            @ np.kron(np.eye(dA), np.outer(Bm[:, j], Bm[:, j].conj())) for j in range(dO))
                np.testing.assert_allclose(tr_o(apply_kraus(kraus, rho_m, dO), dA, dO), tr_o(out, dA, dO), atol=ATOL)
                C = np.kron(partial_trace_operator_loop(U, dA, 2), np.eye(dO))
                pc = C @ rho @ C.conj().T
                p_ctc_changes.append(np.abs(tr_a(pc / np.trace(pc), dA, dO) - tr_a(rho, dA, dO)).max())
        self.assertGreater(max(p_ctc_changes), 1e-2)

    def test_paradox_worlds_use_the_fallback_and_still_do_not_signal(self):
        """one_way (C = diag(2, 0)): the a = 1 world has no consistent history."""
        rho = shared_state(2, 2, CNOT, psi=H[:, 0], o=np.array([1, 0], complex))   # |Phi+>
        kraus = past_preserving_kraus(CNOT, 2, 2, pointer_basis(CNOT, 2, 2))
        out = apply_kraus(kraus, rho, 2)
        np.testing.assert_allclose(tr_a(out, 2, 2), np.eye(2) / 2, atol=ATOL)


class WaysToGetThePastWrong(unittest.TestCase):
    """Bell pair between Alice's a and Bob's b made by CNOT a -> b; Alice's loop is one_way (C = diag(2, 0))."""

    def setUp(self):
        self.psi = CNOT @ np.kron(H[:, 0], np.array([1, 0], complex))
        self.rho = np.outer(self.psi, self.psi.conj())
        self.C = np.kron(partial_trace_operator_loop(CNOT, 2, 2), np.eye(2))

    def select(self, rho):
        """P-CTC inside one sector; the one_way fallback leaves the sector unchanged."""
        F = self.C @ rho @ self.C.conj().T
        return rho if np.trace(F).real < 1e-12 else F / np.trace(F).real

    def bob_projectors(self, basis):
        return [np.kron(np.eye(2), np.outer(basis[:, j], basis[:, j].conj())) for j in (0, 1)]

    def bob_split(self, rho, basis):
        out = 0
        for P in self.bob_projectors(basis):
            r = P @ rho @ P
            w = np.trace(r).real
            if w > 1e-12:
                out = out + w * self.select(r / w)
        return out

    def test_only_explicit_record_registers(self):
        """Nobody wrote a record register, so nothing is protected and the rule is P-CTC: Bob's
        Z statistics go from 0.5 to 1."""
        out = self.select(self.rho)
        self.assertAlmostEqual(tr_a(out, 2, 2)[0, 0].real, 1.0, delta=ATOL)

    def test_split_on_bobs_side_added_coherently(self):
        """Sectors on Bob's qubit in X, summed as amplitudes: Bob's Z statistics go to 1."""
        total = np.zeros(4, complex)
        for P in self.bob_projectors(H):
            s = P @ self.psi
            f = self.C @ s
            total += f * np.linalg.norm(s) / np.linalg.norm(f)
        self.assertAlmostEqual(tr_a(np.outer(total, total.conj()), 2, 2)[0, 0].real, 1.0, delta=ATOL)

    def test_split_on_bobs_side_added_as_a_mixture(self):
        """Sectors on Bob's qubit in Z, mixed: Alice -> Bob is fine, but Bob -> Alice is not. If Bob first
        measures b in X, Alice's P(a = 0) jumps from 0.5 to 1."""
        out = self.bob_split(self.rho, np.eye(2))
        self.assertAlmostEqual(tr_a(out, 2, 2)[0, 0].real, 0.5, delta=ATOL)
        self.assertAlmostEqual(tr_o(out, 2, 2)[0, 0].real, 0.5, delta=ATOL)
        measured = sum(P @ self.rho @ P for P in self.bob_projectors(H))
        self.assertAlmostEqual(tr_o(self.bob_split(measured, np.eye(2)), 2, 2)[0, 0].real, 1.0, delta=ATOL)

    def test_alice_side_pointer_basis_is_safe(self):
        """The correct rule: Alice's own input, split in the basis the interaction read it in (Z)."""
        kraus = past_preserving_kraus(CNOT, 2, 2, pointer_basis(CNOT, 2, 2))
        for rho in (self.rho, sum(P @ self.rho @ P for P in self.bob_projectors(H))):
            out = apply_kraus(kraus, rho, 2)
            self.assertAlmostEqual(tr_o(out, 2, 2)[0, 0].real, 0.5, delta=ATOL)
            self.assertAlmostEqual(tr_a(out, 2, 2)[0, 0].real, 0.5, delta=ATOL)


class WhoReadsWhatDecides(unittest.TestCase):
    def test_basis_changes_alices_prediction_not_bobs(self):
        """Alice's input RY-prepared with P(1) = 0.3, eraser loop (C = diag(2, 1 + i)). An outside system
        that read it in Z gives P(a = 1) = 0.3; one that read it in X gives 1/3. Neither signals."""
        theta = 2 * np.arcsin(np.sqrt(0.3))
        psi = np.array([np.cos(theta / 2), np.sin(theta / 2)], complex)
        Hx = np.kron(H, np.eye(2))
        results = {}
        for name, V in (('Z', CNOT), ('X', Hx @ CNOT @ Hx)):
            rho = shared_state(2, 2, V, psi=psi, o=np.array([1, 0], complex))
            out = apply_kraus(past_preserving_kraus(ERASER, 2, 2, pointer_basis(V, 2, 2)), rho, 2)
            np.testing.assert_allclose(tr_a(out, 2, 2), tr_a(rho, 2, 2), atol=ATOL)
            results[name] = tr_o(out, 2, 2)[1, 1].real
        self.assertAlmostEqual(results['Z'], 0.3, delta=ATOL)
        self.assertAlmostEqual(results['X'], 1 / 3, delta=ATOL)


if __name__ == '__main__':
    unittest.main(verbosity=1)
