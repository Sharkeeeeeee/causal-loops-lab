"""SPDX-License-Identifier: MIT. Loop rules in a timeless (Page-Wootters) universe.

The whole history is one static state on clock (x) system,

    Psi = sum_t |t>_clock (x) psi_t,     psi_t = G_t ... G_1 psi_0,

the zero-energy state of a Feynman-Kitaev constraint H_FK (checked by `constraint_residual`).
Nothing in Psi "happens": time is only the reading of the clock register, and the state at
time t is the conditional state psi_t = <t|_clock Psi.

The loop is the usual teleportation picture: loop qubit m and partner p start in |Phi+>, U acts
on CR x m, and consistency means (m, p) are found in |Phi+> at the end. Here that condition is a
constraint on the static state: Pi_hat = sum_t |t><t| (x) W_t^dag Pi W_t, with W_t the evolution
from clock reading t to the end. Pi_hat acts on every clock reading at once.

Rules, all written without any time parameter:
  no loop : Psi itself (the loop input is maximally mixed).
  P-CTC   : Pi_hat Psi, normalized once, globally.
  PPS     : split Psi into record sectors Psi_r (orthogonal values of the protected record
            registers), apply Pi_hat inside each sector and give it back its weight ||Psi_r||^2.
            A sector with no consistent history keeps Psi_r (the D-CTC fallback of these
            circuits, see hardware/experiments.fallback_matches_no_loop).

What counts as a protected record ("the past") is the question this module studies:
  'clock'     : records written at an earlier clock reading than the loop interaction
  'all'       : every record register
  'influence' : records whose value the loop cannot influence (decided from the dynamics:
                changing the loop's input never changes the record's reduced state)
"""
import itertools
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / 'hardware'))
from experiments import BASIS, EXPERIMENTS, BY_NAME  # noqa: E402,F401

TOL = 1e-10
_S = 1 / np.sqrt(2)
H = np.array([[_S, _S], [_S, -_S]], complex)
X = np.array([[0, 1], [1, 0]], complex)
SDG_H = np.array([[1, 0], [0, 1j]], complex) @ H          # |0> -> (|0> + i|1>)/sqrt2
CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], complex)
PHI_PLUS = np.array([1, 0, 0, 1], complex) * _S
ORDERS = ('record-first', 'loop-first')
DEFINITIONS = ('clock', 'all', 'influence')


def ry(theta):
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], complex)


def apply(gate, targets, n, psi):
    """Apply `gate` (on len(targets) qubits, first target most significant) to psi of shape (2**n, ...)."""
    rest = psi.shape[1:]
    t = psi.reshape((2,) * n + rest)
    t = np.moveaxis(t, list(targets), list(range(len(targets))))
    shape = t.shape
    t = (gate @ t.reshape(2 ** len(targets), -1)).reshape(shape)
    t = np.moveaxis(t, list(range(len(targets))), list(targets))
    return t.reshape(psi.shape)


def full(gate, targets, n):
    return apply(gate, targets, n, np.eye(2 ** n, dtype=complex))


