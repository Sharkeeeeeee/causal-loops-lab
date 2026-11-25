"""SPDX-License-Identifier: MIT. Past-preserving selection on a light-cone lattice: ctc/timeless/lightcone.py.

Run from the repository root:  python -B ctc/tests/test_lightcone.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'timeless'))
from lightcone import I2, LOOP_INPUTS, alice_alone, black_hole, bob_and_alice, random_spacetimes  # noqa: E402

ATOL = 1e-9
LOOPS = ('refusal', 'swap_write')
RANDOM = {d: random_spacetimes(d, 6) for d in (1, 2, 3)}     # 18 random spacetimes, 17-27 events each
P_CTC_BOB = {'refusal': 1 / 3, 'swap_write': 0.0}     # P(rec_b = 1) when nothing protects it


def spacetimes():
    out = [bob_and_alice(loop, alice_copy=c) for loop in LOOPS for c in (False, True)]
    return out + [alice_alone(copy, loop) for loop in LOOPS for copy in ('before', 'after')]


class Spacetime(unittest.TestCase):
    def test_locality_gives_light_cones(self):
        """Worldlines at speed <= 1 and contact interactions are enough: every causal relation lies
        inside the light cone, and events with no causal relation act on different qubits."""
        for s in spacetimes():
            self.assertLessEqual(s.max_speed(), 1)
            for a in s.order:
                for b in s.order:
                    (xa, ta), (xb, tb) = s.where(a), s.where(b)
                    if s.precedes(a, b):
                        self.assertLessEqual(abs(xb - xa), tb - ta + 1e-12)
                    elif a != b and not s.precedes(b, a):
                        self.assertFalse(set(s.events[a].qubits) & set(s.events[b].qubits))

    def test_boosts_respect_causality_and_disagree_on_simultaneity(self):
        s = bob_and_alice()
        for beta in (-0.6, 0.0, 0.6):
            pos = {k: i for i, k in enumerate(s.boost_order(beta))}
            for a, b in s.edges():
                self.assertLess(pos[a], pos[b])
        order = {beta: s.boost_order(beta) for beta in (-0.6, 0.6)}
        self.assertLess(order[-0.6].index('B'), order[-0.6].index('L'))     # Bob's record first
        self.assertGreater(order[0.6].index('B'), order[0.6].index('L'))    # Alice's loop first

    def test_one_static_state_for_every_slice(self):
        """One state per cut, the same whichever frame builds it, satisfying the initial condition and
        one Feynman-Kitaev transport constraint per event."""
        for s in spacetimes():
            init, res = s.residuals(s.history('no_loop'))
            self.assertLess(init, ATOL)
            self.assertLess(max(res.values()), ATOL)
            for c in s.cuts:
                a, b = s.evolve(c, s.boost_order(0.6)), s.evolve(c, s.boost_order(-0.6))
                self.assertLess(np.linalg.norm(a - b), ATOL)

    def test_closing_the_loop(self):
        """With the loop closed (F -> M), M, L and F are in their own causal past. The loop's causal
        future J+(M) is the same with the loop open or closed; its causal past is not."""
        s = bob_and_alice()
        self.assertEqual(s.chronology_violating(), {'M', 'L', 'F'})
        self.assertEqual(s.future('M'), s.future('M', ctc=True))
        self.assertNotIn('L', s.past('L'))
        self.assertIn('L', s.past('L', ctc=True))


class WhatCountsAsThePast(unittest.TestCase):
    def test_simultaneity_slice_depends_on_the_frame(self):
        """'Past = before the slice through L' protects Bob's spacelike record in one frame and not in
        another; where it does not, the loop changes Bob's record (signalling)."""
        for loop in LOOPS:
            s = bob_and_alice(loop)
            got = {}
            for beta in (-0.6, 0.6):
                p = s.protected('foliation', s.slice_through('L', beta))
                got[beta] = s.prob(s.history('pps', p), 'rec_b')
            self.assertAlmostEqual(got[-0.6], 0.5, delta=ATOL)
            self.assertAlmostEqual(got[0.6], P_CTC_BOB[loop], delta=ATOL)

    def test_past_cone_misses_spacelike_records(self):
        for loop in LOOPS:
            s = bob_and_alice(loop)
            self.assertEqual(s.protected('past_cone'), [])
            self.assertAlmostEqual(s.prob(s.history('pps', []), 'rec_b'), P_CTC_BOB[loop], delta=ATOL)

    def test_closed_past_cone_contains_the_loops_own_output(self):
        """With the loop closed, L is in its own past, so the log the loop writes counts as 'past'.
        Bob's record still does not, and it changes (0.5 -> 0.25)."""
        s = bob_and_alice('refusal')
        p = s.protected('past_cone_ctc')
        self.assertEqual(p, ['log'])
        self.assertAlmostEqual(s.prob(s.history('pps', p), 'rec_b'), 0.25, delta=ATOL)

    def test_outside_the_future_cone_protects_spacelike_records(self):
        for loop in LOOPS:
            for c in (False, True):
                s = bob_and_alice(loop, alice_copy=c)
                p = s.protected('outside_future')
                self.assertIn('rec_b', p)
                self.assertEqual('rec_a' in p, c)
                self.assertNotIn('rec_late', p)
                self.assertAlmostEqual(s.prob(s.history('pps', p), 'rec_b'), 0.5, delta=ATOL)

    def test_influenced_records_lie_in_the_future_cone(self):
        for s in spacetimes():
            fut = s.future(s.M, ctc=True)
            for reg, writer in s.records.items():
                if s.influenced(reg):
                    self.assertIn(writer, fut)
            self.assertTrue(set(s.protected('outside_future')) <= set(s.protected('influence')))

    def test_definitions_agree_when_the_loop_acts_on_the_recorded_input(self):
        """swap_write writes onto a, so a copy of a made after the loop is influenced: 'outside the
        future cone' and 'not influenced' pick the same records."""
        for s in [bob_and_alice('swap_write', alice_copy=c) for c in (False, True)] + \
                 [alice_alone(copy, 'swap_write') for copy in ('before', 'after')]:
            self.assertEqual(sorted(s.protected('outside_future')), sorted(s.protected('influence')))


