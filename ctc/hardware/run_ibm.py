"""SPDX-License-Identifier: MIT. Run the loop experiments on IBM Quantum hardware.

Needs `qiskit` and `qiskit-ibm-runtime`, and an IBM Quantum account saved once on this
computer by you (the script never asks for or stores your API key):
  from qiskit_ibm_runtime import QiskitRuntimeService
  QiskitRuntimeService.save_account(channel='ibm_quantum_platform', token='<your key>', set_as_default=True)

Usage (from the repository root):
  python -B ctc/hardware/preregister.py                 # fix predictions and criteria first
  python -B ctc/hardware/run_ibm.py --dry-run           # layouts from reported calibration, no QPU time
  python -B ctc/hardware/run_ibm.py [--backend NAME] [--shots 16384]
  python -B ctc/hardware/run_ibm.py --job-id JOB_ID     # fetch a main job submitted earlier

A full run is two jobs: a preflight that measures every qubit's readout error (a few seconds),
then one job with all experiments plus readout-calibration circuits on the chosen qubits, with
dynamical decoupling and Pauli twirling. Results go to ctc/hardware/data/ and are analysed at once.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import report  # noqa: E402
from experiments import EXPERIMENTS, build_circuit  # noqa: E402
from layout import choose_layout, preflight_circuits, readout_errors  # noqa: E402
import preregister  # noqa: E402

SUPPRESSION = 'dynamical decoupling (XpXm) + gate and measurement Pauli twirling + readout calibration'


def calibration_circuits(backend, physical, value):
    """Prepare every qubit in `value` on the given physical qubits and measure, for readout correction."""
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
    from qiskit.transpiler import generate_preset_pass_manager
    q, c = QuantumRegister(len(physical), 'q'), ClassicalRegister(len(physical), 'c')
    qc = QuantumCircuit(q, c, name=f'cal{value}')
    if value:
        qc.x(q)
    qc.measure(q, c)
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1, initial_layout=list(physical))
    return pm.run(qc)


def save_and_report(job, backend_name, meta):
    result = job.result()
    n = len(EXPERIMENTS)
    data = dict(backend=backend_name, shots=meta['shots'], job_id=job.job_id(),
                retrieved_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),
                options=SUPPRESSION, preregistration_sha256=meta.get('preregistration_sha256'),
                preflight=meta.get('preflight'), layouts=meta['layouts'], transpiled=meta['transpiled'],
                counts={e.name: result[i].data.c.get_counts() for i, e in enumerate(EXPERIMENTS)},
                calibration={e.name: dict(zeros=result[n + 2 * i].data.c.get_counts(),
                                          ones=result[n + 2 * i + 1].data.c.get_counts())
                             for i, e in enumerate(EXPERIMENTS)})
    out = HERE / 'data' / f'ibm_{backend_name}_{job.job_id()}.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, indent=1), encoding='utf-8')
    text, summary = report(data)
    print(text)
    out.with_name(out.stem + '_report.md').write_text(text + '\n', encoding='utf-8')
    out.with_name(out.stem + '_summary.json').write_text(json.dumps(summary, indent=2, default=float),
                                                         encoding='utf-8')
    print(f'wrote {out}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--backend', help='device name; default: least busy device you can use')
    parser.add_argument('--shots', type=int, default=16384)
    parser.add_argument('--preflight-shots', type=int, default=2048)
    parser.add_argument('--preflight-job', help='reuse the readout preflight of an earlier job instead of a new one')
    parser.add_argument('--max-readout', type=float, default=0.03, help='exclude qubits measured above this')
    parser.add_argument('--job-id', help='retrieve an earlier main job instead of submitting')
    parser.add_argument('--dry-run', action='store_true', help='plan layouts from reported calibration only')
    args = parser.parse_args()

    from qiskit.transpiler import generate_preset_pass_manager
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    service = QiskitRuntimeService()
    if args.job_id:
        job = service.job(args.job_id)
        meta = json.loads((HERE / 'data' / f'pending_{args.job_id}.json').read_text(encoding='utf-8'))
        save_and_report(job, job.backend().name, meta)
        return

    prereg = preregister.check()
    if prereg is None and not args.dry_run:
        sys.exit('PREREGISTRATION.md is missing or out of date: run python -B ctc/hardware/preregister.py first')

    backend = service.backend(args.backend) if args.backend else service.least_busy(operational=True,
                                                                                      simulator=False)
    target = backend.target
    preflight = None
    if args.dry_run:
        readout = [target['measure'][(q,)].error or 1.0 for q in range(backend.num_qubits)]
        print(f'backend: {backend.name}  (dry run: reported readout errors, no QPU time)')
    else:
        if args.preflight_job:
            job0 = service.job(args.preflight_job)
            print(f'backend: {backend.name}  reusing preflight job {job0.job_id()}')
        else:
            print(f'backend: {backend.name}  preflight: measuring readout of all {backend.num_qubits} qubits')
            job0 = SamplerV2(mode=backend).run(preflight_circuits(backend), shots=args.preflight_shots)
            print(f'  preflight job {job0.job_id()}')
        res0 = job0.result()
        readout = readout_errors(res0[0].data.c.get_counts(), res0[1].data.c.get_counts()).tolist()
        reported = [target['measure'][(q,)].error for q in range(backend.num_qubits)]
        disagree = [q for q in range(backend.num_qubits)
                    if reported[q] is not None and readout[q] > max(3 * reported[q], 0.03)]
        print(f'  qubits measured above {args.max_readout:.0%}: '
              f'{sum(r > args.max_readout for r in readout)};  far worse than reported: {disagree}')
        preflight = dict(job_id=job0.job_id(), shots=args.preflight_shots, readout_error=readout,
                         reported_readout_error=reported)

    isa, layouts, info = [], {}, {}
    for e in EXPERIMENTS:
        qc = build_circuit(e)
        phys, score = choose_layout(backend, qc, readout, max_readout=args.max_readout)
        if phys is None:
            sys.exit(f'no acceptable layout for {e.name}')
        pm = generate_preset_pass_manager(backend=backend, optimization_level=3, initial_layout=phys,
                                          seed_transpiler=7)
        t = pm.run(qc)
        final = [int(p) for p in t.layout.final_index_layout()]
        if final != phys:
            sys.exit(f'transpiler moved {e.name} from {phys} to {final}')
        ops = {k: int(v) for k, v in t.count_ops().items()}
        isa.append(t)
        layouts[e.name] = phys
        info[e.name] = dict(depth=t.depth(), ops=ops, physical_qubits=phys,
                            readout=[round(readout[p], 4) for p in phys])
        print(f'  {e.name}: qubits {phys}, readout {info[e.name]["readout"]}, depth {t.depth()}, '
              f'two-qubit gates {sum(v for k, v in ops.items() if k in ("cz", "ecr", "cx"))}')
    pubs = list(isa)                       # the Sampler requires one shot count for the whole job
    for e in EXPERIMENTS:
        pubs += [calibration_circuits(backend, layouts[e.name], v) for v in (0, 1)]
    if args.dry_run:
        print(f'  main job would have {len(pubs)} circuits')
        return

    sampler = SamplerV2(mode=backend)
    sampler.options.dynamical_decoupling.enable = True
    sampler.options.dynamical_decoupling.sequence_type = 'XpXm'
    sampler.options.twirling.enable_gates = True
    sampler.options.twirling.enable_measure = True
    job = sampler.run(pubs, shots=args.shots)
    print(f'submitted job {job.job_id()}; waiting for the result (queue times vary).')
    print(f'If you stop this script, fetch it later with: python -B ctc/hardware/run_ibm.py --job-id {job.job_id()}')
    meta = dict(backend=backend.name, shots=args.shots, transpiled=info, layouts=layouts, preflight=preflight,
                preregistration_sha256=prereg)
    pending = HERE / 'data' / f'pending_{job.job_id()}.json'
    pending.parent.mkdir(exist_ok=True)
    pending.write_text(json.dumps(meta, indent=1), encoding='utf-8')
    save_and_report(job, backend.name, meta)


if __name__ == '__main__':
    main()
