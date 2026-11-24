"""SPDX-License-Identifier: MIT. Checks for the direct pure-vs-recorded test (ctc/born_rule/direct_test.py).

The key claim: for standard quantum mechanics with ANY linear noise (random CPTP errors on every
gate, random readout confusion, different noise in the two groups), the signal S is exactly 0;
while the loop model's reweighting of isolated superpositions shows up in S at full size.

Run from the repository root:  python -B ctc/tests/test_born_direct.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'born_rule'))
from direct_test import THETAS, analyze, prep_systematic, signal  # noqa: E402
from model import two_path_shift  # noqa: E402

RNG = np.random.default_rng(11)
CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], complex)


def ry(theta):
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], complex)


def random_channel(d, k=3, strength=0.05):
    """Random CPTP map close to the identity, as a list of Kraus operators."""
    z = (RNG.normal(size=(d * k, d)) + 1j * RNG.normal(size=(d * k, d)))
    v = np.zeros((d * k, d), complex)
    v[:d] = np.eye(d)
    v = v + strength * z
    q, r = np.linalg.qr(v)
    q = q * (np.diag(r) / abs(np.diag(r)))
    return [q[i * d:(i + 1) * d] for i in range(k)]


def apply(kraus, rho):
    return sum(K @ rho @ K.conj().T for K in kraus)


def confusion():
    e0, e1 = RNG.uniform(0.005, 0.04, 2)
    return np.array([[1 - e0, e1], [e0, 1 - e1]])


def p_q1(rho, conf_q, conf_r):
    """P(q reads 1) after readout confusion on both qubits (r's confusion does not matter, kept for realism)."""
    diag = np.real(np.diag(rho)).reshape(2, 2)            # [q, r]
    pq = diag.sum(axis=1)
    return float((conf_q @ pq)[1])


def simulate(noise, theta, group, model=None, prep_error=0.0):
    rho = np.zeros((4, 4), complex)
    rho[0, 0] = 1
    U = np.kron(ry(theta * (1 + prep_error)), np.eye(2))
    rho = apply(noise['prep'], U @ rho @ U.conj().T)
    if group == 'B':
        rho = apply(noise['cnot'], CNOT @ rho @ CNOT.conj().T)
    else:
        rho = apply(noise['idle'], rho)
    p = p_q1(rho, noise['conf_q'][group], noise['conf_r'])
    if model is not None and group == 'A' and abs(np.sin(theta)) > 1e-9:
        eps, phi = model                       # isolated superposition reweighted (Z coupling on |1>)
        p += two_path_shift(np.sin(theta / 2) ** 2, phi, eps)
    return p


def make_noise():
    return dict(prep=random_channel(4), cnot=random_channel(4, strength=0.1), idle=random_channel(4),
                conf_q={'A': confusion(), 'B': confusion()}, conf_r=confusion())


class Cancellation(unittest.TestCase):
    def test_any_linear_noise_gives_exactly_zero(self):
        for _ in range(50):
            noise = make_noise()
            p = {(g, t): simulate(noise, th, g) for g in 'AB' for t, th in THETAS.items()}
            self.assertAlmostEqual(signal(p), 0.0, places=12)

    def test_naive_difference_is_not_zero(self):
        """Without the endpoint and +/- subtraction, CNOT errors would fake a signal."""
        noise = make_noise()
        naive = simulate(noise, np.pi / 2, 'A') - simulate(noise, np.pi / 2, 'B')
        self.assertGreater(abs(naive), 1e-3)

    def test_preparation_miscalibration_is_estimated_exactly(self):
        """An over-rotated RY leaves a first-order S; prep_systematic recovers it from the data."""
        for _ in range(20):
            noise = make_noise()
            p = {(g, t): simulate(noise, th, g, prep_error=0.01) for g in 'AB' for t, th in THETAS.items()}
            self.assertGreater(abs(signal(p)), 1e-6)
            self.assertAlmostEqual(signal(p), prep_systematic(p), places=10)

    def test_model_effect_is_recovered(self):
        for eps, phi in ((1.0, 0.3), (0.2, np.pi / 2), (0.01, 1.0)):
            noise = make_noise()
            p = {(g, t): simulate(noise, th, g, model=(eps, phi)) for g in 'AB' for t, th in THETAS.items()}
            self.assertAlmostEqual(signal(p), two_path_shift(0.5, phi, eps), places=10)


class VirtualFrameFlaw(unittest.TestCase):
    """The first hardware run's flaw: +/- pi/2 were the same physical pulse (the sign was a virtual
    frame change), so crosstalk in group B that rotates q about a lab-frame axis was not cancelled.
    The physical control flips the coherence with real pulses and cancels it."""

    SX = np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]]) / 2
    X = np.array([[0, 1], [1, 0]], complex)

    def p1(self, psi, group, eta, model=None):
        rho = np.kron(np.outer(psi, psi.conj()), np.diag([1, 0]))
        if group == 'B':
            # crosstalk on q from r's first sx pulse, which comes before the CZ (after the CNOT, q's own
            # coherence has moved into the q-r state and a local rotation can no longer change P(q=1))
            Rx = np.kron(np.cos(eta / 2) * np.eye(2) - 1j * np.sin(eta / 2) * self.X, np.eye(2))
            rho = Rx @ rho @ Rx.conj().T
            rho = CNOT @ rho @ CNOT.conj().T
        p = float(np.real(rho[2, 2] + rho[3, 3]))
        if model and group == 'A' and 0.01 < abs(psi[1]) ** 2 < 0.99:
            p += two_path_shift(abs(psi[1]) ** 2, model[1], model[0])
        return p

    def states(self, physical):
        zero = np.array([1, 0], complex)
        plus = self.SX @ zero
        minus = self.SX @ self.X @ zero if physical else plus      # old design: same physical state
        return {'0': zero, '+h': plus, '-h': minus, 'pi': self.X @ zero}

    def S(self, physical, eta, model=None):
        st = self.states(physical)
        d = {k: self.p1(v, 'A', eta, model) - self.p1(v, 'B', eta, model) for k, v in st.items()}
        return (d['+h'] + d['-h']) / 2 - (d['0'] + d['pi']) / 2

    def test_old_design_is_fooled_by_crosstalk(self):
        self.assertGreater(abs(self.S(physical=False, eta=0.04)), 0.015)

    def test_physical_control_cancels_crosstalk(self):
        self.assertAlmostEqual(self.S(physical=True, eta=0.04), 0.0, places=12)

    def test_physical_control_keeps_the_model_signal(self):
        self.assertAlmostEqual(self.S(physical=True, eta=0.04, model=(0.3, 1.0)),
                               two_path_shift(0.5, 1.0, 0.3), places=10)