class TheLoopStaysInsideItsFutureCone(unittest.TestCase):
    PPS = ('outside_future', 'influence')

    def outside_states(self, s, hist_or_vectors):
        return {c: s.red(hist_or_vectors, c, s.outside_future(c)) for c in s.cuts}

    def test_no_loop_input_reaches_outside_the_future_cone(self):
        """On every slice, the joint state of everything outside J+(M) is the same for every loop input."""
        for s in spacetimes():
            hists = [[(1.0, {c: s.evolve(c, mouth_gate=np.kron(prep, I2)) for c in s.cuts})] for prep in LOOP_INPUTS]
            ref = self.outside_states(s, hists[0])
            for h in hists[1:]:
                for c, rho in self.outside_states(s, h).items():
                    np.testing.assert_allclose(rho, ref[c], atol=ATOL)

    def test_pps_changes_nothing_outside_the_future_cone(self):
        """With the seam at L, on every slice the joint state of everything outside J+(M) is the no-loop
        one under PPS (either definition): the rule acts only inside the loop's future light cone."""
        for s in spacetimes():
            ref = self.outside_states(s, s.history('no_loop'))
            for d in self.PPS:
                for c, rho in self.outside_states(s, s.history('pps', s.protected(d))).items():
                    np.testing.assert_allclose(rho, ref[c], atol=ATOL, err_msg=f'{d} {sorted(c)}')

    def test_p_ctc_changes_spacelike_qubits(self):
        """P-CTC changes Bob's qubit on a slice where Bob has not recorded yet ('signalling') and his
        record on a slice where he has ('rewriting the past'). Both are outside J+(M)."""
        s = bob_and_alice('refusal')
        h = s.history('p_ctc')
        before_bob = frozenset({'H', 'S', 'M', 'L'})
        after_bob = frozenset({'H', 'S', 'M', 'B', 'L'})
        self.assertIn('b', s.outside_future(before_bob))
        self.assertIn('rec_b', s.outside_future(after_bob))
        self.assertAlmostEqual(s.prob(h, 'b', before_bob), 1 / 3, delta=ATOL)
        self.assertAlmostEqual(s.prob(h, 'rec_b', after_bob), 1 / 3, delta=ATOL)

    def test_the_only_seam_is_the_loop_event(self):
        for s in spacetimes():
            rules = [('pps', s.protected(d)) for d in self.PPS] + [('p_ctc', ())]
            for name, p in rules:
                init, res = s.residuals(s.history(name, p))
                self.assertLess(init, ATOL)
                for k, r in res.items():
                    if k != s.L:
                        self.assertLess(r, 1e-8, f'{name} {k}')


