"""SPDX-License-Identifier: MIT. A third world rule for weak records: mix the pointer and state rules (THEOREMS.md, Theorem 9).

Theorem 4 (pointer rule) and Theorem 7 (state rule) are both safe, and each has one jump: the pointer
rule at the first trace of a record, the state rule at degenerate spectra. Theorem 9 shows that a jump
is unavoidable for any rule that picks a single basis, and that it is avoidable once the rule may mix
two splits. The rule here does that:

    Phi = (1 - c) Phi_pointer + c Phi_state

where c is the record overlap |<r_j|r_k>| of the readout's record states (c = 0 perfect record, c = 1
none). 1 - c is the probability that an unambiguous measurement of the record would succeed
(Ivanovic-Dieks-Peres), so the reading is: a weak record is a fact exactly as often as it could be
read without error. Both parts are fixed channels on the input given the history (the readout and
rho_A), so the mixture never signals.

Defined for readouts whose record states have one common overlap (every two-outcome readout).
Readouts with unequal overlaps, and several readouts, are not covered.
"""
import numpy as np

from past_preserving import past_preserving_kraus
from records import state_world_kraus


def record_overlap(V, d_a, d_o, o_init=None):
    """Common overlap c = |<V_j o|V_k o>| of a readout V = sum_k |k><k| x V_k (pointer basis = computational).
    Raises if the overlaps differ."""
    o = np.eye(d_o, dtype=complex)[0] if o_init is None else np.asarray(o_init, complex)
    T = V.reshape(d_a, d_o, d_a, d_o)
    records = [T[k, :, k, :] @ o for k in range(d_a)]
    overlaps = [abs(np.vdot(records[j], records[k])) for j in range(d_a) for k in range(j + 1, d_a)]
    if max(overlaps) - min(overlaps) > 1e-9:
        raise ValueError('record overlaps differ; the mixed rule is defined for a common overlap only')
    return float(overlaps[0])


def mixed_rule_kraus(U, d_cr, d_loop, pointer, rho_a, c, fallback='open', n_bases=600):
    """Kraus operators of (1 - c) Phi_pointer + c Phi_state for the input's reduced state rho_a."""
    out = []
    if c < 1:
        out += [np.sqrt(1 - c) * K for K in past_preserving_kraus(U, d_cr, d_loop, pointer, fallback)]
    if c > 0:
        out += [np.sqrt(c) * K for K in state_world_kraus(U, d_cr, d_loop, rho_a, n_bases=n_bases, fallback=fallback)]
    return out
