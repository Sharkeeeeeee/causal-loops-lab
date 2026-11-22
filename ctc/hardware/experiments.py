"""SPDX-License-Identifier: MIT. Loop experiments that run on a real quantum computer.

One circuit per experiment (two for the eraser). Qubit layout: CR qubits, loop qubit m,
partner qubit p, record qubits.
  1. Each random CR input is prepared with RY and copied into a record qubit with CNOT. The
     record is the recorded past (in the eraser it is Bob's idler, read in the X basis).
  2. m and p start in the Bell state |Phi+>.
  3. U acts on CR x m.
  4. Bell measurement on (m, p). Outcome 00 means the loop closed consistently.

The same shots give all three rules:
  no loop (unknown external message) : ignore the Bell outcome; m alone is maximally mixed
  P-CTC (Lloyd et al. 2011)          : keep only Bell outcome 00
  past-preserving selection          : world weights from all shots; inside each world keep its
                                       00 shots. Worlds with no consistent history fall back to
                                       D-CTC, which for these circuits equals ignoring the Bell
                                       outcome (checked exactly by fallback_matches_no_loop).

Running these circuits sends nothing back in time. Postselection is ordinary forward-time
bookkeeping; the experiments test what each rule predicts, not whether loops exist.
"""
from dataclasses import dataclass, field
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from circuits import permutation_unitary  # noqa: E402
from models import d_ctc_fixed_point, partial_trace_operator_loop  # noqa: E402
from past_preserving import apply_kraus, past_preserving_kraus  # noqa: E402

RULES = ('no_loop', 'p_ctc', 'past_preserving')
TOL = 1e-9
_S = 1 / np.sqrt(2)
BASIS = {   # columns: outcome 0, outcome 1
    'Z': np.eye(2, dtype=complex),
    'X': np.array([[_S, _S], [_S, -_S]], complex),
    'Y': np.array([[_S, _S], [1j * _S, -1j * _S]], complex),
}


@dataclass
class Experiment:
    name: str
    title: str
    cr_labels: list
    priors: dict          # CR label -> P(1). Unlisted CR qubits start in 0 and are not recorded.
    gates: object         # gates(qc, cr, m): appends U; cr maps label -> qubit
    headlines: list = field(default_factory=list)   # (label, event, given); event(k, y) -> bool
    mapping: object = None        # bijection on bit tuples (CR..., m), qubit 0 most significant
    matrix: object = None         # or an explicit unitary on (CR..., m)
    cr_basis: dict = field(default_factory=dict)    # CR label -> measurement basis (default Z)
    record_basis: str = 'Z'       # basis in which the record qubits are read (= record basis of the rule)
    group: str = None             # experiments sharing a group are analysed together (eraser)

    @property
    def n_cr(self):
        return len(self.cr_labels)

    @property
    def d_cr(self):
        return 2 ** self.n_cr

    @property
    def recorded(self):
        return [label for label in self.cr_labels if label in self.priors]

    @property
    def n_qubits(self):
        return self.n_cr + 2 + len(self.recorded)

    def unitary(self):
        return permutation_unitary(self.n_cr + 1, self.mapping) if self.matrix is None else self.matrix

    def worlds(self):
        """List of (k, p_k): k = recorded outcome bits (dict), p_k = prior weight."""
        out = []
        recs = self.recorded
        for bits in range(2 ** len(recs)):
            k = {label: (bits >> (len(recs) - 1 - j)) & 1 for j, label in enumerate(recs)}
            p = 1.0
            if self.record_basis == 'Z':
                for label, b in k.items():
                    p *= self.priors[label] if b else 1 - self.priors[label]
            else:
                p = 0.5 ** len(recs)   # X-basis records of the Bell-type preparation are uniform
            out.append((k, p))
        return out

    def record_basis_matrix(self):
        """Record basis of the whole CR input: record_basis on recorded qubits, Z elsewhere."""
        M = np.ones((1, 1), complex)
        for label in self.cr_labels:
            M = np.kron(M, BASIS[self.record_basis] if label in self.priors else BASIS['Z'])
        return M

    def world_vector(self, k):
        index = sum(k.get(label, 0) << (self.n_cr - 1 - i) for i, label in enumerate(self.cr_labels))
        return self.record_basis_matrix()[:, index]

    def decode_y(self, y):
        return {label: (y >> (self.n_cr - 1 - i)) & 1 for i, label in enumerate(self.cr_labels)}