class InsideTheFutureCone(unittest.TestCase):
    def test_light_cone_rule_depends_on_where_the_copy_is(self):
        """Alice copies a before or after her loop. For the refusal loop the copy commutes with the
        loop: the two spacetimes have the same overall unitary for every loop input. 'Outside the
        future cone' still gives two different predictions (0.5 and 1/3); 'not influenced' gives one."""
        before, after = alice_alone('before'), alice_alone('after')
        for prep in LOOP_INPUTS:
            g = np.kron(prep, I2)
            np.testing.assert_allclose(before.evolve(before.final_cut, mouth_gate=g),
                                       after.evolve(after.final_cut, mouth_gate=g), atol=ATOL)
        light = [s.prob(s.history('pps', s.protected('outside_future')), 'a') for s in (before, after)]
        infl = [s.prob(s.history('pps', s.protected('influence')), 'a') for s in (before, after)]
        self.assertAlmostEqual(light[0], 0.5, delta=ATOL)
        self.assertAlmostEqual(light[1], 1 / 3, delta=ATOL)
        self.assertAlmostEqual(infl[0], 0.5, delta=ATOL)
        self.assertAlmostEqual(infl[1], 0.5, delta=ATOL)

    def test_a_record_outside_the_cone_settles_it(self):
        """When Bob holds a copy, the late copy adds nothing: all three definitions give the same final state."""
        for c in (False, True):
            s = bob_and_alice('refusal', alice_copy=c)
            a = s.final_rho(s.history('pps', s.protected('outside_future')))
            for d in ('influence', 'theorem4'):
                b = s.final_rho(s.history('pps', s.protected(d)))
                np.testing.assert_allclose(a, b, atol=ATOL)

    def test_influence_lets_a_later_choice_change_earlier_statistics(self):
        """Alice reads her log after the loop, then decides whether to copy a. 'Not influenced' protects a
        only if she copies, so her later choice moves P(log = 1), read earlier, between 1/4 and 1/3: a
        signal into her own past, outside the loop. Outside-the-cone and Theorem 4 give 1/3 either way."""
        later, never = alice_alone('after'), alice_alone(None)
        self.assertLess(later.events['L'].t, later.events['C'].t)
        infl = [s.prob(s.history('pps', s.protected('influence')), 'log') for s in (later, never)]
        self.assertAlmostEqual(infl[0], 0.25, delta=ATOL)
        self.assertAlmostEqual(infl[1], 1 / 3, delta=ATOL)
        for d in ('outside_future', 'theorem4'):
            for s in (later, never):
                self.assertAlmostEqual(s.prob(s.history('pps', s.protected(d)), 'log'), 1 / 3, delta=ATOL)


def outside_deviation(s, hist, ref, cuts):
    """Largest change of the joint state outside J+(M), over cuts that contain all of R or none of it."""
    complete = [c for c in cuts if s.region <= c or not (s.region & c)]
    return max(float(np.abs(s.red(hist, c, s.outside_future(c)) - ref[c]).max()) for c in complete)


