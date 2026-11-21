"""SPDX-License-Identifier: MIT. Classical 'weighted branches' CTC model with two knobs.

A history (branch) is a pair (x, m): x is the chronology-respecting (CR) input,
drawn from the prior P0(x), and m is the message received from the loop. The
deterministic dynamics sends back f(x, m) and leaves the CR output y(x, m).

Knob kappa (where messages come from). A message sent from branch (x, m) lands in a
branch whose CR input is the same x with probability kappa, or a fresh x' ~ P0 with
probability 1 - kappa. The long-run (Cesaro) distribution of this hop chain, started
from P0(x) * uniform(m), is the prior weight w0(x, m) of each branch.
    kappa = 0: messages come from a typical branch; w0 = P0(x) pi(m) (Deutsch-like).
    kappa = 1: each world only receives its own messages.
The hop chain never changes the x-marginal: it stays P0 for every kappa.

Knob beta (how strongly the universe prefers self-consistent branches).
    w(x, m) proportional to w0(x, m) * exp(-beta * d(f(x, m), m)),
with d the Hamming distance between sent and received message.
    beta = 0: no selection.  beta = inf: inconsistent branches get zero weight.

Corners on the circuits in circuits.py (checked in tests/test_branches.py):
    (kappa, beta) = (0, 0)   equals D-CTC (models.d_ctc)
    (kappa, beta) = (1, inf) equals P-CTC (models.p_ctc)
In general the (1, inf) corner weights each consistent message by its per-world
basin rather than equally, so it equals P-CTC only when those weights agree.
Classical (diagonal, permutation) circuits only. A model built for this project,
not taken from the literature.
"""
import numpy as np

from models import TOL


def classical_tables(circuit):
    """Read P0(x), f(x, m) and y(x, m) off a permutation circuit with a diagonal CR input."""
    U, rho = circuit.U, circuit.rho
    # U must be a 0/1 permutation matrix: a phase such as -1 would be silently read as
    # a classical move although it changes the quantum P-CTC result (see interference()).
    if not np.allclose(U, np.round(abs(U))) or not np.allclose(rho, np.diag(np.diag(rho))):
        raise ValueError('classical model needs a 0/1 permutation U (no phases) and a diagonal CR input')
    d_cr, d_loop = circuit.d_cr, circuit.d_loop
    target = np.argmax(abs(U), axis=0)
    f = np.zeros((d_cr, d_loop), int)
    y = np.zeros((d_cr, d_loop), int)
    for x in range(d_cr):
        for m in range(d_loop):
            j = target[x * d_loop + m]
            y[x, m], f[x, m] = divmod(j, d_loop)
    return np.diag(rho).real.copy(), f, y


def cesaro_limit(T, seed):
    """Cesaro limit of T^n seed for a column-stochastic matrix T (eigenvalue 1 is
    semisimple for stochastic matrices, so the limit is P seed with the spectral
    projector P = K (L^T K)^-1 L^T)."""
    identity = np.eye(T.shape[0])

    def null(A):
        _, s, vh = np.linalg.svd(A)
        rank = int(np.sum(s > 1e-9 * max(1.0, s[0])))
        return vh[rank:].conj().T

    K, L = null(T - identity), null(T.T - identity)
    limit = K @ np.linalg.solve(L.T @ K, L.T @ seed)
    limit = np.clip(limit.real, 0, None)
    return limit / limit.sum()


def hop_weights(P0, f, kappa):
    """Prior branch weights w0(x, m) from the hop chain described in the module docstring."""
    d_cr, d_loop = f.shape
    n = d_cr * d_loop
    T = np.zeros((n, n))
    for x in range(d_cr):
        for m in range(d_loop):
            src = x * d_loop + m
            m_next = f[x, m]
            T[x * d_loop + m_next, src] += kappa
            for x_new in range(d_cr):
                T[x_new * d_loop + m_next, src] += (1 - kappa) * P0[x_new]
    seed = np.outer(P0, np.full(d_loop, 1 / d_loop)).reshape(-1)
    return cesaro_limit(T, seed).reshape(d_cr, d_loop)


def hamming(a, b):
    return bin(int(a) ^ int(b)).count('1')


def branch_weights(circuit, kappa, beta):
    """Normalised branch weights w(x, m), or None if every branch has zero weight."""
    P0, f, _ = classical_tables(circuit)
    w0 = hop_weights(P0, f, kappa)
    d = np.vectorize(hamming)(f, np.arange(f.shape[1])[None, :])
    keep = (d == 0).astype(float) if np.isinf(beta) else np.exp(-beta * d)
    w = w0 * keep
    total = w.sum()
    if total < TOL:
        return None
    return w / total


def output_state(circuit, kappa, beta):
    """Diagonal CR output state implied by the branch weights (None for a true paradox)."""
    w = branch_weights(circuit, kappa, beta)
    if w is None:
        return None
    _, _, y = classical_tables(circuit)
    probabilities = np.zeros(circuit.d_cr)
    np.add.at(probabilities, y.reshape(-1), w.reshape(-1))
    return np.diag(probabilities).astype(complex)


def input_marginal(circuit, kappa, beta):
    """Distribution of the CR input x across branches; equals P0 when nothing is reweighted."""
    w = branch_weights(circuit, kappa, beta)
    return None if w is None else w.sum(axis=1)
