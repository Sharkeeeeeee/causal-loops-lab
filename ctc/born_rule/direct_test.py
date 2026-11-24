"""SPDX-License-Identifier: MIT. Direct test: does an isolated pure superposition give the same
probabilities as the same superposition after it has been recorded?

On each of many disjoint qubit pairs (q, r):
  group A (isolated): RY(theta) on q; measure q and r
  group B (recorded): RY(theta) on q; CNOT q -> r (r records q in Z); measure q and r
with theta in {0, +pi/2, -pi/2, +pi, -pi}. Delta(theta) = P_A(q = 1) - P_B(q = 1).

Signal S = [Delta(+pi/2) + Delta(-pi/2)] / 2 - [Delta(0) + (Delta(+pi) + Delta(-pi)) / 2] / 2.
  - Standard quantum mechanics with ANY linear noise after the preparation (gate errors, decay,
    crosstalk, readout error): S = 0 exactly. The endpoints remove the CNOT's own population error;
    the +/- pairs cancel errors that turn coherence into population (ctc/tests/test_born_direct.py).
  - A miscalibrated RY leaves S_prep = (b - a)(p_h - p_pi / 2), first order in the miscalibration
    (the +/- pi pair removes the stray coherence an over-rotated pi pulse leaves).
    It is estimated from the data (prep_systematic) and reported next to S.
  - Loop model (ctc/born_rule/model.py, coupling in the Z basis): only the isolated superposition
    is reweighted, so S = two_path_shift(1/2, phi, eps) ~ -+ eps phi^2 / 16.

Usage (from the repository root):
  python -B ctc/born_rule/direct_test.py preregister
  python -B ctc/born_rule/direct_test.py local [--pairs 2]
  python -B ctc/born_rule/direct_test.py ibm --backend NAME [--pairs 24] [--shots 40000] [--dry-run]
  python -B ctc/born_rule/direct_test.py analyze FILE
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
from model import two_path_shift  # noqa: E402

THETAS = {'0': 0.0, '+pi/2': np.pi / 2, '-pi/2': -np.pi / 2, '+pi': np.pi, '-pi': -np.pi}
GROUPS = ('A', 'B')
PREREG = HERE / 'DIRECT_TEST_PREREGISTRATION.md'
DATA = HERE / 'data'
Z_NO_DEVIATION, Z_ANOMALY = 3.0, 5.0


# ---------------------------------------------------------------- circuits

def build(group, theta, n_pairs):
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
    q = QuantumRegister(2 * n_pairs, 'q')
    c = ClassicalRegister(2 * n_pairs, 'c')
    qc = QuantumCircuit(q, c, name=f'{group}_{theta}')
    for i in range(n_pairs):
        if THETAS[theta] != 0:
            qc.ry(THETAS[theta], q[2 * i])
    if group == 'B':
        for i in range(n_pairs):
            qc.cx(q[2 * i], q[2 * i + 1])
    qc.barrier()
    qc.measure(q, c)
    return qc


def circuits(n_pairs):
    return [(g, t, build(g, t, n_pairs)) for g in GROUPS for t in THETAS]


# ---------------------------------------------------------------- analysis

def p_one(counts, pair):
    """P(q = 1) for pair index `pair` (clbit 2*pair, clbit 0 is the rightmost character)."""
    total = ones = 0
    for bits, n in counts.items():
        total += n
        ones += n * int(bits[::-1][2 * pair])
    return ones / total


def signal(p):
    """S from a dict p[(group, theta)] -> P(q = 1)."""
    d = {t: p[('A', t)] - p[('B', t)] for t in THETAS}
    return (d['+pi/2'] + d['-pi/2']) / 2 - (d['0'] + (d['+pi'] + d['-pi']) / 2) / 2


def prep_systematic(p):
    """Estimate of S caused by RY miscalibration: (Delta(pi) - Delta(0)) times the deviation of the
    half-way population from half the full population, both read from group A (readout is affine)."""
    d0 = p[('A', '0')] - p[('B', '0')]
    dpi = (p[('A', '+pi')] - p[('B', '+pi')] + p[('A', '-pi')] - p[('B', '-pi')]) / 2
    m0, mpi = p[('A', '0')], (p[('A', '+pi')] + p[('A', '-pi')]) / 2
    mh = (p[('A', '+pi/2')] + p[('A', '-pi/2')]) / 2
    return (dpi - d0) * (mh - (m0 + mpi) / 2) / (mpi - m0)


def analyze(data):
    n_pairs, shots = data['n_pairs'], data['shots']
    per_pair = []
    for i in range(n_pairs):
        p = {(g, t): p_one(data['counts'][f'{g}_{t}'], i) for g in GROUPS for t in THETAS}
        per_pair.append(dict(pair=i, S=signal(p), prep=prep_systematic(p), p=p))
    s = np.array([x['S'] for x in per_pair])
    mean = float(s.mean())
    prep = float(np.mean([x['prep'] for x in per_pair]))
    se_pairs = float(s.std(ddof=1) / np.sqrt(len(s))) if len(s) > 1 else float('nan')
    # shot-noise-only standard error of the mean S (binomial variances, pairs independent)
    var = 0.0
    for x in per_pair:
        v = {k: x['p'][k] * (1 - x['p'][k]) / shots for k in x['p']}
        var += (v[('A', '+pi/2')] + v[('B', '+pi/2')] + v[('A', '-pi/2')] + v[('B', '-pi/2')]) / 4
        var += (v[('A', '0')] + v[('B', '0')]) / 4
        var += (v[('A', '+pi')] + v[('B', '+pi')] + v[('A', '-pi')] + v[('B', '-pi')]) / 16
    se_shots = float(np.sqrt(var) / len(per_pair))
    se = max(se_pairs, se_shots) if np.isfinite(se_pairs) else se_shots
    z = mean / se
    bound95 = abs(mean) + 1.96 * se
    verdict = ('no deviation' if abs(z) < Z_NO_DEVIATION else
               'anomaly (error hunt and replication required)' if abs(z) >= Z_ANOMALY else 'inconclusive')
    return dict(S_mean=mean, se_pairs=se_pairs, se_shots=se_shots, se_used=se, z=z, S_bound95=bound95,
                verdict=verdict, prep_systematic=prep,
                per_pair=[dict(pair=x['pair'], S=x['S'], prep=x['prep'],
                                                p={f'{k[0]}_{k[1]}': v for k, v in x['p'].items()})
                                           for x in per_pair])


def eps_max_curve(bound, phis):
    return [min(1.0, bound / abs(two_path_shift(0.5, phi, 1.0))) for phi in phis]


# ---------------------------------------------------------------- preregistration

def prereg_text():
    return f"""# Preregistration: direct pure-vs-recorded test

