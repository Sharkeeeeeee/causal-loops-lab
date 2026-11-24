"""SPDX-License-Identifier: MIT. Conjecture lottery: the pool of conjectures, defined before any checking.

Each conjecture says: "every unitary U in circuit class X has property P". The rule under test is
past-preserving selection (PP) with the computational basis as record basis. The comparison
rules are P-CTC, D-CTC (Cesaro fixed point from the maximally mixed seed) and no loop
(loop input maximally mixed). Inputs are computational-basis states of the CR system ("worlds"),
except where a property names another input.

Finite classes are checked exhaustively: the result is a proof or a counterexample.
Continuous classes are searched with a fixed budget of random samples, seeded by the SHA-256
of credences.json: the result is a counterexample or "not refuted" (not a proof).
"""

CLASSES = {
    'perm21': dict(kind='finite', d_cr=4, d_loop=2,
                   text='all 40320 classical reversible circuits, CR = 2 bits, loop = 1 bit'),
    'perm12': dict(kind='finite', d_cr=2, d_loop=4,
                   text='all 40320 classical reversible circuits, CR = 1 bit, loop = 2 bits'),
    'cliff11': dict(kind='finite', d_cr=2, d_loop=2,
                    text='all 11520 two-qubit Clifford unitaries (up to global phase), CR = 1 qubit, loop = 1 qubit'),
    'haar11': dict(kind='search', d_cr=2, d_loop=2, budget=20000,
                   text='Haar-random two-qubit unitaries, CR = 1 qubit, loop = 1 qubit'),
    'haar21': dict(kind='search', d_cr=4, d_loop=2, budget=3000,
                   text='Haar-random three-qubit unitaries, CR = 2 qubits, loop = 1 qubit'),
    'ctrl21': dict(kind='search', d_cr=4, d_loop=2, budget=3000,
                   text='controlled form U = (V x 1) sum_k |k><k| x W_k with Haar V and W_k, CR = 2 qubits, loop = 1 qubit'),
}

PROPERTIES = {
    'exists': 'every world has at least one consistent history: C|k> != 0 for every basis input k',
    'pure': 'PP output is a pure state for every basis input',
    'entropy': 'PP output never has more von Neumann entropy than the no-loop output, for every basis input',
    'dctc_diag': 'PP and D-CTC give the same computational-basis distribution, for every basis input',
    'noloop_diag': 'PP and no loop give the same computational-basis distribution, for every basis input',
    'effect_le_pctc': ('on the maximally mixed CR input, the trace distance between PP and no loop is at most '
                       'the trace distance between P-CTC and no loop (vacuous where P-CTC is undefined)'),
    'unital': 'PP maps the maximally mixed CR input to itself',
    'dctc_unique_agree': 'for every basis input whose D-CTC fixed point is unique, PP and D-CTC outputs are equal',
    'support_subset': 'the support of the PP output lies inside the support of the no-loop output, for every basis input',
    'commute': 'PP output commutes with the no-loop output, for every basis input',
}

TOL = 1e-8
LOW, HIGH = 0.35, 0.65        # only conjectures I rate in this range are tested


def conjecture_ids():
    return [f'{c}:{p}' for c in CLASSES for p in PROPERTIES]
