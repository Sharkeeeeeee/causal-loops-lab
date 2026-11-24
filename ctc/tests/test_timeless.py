"""SPDX-License-Identifier: MIT. Loop rules in a timeless (Page-Wootters) universe: ctc/timeless/paw.py.

Run from the repository root:  python -B ctc/tests/test_timeless.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'timeless'))
from paw import BY_NAME, EXPERIMENTS, ORDERS, Model, reduced  # noqa: E402
from experiments import exact  # noqa: E402

ATOL = 1e-9
MODELS = {(e.name, o): Model(e, o) for e in EXPERIMENTS for o in ORDERS}


def p_log_given_a1(m, hist):
    rho = reduced(hist[-1], m.n, [m.regs.index('a'), m.regs.index('log')])
    return rho[3, 3].real / (rho[2, 2].real + rho[3, 3].real)


class Timeless(unittest.TestCase):
    def test_history_is_a_static_state(self):
        """The whole history satisfies the Feynman-Kitaev constraint H_FK Psi = 0: nothing evolves."""
        for m in MODELS.values():
            self.assertLess(m.constraint_residual(m.history)[0], ATOL)

    def test_constrained_histories_are_still_histories(self):
        """Every rule's output is still transported unitarily from one clock reading to the next."""
        for m in MODELS.values():
            for rule, d in (('p_ctc', None), ('pps', 'influence'), ('pps', 'clock'), ('pps', 'all')):
                h = m.state(rule, d) if d else m.state(rule)
                self.assertLess(m.constraint_residual(h)[1], 1e-8)


class SamePredictions(unittest.TestCase):
    def test_reproduces_the_circuit_model_with_either_clock(self):
        """No-loop, P-CTC and PPS (influence definition) equal experiments.exact for every hardware
        experiment, whichever of the two clocks orders the record and loop steps."""
        for (name, order), m in MODELS.items():
            ex = exact(BY_NAME[name])
            for rule, (r, d) in {'no_loop': ('no_loop', None), 'p_ctc': ('p_ctc', None),
                                 'past_preserving': ('pps', 'influence')}.items():
                j = m.joint(m.state(r, d) if d else m.state(r))
                for key, val in ex[rule].items():
                    self.assertAlmostEqual(j[key], val, delta=ATOL, msg=f'{name} {order} {rule} {key}')


class WhatCountsAsThePast(unittest.TestCase):
    def test_influence_criterion(self):
        for m in MODELS.values():
            for reg in m.written:
                self.assertEqual(m.influenced(reg), reg == 'log', f'{m.exp.name} {reg}')

    def test_clock_definition_depends_on_the_clock(self):
        """'Past = recorded at an earlier clock reading' protects the record with one clock and not
        with the other; with the second clock PPS collapses to P-CTC."""
        for name in ('grandfather', 'refusal', 'one_way', 'eraser_z'):
            a, b = MODELS[(name, 'record-first')], MODELS[(name, 'loop-first')]
            self.assertTrue(a.protected('clock'))
            self.assertFalse(b.protected('clock'))
            ja, jb = a.joint(a.state('pps', 'clock')), b.joint(b.state('pps', 'clock'))
            jp = b.joint(b.state('p_ctc'))
            self.assertGreater(max(abs(ja[k] - jb[k]) for k in ja), 0.1)
            self.assertLess(max(abs(jb[k] - jp[k]) for k in jb), ATOL)

    def test_clock_definition_lets_the_loop_change_a_partners_record(self):
        """one_way: the record is the copy a distant partner holds. Defined by clock order, the second
        clock lets the loop change it from 0.5 to 0, i.e. signalling."""
        m = MODELS[('one_way', 'loop-first')]
        self.assertAlmostEqual(m.prob(m.state('pps', 'clock'), m.T, 'rec_a'), 0.0, delta=ATOL)
        self.assertAlmostEqual(m.prob(m.state('pps', 'influence'), m.T, 'rec_a'), 0.5, delta=ATOL)

    def test_influence_definition_is_clock_independent(self):
        for e in EXPERIMENTS:
            a, b = MODELS[(e.name, 'record-first')], MODELS[(e.name, 'loop-first')]
            ja, jb = a.joint(a.state('pps', 'influence')), b.joint(b.state('pps', 'influence'))
            self.assertLess(max(abs(ja[k] - jb[k]) for k in ja), ATOL)

    def test_protecting_every_record_switches_the_loop_off(self):
        """refusal: the log is written by the loop. Protecting it too (definition 'all') freezes
        P(log | a = 1) at the no-loop 0.5; protecting only uninfluenced records gives 0."""
        for order in ORDERS:
            m = MODELS[('refusal', order)]
            self.assertAlmostEqual(p_log_given_a1(m, m.state('pps', 'all')), 0.5, delta=ATOL)
            self.assertAlmostEqual(p_log_given_a1(m, m.state('pps', 'influence')), 0.0, delta=ATOL)


class ThePastAtEveryClockReading(unittest.TestCase):
    def test_pps_keeps_recorded_facts_at_every_reading_after_preparation(self):
        """Under PPS (influence) a recorded input keeps its prior at every clock reading after it is
        prepared, including readings before the record is written (loop-first clock)."""
        for name in ('grandfather', 'refusal', 'one_way'):
            for order in ORDERS:
                m = MODELS[(name, order)]
                label = m.exp.recorded[0]
                h = m.state('pps', 'influence')
                for t in range(1, m.T + 1):
                    self.assertAlmostEqual(m.prob(h, t, label), m.exp.priors[label], delta=ATOL)

    def test_p_ctc_rewrites_readings_before_the_loop(self):
        """refusal, record-first clock: at reading 1 (before the record and before the loop) P-CTC
        already has P(a = 1) = 1/3 instead of 1/2."""
        m = MODELS[('refusal', 'record-first')]
        self.assertAlmostEqual(m.prob(m.state('p_ctc'), 1, 'a'), 1 / 3, delta=ATOL)

    def test_the_unrecorded_beginning_is_not_protected(self):
        """At clock reading 0 the input register is reset to 0 and nothing records that. Wherever
        the loop has an effect, every rule moves this reading, PPS included (refusal: 0.146)."""
        m = MODELS[('refusal', 'record-first')]
        self.assertAlmostEqual(m.prob(m.history, 0, 'a'), 0.0, delta=ATOL)
        self.assertGreater(m.prob(m.state('pps', 'influence'), 0, 'a'), 0.1)
        self.assertGreater(m.prob(m.state('p_ctc'), 0, 'a'), 0.1)
        # where PPS has no effect (Theorem 3: one_way), reading 0 is untouched
        m1 = MODELS[('one_way', 'record-first')]
        self.assertLess(m1.constraint_residual(m1.state('pps', 'influence'))[0], 1e-8)


if __name__ == '__main__':
    unittest.main(verbosity=1)
