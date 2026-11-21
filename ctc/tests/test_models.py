"""SPDX-License-Identifier: MIT. Checks the CTC rules against hand-derived results.

Run from the repository root:  python -B ctc/tests/test_models.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import check_unitary, d_ctc, d_ctc_fixed_point, loop_map_matrix, no_loop, p_ctc  # noqa: E402
from circuits import bootstrap, grandfather, kfk  # noqa: E402

ATOL = 1e-10


def run_all(c):
    base = no_loop(c.U, c.rho, c.d_cr, c.d_loop, c.baseline_loop)
    post, weight = p_ctc(c.U, c.rho, c.d_cr, c.d_loop)
    deutsch, tau, multiplicity = d_ctc(c.U, c.rho, c.d_cr, c.d_loop)
    return base, post, weight, deutsch, tau, multiplicity


def is_state(rho):
    eig = np.linalg.eigvalsh((rho + rho.conj().T) / 2)
    return abs(np.trace(rho) - 1) < ATOL and eig.min() > -ATOL


class Structure(unittest.TestCase):
    def test_circuits_are_unitary(self):
        for c in [grandfather(0.1), kfk(0.3, 0.6, 'motivated'), kfk(0.3, 0.6, 'unconditional'), bootstrap()]:
            self.assertLess(check_unitary(c.U), ATOL, c.name)

    def test_deutsch_output_is_a_fixed_point_and_a_state(self):
        for c in [grandfather(0.2), kfk(0.4, 0.7, 'motivated'), bootstrap()]:
            M = loop_map_matrix(c.U, c.rho, c.d_cr, c.d_loop)
            tau, _ = d_ctc_fixed_point(c.U, c.rho, c.d_cr, c.d_loop)
            self.assertTrue(np.allclose((M @ tau.reshape(-1)).reshape(tau.shape), tau, atol=ATOL), c.name)
            self.assertTrue(is_state(tau), c.name)

    def test_deutsch_matches_cesaro_iteration(self):
        c = kfk(0.4, 0.7, 'motivated')
        M = loop_map_matrix(c.U, c.rho, c.d_cr, c.d_loop)
        v = (np.eye(c.d_loop) / c.d_loop).reshape(-1).astype(complex)
        total = np.zeros_like(v)
        for _ in range(4000):
            total += v
            v = M @ v
        tau, _ = d_ctc_fixed_point(c.U, c.rho, c.d_cr, c.d_loop)
        self.assertTrue(np.allclose(total.reshape(tau.shape) / 4000, tau, atol=1e-3))

    def test_no_coupling_means_no_effect(self):
        """H3 sanity check: if the loop never touches the CR system, all rules agree."""
        from circuits import Circuit, bit_state, permutation_unitary
        U = permutation_unitary(2, lambda b: (b[0], 1 - b[1]))  # loop flips itself only
        c = Circuit('decoupled', ['a'], ['m'], U, bit_state(0.3), bit_state(0.5))
        base, post, _, deutsch, _, _ = run_all(c)
        # P-CTC: Tr(X) = 0 makes this a paradox for the loop alone, so use identity instead.
        self.assertTrue(np.allclose(base, deutsch, atol=ATOL))
        U2 = np.eye(4, dtype=complex)
        c2 = Circuit('identity', ['a'], ['m'], U2, bit_state(0.3), bit_state(0.5))
        base2, post2, _, deutsch2, _, _ = run_all(c2)
        self.assertTrue(np.allclose(base2, post2, atol=ATOL))
        self.assertTrue(np.allclose(base2, deutsch2, atol=ATOL))


class Grandfather(unittest.TestCase):
    def test_failure_becomes_certain_under_p_ctc(self):
        for eps in [1e-4, 0.01, 0.3]:
            c = grandfather(eps)
            base, post, weight, deutsch, tau, _ = run_all(c)
            self.assertAlmostEqual(c.probability_one(base, 'jam'), eps, places=10)
            self.assertAlmostEqual(c.probability_one(post, 'jam'), 1.0, places=10)
            self.assertAlmostEqual(c.probability_one(deutsch, 'jam'), eps, places=10)
            self.assertTrue(np.allclose(tau, np.eye(2) / 2, atol=ATOL))

    def test_no_failure_channel_is_a_true_paradox(self):
        c = grandfather(0.0)
        post, weight = p_ctc(c.U, c.rho, c.d_cr, c.d_loop)
        self.assertIsNone(post)
        self.assertLess(weight, 1e-12)


class KFK(unittest.TestCase):
    def test_motivated_sender(self):
        for q, r in [(0.3, 0.0), (0.3, 0.6), (0.5, 0.95), (0.9, 0.5)]:
            c = kfk(q, r, 'motivated')
            base, post, _, deutsch, _, _ = run_all(c)
            self.assertAlmostEqual(c.probability_one(base, 'outcome'), q, places=10)
            expected_post = q * (1 - r) / ((1 - q) + q * (1 - r))
            self.assertAlmostEqual(c.probability_one(post, 'outcome'), expected_post, places=10)
            self.assertAlmostEqual(c.probability_one(deutsch, 'outcome'), q / (1 + q * r), places=10)

    def test_motivated_paradox_when_reminder_always_works(self):
        post, _ = p_ctc(*[getattr(kfk(1.0, 1.0, 'motivated'), k) for k in ('U', 'rho', 'd_cr', 'd_loop')])
        self.assertIsNone(post)

    def test_unconditional_sender_all_rules_agree(self):
        for q, r in [(0.3, 0.6), (0.8, 0.1)]:
            c = kfk(q, r, 'unconditional')
            _, post, _, deutsch, _, _ = run_all(c)
            for out in (post, deutsch):
                self.assertAlmostEqual(c.probability_one(out, 'outcome'), q * (1 - r), places=10)
                self.assertAlmostEqual(c.probability_one(out, 'record'), 1.0, places=10)


class Bootstrap(unittest.TestCase):
    def test_same_statistics_different_coherence(self):
        c = bootstrap()
        base, post, _, deutsch, _, _ = run_all(c)
        for out in (base, post, deutsch):
            self.assertAlmostEqual(c.probability_one(out, 'record'), 0.5, places=10)
        self.assertAlmostEqual(c.expectation_x(post, 'record'), 1.0, places=10)
        self.assertAlmostEqual(c.expectation_x(deutsch, 'record'), 0.0, places=10)
        self.assertAlmostEqual(c.expectation_x(base, 'record'), 0.0, places=10)


if __name__ == '__main__':
    unittest.main(verbosity=2)
