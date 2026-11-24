"""SPDX-License-Identifier: MIT. Beyond one fine readout: THEOREMS.md, Theorem 4, parts 4a-4c.

  4a  several readouts in incompatible bases: the last readout fixes the record basis;
  4b  coarse readouts: inside each block the loop acts on the pre-readout state projected into it;
  4c  weak readouts: the pointer rule is all-or-nothing, the eigenbasis rule is continuous, both
      are safe; a continuous rule that splits on the outside's record states signals.

Run from the repository root:  python -B ctc/tests/test_readouts.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import partial_trace_operator_loop  # noqa: E402
from past_preserving import apply_kraus, basis_containing, past_preserving_kraus  # noqa: E402
from records import (blocks_after, eigenbasis_rule, pointer_basis, pointer_blocks,  # noqa: E402
                     world_kraus, world_vectors)

RNG = np.random.default_rng(45)
ATOL = 1e-9
S = 1 / np.sqrt(2)
H = np.array([[S, S], [S, -S]], complex)
CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], complex)
ERASER = np.diag([1, 1, 1, 1j]).astype(complex)


def random_unitary(d):
    z = RNG.normal(size=(d, d)) + 1j * RNG.normal(size=(d, d))
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / abs(np.diag(r)))


def random_pure(d):
    v = RNG.normal(size=d) + 1j * RNG.normal(size=d)
    return v / np.linalg.norm(v)


def embed(op, pos, dims):
    """op acting on the subsystems listed in pos (in order), identity elsewhere."""
    n = len(dims)
    d = int(np.prod(dims))
    out = np.zeros((d, d), complex)
    k = len(pos)
    rest = [i for i in range(n) if i not in pos]
    perm = list(pos) + rest
    dp = [dims[i] for i in perm]
    big = np.kron(op, np.eye(int(np.prod([dims[i] for i in rest])) if rest else 1))
    T = big.reshape(dp + dp)
    inv = np.argsort(perm)
    T = np.transpose(T, list(inv) + [n + i for i in inv])
    return T.reshape(d, d)


def marginal(rho, dims, keep):
    n = len(dims)
    T = rho.reshape(dims + dims)
    others = [i for i in range(n) if i not in keep]
    letters = 'abcdefghij'
    left = [letters[i] for i in range(n)]
    right = [letters[i] if i in others else letters[i].upper() for i in range(n)]
    out = ''.join(letters[i] for i in keep) + ''.join(letters[i].upper() for i in keep)
    return np.einsum(''.join(left) + ''.join(right) + '->' + out, T).reshape(
        int(np.prod([dims[i] for i in keep])), -1)


def alice_channel(kraus, rho, dims):
    """Apply Kraus operators on subsystem 0 (Alice), identity on the rest."""
    return sum(embed(K, [0], dims) @ rho @ embed(K, [0], dims).conj().T for K in kraus)


def outside_measurement(rho, dims, sub, basis):
    out = 0
    for j in range(dims[sub]):
        P = embed(np.outer(basis[:, j], basis[:, j].conj()), [sub], dims)
        out = out + P @ rho @ P
    return out


class IncompatibleReadouts(unittest.TestCase):
    """Bob reads a in Z (CNOT a -> b), then Carol reads it in X."""

    def setUp(self):
        self.dims = [2, 2, 2]
        Hx = np.kron(H, np.eye(2))
        self.read_z, self.read_x = CNOT, Hx @ CNOT @ Hx
        psi = np.array([np.sqrt(0.7), np.sqrt(0.3)], complex)
        v = np.kron(np.kron(psi, [1, 0]), [1, 0])
        v = embed(self.read_z, [0, 1], self.dims) @ v
        v = embed(self.read_x, [0, 2], self.dims) @ v
        self.rho = np.outer(v, v.conj())

    def test_the_last_readout_fixes_the_basis(self):
        blocks = blocks_after([pointer_blocks(self.read_z, 2, 2), pointer_blocks(self.read_x, 2, 2)])
        basis = np.column_stack(world_vectors(blocks))
        self.assertTrue(np.allclose(abs(basis.conj().T @ H), np.eye(2), atol=1e-7)
                        or np.allclose(abs(basis.conj().T @ H), np.eye(2)[::-1], atol=1e-7))

    def test_every_record_is_protected_and_nobody_can_signal(self):
        """PPS in the last readout's basis is a fixed channel on Alice: Bob's and Carol's records, and
        their joint statistics, never change; neither can change Alice's output by acting first."""
        blocks = blocks_after([pointer_blocks(self.read_z, 2, 2), pointer_blocks(self.read_x, 2, 2)])
        for U in (CNOT, ERASER, random_unitary(4)):
            kraus = world_kraus(U, 2, 2, world_vectors(blocks))
            out = alice_channel(kraus, self.rho, self.dims)
            np.testing.assert_allclose(marginal(out, self.dims, [1, 2]), marginal(self.rho, self.dims, [1, 2]), atol=ATOL)
            for sub in (1, 2):
                for basis in (np.eye(2), H, random_unitary(2)):
                    pre = outside_measurement(self.rho, self.dims, sub, basis)
                    np.testing.assert_allclose(marginal(alice_channel(kraus, pre, self.dims), self.dims, [0]),
                                               marginal(out, self.dims, [0]), atol=ATOL)

    def test_the_loop_sees_the_source_as_the_last_readout_left_it(self):
        """one_way loop (C = diag(2, 0)): after Carol's X readout both worlds |+> and |-> go to |0>, so
        P(a = 0) = 1; with Bob's Z readout alone PPS would leave it at 0.7. Bob's record stays 0.7/0.3."""
        blocks = blocks_after([pointer_blocks(self.read_z, 2, 2), pointer_blocks(self.read_x, 2, 2)])
        out = alice_channel(world_kraus(CNOT, 2, 2, world_vectors(blocks)), self.rho, self.dims)
        self.assertAlmostEqual(marginal(out, self.dims, [0])[0, 0].real, 1.0, delta=ATOL)
        self.assertAlmostEqual(marginal(out, self.dims, [1])[0, 0].real, 0.7, delta=ATOL)


