"""SPDX-License-Identifier: MIT. Checks for the isolated-pure-state model in ctc/born_rule/.

Run from the repository root:  python -B ctc/tests/test_born_rule.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'born_rule'))
sys.path.insert(0, str(HERE.parent))
from model import intensity, max_eps, sorkin_kappa, two_path_shift  # noqa: E402
from past_preserving import basis_containing, past_preserving  # noqa: E402


class Model(unittest.TestCase):
    def test_standard_quantum_mechanics_gives_zero(self):
        for phis in ([0, 0, 0.7], [0.3, 1.2, 2.0]):
            self.assertAlmostEqual(sorkin_kappa(0.0, phis), 0.0, places=14)
        self.assertAlmostEqual(sorkin_kappa(1.0, [0.9, 0.9, 0.9]), 0.0, places=12)   # C proportional to 1

    def test_kappa_is_fourth_order_in_phi(self):
        k1, k2 = sorkin_kappa(1.0, [0, 0, 0.01]), sorkin_kappa(1.0, [0, 0, 0.02])
        self.assertAlmostEqual(k2 / k1, 16.0, places=2)

    def test_two_path_shift_is_second_order(self):
        s1, s2 = two_path_shift(0.5, 0.01, 1.0), two_path_shift(0.5, 0.02, 1.0)
        self.assertAlmostEqual(s2 / s1, 4.0, places=3)
        self.assertAlmostEqual(s1, -0.01 ** 2 / 16, places=8)

    def test_two_path_shift_matches_past_preserving_module(self):
        """Independent route: ctc/past_preserving.py on a fresh pure path state (record basis containing
        it) with U = controlled phase between path and loop."""
        for p, phi in ((0.5, np.pi / 2), (0.3, 1.0), (0.8, 2.5)):
            psi = np.array([np.sqrt(1 - p), np.sqrt(p)], complex)
            U = np.diag([1, 1, 1, np.exp(1j * phi)]).astype(complex)
            out = past_preserving(U, np.outer(psi, psi.conj()), 2, 2, basis_containing(psi))
            self.assertAlmostEqual(out[1, 1].real - p, two_path_shift(p, phi, 1.0), places=10)

    def test_through_probability_is_kept(self):
        """Getting through the open slits is a recorded fact: its probability does not change."""
        c = (1 + np.exp(1j * np.array([0, 0, 2.0]))) / 2
        amps, phases = (1, 1, 1), (0.0, 1.0, 2.0)
        total_qm = sum(intensity((j,), amps, phases, c, 0.0) for j in range(3))
        total_loop = sum(intensity((j,), amps, phases, c, 1.0) for j in range(3))
        self.assertAlmostEqual(total_qm, total_loop, places=12)

    def test_max_eps_is_consistent(self):
        e = max_eps(6.2e-5, [0, 0, np.pi / 2])
        self.assertLessEqual(abs(sorkin_kappa(e, [0, 0, np.pi / 2])), 6.2e-5 * (1 + 1e-9))
        self.assertGreater(abs(sorkin_kappa(min(1.0, e * 1.01), [0, 0, np.pi / 2])), 6.2e-5)


if __name__ == '__main__':
    unittest.main(verbosity=1)
