"""SPDX-License-Identifier: MIT. Control for the direct test: flip the superposition's coherence PHYSICALLY.

Why: in the first direct test (job dc1k4l5hdvas73bkumqg, S = +0.016, z = 10) the +/- pi/2 preparations
compiled to the SAME physical pulse (one sx); the sign lived only in virtual RZ frame changes. So an
error in group B that turns physical coherence into population (for example microwave crosstalk from
the CNOT's pulses on r) was not cancelled, and it has exactly the observed signature: same sign for
+/- pi/2, nothing at the endpoints, same direction on every pair.

Here the two superpositions are physically different pulse sequences with opposite lab-frame coherence:
  '+h': sx          from |0>:  (|0> - i|1>)/sqrt(2)
  '-h': x, then sx  from |0>:  sx|1> = (-i|0> + |1>)/sqrt(2)  -> opposite coherence, same population
plus endpoints '0' (nothing) and 'pi' (x). Circuits are written in native gates and transpiled at
optimization level 0, so no pulses are merged.

  S = [Delta(+h) + Delta(-h)]/2 - [Delta(0) + Delta(pi)]/2
  crosstalk / coherence-to-population artifact: Delta(+h) and Delta(-h) have opposite signs, S -> 0
  loop model (population-only reweighting of the isolated superposition): S stays at the model value

Usage (from the repository root):
  python -B ctc/born_rule/physical_control.py preregister
  python -B ctc/born_rule/physical_control.py ibm --backend ibm_kingston --pairs 24 --shots 40000 [--dry-run]
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from direct_test import DATA, Z_ANOMALY, Z_NO_DEVIATION, choose_pairs, p_one  # noqa: E402

PREPS = {'0': [], '+h': ['sx'], '-h': ['x', 'sx'], 'pi': ['x']}
GROUPS = ('A', 'B')
PREREG = HERE / 'PHYSICAL_CONTROL_PREREGISTRATION.md'
FIRST_RUN = dict(job='dc1k4l5hdvas73bkumqg', S=0.0161, se=0.00155)


def build(group, prep, n_pairs):
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
    q, c = QuantumRegister(2 * n_pairs, 'q'), ClassicalRegister(2 * n_pairs, 'c')
    qc = QuantumCircuit(q, c, name=f'{group}_{prep}')
    for i in range(n_pairs):
        for gate in PREPS[prep]:
            getattr(qc, gate)(q[2 * i])
    if group == 'B':
        for i in range(n_pairs):
            qc.cx(q[2 * i], q[2 * i + 1])
    qc.barrier()
    qc.measure(q, c)
    return qc


def signal(p):
    d = {k: p[('A', k)] - p[('B', k)] for k in PREPS}
    return (d['+h'] + d['-h']) / 2 - (d['0'] + d['pi']) / 2


def odd_part(p):
    """[Delta(+h) - Delta(-h)] / 2: the coherence-to-population error the first test could not cancel."""
    return ((p[('A', '+h')] - p[('B', '+h')]) - (p[('A', '-h')] - p[('B', '-h')])) / 2


def analyze(data):
    n, shots = data['n_pairs'], data['shots']
    rows = []
    for i in range(n):
        p = {(g, k): p_one(data['counts'][f'{g}_{k}'], i) for g in GROUPS for k in PREPS}
        rows.append(dict(pair=i, S=signal(p), odd=odd_part(p), p={f'{g}_{k}': v for (g, k), v in p.items()}))
    s = np.array([r['S'] for r in rows])
    o = np.array([r['odd'] for r in rows])
    se_pairs = float(s.std(ddof=1) / np.sqrt(n))
    var = 0.0
    for r in rows:
        v = {k: r['p'][k] * (1 - r['p'][k]) / shots for k in r['p']}
        var += (v['A_+h'] + v['B_+h'] + v['A_-h'] + v['B_-h'] + v['A_0'] + v['B_0'] + v['A_pi'] + v['B_pi']) / 4
    se_shots = float(np.sqrt(var) / n)
    se = max(se_pairs, se_shots)
    mean = float(s.mean())
    z = mean / se
    verdict = ('no deviation' if abs(z) < Z_NO_DEVIATION else
               'anomaly persists (error hunt and replication required)' if abs(z) >= Z_ANOMALY else 'inconclusive')
    return dict(S_mean=mean, se_pairs=se_pairs, se_shots=se_shots, se_used=se, z=z,
                S_bound95=abs(mean) + 1.96 * se, verdict=verdict,
                odd_mean=float(o.mean()), odd_se=float(o.std(ddof=1) / np.sqrt(n)),
                odd_positive=int(np.sum(o > 0)), per_pair=rows)


def prereg_text():
    return f"""# Preregistration: physical-coherence control for the direct test

Fixed before submission; SHA-256 stored with the results.

## Why

The first direct test (job {FIRST_RUN['job']}) gave S = +{FIRST_RUN['S']} +/- {FIRST_RUN['se']} (z about 10), positive on all
24 pairs. Its +/- pi/2 preparations were the same physical pulse; the sign was a virtual frame change.
Errors that turn physical coherence into population were therefore not cancelled.