class CoarseReadouts(unittest.TestCase):
    def coarse_readout(self, d_a, groups):
        """A readout that only tells which group a basis state is in (record states |g> on O)."""
        d_o = len(groups)
        V = np.zeros((d_a * d_o, d_a * d_o), complex)
        for g, members in enumerate(groups):
            P = sum(np.outer(np.eye(d_a)[k], np.eye(d_a)[k]) for k in members)
            shift = np.roll(np.eye(d_o), g, axis=0)        # |0> -> |g>
            V += np.kron(P, shift)
        return V

    def test_blocks_are_found(self):
        V = self.coarse_readout(3, [[0], [1, 2]])
        ranks = sorted(int(round(np.trace(P).real)) for P in pointer_blocks(V, 3, 2))
        self.assertEqual(ranks, [1, 2])
        self.assertIsNone(pointer_basis(V, 3, 2))           # not a fine readout

    def test_no_signalling_for_any_operation_on_the_outside(self):
        """Pre-readout state pure, all correlations from the readout. The rule (P-CTC inside each block on
        the projected pre-readout state) is then a fixed channel given that state: the outside party's
        marginal never changes, and no unitary or measurement on the outside changes Alice's output."""
        for d_a, groups in ((3, [[0], [1, 2]]), (4, [[0, 1], [2, 3]]), (4, [[0], [1, 2, 3]])):
            V = self.coarse_readout(d_a, groups)
            d_o = len(groups)
            dims = [d_a, d_o]
            for _ in range(4):
                psi = random_pure(d_a)
                U = random_unitary(2 * d_a)
                v = V @ np.kron(psi, np.eye(d_o)[0])
                rho = np.outer(v, v.conj())
                kraus = world_kraus(U, d_a, 2, world_vectors(pointer_blocks(V, d_a, d_o), psi))
                out = alice_channel(kraus, rho, dims)
                np.testing.assert_allclose(marginal(out, dims, [1]), marginal(rho, dims, [1]), atol=ATOL)
                W = embed(random_unitary(d_o), [1], dims)
                for pre in (W @ rho @ W.conj().T, outside_measurement(rho, dims, 1, random_unitary(d_o))):
                    np.testing.assert_allclose(marginal(alice_channel(kraus, pre, dims), dims, [0]),
                                               marginal(out, dims, [0]), atol=ATOL)

    def test_no_readout_at_all_is_p_ctc(self):
        """One block containing everything: the rule is P-CTC on the (fresh) input."""
        psi, U = random_pure(3), random_unitary(6)
        kraus = world_kraus(U, 3, 2, world_vectors([np.eye(3)], psi))
        C = partial_trace_operator_loop(U, 3, 2)
        w = C @ psi
        np.testing.assert_allclose(apply_kraus(kraus, np.outer(psi, psi.conj())),
                                   np.outer(w, w.conj()) / np.vdot(w, w).real, atol=ATOL)

    def test_premise_matters(self):
        """If the input was entangled beforehand with a hidden partner D by an interaction that read no
        basis, there is no fixed state inside a block. Applying P-CTC to whatever the block holds then
        changes D's own statistics (the P-CTC signalling mechanism, confined to the block)."""
        d_a = 3
        V = self.coarse_readout(d_a, [[0], [1, 2]])
        dims = [d_a, 3, 2]                                     # A, D, O
        phi = sum(np.kron(np.eye(3)[k], np.eye(3)[k]) for k in range(3)) / np.sqrt(3)
        v = embed(V, [0, 2], dims) @ np.kron(phi, [1, 0])
        rho = np.outer(v, v.conj())
        C = embed(partial_trace_operator_loop(random_unitary(6), d_a, 2), [0], dims)
        out = 0
        for P in pointer_blocks(V, d_a, 2):
            Pb = embed(P, [0], dims)
            x = Pb @ rho @ Pb
            y = C @ x @ C.conj().T
            out = out + np.trace(x).real * y / np.trace(y).real
        self.assertGreater(np.abs(marginal(out, dims, [1]) - marginal(rho, dims, [1])).max(), 1e-3)


