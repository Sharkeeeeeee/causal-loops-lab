"""SPDX-License-Identifier: MIT. A time loop made by time dilation (wormhole time machine): ctc/timeless/wormhole.py.

Run from the repository root:  python -B ctc/tests/test_wormhole.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'timeless'))
from wormhole import TwinMouths, identification_error, light_clock, time_machine  # noqa: E402

ATOL = 1e-9
L_CLOCK = 0.05


def proper_time(velocity, t_end, n=20000):
    t = (np.arange(n) + 0.5) * t_end / n
    return float(sum(np.sqrt(1 - velocity(u) ** 2) for u in t) * t_end / n)


class TimeDilation(unittest.TestCase):
    """Light clocks, built only from 'light moves at speed 1', run slow when they move."""

    def test_every_photon_moves_at_the_speed_of_light(self):
        for vel in (lambda t: 0.0, TwinMouths().velocity_B):
            _, segs = light_clock(vel, 20, L_CLOCK)
            for t0, x0, y0, t1, x1, y1 in segs:
                self.assertAlmostEqual((x1 - x0) ** 2 + (y1 - y0) ** 2, (t1 - t0) ** 2, delta=1e-12)

    def test_light_clocks_measure_proper_time_and_the_twin_falls_behind(self):
        w = TwinMouths()
        n_home, _ = light_clock(lambda t: 0.0, 20, L_CLOCK)
        n_trip, _ = light_clock(w.velocity_B, 20, L_CLOCK)
        self.assertLessEqual(abs(n_home * 2 * L_CLOCK - 20), 2 * L_CLOCK + ATOL)
        self.assertLessEqual(abs(n_trip * 2 * L_CLOCK - proper_time(w.velocity_B, 20)), 2 * L_CLOCK + ATOL)
        self.assertAlmostEqual((n_home - n_trip) * 2 * L_CLOCK, w.shift(20), delta=4 * L_CLOCK)   # 4 = (1 - 0.6) * 10

    def test_dilation_factor(self):
        n0, _ = light_clock(lambda t: 0.0, 50, L_CLOCK)
        for v in (0.3, 0.6, 0.8, 0.95):
            n, _ = light_clock(lambda t, v=v: v, 50, L_CLOCK)
            self.assertAlmostEqual(n / n0, np.sqrt(1 - v * v), delta=0.01)


class TimeMachine(unittest.TestCase):
    def test_no_dilation_no_time_machine(self):
        """Without enough time dilation the wormhole never sends anything into the past far enough."""
        for v in (0.0, 0.3):
            w = TwinMouths(v=v)
            self.assertIsNone(w.horizon_formula())
            self.assertIsNone(w.horizon_on('A'))
            self.assertIsNone(w.horizon_on('B'))

    def test_chronology_horizon(self):
        """The first closed causal curve appears when the time shift reaches the distance light needs from A to
        B; the horizon on A is the same surface seen through the wormhole (A's clock = B's clock)."""
        for v in (0.5, 0.8, 0.95):
            w = TwinMouths(v=v)
            hB, hA = w.horizon_on('B'), w.horizon_on('A')
            self.assertAlmostEqual(hB, w.horizon_formula(), delta=1e-6)
            self.assertAlmostEqual(hA, w.tau_B(hB), delta=1e-6)
            self.assertAlmostEqual(w.shift(hB), w.x_B(hB), delta=1e-6)
        w = TwinMouths()
        self.assertAlmostEqual(w.horizon_on('B'), 7.5, delta=1e-6)
        self.assertAlmostEqual(w.horizon_on('A'), 4.5, delta=1e-6)
        for t in (0, 2, 4.4, 4.6, 6, 9, 15):
            self.assertEqual(w.chronology_violating(t, 0.0), t > 4.5)

    def test_the_loop_is_the_wormhole(self):
        """m goes into mouth B at F and comes out of mouth A at M, at equal proper time: F -> M is the throat."""
        s = time_machine()
        self.assertEqual(identification_error(s), (0.0, 0.0, 0.0))
        (_, tM), (_, tF) = s.pos('M'), s.pos('F')
        self.assertAlmostEqual(tF - tM, 4.0, delta=ATOL)                 # 4 lab-time units into the past
        self.assertGreater(tF, s.mouths.horizon_on('B'))
        self.assertGreater(tM, s.mouths.horizon_on('A'))
        self.assertTrue(s.worldlines_ok())


class LoopOnTheTimeMachine(unittest.TestCase):
    def setUp(self):
        self.s = time_machine()
        self.w = self.s.mouths

    def geo(self, a, b):
        (xa, ta), (xb, tb) = self.s.pos(a), self.s.pos(b)
        return self.w.in_future(ta, float(xa[0]), tb, float(xb[0]))

    def test_circuit_causality_agrees_with_the_spacetime(self):
        """Every causal relation of the circuit, the loop edge F -> M included, is a causal relation of the
        wormhole spacetime; the loop's causal future is the same set of events in both."""
        s = self.s
        for a in s.order:
            for b in s.future(a, ctc=True) - {a}:
                self.assertTrue(self.geo(a, b), f'{a} -> {b}')
        self.assertEqual({k for k in s.order if self.geo('M', k)}, set(s.future('M', ctc=True)))

    def test_chronology_violating_events(self):
        s = self.s
        geo_cv = {k for k in s.order if self.w.chronology_violating(s.pos(k)[1], float(s.pos(k)[0][0]))}
        self.assertEqual(geo_cv, {'M', 'L', 'F'})
        self.assertEqual(s.chronology_violating(), {'M', 'L', 'F'})

    def test_p_ctc_reaches_bob_through_no_path_at_all(self):
        """Bob's record is outside the causal future of every loop event, even counting every path through the
        wormhole. P-CTC still changes it (0.5 -> 1/3); PPS (Theorem 5) does not, on any slice."""
        s = self.s
        for k in ('M', 'L', 'F'):
            self.assertFalse(self.geo(k, 'B'))
        self.assertAlmostEqual(s.prob(s.history('p_ctc'), 'rec_b'), 1 / 3, delta=ATOL)
        ref = {c: s.red(s.history('no_loop'), c, s.outside_future(c)) for c in s.cuts}
        for d in ('outside_future', 'theorem4'):
            h = s.history('pps', s.protected(d))
            self.assertAlmostEqual(s.prob(h, 'rec_b'), 0.5, delta=ATOL)
            for c in s.cuts:
                if s.region <= c or not (s.region & c):
                    np.testing.assert_allclose(s.red(h, c, s.outside_future(c)), ref[c], atol=ATOL)

    def test_the_only_seam_is_the_loop_event(self):
        s = self.s
        for name, p in (('pps', s.protected('theorem4')), ('p_ctc', ())):
            init, res = s.residuals(s.history(name, p))
            self.assertLess(init, ATOL)
            for k, r in res.items():
                if k != s.seam:
                    self.assertLess(r, 1e-8, f'{name} {k}')


if __name__ == '__main__':
    unittest.main(verbosity=1)
