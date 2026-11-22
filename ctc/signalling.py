"""SPDX-License-Identifier: MIT. No-signalling tests for the CTC rules.

Alice owns the CTC circuit. Bob is far away and shares correlations (classical) or
entanglement (quantum) with one of Alice's CR qubits, prepared before the loop runs.
Alice freely chooses whether to run the loop. If Bob's local state depends on that
choice, the rule lets Alice signal to Bob without any ordinary channel.

Bob -> Alice is tested separately: Bob measures his half in a basis of his choice
before Alice's loop runs. A rule applied to Alice's reduced state cannot see the
choice; a rule applied branch by branch can.

Derived in this project (see ctc/NO_SIGNALLING.md); likely known in some form.
"""
import numpy as np

from circuits import Circuit
from models import d_ctc, no_loop, p_ctc, t_ctc
from branches import output_state

RULES = ('no_loop', 'p_ctc', 'd_ctc', 't_ctc')


def single_qubit_marginals(rho, n):
    out = []
    t = rho.reshape([2] * (2 * n))
    for k in range(n):
        letters = list(range(2 * n))
        keep_in, keep_out = k, n + k
        others = [q for q in range(n) if q != k]
        for q in others:
            letters[n + q] = letters[q]
        out.append(np.einsum(t, letters, [keep_in, keep_out]))
    return out


def attach_partner(circuit, label, mode):
    """Add Bob's qubit as the last CR qubit, correlated with Alice's CR qubit `label`.

    mode 'classical': Bob holds a perfect copy of the bit (diagonal joint distribution).
    mode 'entangled': Alice's qubit and Bob's form sqrt(1-p)|00> + sqrt(p)|11>, where p is
    the probability that Alice's qubit reads 1. In both cases Alice's own reduced state
    in the computational basis is unchanged. Requires circuit.rho to be a product over
    CR qubits (true for every circuit in this package)."""
    n = len(circuit.cr_labels)
    marginals = single_qubit_marginals(circuit.rho, n)
    product = marginals[0]
    for m in marginals[1:]:
        product = np.kron(product, m)
    if not np.allclose(product, circuit.rho, atol=1e-10):
        raise ValueError('attach_partner needs a product CR input')
    k = circuit.cr_labels.index(label)
    p1 = float(marginals[k][1, 1].real)
    if mode == 'classical':
        pair = np.diag([1 - p1, 0, 0, p1]).astype(complex)
    elif mode == 'entangled':
        v = np.array([np.sqrt(1 - p1), 0, 0, np.sqrt(p1)], complex)
        pair = np.outer(v, v.conj())
    else:
        raise ValueError(mode)
    # Build rho over (qubits..., bob) with Alice's qubit k paired with bob.
    pieces = [marginals[j] for j in range(n)]
    pieces[k] = None
    order_labels = list(range(n)) + ['bob']
    rho = np.ones((1, 1), complex)
    built = []
    for j in range(n):
        if j == k:
            rho = np.kron(rho, pair)
            built += [j, 'bob']
        else:
            rho = np.kron(rho, pieces[j])
            built.append(j)
    # Reorder so that bob is last.
    perm = [built.index(lbl) for lbl in order_labels]
    t = rho.reshape([2] * (2 * (n + 1)))
    t = t.transpose(perm + [p + n + 1 for p in perm])
    rho = t.reshape(2 ** (n + 1), 2 ** (n + 1))
    d_cr, d_loop = circuit.d_cr, circuit.d_loop
    U4 = circuit.U.reshape(d_cr, d_loop, d_cr, d_loop)
    U = np.einsum('xlym,bc->xblycm', U4, np.eye(2)).reshape(d_cr * 2 * d_loop, d_cr * 2 * d_loop)
    return Circuit(circuit.name + '+bob_' + mode, circuit.cr_labels + ['bob'], circuit.loop_labels,
                   U, rho, circuit.baseline_loop, dict(circuit.notes, partner_of=label, mode=mode))


