"""SPDX-License-Identifier: MIT. Past-preserving selection in a discrete spacetime (light cones, any dimension).

Limitation 2 of README.md: the local clocks of clocks.py gave relativity of simultaneity only in toy form (no
space, one step per clock). Here the clocks are replaced by a spacetime:

- Every qubit has a worldline x(t) in d spatial dimensions that respects a local light cone (`Flat`: speed at
  most 1; `River`: a 1 + 1 black hole whose cones tilt inward, Painleve-Gullstrand style). Every event is a
  contact interaction: all its qubits are at one point at that time. The causal order of events is the order
  along shared worldlines. Locality alone makes it lie inside the light cone (tested).
- The timeless state is a many-fingered-time (Tomonaga-Schwinger) history: one state per cut (a down-set of
  events, i.e. a spacelike slice), psi_cut = prod_{e in cut} G_e psi_0. It is well defined because events
  with no causal relation act on different qubits. One Feynman-Kitaev constraint per event.
- A frame (flat case) is a boost t' = t - beta n.x with |beta| < 1: it respects every causal relation and can
  still reorder spacelike events (tested).
- The loop: the time-travelling qubit m emerges with partner p at the past mouth M, interacts with whatever
  reaches it, and the constraint "(m, p) in |Phi+>" closes the loop at the future mouth F. With the loop
  closed (an edge F -> M) the events of the region R = J+(M) n J-(F) are in their own causal past. The
  loop's causal future J+(M) is the same with the loop open or closed.

"The past" of the loop:
  foliation      : records written before the slice through L in a chosen frame
  past_cone      : records written in J-(L), the loop's causal past (loop open)
  past_cone_ctc  : the same with the loop closed (F -> M), so L is in its own past
  outside_future : record registers written outside J+(M)
  influence      : record registers whose reduced state no loop input can change (README result 4)
  theorem4       : every qubit that enters R is split in the pointer basis of the interactions that read
                   it outside J+(M) (Theorem 4 with the outside taken to be the complement of J+(M);
                   THEOREMS.md, Theorem 5). Needs no record registers.
"""
from dataclasses import dataclass
import itertools
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / 'hardware'))
from paw import CNOT, H, PHI_PLUS, SDG_H, TOL, X, apply, full, reduced, ry  # noqa: E402
from clocks import SWAP_WRITE  # noqa: E402
from experiments import BY_NAME  # noqa: E402
from records import operator_schmidt, pointer_blocks  # noqa: E402

I2 = np.eye(2, dtype=complex)
SWAP = np.eye(4, dtype=complex)[[0, 2, 1, 3]]
BELL = CNOT @ np.kron(H, I2)                                # |00> -> |Phi+>
LOOPS = {                                                   # all on (a, log, m)
    'refusal': BY_NAME['refusal'].unitary(),                # the loop writes the log; a is only a control
    'swap_write': full(SWAP_WRITE, [0, 2], 3),              # the loop writes onto a
}
LOOP_INPUTS = (I2, X, H, SDG_H)                             # m prepared in |0>, |1>, |+>, |+i>, no partner
DEFINITIONS = ('foliation', 'past_cone', 'past_cone_ctc', 'outside_future', 'influence', 'theorem4', 'all')
EPS = 1e-9


# ---------------------------------------------------------------- backgrounds

class Flat:
    """Minkowski light cones, speed of light 1, any spatial dimension."""

    def segment_ok(self, t0, x0, t1, x1):
        return np.linalg.norm(x1 - x0) <= (t1 - t0) + EPS

    def in_future(self, t0, x0, t1, x1):
        return t1 >= t0 - EPS and np.linalg.norm(x1 - x0) <= (t1 - t0) + EPS