## Design

Same qubit pairs and groups as before (A isolated; B recorded by CNOT q -> r). Preparations in native
gates, transpiled at optimization level 0: '0' none; '+h' sx; '-h' x then sx (opposite physical coherence,
same population); 'pi' x. S = [Delta(+h) + Delta(-h)]/2 - [Delta(0) + Delta(pi)]/2, where
Delta = P_A(q=1) - P_B(q=1). Also reported: odd part O = [Delta(+h) - Delta(-h)]/2.

## Predictions

| hypothesis | S | O |
|---|---|---|
| coherence-to-population hardware error (crosstalk) | about 0 | about +0.016 (carries the old signal) |
| loop model (population-only reweighting of isolated superpositions) | about +0.016 | about 0 |
| standard QM, no such error | 0 | 0 |

## Decision rules

Standard error = larger of pair spread / sqrt(pairs) and shot noise.
- |z(S)| < {Z_NO_DEVIATION}: no deviation; the first result is attributed to the uncancelled coherence error if O
  is also significant (|O| / SE_O >= 5) with the old sign.
- |z(S)| >= {Z_ANOMALY}: the anomaly persists; then replicate on another device before any interpretation.
- In between: inconclusive.
"""


def prereg_check():
    if not PREREG.exists():
        return None
    content = PREREG.read_text(encoding='utf-8')
    return hashlib.sha256(content.encode('utf-8')).hexdigest() if content == prereg_text() else None


def run_ibm(backend_name, n_pairs, shots, dry_run, preflight_job):
    sys.path.insert(0, str(HERE.parent / 'hardware'))
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from layout import readout_errors
    prereg = prereg_check()
    if prereg is None and not dry_run:
        sys.exit('PHYSICAL_CONTROL_PREREGISTRATION.md missing or out of date: run preregister first')
    service = QiskitRuntimeService()
    backend = service.backend(backend_name)
    readout = [backend.target['measure'][(x,)].error or 1.0 for x in range(backend.num_qubits)]
    if preflight_job:
        r0 = service.job(preflight_job).result()
        measured = readout_errors(r0[0].data.c.get_counts(), r0[1].data.c.get_counts())
        readout = [max(a, b) for a, b in zip(readout, measured)]
    pairs = choose_pairs(backend, n_pairs, readout)
    layout = [x for pair in pairs for x in pair]
    isa = []
    for g in GROUPS:
        for k in PREPS:
            tc = transpile(build(g, k, n_pairs), backend=backend, initial_layout=layout, optimization_level=0)
            if [int(x) for x in tc.layout.final_index_layout()] != layout:
                sys.exit(f'transpiler moved qubits in {g}_{k}')
            q0 = layout[0]
            seq = [inst.operation.name for inst in tc.data if inst.operation.name not in ('barrier', 'measure', 'rz')
                   and q0 in [tc.find_bit(x).index for x in inst.qubits]]
            print(f'  {g}_{k}: physical pulses on q={q0}: {seq}')
            isa.append((g, k, tc))
    print(f'backend {backend.name}; pairs {pairs}; {len(isa)} circuits x {shots} shots')
    if dry_run:
        return
    job = SamplerV2(mode=backend).run([tc for _, _, tc in isa], shots=shots)
    print(f'submitted job {job.job_id()}; waiting')
    res = job.result()
    data = dict(backend=backend.name, job_id=job.job_id(), n_pairs=n_pairs, shots=shots, pairs=pairs,
                preregistration_sha256=prereg, retrieved_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),
                counts={f'{g}_{k}': res[i].data.c.get_counts() for i, (g, k, _) in enumerate(isa)})
    data['analysis'] = analyze(data)
    out = DATA / f'control_{backend.name}_{job.job_id()}.json'
    out.write_text(json.dumps(data, indent=1), encoding='utf-8')
    a = data['analysis']
    print(f"S = {a['S_mean']:+.2e} +/- {a['se_used']:.2e}, z = {a['z']:+.2f} -> {a['verdict']}")
    print(f"odd part O = {a['odd_mean']:+.2e} +/- {a['odd_se']:.2e} (positive on {a['odd_positive']}/{n_pairs} pairs)")
    print(f'wrote {out}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('preregister', 'ibm'))
    parser.add_argument('--backend', default='ibm_kingston')
    parser.add_argument('--pairs', type=int, default=24)
    parser.add_argument('--shots', type=int, default=40000)
    parser.add_argument('--preflight-job', default='dc1j2plhdvas73bktbi0')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.command == 'preregister':
        PREREG.write_text(prereg_text(), encoding='utf-8', newline='\n')
        print(f'SHA-256 {hashlib.sha256(prereg_text().encode("utf-8")).hexdigest()}  ({PREREG})')
    else:
        run_ibm(args.backend, args.pairs, args.shots, args.dry_run, args.preflight_job)


if __name__ == '__main__':
    main()