def bob_state(rho_cr, n_cr):
    """Bob is the last CR qubit."""
    d_rest = 2 ** (n_cr - 1)
    return np.einsum('aiaj->ij', rho_cr.reshape(d_rest, 2, d_rest, 2))


def output(circuit, rule, kappa=None, beta=None, t=1.0):
    c = circuit
    if rule == 'no_loop':
        return no_loop(c.U, c.rho, c.d_cr, c.d_loop, c.baseline_loop)
    if rule == 'p_ctc':
        return p_ctc(c.U, c.rho, c.d_cr, c.d_loop)[0]
    if rule == 'd_ctc':
        return d_ctc(c.U, c.rho, c.d_cr, c.d_loop)[0]
    if rule == 't_ctc':
        return t_ctc(c.U, c.rho, c.d_cr, c.d_loop, t)[0]
    if rule == 'branches':
        return output_state(c, kappa, beta)
    raise ValueError(rule)


def trace_distance(a, b):
    return float(0.5 * np.sum(abs(np.linalg.eigvalsh((a - b + (a - b).conj().T) / 2))))


def alice_to_bob(circuit_with_bob, rule, **knobs):
    """Trace distance between Bob's state when Alice runs the loop under `rule` and when
    she does not build it at all (Bob then keeps his prior state). None for a paradox."""
    c = circuit_with_bob
    out = output(c, rule, **knobs)
    if out is None:
        return None
    n = len(c.cr_labels)
    return trace_distance(bob_state(out, n), bob_state(c.rho, n))


def p_ctc_signalling_operator(circuit):
    """C^dag C for Alice's loop. P-CTC is no-signalling for every shared state iff this
    is proportional to the identity (then C is proportional to a unitary)."""
    from models import partial_trace_operator_loop
    C = partial_trace_operator_loop(circuit.U, circuit.d_cr, circuit.d_loop)
    return C.conj().T @ C


def measure_bob(rho, n_cr, basis):
    """Bob measures his qubit (last CR qubit) in Z or X before Alice's loop runs.
    Returns the list of (probability, conditional CR state)."""
    vectors = {'Z': [np.array([1, 0], complex), np.array([0, 1], complex)],
               'X': [np.array([1, 1], complex) / np.sqrt(2), np.array([1, -1], complex) / np.sqrt(2)]}[basis]
    d_rest = 2 ** (n_cr - 1)
    branches = []
    for v in vectors:
        P = np.kron(np.eye(d_rest), np.outer(v, v.conj()))
        branch = P @ rho @ P
        p = float(np.trace(branch).real)
        if p > 1e-12:
            branches.append((p, branch / p))
    return branches


def alice_marginal(rho_cr, n_cr):
    """Alice's reduced state: trace out Bob (last CR qubit)."""
    d_rest = 2 ** (n_cr - 1)
    return np.einsum('aibi->ab', rho_cr.reshape(d_rest, 2, d_rest, 2))


def bob_to_alice(circuit_with_bob, rule, basis, prescription):
    """Alice's output after Bob measured in `basis`.
    prescription 'global': the rule acts on the whole post-measurement state (Bob's result
    unknown to the loop). 'per_branch': the rule acts on each of Bob's outcomes separately
    and the results are averaged with Bob's outcome probabilities."""
    c = circuit_with_bob
    n = len(c.cr_labels)
    branches = measure_bob(c.rho, n, basis)
    if prescription == 'global':
        mixed = sum(p * b for p, b in branches)
        trial = Circuit(c.name, c.cr_labels, c.loop_labels, c.U, mixed, c.baseline_loop)
        return alice_marginal(output(trial, rule), n)
    if prescription == 'per_branch':
        total = 0
        for p, b in branches:
            trial = Circuit(c.name, c.cr_labels, c.loop_labels, c.U, b, c.baseline_loop)
            total = total + p * alice_marginal(output(trial, rule), n)
        return total
    raise ValueError(prescription)
