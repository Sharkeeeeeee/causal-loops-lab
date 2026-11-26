"""SPDX-License-Identifier: MIT. Choosing the world rule: jumps are forced for single-basis rules, a mixed rule avoids them (THEOREMS.md, Theorem 9).

  9(1) state-only   any rule that depends only on rho_A and obeys (R) jumps at rho_A = 1/d: the limits along
                    two diagonal directions differ;
  9(3) mixed rule   (1 - c) Phi_pointer + c Phi_state, c the record overlap, is safe (a fixed channel given the
                    history), continuous in the record strength on the weak-readout family, P-CTC with no
                    record, the pointer rule with a perfect one (so recorded fair coins and Theorem 4's Bell
                    example behave as under the pointer rule).

9(2), the topological statement for single-basis history rules, is proved in THEOREMS.md, not tested.

Run from the repository root:  python -B ctc/tests/test_mixed_rule.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from mixed_rule import mixed_rule_kraus, record_overlap  # noqa: E402
from past_preserving import basis_containing, past_preserving_kraus  # noqa: E402
from records import state_world_kraus  # noqa: E402
from test_readouts import ERASER, alice_channel, embed, marginal, outside_measurement  # noqa: E402

RNG = np.random.default_rng(909)
ATOL = 1e-9
CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], complex)
S = 1 / np.sqrt(2)
H = np.array([[S, S], [S, -S]], complex)


def haar(d):
    z = RNG.normal(size=(d, d)) + 1j * RNG.normal(size=(d, d))
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / abs(np.diag(r)))


def readout(c):
    """Controlled rotation onto O from |0> with record overlap c."""
    th = 2 * np.arccos(c)
    co, si = np.cos(th / 2), np.sin(th / 2)
    return np.kron(np.diag([1, 0]), np.eye(2)) + np.kron(np.diag([0, 1]), np.array([[co, -si], [si, co]]))


def weak_state(p1, c):
    psi = np.array([np.sqrt(1 - p1), np.sqrt(p1)], complex)
    v = readout(c) @ np.kron(psi, [1, 0])
    return np.outer(v, v.conj()), psi


def p1_after(kraus, rho):
    return marginal(alice_channel(kraus, rho, [2, 2]), [2, 2], [0])[1, 1].real


def mixed(U, rho, c):
    return mixed_rule_kraus(U, 2, 2, np.eye(2), marginal(rho, [2, 2], [0]), c)


class StateOnlyRulesJump(unittest.TestCase):
    def test_limits_along_two_directions_differ(self):
        """rho_A = 1/2 + t sigma: (R) and state completeness force the eigenbasis for t != 0 (purify by a
        perfect record in it). Along Z the worlds are Z, along X they are X; the outputs do not meet."""
        outs = {}
        for name, B in (('Z', np.eye(2, dtype=complex)), ('X', H)):
            vals = []
            for t in (1e-2, 1e-4, 1e-6):
                rho_a = B @ np.diag([0.5 + t, 0.5 - t]) @ B.conj().T
                vals.append(sum(K @ rho_a @ K.conj().T for K in state_world_kraus(ERASER, 2, 2, rho_a))[1, 1].real)
            outs[name] = vals
            self.assertLess(abs(vals[-1] - vals[-2]), 1e-4)
        self.assertGreater(abs(outs['Z'][-1] - outs['X'][-1]), 0.1)


class MixedRule(unittest.TestCase):
    def test_record_overlap(self):
        for c in (0.0, 0.3, 0.9, 1.0):
            self.assertAlmostEqual(record_overlap(readout(c), 2, 2), c, delta=1e-9)
        self.assertAlmostEqual(record_overlap(CNOT, 2, 2), 0.0, delta=1e-12)

    def test_never_signals(self):
        dims = [2, 2]
        for _ in range(12):
            U = haar(4)
            c = float(RNG.random())
            rho, _ = weak_state(float(RNG.random()), c)
            kraus = mixed(U, rho, c)
            out = alice_channel(kraus, rho, dims)
            np.testing.assert_allclose(marginal(out, dims, [1]), marginal(rho, dims, [1]), atol=ATOL)
            W = embed(haar(2), [1], dims)
            for pre in (W @ rho @ W.conj().T, outside_measurement(rho, dims, 1, haar(2))):
                np.testing.assert_allclose(marginal(alice_channel(kraus, pre, dims), dims, [0]),
                                           marginal(out, dims, [0]), atol=1e-7)

    def test_continuous_from_no_record_to_a_perfect_one(self):
        cs = np.linspace(1, 0, 101)
        for p1 in (0.3, 0.5):
            vals = []
            for c in cs:
                rho, psi = weak_state(p1, c)
                vals.append(p1_after(mixed(ERASER, rho, c), rho))
            fresh_rho, psi = weak_state(p1, 1.0)
            self.assertAlmostEqual(vals[0], p1_after(past_preserving_kraus(ERASER, 2, 2, basis_containing(psi)), fresh_rho), delta=1e-9)
            self.assertAlmostEqual(vals[-1], p1, delta=1e-9)
            self.assertLess(np.max(np.abs(np.diff(vals))), 0.01)

    def test_the_single_basis_rules_jump_on_the_same_family(self):
        rho1, psi = weak_state(0.3, 1.0)
        rho2, _ = weak_state(0.3, 0.995)
        fresh = p1_after(past_preserving_kraus(ERASER, 2, 2, basis_containing(psi)), rho1)
        pointer = p1_after(past_preserving_kraus(ERASER, 2, 2, np.eye(2)), rho2)
        self.assertGreater(pointer - fresh, 0.1)                       # pointer rule: jump at the first trace
        near = weak_state(0.5, 1e-4)[0]
        at = weak_state(0.5, 0.0)[0]
        s_near = p1_after(state_world_kraus(ERASER, 2, 2, marginal(near, [2, 2], [0])), near)
        s_at = p1_after(state_world_kraus(ERASER, 2, 2, marginal(at, [2, 2], [0])), at)
        self.assertGreater(abs(s_at - s_near), 0.04)                   # state rule: jump at the degenerate point
        m_near, m_at = p1_after(mixed(ERASER, near, 1e-4), near), p1_after(mixed(ERASER, at, 0.0), at)
        self.assertLess(abs(m_at - m_near), 1e-3)

    def test_perfect_records_behave_as_under_the_pointer_rule(self):
        """A recorded fair coin is split on (no jump at P = 1/2), and Theorem 4's Bell example (one_way loop,
        Bell pair made by a CNOT) gives Alice P(a = 0) = 0.5, as under the pointer rule."""
        for U in (ERASER, CNOT, haar(4)):
            rho, _ = weak_state(0.5, 0.0)
            np.testing.assert_allclose(alice_channel(mixed(U, rho, 0.0), rho, [2, 2]),
                                       alice_channel(past_preserving_kraus(U, 2, 2, np.eye(2)), rho, [2, 2]), atol=ATOL)
        bell = CNOT @ np.kron(np.array([S, S], complex), [1, 0])
        rho = np.outer(bell, bell.conj())
        c = record_overlap(CNOT, 2, 2)
        out = alice_channel(mixed(CNOT, rho, c), rho, [2, 2])
        self.assertAlmostEqual(marginal(out, [2, 2], [0])[0, 0].real, 0.5, delta=ATOL)
        self.assertAlmostEqual(marginal(out, [2, 2], [1])[0, 0].real, 0.5, delta=ATOL)


if __name__ == '__main__':
    unittest.main(verbosity=1)
