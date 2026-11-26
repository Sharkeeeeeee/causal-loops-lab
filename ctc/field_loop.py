"""SPDX-License-Identifier: MIT. A field mode coupled to a time loop: does the consistency rule change
the chronology-protection divergence? (ctc/FIELD_LOOP.md)

Model, one frequency at a time. A field mode a (the CR system, entering from outside) meets the loop
mode b at a beamsplitter of angle theta; b then runs once around the loop, picking up the phase
phi = omega * Delta, where Delta is the loop's time shift. A passive, frequency-conserving coupling
keeps different frequencies independent, so every rule below factorizes over modes.

Energy in the loop region. P-CTC (and PPS inside each world) assigns the loop no state of its own;
its operational value is the weak value of the loop's photon number,
    <n_b>_w = Tr[C_n rho C^dag] / Tr[C rho C^dag],   C = Tr_b U,   C_n = Tr_b[U (1 x n_b)]
(the two-state value; Bishop, Costa and Ralph 2024 assign states to the loop this way). With
z = cos(theta) e^{i phi}:
    vacuum input:   <n_b>_w = z / (1 - z)                       (loop photons circulating: sum_m m z^m / sum_m z^m)
    Fock input k:   <n_b>_w = z / (1 - z) + k sin^2(theta) / |1 - z|^2
D-CTC: the loop state is the fixed point; for a passive coupling the vacuum stays vacuum (0), and a
thermal input with mean n gives a thermal loop with mean n.

Summed over a continuum of modes with Abel regularization, the vacuum term gives
    E_vac(Delta) = sum_m c^m int_0^inf omega cos(m omega Delta) d omega  ->  -Li_2(c) / Delta^2,
a sum over windings m of c^m / (m Delta)^2, which diverges as the time shift goes to zero (the
chronology horizon). D-CTC gives zero.
"""
import numpy as np


def vacuum_weak_energy(theta, phi):
    z = np.cos(theta) * np.exp(1j * phi)
    return z / (1 - z)


def fock_weak_energy(theta, phi, k):
    z = np.cos(theta) * np.exp(1j * phi)
    return z / (1 - z) + k * np.sin(theta) ** 2 / abs(1 - z) ** 2


def pps_thermal_energy(theta, phi, nbar):
    """PPS on a thermal input (a mode entangled with the outside): worlds = Fock states (Theorem 7),
    P-CTC inside each; linear in the photon number, so the average is the k = nbar value."""
    return fock_weak_energy(theta, phi, nbar).real


def dctc_thermal_energy(nbar):
    return float(nbar)


def li2(c, terms=20000):
    m = np.arange(1, terms + 1)
    return float(np.sum(c ** m / m ** 2))


def vacuum_energy_continuum(c, delta, eps):
    """sum_m c^m int_0^inf omega cos(m omega delta) e^{-eps omega} d omega (Abel-regularized)."""
    m = np.arange(1, 20001)
    x = m * delta
    return float(np.sum(c ** m * (eps ** 2 - x ** 2) / (eps ** 2 + x ** 2) ** 2))


def truncated_model(theta, phi, n_max):
    """The two-mode unitary on a truncated Fock space (CR mode first), for numerical checks."""
    from scipy.linalg import expm
    a = np.diag(np.sqrt(np.arange(1, n_max)), 1)
    eye = np.eye(n_max)
    A, B = np.kron(a, eye), np.kron(eye, a)
    bs = expm(theta * (A.conj().T @ B - A @ B.conj().T))
    nb = np.diag(np.arange(n_max))
    return np.kron(eye, np.diag(np.exp(1j * phi * np.arange(n_max)))) @ bs, nb


def weak_loop_number(U, nb, rho, n_max):
    from models import partial_trace_operator_loop
    C = partial_trace_operator_loop(U, n_max, n_max)
    Cn = partial_trace_operator_loop(U @ np.kron(np.eye(n_max), nb), n_max, n_max)
    return np.trace(Cn @ rho @ C.conj().T) / np.trace(C @ rho @ C.conj().T)
