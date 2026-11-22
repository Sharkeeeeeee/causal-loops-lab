"""SPDX-License-Identifier: MIT. Toy closed-timelike-curve (CTC) rules.

Three rules for a unitary U acting on (CR system) x (loop system):
  no_loop : ordinary quantum mechanics, the loop input is an external state.
  p_ctc   : postselected CTC (Lloyd et al. 2011). Output ~ C rho C^dag, C = Tr_loop[U].
  d_ctc   : Deutsch CTC (1991). The loop state tau must satisfy
            tau = Tr_CR[U (rho x tau) U^dag].
  t_ctc   : transition-probability CTC (Allen 2014). A weighted mixture of the P-CTC
            term and the maximally mixed loop channel.

Ordering convention: CR subsystems first, loop subsystems last.
These are mathematical models. Running them does not send anything anywhere in time.
"""
import numpy as np

TOL = 1e-12


def kron_all(items):
    out = np.ones((1, 1), complex)
    for item in items:
        out = np.kron(out, item)
    return out


def partial_trace_operator_loop(U, d_cr, d_loop):
    """C = Tr_loop[U]: partial trace of the operator itself (not of a state)."""
    return np.einsum('aibi->ab', U.reshape(d_cr, d_loop, d_cr, d_loop))


def partial_trace_state(rho, d_cr, d_loop, keep):
    t = rho.reshape(d_cr, d_loop, d_cr, d_loop)
    if keep == 'cr':
        return np.einsum('aibi->ab', t)
    if keep == 'loop':
        return np.einsum('aiaj->ij', t)
    raise ValueError(keep)


def check_unitary(U):
    return float(np.max(abs(U.conj().T @ U - np.eye(U.shape[0]))))


def no_loop(U, rho, d_cr, d_loop, loop_input):
    """Ordinary evolution with an externally supplied loop input state."""
    joint = U @ np.kron(rho, loop_input) @ U.conj().T
    return partial_trace_state(joint, d_cr, d_loop, 'cr')


def p_ctc(U, rho, d_cr, d_loop):
    """Return (output state, consistency weight). Output is None when the weight is
    zero, meaning no self-consistent history exists (a genuine paradox)."""
    C = partial_trace_operator_loop(U, d_cr, d_loop)
    unnormalized = C @ rho @ C.conj().T
    weight = float(np.trace(unnormalized).real)
    if weight < TOL:
        return None, weight
    return unnormalized / weight, weight


def maximally_mixed_loop(U, rho, d_cr, d_loop):
    """Ordinary evolution with the loop input replaced by the maximally mixed state."""
    return no_loop(U, rho, d_cr, d_loop, np.eye(d_loop, dtype=complex) / d_loop)


def t_ctc(U, rho, d_cr, d_loop, t=1.0):
    """Transition-probability CTC (Allen 2014, Phys. Rev. A 90, 042107, Eq. 33):

        rho_f = z^-1 ( C rho C^dag + t d Tr_loop[U (rho x 1/d) U^dag] ),  C = Tr_loop[U].

    t = 1 is Allen's T-CTC (the Haar average over pure loop states, Eq. 24). t = 0 is
    P-CTC and t -> inf is the maximally mixed loop channel. Values t != 1 are this
    project's generalisation, not Allen's. Returns (output state, lam), where lam is
    the weight of the channel term (Allen Eq. 38 at t = 1). Output is None only if
    both terms vanish, which cannot happen for t > 0."""
    if np.isinf(t):
        return maximally_mixed_loop(U, rho, d_cr, d_loop), 1.0
    C = partial_trace_operator_loop(U, d_cr, d_loop)
    selected = C @ rho @ C.conj().T
    channel = t * d_loop * maximally_mixed_loop(U, rho, d_cr, d_loop)
    total = selected + channel
    z = float(np.trace(total).real)
    if z < TOL:
        return None, float('nan')
    return total / z, float(np.trace(channel).real) / z


def p_ctc_success_probability(U, rho, d_cr, d_loop):
    """Probability that the postselection succeeds when the P-CTC is realised as
    teleportation through a maximally entangled pair: Tr[C rho C^dag] / d_loop^2."""
    C = partial_trace_operator_loop(U, d_cr, d_loop)
    return float(np.trace(C @ rho @ C.conj().T).real) / d_loop ** 2


def p_ctc_by_teleportation(U, rho, d_cr, d_loop):
    """Independent check of p_ctc: simulate the postselected-teleportation circuit
    explicitly. Systems CR x E x E'; E,E' start in |Phi> = sum_i |ii>/sqrt(d); U acts
    on CR x E; then E,E' are projected back onto |Phi>. Returns (normalised CR state
    or None, success probability)."""
    phi = np.eye(d_loop, dtype=complex).reshape(-1) / np.sqrt(d_loop)
    projector_phi = np.outer(phi, phi.conj())
    state = np.kron(rho, projector_phi)
    big_U = np.kron(U, np.eye(d_loop))
    P = np.kron(np.eye(d_cr), projector_phi)
    out = P @ big_U @ state @ big_U.conj().T @ P
    cr = np.einsum('aibi->ab', out.reshape(d_cr, d_loop * d_loop, d_cr, d_loop * d_loop))
    success = float(np.trace(cr).real)
    if success < TOL:
        return None, success
    return cr / success, success


def loop_map_matrix(U, rho, d_cr, d_loop):
    """Matrix of the linear map tau -> Tr_CR[U (rho x tau) U^dag] on row-major vec(tau)."""
    M = np.zeros((d_loop * d_loop, d_loop * d_loop), complex)
    for k in range(d_loop * d_loop):
        basis = np.zeros(d_loop * d_loop, complex)
        basis[k] = 1
        tau = basis.reshape(d_loop, d_loop)
        joint = U @ np.kron(rho, tau) @ U.conj().T
        M[:, k] = partial_trace_state(joint, d_cr, d_loop, 'loop').reshape(-1)
    return M


def _null_space(A, tol=1e-9):
    _, s, vh = np.linalg.svd(A)
    rank = int(np.sum(s > tol * max(1.0, s[0] if len(s) else 0)))
    return vh[rank:].conj().T


def d_ctc_fixed_point(U, rho, d_cr, d_loop):
    """Deutsch fixed point selected as the Cesaro limit of the map applied to the
    maximally mixed seed. For a CPTP map the eigenvalue 1 is semisimple, so this
    limit equals P(seed), with P = K (L^dag K)^-1 L^dag built from the right (K) and
    left (L) fixed spaces. In the circuits of this package it is also the
    maximum-entropy fixed point; that is not claimed in general."""
    M = loop_map_matrix(U, rho, d_cr, d_loop)
    identity = np.eye(M.shape[0])
    K = _null_space(M - identity)
    L = _null_space(M.conj().T - identity)
    P = K @ np.linalg.solve(L.conj().T @ K, L.conj().T)
    seed = (np.eye(d_loop, dtype=complex) / d_loop).reshape(-1)
    tau = (P @ seed).reshape(d_loop, d_loop)
    tau = (tau + tau.conj().T) / 2
    return tau / np.trace(tau).real, K.shape[1]


def d_ctc(U, rho, d_cr, d_loop):
    """Return (CR output, loop fixed point, dimension of the fixed-point space)."""
    tau, multiplicity = d_ctc_fixed_point(U, rho, d_cr, d_loop)
    joint = U @ np.kron(rho, tau) @ U.conj().T
    return partial_trace_state(joint, d_cr, d_loop, 'cr'), tau, multiplicity
