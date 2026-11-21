"""SPDX-License-Identifier: MIT. Circuits re-implemented from two papers.

[L11] S. Lloyd et al., "Closed timelike curves via post-selection: theory and
      experimental demonstration", arXiv:1005.2219v1; Phys. Rev. Lett. 106, 040403 (2011).
      Fig. 2a (grandfather), Fig. 2b (unproved theorem), Figs. 3-4 (quantum gun).
[BHW] T. A. Brun, J. Harrington, M. M. Wilde, "Localized closed timelike curves can
      perfectly distinguish quantum states", arXiv:0811.1209v2; Phys. Rev. Lett. 102,
      210402 (2009). Fig. 1 (|0> vs |->), Fig. 2 and Eq. (3) (BB84 states).

Wiring was read from the figures of the arXiv PDFs. Convention notes are in
ctc/LITERATURE_REPRODUCTION.md. CR qubits first, loop qubits last; qubit 0 is the
most significant bit.
"""
import numpy as np

from circuits import Circuit, bit_state

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], complex)
H = np.array([[1, 1], [1, -1]], complex) / np.sqrt(2)
CX = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], complex)  # control first
SWAP = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], complex)

KET = {'0': np.array([1, 0], complex), '1': np.array([0, 1], complex),
       '+': np.array([1, 1], complex) / np.sqrt(2), '-': np.array([1, -1], complex) / np.sqrt(2)}


def embed(n, gate, targets):
    """Full 2^n x 2^n matrix of `gate` acting on qubits `targets` (in that order)."""
    k = len(targets)
    rest = [q for q in range(n) if q not in targets]
    order = list(targets) + rest
    g = gate.reshape([2] * (2 * k))
    full = np.zeros((2 ** n, 2 ** n), complex)
    for index in range(2 ** n):
        v = np.zeros(2 ** n, complex)
        v[index] = 1
        t = v.reshape([2] * n).transpose(order)
        t = np.tensordot(g, t, axes=(list(range(k, 2 * k)), list(range(k))))
        full[:, index] = t.transpose(np.argsort(order)).reshape(-1)
    return full


def pure(vector):
    return np.outer(vector, vector.conj())


def gun(theta):
    """[L11] quantum gun. The paper writes e^{-i theta sigma_x} but expands it as
    cos(theta/2) 1 - i sin(theta/2) sigma_x and says theta = pi flips the bit, so the
    consistent reading is exp(-i theta sigma_x / 2)."""
    return np.cos(theta / 2) * I2 - 1j * np.sin(theta / 2) * X


def lloyd_grandfather(theta=np.pi):
    """[L11] Fig. 2a / Fig. 3a. Probe A records the traveller before the gun, probe B after.
    Slots: probe_a, probe_b, traveller(loop)."""
    U = embed(3, CX, [2, 1]) @ embed(3, gun(theta), [2]) @ embed(3, CX, [2, 0])
    return Circuit('lloyd_grandfather', ['probe_a', 'probe_b'], ['traveller'], U,
                   pure(np.kron(KET['0'], KET['0'])), bit_state(0.5), dict(theta=theta))


def lloyd_unproved_theorem():
    """[L11] Fig. 2b. The qubit emerging from the CTC is copied into the 'proof' qubit,
    the proof is copied into a second qubit, and that copy is sent back into the CTC.
    Slots in:  proof(|0>), deposit(|0>), emerged(loop input)
    Slots out: proof, emerged, deposit(loop output)  -> the final SWAP relabels slots 1,2."""
    U = embed(3, SWAP, [1, 2]) @ embed(3, CX, [0, 1]) @ embed(3, CX, [2, 0])
    return Circuit('lloyd_unproved_theorem', ['proof', 'emerged'], ['deposit'], U,
                   pure(np.kron(KET['0'], KET['0'])), bit_state(0.5))


def bhw_two_state(label):
    """[BHW] Fig. 1: swap A and B, then controlled-Hadamard (A control, B target)."""
    controlled_h = np.kron(pure(KET['0']), I2) + np.kron(pure(KET['1']), H)
    U = controlled_h @ SWAP
    return Circuit('bhw_two_state', ['A'], ['B'], U, pure(KET[label]), bit_state(0.5), dict(input=label))


def bhw_bb84_unitary():
    """[BHW] Fig. 2 / Eq. (3). Slots: psi, ancilla, ctc0, ctc1. Two SWAPs (psi<->ctc0,
    ancilla<->ctc1), then U_ab on (ctc0, ctc1) controlled by the CR value |ab>."""
    U_ab = {(0, 0): SWAP,
            (0, 1): np.kron(X, X),
            (1, 0): np.kron(X @ H, I2),
            (1, 1): np.kron(X, H) @ SWAP}
    controlled = sum(embed(4, pure(np.kron(KET[str(a)], KET[str(b)])), [0, 1]) @ embed(4, U, [2, 3])
                     for (a, b), U in U_ab.items())
    return controlled @ embed(4, SWAP, [1, 3]) @ embed(4, SWAP, [0, 2])


def bhw_bb84(rho_psi):
    """rho_psi: 2x2 input state; the ancilla is |0>."""
    return Circuit('bhw_bb84', ['a', 'b'], ['ctc0', 'ctc1'], bhw_bb84_unitary(),
                   np.kron(rho_psi, pure(KET['0'])), np.eye(4, dtype=complex) / 4)


# Claimed BB84 map [BHW]: |00>->|00>, |+0>->|10>, |10>->|01>, |-0>->|11>.
BB84_CLAIM = {'0': (0, 0), '+': (1, 0), '1': (0, 1), '-': (1, 1)}
