"""SPDX-License-Identifier: MIT. Past-preserving selection vs. Hartle 1994 (gr-qc/9309012).

Checks the comparison table in ctc/NOVELTY_CHECK.md (third round). In Hartle's measurement model
(Sec. V, Eqs. 5.5-5.6) the initial alternatives alpha are decohered by a persistent record and the
non-unitary evolution X acts on the system only. Then
    p(beta, alpha) = |<beta|X|alpha>|^2 <alpha|rho|alpha> / Tr(X rho X^dag)       (5.5)
    p(beta | alpha) = |<beta|X|alpha>|^2 / sum_beta' |<beta'|X|alpha>|^2           (5.6)
With X = C = Tr_loop U:
  - Hartle's conditional (5.6) equals past-preserving selection inside each world;
  - Hartle's world weights equal P-CTC applied to the dephased input (the past is reweighted);
  - past-preserving selection keeps the world weights <alpha|rho|alpha>.

Run from the repository root:  python -B ctc/tests/test_hartle.py
"""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import p_ctc, partial_trace_operator_loop  # noqa: E402
from past_preserving import past_preserving_kraus  # noqa: E402

ATOL = 1e-9
RNG = np.random.default_rng(1994)


def random_unitary(d):
    z = (RNG.normal(size=(d, d)) + 1j * RNG.normal(size=(d, d))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / abs(np.diag(r)))


def hartle_joint(X, weights):
    """Eq. (5.5) for a record-decohered input with world weights `weights`: p[alpha, beta]."""
    amp2 = abs(X.T) ** 2                       # amp2[alpha, beta] = |<beta|X|alpha>|^2
    joint = amp2 * weights[:, None]
    return joint / joint.sum()                 # sum = Tr(X rho X^dag) for the dephased rho


def pp_joint(U, d_cr, d_loop, weights):
    """Past-preserving selection, computational record basis: p[alpha, beta]."""
    out = np.zeros((d_cr, d_cr))
    for k, K in enumerate(past_preserving_kraus(U, d_cr, d_loop)):
        out[k] = weights[k] * abs(K[:, k]) ** 2   # generic U: one Kraus operator per world
    return out


class HartleComparison(unittest.TestCase):
    def test_conditionals_agree_and_weights_differ(self):
        for d_cr, d_loop in [(2, 2), (3, 2), (4, 3)]:
            for _ in range(5):
                U = random_unitary(d_cr * d_loop)
                C = partial_trace_operator_loop(U, d_cr, d_loop)
                w = RNG.dirichlet(np.ones(d_cr))
                h = hartle_joint(C, w)
                pp = pp_joint(U, d_cr, d_loop, w)
                # (5.6): conditionals inside each recorded world are identical
                np.testing.assert_allclose(h / h.sum(1, keepdims=True),
                                           pp / pp.sum(1, keepdims=True), atol=ATOL)
                # past-preserving keeps the recorded past
                np.testing.assert_allclose(pp.sum(1), w, atol=ATOL)
                # Hartle's world weights = P-CTC on the dephased input
                out, _ = p_ctc(U, np.diag(w).astype(complex), d_cr, d_loop)
                norms = np.linalg.norm(C, axis=0) ** 2          # ||C|alpha>||^2
                np.testing.assert_allclose(h.sum(1), w * norms / (w * norms).sum(), atol=ATOL)
                # and the future marginal of Hartle's rule is the P-CTC output on the dephased input
                np.testing.assert_allclose(h.sum(0), np.diag(out).real, atol=ATOL)
                # generic U: Hartle reweights the past, past-preserving does not
                self.assertGreater(np.max(abs(h.sum(1) - w)), 1e-4)


if __name__ == '__main__':
    unittest.main(verbosity=2)