class Model:
    """One hardware experiment as a timeless history.

    Registers: CR qubits, loop m, partner p, one record per recorded CR qubit. Clock readings:
    0 (all registers 0), then one per step: 'prepare' (RY on CR inputs, |Phi+> on m, p),
    'record' (CNOT CR -> record) and 'loop' (U on CR x m), in the given order. The record and
    loop steps commute in every experiment, so the two orders describe the same physics read
    with two different clocks.
    """

    def __init__(self, exp, order='record-first'):
        if order not in ORDERS:
            raise ValueError(order)
        self.exp, self.order = exp, order
        self.regs = list(exp.cr_labels) + ['m', 'p'] + ['rec_' + l for l in exp.recorded]
        self.n = len(self.regs)
        self.D = 2 ** self.n
        ix = self.regs.index
        n = self.n
        self.prep_cr = np.eye(self.D, dtype=complex)
        for label in exp.recorded:
            self.prep_cr = full(ry(2 * np.arcsin(np.sqrt(exp.priors[label]))), [ix(label)], n) @ self.prep_cr
        bell = full(CNOT, [ix('m'), ix('p')], n) @ full(H, [ix('m')], n)
        record = np.eye(self.D, dtype=complex)
        for label in exp.recorded:
            record = full(CNOT, [ix(label), ix('rec_' + label)], n) @ record
        loop = full(exp.unitary(), [ix(l) for l in exp.cr_labels] + [ix('m')], n)
        self.steps = [('prepare', bell @ self.prep_cr)]
        self.steps += [('record', record), ('loop', loop)] if order == 'record-first' else [('loop', loop), ('record', record)]
        self.T = len(self.steps)
        self.step_of = {name: i + 1 for i, (name, _) in enumerate(self.steps)}   # clock reading after the step
        self.psi0 = np.zeros(self.D, complex)
        self.psi0[0] = 1
        self.history = self._evolve(self.psi0, [G for _, G in self.steps])
        self.W = [None] * (self.T + 1)
        self.W[self.T] = np.eye(self.D, dtype=complex)
        for t in range(self.T - 1, -1, -1):
            self.W[t] = self.W[t + 1] @ self.steps[t][1]
        self.Pi = full(np.outer(PHI_PLUS, PHI_PLUS.conj()), [ix('m'), ix('p')], n)
        # record registers and the step that writes them
        self.written = {'rec_' + l: 'record' for l in exp.recorded}
        if 'log' in exp.cr_labels:
            self.written['log'] = 'loop'

    # ---------------------------------------------------------------- building blocks
    @staticmethod
    def _evolve(psi0, gates):
        out = [psi0]
        for G in gates:
            out.append(G @ out[-1])
        return np.array(out)

    def lift(self, op_final):
        """A condition on the final clock reading, as an operator on every clock reading."""
        return [self.W[t].conj().T @ op_final @ self.W[t] for t in range(self.T + 1)]

    @staticmethod
    def act(ops, hist):
        return np.array([ops[t] @ hist[t] for t in range(len(ops))])

    def basis_of(self, reg):
        return BASIS[self.exp.record_basis] if reg.startswith('rec_') else BASIS['Z']

    def sectors(self, registers):
        """(key, projector at the final clock reading) for every joint record value."""
        ix = self.regs.index
        for outcome in itertools.product((0, 1), repeat=len(registers)):
            P = np.eye(self.D, dtype=complex)
            for reg, j in zip(registers, outcome):
                b = self.basis_of(reg)[:, j]
                P = full(np.outer(b, b.conj()), [ix(reg)], self.n) @ P
            yield outcome, P

    # ---------------------------------------------------------------- what counts as the past
    def influenced(self, reg):
        """True if the loop's input can change the reduced state of `reg` at the end."""
        ix = self.regs.index
        finals = []
        for prep in (np.eye(2), X, H, SDG_H):        # loop input |0>, |1>, |+>, |+i>, no partner
            gates = [full(prep, [ix('m')], self.n) @ self.prep_cr] + [G for name, G in self.steps[1:]]
            psi = self._evolve(self.psi0, gates)[-1]
            finals.append(reduced(psi, self.n, [ix(reg)]))
        return any(not np.allclose(finals[0], f, atol=1e-9) for f in finals[1:])

    def protected(self, definition):
        regs = list(self.written)
        if definition == 'clock':
            return [r for r in regs if self.step_of[self.written[r]] < self.step_of['loop']]
        if definition == 'all':
            return regs
        if definition == 'influence':
            return [r for r in regs if not self.influenced(r)]
        raise ValueError(definition)

    # ---------------------------------------------------------------- rules
    def state(self, rule, definition='influence'):
        """The global history under a rule, as an array (clock reading, system amplitudes).
        Every clock reading has norm 1 (the constrained histories are still unitarily transported)."""
        Psi = self.history
        if rule == 'no_loop':
            return Psi.copy()
        PiL = self.lift(self.Pi)
        if rule == 'p_ctc':
            F = self.act(PiL, Psi)
            f = np.linalg.norm(F[-1])
            return None if f < TOL else F / f
        if rule == 'pps':
            total = np.zeros_like(Psi)
            for _, P in self.sectors(self.protected(definition)):
                S = self.act(self.lift(P), Psi)
                w = np.linalg.norm(S[-1]) ** 2
                if w < TOL:
                    continue
                F = self.act(PiL, S)
                f = np.linalg.norm(F[-1]) ** 2
                total += S if f < TOL * w else F * np.sqrt(w / f)
            return total
        raise ValueError(rule)

    # ---------------------------------------------------------------- timelessness
    def constraint_operator(self):
        """Feynman-Kitaev constraint: H_FK Psi = 0 exactly for the history state (no time evolution)."""
        T, D = self.T, self.D
        Hfk = np.zeros(((T + 1) * D, (T + 1) * D), complex)
        blk = lambda a, b: (slice(a * D, (a + 1) * D), slice(b * D, (b + 1) * D))
        I = np.eye(D)
        for t in range(1, T + 1):
            G = self.steps[t - 1][1]
            Hfk[blk(t, t)] += I
            Hfk[blk(t - 1, t - 1)] += I
            Hfk[blk(t, t - 1)] -= G
            Hfk[blk(t - 1, t)] -= G.conj().T
        transport = Hfk.copy()
        Hfk[blk(0, 0)] += I - np.outer(self.psi0, self.psi0.conj())
        return Hfk, transport

    def constraint_residual(self, hist):
        """(total residual of H_FK, residual of its transport part alone) for a history."""
        Hfk, transport = self.constraint_operator()
        v = hist.reshape(-1)
        return float(np.linalg.norm(Hfk @ v)), float(np.linalg.norm(transport @ v))

    # ---------------------------------------------------------------- readout
    def prob(self, hist, t, reg, value=1, basis=None):
        """P(reg reads `value`) in the conditional state at clock reading t."""
        b = (self.basis_of(reg) if basis is None else BASIS[basis])[:, value]
        rho = reduced(hist[t], self.n, [self.regs.index(reg)])
        return float(np.real(b.conj() @ rho @ b))

    def joint(self, hist):
        """Final distribution {(record bits, CR outcome y): prob} in the format of experiments.exact."""
        exp, ix = self.exp, self.regs.index
        psi = hist[-1].copy()
        for label in exp.cr_labels:
            psi = apply(BASIS[exp.cr_basis.get(label, 'Z')].conj().T, [ix(label)], self.n, psi)
        for label in exp.recorded:
            psi = apply(BASIS[exp.record_basis].conj().T, [ix('rec_' + label)], self.n, psi)
        p = np.abs(psi.reshape((2,) * self.n)) ** 2
        p = p.sum(axis=(ix('m'), ix('p')))            # m, p are adjacent: summing removes both axes
        kept = [r for r in self.regs if r not in ('m', 'p')]
        out = {}
        for bits in itertools.product((0, 1), repeat=len(kept)):
            val = dict(zip(kept, bits))
            y = sum(val[l] << (exp.n_cr - 1 - i) for i, l in enumerate(exp.cr_labels))
            k = tuple(val['rec_' + l] for l in exp.recorded)
            out[(k, y)] = out.get((k, y), 0.0) + float(p[bits])
        return out


def reduced(psi, n, keep):
    t = psi.reshape((2,) * n)
    others = [i for i in range(n) if i not in keep]
    t = np.moveaxis(t, keep + others, list(range(n))).reshape(2 ** len(keep), -1)
    return t @ t.conj().T
