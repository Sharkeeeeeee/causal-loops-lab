"""SPDX-License-Identifier: MIT. Checks the classical kappa-beta branch model (branches.py).

Run from the repository root:  python -B ctc/tests/test_branches.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import d_ctc, p_ctc  # noqa: E402
from circuits import bootstrap, grandfather, kfk  # noqa: E402
from branches import classical_tables, input_marginal, output_state  # noqa: E402

ATOL = 1e-9
INF = np.inf
CIRCUITS = [grandfather(0.05), grandfather(0.3), kfk(0.3, 0.6, 'motivated'), kfk(0.7, 0.2, 'motivated'),
            kfk(0.3, 0.6, 'unconditional'), bootstrap()]


def diag(rho):
    return np.diag(rho).real


class Corners(unittest.TestCase):
    def test_kappa0_beta0_is_deutsch(self):
        for c in CIRCUITS:
            quantum, _, _ = d_ctc(c.U, c.rho, c.d_cr, c.d_loop)
            self.assertTrue(np.allclose(diag(output_state(c, 0, 0)), diag(quantum), atol=ATOL), c.name)

    def test_kappa1_beta_inf_is_postselection(self):
        """Compared on outcome probabilities (diagonals); the classical model has no coherences."""
        for c in CIRCUITS:
            quantum, _ = p_ctc(c.U, c.rho, c.d_cr, c.d_loop)
            self.assertTrue(np.allclose(diag(output_state(c, 1, INF)), diag(quantum), atol=ATOL), c.name)

    def test_true_paradox_has_no_branches(self):
        self.assertIsNone(output_state(grandfather(0.0), 1, INF))
        self.assertIsNone(output_state(kfk(1.0, 1.0, 'motivated'), 0, INF))


class NoSelectionNoReweighting(unittest.TestCase):
    def test_world_prior_is_untouched_when_beta_is_zero(self):
        """Branch weights set only by message dynamics never reweight the CR input."""
        for c in CIRCUITS:
            P0, _, _ = classical_tables(c)
            for kappa in np.linspace(0, 1, 6):
                self.assertTrue(np.allclose(input_marginal(c, kappa, 0), P0, atol=ATOL), (c.name, kappa))

    def test_grandfather_failure_stays_eps_without_selection(self):
        for kappa in np.linspace(0, 1, 6):
            c = grandfather(0.05)
            self.assertAlmostEqual(c.probability_one(output_state(c, kappa, 0), 'jam'), 0.05, places=9)


class ClosedForms(unittest.TestCase):
    def test_grandfather_depends_only_on_beta(self):
        """P(fail) = eps / (eps + (1 - eps) e^-beta) for every kappa (hand-derived)."""
        eps = 0.05
        c = grandfather(eps)
        for kappa in (0, 0.4, 1):
            for beta in (0.5, 2.0, 6.0):
                expected = eps / (eps + (1 - eps) * np.exp(-beta))
                self.assertAlmostEqual(c.probability_one(output_state(c, kappa, beta), 'jam'), expected, places=9)

    def test_kfk_new_corners(self):
        """Hand-derived: per-world Deutsch (1, 0) gives q(1 - r/2); typical-but-consistent
        (0, inf) gives q(1-r) pi / ((1-q)(1-pi) + q(1-r) pi) with pi = q / (1 + q r)."""
        for q, r in [(0.3, 0.6), (0.3, 1.0), (0.8, 0.3)]:
            c = kfk(q, r, 'motivated')
            self.assertAlmostEqual(c.probability_one(output_state(c, 1, 0), 'outcome'), q * (1 - r / 2), places=9)
            pi = q / (1 + q * r)
            expected = q * (1 - r) * pi / ((1 - q) * (1 - pi) + q * (1 - r) * pi)
            self.assertAlmostEqual(c.probability_one(output_state(c, 0, INF), 'outcome'), expected, places=9)

    def test_unconditional_sender_is_the_same_everywhere(self):
        c = kfk(0.3, 0.6, 'unconditional')
        for kappa in (0, 0.5, 1):
            for beta in (0, 1.0, INF):
                self.assertAlmostEqual(c.probability_one(output_state(c, kappa, beta), 'outcome'), 0.3 * 0.4, places=9)


if __name__ == '__main__':
    unittest.main(verbosity=2)