# ---------------------------------------------------------------- experiments

def _grandfather_gates(qc, cr, m):
    qc.x(m)
    qc.cx(cr['jam'], m)                    # m' = m XOR NOT jam


def _refusal_gates(qc, cr, m):
    qc.cx(m, cr['log'])                    # the receiver writes the message into the log
    qc.rccx(cr['a'], cr['log'], m)         # if a = 1 and a message arrived, the sender refuses.
    # rccx is a Toffoli up to a relative phase (3 CNOTs instead of 6). Every consistent history
    # here leaves a distinct record, so no rule's prediction depends on that phase; the tests
    # check this exactly (Gates.test_relative_phase_does_not_matter).


def _one_way_gates(qc, cr, m):
    qc.cx(cr['a'], m)                      # a controls the loop; the loop never acts on a


def _eraser_gates(qc, cr, m):
    qc.cp(np.pi / 2, cr['a'], m)           # a message from the future adds a phase to the right path


ERASER_U = np.diag([1, 1, 1, np.exp(1j * np.pi / 2)]).astype(complex)
_bob_plus = ("P(Bob idler reads X = +)  [Bob's own statistics]", lambda k, y: k['a'] == 0, None)


def _eraser(basis):
    return Experiment(
        f'eraser_{basis.lower()}', f'Delayed-choice eraser with a loop: path measured in {basis}',
        ['a'], {'a': 0.5}, _eraser_gates,
        [_bob_plus,
         (f'P(path reads {basis} = +)  [whole screen]', lambda k, y: y['a'] == 0, None),
         (f'P(path reads {basis} = +, given Bob X = +)  [sorted fringe]', lambda k, y: y['a'] == 0,
          lambda k, y: k['a'] == 0)],
        matrix=ERASER_U, cr_basis={'a': basis}, record_basis='X', group='eraser')


EXPERIMENTS = [
    Experiment(
        'grandfather', 'Grandfather paradox: the gun jams with prior 0.2',
        ['jam'], {'jam': 0.2}, _grandfather_gates,
        [('P(jam = 1)  [past]', lambda k, y: y['jam'] == 1, None)],
        mapping=lambda b: (b[0], b[1] ^ (1 - b[0]))),
    Experiment(
        'refusal', 'Refusal: if a = 1 the sender never sends a message it received',
        ['a', 'log'], {'a': 0.5}, _refusal_gates,
        [('P(a = 1)  [past]', lambda k, y: k['a'] == 1, None),
         ('P(message logged, given a = 1)  [future]', lambda k, y: y['log'] == 1, lambda k, y: k['a'] == 1),
         ('P(message logged, given a = 0)  [future]', lambda k, y: y['log'] == 1, lambda k, y: k['a'] == 0)],
        mapping=lambda b: (b[0], b[1] ^ b[2], b[2] ^ (b[0] & (b[1] ^ b[2])))),
    Experiment(
        'one_way', 'One-way control: a controls the loop, the loop never acts on a',
        ['a'], {'a': 0.5}, _one_way_gates,
        [('P(a = 1)  [past; equals the record held by a partner]', lambda k, y: y['a'] == 1, None)],
        mapping=lambda b: (b[0], b[1] ^ b[0])),
    _eraser('X'),
    _eraser('Y'),
    Experiment(
        'eraser_z', "Eraser, Bob reads which-path (Z): P-CTC changes Bob's own statistics",
        ['a'], {'a': 0.5}, _eraser_gates,
        [("P(Bob idler reads Z = 0)  [Bob's own statistics]", lambda k, y: k['a'] == 0, None),
         ('P(path reads Z = 1, right slit)', lambda k, y: y['a'] == 1, None)],
        matrix=ERASER_U, record_basis='Z', group='eraser'),
]
BY_NAME = {e.name: e for e in EXPERIMENTS}


# ---------------------------------------------------------------- exact predictions

def is_consistent_world(exp, k, U=None):
    C = partial_trace_operator_loop(exp.unitary() if U is None else U, exp.d_cr, 2)
    return np.linalg.norm(C @ exp.world_vector(k)) > TOL


