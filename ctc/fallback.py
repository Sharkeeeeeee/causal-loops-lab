"""SPDX-License-Identifier: MIT. Worlds with no consistent history: where the fallback comes from (THEOREMS.md, Theorem 8).

PPS acts inside each recorded world k by C|k> / ||C|k>||, C = Tr_L U. When C|k> = 0 that is undefined,
and the project first used the Deutsch (D-CTC) fixed point there, without a reason. This module
derives a fallback instead:

  regularize   give the loop a little noise, eps, so that C|k> = 0 no longer kills the world. P-CTC with
               a noisy loop (Kraus E_j) outputs sum_j Tr_L(E_j) rho Tr_L(E_j)^dag, normalized.
  limit        as eps -> 0 the output of a world with C|k> != 0 tends to PPS; the output of a world with
               C|k> = 0 tends to whatever the noise alone lets through.
  uniqueness   if the noise has no preferred loop basis (it commutes with every loop unitary, the
               relabelling invariance (U4) of Theorem 6), it is depolarizing, and the limit is the
               open loop: Tr_L[U(|k><k| x 1/n)U^dag], the loop cut and fed a random message.

Other noise gives other limits (a dephasing loop is checked in the tests), so the derivation needs the
noise to be basis-free. The D-CTC fixed point is not a limit of this kind.

Also here: the two pieces used for the computational-power statements of Theorem 8 (a paradox world
that runs Deutsch's fixed-point search, and the single postselection that simulates the open fallback).
"""
import numpy as np

from models import d_ctc, no_loop, partial_trace_operator_loop


def weyl(n):
    """The n^2 Weyl operators X^a Z^b on C^n. (1/n^2) sum P X P^dag = Tr(X) 1/n: full depolarization."""
    X = np.roll(np.eye(n), 1, axis=0).astype(complex)
    Z = np.diag(np.exp(2j * np.pi * np.arange(n) / n))
    return [np.linalg.matrix_power(X, a) @ np.linalg.matrix_power(Z, b) for a in range(n) for b in range(n)]


def noisy_loop_kraus(U, d_cr, d_loop, eps, noise='depolarize'):
    """Kraus operators of 'U, then noise on the loop': sqrt(1 - eps) U plus the noise terms.
    noise='depolarize': sqrt(eps)/n (1 x P) U over the Weyl operators P (basis-free).
    noise='dephase':    sqrt(eps/n) (1 x Z^b) U, b = 0..n-1 (dephasing in the computational basis)."""
    n = d_loop
    out = [np.sqrt(1 - eps) * U]
    if noise == 'depolarize':
        ops = [P / n for P in weyl(n)]
    elif noise == 'dephase':
        Z = np.diag(np.exp(2j * np.pi * np.arange(n) / n))
        ops = [np.linalg.matrix_power(Z, b) / np.sqrt(n) for b in range(n)]
    else:
        raise ValueError(noise)
    out += [np.sqrt(eps) * np.kron(np.eye(d_cr), P) @ U for P in ops]
    return out


def p_ctc_channel(kraus, rho, d_cr, d_loop):
    """P-CTC with a noisy loop: sum_j C_j rho C_j^dag / trace, C_j = Tr_L(E_j). Returns (state, weight)."""
    out = 0
    for E in kraus:
        Cj = partial_trace_operator_loop(E, d_cr, d_loop)
        out = out + Cj @ rho @ Cj.conj().T
    weight = float(np.trace(out).real)
    return out / weight, weight


def regularized_world(U, d_cr, d_loop, v, eps, noise='depolarize'):
    """Output of world |v> under PPS with a noisy loop (P-CTC inside the world, with the noisy loop)."""
    return p_ctc_channel(noisy_loop_kraus(U, d_cr, d_loop, eps, noise), np.outer(v, v.conj()), d_cr, d_loop)[0]


def open_loop_world(U, d_cr, d_loop, v):
    return no_loop(U, np.outer(v, v.conj()), d_cr, d_loop, np.eye(d_loop, dtype=complex) / d_loop)


def dctc_world(U, d_cr, d_loop, v):
    return d_ctc(U, np.outer(v, v.conj()), d_cr, d_loop)[0]


def _permutation(dim, mapping):
    P = np.zeros((dim, dim), complex)
    for i, j in mapping.items():
        P[j, i] = 1
    return P


def fixed_point_search(m, target, grandfather=True):
    """A loop that runs Deutsch's fixed-point search, inside a world with no consistent history.

    CR = (flag c, output o), loop = (string s, grandfather bit g); dims d_cr = 2m, d_loop = 2m.
    One round: o <- o + s (the CR reads the incoming string), then the loop moves s by the chain
    'stay if s is the target, else step to s + 1', made reversible with the flag c. Its unique stationary
    state is s = target, so a D-CTC loop outputs the target in o. The bit g is flipped every round
    (a grandfather paradox), so C = Tr_L U = 0 for every input: every world is a paradox world, and
    PPS uses its fallback. With the D-CTC fallback the output reads the target; with the open loop it
    reads a uniformly random string.
    """
    # step on (c, s) with c = 0 in: (0, target) -> (0, target); (0, s) -> (1, s + 1) otherwise
    idx = {}
    for c in range(2):
        for s in range(m):
            idx[(c, s)] = c * m + s
    mapping, used = {}, set()
    for s in range(m):
        out = (0, target) if s == target else (1, (s + 1) % m)
        mapping[idx[(0, s)]] = idx[out]
        used.add(idx[out])
    free = [i for i in range(2 * m) if i not in used]
    for s, f in zip(range(m), free):
        mapping[idx[(1, s)]] = f
    step = _permutation(2 * m, mapping)                       # on (c, s)
    # full register order: c, o, s, g  (CR = c, o; loop = s, g)
    d = 2 * m * m * 2
    U_read = np.zeros((d, d), complex)
    U_step = np.zeros((d, d), complex)
    for c in range(2):
        for o in range(m):
            for s in range(m):
                for g in range(2):
                    i = ((c * m + o) * m + s) * 2 + g
                    j_read = ((c * m + (o + s) % m) * m + s) * 2 + g
                    U_read[j_read, i] = 1
                    k = int(np.argmax(step[:, c * m + s]))
                    c2, s2 = divmod(k, m)
                    g2 = 1 - g if grandfather else g
                    U_step[((c2 * m + o) * m + s2) * 2 + g2, i] = 1
    return U_step @ U_read


def output_register(rho_cr, m):
    """Distribution of the output register o from a CR state over (c, o)."""
    p = np.real(np.diag(rho_cr)).reshape(2, m)
    return p.sum(axis=0)


def single_postselection(U, d_cr, d_loop, v, eps):
    """The simulation used for the upper bound PPS (open fallback) <= PostBQP = PP: one P-CTC run with a
    depolarized loop. In a world with C|v> != 0 its error is at most eps / ((1 - eps) ||C v||^2)."""
    return regularized_world(U, d_cr, d_loop, v, eps)
