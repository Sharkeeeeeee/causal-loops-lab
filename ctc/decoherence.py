"""SPDX-License-Identifier: MIT. Letting decoherence choose the record basis of past-preserving selection.

Systems, in this order: S (photon path), B (Bob's idler, optional), E (environment qubits).
Before the loop:
  1. Bob's idler copies the path in Z (CNOT S -> B), if present.
  2. Each environment qubit makes a partial record of S in a pointer basis (Z or X):
     |a>|0> -> |a>|E_a>, with overlap <E_0|E_1> = 1 - s. s = 0: no record, s = 1: perfect copy.
Then the loop (a message from the future adds a phase phi to the right path).

Decoherence-defined past-preserving rule (this project's proposal):
  - worlds are the outcomes e of reading the environment in its record basis; their
    probabilities stay fixed (records are the past);
  - inside world e, the record basis of S is the eigenbasis of S's conditional state
    rho_{S|e} (Bob traced out, since Bob's idler is his and he can still erase it);
  - inside world e, apply past-preserving selection (past_preserving.py) in that basis.
Everything the rule uses (the worlds and the bases) is a function of the state of S and
the environment only, which Bob cannot change; inside each world the rule is a channel
on S. So it cannot signal in either direction. When rho_{S|e} is degenerate the basis is
not determined: the rule reports this as ambiguous.
"""
import numpy as np

from double_slit import extend
from models import no_loop, p_ctc
from past_preserving import apply_kraus, past_preserving_kraus

H = np.array([[1, 1], [1, -1]], complex) / np.sqrt(2)


def loop_unitary(phi):
    return np.diag([1, 1, 1, np.exp(1j * phi)]).astype(complex)


def initial_state(p1=0.5, n_env=1, s=0.0, pointer='Z', bob=True):
    """Pure state vector over S, (B), E_1..E_n."""
    psi = np.array([np.sqrt(1 - p1), np.sqrt(p1)], complex)
    if bob:
        psi = np.array([psi[0], 0, 0, psi[1]], complex)      # S, B after CNOT S -> B
    d_b = 2 if bob else 1
    overlap = 1 - s
    e0 = np.array([1, 0], complex)
    e1 = np.array([overlap, np.sqrt(max(0.0, 1 - overlap ** 2))], complex)
    basis = np.eye(2, dtype=complex) if pointer == 'Z' else H     # columns: pointer states of S
    for _ in range(n_env):
        t = psi.reshape(2, -1)
        new = np.zeros((2, t.shape[1], 2), complex)
        for a, env in ((0, e0), (1, e1)):
            P = np.outer(basis[:, a], basis[:, a].conj())
            new += np.einsum('ij,jk,l->ikl', P, t, env)
        psi = new.reshape(-1)
    return psi, d_b, 2 ** n_env


def env_record_rule(U, rho, d_b, d_e, gap=1e-9):
    """Decoherence-defined past-preserving rule. rho over S x B x E. Returns
    (output rho over S x B x E with E's records kept, ambiguous flag)."""
    t = rho.reshape(2, d_b, d_e, 2, d_b, d_e)
    out = np.zeros_like(t)
    ambiguous = False
    for e in range(d_e):
        rho_e = t[:, :, e, :, :, e].reshape(2 * d_b, 2 * d_b)
        p_e = np.trace(rho_e).real
        if p_e < 1e-14:
            continue
        rho_s = np.einsum('aibi->ab', rho_e.reshape(2, d_b, 2, d_b)) / p_e
        lam, vecs = np.linalg.eigh((rho_s + rho_s.conj().T) / 2)
        if abs(lam[1] - lam[0]) < gap and abs(rho_s[0, 1]) < 0.5 - gap:   # degenerate, and not a pure state
            ambiguous = True
        basis = vecs[:, ::-1]
        new = apply_kraus(past_preserving_kraus(U, 2, 2, basis), rho_e, d_partner=d_b)
        out[:, :, e, :, :, e] = new.reshape(2, d_b, 2, d_b)
    return out.reshape(rho.shape), ambiguous


def run(rule, phi=np.pi / 2, **state):
    psi, d_b, d_e = initial_state(**state)
    rho = np.outer(psi, psi.conj())
    U = loop_unitary(phi)
    d_rest = d_b * d_e
    if rule == 'no_loop':
        return no_loop(extend(U, 2, 2, d_rest), rho, 2 * d_rest, 2, np.diag([1, 0]).astype(complex)), False, d_b, d_e
    if rule == 'p_ctc':
        return p_ctc(extend(U, 2, 2, d_rest), rho, 2 * d_rest, 2)[0], False, d_b, d_e
    if rule == 'env_record':
        out, amb = env_record_rule(U, rho, d_b, d_e)
        return out, amb, d_b, d_e
    raise ValueError(rule)


def marginal(rho, d_b, d_e, keep):
    t = rho.reshape(2, d_b, d_e, 2, d_b, d_e)
    spec = {'S': 'abcdbc->ad', 'B': 'abcaec->be', 'E': 'abcabf->cf', 'SB': 'abcdec->abde'}[keep]
    m = np.einsum(spec, t)
    return m.reshape(2 * d_b, 2 * d_b) if keep == 'SB' else m


def record_probabilities(rho, d_b, d_e):
    """Probabilities of the environment's records (its reading basis)."""
    return np.diag(marginal(rho, d_b, d_e, 'E')).real


def environment_coherence(rho, d_b, d_e):
    """Total off-diagonal weight of the environment in its reading basis. The rule removes
    it; only someone able to undo the decoherence could notice."""
    E = marginal(rho, d_b, d_e, 'E')
    return float(np.sum(abs(E - np.diag(np.diag(E)))))


def bob_premeasures(rho, d_b, d_e, basis):
    """Bob measures his idler in Z or X before the loop (outcome not used by the rule)."""
    vecs = np.eye(2, dtype=complex) if basis == 'Z' else H
    out = 0
    for v in vecs.T:
        P = np.kron(np.kron(np.eye(2), np.outer(v, v.conj())), np.eye(d_e))
        out = out + P @ rho @ P
    return out


def sorted_by_bob(rho, d_b, d_e, outcome='X+'):
    """Unnormalized S state for the hits where Bob later finds `outcome` on his idler."""
    v = {'X+': np.array([1, 1]), 'X-': np.array([1, -1]), 'Z0': np.array([1, 0]), 'Z1': np.array([0, 1])}[outcome]
    v = v.astype(complex) / np.linalg.norm(v)
    sb = marginal(rho, d_b, d_e, 'SB').reshape(2, 2, 2, 2)
    return np.einsum('aibj,i,j->ab', sb, v.conj(), v)


def visibility(rho_s):
    return float(2 * abs(rho_s[0, 1]) / np.trace(rho_s).real)


def fringe_shift(rho_s):
    return None if abs(rho_s[0, 1]) < 1e-12 else float(-np.angle(rho_s[0, 1]))
