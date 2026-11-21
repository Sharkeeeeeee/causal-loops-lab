"""SPDX-License-Identifier: MIT. Reproduces statements from [L11] and [BHW] (see literature.py).

Run from the repository root:  python -B ctc/tests/test_literature.py
Each test names the statement it checks. 'Ours' marks results derived here, not in the papers.
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import (check_unitary, d_ctc, p_ctc, p_ctc_by_teleportation,  # noqa: E402
                    p_ctc_success_probability)
from literature import (BB84_CLAIM, KET, bhw_bb84, bhw_two_state, lloyd_grandfather,  # noqa: E402
                        lloyd_unproved_theorem, pure)

ATOL = 1e-10


def diag(rho):
    return np.diag(rho).real


def basis(n_qubits, bits):
    v = np.zeros(2 ** n_qubits)
    v[int(''.join(map(str, bits)), 2)] = 1
    return v


class BrunHarringtonWilde(unittest.TestCase):
    def test_fig1_distinguishes_0_and_minus(self):
        """[BHW] Fig. 1: outcome 0 for |0>, outcome 1 for |->; unique rho_CTC = |0><0|, |1><1|."""
        for label, outcome in [('0', 0), ('-', 1)]:
            c = bhw_two_state(label)
            out, tau, multiplicity = d_ctc(c.U, c.rho, c.d_cr, c.d_loop)
            self.assertTrue(np.allclose(diag(out), basis(1, [outcome]), atol=ATOL))
            self.assertTrue(np.allclose(tau, pure(KET[str(outcome)]), atol=ATOL))
            self.assertEqual(multiplicity, 1)

    def test_fig2_perfectly_distinguishes_bb84(self):
        """[BHW] Fig. 2, Eq. (3): |00>->|00>, |+0>->|10>, |10>->|01>, |-0>->|11>,
        with a unique fixed point that is a computational basis state."""
        for label, bits in BB84_CLAIM.items():
            c = bhw_bb84(pure(KET[label]))
            self.assertLess(check_unitary(c.U), ATOL)
            out, tau, multiplicity = d_ctc(c.U, c.rho, c.d_cr, c.d_loop)
            self.assertTrue(np.allclose(diag(out), basis(2, bits), atol=ATOL), label)
            self.assertEqual(multiplicity, 1, label)
            self.assertTrue(np.allclose(diag(tau), basis(2, bits), atol=ATOL), label)

    def test_ours_deutsch_map_is_nonlinear_on_mixtures(self):
        """Ours: feeding the 50/50 mixture of |0> and |+> is not the mixture of the outputs.
        This is the input-dependence that Bennett-Leung-Smith-Smolin (2009) debated."""
        mixed = (pure(KET['0']) + pure(KET['+'])) / 2
        out_mixed, _, _ = d_ctc(*[getattr(bhw_bb84(mixed), k) for k in ('U', 'rho', 'd_cr', 'd_loop')])
        averaged = (basis(2, BB84_CLAIM['0']) + basis(2, BB84_CLAIM['+'])) / 2
        self.assertGreater(np.max(abs(diag(out_mixed) - averaged)), 0.05)


class Lloyd2011(unittest.TestCase):
    def test_perfect_gun_is_a_paradox_for_p_ctc(self):
        """[L11] p.3: with a perfect sigma_x the projection amplitude is always null."""
        c = lloyd_grandfather(np.pi)
        post, weight = p_ctc(c.U, c.rho, c.d_cr, c.d_loop)
        self.assertIsNone(post)
        self.assertLess(p_ctc_success_probability(c.U, c.rho, c.d_cr, c.d_loop), ATOL)

    def test_deutsch_maximally_mixed_and_always_succeeds(self):
        """[L11] p.2 and Fig. 2 caption: rho = (|0><0|+|1><1|)/2 is the only fixed point;
        'Using Deutsch's CTCs, she always succeeds' (probes opposite)."""
        c = lloyd_grandfather(np.pi)
        out, tau, multiplicity = d_ctc(c.U, c.rho, c.d_cr, c.d_loop)
        self.assertEqual(multiplicity, 1)
        self.assertTrue(np.allclose(tau, np.eye(2) / 2, atol=ATOL))
        opposite = c.probability_one(out, 'probe_a') + c.probability_one(out, 'probe_b') - 2 * out[3, 3].real
        self.assertAlmostEqual(opposite, 1.0, places=10)

    def test_imperfect_gun_probes_always_agree(self):
        """[L11] p.3 / Fig. 4: probes never found in 01 or 10 when time travel succeeds."""
        for theta in np.linspace(0, np.pi * 0.99, 12):
            c = lloyd_grandfather(theta)
            post, _ = p_ctc(c.U, c.rho, c.d_cr, c.d_loop)
            self.assertAlmostEqual(post[1, 1].real + post[2, 2].real, 0.0, places=10)

    def test_fig4_theory_curve(self):
        """[L11] Fig. 4 solid curve: 0.5 at theta = 0 falling to 0 at 180 degrees.
        The closed form cos^2(theta/2)/2 is ours; the paper gives the curve only."""
        for theta in np.linspace(0, np.pi, 19):
            c = lloyd_grandfather(theta)
            success = p_ctc_success_probability(c.U, c.rho, c.d_cr, c.d_loop)
            self.assertAlmostEqual(success, np.cos(theta / 2) ** 2 / 2, places=10)
        c = lloyd_grandfather(np.pi / 2)
        self.assertAlmostEqual(p_ctc_success_probability(c.U, c.rho, c.d_cr, c.d_loop), 0.25, places=10)

    def test_teleportation_simulation_matches_c_formula(self):
        """[L11-PRD] Eqs. (8)-(9): postselected teleportation equals C rho C^dag, C = Tr_CTC U,
        with success probability Tr[C rho C^dag]/d^2. Checked by explicit simulation."""
        cases = [lloyd_grandfather(t) for t in (0.0, 1.0, 2.5)] + [lloyd_unproved_theorem(),
                                                                  bhw_bb84(pure(KET['+']))]
        for c in cases:
            post, _ = p_ctc(c.U, c.rho, c.d_cr, c.d_loop)
            tele, success = p_ctc_by_teleportation(c.U, c.rho, c.d_cr, c.d_loop)
            self.assertTrue(np.allclose(post, tele, atol=ATOL), c.name)
            self.assertAlmostEqual(success, p_ctc_success_probability(c.U, c.rho, c.d_cr, c.d_loop), places=10)

    def test_unproved_theorem_proof_bit_is_completely_mixed(self):
        """[L11] Fig. 2b caption: the proof bit gets a completely mixed value because it is
        maximally entangled with the qubit emerging from the CTC."""
        c = lloyd_unproved_theorem()
        post, _ = p_ctc(c.U, c.rho, c.d_cr, c.d_loop)
        bell = (basis(2, [0, 0]) + basis(2, [1, 1])) / np.sqrt(2)
        self.assertTrue(np.allclose(post, np.outer(bell, bell), atol=ATOL))
        proof = np.einsum('aibi->ab', post.reshape(2, 2, 2, 2))
        self.assertTrue(np.allclose(proof, np.eye(2) / 2, atol=ATOL))

    def test_ours_deutsch_gun_curve(self):
        """Ours: under D-CTC the probes disagree ('kill') with probability sin^2(theta/2)."""
        for theta in np.linspace(0.05, np.pi, 10):
            c = lloyd_grandfather(theta)
            out, _, _ = d_ctc(c.U, c.rho, c.d_cr, c.d_loop)
            self.assertAlmostEqual(out[1, 1].real + out[2, 2].real, np.sin(theta / 2) ** 2, places=10)

    def test_ours_unproved_theorem_deutsch_is_classical(self):
        """Ours: D-CTC gives the same 50/50 statistics but a classical mixture, not entanglement."""
        c = lloyd_unproved_theorem()
        out, _, _ = d_ctc(c.U, c.rho, c.d_cr, c.d_loop)
        expected = (np.outer(basis(2, [0, 0]), basis(2, [0, 0])) + np.outer(basis(2, [1, 1]), basis(2, [1, 1]))) / 2
        self.assertTrue(np.allclose(out, expected, atol=ATOL))


if __name__ == '__main__':
    unittest.main(verbosity=2)
