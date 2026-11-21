"""SPDX-License-Identifier: MIT. Quantum-only effects that the classical branch model cannot show.

Run from the repository root:  python -B ctc/tests/test_quantum_effects.py
All closed forms here are derived in this project (see ctc/QUANTUM_EFFECTS.md).
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import d_ctc, no_loop, p_ctc, p_ctc_by_teleportation  # noqa: E402
from circuits import bit_state, interference, phase_only_loop  # noqa: E402
from branches import output_state  # noqa: E402

ATOL = 1e-10


def run(c):
    base = no_loop(c.U, c.rho, c.d_cr, c.d_loop, c.baseline_loop)
    post, _ = p_ctc(c.U, c.rho, c.d_cr, c.d_loop)
    deutsch, _, _ = d_ctc(c.U, c.rho, c.d_cr, c.d_loop)
    return base, post, deutsch


def p_ctc_closed_form(p1, phi):
    """P(a = 1) = p1 cos^2(phi/2) / ((1 - p1) + p1 cos^2(phi/2))."""
    w = p1 * np.cos(phi / 2) ** 2
    return w / ((1 - p1) + w)


class Interference(unittest.TestCase):
    def test_cz_deletes_a_consistent_branch(self):
        """CZ: both message values are consistent, yet P-CTC removes the a = 1 branch."""
        for p1 in (0.1, 0.5, 0.9):
            c = interference(p1, np.pi)
            base, post, deutsch = run(c)
            self.assertAlmostEqual(c.probability_one(post, 'a'), 0.0, places=10)
            self.assertAlmostEqual(c.probability_one(base, 'a'), p1, places=10)
            self.assertAlmostEqual(c.probability_one(deutsch, 'a'), p1, places=10)

    def test_phase_reweights_the_world_continuously(self):
        for p1 in (0.2, 0.7):
            for phi in np.linspace(0, np.pi * 0.98, 9):
                c = interference(p1, phi)
                _, post, deutsch = run(c)
                self.assertAlmostEqual(c.probability_one(post, 'a'), p_ctc_closed_form(p1, phi), places=10)
                self.assertAlmostEqual(c.probability_one(deutsch, 'a'), p1, places=10)

    def test_deletion_happens_even_for_a_classical_input(self):
        """The cancellation is between the two message histories, so dephasing `a` first
        does not prevent it."""
        c = interference(0.4, np.pi)
        c.rho = bit_state(0.4)
        _, post, _ = run(c)
        self.assertAlmostEqual(c.probability_one(post, 'a'), 0.0, places=10)

    def test_teleportation_simulation_agrees(self):
        for phi in (0.0, 1.0, 2.5):
            c = interference(0.6, phi)
            _, post, _ = run(c)
            tele, _ = p_ctc_by_teleportation(c.U, c.rho, c.d_cr, c.d_loop)
            self.assertTrue(np.allclose(post, tele, atol=ATOL))

    def test_deutsch_keeps_weights_but_destroys_coherence(self):
        c = interference(0.5, np.pi)
        _, _, deutsch = run(c)
        self.assertAlmostEqual(c.expectation_x(deutsch, 'a'), 0.0, places=10)
        self.assertAlmostEqual(c.expectation_x(c.rho, 'a'), 1.0, places=10)

    def test_classical_model_refuses_phase_gates(self):
        """branches.py must not read the -1 phase as an ordinary classical move."""
        c = interference(0.4, np.pi)
        c.rho = bit_state(0.4)
        with self.assertRaises(ValueError):
            output_state(c, 1, np.inf)


class PhaseOnlyLoop(unittest.TestCase):
    def test_p_ctc_undefined_without_any_contradiction(self):
        c = phase_only_loop()
        _, post, deutsch = run(c)
        self.assertIsNone(post)
        self.assertTrue(np.allclose(deutsch, c.rho, atol=ATOL))


if __name__ == '__main__':
    unittest.main(verbosity=2)
