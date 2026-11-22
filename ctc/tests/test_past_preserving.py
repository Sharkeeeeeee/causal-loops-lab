"""SPDX-License-Identifier: MIT. Tests for past-preserving selection and the CTC double slit.

Run from the repository root:  python -B ctc/tests/test_past_preserving.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from circuits import bootstrap, grandfather, interference, kfk  # noqa: E402
from double_slit import (ctc_double_slit, entangled_input, fringe_shift, idler_conditional, run_entangled,  # noqa: E402
                         run_fresh, trace_out_first, trace_out_last, visibility)
from models import p_ctc  # noqa: E402
from past_preserving import apply_kraus, basis_containing, past_preserving, past_preserving_kraus, x_basis  # noqa: E402

ATOL = 1e-9
RNG = np.random.default_rng(7)


def random_unitary(d):
    z = (RNG.normal(size=(d, d)) + 1j * RNG.normal(size=(d, d))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / abs(np.diag(r)))


def random_state(d):
    v = RNG.normal(size=d) + 1j * RNG.normal(size=d)
    return np.outer(v, v.conj()) / np.vdot(v, v).real


def trace_distance(a, b):
    return 0.5 * np.sum(abs(np.linalg.eigvalsh(a - b)))


CLASSICAL = [grandfather(0.05), grandfather(0.0), kfk(0.3, 0.6, 'motivated'), kfk(0.3, 0.6, 'unconditional'),
             bootstrap()]


class Rule(unittest.TestCase):
    def test_kraus_complete(self):
        """sum K^dag K = 1: the rule is a linear, trace-preserving map."""
        cases = [(c.U, c.d_cr, c.d_loop) for c in CLASSICAL] + [(random_unitary(8), 4, 2) for _ in range(5)]
        for U, d_cr, d_loop in cases:
            for basis in (None, random_unitary(d_cr)):
                kraus = past_preserving_kraus(U, d_cr, d_loop, basis)
                total = sum(K.conj().T @ K for K in kraus)
                self.assertTrue(np.allclose(total, np.eye(d_cr), atol=ATOL))

    def test_never_signals(self):
        """Alice's rule applied to random entangled Alice-Bob states leaves Bob's state
        unchanged (Alice -> Bob), and Bob's choice of measurement before the loop does
        not show up in Alice's output (Bob -> Alice)."""
        for _ in range(10):
            U = random_unitary(8)                       # Alice CR = 2 qubits, loop = 1 qubit
            kraus = past_preserving_kraus(U, 4, 2, random_unitary(4))
            rho = random_state(8)                       # Alice (4) x Bob (2)
            out = apply_kraus(kraus, rho, d_partner=2)
            self.assertLess(trace_distance(trace_out_first(out, 4, 2), trace_out_first(rho, 4, 2)), ATOL)
            alice_outputs = []
            for basis in (np.eye(2), x_basis(1)):
                dephased = sum(np.kron(np.eye(4), np.outer(v, v.conj())) @ rho @ np.kron(np.eye(4), np.outer(v, v.conj()))
                               for v in basis.T)
                alice_outputs.append(trace_out_last(apply_kraus(kraus, dephased, d_partner=2), 4, 2))
            self.assertLess(trace_distance(*alice_outputs), ATOL)

    def test_pure_input_with_natural_basis_is_p_ctc(self):
        for c in (interference(0.5, 1.2), interference(0.3, np.pi / 2), bootstrap()):
            psi = np.linalg.eigh(c.rho)[1][:, -1]
            out = past_preserving(c.U, c.rho, c.d_cr, c.d_loop, basis_containing(psi))
            self.assertTrue(np.allclose(out, p_ctc(c.U, c.rho, c.d_cr, c.d_loop)[0], atol=ATOL), c.name)


