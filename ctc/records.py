"""SPDX-License-Identifier: MIT. The record basis from the interaction (pointer basis), for Theorem 4.

Past-preserving selection needs a record basis for Alice's input. Theorem 4 (THEOREMS.md) takes it
from the dynamics, not from the state: an interaction V on (source (x) target) "reads" the source in
the basis {|k>} if it has the controlled form

    V = sum_k |k><k| (x) V_k.

Then the target ends up holding a record of k (perfect when the states V_k|t0> are orthogonal).
This module finds that basis from V alone:

  1. operator Schmidt decomposition V = sum_i A_i (x) B_i;
  2. V has the controlled form in some basis iff the source-side operators A_i are normal and
     commute; the basis is their joint eigenbasis;
  3. if the A_i do not commute, V does not read the source in any single basis (for example a SWAP,
     or a generic entangling unitary), and the function returns None.

Partial records (V_k|t0> not orthogonal) still have a pointer basis; `record_quality` reports how
distinguishable the record states are.

Derived in this project; the pointer-basis idea is Zurek's einselection. Novelty not checked.
"""
import numpy as np

TOL = 1e-9


def operator_schmidt(V, d_s, d_t, tol=1e-10):
    """V = sum_i A_i (x) B_i with A_i on the source (d_s), B_i on the target (d_t)."""
    M = np.asarray(V, complex).reshape(d_s, d_t, d_s, d_t).transpose(0, 2, 1, 3).reshape(d_s * d_s, d_t * d_t)
    U, s, Wh = np.linalg.svd(M)
    keep = np.where(s > tol * max(s[0], 1e-300))[0]
    A = [(U[:, i] * np.sqrt(s[i])).reshape(d_s, d_s) for i in keep]
    B = [(Wh[i, :] * np.sqrt(s[i])).reshape(d_t, d_t) for i in keep]
    return A, B


def pointer_basis(V, d_s, d_t, seed=7):
    """Columns: the basis in which V reads the source. None if V reads it in no single basis, does
    not touch it, or reads it only coarsely (two basis states the target cannot tell apart)."""
    A, _ = operator_schmidt(V, d_s, d_t)
    if len(A) == 1:
        return None                                   # product unitary: the target learns nothing
    for a in A:
        if not np.allclose(a @ a.conj().T, a.conj().T @ a, atol=TOL):
            return None
        for b in A:
            if not np.allclose(a @ b, b @ a, atol=TOL):
                return None
    rng = np.random.default_rng(seed)
    herm = sum(rng.normal() * (a + a.conj().T) / 2 + rng.normal() * (a - a.conj().T) / 2j for a in A)
    _, vecs = np.linalg.eigh(herm)
    signatures = []
    for k in range(d_s):
        v = vecs[:, k]
        signatures.append(tuple(np.round([v.conj() @ a @ v for a in A], 7)))
        for a in A:
            if np.linalg.norm(a @ v - (v.conj() @ a @ v) * v) > 1e-7:
                return None
    if len(set(signatures)) < d_s:
        return None                                   # coarse readout: the basis is not fixed by V
    return vecs


def record_quality(V, d_s, d_t, target_init, basis=None):
    """1 - max_{k != l} |<V_k t0 | V_l t0>|: 1 for a perfect record, 0 for none."""
    basis = pointer_basis(V, d_s, d_t) if basis is None else basis
    if basis is None:
        return 0.0
    V4 = np.asarray(V, complex).reshape(d_s, d_t, d_s, d_t)
    states = []
    for k in range(d_s):
        b = basis[:, k]
        Vk = np.einsum('i,ixjy,j->xy', b.conj(), V4, b)   # <k| V |k> on the target
        states.append(Vk @ target_init)
    worst = max((abs(np.vdot(states[k], states[l])) for k in range(d_s) for l in range(d_s) if k != l), default=0.0)
    return float(1 - worst)


def reads(basis, d_t, rng):
    """A random interaction that reads a d_s-dimensional source in `basis` (for tests)."""
    d_s = basis.shape[0]
    V = np.zeros((d_s * d_t, d_s * d_t), complex)
    for k in range(d_s):
        z = rng.normal(size=(d_t, d_t)) + 1j * rng.normal(size=(d_t, d_t))
        q, r = np.linalg.qr(z)
        Vk = q * (np.diag(r) / abs(np.diag(r)))
        P = np.outer(basis[:, k], basis[:, k].conj())
        V += np.kron(P, Vk)
    return V


# ---------------------------------------------------------------- beyond one fine readout (THEOREMS.md 4a-4c)

def pointer_blocks(V, d_s, d_t, seed=7):
    """Projectors onto the blocks V reads (joint eigenspaces of the source-side operators). A fine
    readout gives rank-1 blocks, a coarse one larger blocks. None if V reads no basis or nothing."""
    A, _ = operator_schmidt(V, d_s, d_t)
    if len(A) == 1:
        return None
    for a in A:
        if not np.allclose(a @ a.conj().T, a.conj().T @ a, atol=TOL):
            return None
        for b in A:
            if not np.allclose(a @ b, b @ a, atol=TOL):
                return None
    rng = np.random.default_rng(seed)
    herm = sum(rng.normal() * (a + a.conj().T) / 2 + rng.normal() * (a - a.conj().T) / 2j for a in A)
    _, vecs = np.linalg.eigh(herm)
    groups = {}
    for k in range(d_s):
        v = vecs[:, k]
        sig = tuple(np.round([v.conj() @ a @ v for a in A], 6))
        groups.setdefault(sig, []).append(v)
    return [sum(np.outer(v, v.conj()) for v in vs) for vs in groups.values()]