def fallback_matches_no_loop(exp):
    """For every world with no consistent history, the D-CTC fixed point is maximally mixed, so
    the D-CTC fallback equals the no-loop output and can be read from shots ignoring the Bell test."""
    U = exp.unitary()
    for k, _ in exp.worlds():
        if not is_consistent_world(exp, k):
            v = exp.world_vector(k)
            tau, _ = d_ctc_fixed_point(U, np.outer(v, v.conj()), exp.d_cr, 2)
            if not np.allclose(tau, np.eye(2) / 2, atol=1e-8):
                return False
    return True


def initial_state(exp):
    """Joint pure state of (CR, records): RY-prepared CR qubits, each copied by CNOT."""
    n_r = len(exp.recorded)
    psi = np.zeros(exp.d_cr * 2 ** n_r, complex)
    for x in range(exp.d_cr):
        bits = exp.decode_y(x)
        amp = 1.0
        for label in exp.cr_labels:
            p1 = exp.priors.get(label, 0.0)
            amp *= np.sqrt(p1) if bits[label] else np.sqrt(1 - p1)
        r = sum(bits[label] << (n_r - 1 - j) for j, label in enumerate(exp.recorded))
        psi[x * 2 ** n_r + r] += amp
    return np.outer(psi, psi.conj())


def exact(exp, U=None):
    """Joint distributions P(k, y) for each rule, as {rule: {(k_tuple, y): prob}}."""
    U = exp.unitary() if U is None else U
    d, n_r = exp.d_cr, len(exp.recorded)
    d_r = 2 ** n_r
    rho = initial_state(exp)
    C = np.kron(partial_trace_operator_loop(U, d, 2), np.eye(d_r))
    states = {}
    joint_U = np.einsum('xlym,bc->xblycm', U.reshape(d, 2, d, 2), np.eye(d_r)).reshape(d * d_r * 2, d * d_r * 2)
    big = joint_U @ np.kron(rho, np.eye(2) / 2) @ joint_U.conj().T
    states['no_loop'] = np.einsum('aibi->ab', big.reshape(d * d_r, 2, d * d_r, 2))
    pc = C @ rho @ C.conj().T
    states['p_ctc'] = pc / np.trace(pc).real if np.trace(pc).real > TOL else None
    states['past_preserving'] = apply_kraus(past_preserving_kraus(U, d, 2, exp.record_basis_matrix()), rho, d_r)

    cr_meas = np.ones((1, 1), complex)
    for label in exp.cr_labels:
        cr_meas = np.kron(cr_meas, BASIS[exp.cr_basis.get(label, 'Z')])
    rec_meas = np.ones((1, 1), complex)
    for _ in range(n_r):
        rec_meas = np.kron(rec_meas, BASIS[exp.record_basis])
    M = np.kron(cr_meas, rec_meas)          # column j = measurement outcome j (CR bits, then record bits)
    out = {}
    for rule, state in states.items():
        out[rule] = {}
        probs = np.full(d * d_r, np.nan) if state is None else np.einsum('ij,ik,kj->j', M.conj(), state, M).real
        for y in range(d):
            for r in range(d_r):
                key = tuple((r >> (n_r - 1 - j)) & 1 for j in range(n_r))
                out[rule][(key, y)] = float(probs[y * d_r + r])
    return out


# ---------------------------------------------------------------- circuits (need qiskit)

def _measure_basis(qc, qubit, basis):
    if basis == 'X':
        qc.h(qubit)
    elif basis == 'Y':
        qc.sdg(qubit)
        qc.h(qubit)


def build_circuit(exp):
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
    q = QuantumRegister(exp.n_qubits, 'q')
    c = ClassicalRegister(exp.n_qubits, 'c')
    qc = QuantumCircuit(q, c, name=exp.name)
    cr = {label: q[i] for i, label in enumerate(exp.cr_labels)}
    m, p = q[exp.n_cr], q[exp.n_cr + 1]
    for j, label in enumerate(exp.recorded):
        qc.ry(2 * np.arcsin(np.sqrt(exp.priors[label])), cr[label])
        qc.cx(cr[label], q[exp.n_cr + 2 + j])
    qc.h(m)
    qc.cx(m, p)
    qc.barrier()
    exp.gates(qc, cr, m)
    qc.barrier()
    qc.cx(m, p)
    qc.h(m)
    for label in exp.cr_labels:
        _measure_basis(qc, cr[label], exp.cr_basis.get(label, 'Z'))
    for j in range(len(exp.recorded)):
        _measure_basis(qc, q[exp.n_cr + 2 + j], exp.record_basis)
    qc.measure(q, c)
    return qc


