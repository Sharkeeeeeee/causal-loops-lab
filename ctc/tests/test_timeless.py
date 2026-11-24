"""SPDX-License-Identifier: MIT. Loop rules in a timeless (Page-Wootters) universe: ctc/timeless/paw.py.

Run from the repository root:  python -B ctc/tests/test_timeless.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'timeless'))
from paw import BY_NAME, EXPERIMENTS, ORDERS, Model, reduced  # noqa: E402
from experiments import exact, initial_state  # noqa: E402
from past_preserving import apply_kraus, past_preserving_kraus  # noqa: E402

ATOL = 1e-9
MODELS = {(e.name, o): Model(e, o) for e in EXPERIMENTS for o in ORDERS}


def p_log_given_a1(m, hist):
    rho = m.reduced_at(hist, -1, ['a', 'log'])
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
        """No-loop and P-CTC equal experiments.exact for every hardware experiment, whichever of the two
        clocks orders the record and loop steps."""
        for (name, order), m in MODELS.items():
            ex = exact(BY_NAME[name])
            for rule in ('no_loop', 'p_ctc'):
                j = m.joint(m.state(rule))
                for key, val in ex[rule].items():
                    self.assertAlmostEqual(j[key], val, delta=ATOL, msg=f'{name} {order} {rule} {key}')

    def test_pps_equals_the_circuit_rule_in_the_pointer_basis(self):
        """PPS (influence definition) equals the circuit-model rule with the pointer basis of the record
        CNOTs (Z), as a full density matrix on CR and records, for every experiment and both clocks.
        For eraser_x/y this differs from the hardware design's X record basis (Theorem 4)."""
        for (name, order), m in MODELS.items():
            exp = BY_NAME[name]
            d, d_r = exp.d_cr, 2 ** len(exp.recorded)
            kraus = past_preserving_kraus(exp.unitary(), d, 2, np.eye(d))
            circuit = apply_kraus(kraus, initial_state(exp), d_r)
            paw = m.reduced_at(m.state('pps', 'influence'), -1, [r for r in m.regs if r not in ('m', 'p')])
            np.testing.assert_allclose(paw, circuit, atol=ATOL, err_msg=f'{name} {order}')


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

    def test_global_back_propagation_moves_the_beginning(self):
        """Spreading the rule back over the whole history moves clock reading 0 (all registers reset,
        nothing recorded): P-CTC and PPS in refusal, and even PPS in one_way, where the loop has no
        effect at all (each sector's history goes back to a different reading 0)."""
        m = MODELS[('refusal', 'record-first')]
        self.assertAlmostEqual(m.prob(m.history, 0, 'a'), 0.0, delta=ATOL)
        self.assertGreater(m.prob(m.state('p_ctc'), 0, 'a'), 0.1)
        self.assertGreater(m.prob(m.state('pps', 'influence'), 0, 'a'), 0.1)
        m1 = MODELS[('one_way', 'record-first')]
        self.assertGreater(m1.constraint_residual(m1.state('pps', 'influence'))[0], 0.1)


class SeamAtTheLoopEvent(unittest.TestCase):
    RULES = (('pps', 'influence'), ('p_ctc', None))

    def test_initial_condition_holds_and_the_only_break_is_the_loop_event(self):
        for m in MODELS.values():
            for rule, d in self.RULES:
                init, breaks = m.step_breaks(m.state_seam(rule, d))
                self.assertLess(init, ATOL)
                for t, b in enumerate(breaks, 1):
                    if t != m.step_of['loop']:
                        self.assertLess(b, 1e-8, f'{m.exp.name} {m.order} {rule} step {t}')

    def test_final_predictions_are_unchanged(self):
        for m in MODELS.values():
            for rule, d in self.RULES:
                g = m.state(rule, d) if d else m.state(rule)
                s = m.state_seam(rule, d)
                a, b = m.joint(g), m.joint(s)
                self.assertLess(max(abs(a[k] - b[k]) for k in a), ATOL)

    def test_pps_changes_nothing_the_loop_does_not_touch(self):
        """Across the seam, under PPS with the pointer basis, no record and no register outside the loop
        interaction changes: the discontinuity is local to the loop event."""
        for m in MODELS.values():
            h = m.state_seam('pps', 'influence')
            for reg in m.regs:
                if reg not in m.support_of_loop():
                    self.assertLess(m.jump(h, reg), 1e-9, f'{m.exp.name} {m.order} {reg}')

    def test_p_ctc_changes_records_it_never_touches(self):
        """Under P-CTC, an existing record outside the loop interaction jumps at the seam (record-first
        clock): P-CTC cannot be made local; it has to rewrite the past."""
        for name, size in (('one_way', 0.5), ('grandfather', 0.8), ('refusal', 1 / 6)):
            m = MODELS[(name, 'record-first')]
            reg = 'rec_' + m.exp.recorded[0]
            self.assertAlmostEqual(m.jump(m.state_seam('p_ctc'), reg), size, delta=1e-9)


if __name__ == '__main__':
    unittest.main(verbosity=1)