class River:
    """A 1 + 1 black hole in river form: space flows toward +x with speed v(x) (v_out for x < h, v_in for
    x >= h) and light moves at 1 relative to the flow, so the local cone is dx/dt in [v - 1, v + 1]. With
    v_in > 1 both light rays inside move toward +x: x = h is a horizon and nothing inside reaches x < h."""

    def __init__(self, h, v_out=0.0, v_in=1.5):
        self.h, self.v_out, self.v_in = h, v_out, v_in

    def v(self, x):
        return self.v_in if x >= self.h else self.v_out

    def inside(self, x):
        return float(np.atleast_1d(x)[0]) >= self.h - EPS

    def segment_ok(self, t0, x0, t1, x1):
        x0, x1 = float(x0[0]), float(x1[0])
        s = (x1 - x0) / (t1 - t0)
        regions = {self.v(x0), self.v(x1)} | ({self.v_out, self.v_in} if min(x0, x1) < self.h <= max(x0, x1) else set())
        return all(v - 1 - EPS <= s <= v + 1 + EPS for v in regions)

    def ray(self, x, dt, sign):
        """Position after time dt of the light ray leaving x toward -x (sign -1) or +x (sign +1)."""
        for _ in range(4):
            s = self.v(x) + sign
            if x < self.h and s > 0 and (self.h - x) / s < dt:
                dt -= (self.h - x) / s
                x = self.h
                continue
            if x >= self.h and s < 0 and (x - self.h) / -s < dt:
                dt -= (x - self.h) / -s + 1e-12
                x = self.h - 1e-12
                continue
            return x + s * dt
        return x

    def in_future(self, t0, x0, t1, x1):
        if t1 < t0 - EPS:
            return False
        x0, x1, dt = float(x0[0]), float(x1[0]), max(t1 - t0, 0.0)
        return self.ray(x0, dt, -1) - EPS <= x1 <= self.ray(x0, dt, +1) + EPS


@dataclass(frozen=True)
class Event:
    name: str
    t: float
    qubits: tuple
    gate: object = None          # None: a marker (the future mouth F, where the constraint closes the loop)


class Split(list):
    """Theorem 4 sectors: functions on the final state vector, one per joint pointer block."""


# ---------------------------------------------------------------- the spacetime

