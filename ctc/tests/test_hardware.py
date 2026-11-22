"""SPDX-License-Identifier: MIT. Checks for the hardware experiments in ctc/hardware/.

The gate-level tests need qiskit and are skipped without it.
Run from the repository root:  python -B ctc/tests/test_hardware.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'hardware'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from double_slit import ctc_double_slit, fringe_shift, idler_conditional, run_entangled, trace_out_first, visibility  # noqa: E402,E501
from experiments import (BY_NAME, EXPERIMENTS, RULES, build_circuit, build_unitary_circuit,  # noqa: E402
                         estimate_from_tally, exact, fallback_matches_no_loop, fringe, headline_values, parse)
from preregister import eraser_exact  # noqa: E402

try:
    import qiskit  # noqa: F401
    HAVE_QISKIT = True
except ImportError:
    HAVE_QISKIT = False

EXPECTED = {   # exact headline values: no loop, P-CTC, past-preserving
    'grandfather': [[0.2], [1.0], [0.2]],
    'refusal': [[0.5, 0.5, 0.5], [1 / 3, 0.0, 0.5], [0.5, 0.0, 0.5]],
    'one_way': [[0.5], [0.0], [0.5]],
}


class Exact(unittest.TestCase):
    def test_classical_headlines(self):
        for name, expected_by_rule in EXPECTED.items():
            exp = BY_NAME[name]
            theory = exact(exp)
            for rule, expected in zip(RULES, expected_by_rule):
                self.assertTrue(np.allclose(headline_values(exp, theory[rule]), expected, atol=1e-9),
                                (exp.name, rule))

    def test_fallback_readable_from_data(self):
        for exp in EXPERIMENTS:
            self.assertTrue(fallback_matches_no_loop(exp), exp.name)

    def test_eraser_matches_double_slit_module(self):
        """Independent route: ctc/double_slit.py (phi = pi/2). Past-preserving with X record and
        P-CTC must give the same Bob-sorted fringe and Bob statistics there and here."""
        c = ctc_double_slit(0.5, np.pi / 2)
        ours = eraser_exact()
        for rule, theirs_rule in (('p_ctc', 'p_ctc'), ('past_preserving', 'past_X')):
            out = run_entangled(c, theirs_rule)
            cond = idler_conditional(out, 'X+')
            v, s = ours[rule]['sorted']
            self.assertAlmostEqual(v, visibility(cond), places=9)
            self.assertAlmostEqual(s, fringe_shift(cond), places=9)
            bob = trace_out_first(out, 2, 2)
            bob_plus = float(np.real(np.array([1, 1]) @ bob @ np.array([1, 1])) / 2)
            hx = headline_values(BY_NAME['eraser_x'], exact(BY_NAME['eraser_x'])[rule])
            self.assertAlmostEqual(hx[0], bob_plus, places=9)
        self.assertAlmostEqual(ours['past_preserving']['sorted'][0], np.sqrt(8) / 3, places=9)   # 0.943
        self.assertAlmostEqual(ours['past_preserving']['sorted'][1], np.pi / 4, places=9)


@unittest.skipUnless(HAVE_QISKIT, 'qiskit not installed')
class Gates(unittest.TestCase):
    def gate_unitary(self, exp):
        from qiskit.quantum_info import Operator
        return Operator(build_unitary_circuit(exp)).reverse_qargs().data

    def test_gates_implement_unitary_up_to_phases(self):
        for exp in EXPERIMENTS:
            G = self.gate_unitary(exp)
            self.assertTrue(np.allclose(abs(G), abs(exp.unitary()), atol=1e-9), exp.name)
            if exp.name != 'refusal':
                self.assertTrue(np.allclose(G, exp.unitary(), atol=1e-9), exp.name)

    def test_relative_phase_does_not_matter(self):
        """The refusal circuit uses a relative-phase Toffoli. All three rules give identical
        predictions with the gate-level unitary (phases included) and the permutation."""
        for exp in EXPERIMENTS:
            a, b = exact(exp), exact(exp, U=self.gate_unitary(exp))
            for rule in RULES:
                for key in a[rule]:
                    self.assertAlmostEqual(a[rule][key], b[rule][key], places=9, msg=(exp.name, rule, key))

    def test_estimators_recover_exact_predictions(self):
        """Feed the exact outcome probabilities of the full circuit (no shot noise) into the
        estimators: all three rules must come out exactly as predicted."""
        from qiskit.quantum_info import Statevector
        for exp in EXPERIMENTS:
            qc = build_circuit(exp).remove_final_measurements(inplace=False)
            probs = Statevector(qc).probabilities_dict()
            n = np.zeros((2 ** len(exp.recorded), exp.d_cr, 2))
            for bitstring, p in probs.items():
                k, y, ok = parse(exp, bitstring)
                n[sum(b << (len(k) - 1 - j) for j, b in enumerate(k)), y, int(ok)] += p
            measured = estimate_from_tally(exp, n)
            theory = exact(exp, U=self.gate_unitary(exp))
            for rule in RULES:
                for key, value in theory[rule].items():
                    self.assertAlmostEqual(measured[rule][key], value, places=9, msg=(exp.name, rule, key))


class Readout(unittest.TestCase):
    def test_correction_undoes_known_bit_flips(self):
        from analyze import readout_correct
        rng = np.random.default_rng(3)
        n = 5
        e0, e1 = rng.uniform(0.005, 0.03, n), rng.uniform(0.01, 0.06, n)
        true = rng.dirichlet(np.ones(2 ** n))

        def noisy(p):
            out = np.zeros_like(p)
            for idx, value in enumerate(p):
                for jdx in range(2 ** n):
                    prob = 1.0
                    for i in range(n):
                        b, r = (idx >> i) & 1, (jdx >> i) & 1
                        flip = e1[i] if b else e0[i]
                        prob *= flip if b != r else 1 - flip
                    out[jdx] += value * prob
            return out

        def as_counts(p, shots=10 ** 6):
            return {format(i, f'0{n}b'): v * shots for i, v in enumerate(p)}

        zeros = as_counts(noisy(np.eye(2 ** n)[0]))
        ones = as_counts(noisy(np.eye(2 ** n)[-1]))
        fixed, rates = readout_correct(as_counts(noisy(true)), zeros, ones)
        recovered = np.zeros(2 ** n)
        for bitstring, c in fixed.items():
            recovered[int(bitstring, 2)] = c
        self.assertTrue(np.allclose(recovered / recovered.sum(), true, atol=1e-9))
        self.assertTrue(np.allclose(rates['e0'], e0) and np.allclose(rates['e1'], e1))


class Fringe(unittest.TestCase):
    def test_fringe_helper(self):
        v, s = fringe((1 + np.cos(0.3) * 0.8) / 2, (1 + np.sin(0.3) * 0.8) / 2)
        self.assertAlmostEqual(v, 0.8)
        self.assertAlmostEqual(s, 0.3)


if __name__ == '__main__':
    unittest.main(verbosity=1)
