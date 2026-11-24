"""SPDX-License-Identifier: MIT. Past-preserving selection inherits the computational power of P-CTC.

Claim (PERSPECTIVES.md, section 1.5): when the CR input is a definite record |k> and C|k> != 0,
past-preserving selection outputs C|k> / ||C|k>||, exactly as P-CTC does. A computation starts
from a definite classical input, so past-preserving selection can do everything P-CTC can do on
such inputs. P-CTC on classical inputs is known to equal PostBQP = PP (Lloyd et al. 2011,
Aaronson 2005). The two rules differ only for mixed or superposed inputs, where P-CTC
reweights the worlds and past-preserving selection does not.

The search example builds the superposition inside U, after the record is made, so the
"past" that past-preserving selection protects is only the input |0...0>.

Run from the repository root:  python -B ctc/tests/test_computational_power.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import maximally_mixed_loop, p_ctc, partial_trace_operator_loop  # noqa: E402
from past_preserving import basis_containing, past_preserving  # noqa: E402

ATOL = 1e-9
RNG = np.random.default_rng(1124)


def random_unitary(d):
    z = (RNG.normal(size=(d, d)) + 1j * RNG.normal(size=(d, d))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / abs(np.diag(r)))


def random_pure(d):
    v = RNG.normal(size=d) + 1j * RNG.normal(size=d)
    return v / np.linalg.norm(v)


def search_circuit(n, solutions):
    """U on (n-qubit CR register) x (one loop qubit). First Hadamards on every CR qubit, then
    a NOT on the loop qubit controlled by "x is not a solution". Only histories in which x is
    a solution are self-consistent, so selection acts as postselection on f(x) = 1."""
    d = 2 ** n
    h = np.array([[1, 1], [1, -1]], complex) / np.sqrt(2)
    hn = np.ones((1, 1), complex)
    for _ in range(n):
        hn = np.kron(hn, h)
    mark = np.zeros((d, d), complex)
    for x in solutions:
        mark[x, x] = 1
    unmark = np.eye(d) - mark
    X = np.array([[0, 1], [1, 0]], complex)
    oracle = np.kron(mark, np.eye(2)) + np.kron(unmark, X)
    return oracle @ np.kron(hn, np.eye(2))


class DefiniteInputsAgree(unittest.TestCase):
    def test_basis_input_matches_p_ctc(self):
        """Random U, computational record basis, input |k>: past-preserving == P-CTC."""
        for d_cr, d_loop in [(2, 2), (3, 2), (4, 2), (2, 3), (4, 4)]:
            for _ in range(5):
                U = random_unitary(d_cr * d_loop)
                for k in range(d_cr):
                    rho = np.zeros((d_cr, d_cr), complex)
                    rho[k, k] = 1
                    out_p, weight = p_ctc(U, rho, d_cr, d_loop)
                    self.assertIsNotNone(out_p)  # generic U: C|k> != 0
                    out_pp = past_preserving(U, rho, d_cr, d_loop)
                    np.testing.assert_allclose(out_pp, out_p, atol=ATOL)

    def test_pure_input_with_its_own_record_basis(self):
        """Pure input psi with a record basis that contains psi: past-preserving == P-CTC."""
        for d_cr, d_loop in [(2, 2), (3, 3), (4, 2)]:
            for _ in range(5):
                U = random_unitary(d_cr * d_loop)
                psi = random_pure(d_cr)
                rho = np.outer(psi, psi.conj())
                out_p, _ = p_ctc(U, rho, d_cr, d_loop)
                out_pp = past_preserving(U, rho, d_cr, d_loop, basis_containing(psi))
                np.testing.assert_allclose(out_pp, out_p, atol=ATOL)

    def test_mixed_input_differs(self):
        """For a mixed input the rules differ: P-CTC reweights the worlds, past-preserving does not."""
        d_cr, d_loop = 2, 2
        U = random_unitary(d_cr * d_loop)
        rho = np.diag([0.5, 0.5]).astype(complex)
        out_p, _ = p_ctc(U, rho, d_cr, d_loop)
        out_pp = past_preserving(U, rho, d_cr, d_loop)
        self.assertGreater(np.max(abs(out_p - out_pp)), 1e-3)


class SearchByConsistency(unittest.TestCase):
    def test_finds_a_solution_with_certainty(self):
        """One loop qubit, one call to the circuit: past-preserving selection returns a
        solution with probability 1, for any number of solutions >= 1. Without the loop the
        success probability is (#solutions) / 2^n."""
        n = 6
        d = 2 ** n
        for solutions in [[37], [5, 50], list(RNG.choice(d, size=7, replace=False))]:
            U = search_circuit(n, solutions)
            rho0 = np.zeros((d, d), complex)
            rho0[0, 0] = 1                        # the recorded past: input 000000
            p_pp = past_preserving(U, rho0, d, 2)
            p_p, _ = p_ctc(U, rho0, d, 2)
            p_none = maximally_mixed_loop(U, rho0, d, 2)
            success = lambda rho: float(sum(rho[x, x].real for x in solutions))
            self.assertAlmostEqual(success(p_pp), 1.0, places=9)
            self.assertAlmostEqual(success(p_p), 1.0, places=9)
            self.assertAlmostEqual(success(p_none), len(solutions) / d, places=9)
            self.assertAlmostEqual(np.trace(p_pp).real, 1.0, places=9)

    def test_no_solution_falls_back(self):
        """No solution: P-CTC is undefined; past-preserving selection falls back to D-CTC and
        still outputs a normalized state. Checking that output against f answers 'no solution'."""
        n = 3
        d = 2 ** n
        U = search_circuit(n, [])
        rho0 = np.zeros((d, d), complex)
        rho0[0, 0] = 1
        self.assertTrue(np.allclose(partial_trace_operator_loop(U, d, 2) @ rho0[:, 0], 0))
        out_p, weight = p_ctc(U, rho0, d, 2)
        self.assertIsNone(out_p)
        out_pp = past_preserving(U, rho0, d, 2)
        self.assertAlmostEqual(np.trace(out_pp).real, 1.0, places=9)


if __name__ == '__main__':
    unittest.main(verbosity=2)
