"""SPDX-License-Identifier: MIT. Tests for the transition-probability CTC rule (models.t_ctc).

[A14] J.-M. A. Allen, "Treating Time Travel Quantum Mechanically", Phys. Rev. A 90,
      042107 (2014), arXiv:1401.4933. Equation numbers refer to the arXiv version.

Run from the repository root:  python -B ctc/tests/test_t_ctc.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from circuits import Circuit, bit_state, grandfather, interference, kfk  # noqa: E402
from literature import bhw_bb84, lloyd_unproved_theorem  # noqa: E402
from models import d_ctc, maximally_mixed_loop, p_ctc, partial_trace_operator_loop, t_ctc  # noqa: E402
from signalling import alice_to_bob, attach_partner, bob_state, bob_to_alice, output  # noqa: E402

ATOL = 1e-9
RNG = np.random.default_rng(20261122)


def random_unitary(d):
    z = (RNG.normal(size=(d, d)) + 1j * RNG.normal(size=(d, d))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / abs(np.diag(r)))


def random_pure(d):
    v = RNG.normal(size=d) + 1j * RNG.normal(size=d)
    return v / np.linalg.norm(v)


# The six Pauli eigenstates form a 3-design on one qubit, so averaging over them
# reproduces the Haar integral of any expression of degree 2 in |phi> and <phi| exactly.
PAULI_STATES = [np.array(v, complex) / np.linalg.norm(v) for v in
                ([1, 0], [0, 1], [1, 1], [1, -1], [1, 1j], [1, -1j])]


def t_ctc_by_haar_average(U, rho, d_cr):
    """Allen Eq. (24) evaluated directly: rho_f ~ avg_phi U_phi rho U_phi^dag with
    U_phi = <phi|U|phi>, for a one-qubit loop. Independent of the closed form Eq. (33)."""
    U4 = U.reshape(d_cr, 2, d_cr, 2)
    total = np.zeros((d_cr, d_cr), complex)
    for phi in PAULI_STATES:
        U_phi = np.einsum('i,aibj,j->ab', phi.conj(), U4, phi)
        total += U_phi @ rho @ U_phi.conj().T
    return total / np.trace(total).real


class AgreesWithAllen(unittest.TestCase):
    def test_closed_form_equals_haar_average(self):
        """Eq. (33) (closed form) equals Eq. (24) (integral over pure loop states)."""
        cases = [grandfather(0.05), interference(0.5, 1.2), kfk(0.3, 0.6, 'motivated')]
        for c in cases:
            closed, _ = t_ctc(c.U, c.rho, c.d_cr, c.d_loop)
            self.assertTrue(np.allclose(closed, t_ctc_by_haar_average(c.U, c.rho, c.d_cr), atol=ATOL), c.name)
        for _ in range(5):
            U = random_unitary(4)
            v = random_pure(2)
            rho = np.outer(v, v.conj())
            self.assertTrue(np.allclose(t_ctc(U, rho, 2, 2)[0], t_ctc_by_haar_average(U, rho, 2), atol=ATOL))

    def test_unproved_theorem_matches_eq_35(self):
        c = lloyd_unproved_theorem()
        expected = np.zeros((4, 4))
        expected[0, 0] = expected[3, 3] = 0.5
        expected[0, 3] = expected[3, 0] = 0.25
        self.assertTrue(np.allclose(t_ctc(c.U, c.rho, c.d_cr, c.d_loop)[0], expected, atol=ATOL))

    def test_channel_weight_matches_eq_38(self):
        """lambda = d / (d + ||P psi||^2) >= 1 / (d + 1)."""
        for _ in range(5):
            U = random_unitary(8)            # CR = 2 qubits, loop = 1 qubit
            v = random_pure(4)
            P = partial_trace_operator_loop(U, 4, 2)
            _, lam = t_ctc(U, np.outer(v, v.conj()), 4, 2)
            self.assertAlmostEqual(lam, 2 / (2 + np.linalg.norm(P @ v) ** 2), places=10)
            self.assertGreaterEqual(lam, 1 / 3 - ATOL)

    def test_product_unitary_ignores_loop(self):
        """Sec. IV E.1: U = V x W gives rho_f = V rho V^dag."""
        V, W = random_unitary(2), random_unitary(2)
        v = random_pure(2)
        rho = np.outer(v, v.conj())
        self.assertTrue(np.allclose(t_ctc(np.kron(V, W), rho, 2, 2)[0], V @ rho @ V.conj().T, atol=ATOL))

    def test_distinguishability_bound_eq_40(self):
        """D(rho_a, rho_b) <= sqrt(1 - |<a|b>|^2 / (d+1)^2): no perfect discrimination
        of non-orthogonal states, unlike D-CTC and P-CTC."""
        for _ in range(20):
            U = random_unitary(4)
            a, b = random_pure(2), random_pure(2)
            ra = t_ctc(U, np.outer(a, a.conj()), 2, 2)[0]
            rb = t_ctc(U, np.outer(b, b.conj()), 2, 2)[0]
            dist = 0.5 * np.sum(abs(np.linalg.eigvalsh(ra - rb)))
            self.assertLessEqual(dist, np.sqrt(1 - abs(np.vdot(a, b)) ** 2 / 9) + ATOL)

    def test_bb84_not_perfectly_distinguished(self):
        """Brun-Harrington-Wilde's BB84 circuit: D-CTC is perfect, T-CTC is not."""
        c = bhw_bb84(np.diag([1, 0]).astype(complex))
        self.assertAlmostEqual(d_ctc(c.U, c.rho, c.d_cr, c.d_loop)[0][0, 0].real, 1.0, places=9)
        self.assertAlmostEqual(t_ctc(c.U, c.rho, c.d_cr, c.d_loop)[0][0, 0].real, 1 / 3, places=9)


