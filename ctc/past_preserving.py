"""SPDX-License-Identifier: MIT. Past-preserving selection: a candidate rule for H2.

Idea (ctc/PAST_PRESERVING.md): facts that are already recorded before the loop keep
their probabilities. Consistency selection only acts inside each recorded past world.

Given a record basis {|k>} of Alice's CR input (all of it, not only some qubits):
  - if C|k> != 0 (C = Tr_loop U), the world k goes to C|k> / ||C|k>||   (P-CTC inside k)
  - if C|k> == 0 (no consistent history in world k), fall back to D-CTC for |k><k|.
The weight of world k stays <k|rho|k>. As a map this is
    rho -> sum_k K_k rho K_k^dag,   K_k = C|k><k| / ||C|k>||   (plus fallback Kraus terms),
and sum_k K_k^dag K_k = 1. So it is linear and trace preserving: it cannot signal in
either direction, for any state Alice shares with anyone.

The price: the rule needs a record basis. For a pure, uncorrelated input the natural
choice is a basis that contains the input state (then the rule is P-CTC). For a mixed
input with a degenerate spectrum the choice is not fixed by the state, and different
choices give different outputs (the preparation problem of nonlinear extensions).

Derived in this project; novelty not checked.
"""
import numpy as np

from models import d_ctc, partial_trace_operator_loop

TOL = 1e-9


def past_preserving_kraus(U, d_cr, d_loop, basis=None):
    """Kraus operators of the rule. `basis` is a d_cr x d_cr unitary whose columns are
    the record basis (default: computational basis)."""
    basis = np.eye(d_cr, dtype=complex) if basis is None else np.asarray(basis, complex)
    C = partial_trace_operator_loop(U, d_cr, d_loop)
    kraus = []
    for k in range(d_cr):
        v = basis[:, k]
        w = C @ v
        norm = np.linalg.norm(w)
        if norm > TOL:
            kraus.append(np.outer(w / norm, v.conj()))
            continue
        sigma = d_ctc(U, np.outer(v, v.conj()), d_cr, d_loop)[0]
        lam, vecs = np.linalg.eigh((sigma + sigma.conj().T) / 2)
        for value, s in zip(lam, vecs.T):
            if value > 1e-12:
                kraus.append(np.sqrt(value) * np.outer(s, v.conj()))
    return kraus


def apply_kraus(kraus, rho, d_partner=1):
    """Apply Alice's Kraus operators to rho over (Alice x partner); partner untouched."""
    eye = np.eye(d_partner)
    out = 0
    for K in kraus:
        KK = np.kron(K, eye)
        out = out + KK @ rho @ KK.conj().T
    return out


def past_preserving(U, rho, d_cr, d_loop, basis=None):
    return apply_kraus(past_preserving_kraus(U, d_cr, d_loop, basis), rho)


def basis_containing(psi):
    """An orthonormal basis whose first vector is psi (record basis of a pure input)."""
    psi = np.asarray(psi, complex) / np.linalg.norm(psi)
    d = len(psi)
    M = np.column_stack([psi] + [np.eye(d)[:, j] for j in range(d)])
    Q, _ = np.linalg.qr(M)
    Q = Q[:, :d]
    return Q * (np.vdot(Q[:, 0], psi) / abs(np.vdot(Q[:, 0], psi)))  # fix the global phase of column 0


def x_basis(n_qubits=1):
    h = np.array([[1, 1], [1, -1]], complex) / np.sqrt(2)
    out = np.ones((1, 1), complex)
    for _ in range(n_qubits):
        out = np.kron(out, h)
    return out
