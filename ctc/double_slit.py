"""SPDX-License-Identifier: MIT. A double-slit experiment with a time loop, as a qubit model.

Path qubit a: |0> = left slit, |1> = right slit. A screen position is modelled by the
phase theta it adds between the two paths, so the screen measures a in the basis
|+_theta> = (|0> + e^{i theta}|1>)/sqrt(2) and the pattern is P(+_theta).

The loop: a one-bit message from the future controls a phase phi on the right path
(applied only when message = 1). Without a time machine there is no message (|0>),
so nothing happens. Same unitary as circuits.interference, but with that baseline.

Two versions:
  fresh     : the photon's path is a pure superposition, correlated with nothing.
  entangled : an idler qubit (held by Bob) records the path, sqrt(1-p)|00> + sqrt(p)|11>.
              Bob may later measure the idler in Z (which path) or X (erase), which is
              the delayed-choice quantum eraser.
"""
import numpy as np

from circuits import Circuit, bit_state
from models import d_ctc, no_loop, p_ctc, t_ctc
from past_preserving import apply_kraus, basis_containing, past_preserving_kraus, x_basis

THETAS = np.linspace(0, 2 * np.pi, 181)


def ctc_double_slit(p1=0.5, phi=np.pi):
    U = np.diag([1, 1, 1, np.exp(1j * phi)]).astype(complex)
    a = np.array([np.sqrt(1 - p1), np.sqrt(p1)], complex)
    return Circuit('ctc_double_slit', ['a'], ['message'], U, np.outer(a, a.conj()), bit_state(0.0),
                   dict(p1=p1, phi=phi))


def entangled_input(p1=0.5):
    v = np.array([np.sqrt(1 - p1), 0, 0, np.sqrt(p1)], complex)
    return np.outer(v, v.conj())


def pattern(rho_a, thetas=THETAS):
    """P(+_theta) for a one-qubit (unnormalized allowed) path state."""
    tr = np.trace(rho_a).real
    return np.array([(rho_a[0, 0] + rho_a[1, 1] + rho_a[0, 1] * np.exp(1j * t) + rho_a[1, 0] * np.exp(-1j * t)).real
                     / (2 * tr) for t in thetas])


def visibility(rho_a):
    return float(2 * abs(rho_a[0, 1]) / np.trace(rho_a).real)


def fringe_shift(rho_a):
    """Screen phase of the bright fringe (radians, in (-pi, pi]); None without fringes."""
    return None if abs(rho_a[0, 1]) < 1e-12 else float(-np.angle(rho_a[0, 1]))


def trace_out_last(rho, d_keep, d_drop):
    return np.einsum('aibi->ab', rho.reshape(d_keep, d_drop, d_keep, d_drop))


def trace_out_first(rho, d_drop, d_keep):
    return np.einsum('iaib->ab', rho.reshape(d_drop, d_keep, d_drop, d_keep))


def extend(U, d_cr, d_loop, d_partner):
    """U on (Alice CR x loop) -> U on (Alice CR x partner x loop), partner untouched."""
    U4 = U.reshape(d_cr, d_loop, d_cr, d_loop)
    return np.einsum('xlym,bc->xblycm', U4, np.eye(d_partner)).reshape(d_cr * d_partner * d_loop,
                                                                        d_cr * d_partner * d_loop)


RULES = ('no_loop', 'd_ctc', 't_ctc', 'p_ctc', 'past_Z', 'past_X')


def run_fresh(circuit, rule):
    """Output path state for the fresh photon. For a pure input the natural record basis
    contains the input state; 'past_Z' / 'past_X' instead treat the path as already
    recorded in the which-path / X basis."""
    c = circuit
    if rule == 'no_loop':
        return no_loop(c.U, c.rho, 2, 2, c.baseline_loop)
    if rule == 'd_ctc':
        return d_ctc(c.U, c.rho, 2, 2)[0]
    if rule == 't_ctc':
        return t_ctc(c.U, c.rho, 2, 2)[0]
    if rule == 'p_ctc':
        return p_ctc(c.U, c.rho, 2, 2)[0]
    if rule == 'past_pure':
        psi = np.linalg.eigh(c.rho)[1][:, -1]
        return apply_kraus(past_preserving_kraus(c.U, 2, 2, basis_containing(psi)), c.rho)
    basis = {'past_Z': None, 'past_X': x_basis(1)}[rule]
    return apply_kraus(past_preserving_kraus(c.U, 2, 2, basis), c.rho)


def run_entangled(circuit, rule, p1=0.5):
    """Joint (path, idler) state after the loop. The idler is Bob's and is untouched."""
    c = circuit
    rho = entangled_input(p1)
    U = extend(c.U, 2, 2, 2)
    if rule == 'no_loop':
        return no_loop(U, rho, 4, 2, c.baseline_loop)
    if rule == 'd_ctc':
        return d_ctc(U, rho, 4, 2)[0]
    if rule == 't_ctc':
        return t_ctc(U, rho, 4, 2)[0]
    if rule == 'p_ctc':
        return p_ctc(U, rho, 4, 2)[0]
    basis = {'past_Z': None, 'past_X': x_basis(1)}[rule]
    return apply_kraus(past_preserving_kraus(c.U, 2, 2, basis), rho, d_partner=2)


def idler_conditional(rho_joint, outcome):
    """Path state (unnormalized) after Bob measures the idler: 'Z0','Z1','X+','X-'."""
    vec = {'Z0': [1, 0], 'Z1': [0, 1], 'X+': [1, 1], 'X-': [1, -1]}[outcome]
    v = np.array(vec, complex) / np.linalg.norm(vec)
    P = np.kron(np.eye(2), np.outer(v, v.conj()))
    return trace_out_last(P @ rho_joint @ P, 2, 2)


def summarize(phi, p1=0.5):
    c = ctc_double_slit(p1, phi)
    fresh = {}
    for rule in ('no_loop', 'd_ctc', 't_ctc', 'p_ctc', 'past_pure', 'past_Z', 'past_X'):
        out = run_fresh(c, rule)
        fresh[rule] = None if out is None else dict(P_right=float(out[1, 1].real), visibility=visibility(out),
                                                    fringe_shift=fringe_shift(out))
    prior_bob = trace_out_first(entangled_input(p1), 2, 2)
    ent = {}
    for rule in RULES:
        out = run_entangled(c, rule, p1)
        if out is None:
            ent[rule] = None
            continue
        bob = trace_out_first(out, 2, 2)
        ent[rule] = dict(
            marginal_visibility=visibility(trace_out_last(out, 2, 2)),
            eraser_visibility_given_plus=visibility(idler_conditional(out, 'X+')),
            eraser_shift_given_plus=fringe_shift(idler_conditional(out, 'X+')),
            bob_change=float(0.5 * np.sum(abs(np.linalg.eigvalsh(bob - prior_bob)))))
    return dict(fresh=fresh, entangled=ent)