class Scenarios(unittest.TestCase):
    def test_grandfather_is_unaffected(self):
        """The past (whether the gun jams) keeps its probability eps; the paradox world
        falls back to a mixed message. Contrast: P-CTC forces P(jam) = 1."""
        for eps in (0.0, 0.05, 0.4):
            c = grandfather(eps)
            out = past_preserving(c.U, c.rho, c.d_cr, c.d_loop)
            self.assertAlmostEqual(c.probability_one(out, 'jam'), eps, places=12)

    def test_kfk_past_fixed_future_changed(self):
        """P(bad tendency) stays q; P(bad outcome) = q (1 - r/2) for the motivated sender
        (the world 'bad, reminder works' has no consistent history and falls back)."""
        q, r = 0.3, 0.6
        c = kfk(q, r, 'motivated')
        out = past_preserving(c.U, c.rho, c.d_cr, c.d_loop)
        self.assertAlmostEqual(c.probability_one(out, 'bad'), q, places=12)
        self.assertAlmostEqual(c.probability_one(out, 'outcome'), q * (1 - r / 2), places=12)
        u = kfk(q, r, 'unconditional')
        self.assertAlmostEqual(u.probability_one(past_preserving(u.U, u.rho, u.d_cr, u.d_loop), 'outcome'),
                               q * (1 - r), places=12)


class DoubleSlit(unittest.TestCase):
    def test_no_time_machine_gives_full_fringes(self):
        c = ctc_double_slit(0.5, np.pi / 2)
        self.assertAlmostEqual(visibility(run_fresh(c, 'no_loop')), 1.0, places=12)

    def test_fresh_photon(self):
        """phi = pi/2: P-CTC (= past-preserving for a pure photon) moves the bright fringe
        by pi/4 and gives P(right slit) = 1/3; D-CTC keeps P(right) = 1/2 and lowers the
        visibility to 1/sqrt(2). phi = pi: P-CTC closes the right slit."""
        c = ctc_double_slit(0.5, np.pi / 2)
        for rule in ('p_ctc', 'past_pure'):
            out = run_fresh(c, rule)
            self.assertAlmostEqual(out[1, 1].real, 1 / 3, places=12)
            self.assertAlmostEqual(fringe_shift(out), np.pi / 4, places=12)
            self.assertAlmostEqual(visibility(out), np.sqrt(8) / 3, places=12)
        d = run_fresh(c, 'd_ctc')
        self.assertAlmostEqual(d[1, 1].real, 0.5, places=12)
        self.assertAlmostEqual(visibility(d), 1 / np.sqrt(2), places=12)
        self.assertAlmostEqual(run_fresh(ctc_double_slit(0.5, np.pi), 'p_ctc')[1, 1].real, 0.0, places=12)

    def test_eraser(self):
        """Photon entangled with Bob's idler, phi = pi/2. Every rule: the screen as a whole
        shows no fringes. Sorted by Bob's later X result:
          no loop          -> full fringes, no shift
          P-CTC            -> fringes shifted by pi/4, but Bob's own statistics change (signalling)
          past-preserving X-> the same shifted fringes, and Bob's statistics do not change
          past-preserving Z-> no fringes even after sorting (the loop acts as a which-path record)."""
        c = ctc_double_slit(0.5, np.pi / 2)
        prior_bob = trace_out_first(entangled_input(0.5), 2, 2)
        outs = {rule: run_entangled(c, rule) for rule in ('no_loop', 'p_ctc', 'past_X', 'past_Z')}
        for rule, out in outs.items():
            self.assertAlmostEqual(visibility(trace_out_last(out, 2, 2)), 0.0, places=12, msg=rule)
        self.assertAlmostEqual(visibility(idler_conditional(outs['no_loop'], 'X+')), 1.0, places=12)
        for rule in ('p_ctc', 'past_X'):
            sorted_hits = idler_conditional(outs[rule], 'X+')
            self.assertAlmostEqual(fringe_shift(sorted_hits), np.pi / 4, places=12, msg=rule)
            self.assertAlmostEqual(visibility(sorted_hits), np.sqrt(8) / 3, places=12, msg=rule)
        self.assertAlmostEqual(trace_distance(trace_out_first(outs['p_ctc'], 2, 2), prior_bob), 1 / 6, places=12)
        self.assertLess(trace_distance(trace_out_first(outs['past_X'], 2, 2), prior_bob), ATOL)
        self.assertAlmostEqual(visibility(idler_conditional(outs['past_Z'], 'X+')), 0.0, places=12)

    def test_record_basis_matters(self):
        """The preparation problem, concretely: for the entangled photon both Z and X are
        eigenbases of the path's reduced state (1/2), yet they predict different data."""
        c = ctc_double_slit(0.5, np.pi / 2)
        a = idler_conditional(run_entangled(c, 'past_X'), 'X+')
        b = idler_conditional(run_entangled(c, 'past_Z'), 'X+')
        self.assertGreater(abs(visibility(a) - visibility(b)), 0.5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
