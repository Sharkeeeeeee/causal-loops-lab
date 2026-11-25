"""SPDX-License-Identifier: MIT. A time loop made by time dilation: the wormhole time machine, with loop rules on it.

Until now the time loop was put in by hand, as an edge F -> M. Here it comes from a known construction in general
relativity, the wormhole time machine of Morris, Thorne and Yurtsever (1988):

1. Two mouths of a short wormhole, A and B, start at rest with synchronized clocks. Mouth A stays at x = 0;
   mouth B makes a twin-paradox trip (out at speed v, back at speed v, then rest at its old place, x = d0).
2. Time dilation: B's clock falls behind A's by (1 - sqrt(1 - v^2)) T. The light clocks below simulate this
   from one rule only (light moves at speed 1 in every frame); no dilation formula is put into them.
3. The wormhole throat is short and does not move relative to itself, so it joins the two mouths at equal
   proper time: entering B when B's clock reads tau, you exit A when A's clock reads tau. After the trip that
   is an earlier lab time. Once the time shift exceeds the distance light needs from A to B, a closed causal
   curve exists: a chronology horizon forms.

Limits of the construction, as in the original paper: outside the mouths spacetime is flat (1 + 1 here), the
throat is idealized as a point identification, and holding a wormhole open needs exotic matter (it violates
the null energy condition). Hawking's chronology-protection conjecture says quantum effects destroy the
machine at the horizon; nothing here tests that.

Then the loop rules of lightcone.py run on this spacetime: the time-travelling qubit m really goes into mouth
B at F and comes out of mouth A at M, and F -> M is the wormhole identification, checked from the clocks.
"""
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lightcone import BELL, CNOT, H, LOOPS, Event, Lattice  # noqa: E402

EPS = 1e-9


class TwinMouths:
    """Mouth A rests at x = 0. Mouth B rests at x = d0 except for a round trip during 0 < t < T: out at speed v for
    T/2, back at speed v for T/2."""

    def __init__(self, v=0.8, T=10.0, d0=1.0):
        self.v, self.T, self.d0 = v, T, d0
        self.s = np.sqrt(1 - v * v)

    def velocity_B(self, t):
        if 0 <= t < self.T / 2:
            return self.v
        if self.T / 2 <= t < self.T:
            return -self.v
        return 0.0

    def x_B(self, t):
        u = min(max(t, 0.0), self.T)
        return self.d0 + self.v * (u if u <= self.T / 2 else self.T - u)

    def tau_B(self, t):
        """B's proper time at lab time t (the exact integral of sqrt(1 - v^2); A's proper time is t)."""
        return min(t, 0.0) + self.s * min(max(t, 0.0), self.T) + max(t - self.T, 0.0)

    def tau_B_inverse(self, tau):
        if tau <= 0:
            return tau
        if tau <= self.s * self.T:
            return tau / self.s
        return tau - self.s * self.T + self.T

    def shift(self, t):
        """How far back in lab time the wormhole sends you: enter B at lab time t, exit A at lab time tau_B(t)."""
        return t - self.tau_B(t)

    def horizon_formula(self):
        """Lab time at B of the chronology horizon: the first t with shift(t) = x_B(t), on the return leg:
        (1 - s) t = d0 + v (T - t). None if the final shift (1 - s) T never reaches d0."""
        if (1 - self.s) * self.T < self.d0:
            return None
        return (self.d0 + self.v * self.T) / (1 - self.s + self.v)

    # ---------------------------------------------------------------- causal structure through the wormhole
    def earliest_at_B(self, t0, x0):
        """Earliest lab time a signal from (t0, x0) reaches mouth B (B moves slower than light, so bisection works)."""
        g = lambda t: (t - t0) - abs(self.x_B(t) - x0)
        lo, hi = t0, t0 + abs(self.x_B(t0) - x0) / (1 - self.v) + 1
        for _ in range(64):
            mid = (lo + hi) / 2
            lo, hi = (lo, mid) if g(mid) >= 0 else (mid, hi)
        return hi

    def reach(self, t0, x0):
        """(earliest lab time at A, earliest lab time at B) for signals from (t0, x0), using the wormhole any number
        of times in either direction. Iterated to a fixed point."""
        eA, eB = t0 + abs(x0), self.earliest_at_B(t0, x0)
        for _ in range(500):
            nA = min(eA, self.tau_B(eB))                                   # in at B, out at A
            nB = min(eB, self.tau_B_inverse(nA), self.earliest_at_B(nA, 0.0))   # in at A, out at B; or light A -> B
            nA = min(nA, nB + self.x_B(nB))                                # light B -> A
            if abs(nA - eA) < 1e-12 and abs(nB - eB) < 1e-12:
                break
            eA, eB = nA, nB
        return eA, eB

    def in_future(self, t0, x0, t1, x1):
        """Is (t1, x1) in the causal future of (t0, x0), counting paths through the wormhole?"""
        if abs(x1 - x0) <= t1 - t0 + EPS:
            return True
        eA, eB = self.reach(t0, x0)
        return abs(x1) <= t1 - eA + EPS or abs(x1 - self.x_B(eB)) <= t1 - eB + EPS

    def chronology_violating(self, t, x):
        """Is (t, x) in its own causal past through the wormhole (a closed causal curve passes through it)?"""
        eA, eB = self.reach(t, x)
        out_A = self.tau_B(eB)                      # last trip B -> A: earliest exit from A
        out_B = self.tau_B_inverse(eA)              # last trip A -> B: earliest exit from B
        return abs(x) <= t - out_A - EPS or abs(x - self.x_B(out_B)) <= t - out_B - EPS

    def horizon_on(self, mouth, t_max=20.0):
        """First lab time at which an event on the mouth is chronology violating (scan plus bisection)."""
        where = (lambda t: 0.0) if mouth == 'A' else self.x_B
        ts = np.linspace(-1, t_max, 211)
        hits = [t for t in ts if self.chronology_violating(t, where(t))]
        if not hits:
            return None
        hi = hits[0]
        lo = hi - (ts[1] - ts[0])
        for _ in range(60):
            mid = (lo + hi) / 2
            lo, hi = (lo, mid) if self.chronology_violating(mid, where(mid)) else (mid, hi)
        return hi


