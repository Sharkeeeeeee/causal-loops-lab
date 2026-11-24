"""SPDX-License-Identifier: MIT. Local clocks and a superposed clock: ctc/timeless/clocks.py.

Run from the repository root:  python -B ctc/tests/test_clocks.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'timeless'))
from clocks import CP_HALF_PI, ONE_WAY, LocalClocks, QuantumSwitch  # noqa: E402

ATOL = 1e-9


def conditional(model, final, reg, P):
    v = P @ final
    return model.prob(v / np.linalg.norm(v), reg)


class LocalClockSystem(unittest.TestCase):
    def setUp(self):
        self.models = {'one_way': LocalClocks(ONE_WAY), 'eraser': LocalClocks(CP_HALF_PI)}
        self.p_ctc_bob = {'one_way': 0.0, 'eraser': 1 / 3}   # P(rec_b = 1); eraser: Bob's Z = 0 goes to 2/3

    def test_one_static_state_two_clock_constraints(self):
        for m in self.models.values():
            J_A, J_B, H_in = m.constraints()
            v = m.global_vector(m.rule('no_loop'))
            for J in (J_A, J_B, H_in):
                self.assertLess(np.linalg.norm(J @ v), ATOL)
            self.assertLess(np.linalg.norm(J_A @ J_B - J_B @ J_A), ATOL)

    def test_p_ctc_changes_bobs_record_in_every_frame(self):
        """Bob-first frame: at (0, 1) Bob's record exists and Alice's loop has not happened, yet P-CTC has
        already changed it ("rewrote the past"). Alice-first frame: the same number at the end ("signalling")."""
        for name, m in self.models.items():
            h = m.rule('p_ctc')
            self.assertAlmostEqual(m.prob(h[(0, 1)], 'rec_b'), self.p_ctc_bob[name], delta=ATOL)
            self.assertAlmostEqual(m.prob(h[(1, 1)], 'rec_b'), self.p_ctc_bob[name], delta=ATOL)

    def test_clock_definition_depends_on_the_frame(self):
        for name, m in self.models.items():
            bob_first = m.rule('pps', m.clock_sectors('Bob first'))
            alice_first = m.rule('pps', m.clock_sectors('Alice first'))
            self.assertAlmostEqual(m.prob(bob_first[(1, 1)], 'rec_b'), 0.5, delta=ATOL)
            self.assertAlmostEqual(m.prob(alice_first[(1, 1)], 'rec_b'), self.p_ctc_bob[name], delta=ATOL)

    def test_influence_definition_needs_no_frame(self):
        for m in self.models.values():
            h = m.rule('pps', m.influence_sectors(['rec_b']))
            for pt in m.points:
                self.assertAlmostEqual(m.prob(h[pt], 'b'), 0.5, delta=ATOL)
            self.assertAlmostEqual(m.prob(h[(1, 1)], 'rec_b'), 0.5, delta=ATOL)


class SuperposedClock(unittest.TestCase):
    def test_recorded_order_definitions_agree(self):
        """When the order is itself recorded (rec_c), 'past by clock order' and 'past by influence' coincide."""
        for bob in (True, False):
            s = QuantumSwitch('classical', 0.3, bob=bob)
            a = s.rule('pps', s.clock_sectors())[2]
            b = s.rule('pps', s.influence_sectors(s.candidates()))[2]
            self.assertLess(np.linalg.norm(a - b), 1e-8)
            splits = {tuple(sorted(u)) for _, u in s.last_influence_split}
            self.assertIn(tuple(sorted(['rec', 'rec_c'] + (['rec_b'] if bob else []))), splits)   # rec protected when rec_c = 0
            self.assertIn(tuple(sorted(['rec_c'] + (['rec_b'] if bob else []))), splits)          # not when rec_c = 1

    def test_indefinite_order_clock_definition_disturbs_the_order(self):
        """Fresh qubit, order unrecorded. The clock definition must split by c and changes the order's
        interference P(c = +) from 0.75 to 0.709; the influence definition leaves it at 0.75."""
        s = QuantumSwitch('coherent', 0.3, bob=False)
        no_loop = s.x_plus(s.rule('no_loop')[2], 'c')
        clock = s.x_plus(s.rule('pps', s.clock_sectors())[2], 'c')
        infl = s.x_plus(s.rule('pps', s.influence_sectors(s.candidates()))[2], 'c')
        self.assertAlmostEqual(no_loop, 0.75, delta=ATOL)
        self.assertAlmostEqual(infl, no_loop, delta=ATOL)
        self.assertLess(clock, no_loop - 0.03)

    def test_indefinite_order_record_is_not_past(self):
        """Influence: the record is written by the loop in one branch, so it is not past anywhere, and the
        fresh qubit is selected as under P-CTC. Clock: the c = 0 branch keeps its prior."""
        s = QuantumSwitch('coherent', 0.3, bob=False)
        infl_sectors = s.influence_sectors(s.candidates())
        self.assertEqual([sorted(u) for _, u in s.last_influence_split], [[]])
        c0 = s.proj('c', 0)
        self.assertAlmostEqual(conditional(s, s.rule('pps', infl_sectors)[2], 'rec', c0), 0.0, delta=ATOL)
        self.assertAlmostEqual(conditional(s, s.rule('pps', s.clock_sectors())[2], 'rec', c0), 0.3, delta=ATOL)

    def test_no_signalling_to_a_partner_with_a_prior_copy(self):
        """Bob copied a before anything else. Both PPS definitions keep his record; P-CTC changes it."""
        for variant in ('coherent', 'classical'):
            s = QuantumSwitch(variant, 0.3, bob=True)
            for sectors in (s.clock_sectors(), s.influence_sectors(s.candidates())):
                self.assertAlmostEqual(s.prob(s.rule('pps', sectors)[2], 'rec_b'), 0.3, delta=ATOL)
            self.assertAlmostEqual(s.prob(s.rule('p_ctc')[2], 'rec_b'), 0.0, delta=ATOL)


if __name__ == '__main__':
    unittest.main(verbosity=1)
