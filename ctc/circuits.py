"""SPDX-License-Identifier: MIT. Toy circuits for the CTC rules in models.py.

All circuits here are classical reversible maps on bits (permutation unitaries)
with classical (diagonal) CR inputs, except where coherence is the point
(bootstrap). Qubit 0 is the most significant bit. CR qubits come first, loop
qubits last.
"""
from dataclasses import dataclass, field
import numpy as np

from models import kron_all


def permutation_unitary(n, mapping):
    """Unitary of a bijection on n-bit tuples."""
    dim = 2 ** n
    U = np.zeros((dim, dim), complex)
    seen = set()
    for index in range(dim):
        bits = tuple((index >> (n - 1 - k)) & 1 for k in range(n))
        out = mapping(bits)
        target = sum(b << (n - 1 - k) for k, b in enumerate(out))
        if target in seen:
            raise ValueError('mapping is not a bijection')
        seen.add(target)
        U[target, index] = 1
    return U


def bit_state(p1):
    """Classical bit that is 1 with probability p1."""
    return np.diag([1 - p1, p1]).astype(complex)


@dataclass
class Circuit:
    name: str
    cr_labels: list
    loop_labels: list
    U: np.ndarray
    rho: np.ndarray
    baseline_loop: np.ndarray
    notes: dict = field(default_factory=dict)

    @property
    def d_cr(self):
        return 2 ** len(self.cr_labels)

    @property
    def d_loop(self):
        return 2 ** len(self.loop_labels)

    def probability_one(self, rho_cr, label):
        """P(CR qubit `label` reads 1) in the computational basis."""
        k = self.cr_labels.index(label)
        n = len(self.cr_labels)
        diag = np.diag(rho_cr).real
        return float(sum(diag[i] for i in range(self.d_cr) if (i >> (n - 1 - k)) & 1))

    def expectation_x(self, rho_cr, label):
        """<X> on one CR qubit; detects coherence that P(1) cannot see."""
        k = self.cr_labels.index(label)
        n = len(self.cr_labels)
        X = np.array([[0, 1], [1, 0]], complex)
        ops = [X if j == k else np.eye(2) for j in range(n)]
        return float(np.trace(kron_all(ops) @ rho_cr).real)


def grandfather(eps):
    """Receive bit c from the future; intend to send back NOT c.
    CR qubit g = 1 means the action fails ('gun jams'), with prior probability eps.
    Loop: c -> c XOR (NOT g). Without the failure channel there is no consistent
    history at all."""
    U = permutation_unitary(2, lambda b: (b[0], b[1] ^ (1 - b[0])))
    return Circuit('grandfather', ['jam'], ['message'], U, bit_state(eps),
                   bit_state(0.5), dict(eps=eps))


def kfk(q, r, mode):
    """A message from the future reminds one person.

    CR qubits: bad   (person would choose badly without a reminder, prior q)
               works (the reminder is effective, prior r)
               outcome (1 = the bad outcome happens; starts 0)
               record  (sender register; after the swap it holds the received message)
    Loop qubit: message (1 = a reminder arrives from the future)

    outcome = bad AND NOT (message AND works)
    mode 'motivated'    : the future sender sends a reminder iff the bad outcome happened.
    mode 'unconditional': the future sender always sends a reminder.
    Baseline (no loop): no message arrives.
    """
    if mode not in ('motivated', 'unconditional'):
        raise ValueError(mode)

    def step(b):
        bad, works, outcome, record, message = b
        outcome ^= bad & (1 - (message & works))
        if mode == 'motivated':
            record ^= outcome
        record, message = message, record
        return bad, works, outcome, record, message

    U = permutation_unitary(5, step)
    sender = bit_state(0.0 if mode == 'motivated' else 1.0)
    rho = kron_all([bit_state(q), bit_state(r), bit_state(0.0), sender])
    return Circuit('kfk_' + mode, ['bad', 'works', 'outcome', 'record'], ['message'],
                   U, rho, bit_state(0.0), dict(q=q, r=r, mode=mode))


def bootstrap():
    """A message with no source: the loop bit is copied into a CR record and sent
    back unchanged. Baseline: an unknown external bit (maximally mixed)."""
    U = permutation_unitary(2, lambda b: (b[0] ^ b[1], b[1]))
    return Circuit('bootstrap', ['record'], ['message'], U, bit_state(0.0), bit_state(0.5))