class Analysis(unittest.TestCase):
    def fake_counts(self, n_pairs, shots, s_inject=0.0):
        """Counts with P(q=1) = 0, 0.5, 0.5, 1 (plus an injected shift in group A at +/- pi/2)."""
        target = {'0': 0.0, '+pi/2': 0.5, '-pi/2': 0.5, '+pi': 1.0, '-pi': 1.0}
        counts = {}
        for g in 'AB':
            for t, pt in target.items():
                pp = pt + (s_inject if g == 'A' and t in ('+pi/2', '-pi/2') else 0.0)
                ones = int(round(pp * shots))
                bits1 = ''.join('01'[(j % 2 == 0)] for j in range(2 * n_pairs))[::-1]   # every q = 1, r = 0
                bits0 = '0' * (2 * n_pairs)
                counts[f'{g}_{t}'] = {k: v for k, v in ((bits1, ones), (bits0, shots - ones)) if v}
        return dict(n_pairs=n_pairs, shots=shots, counts=counts)

    def test_injected_shift_is_measured(self):
        a = analyze(self.fake_counts(4, 100000, s_inject=-0.01))
        self.assertAlmostEqual(a['S_mean'], -0.01, places=6)
        self.assertEqual(a['verdict'][:7], 'anomaly')
        b = analyze(self.fake_counts(4, 100000))
        self.assertAlmostEqual(b['S_mean'], 0.0, places=9)
        self.assertEqual(b['verdict'], 'no deviation')


if __name__ == '__main__':
    unittest.main(verbosity=1)