class Lattice:
    """A spacetime of contact events on qubit worldlines, with one time loop (past mouth M, future mouth F)
    and named record registers {register: event that writes it}."""

    def __init__(self, worldlines, events, records, cone=None, loop='L', mouth='M', future_mouth='F'):
        self.worldlines = {q: [(float(t), np.atleast_1d(np.asarray(x, float))) for t, x in pts] for q, pts in worldlines.items()}
        self.dim = len(next(iter(self.worldlines.values()))[0][1])
        self.cone = cone or Flat()
        self.qubits = list(worldlines)
        self.n = len(self.qubits)
        self.D = 2 ** self.n
        self.events = {e.name: e for e in events}
        self.order = [e.name for e in sorted(events, key=lambda e: (e.t, e.name))]
        self.dyn = [k for k in self.order if self.events[k].gate is not None]
        self.records = dict(records)
        self.L, self.M, self.F = loop, mouth, future_mouth
        self.psi0 = np.zeros(self.D, complex)
        self.psi0[0] = 1
        self._succ = {False: self._successors(False), True: self._successors(True)}
        self._fut = {}
        self._forward = {}
        self.cuts = self._cuts() if len(self.dyn) <= 14 else None
        self.final_cut = frozenset(self.dyn)
        self.final = self.forward(self.final_cut)
        self.region = frozenset(k for k in self.dyn if k in self.future(self.M) and k in self.past(self.F))
        self.seam = [k for k in self.order if k in self.region and 'm' in self.events[k].qubits][-1]
        self.outside_cut = frozenset(k for k in self.dyn if k not in self.future(self.M))

    # ---------------------------------------------------------------- geometry
    def x(self, q, t):
        pts = self.worldlines[q]
        if t <= pts[0][0]:
            return pts[0][1]
        for (t0, x0), (t1, x1) in zip(pts, pts[1:]):
            if t0 <= t <= t1:
                return x0 + (x1 - x0) * (t - t0) / (t1 - t0)
        return pts[-1][1]

    def pos(self, name):
        """(x as an array, t). Raises if the event's qubits are not at one point (not a contact event)."""
        e = self.events[name]
        xs = [self.x(q, e.t) for q in e.qubits]
        if any(not np.allclose(xs[0], y, atol=1e-9) for y in xs[1:]):
            raise ValueError(f'{name}: qubits at {xs}, not a contact interaction')
        return xs[0], e.t

    def where(self, name):
        x, t = self.pos(name)
        return (float(x[0]) if self.dim == 1 else x), t

    def max_speed(self):
        return max(np.linalg.norm(x1 - x0) / (t1 - t0) for pts in self.worldlines.values()
                   for (t0, x0), (t1, x1) in zip(pts, pts[1:]))

    def worldlines_ok(self):
        return all(self.cone.segment_ok(t0, x0, t1, x1) for pts in self.worldlines.values()
                   for (t0, x0), (t1, x1) in zip(pts, pts[1:]))

    def in_light_cone(self, a, b):
        (xa, ta), (xb, tb) = self.pos(a), self.pos(b)
        return self.cone.in_future(ta, xa, tb, xb)

    # ---------------------------------------------------------------- causal order
    def edges(self, ctc=False):
        out = set()
        for q in self.qubits:
            on_q = [k for k in self.order if q in self.events[k].qubits]
            out |= set(zip(on_q, on_q[1:]))
        if ctc:
            out.add((self.F, self.M))                       # the loop: what enters at F emerges at M
        return out

    def _successors(self, ctc):
        succ = {k: set() for k in self.order}
        for a, b in self.edges(ctc):
            succ[a].add(b)
        return succ

    def future(self, name, ctc=False):
        """J+(name), including the event itself."""
        key = (name, ctc)
        if key not in self._fut:
            seen, todo = {name}, [name]
            while todo:
                for b in self._succ[ctc][todo.pop()]:
                    if b not in seen:
                        seen.add(b)
                        todo.append(b)
            self._fut[key] = frozenset(seen)
        return self._fut[key]

    def past(self, name, ctc=False):
        """J-(name): events with a causal path of length >= 1 to it (the event itself only through a loop)."""
        return {k for k in self.order if any(name in self.future(b, ctc) for b in self._succ[ctc][k])}

    def precedes(self, a, b):
        return a != b and b in self.future(a)

    def boost_order(self, beta, direction=None):
        """Events ordered by t' = t - beta n.x (a Lorentz boost along the unit vector n; flat background)."""
        n = np.zeros(self.dim)
        n[0] = 1
        n = n if direction is None else np.asarray(direction, float) / np.linalg.norm(direction)
        return sorted(self.order, key=lambda k: self.pos(k)[1] - beta * n @ self.pos(k)[0])

    def slice_through(self, name, beta, direction=None):
        """The simultaneity slice of a boosted frame just before event `name`: a cut."""
        order = self.boost_order(beta, direction)
        return frozenset(k for k in order[:order.index(name)] if k in self.dyn)

    def chronology_violating(self):
        """Events that are in their own causal past once the loop is closed."""
        return {k for k in self.order if k in self.past(k, ctc=True)}

    def linear_extension(self, rng):
        done, out = set(), []
        preds = {k: {a for a, b in self.edges() if b == k and a in self.dyn} for k in self.dyn}
        while len(out) < len(self.dyn):
            ready = [k for k in self.dyn if k not in done and preds[k] <= done]
            k = ready[rng.integers(len(ready))]
            done.add(k)
            out.append(k)
        return out

    def sample_cuts(self, rng, k=4):
        cuts = {frozenset(), self.final_cut, self.outside_cut, self.outside_cut | self.region}
        for _ in range(k):
            ext = self.linear_extension(rng)
            cuts |= {frozenset(ext[:i]) for i in range(len(ext) + 1)}
        return sorted(cuts, key=len)

    # ---------------------------------------------------------------- the static history
    def _cuts(self):
        preds = {k: {a for a, b in self.edges() if b == k and a in self.dyn} for k in self.dyn}
        out = []

        def grow(i, cut):
            if i == len(self.dyn):
                out.append(frozenset(cut))
                return
            k = self.dyn[i]
            grow(i + 1, cut)
            if preds[k] <= cut:
                grow(i + 1, cut | {k})
        grow(0, frozenset())
        return out

    def ix(self, q):
        return self.qubits.index(q)

    def apply_event(self, name, v, inverse=False, gate=None):
        e = self.events[name]
        G = e.gate if gate is None else gate
        return apply(G.conj().T if inverse else G, [self.ix(q) for q in e.qubits], self.n, v)

    def evolve(self, cut, order=None, mouth_gate=None):
        v = self.psi0
        for k in (order or self.order):
            if k in cut and self.events[k].gate is not None:
                v = self.apply_event(k, v, gate=mouth_gate if k == self.M else None)
        return v

    def forward(self, cut):
        if cut not in self._forward:
            self._forward[cut] = self.evolve(cut)
        return self._forward[cut]

    def back(self, v, cut):
        for k in reversed(self.dyn):
            if k not in cut:
                v = self.apply_event(k, v, inverse=True)
        return v

    def covering_pairs(self, name):
        cuts = set(self.cuts)
        return [(c, c | {name}) for c in self.cuts if name not in c and (c | {name}) in cuts]

    # ---------------------------------------------------------------- the record basis (Theorem 4, Theorem 5)
    def inputs(self):
        """{qubit: its first event in R} for every qubit other than m, p that enters the loop region."""
        out = {}
        for q in self.qubits:
            if q in ('m', 'p'):
                continue
            on_q = [k for k in self.order if q in self.events[k].qubits and k in self.region]
            if on_q:
                out[q] = on_q[0]
        return out

    def pointer_blocks_of(self):
        """{input: list of 2x2 block projectors at its entry into R}, from the interactions that read it
        before (all outside J+(M)): the last readout fixes the blocks, compatible earlier ones refine them,
        single-qubit gates carry them along (THEOREMS.md 4a). Raises ValueError outside Theorem 4's scope."""
        inputs = self.inputs()
        out = {}
        for q, entry in inputs.items():
            blocks = None
            for k in self.order:
                e = self.events[k]
                if q not in e.qubits or e.gate is None:
                    continue
                if k == entry:
                    break
                if k in self.future(self.M):
                    raise ValueError(f'{k}: an input touched inside J+(M) before entering R')
                if len(e.qubits) == 1:
                    blocks = None if blocks is None else [e.gate @ P @ e.gate.conj().T for P in blocks]
                    continue
                others = [r for r in e.qubits if r != q]
                if len(e.qubits) != 2 or others[0] in inputs:
                    raise ValueError(f'{k}: not a two-qubit interaction with the outside')
                V = e.gate if e.qubits[0] == q else SWAP @ e.gate @ SWAP
                if len(operator_schmidt(V, 2, 2)[0]) == 1:
                    continue                                 # a product gate reads nothing
                new = pointer_blocks(V, 2, 2)
                if new is None:
                    raise ValueError(f'{k}: reads {q} in no basis (a non-readout interaction)')
                if blocks is not None and all(np.allclose(P @ Q, Q @ P, atol=1e-9) for P in blocks for Q in new):
                    new = [P @ Q for P in blocks for Q in new if np.linalg.norm(P @ Q) > 1e-9]
                blocks = new
            out[q] = blocks if blocks is not None else [I2.copy()]
        return out

    def theorem4_split(self):
        """One sector per joint block of the inputs, applied on the outside cut (all events not in J+(M))."""
        blocks = self.pointer_blocks_of()
        names = list(blocks)
        fut = [k for k in self.dyn if k in self.future(self.M)]
        split = Split()
        for combo in itertools.product(*[blocks[q] for q in names]):
            def f(v, combo=combo):
                for k in reversed(fut):
                    v = self.apply_event(k, v, inverse=True)
                for q, P in zip(names, combo):
                    v = apply(P, [self.ix(q)], self.n, v)
                for k in fut:
                    v = self.apply_event(k, v)
                return v
            split.append(f)
        return split

    # ---------------------------------------------------------------- rules (computed at the last cut)
    def project(self, v, regs_values):
        for reg, val in regs_values:
            e = np.zeros(2, complex)
            e[val] = 1
            v = apply(np.outer(e, e), [self.ix(reg)], self.n, v)
        return v

    def bell(self, v):
        return apply(np.outer(PHI_PLUS, PHI_PLUS.conj()), [self.ix('m'), self.ix('p')], self.n, v)

    def rule(self, name, protected=()):
        """Final state as a mixture [(weight, vector)]. `protected`: record registers (split in Z, the pointer
        basis of the CNOTs that write them) or a Split from theorem4_split()."""
        if name == 'no_loop':
            return [(1.0, self.final)]
        if name == 'p_ctc':
            F = self.bell(self.final)
            return [(1.0, F / np.linalg.norm(F))]
        if name == 'pps':
            if isinstance(protected, Split):
                sectors = list(protected)
            else:
                sectors = [lambda v, vals=vals: self.project(v, zip(protected, vals))
                           for vals in itertools.product((0, 1), repeat=len(protected))]
            out = []
            for f in sectors:
                S = f(self.final)
                w = np.linalg.norm(S) ** 2
                if w < TOL:
                    continue
                F = self.bell(S)
                g = np.linalg.norm(F) ** 2
                out.append((w, S / np.sqrt(w) if g < TOL * w else F / np.sqrt(g)))   # D-CTC fallback = no loop here
            return out
        raise ValueError(name)

    def history(self, name, protected=(), seam=True, cuts=None):
        """[(weight, {cut: vector})]. With the seam (default), cuts that contain the whole loop region R carry
        the rule's state propagated back from the end and every other cut keeps the forward history. (No
        Cauchy slice passes through R once the loop is closed; cuts that split R get the forward history.)"""
        cuts = self.cuts if cuts is None else cuts
        out = []
        for w, v in self.rule(name, protected):
            out.append((w, {c: self.back(v, c) if (not seam or self.region <= c) else self.forward(c) for c in cuts}))
        return out

    # ---------------------------------------------------------------- what counts as the past
    def influenced(self, reg):
        rhos = [reduced(self.evolve(self.final_cut, mouth_gate=np.kron(prep, I2)), self.n, [self.ix(reg)])
                for prep in LOOP_INPUTS]
        return any(not np.allclose(rhos[0], r, atol=1e-9) for r in rhos[1:])

    def protected(self, definition, cut=None):
        recs = self.records
        if definition == 'foliation':
            return [r for r in recs if recs[r] in cut]
        if definition == 'past_cone':
            return [r for r in recs if recs[r] in self.past(self.L)]
        if definition == 'past_cone_ctc':
            return [r for r in recs if recs[r] in self.past(self.L, ctc=True)]
        if definition == 'outside_future':
            return [r for r in recs if recs[r] not in self.future(self.M, ctc=True)]
        if definition == 'influence':
            return [r for r in recs if not self.influenced(r)]
        if definition == 'theorem4':
            return self.theorem4_split()
        if definition == 'all':
            return list(recs)
        raise ValueError(definition)

    def outside_future(self, cut):
        """Qubits whose latest event in the cut lies outside the loop's causal future J+(M)."""
        fut = self.future(self.M, ctc=True)
        out = []
        for q in self.qubits:
            last = [k for k in self.order if k in cut and q in self.events[k].qubits]
            if not last or last[-1] not in fut:
                out.append(q)
        return out

    # ---------------------------------------------------------------- readout
    def red(self, hist, cut, regs):
        return sum(w * reduced(h[cut], self.n, [self.ix(r) for r in regs]) for w, h in hist)

    def prob(self, hist, reg, cut=None, value=1):
        return float(self.red(hist, self.final_cut if cut is None else cut, [reg])[value, value].real)

    def conditional(self, hist, reg, given, value):
        rho = self.red(hist, self.final_cut, [given, reg])
        return float(rho[2 * value + 1, 2 * value + 1].real / (rho[2 * value, 2 * value].real + rho[2 * value + 1, 2 * value + 1].real))

    def final_rho(self, hist):
        return sum(w * np.outer(h[self.final_cut], h[self.final_cut].conj()) for w, h in hist)

    def residuals(self, hist):
        """(initial-condition residual, {event: transport residual}) maximized over mixture components.
        The transport residual of event e is sqrt(<Psi|J_e|Psi>) for its Feynman-Kitaev constraint J_e."""
        init = max(float(np.linalg.norm(h[frozenset()] - self.psi0)) for _, h in hist)
        res = {}
        for k in self.dyn:
            res[k] = max(np.sqrt(sum(np.linalg.norm(self.apply_event(k, h[a]) - h[b]) ** 2 for a, b in self.covering_pairs(k)))
                         for _, h in hist)
        return init, res

    def chain_breaks(self, name, protected, rng, k=3):
        """Like residuals, along k random frames (linear extensions), for spacetimes too large to list all cuts."""
        exts = [self.linear_extension(rng) for _ in range(k)]
        cuts = list({frozenset(e[:i]) for e in exts for i in range(len(e) + 1)})
        hist = self.history(name, protected, cuts=cuts)
        init = max(float(np.linalg.norm(h[frozenset()] - self.psi0)) for _, h in hist)
        res = {}
        for e in exts:
            for i, ev in enumerate(e):
                a, b = frozenset(e[:i]), frozenset(e[:i + 1])
                r = max(float(np.linalg.norm(self.apply_event(ev, h[a]) - h[b])) for _, h in hist)
                res[ev] = max(res.get(ev, 0.0), r)
        return init, res


