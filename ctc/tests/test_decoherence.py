"""SPDX-License-Identifier: MIT. Tests for the decoherence-defined record basis (decoherence.py).

Run from the repository root:  python -B ctc/tests/test_decoherence.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from decoherence import (bob_premeasures, env_record_rule, fringe_shift, initial_state, loop_unitary,  # noqa: E402
                         marginal, record_probabilities, run, sorted_by_bob, visibility)

ATOL = 1e-9
PHI = np.pi / 2


def trace_distance(a, b):
    return 0.5 * np.sum(abs(np.linalg.eigvalsh(a - b)))


def fresh_closed_form(s):
    """Fresh photon, one environment qubit reading Z with overlap c = 1 - s:
    P(right) = d^2/2 + (1 + c^2)/2 * c^2/(2 + c^2), d^2 = 1 - c^2."""
    c = 1 - s
    return (1 - c ** 2) / 2 + (1 + c ** 2) / 2 * c ** 2 / (2 + c ** 2)


class FreshPhoton(unittest.TestCase):
    def test_past_fixed_by_decoherence(self):
        """P(right slit) goes continuously from 1/3 (no record: P-CTC) to 1/2 (perfect record: fixed)."""
        for s in (0.0, 0.1, 0.5, 0.9, 1.0):
            out, amb, d_b, d_e = run('env_record', PHI, bob=False, s=s)
            self.assertFalse(amb)
            self.assertAlmostEqual(marginal(out, d_b, d_e, 'S')[1, 1].real, fresh_closed_form(s), places=12)
        self.assertAlmostEqual(fresh_closed_form(0.0), 1 / 3, places=12)
        self.assertAlmostEqual(fresh_closed_form(1.0), 1 / 2, places=12)

    def test_records_never_rewritten(self):
        """The rule keeps the environment's record probabilities; P-CTC rewrites them."""
        for s in (0.1, 0.5, 1.0):
            base, _, d_b, d_e = run('no_loop', PHI, bob=False, s=s)
            rule, _, _, _ = run('env_record', PHI, bob=False, s=s)
            post, _, _, _ = run('p_ctc', PHI, bob=False, s=s)
            self.assertTrue(np.allclose(record_probabilities(rule, d_b, d_e), record_probabilities(base, d_b, d_e),
                                        atol=ATOL))
        self.assertGreater(abs(record_probabilities(post, d_b, d_e)[1] - record_probabilities(base, d_b, d_e)[1]),
                           0.1)


class Eraser(unittest.TestCase):
    def test_never_signals_to_or_from_bob(self):
        for pointer in ('Z', 'X'):
            for s in (0.0, 0.05, 0.5, 1.0):
                for p1 in (0.5, 0.3):
                    psi, d_b, d_e = initial_state(p1=p1, s=s, pointer=pointer, n_env=2)
                    rho = np.outer(psi, psi.conj())
                    U = loop_unitary(PHI)
                    out, _ = env_record_rule(U, rho, d_b, d_e)
                    self.assertLess(trace_distance(marginal(out, d_b, d_e, 'B'), marginal(rho, d_b, d_e, 'B')), ATOL)
                    z, _ = env_record_rule(U, bob_premeasures(rho, d_b, d_e, 'Z'), d_b, d_e)
                    x, _ = env_record_rule(U, bob_premeasures(rho, d_b, d_e, 'X'), d_b, d_e)
                    self.assertLess(trace_distance(marginal(z, d_b, d_e, 'S'), marginal(x, d_b, d_e, 'S')), ATOL)

    def test_pointer_basis_decides(self):
        """Any nonzero record by a Z-monitoring environment removes the sorted fringes;
        an X-monitoring environment gives P-CTC's shifted fringes. Bob's statistics never change."""
        for s in (0.01, 0.3, 1.0):
            out, amb, d_b, d_e = run('env_record', PHI, s=s, pointer='Z')
            self.assertFalse(amb)
            self.assertAlmostEqual(visibility(sorted_by_bob(out, d_b, d_e)), 0.0, places=10)
            out, amb, d_b, d_e = run('env_record', PHI, s=s, pointer='X')
            self.assertFalse(amb)
            sorted_hits = sorted_by_bob(out, d_b, d_e)
            self.assertAlmostEqual(visibility(sorted_hits), np.sqrt(8) / 3, places=10)
            self.assertAlmostEqual(fringe_shift(sorted_hits), np.pi / 4, places=10)

    def test_no_environment_is_ambiguous_only_at_the_symmetric_point(self):
        _, amb, _, _ = run('env_record', PHI, p1=0.5, s=0.0)
        self.assertTrue(amb)
        out, amb, d_b, d_e = run('env_record', PHI, p1=0.3, s=0.0)
        self.assertFalse(amb)        # Bob's own Z copy already selects Z
        self.assertAlmostEqual(visibility(sorted_by_bob(out, d_b, d_e)), 0.0, places=10)

    def test_no_loop_baseline(self):
        """Without a time machine the sorted visibility is the environment overlap 1 - s (Z pointer)."""
        for s in (0.0, 0.3, 1.0):
            out, _, d_b, d_e = run('no_loop', PHI, s=s, pointer='Z')
            self.assertAlmostEqual(visibility(sorted_by_bob(out, d_b, d_e)), 1 - s, places=10)


if __name__ == '__main__':
    unittest.main(verbosity=2)
