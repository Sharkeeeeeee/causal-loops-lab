"""SPDX-License-Identifier: MIT. Theorems 1 and 2 for any quantum U (THEOREMS.md, Theorems 1Q and 2Q).

For a loop basis {|b_m>} write A_ym = <y, b_m| U |k, b_m>, the amplitude of the history that starts
the loop in b_m, finds it in b_m again, and leaves the CR system in y.

  1Q  if in some loop basis every history from k to y fails to return the loop (A_ym = 0 for all m),
      then y never occurs in world k. The basis is free: C = Tr_L U does not depend on it.
  2Q  P_PPS(y | k) = |sum_m A_ym|^2 / Z, while the no-loop run conditioned on the loop coming back
      unchanged gives sum_m |A_ym|^2 / Z'. They agree whenever the output records which history
      returned (for each y at most one m with A_ym != 0); otherwise they differ by the interference
      terms sum_{m != m'} A_ym conj(A_ym').

Run from the repository root:  python -B ctc/tests/test_quantum_h1h2.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from past_preserving import past_preserving  # noqa: E402

RNG = np.random.default_rng(1212)
ATOL = 1e-9


def haar(d):
    z = RNG.normal(size=(d, d)) + 1j * RNG.normal(size=(d, d))
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / abs(np.diag(r)))


def amplitudes(U, d, n, k, B):
    """A[y, m] = <y, b_m| U |k, b_m>."""
    return np.array([[np.vdot(np.kron(np.eye(d)[y], B[:, m]), U @ np.kron(np.eye(d)[k], B[:, m])) for m in range(n)]
                     for y in range(d)])


def pps_distribution(U, d, n, k):
    rho = np.zeros((d, d), complex)
    rho[k, k] = 1
    return np.real(np.diag(past_preserving(U, rho, d, n)))


def conditioned_no_loop(U, d, n, k, B):
    """Ordinary run: loop prepared in a uniformly random b_m, measured in the same basis afterwards,
    kept only if it came back as b_m. Returns P(y | k, loop unchanged)."""
    joint = np.zeros(d)
    for m in range(n):
        out = U @ np.kron(np.eye(d)[k], B[:, m])
        for y in range(d):
            joint[y] += abs(np.vdot(np.kron(np.eye(d)[y], B[:, m]), out)) ** 2 / n
    return joint / joint.sum()


def recording_unitary(d, n):
    """A classical reversible circuit with random phases in which each output y is reached from at most
    one consistent message (N_xy in {0, 1}), dressed with a random loop basis change."""
    while True:
        perm = RNG.permutation(d * n)
        U = np.zeros((d * n, d * n), complex)
        for i, j in enumerate(perm):
            U[j, i] = np.exp(2j * np.pi * RNG.random())
        ok = True
        for x in range(d):
            ys = [perm[x * n + m] // n for m in range(n) if perm[x * n + m] % n == m]
            if len(ys) != len(set(ys)) or not ys:
                ok = False
        if ok:
            return U


class Theorem1Q(unittest.TestCase):
    def test_no_returning_history_means_never(self):
        """Build U with no returning history from k = 0 to y = 1 in the basis B (a classical circuit in that
        basis). In the computational basis the same U has returning histories to y = 1, but they cancel."""
        d, n = 2, 3
        found = 0
        for _ in range(200):
            perm = RNG.permutation(d * n)
            if any(perm[0 * n + m] == 1 * n + m for m in range(n)) or not any(perm[m] % n == m for m in range(n)):
                continue
            P = np.zeros((d * n, d * n), complex)
            for i, j in enumerate(perm):
                P[j, i] = np.exp(2j * np.pi * RNG.random())
            B = haar(n)
            U = np.kron(np.eye(d), B) @ P @ np.kron(np.eye(d), B.conj().T)
            self.assertLess(np.abs(amplitudes(U, d, n, 0, B)[1]).max(), ATOL)
            self.assertLess(pps_distribution(U, d, n, 0)[1], ATOL)
            comp = amplitudes(U, d, n, 0, np.eye(n))[1]
            self.assertGreater(np.abs(comp).max(), 1e-3)            # nonzero histories in another basis ...
            self.assertLess(abs(comp.sum()), ATOL)                  # ... that cancel
            found += 1
            if found == 5:
                break
        self.assertEqual(found, 5)

    def test_the_consistency_sum_does_not_depend_on_the_basis(self):
        d, n = 3, 2
        U = haar(d * n)
        sums = [amplitudes(U, d, n, 1, haar(n)).sum(axis=1) for _ in range(4)]
        for s in sums[1:]:
            np.testing.assert_allclose(s, sums[0], atol=ATOL)


class Theorem2Q(unittest.TestCase):
    def test_recorded_histories_give_conditioning(self):
        for d, n in ((2, 2), (3, 2), (2, 3)):
            for _ in range(4):
                B = haar(n)
                U = np.kron(np.eye(d), B) @ recording_unitary(d, n) @ np.kron(np.eye(d), B.conj().T)
                for k in range(d):
                    A = amplitudes(U, d, n, k, B)
                    self.assertTrue(all(np.sum(np.abs(A[y]) > 1e-9) <= 1 for y in range(d)))
                    np.testing.assert_allclose(pps_distribution(U, d, n, k), conditioned_no_loop(U, d, n, k, B), atol=ATOL)

    def test_general_formula_and_interference_terms(self):
        for d, n in ((2, 2), (3, 3)):
            U, B = haar(d * n), haar(n)
            for k in range(d):
                A = amplitudes(U, d, n, k, B)
                pps = np.abs(A.sum(axis=1)) ** 2
                cond = (np.abs(A) ** 2).sum(axis=1)
                np.testing.assert_allclose(pps_distribution(U, d, n, k), pps / pps.sum(), atol=ATOL)
                np.testing.assert_allclose(conditioned_no_loop(U, d, n, k, B), cond / cond.sum(), atol=ATOL)
                inter = np.array([sum(A[y, m] * np.conj(A[y, j]) for m in range(n) for j in range(n) if m != j).real
                                  for y in range(d)])
                np.testing.assert_allclose(pps, cond + inter, atol=ATOL)
                self.assertGreater(np.abs(pps / pps.sum() - cond / cond.sum()).max(), 1e-3)


if __name__ == '__main__':
    unittest.main(verbosity=1)
