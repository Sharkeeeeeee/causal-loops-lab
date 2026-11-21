"""SPDX-License-Identifier: MIT. No-signalling tests (signalling.py, ctc/NO_SIGNALLING.md).

Run from the repository root:  python -B ctc/tests/test_signalling.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from circuits import Circuit, bit_state, bootstrap, grandfather, interference, kfk  # noqa: E402
from literature import bhw_bb84  # noqa: E402
from signalling import (alice_marginal, alice_to_bob, attach_partner, bob_state, bob_to_alice,  # noqa: E402
                        output, p_ctc_signalling_operator)

ATOL = 1e-9
INF = np.inf
SCENARIOS = [(grandfather(0.05), 'jam'), (kfk(0.3, 0.6, 'motivated'), 'bad'),
             (kfk(0.3, 0.6, 'unconditional'), 'bad'), (interference(0.5, np.pi), 'a'), (bootstrap(), 'record')]


class Setup(unittest.TestCase):
    def test_partner_leaves_alice_unchanged(self):
        for c, label in SCENARIOS:
            for mode in ('classical', 'entangled'):
                cb = attach_partner(c, label, mode)
                n = len(cb.cr_labels)
                self.assertTrue(np.allclose(np.diag(alice_marginal(cb.rho, n)), np.diag(c.rho), atol=ATOL))

    def test_partner_does_not_change_alice_results(self):
        """Adding Bob must not change what Alice sees under any rule."""
        for c, label in SCENARIOS:
            cb = attach_partner(c, label, 'classical')
            n = len(cb.cr_labels)
            for rule in ('no_loop', 'p_ctc', 'd_ctc'):
                alone, joint = output(c, rule), output(cb, rule)
                if alone is None:
                    self.assertIsNone(joint)
                    continue
                self.assertTrue(np.allclose(np.diag(alice_marginal(joint, n)), np.diag(alone), atol=ATOL), (c.name, rule))


class AliceToBob(unittest.TestCase):
    def test_no_loop_and_deutsch_never_signal(self):
        for c, label in SCENARIOS:
            for mode in ('classical', 'entangled'):
                cb = attach_partner(c, label, mode)
                for rule in ('no_loop', 'd_ctc'):
                    self.assertLess(alice_to_bob(cb, rule), ATOL, (c.name, mode, rule))

    def test_postselection_signals_exactly_when_alice_is_reweighted(self):
        """Bob's shift equals the change in Alice's marginal of the correlated bit."""
        expected = {'grandfather': 0.95,                                   # 0.05 -> 1
                    'kfk_motivated': 0.3 - 0.3 * 0.4 / (1 - 0.3 * 0.6),    # q -> q(1-r)/(1-qr)
                    'kfk_unconditional': 0.0,
                    'interference': 0.5,                                   # a = 1 branch deleted
                    'bootstrap': 0.0}                                      # record has no prior randomness
        for c, label in SCENARIOS:
            for mode in ('classical', 'entangled'):
                cb = attach_partner(c, label, mode)
                self.assertAlmostEqual(alice_to_bob(cb, 'p_ctc'), expected[c.name], places=9, msg=(c.name, mode))

    def test_branch_model_signals_iff_beta_positive(self):
        for c, label in SCENARIOS:
            if c.name == 'interference':
                continue  # has a phase; the classical model refuses it
            cb = attach_partner(c, label, 'classical')
            for kappa in (0, 0.5, 1):
                self.assertLess(alice_to_bob(cb, 'branches', kappa=kappa, beta=0), ATOL, (c.name, kappa))
                if c.name in ('grandfather', 'kfk_motivated'):
                    for beta in (0.1, 1.0, INF):
                        self.assertGreater(alice_to_bob(cb, 'branches', kappa=kappa, beta=beta), 1e-3,
                                           (c.name, kappa, beta))

    def test_grandfather_closed_form(self):
        """Bob's copy of the jam bit moves from eps to eps / (eps + (1 - eps) e^-beta)."""
        eps = 0.05
        cb = attach_partner(grandfather(eps), 'jam', 'classical')
        for beta in (0.5, 2.0, 5.0):
            moved = eps / (eps + (1 - eps) * np.exp(-beta))
            self.assertAlmostEqual(alice_to_bob(cb, 'branches', kappa=0.3, beta=beta), moved - eps, places=9)


class PostselectionCriterion(unittest.TestCase):
    def test_bob_state_is_transpose_of_cdagc(self):
        """With Bob maximally entangled with all of Alice's CR system, Bob's P-CTC state is
        (C^dag C)^T / Tr. So P-CTC is no-signalling for every shared state iff C^dag C ~ 1."""
        for c in (grandfather(0.05), interference(0.5, 1.2),
                  Circuit('bootstrap_mixed', ['record'], ['message'], bootstrap().U, bit_state(0.5), bit_state(0.5))):
            cb = attach_partner(Circuit(c.name, c.cr_labels, c.loop_labels, c.U, np.eye(2) / 2, c.baseline_loop),
                                c.cr_labels[0], 'entangled')
            post = output(cb, 'p_ctc')
            M = p_ctc_signalling_operator(c)
            predicted = M.T / np.trace(M)
            self.assertTrue(np.allclose(bob_state(post, len(cb.cr_labels)), predicted, atol=ATOL), c.name)

    def test_criterion_classifies_circuits(self):
        def proportional_to_identity(M):
            return np.allclose(M, np.trace(M) / M.shape[0] * np.eye(M.shape[0]), atol=ATOL)
        self.assertFalse(proportional_to_identity(p_ctc_signalling_operator(grandfather(0.05))))
        self.assertFalse(proportional_to_identity(p_ctc_signalling_operator(bootstrap())))
        trivial = Circuit('identity', ['a'], ['m'], np.eye(4, dtype=complex), bit_state(0.3), bit_state(0.5))
        self.assertTrue(proportional_to_identity(p_ctc_signalling_operator(trivial)))

    def test_bootstrap_signals_once_the_record_is_entangled(self):
        """bootstrap() does not signal only because its record starts in |0>."""
        c = Circuit('bootstrap_mixed', ['record'], ['message'], bootstrap().U, bit_state(0.5), bit_state(0.5))
        self.assertAlmostEqual(alice_to_bob(attach_partner(c, 'record', 'entangled'), 'p_ctc'), 0.5, places=9)


class BobToAlice(unittest.TestCase):
    def setUp(self):
        self.cb = attach_partner(bhw_bb84(np.eye(2) / 2), 'a', 'entangled')  # psi maximally entangled with Bob

    def alice_probs(self, rule, basis, prescription):
        return np.diag(bob_to_alice(self.cb, rule, basis, prescription)).real

    def test_global_prescriptions_do_not_signal(self):
        for rule in ('p_ctc', 'd_ctc'):
            self.assertTrue(np.allclose(self.alice_probs(rule, 'Z', 'global'), self.alice_probs(rule, 'X', 'global'),
                                        atol=ATOL), rule)

    def test_deutsch_per_branch_lets_bob_signal_perfectly(self):
        """Applied branch by branch, D-CTC reveals Bob's basis in Alice's first output bit."""
        z = self.alice_probs('d_ctc', 'Z', 'per_branch')
        x = self.alice_probs('d_ctc', 'X', 'per_branch')
        self.assertAlmostEqual(z[0] + z[1], 1.0, places=9)   # first bit 0 after a Z measurement
        self.assertAlmostEqual(x[2] + x[3], 1.0, places=9)   # first bit 1 after an X measurement


if __name__ == '__main__':
    unittest.main(verbosity=2)
