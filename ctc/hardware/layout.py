"""SPDX-License-Identifier: MIT. Choose physical qubits from measured, not reported, readout errors.

The first hardware runs showed that a backend's reported calibration can be wrong: qubit 42 on
ibm_marrakesh was reported at 0.7% readout error and measured at about 40%. So before the main
job, a short preflight job measures the readout error of every qubit, and layouts are chosen
by enumerating every placement of a circuit's interaction graph on the coupling map (VF2),
excluding badly measured qubits, and scoring the rest by measured readout error plus reported
two-qubit gate error.
"""
import numpy as np


def preflight_circuits(backend):
    """All qubits in 0, and all qubits in 1, measured. Run without twirling."""
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
    n = backend.num_qubits
    out = []
    for value in (0, 1):
        q, c = QuantumRegister(n, 'q'), ClassicalRegister(n, 'c')
        qc = QuantumCircuit(q, c, name=f'preflight{value}')
        if value:
            qc.x(q)
        qc.measure(q, c)
        out.append(qc)
    return out


def readout_errors(counts0, counts1):
    """Per-qubit average readout error 0.5 * (P(1|0) + P(0|1)) from the two preflight results."""
    def wrong(counts, value):
        n = len(next(iter(counts)))
        err = np.zeros(n)
        for bitstring, c in counts.items():
            for i, ch in enumerate(reversed(bitstring)):
                err[i] += c * (int(ch) != value)
        return err / sum(counts.values())
    return 0.5 * (wrong(counts0, 0) + wrong(counts1, 1))


def interaction_edges(circuit):
    """Pairs of virtual qubits that share a two-qubit gate."""
    edges = set()
    for inst in circuit.data:
        if inst.operation.name in ('barrier', 'measure'):
            continue
        qs = [circuit.find_bit(q).index for q in inst.qubits]
        if len(qs) == 2:
            edges.add(tuple(sorted(qs)))
        elif len(qs) > 2:
            raise ValueError(f'decompose {inst.operation.name} into two-qubit gates first')
    return sorted(edges)


def two_qubit_error(target, a, b):
    errs = []
    for name in ('cz', 'ecr', 'cx'):
        if name in target.operation_names:
            for pair in ((a, b), (b, a)):
                props = target[name].get(pair)
                if props is not None and props.error is not None:
                    errs.append(props.error)
    return min(errs) if errs else None


def choose_layout(backend, circuit, readout, max_readout=0.03, max_gate=0.01, call_limit=None):
    """Best placement of `circuit` (virtual -> physical list) and its score, or (None, None)."""
    import rustworkx as rx
    from qiskit import transpile
    flat = transpile(circuit, basis_gates=['u', 'cx'], optimization_level=0)   # expose 2-qubit structure
    edges = interaction_edges(flat)
    n = circuit.num_qubits
    pattern = rx.PyGraph()
    pattern.add_nodes_from(range(n))
    pattern.add_edges_from_no_data(edges)

    target = backend.target
    good = [q for q in range(backend.num_qubits) if readout[q] <= max_readout]
    coupling = rx.PyGraph()
    index = {q: coupling.add_node(q) for q in good}
    seen = set()
    for a, b in backend.coupling_map.get_edges():
        if a in index and b in index and (b, a) not in seen:
            err = two_qubit_error(target, a, b)
            if err is not None and err <= max_gate:
                coupling.add_edge(index[a], index[b], err)
                seen.add((a, b))

    best, best_score = None, None
    for mapping in rx.vf2_mapping(coupling, pattern, subgraph=True, induced=False, call_limit=call_limit):
        phys = [None] * n
        for node, virt in mapping.items():
            phys[virt] = coupling[node]
        score = sum(-np.log(1 - readout[p]) for p in phys)
        score += sum(-np.log(1 - two_qubit_error(target, phys[a], phys[b])) for a, b in edges)
        if best_score is None or score < best_score:
            best, best_score = phys, score
    return best, best_score
