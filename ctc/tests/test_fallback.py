"""SPDX-License-Identifier: MIT. Worlds with no consistent history (THEOREMS.md, Theorem 8).

  8(1) limit       PPS with a slightly depolarized loop tends to PPS in every world with C|k> != 0, and to
                   the open loop Tr_L[U(|k><k| x 1/n)U^dag] in every world with C|k> = 0;
  8(2) uniqueness  noise with a preferred loop operation gives a different limit; the D-CTC fixed point
                   differs from the open loop in generic paradox worlds, and agrees in the earlier examples;
  8(3) power       with the D-CTC fallback a paradox world runs Deutsch's fixed-point search; with the open
                   loop one postselected run with tiny noise reproduces PPS (the PP upper bound).

Run from the repository root:  python -B ctc/tests/test_fallback.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from circuits import grandfather  # noqa: E402
from fallback import (dctc_world, fixed_point_search, noisy_loop_kraus, open_loop_world, output_register,  # noqa: E402
                      p_ctc_channel, regularized_world, single_postselection)
from models import partial_trace_operator_loop  # noqa: E402
from past_preserving import past_preserving  # noqa: E402

RNG = np.random.default_rng(808)
X = np.array([[0, 1], [1, 0]], complex)


def haar(d):
    z = RNG.normal(size=(d, d)) + 1j * RNG.normal(size=(d, d))
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / abs(np.diag(r)))


def with_grandfather(U):
    """Add a loop bit that is flipped every round: C = Tr_L U x Tr X = 0, every world is a paradox world,
    while the rest of the loop is the generic U."""
    return np.kron(U, X)


def pps_world(U, d, n, v):
    C = partial_trace_operator_loop(U, d, n)
    w = C @ v
    return np.outer(w, w.conj()) / np.vdot(w, w).real


class Limit(unittest.TestCase):
    def test_consistent_worlds_tend_to_pps(self):
        for d, n in ((2, 2), (3, 2), (2, 3)):
            U = haar(d * n)
            v = np.eye(d)[0]
            errs = [np.abs(regularized_world(U, d, n, v, e) - pps_world(U, d, n, v)).max() for e in (1e-2, 1e-4, 1e-6)]
            self.assertLess(errs[-1], 1e-5)
            self.assertTrue(errs[0] > errs[1] > errs[2])

    def test_paradox_worlds_tend_to_the_open_loop(self):
        for d, n in ((2, 2), (3, 2), (2, 3)):
            U = with_grandfather(haar(d * n))
            for k in range(d):
                v = np.eye(d)[k]
                self.assertLess(np.linalg.norm(partial_trace_operator_loop(U, d, 2 * n) @ v), 1e-12)
                for e in (1e-1, 1e-6):     # exact for every eps: only the noise lets anything through
                    np.testing.assert_allclose(regularized_world(U, d, 2 * n, v, e), open_loop_world(U, d, 2 * n, v), atol=1e-9)


class Uniqueness(unittest.TestCase):
    def test_noise_with_a_preferred_operation_gives_another_limit(self):
        """A loop kicked by a fixed unitary K with probability eps: the limit is P-CTC of (1 x K)U, here
        a pure state, not the open loop."""
        d, n = 2, 2
        U0 = haar(d * n)
        U = with_grandfather(U0)
        K = np.kron(np.eye(n), X)                                     # undo the grandfather flip
        kraus = [np.sqrt(1 - 1e-6) * U, np.sqrt(1e-6) * np.kron(np.eye(d), K) @ U]
        v = np.eye(d)[0]
        kicked = p_ctc_channel(kraus, np.outer(v, v), d, 2 * n)[0]
        np.testing.assert_allclose(kicked, pps_world(U0, d, n, v), atol=1e-6)
        self.assertGreater(np.abs(kicked - open_loop_world(U, d, 2 * n, v)).max(), 1e-2)

    def test_only_the_depolarizing_noise_is_basis_free(self):
        """Basis-free means N(W X W^dag) = W N(X) W^dag for every loop unitary W. The full depolarizing
        noise passes; the dephasing noise, which prefers the computational basis, fails."""
        n = 3

        def channel(noise, Xm):
            ks = noisy_loop_kraus(np.eye(n, dtype=complex), 1, n, 1.0, noise)
            return sum(K @ Xm @ K.conj().T for K in ks)
        Xm = RNG.normal(size=(n, n)) + 1j * RNG.normal(size=(n, n))
        W = haar(n)
        for noise, basis_free in (('depolarize', True), ('dephase', False)):
            gap = np.abs(channel(noise, W @ Xm @ W.conj().T) - W @ channel(noise, Xm) @ W.conj().T).max()
            self.assertEqual(gap < 1e-9, basis_free, noise)

    def test_dctc_differs_from_the_open_loop_in_generic_paradox_worlds(self):
        diffs = []
        for d, n in ((2, 2), (2, 3), (3, 2)):
            U = with_grandfather(haar(d * n))
            v = np.eye(d)[0]
            diffs.append(np.abs(dctc_world(U, d, 2 * n, v) - open_loop_world(U, d, 2 * n, v)).max())
        self.assertGreater(min(diffs), 1e-3)

    def test_the_earlier_examples_do_not_depend_on_the_choice(self):
        c = grandfather(0.0)
        for k in range(c.d_cr):
            v = np.eye(c.d_cr)[k]
            np.testing.assert_allclose(dctc_world(c.U, c.d_cr, c.d_loop, v), open_loop_world(c.U, c.d_cr, c.d_loop, v), atol=1e-9)
        # Theorem 3 with a zero-trace block: both give V|k><k|V^dag
        V = haar(2)
        U = np.kron(V, np.eye(2)) @ (np.kron(np.diag([1, 0]), np.diag([1, -1])) + np.kron(np.diag([0, 1]), haar(2)))
        v = np.eye(2)[0]
        np.testing.assert_allclose(dctc_world(U, 2, 2, v), open_loop_world(U, 2, 2, v), atol=1e-9)
        np.testing.assert_allclose(open_loop_world(U, 2, 2, v), V @ np.outer(v, v) @ V.conj().T, atol=1e-9)


class Power(unittest.TestCase):
    def test_a_dctc_fallback_runs_the_fixed_point_search(self):
        m = 4
        rho = np.zeros((2 * m, 2 * m))
        rho[0, 0] = 1
        for target in range(m):
            U = fixed_point_search(m, target)
            self.assertLess(np.abs(partial_trace_operator_loop(U, 2 * m, 2 * m)).max(), 1e-12)
            dctc = output_register(past_preserving(U, rho, 2 * m, 2 * m, fallback='dctc'), m)
            opened = output_register(past_preserving(U, rho, 2 * m, 2 * m, fallback='open'), m)
            np.testing.assert_allclose(dctc, np.eye(m)[target], atol=1e-9)
            np.testing.assert_allclose(opened, np.ones(m) / m, atol=1e-9)

    def test_one_postselection_reproduces_the_open_rule(self):
        """Circuits of Hadamard, CNOT and Toffoli gates: a nonzero ||C v||^2 is at least 2^-h (h Hadamards),
        so eps = 2^-(h+10) gives trace distance below 2^-9 in consistent worlds and exactness in paradox
        worlds."""
        H = np.array([[1, 1], [1, -1]], complex) / np.sqrt(2)
        nq, d, n = 4, 4, 4
        checked = {'consistent': 0, 'paradox': 0}
        for _ in range(60):
            U, h = np.eye(2 ** nq, dtype=complex), 0
            for _ in range(10):
                kind = RNG.integers(3)
                if kind == 0:
                    q = int(RNG.integers(nq))
                    U = gate(H, [q], nq) @ U
                    h += 1
                elif kind == 1:
                    a, b = RNG.choice(nq, 2, replace=False)
                    U = controlled_x([int(a)], int(b), nq) @ U
                else:
                    a, b, c = RNG.choice(nq, 3, replace=False)
                    U = controlled_x([int(a), int(b)], int(c), nq) @ U
            C = partial_trace_operator_loop(U, d, n)
            for k in range(d):
                v = np.eye(d)[k]
                weight = np.linalg.norm(C @ v) ** 2
                eps = 2.0 ** -(h + 10)
                sim = single_postselection(U, d, n, v, eps)
                exact = past_preserving(U, np.outer(v, v), d, n, basis=np.eye(d))
                dist = 0.5 * np.abs(np.linalg.eigvalsh(sim - exact)).sum()
                if weight > 1e-12:
                    self.assertGreaterEqual(weight, 2.0 ** -h - 1e-12)
                    self.assertLess(dist, 2.0 ** -9)
                    checked['consistent'] += 1
                else:
                    self.assertLess(dist, 1e-9)
                    checked['paradox'] += 1
        self.assertGreater(checked['consistent'], 20)
        self.assertGreater(checked['paradox'], 0)


def gate(G, qubits, nq):
    ops = [np.eye(2, dtype=complex)] * nq
    ops = list(ops)
    ops[qubits[0]] = G
    out = np.ones((1, 1), complex)
    for o in ops:
        out = np.kron(out, o)
    return out


def controlled_x(controls, target, nq):
    dim = 2 ** nq
    P = np.zeros((dim, dim), complex)
    for i in range(dim):
        bits = [(i >> (nq - 1 - q)) & 1 for q in range(nq)]
        if all(bits[c] for c in controls):
            bits[target] ^= 1
        j = sum(b << (nq - 1 - q) for q, b in enumerate(bits))
        P[j, i] = 1
    return P


if __name__ == '__main__':
    unittest.main(verbosity=1)