Fixed before the hardware job is submitted; its SHA-256 is stored with the results.

## Circuits

On each of many disjoint qubit pairs (q, r), group A (isolated): RY(theta) on q, measure q and r.
Group B (recorded): RY(theta) on q, CNOT q -> r, measure q and r. theta in {{0, +pi/2, -pi/2, +pi, -pi}}.
Ten circuits, all pairs in parallel, the same number of shots each. No twirling, no dynamical
decoupling, no readout correction: the signal is built to cancel linear errors instead.

## Signal

Delta(theta) = P_A(q=1) - P_B(q=1);  S = [Delta(+pi/2) + Delta(-pi/2)]/2 - [Delta(0) + (Delta(+pi) + Delta(-pi))/2]/2,
computed per pair and averaged over pairs.

## Predictions

- Standard quantum mechanics, with any linear noise after the preparation: S = 0. A miscalibrated RY
  adds S_prep = (b - a)(p_h - p_pi/2), estimated from group A and reported as prep_systematic; it does
  not enter the decision unless |prep_systematic| exceeds one standard error, in which case S - prep_systematic
  is also reported.
- Loop model with Z-basis coupling (ctc/born_rule/model.py): S = eps [w/(1+w) - 1/2], w = cos^2(phi/2),
  about -/+ eps phi^2/16 (sign depends on which basis state is coupled).

## Decision rules

- Standard error: the larger of (a) pair-to-pair spread / sqrt(pairs) and (b) shot noise.
- |z| < {Z_NO_DEVIATION}: no deviation. Report the 95% bound |S| < |S_mean| + 1.96 SE and the resulting
  limit eps < bound / |w/(1+w) - 1/2| for each phi.
- {Z_NO_DEVIATION} <= |z| < {Z_ANOMALY}: inconclusive; report as such.
- |z| >= {Z_ANOMALY}: anomaly. Before any interpretation: rerun on other qubits and another device, and look
  for nonlinear hardware effects (for example readout saturation, leakage), which this design does not cancel.

## Known limits

- The test probes loops that couple in the Z basis and act while the state is isolated at measurement.
- The model's timing is not fixed: in group B the qubit is also isolated for the short time before the
  CNOT. If loops act then too, the predicted S is reduced by the fraction of exposure B shares with A.