def build_unitary_circuit(exp):
    """U alone on (CR..., m), for checking the gates against exp.unitary()."""
    from qiskit import QuantumCircuit, QuantumRegister
    q = QuantumRegister(exp.n_cr + 1, 'q')
    qc = QuantumCircuit(q)
    exp.gates(qc, {label: q[i] for i, label in enumerate(exp.cr_labels)}, q[exp.n_cr])
    return qc


# ---------------------------------------------------------------- estimates from counts

def parse(exp, bitstring):
    """Qiskit bitstrings put clbit 0 on the right. Returns (k_tuple, y, consistent)."""
    bits = [int(ch) for ch in reversed(bitstring.replace(' ', ''))]
    y = sum(bits[i] << (exp.n_cr - 1 - i) for i in range(exp.n_cr))
    consistent = bits[exp.n_cr] == 0 and bits[exp.n_cr + 1] == 0
    k = tuple(bits[exp.n_cr + 2 + j] for j in range(len(exp.recorded)))
    return k, y, consistent


def tally(exp, counts):
    """Array n[k_index, y, consistent] from a counts dict (values may be non-integer)."""
    n = np.zeros((2 ** len(exp.recorded), exp.d_cr, 2))
    for bitstring, c in counts.items():
        k, y, ok = parse(exp, bitstring)
        n[sum(b << (len(k) - 1 - j) for j, b in enumerate(k)), y, int(ok)] += c
    return n


def estimate_from_tally(exp, n):
    out = {rule: {} for rule in RULES}
    total = n.sum()
    consistent_total = n[:, :, 1].sum()
    for k_index, (k, _) in enumerate(exp.worlds()):
        key = tuple(k.values())
        n_world, n_world_ok = n[k_index].sum(), n[k_index, :, 1].sum()
        good = is_consistent_world(exp, k)
        for y in range(exp.d_cr):
            out['no_loop'][(key, y)] = n[k_index, y].sum() / total
            out['p_ctc'][(key, y)] = n[k_index, y, 1] / consistent_total if consistent_total else np.nan
            if good:
                within = n[k_index, y, 1] / n_world_ok if n_world_ok else np.nan
            else:
                within = n[k_index, y].sum() / n_world if n_world else np.nan
            out['past_preserving'][(key, y)] = n_world / total * within
    return out


def estimate(exp, counts):
    return estimate_from_tally(exp, tally(exp, counts))


def headline_values(exp, joint):
    """Evaluate exp.headlines on a joint distribution {(k_tuple, y): prob}."""
    values = []
    recs = exp.recorded
    for _, event, given in exp.headlines:
        num = den = 0.0
        for (key, y), prob in joint.items():
            k, yd = dict(zip(recs, key)), exp.decode_y(y)
            if given is None or given(k, yd):
                den += prob
                if event(k, yd):
                    num += prob
        values.append(num / den if den > 0 else np.nan)
    return values


def consistency_rates(exp, counts):
    """Fraction of shots passing the Bell test in each world; exact value ||C|k>||^2 / 4."""
    n = tally(exp, counts)
    C = partial_trace_operator_loop(exp.unitary(), exp.d_cr, 2)
    rows = []
    for k_index, (k, _) in enumerate(exp.worlds()):
        n_world = n[k_index].sum()
        measured = n[k_index, :, 1].sum() / n_world if n_world else np.nan
        rows.append((k, measured, np.linalg.norm(C @ exp.world_vector(k)) ** 2 / 4))
    return rows


def fringe(px_plus, py_plus):
    """Visibility and bright-fringe phase from P(X = +) and P(Y = +) of the path qubit."""
    x, y = 2 * px_plus - 1, 2 * py_plus - 1
    return float(np.hypot(x, y)), float(np.arctan2(y, x))