def blocks_after(readouts):
    """Blocks of the source as the loop finds it, after readouts given in time order (each a list of
    projectors). The last readout fixes the blocks; an earlier readout refines them only if it
    commutes with them. An incompatible earlier readout was disturbed by the later one: its record
    stays protected (the rule never touches the outside), but it no longer describes the source."""
    blocks = [P for P in readouts[-1]]
    for earlier in reversed(readouts[:-1]):
        if all(np.allclose(P @ Q, Q @ P, atol=TOL) for P in blocks for Q in earlier):
            blocks = [P @ Q for P in blocks for Q in earlier if np.linalg.norm(P @ Q) > 1e-9]
    return blocks


def world_vectors(blocks, psi=None):
    """One world per block. Rank-1 block: its vector. Larger block: the source's own state projected
    into it, P psi / ||P psi||, which needs the pre-readout state psi (the loop finds the source in
    that state: nothing distinguished the alternatives inside the block)."""
    worlds = []
    for P in blocks:
        rank = int(round(np.trace(P).real))
        if rank == 1:
            w, v = np.linalg.eigh(P)
            worlds.append(v[:, -1])
        else:
            if psi is None:
                raise ValueError('a coarse block needs the pre-readout state')
            u = P @ psi
            if np.linalg.norm(u) > 1e-12:
                worlds.append(u / np.linalg.norm(u))
    return worlds


def world_kraus(U, d_cr, d_loop, worlds, fallback='open'):
    """PPS Kraus operators for orthonormal world vectors: P-CTC inside each world (open-loop fallback),
    and the identity on whatever the worlds do not span (unread, and empty under the premise)."""
    from models import partial_trace_operator_loop
    from past_preserving import fallback_kraus
    C = partial_trace_operator_loop(U, d_cr, d_loop)
    kraus, span = [], np.zeros((d_cr, d_cr), complex)
    for v in worlds:
        span += np.outer(v, v.conj())
        w = C @ v
        if np.linalg.norm(w) > TOL:
            kraus.append(np.outer(w / np.linalg.norm(w), v.conj()))
            continue
        kraus += fallback_kraus(U, d_cr, d_loop, v, fallback)
    rest = np.eye(d_cr) - span
    if np.linalg.norm(rest) > 1e-9:
        kraus.append(rest)
    return kraus


def eigenbasis_rule(rho_a, fallback):
    """The record basis read off the source's reduced state (its eigenbasis), with `fallback` used
    when the spectrum is degenerate. A candidate for weak records (THEOREMS.md 4c)."""
    lam, vecs = np.linalg.eigh((rho_a + rho_a.conj().T) / 2)
    if np.min(np.diff(lam)) < 1e-9:
        return fallback
    return vecs


def _bases_of_subspace(vectors, n_bases, rng):
    """n_bases orthonormal bases of the subspace spanned by the orthonormal `vectors`, spread evenly
    (Fibonacci points on the Bloch sphere for a 2-dimensional subspace, Haar-random otherwise).
    The average of their projectors is exactly the projector on the subspace."""
    m = len(vectors)
    S = np.column_stack(vectors)
    out = []
    for j in range(n_bases):
        if m == 2:
            z = 1 - (2 * j + 1) / n_bases
            phi = j * np.pi * (3 - np.sqrt(5))
            a, b = np.sqrt((1 + z) / 2), np.sqrt((1 - z) / 2) * np.exp(1j * phi)
            W = np.array([[a, -np.conj(b)], [b, np.conj(a)]])
        else:
            z = rng.normal(size=(m, m)) + 1j * rng.normal(size=(m, m))
            W, r = np.linalg.qr(z)
            W = W * (np.diag(r) / abs(np.diag(r)))
        out.append([S @ W[:, i] for i in range(m)])
    return out


def state_world_kraus(U, d_cr, d_loop, rho_a, n_bases=600, tol=1e-7, seed=11, fallback='open'):
    """The state-based world rule (THEOREMS.md, Theorem 7).

    The worlds are the eigenvectors of the input's reduced state rho_a, each with its weight; inside
    each world the loop acts by P-CTC (open-loop fallback, Theorem 8), as in Theorem 6. Where the spectrum is
    degenerate no basis is singled out by the state, so the rule averages over all bases of that
    eigenspace (each world of each basis with weight 1/n_bases). Zero eigenvalues carry no weight;
    the identity is used there so that the map stays trace preserving.
    """
    from models import partial_trace_operator_loop
    from past_preserving import fallback_kraus
    C = partial_trace_operator_loop(U, d_cr, d_loop)
    lam, vecs = np.linalg.eigh((rho_a + rho_a.conj().T) / 2)
    groups, i = [], 0
    while i < d_cr:
        j = i + 1
        while j < d_cr and abs(lam[j] - lam[i]) < tol:
            j += 1
        groups.append((lam[i], [vecs[:, k] for k in range(i, j)]))
        i = j
    rng = np.random.default_rng(seed)

    def world(v, weight):
        w = C @ v
        if np.linalg.norm(w) > TOL:
            return [np.sqrt(weight) * np.outer(w / np.linalg.norm(w), v.conj())]
        return fallback_kraus(U, d_cr, d_loop, v, fallback, weight)

    kraus = []
    for value, vs in groups:
        if value < tol:
            P = sum(np.outer(v, v.conj()) for v in vs)
            kraus.append(P)                      # carries no weight; keeps the map trace preserving
        elif len(vs) == 1:
            kraus += world(vs[0], 1.0)
        else:
            for basis in _bases_of_subspace(vs, n_bases, rng):
                for v in basis:
                    kraus += world(v, 1.0 / n_bases)
    return kraus