# ---------------------------------------------------------------- spacetimes

def bob_and_alice(loop='refusal', alice_copy=False, late_copy=True):
    """A source at x = 2 makes |Phi+> on (a, b) at t = 0 (H on a, then a CNOT that reads a in Z); a travels
    to Alice at x = 4, b to Bob at x = 0 (both at light speed). Bob copies b into rec_b at t = 2. Alice's
    loop: mouth M at t = 0, loop event L at t = 3 on (a, log, m), future mouth F at t = 5. Optional: Alice
    copies a before the loop (rec_a, t = 2.5) and after it (rec_late, t = 4). Bob's record is spacelike to
    M and L."""
    wl = {'a': [(0, 2), (2, 4), (9, 4)], 'b': [(0, 2), (2, 0), (9, 0)], 'rec_b': [(0, 0), (9, 0)],
          'log': [(0, 4), (9, 4)], 'm': [(0, 4), (9, 4)], 'p': [(0, 4), (9, 4)]}
    ev = [Event('H', -0.5, ('a',), H), Event('S', 0, ('a', 'b'), CNOT), Event('M', 0, ('m', 'p'), BELL),
          Event('B', 2, ('b', 'rec_b'), CNOT), Event('L', 3, ('a', 'log', 'm'), LOOPS[loop]),
          Event('F', 5, ('m', 'p'))]
    rec = {'rec_b': 'B', 'log': 'L'} if loop == 'refusal' else {'rec_b': 'B'}
    if alice_copy:
        wl['rec_a'] = [(0, 4), (9, 4)]
        ev.append(Event('A', 2.5, ('a', 'rec_a'), CNOT))
        rec['rec_a'] = 'A'
    if late_copy:
        wl['rec_late'] = [(0, 4), (9, 4)]
        ev.append(Event('R', 4, ('a', 'rec_late'), CNOT))
        rec['rec_late'] = 'R'
    return Lattice(wl, ev, rec)