class WeakReadouts(unittest.TestCase):
    """Input with P(1) = 0.3, readout controlled-RY(theta) onto O from |0> (record overlap cos(theta/2)),
    eraser loop C = diag(2, 1 + i)."""

    def setUp(self):
        th = 2 * np.arcsin(np.sqrt(0.3))
        self.psi = np.array([np.cos(th / 2), np.sin(th / 2)], complex)
        self.dims = [2, 2]

    def readout(self, theta):
        c, s = np.cos(theta / 2), np.sin(theta / 2)
        return np.kron(np.diag([1, 0]), np.eye(2)) + np.kron(np.diag([0, 1]), np.array([[c, -s], [s, c]]))

    def state(self, theta):
        v = self.readout(theta) @ np.kron(self.psi, [1, 0])
        return np.outer(v, v.conj())

    def alice_p1(self, basis, rho):
        return marginal(alice_channel(past_preserving_kraus(ERASER, 2, 2, basis), rho, self.dims), self.dims, [0])[1, 1].real

    def test_pointer_rule_is_all_or_nothing(self):
        fresh = self.alice_p1(basis_containing(self.psi), self.state(0.0))
        self.assertAlmostEqual(fresh, 0.6 / 3.4, delta=ATOL)                      # P-CTC on the fresh input
        for theta in (0.05, 0.6, 2.0, np.pi):
            self.assertAlmostEqual(self.alice_p1(pointer_basis(self.readout(theta), 2, 2), self.state(theta)), 0.3, delta=ATOL)

    def test_eigenbasis_rule_is_continuous_and_safe(self):
        values = []
        for theta in (0.0, 0.05, 0.6, 1.2, 2.0, np.pi):
            rho = self.state(theta)
            basis = eigenbasis_rule(marginal(rho, self.dims, [0]), np.eye(2))
            values.append(self.alice_p1(basis, rho))
            kraus = past_preserving_kraus(ERASER, 2, 2, basis)
            out = alice_channel(kraus, rho, self.dims)
            np.testing.assert_allclose(marginal(out, self.dims, [1]), marginal(rho, self.dims, [1]), atol=ATOL)
            pre = outside_measurement(rho, self.dims, 1, random_unitary(2))
            # Bob's measurement leaves Alice's reduced state, hence the basis, unchanged
            basis_pre = eigenbasis_rule(marginal(pre, self.dims, [0]), np.eye(2))
            for k in range(2):
                np.testing.assert_allclose(np.outer(basis_pre[:, k], basis_pre[:, k].conj()),
                                           np.outer(basis[:, k], basis[:, k].conj()), atol=1e-8)
            np.testing.assert_allclose(marginal(alice_channel(kraus, pre, self.dims), self.dims, [0]),
                                       marginal(out, self.dims, [0]), atol=ATOL)
        self.assertAlmostEqual(values[0], 0.6 / 3.4, delta=ATOL)
        self.assertAlmostEqual(values[-1], 0.3, delta=ATOL)
        self.assertTrue(all(b >= a - 1e-12 for a, b in zip(values, values[1:])))
        self.assertLess(values[1] - values[0], 1e-3)                              # no jump at the first trace of a record

    def test_splitting_on_the_outside_record_states_signals(self):
        """A continuous alternative: worlds = the outside system's record states (symmetrically
        orthonormalized), P-CTC inside each. Bob measuring his system first changes Alice's output."""
        C = embed(partial_trace_operator_loop(ERASER, 2, 2), [0], self.dims)
        signals = []
        for theta in (0.3, 1.2, 2.0):
            c, s = np.cos(theta / 2), np.sin(theta / 2)
            E = np.column_stack([[1, 0], [c, s]]).astype(complex)
            w, Q = np.linalg.eigh(E.conj().T @ E)
            F = E @ Q @ np.diag(w ** -0.5) @ Q.conj().T

            def outside_worlds(r):
                out = 0
                for j in range(2):
                    P = embed(np.outer(F[:, j], F[:, j].conj()), [1], self.dims)
                    x = P @ r @ P
                    y = C @ x @ C.conj().T
                    out = out + np.trace(x).real * y / np.trace(y).real
                return marginal(out, self.dims, [0])[1, 1].real

            rho = self.state(theta)
            B = np.column_stack([[-s, c], [c, s]]).astype(complex)
            signals.append(abs(outside_worlds(rho) - outside_worlds(outside_measurement(rho, self.dims, 1, B))))
        self.assertGreater(min(signals), 1e-3)


if __name__ == '__main__':
    unittest.main(verbosity=1)