class RandomSpacetimes(unittest.TestCase):
    """18 random spacetimes in 1, 2 and 3 spatial dimensions: random walkers, readout interactions, a time
    traveller that may meet several walkers before its last interaction (THEOREMS.md, Theorem 5)."""

    def setUp(self):
        self.rng = np.random.default_rng(5)

    def all(self):
        return [(d, s) for d, ss in RANDOM.items() for s in ss]

    def test_light_cones_in_any_dimension(self):
        for d, s in self.all():
            self.assertTrue(s.worldlines_ok())
            for a in s.order:
                for b in s.order:
                    if s.precedes(a, b):
                        self.assertTrue(s.in_light_cone(a, b), f'{d}D {a} {b}')
                    elif a != b and not s.precedes(b, a):
                        self.assertFalse(set(s.events[a].qubits) & set(s.events[b].qubits))

    def test_boosts_in_any_direction_respect_causality(self):
        for d, s in self.all():
            for _ in range(3):
                n, beta = self.rng.normal(size=d), self.rng.uniform(-0.9, 0.9)
                pos = {k: i for i, k in enumerate(s.boost_order(beta, n))}
                for a, b in s.edges():
                    self.assertLess(pos[a], pos[b])

    def test_closing_the_loop_makes_exactly_the_region_chronology_violating(self):
        sizes = []
        for d, s in self.all():
            self.assertEqual(s.chronology_violating(), set(s.region) | {s.F})
            self.assertEqual(s.future(s.M), s.future(s.M, ctc=True))
            sizes.append(len(s.region))
        self.assertGreater(max(sizes), 5)              # the time traveller meets several walkers

    def test_no_loop_input_reaches_outside_the_future_cone(self):
        for d, s in self.all():
            cuts = s.sample_cuts(self.rng, 2)
            hists = [[(1.0, {c: s.evolve(c, mouth_gate=np.kron(prep, I2)) for c in cuts})] for prep in LOOP_INPUTS]
            ref = {c: s.red(hists[0], c, s.outside_future(c)) for c in cuts}
            for h in hists[1:]:
                for c in cuts:
                    np.testing.assert_allclose(s.red(h, c, s.outside_future(c)), ref[c], atol=ATOL)

    def test_theorem5_pps_acts_only_inside_the_future_cone(self):
        """Theorem 4's split (pointer basis of the readouts outside J+(M), no record registers needed): on
        every sampled slice that contains all of R or none of it, everything outside J+(M) is exactly as
        without the loop. P-CTC changes it whenever an input was read (and the loop cares)."""
        read, moved = 0, 0
        for d, s in self.all():
            cuts = s.sample_cuts(self.rng, 3)
            ref = {c: s.red(s.history('no_loop', cuts=cuts), c, s.outside_future(c)) for c in cuts}
            self.assertLess(outside_deviation(s, s.history('pps', s.protected('theorem4'), cuts=cuts), ref, cuts), ATOL)
            if any(len(b) > 1 for b in s.pointer_blocks_of().values()):
                read += 1
                moved += outside_deviation(s, s.history('p_ctc', cuts=cuts), ref, cuts) > 1e-3
        self.assertGreaterEqual(read, 6)
        self.assertGreaterEqual(moved, 0.8 * read)

    def test_record_registers_alone_are_not_enough(self):
        """Protecting only record registers outside J+(M) fails when an input was read by a walker that
        keeps no permanent record: the rule then acts like P-CTC and changes the outside."""
        failures = 0
        for d, s in self.all():
            cuts = s.sample_cuts(self.rng, 2)
            ref = {c: s.red(s.history('no_loop', cuts=cuts), c, s.outside_future(c)) for c in cuts}
            failures += outside_deviation(s, s.history('pps', s.protected('outside_future'), cuts=cuts), ref, cuts) > 1e-3
        self.assertGreater(failures, 0)

    def test_the_only_seam_is_the_last_loop_interaction(self):
        for d, s in self.all():
            for name, p in (('pps', s.protected('theorem4')), ('p_ctc', ())):
                init, res = s.chain_breaks(name, p, self.rng, 2)
                self.assertLess(init, ATOL)
                for k, r in res.items():
                    if k != s.seam:
                        self.assertLess(r, 1e-8, f'{d}D {name} {k}')


class BlackHole(unittest.TestCase):
    """Alice's loop inside a 1 + 1 black hole (light cones tilt inward), Bob outside."""

    def test_cones_tilt_and_nothing_escapes(self):
        s = black_hole()
        self.assertTrue(s.worldlines_ok())
        for a in s.order:
            for b in s.order:
                if s.precedes(a, b):
                    self.assertTrue(s.in_light_cone(a, b))
        for k in s.future(s.M, ctc=True):
            self.assertTrue(s.cone.inside(s.pos(k)[0]))
        for k in ('M', 'L'):
            x = s.pos(k)[0][0]
            self.assertGreaterEqual(s.cone.ray(x, 100.0, -1), s.cone.h)    # the outward light ray stays inside
            self.assertFalse(s.in_light_cone(k, 'B'))
        self.assertFalse(s.cone.segment_ok(0, np.array([5.0]), 1, np.array([5.0])))   # nothing stands still inside

    def test_p_ctc_signals_out_of_the_black_hole_pps_does_not(self):
        s = black_hole()
        self.assertAlmostEqual(s.prob(s.history('p_ctc'), 'rec_b'), 1 / 3, delta=ATOL)
        ref = {c: s.red(s.history('no_loop'), c, s.outside_future(c)) for c in s.cuts}
        for d in ('outside_future', 'theorem4'):
            h = s.history('pps', s.protected(d))
            self.assertAlmostEqual(s.prob(h, 'rec_b'), 0.5, delta=ATOL)
            self.assertLess(outside_deviation(s, h, ref, s.cuts), ATOL)


if __name__ == '__main__':
    unittest.main(verbosity=1)