- Nonlinear hardware effects are not cancelled.
"""


def prereg_check():
    if not PREREG.exists():
        return None
    content = PREREG.read_text(encoding='utf-8')
    return hashlib.sha256(content.encode('utf-8')).hexdigest() if content == prereg_text() else None


# ---------------------------------------------------------------- running

def choose_pairs(backend, n_pairs, readout, max_readout=0.03, max_gate=0.01):
    from layout import two_qubit_error
    target = backend.target
    edges = []
    for a, b in backend.coupling_map.get_edges():
        if a < b or (b, a) not in set(backend.coupling_map.get_edges()):
            err = two_qubit_error(target, a, b)
            if err is None or err > max_gate or readout[a] > max_readout or readout[b] > max_readout:
                continue
            edges.append((readout[a] + readout[b] + err, a, b))
    used, pairs = set(), []
    for _, a, b in sorted(edges):
        if a not in used and b not in used:
            pairs.append((a, b))
            used |= {a, b}
        if len(pairs) == n_pairs:
            break
    if len(pairs) < n_pairs:
        raise RuntimeError(f'only {len(pairs)} good pairs available')
    return pairs


def save(data, name):
    DATA.mkdir(exist_ok=True)
    data['analysis'] = analyze(data)
    out = DATA / name
    out.write_text(json.dumps(data, indent=1), encoding='utf-8')
    a = data['analysis']
    print(f"S = {a['S_mean']:+.2e} +/- {a['se_used']:.2e}  (pairs SE {a['se_pairs']:.2e}, shots SE "
          f"{a['se_shots']:.2e}), z = {a['z']:+.2f}  ->  {a['verdict']}; 95% bound |S| < {a['S_bound95']:.2e}; "
          f"prep systematic estimate {a['prep_systematic']:+.2e}")
    print(f'wrote {out}')
    return out


def run_local(n_pairs, shots):
    from qiskit.primitives import StatevectorSampler
    circs = circuits(n_pairs)
    res = StatevectorSampler(seed=5).run([c for _, _, c in circs], shots=shots).result()
    data = dict(backend='qiskit StatevectorSampler (ideal)', n_pairs=n_pairs, shots=shots,
                counts={f'{g}_{t}': res[i].data.c.get_counts() for i, (g, t, _) in enumerate(circs)})
    return save(data, 'direct_local_ideal.json')


def run_ibm(backend_name, n_pairs, shots, dry_run, preflight_job):
    sys.path.insert(0, str(HERE.parent / 'hardware'))
    from qiskit.transpiler import generate_preset_pass_manager
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from layout import readout_errors
    prereg = prereg_check()
    if prereg is None and not dry_run:
        sys.exit('DIRECT_TEST_PREREGISTRATION.md missing or out of date: run the preregister command first')
    service = QiskitRuntimeService()
    backend = service.backend(backend_name)
    readout = [backend.target['measure'][(q,)].error or 1.0 for q in range(backend.num_qubits)]
    if preflight_job:
        r0 = service.job(preflight_job).result()
        measured = readout_errors(r0[0].data.c.get_counts(), r0[1].data.c.get_counts())
        readout = [max(a, b) for a, b in zip(readout, measured)]
    pairs = choose_pairs(backend, n_pairs, readout)
    layout = [x for pair in pairs for x in pair]
    isa = []
    for g, t, qc in circuits(n_pairs):
        pm = generate_preset_pass_manager(backend=backend, optimization_level=1, initial_layout=layout,
                                          seed_transpiler=7)
        tc = pm.run(qc)
        if [int(p) for p in tc.layout.final_index_layout()] != layout:
            sys.exit(f'transpiler moved qubits in {g}_{t}')
        isa.append((g, t, tc))
    two_q = {f'{g}_{t}': sum(v for k, v in tc.count_ops().items() if k in ('cz', 'ecr', 'cx')) for g, t, tc in isa}
    print(f'backend {backend.name}; {n_pairs} pairs {pairs}; two-qubit gates per circuit {two_q}')
    print(f'{len(isa)} circuits x {shots} shots = {len(isa) * shots} shots')
    if dry_run:
        return
    job = SamplerV2(mode=backend).run([tc for _, _, tc in isa], shots=shots)
    print(f'submitted job {job.job_id()}; waiting')
    res = job.result()
    data = dict(backend=backend.name, job_id=job.job_id(), n_pairs=n_pairs, shots=shots, pairs=pairs,
                preregistration_sha256=prereg, preflight_job=preflight_job,
                retrieved_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),
                counts={f'{g}_{t}': res[i].data.c.get_counts() for i, (g, t, _) in enumerate(isa)})
    return save(data, f'direct_{backend.name}_{job.job_id()}.json')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('preregister', 'local', 'ibm', 'analyze'))
    parser.add_argument('file', nargs='?')
    parser.add_argument('--backend', default='ibm_kingston')
    parser.add_argument('--pairs', type=int, default=24)
    parser.add_argument('--shots', type=int, default=40000)
    parser.add_argument('--preflight-job')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.command == 'preregister':
        PREREG.write_text(prereg_text(), encoding='utf-8', newline='\n')
        print(f'SHA-256 {hashlib.sha256(prereg_text().encode("utf-8")).hexdigest()}  ({PREREG})')
    elif args.command == 'local':
        run_local(min(args.pairs, 3), min(args.shots, 20000))
    elif args.command == 'ibm':
        run_ibm(args.backend, args.pairs, args.shots, args.dry_run, args.preflight_job)
    else:
        data = json.loads(Path(args.file).read_text(encoding='utf-8'))
        save(data, Path(args.file).name)


if __name__ == '__main__':
    main()
