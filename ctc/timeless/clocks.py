"""SPDX-License-Identifier: MIT. Fuller clock systems for the timeless model: local clocks and a superposed clock.

paw.py used one clock and two orderings of commuting steps. Here:

1. LocalClocks: Alice and Bob each carry their own clock register. The static state is
       Psi = sum_{tA, tB} |tA>|tB> (x) A^tA B^tB psi_0
   and satisfies one constraint per clock (J_A Psi = J_B Psi = 0, with [J_A, J_B] = 0). A global
   "now" is a frame: a staircase path through the (tA, tB) lattice. Two frames disagree on whether
   Bob's record or Alice's loop comes first, like observers in relativity disagreeing on the order
   of spacelike-separated events. Nothing outside the static state picks a frame.

2. QuantumSwitch: the order of Alice's record and her loop interaction is controlled by a qubit c in
   |+>. Relative to the loop, the clock reading of the record is in superposition. In the
   'classical' variant c is itself recorded (copied into rec_c), so the order is a recorded fact.

The rules are as in paw.py, but computed at the final clock reading and propagated back (the
constraint and the sector projectors commute with this). "The past" is defined three ways:
  clock     : records written before the loop interaction (needs an order; for the switch that
              means splitting the state by c, whether or not anything recorded c)
  influence : records whose reduced state no loop input can change, decided sector by sector
              (a record can be past inside one sector of other protected records and not in another)
"""
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paw import CNOT, H, PHI_PLUS, SDG_H, TOL, X, full, reduced, ry  # noqa: E402

LOOP_INPUTS = (np.eye(2, dtype=complex), X, H, SDG_H)       # |0>, |1>, |+>, |+i>
CP_HALF_PI = np.diag([1, 1, 1, 1j]).astype(complex)         # the eraser's loop: phase pi/2 when a = m = 1
# |a, m> -> |m, a xor m>: a = 1 has no consistent history (a grandfather-type loop that also writes a)
SWAP_WRITE = np.zeros((4, 4), complex)
for _a in (0, 1):
    for _m in (0, 1):
        SWAP_WRITE[2 * _m + (_a ^ _m), 2 * _a + _m] = 1
ONE_WAY = CNOT                                              # a controls a NOT on the loop


class Static:
    """A static history: states at clock points, all determined by the final point."""

    def __init__(self, names):
        self.names = list(names)
        self.n = len(self.names)
        self.D = 2 ** self.n
        self.Pi = self.op(np.outer(PHI_PLUS, PHI_PLUS.conj()), ['m', 'p'])

    def ix(self, r):
        return self.names.index(r)

    def op(self, gate, regs):
        return full(gate, [self.ix(r) for r in regs], self.n)

    def proj(self, reg, value):
        e = np.zeros(2, complex)
        e[value] = 1
        return self.op(np.outer(e, e), [reg])

    def prob(self, psi, reg, value=1):
        return float(reduced(psi, self.n, [self.ix(reg)])[value, value].real)

    def x_plus(self, psi, reg):
        rho = reduced(psi, self.n, [self.ix(reg)])
        return float(0.5 + rho[0, 1].real)

    # subclasses provide: self.final (no-loop final state), self.W {point: evolution to the end},
    # self.points, and final_with_loop_input(prep)

    def back(self, final):
        return {pt: self.W[pt].conj().T @ final for pt in self.points}

    def rule(self, name, sectors=None):
        if name == 'no_loop':
            return self.back(self.final)
        if name == 'p_ctc':
            F = self.Pi @ self.final
            return self.back(F / np.linalg.norm(F))
        if name == 'pps':
            total = np.zeros(self.D, complex)
            for P in sectors:
                S = P @ self.final
                w = np.linalg.norm(S) ** 2
                if w < TOL:
                    continue
                F = self.Pi @ S
                f = np.linalg.norm(F) ** 2
                total += S if f < TOL * w else F * np.sqrt(w / f)
            return self.back(total)
        raise ValueError(name)

    # ---------------------------------------------------------------- influence, sector by sector
    def uninfluenced(self, reg, P):
        finals = [P @ self.final_with_loop_input(prep) for prep in LOOP_INPUTS]
        weights = [np.linalg.norm(v) ** 2 for v in finals]
        if max(weights) < TOL:
            return True
        if max(weights) - min(weights) > 1e-9:
            return False
        rhos = [reduced(v / np.sqrt(w), self.n, [self.ix(reg)]) for v, w in zip(finals, weights)]
        return all(np.allclose(rhos[0], r, atol=1e-9) for r in rhos[1:])

    def influence_sectors(self, candidates):
        """Split by every record the loop cannot influence, given the records already split on."""
        sectors = [(np.eye(self.D, dtype=complex), frozenset())]
        changed = True
        while changed:
            changed, new = False, []
            for P, used in sectors:
                if np.linalg.norm(P @ self.final) ** 2 < TOL:
                    new.append((P, used))
                    continue
                for reg in candidates:
                    if reg not in used and self.uninfluenced(reg, P):
                        new += [(P @ self.proj(reg, v), used | {reg}) for v in (0, 1)]
                        changed = True
                        break
                else:
                    new.append((P, used))
            sectors = new
        self.last_influence_split = sectors
        return [P for P, _ in sectors]


