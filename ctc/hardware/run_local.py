"""SPDX-License-Identifier: MIT. Run the experiments on Qiskit's ideal local simulator.

Needs only `qiskit`. Use this before spending hardware time: it runs the circuits, the
(ideal) readout calibration and the full analysis end to end, with shot noise but no
hardware noise.

Usage (from the repository root):
  python -B ctc/hardware/run_local.py [--shots 16384] [--seed 1]
"""
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import report  # noqa: E402
from experiments import EXPERIMENTS, build_circuit  # noqa: E402


def calibration(n, value):
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
    q, c = QuantumRegister(n, 'q'), ClassicalRegister(n, 'c')
    qc = QuantumCircuit(q, c)
    if value:
        qc.x(q)
    qc.measure(q, c)
    return qc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--shots', type=int, default=16384)
    parser.add_argument('--seed', type=int, default=1)
    args = parser.parse_args()

    from qiskit.primitives import StatevectorSampler
    sampler = StatevectorSampler(seed=args.seed)
    circuits = [build_circuit(e) for e in EXPERIMENTS]
    for e in EXPERIMENTS:
        circuits += [calibration(e.n_qubits, 0), calibration(e.n_qubits, 1)]
    result = sampler.run(circuits, shots=args.shots).result()
    n = len(EXPERIMENTS)
    data = dict(backend='qiskit StatevectorSampler (ideal)', shots=args.shots, seed=args.seed,
                options='ideal simulator; readout calibration path exercised with ideal calibration',
                counts={e.name: result[i].data.c.get_counts() for i, e in enumerate(EXPERIMENTS)},
                calibration={e.name: dict(zeros=result[n + 2 * i].data.c.get_counts(),
                                          ones=result[n + 2 * i + 1].data.c.get_counts())
                             for i, e in enumerate(EXPERIMENTS)})
    out = HERE / 'data' / 'local_ideal.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, indent=1), encoding='utf-8')
    text, summary = report(data)
    print(text)
    out.with_name('local_ideal_report.md').write_text(text + '\n', encoding='utf-8')
    out.with_name('local_ideal_summary.json').write_text(json.dumps(summary, indent=2, default=float),
                                                         encoding='utf-8')
    print(f'wrote {out}')


if __name__ == '__main__':
    main()
