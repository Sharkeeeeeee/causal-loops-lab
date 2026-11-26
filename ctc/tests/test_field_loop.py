"""SPDX-License-Identifier: MIT. Checks for the field-mode toy of ctc/FIELD_LOOP.md (ctc/field_loop.py).

Run from the repository root:  python -B ctc/tests/test_field_loop.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from field_loop import (dctc_thermal_energy, fock_weak_energy, li2, pps_thermal_energy,  # noqa: E402
                        truncated_model, vacuum_energy_continuum, vacuum_weak_energy, weak_loop_number)
from models import d_ctc  # noqa: E402

N = 22


def fock(k, n=N):
    r = np.zeros((n, n))
    r[k, k] = 1
    return r


class SingleMode(unittest.TestCase):
    def test_vacuum_weak_energy_matches_the_winding_sum(self):
        for theta in (1.0, 1.2):
            for phi in (0.0, 0.7, 2.0):
                U, nb = truncated_model(theta, phi, N)
                w = weak_loop_number(U, nb, fock(0), N)
                self.assertAlmostEqual(w, vacuum_weak_energy(theta, phi), delta=1e-4)   # Fock-space truncation

    def test_fock_worlds_add_the_classical_cavity_enhancement(self):
        for phi in (0.0, 0.7):
            U, nb = truncated_model(1.2, phi, N)
            for k in (1, 2, 3):
                w = weak_loop_number(U, nb, fock(k), N)
                self.assertAlmostEqual(w.real, fock_weak_energy(1.2, phi, k).real, delta=1e-2)

    def test_vacuum_energy_can_be_negative(self):
        """Off resonance (cos phi < cos theta) the loop's weak energy is negative."""
        self.assertLess(vacuum_weak_energy(1.0, 2.0).real, 0)
        self.assertGreater(vacuum_weak_energy(1.0, 0.0).real, 0)

    def test_dctc_keeps_the_vacuum_and_the_thermal_mean(self):
        n = 9
        U, nb = truncated_model(1.0, 0.0, n)
        _, tau, _ = d_ctc(U, fock(0, n), n, n)
        self.assertLess(abs(np.trace(tau @ nb)), 1e-9)
        nbar = 0.2
        p = (nbar / (1 + nbar)) ** np.arange(n) / (1 + nbar)
        _, tau, _ = d_ctc(U, np.diag(p / p.sum()), n, n)
        self.assertAlmostEqual(np.trace(tau @ nb).real, dctc_thermal_energy(nbar), delta=5e-3)

    def test_pps_on_a_thermal_input_differs_from_global_pctc(self):
        nbar = 0.5
        p = (nbar / (1 + nbar)) ** np.arange(N) / (1 + nbar)
        rho = np.diag(p / p.sum())
        U, nb = truncated_model(1.2, 0.0, N)
        pps = sum(p[k] * weak_loop_number(U, nb, fock(k), N).real for k in range(8)) / p[:8].sum()
        self.assertAlmostEqual(pps, pps_thermal_energy(1.2, 0.0, nbar), delta=2e-2)
        self.assertGreater(abs(pps - weak_loop_number(U, nb, rho, N).real), 0.01)   # 1.636 vs 1.619


class ContinuumOfModes(unittest.TestCase):
    def test_vacuum_energy_scales_like_minus_li2_over_delta_squared(self):
        for c in (0.3, 0.6, 0.9):
            for delta in (0.5, 0.2, 0.1):
                e = vacuum_energy_continuum(c, delta, eps=1e-4)
                self.assertAlmostEqual(e * delta ** 2, -li2(c), delta=1e-3)

    def test_it_diverges_at_the_chronology_horizon(self):
        values = [vacuum_energy_continuum(0.6, d, eps=1e-5) for d in (0.4, 0.1, 0.025)]
        self.assertTrue(values[0] > values[1] > values[2])
        self.assertAlmostEqual(values[2] / values[1], 16, delta=0.05)


if __name__ == '__main__':
    unittest.main(verbosity=2)