class Family(unittest.TestCase):
    def test_limits(self):
        for c in (grandfather(0.05), interference(0.5, 1.2), lloyd_unproved_theorem()):
            self.assertTrue(np.allclose(t_ctc(c.U, c.rho, c.d_cr, c.d_loop, 0.0)[0],
                                        p_ctc(c.U, c.rho, c.d_cr, c.d_loop)[0], atol=ATOL), c.name)
            self.assertTrue(np.allclose(t_ctc(c.U, c.rho, c.d_cr, c.d_loop, np.inf)[0],
                                        maximally_mixed_loop(c.U, c.rho, c.d_cr, c.d_loop), atol=ATOL), c.name)

    def test_grandfather_closed_form(self):
        """P(jam) = eps (2 + t) / (t + 2 eps). T-CTC (t = 1): 3 eps / (1 + 2 eps)."""
        for eps in (0.0, 0.05, 0.4):
            c = grandfather(eps)
            for t in (0.25, 1.0, 4.0):
                out = t_ctc(c.U, c.rho, c.d_cr, c.d_loop, t)[0]
                self.assertAlmostEqual(c.probability_one(out, 'jam'), eps * (2 + t) / (t + 2 * eps), places=10)

    def test_no_paradox_for_any_positive_t(self):
        """The perfect gun (eps = 0) has no P-CTC history, but T-CTC is defined: the gun works."""
        c = grandfather(0.0)
        self.assertIsNone(p_ctc(c.U, c.rho, c.d_cr, c.d_loop)[0])
        self.assertAlmostEqual(c.probability_one(t_ctc(c.U, c.rho, c.d_cr, c.d_loop)[0], 'jam'), 0.0, places=12)


class Signalling(unittest.TestCase):
    def test_alice_to_bob(self):
        eps = 0.05
        expected = {'grandfather': 3 * eps / (1 + 2 * eps) - eps, 'kfk_unconditional': 0.0, 'interference': 0.25}
        cases = [(grandfather(eps), 'jam'), (kfk(0.3, 0.6, 'unconditional'), 'bad'), (interference(0.5, np.pi), 'a')]
        for c, label in cases:
            for mode in ('classical', 'entangled'):
                got = alice_to_bob(attach_partner(c, label, mode), 't_ctc')
                self.assertAlmostEqual(got, expected[c.name], places=9, msg=(c.name, mode))
        self.assertGreater(alice_to_bob(attach_partner(kfk(0.3, 0.6, 'motivated'), 'bad', 'classical'), 't_ctc'), 1e-3)

    def test_bob_state_formula(self):
        """Bob maximally entangled with all of Alice's CR system: his T-CTC state is
        proportional to (C^dag C)^T + t d 1. So, as for P-CTC, no signalling for all
        shared states iff C^dag C ~ 1 (for every finite t)."""
        for c in (grandfather(0.05), interference(0.5, 1.2)):
            cb = attach_partner(Circuit(c.name, c.cr_labels, c.loop_labels, c.U, np.eye(2) / 2, c.baseline_loop),
                                c.cr_labels[0], 'entangled')
            C = partial_trace_operator_loop(c.U, c.d_cr, c.d_loop)
            for t in (0.5, 1.0, 3.0):
                M = (C.conj().T @ C).T + t * c.d_loop * np.eye(2)
                got = bob_state(output(cb, 't_ctc', t=t), len(cb.cr_labels))
                self.assertTrue(np.allclose(got, M / np.trace(M), atol=ATOL), (c.name, t))

    def test_bob_to_alice_per_branch_signals(self):
        """Grandfather, Alice's jam bit entangled with Bob. Applied to the global state,
        T-CTC hides Bob's basis. Applied per branch, Z gives P(jam) = eps, X gives 3eps/(1+2eps)."""
        eps = 0.05
        cb = attach_partner(grandfather(eps), 'jam', 'entangled')
        z = bob_to_alice(cb, 't_ctc', 'Z', 'global')[1, 1].real
        x = bob_to_alice(cb, 't_ctc', 'X', 'global')[1, 1].real
        self.assertAlmostEqual(z, x, places=10)
        self.assertAlmostEqual(bob_to_alice(cb, 't_ctc', 'Z', 'per_branch')[1, 1].real, eps, places=10)
        self.assertAlmostEqual(bob_to_alice(cb, 't_ctc', 'X', 'per_branch')[1, 1].real, 3 * eps / (1 + 2 * eps),
                               places=10)


if __name__ == '__main__':
    unittest.main(verbosity=2)
