"""SPDX-License-Identifier: MIT. Is past-preserving selection linear in the loop's own operation? (process matrices)

Araujo, Guerin and Baumeler (PRA 96, 052315, 2017) showed that a no-signalling P-CTC is a process matrix, and process
matrices are linear in every party's operation: if a coin chooses operation U1 with probability p and U2 otherwise,
the result is p out(U1) + (1 - p) out(U2). PPS is linear in states (Theorem 0). Here: is it linear in the loop's
operation?

Spacetime (lightcone.py): a source shares |Phi+> between Alice's input a and Bob's b; Bob records b. Alice's coin c
(P(c = 0) = p) controls which unitary the loop applies to (a, m): U1 if c = 0, U2 if c = 1. Optionally Alice writes c
into a notebook before the loop, outside its causal future.

Run from the repository root:  python -B ctc/tests/test_operation_linearity.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'timeless'))
from lightcone import BELL, CNOT, Event, H, Lattice  # noqa: E402
from paw import reduced, ry  # noqa: E402

ATOL = 1e-10


def random_unitary(rng, d):
    q, r = np.linalg.qr(rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d)))
    return q * (np.diag(r) / abs(np.diag(r)))


def coin_spacetime(U1, U2, p, notebook):
    wl = {'a': [(0, 2), (2, 4), (9, 4)], 'b': [(0, 2), (2, 0), (9, 0)], 'rec_b': [(0, 0), (9, 0)],
          'c': [(0, 4), (9, 4)], 'm': [(0, 4), (9, 4)], 'p': [(0, 4), (9, 4)]}
    G = np.kron(np.diag([1, 0]), U1) + np.kron(np.diag([0, 1]), U2)      # on (c, a, m)
    ev = [Event('H', -0.5, ('a',), H), Event('S', 0, ('a', 'b'), CNOT), Event('M', 0, ('m', 'p'), BELL),
          Event('coin', 0, ('c',), ry(2 * np.arccos(np.sqrt(p)))), Event('B', 2, ('b', 'rec_b'), CNOT),
          Event('L', 3, ('c', 'a', 'm'), G), Event('F', 5, ('m', 'p'))]
    rec = {'rec_b': 'B'}
    if notebook:
        wl['note'] = [(0, 4), (9, 4)]
        ev.append(Event('N', 1, ('c', 'note'), CNOT))
        rec['note'] = 'N'
    return Lattice(wl, ev, rec)


def output(s, rule, regs):
    hist = s.history(rule, s.protected('theorem4')) if rule == 'pps' else s.history(rule)
    return s.red(hist, s.final_cut, regs)


class LinearityInTheLoopsOperation(unittest.TestCase):
    P = 0.3

    def setUp(self):
        rng = np.random.default_rng(11)
        self.pairs = [(random_unitary(rng, 4), random_unitary(rng, 4)) for _ in range(6)]

    def mixture_gap(self, rule, notebook, regs=('a',)):
        """max over pairs of || out(mixed operation) - [p out(U1) + (1 - p) out(U2)] ||."""
        gaps = []
        for U1, U2 in self.pairs:
            mixed = output(coin_spacetime(U1, U2, self.P, notebook), rule, list(regs))
            pure = [output(coin_spacetime(U1, U2, q, notebook), rule, list(regs)) for q in (1.0, 0.0)]
            gaps.append(float(np.abs(mixed - (self.P * pure[0] + (1 - self.P) * pure[1])).max()))
        return gaps

    def test_recorded_coin_pps_is_linear(self):
        """The coin is written into a notebook outside the loop's causal future: Theorem 5 splits on it, and the
        output is exactly the mixture of the two outputs."""
        self.assertLess(max(self.mixture_gap('pps', notebook=True)), ATOL)

    def test_unrecorded_coin_pps_is_not_linear(self):
        """Nobody records the coin. It is then a fresh input of the loop region and is selected like any fresh
        input: the output is not the mixture. So PPS is not a process matrix for such operations."""
        gaps = self.mixture_gap('pps', notebook=False)
        self.assertGreater(min(gaps), 1e-3)

    def test_the_unrecorded_coin_itself_is_selected(self):
        """Why: inside each world, P-CTC reweights the coin's values, so P(c = 0) moves away from p. With the
        notebook it stays at p."""
        for U1, U2 in self.pairs[:3]:
            fresh = output(coin_spacetime(U1, U2, self.P, False), 'pps', ['c'])[0, 0].real
            kept = output(coin_spacetime(U1, U2, self.P, True), 'pps', ['c'])[0, 0].real
            self.assertGreater(abs(fresh - self.P), 1e-3)
            self.assertAlmostEqual(kept, self.P, delta=ATOL)

    def test_no_signalling_either_way(self):
        """The nonlinearity is confined to Alice's own region: Bob's record keeps its no-loop state whether or not
        the coin is recorded. P-CTC changes it."""
        for U1, U2 in self.pairs:
            for notebook in (False, True):
                s = coin_spacetime(U1, U2, self.P, notebook)
                ref = output(s, 'no_loop', ['rec_b'])
                np.testing.assert_allclose(output(s, 'pps', ['rec_b']), ref, atol=ATOL)
        moved = [float(np.abs(output(s, 'p_ctc', ['rec_b']) - output(s, 'no_loop', ['rec_b'])).max())
                 for s in (coin_spacetime(U1, U2, self.P, False) for U1, U2 in self.pairs)]
        self.assertGreater(max(moved), 1e-3)

    def test_p_ctc_is_not_linear_even_with_a_recorded_coin(self):
        """P-CTC normalizes once over everything, so even a recorded coin does not make it linear (Araujo et al.:
        it is linear only when the postselection probability is constant)."""
        self.assertGreater(min(self.mixture_gap('p_ctc', notebook=True)), 1e-3)


if __name__ == '__main__':
    unittest.main(verbosity=1)