class LocalClocks(Static):
    """Alice (a, loop m, partner p) and Bob (b, record rec_b), a and b in |Phi+>, each with a clock."""

    FRAMES = {'Bob first': [(0, 0), (0, 1), (1, 1)], 'Alice first': [(0, 0), (1, 0), (1, 1)]}

    def __init__(self, loop=ONE_WAY):
        super().__init__(['a', 'm', 'p', 'b', 'rec_b'])
        self.U = loop
        self.prep_ab = self.op(CNOT, ['a', 'b']) @ self.op(H, ['a'])
        prep_mp = self.op(CNOT, ['m', 'p']) @ self.op(H, ['m'])
        self.psi0 = np.zeros(self.D, complex)
        self.psi0[0] = 1
        self.psi0 = prep_mp @ self.prep_ab @ self.psi0
        self.A = self.op(loop, ['a', 'm'])
        self.B = self.op(CNOT, ['b', 'rec_b'])
        self.points = [(ta, tb) for ta in (0, 1) for tb in (0, 1)]
        mp = np.linalg.matrix_power
        self.state = {(ta, tb): mp(self.A, ta) @ mp(self.B, tb) @ self.psi0 for ta, tb in self.points}
        self.final = self.state[(1, 1)]
        self.W = {(ta, tb): mp(self.A, 1 - ta) @ mp(self.B, 1 - tb) for ta, tb in self.points}

    def final_with_loop_input(self, prep):
        e0 = np.zeros(self.D, complex)
        e0[0] = 1
        return self.A @ self.B @ self.op(prep, ['m']) @ self.prep_ab @ e0

    def clock_sectors(self, frame):
        path = self.FRAMES[frame]
        step = {('A' if b[0] > a[0] else 'B'): i for i, (a, b) in enumerate(zip(path, path[1:]))}
        if step['B'] < step['A']:
            return [self.proj('rec_b', v) for v in (0, 1)]
        return [np.eye(self.D, dtype=complex)]

    def constraints(self):
        """(J_A, J_B, H_in) on clock_A (x) clock_B (x) system: one Feynman-Kitaev transport constraint per
        clock, and the initial condition at (0, 0). The history satisfies all three."""
        D = self.D
        I2, I = np.eye(2), np.eye(D)
        def fk(G):
            out = np.zeros((2 * D, 2 * D), complex)
            out[:D, :D] += I
            out[D:, D:] += I
            out[D:, :D] -= G
            out[:D, D:] -= G.conj().T
            return out
        e00 = np.zeros((4, 4))
        e00[0, 0] = 1
        # ordering (clock_A, clock_B, system)
        J_A = np.einsum('aibj,cd->acibdj', fk(self.A).reshape(2, D, 2, D), I2).reshape(4 * D, 4 * D)
        J_B = np.einsum('ab,cidj->acibdj', I2, fk(self.B).reshape(2, D, 2, D)).reshape(4 * D, 4 * D)
        H_in = np.kron(e00, I - np.outer(self.psi0, self.psi0.conj()))
        return J_A, J_B, H_in

    def global_vector(self, hist):
        return np.concatenate([hist[(ta, tb)] for ta in (0, 1) for tb in (0, 1)])


class QuantumSwitch(Static):
    """Order of Alice's record (rec <- a) and her loop interaction controlled by c in |+>.
    With bob=True, Bob holds rec_b, a copy of a made before anything else in every branch; with
    bob=False nothing outside Alice's lab holds a's value (a is a "fresh" qubit)."""

    def __init__(self, variant='coherent', prior=0.5, loop=SWAP_WRITE, bob=True):
        names = ['c'] + (['rec_c'] if variant == 'classical' else []) + ['a', 'm', 'p', 'rec'] + (['rec_b'] if bob else [])
        super().__init__(names)
        self.variant = variant
        e0 = np.zeros(self.D, complex)
        e0[0] = 1
        prep = self.op(ry(2 * np.arcsin(np.sqrt(prior))), ['a'])
        if bob:
            prep = self.op(CNOT, ['a', 'rec_b']) @ prep
        prep = self.op(H, ['c']) @ prep
        if variant == 'classical':
            prep = self.op(CNOT, ['c', 'rec_c']) @ prep
        self.prep_no_mp = prep
        self.psi0 = self.op(CNOT, ['m', 'p']) @ self.op(H, ['m']) @ prep @ e0
        R = self.op(CNOT, ['a', 'rec'])
        L = self.op(loop, ['a', 'm'])
        c0, c1 = self.proj('c', 0), self.proj('c', 1)
        self.ticks = [c0 @ R + c1 @ L, c0 @ L + c1 @ R]
        self.points = [0, 1, 2]
        self.state = {0: self.psi0}
        for t, G in enumerate(self.ticks, 1):
            self.state[t] = G @ self.state[t - 1]
        self.final = self.state[2]
        self.W = {2: np.eye(self.D, dtype=complex), 1: self.ticks[1], 0: self.ticks[1] @ self.ticks[0]}

    def final_with_loop_input(self, prep):
        e0 = np.zeros(self.D, complex)
        e0[0] = 1
        return self.ticks[1] @ self.ticks[0] @ self.op(prep, ['m']) @ self.prep_no_mp @ e0

    def candidates(self):
        return [r for r in ('rec_b', 'rec_c', 'rec') if r in self.names]

    def clock_sectors(self):
        """rec_b is always written before the loop; rec only in the c = 0 branch. Using that order
        means splitting by c, a variable nothing has recorded in the coherent variant."""
        out = []
        bob = [self.proj('rec_b', b) for b in (0, 1)] if 'rec_b' in self.names else [np.eye(self.D, dtype=complex)]
        for Pb in bob:
            out += [Pb @ self.proj('c', 0) @ self.proj('rec', r) for r in (0, 1)]
            out.append(Pb @ self.proj('c', 1))
        return out