# ---------------------------------------------------------------- simulated time dilation

def light_clock(velocity, t_end, L=0.05):
    """A transverse light clock (mirrors at y = 0 and y = L) carried along x with velocity(t), in 2 + 1 dimensions.

    The only physics used: the photon moves at speed 1 in the lab, and it is emitted toward the opposite mirror in
    the clock's own frame, so in the lab it keeps up with the mirrors along x. Its velocity is then (v, +-w) with
    v^2 + w^2 = 1. Returns (round trips completed, photon segments as (t0, x0, y0, t1, x1, y1))."""
    t, x, y, segments = 0.0, 0.0, 0.0, []
    while True:
        v = velocity(t)
        w = np.sqrt(1 - v * v)                       # the photon's speed is 1
        y1 = L - y
        t1 = t + L / w
        if t1 > t_end:
            break
        x1 = x + v * (t1 - t)
        segments.append((t, x, y, t1, x1, y1))
        t, x, y = t1, x1, y1
    return len(segments) // 2, segments


# ---------------------------------------------------------------- the loop on the time machine

def time_machine(mouths=None, loop='refusal'):
    """bob_and_alice of lightcone.py on the wormhole spacetime (default mouths: v = 0.8, T = 10, d0 = 1, so B's
    clock ends 4 behind and the chronology horizon is at lab time 4.5 on A and 7.5 on B).

    The time-travelling qubit m comes out of mouth A at M = (t 7, x 0) with its partner p, meets Alice's input a
    and her log at L = (10, 0.5), and goes into mouth B at F = (11, 1), where B's clock reads 7: F -> M is the
    wormhole. A source at (6, -3) shares |Phi+> between a and Bob's b; Bob copies b at (9.5, -6)."""
    w = mouths or TwinMouths()
    t_F, t_M = 11.0, None
    t_M = w.tau_B(t_F)
    x_F = w.x_B(t_F)
    lab = 0.5
    wl = {'a': [(6, -3), (9.5, lab), (12, lab)], 'b': [(6, -3), (9, -6), (12, -6)], 'rec_b': [(5, -6), (12, -6)],
          'log': [(5, lab), (12, lab)], 'm': [(t_M, 0.0), (10, lab), (t_F, x_F)], 'p': [(t_M, 0.0), (10, lab), (t_F, x_F)]}
    ev = [Event('H', 5.5, ('a',), H), Event('S', 6, ('a', 'b'), CNOT), Event('M', t_M, ('m', 'p'), BELL),
          Event('B', 9.5, ('b', 'rec_b'), CNOT), Event('L', 10, ('a', 'log', 'm'), LOOPS[loop]),
          Event('F', t_F, ('m', 'p'))]
    rec = {'rec_b': 'B', 'log': 'L'} if loop == 'refusal' else {'rec_b': 'B'}
    s = Lattice(wl, ev, rec)
    s.mouths = w
    return s


def identification_error(s):
    """|B's clock at F - A's clock at M| and the distances of F from mouth B and of M from mouth A."""
    (xF, tF), (xM, tM) = s.pos('F'), s.pos('M')
    w = s.mouths
    return abs(w.tau_B(tF) - tM), abs(float(xF[0]) - w.x_B(tF)), abs(float(xM[0]))