def alice_alone(copy='after', loop='refusal', prior=0.5):
    """Alice prepares a herself (nobody else holds it) and copies it once, before (t = 1) or after (t = 3)
    her loop event (t = 2), or not at all (copy=None). For the refusal loop the copy commutes with the loop,
    so 'before' and 'after' have the same overall unitary."""
    wl = {q: [(0, 0), (9, 0)] for q in ('a', 'rec', 'log', 'm', 'p')}
    ev = [Event('P', 0, ('a',), ry(2 * np.arcsin(np.sqrt(prior)))), Event('M', 0, ('m', 'p'), BELL),
          Event('L', 2, ('a', 'log', 'm'), LOOPS[loop]), Event('F', 4, ('m', 'p'))]
    rec = {'log': 'L'} if loop == 'refusal' else {}
    if copy is not None:
        ev.append(Event('C', 1 if copy == 'before' else 3, ('a', 'rec'), CNOT))
        rec['rec'] = 'C'
    return Lattice(wl, ev, rec)


def black_hole(loop='refusal'):
    """bob_and_alice in a 1 + 1 black hole (River with horizon at x = 3, inflow 1.5 inside). Alice's lab falls
    in at speed 1 from x = 4; a crosses the horizon at t = 1 and meets her loop at x = 7, t = 3. Bob stays
    outside at x = 0. Nothing in J+(M) can reach him."""
    lab = [(0, 4), (9, 13)]
    wl = {'a': [(0, 2), (1, 3), (3, 7), (9, 13)], 'b': [(0, 2), (2, 0), (9, 0)], 'rec_b': [(0, 0), (9, 0)],
          'log': lab, 'm': lab, 'p': lab, 'rec_late': lab}
    ev = [Event('H', -0.5, ('a',), H), Event('S', 0, ('a', 'b'), CNOT), Event('M', 0, ('m', 'p'), BELL),
          Event('B', 2, ('b', 'rec_b'), CNOT), Event('L', 3, ('a', 'log', 'm'), LOOPS[loop]),
          Event('R', 4, ('a', 'rec_late'), CNOT), Event('F', 5, ('m', 'p'))]
    rec = {'rec_b': 'B', 'rec_late': 'R'} | ({'log': 'L'} if loop == 'refusal' else {})
    return Lattice(wl, ev, rec, cone=River(3.0))


def _random_su2(rng):
    q, r = np.linalg.qr(rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2)))
    return q * (np.diag(r) / abs(np.diag(r)))


def _random_u4(rng):
    q, r = np.linalg.qr(rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4)))
    return q * (np.diag(r) / abs(np.diag(r)))


def _controlled(U, control_first=True):
    V = np.kron(np.diag([1, 0]), I2) + np.kron(np.diag([0, 1]), U)
    return V if control_first else SWAP @ V @ SWAP


def random_spacetime(seed, dims=1, walkers=5, steps=7):
    """Random walkers on a small grid in `dims` spatial dimensions (one axis step or none per unit time, so
    speed <= 1). Co-located walkers interact by controlled gates (readouts, random direction and target
    unitary; CNOT copies give record registers). The loop mouth sits at the origin: m interacts with a walker
    that visits it (CNOT, controlled unitaries either way, swap_write, or a generic two-qubit unitary).
    Returns None if the draw leaves Theorem 4's scope or m never interacts."""
    rng = np.random.default_rng(seed)
    side = {1: 4, 2: 3, 3: 2}[dims]
    names = [f'w{i}' for i in range(walkers)]
    here = {w: rng.integers(side, size=dims) for w in names}
    wl = {w: [(0, here[w].copy())] for w in names}
    origin = np.zeros(dims, int)
    wl['m'] = [(0, origin), (steps + 2, origin)]
    wl['p'] = [(0, origin), (steps + 2, origin)]
    ev = [Event('M', 0, ('m', 'p'), BELL)]
    ev += [Event(f'prep_{w}', 0, (w,), _random_su2(rng)) for w in names]
    touched_m = False
    for t in range(1, steps + 1):
        for w in names:
            step = np.zeros(dims, int)
            if rng.random() < 0.7:
                step[rng.integers(dims)] = rng.choice([-1, 1])
            here[w] = np.clip(here[w] + step, 0, side - 1)
            wl[w].append((t, here[w].copy()))
        free = names[:]
        rng.shuffle(free)
        at_mouth = [w for w in free if not here[w].any()]
        if at_mouth and rng.random() < 0.8:
            w = at_mouth[0]
            kind = rng.integers(5)
            gate = [CNOT, _controlled(_random_su2(rng)), _controlled(_random_su2(rng), False), SWAP_WRITE, _random_u4(rng)][kind]
            ev.append(Event(f'K{t}', t, (w, 'm'), gate))
            free.remove(w)
            touched_m = True
        sites = {}
        for w in free:
            sites.setdefault(tuple(here[w]), []).append(w)
        for group in sites.values():
            for u, v in zip(group[::2], group[1::2]):
                if rng.random() < 0.8:
                    gate = CNOT if rng.random() < 0.3 else _controlled(_random_su2(rng))
                    ev.append(Event(f'G{t}_{u}_{v}', t, (u, v), gate))
        for w in names:
            if rng.random() < 0.15:
                ev.append(Event(f'U{t}_{w}', t + 0.5, (w,), _random_su2(rng)))
    ev.append(Event('F', steps + 1, ('m', 'p')))
    if not touched_m:
        return None
    for w in names:
        wl[w].append((steps + 2, here[w].copy()))
    records = {}
    for e in ev:
        if e.gate is CNOT and len(e.qubits) == 2 and 'm' not in e.qubits:
            target = e.qubits[1]
            if not any(f.t > e.t and target in f.qubits for f in ev):
                records[target] = e.name
    s = Lattice(wl, ev, records, loop=None)
    try:
        s.pointer_blocks_of()
    except ValueError:
        return None
    s.L = s.seam
    return s


def random_spacetimes(dims, count, start=0):
    out, seed = [], start
    while len(out) < count:
        s = random_spacetime(seed, dims)
        seed += 1
        if s is not None:
            out.append(s)
    return out
