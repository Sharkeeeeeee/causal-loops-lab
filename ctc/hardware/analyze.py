"""SPDX-License-Identifier: MIT. Compare measured counts with the exact predictions of each rule.

Usage (from the repository root):
  python -B ctc/hardware/analyze.py ctc/hardware/data/<file>.json
"""
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from experiments import (BY_NAME, RULES, consistency_rates, estimate, exact, fringe,  # noqa: E402
                         headline_values)
from preregister import CRITERIA  # noqa: E402

NAMES = {'no_loop': 'no loop', 'p_ctc': 'P-CTC', 'past_preserving': 'past-preserving'}
REPS = 300


def readout_correct(counts, zeros, ones):
    """Tensored readout correction. `zeros` / `ones` are counts from circuits that prepare every
    qubit in 0 / 1 on the same physical qubits. Per clbit i: e0 = P(read 1 | 0), e1 = P(read 0 | 1).
    Inverts the product of 2x2 confusion matrices, clips negative quasi-probabilities and
    renormalises to the original number of shots."""
    def bit_rates(cal, value):
        total = sum(cal.values())
        n = len(next(iter(cal)))
        wrong = np.zeros(n)
        for bitstring, c in cal.items():
            for i, ch in enumerate(reversed(bitstring)):
                wrong[i] += c * (int(ch) != value)
        return wrong / total

    e0, e1 = bit_rates(zeros, 0), bit_rates(ones, 1)
    n = len(e0)
    M = np.ones((1, 1))
    for i in reversed(range(n)):                      # index = sum_i b_i 2^i  (clbit 0 least significant)
        M = np.kron(M, np.array([[1 - e0[i], e1[i]], [e0[i], 1 - e1[i]]]))
    shots = sum(counts.values())
    measured = np.zeros(2 ** n)
    for bitstring, c in counts.items():
        measured[int(bitstring, 2)] += c
    true = np.clip(np.linalg.solve(M, measured / shots), 0, None)
    true = true / true.sum() * shots
    return {format(i, f'0{n}b'): float(v) for i, v in enumerate(true) if v > 0}, dict(e0=e0.tolist(),
                                                                                       e1=e1.tolist())


def _resample(counts, rng):
    keys = list(counts)
    vals = np.array([counts[k] for k in keys], float)
    return dict(zip(keys, rng.multinomial(int(round(vals.sum())), vals / vals.sum())))


def _table(exp, counts):
    measured = estimate(exp, counts)
    return np.array([headline_values(exp, measured[rule]) for rule in RULES])   # [rule, headline]


def _corrected(raw, cal):
    return readout_correct(raw, cal['zeros'], cal['ones'])[0] if cal else raw


def measure(exp, raw, cal, rng):
    """Point estimates [rule, headline] and bootstrap samples [rep, rule, headline]. The bootstrap
    resamples the experiment shots and, if present, both readout calibration circuits."""
    point = _table(exp, _corrected(raw, cal))
    samples = []
    for _ in range(REPS):
        cal_r = dict(zeros=_resample(cal['zeros'], rng), ones=_resample(cal['ones'], rng)) if cal else None
        samples.append(_table(exp, _corrected(_resample(raw, rng), cal_r)))
    return point, np.array(samples)


def report(data):
    corrected = 'calibration' in data
    rng = np.random.default_rng(0)
    lines = [f"backend: {data['backend']}   shots per experiment: {data['shots']}"
             + (f"   job: {data['job_id']}" if data.get('job_id') else ''),
             f"error suppression: {data.get('options', 'none')}",
             'measured = readout-corrected (raw = uncorrected); std from a bootstrap over shots'
             + (' and readout calibration' if corrected else ''), '']
    if data.get('preregistration_sha256'):
        lines += [f"preregistration SHA-256: {data['preregistration_sha256']}", '']
    if data.get('layouts'):
        lines += ['physical qubits: ' + '; '.join(f'{k} {v}' for k, v in data['layouts'].items()), '']
    summary, results = {}, {}
    for name, raw in data['counts'].items():
        exp = BY_NAME[name]
        theory = np.array([headline_values(exp, exact(exp)[rule]) for rule in RULES])
        cal = data['calibration'][name] if corrected else None
        point, samples = measure(exp, raw, cal, rng)
        raw_point = _table(exp, raw)
        std = np.nanstd(samples, axis=0)
        results[name] = dict(exp=exp, theory=theory, point=point, samples=samples)
        header = '| quantity | rule | exact | measured | std |' + (' raw |' if corrected else '')
        lines += [f'## {exp.title}', '', header, '|---|---|---|---|---|' + ('---|' if corrected else '')]
        summary[name] = {}
        for r, rule in enumerate(RULES):
            summary[name][rule] = []
            for h, (label, _, _) in enumerate(exp.headlines):
                summary[name][rule].append(dict(quantity=label, exact=theory[r, h], measured=point[r, h],
                                                std=std[r, h], raw=raw_point[r, h]))
                lines.append(f'| {label} | {NAMES[rule]} | {theory[r, h]:.3f} | {point[r, h]:.3f} | {std[r, h]:.3f} |'
                             + (f' {raw_point[r, h]:.3f} |' if corrected else ''))
        if corrected:
            _, rates = readout_correct(raw, cal['zeros'], cal['ones'])
            lines += ['', 'readout error per clbit, P(1|0): ' + ', '.join(f'{x:.3f}' for x in rates['e0'])
                      + ';  P(0|1): ' + ', '.join(f'{x:.3f}' for x in rates['e1'])]
        lines += ['', '| recorded world | Bell test passed (measured) | exact |', '|---|---|---|']
        for k, meas, ex in consistency_rates(exp, _corrected(raw, cal)):
            lines.append(f'| {k} | {meas:.3f} | {ex:.3f} |')
        lines.append('')

    eraser = None
    if 'eraser_x' in results and 'eraser_y' in results:
        eraser = eraser_section(results)
        lines += eraser['lines']
        summary['eraser_fringe'] = eraser['summary']
    lines += criteria_section(results, eraser, preregistered=bool(data.get('preregistration_sha256')))
    return '\n'.join(lines), summary


def eraser_section(results):
    rx, ry = results['eraser_x'], results['eraser_y']
    lines = ['## Eraser fringe (from the X and Y circuits)', '',
             '| fringe | rule | exact V | measured V | std | exact shift | measured shift | std |',
             '|---|---|---|---|---|---|---|---|']
    out, summary = {}, {}
    for r, rule in enumerate(RULES):
        for h, name in ((2, 'sorted by Bob X = +'), (1, 'whole screen')):
            ev, es = fringe(rx['theory'][r, h], ry['theory'][r, h])
            mv, ms = fringe(rx['point'][r, h], ry['point'][r, h])
            boot = np.array([fringe(a, b) for a, b in zip(rx['samples'][:, r, h], ry['samples'][:, r, h])])
            sv, ss = np.nanstd(boot, axis=0)
            out[(rule, h)] = dict(exact=(ev, es), measured=(mv, ms), boot=boot)
            summary[f'{rule} {name}'] = dict(exact_visibility=ev, measured_visibility=mv, std_visibility=sv,
                                             exact_shift=es, measured_shift=ms, std_shift=ss)
            shift_e = f'{es:.3f}' if ev > 1e-9 else 'n/a'
            lines.append(f'| {name} | {NAMES[rule]} | {ev:.3f} | {mv:.3f} | {sv:.3f} | {shift_e} | {ms:.3f} | {ss:.3f} |')
    lines.append('')
    return dict(lines=lines, values=out, summary=summary)


def criteria_section(results, eraser, preregistered=True):
    c = CRITERIA
    pp, pc = RULES.index('past_preserving'), RULES.index('p_ctc')
    title = ('## Preregistered criteria' if preregistered else
             '## Criteria (applied after the fact: this run was not preregistered)')
    lines = [title, '', '| criterion | quantity | value | result |', '|---|---|---|---|']
    verdicts = []
    for name, res in results.items():
        exp = res['exp']
        for h, (label, _, _) in enumerate(exp.headlines):
            gap = res['theory'][pp, h] - res['theory'][pc, h]
            if abs(gap) >= c['discrimination_min_gap']:
                diff = res['point'][pp, h] - res['point'][pc, h]
                z = diff / np.nanstd(res['samples'][:, pp, h] - res['samples'][:, pc, h])
                ok = np.sign(diff) == np.sign(gap) and abs(z) >= c['discrimination_min_z']
                verdicts.append(ok)
                lines.append(f'| C1 | {name}: {label} | PP - P-CTC = {diff:+.3f} (exact {gap:+.3f}), z = {z:.1f} | '
                             f'{"PASS" if ok else "FAIL"} |')
    for name, res in results.items():
        for h, (label, _, _) in enumerate(res['exp'].headlines):
            err = res['point'][pp, h] - res['theory'][pp, h]
            ok = abs(err) <= c['accuracy_tolerance']
            verdicts.append(ok)
            lines.append(f'| C2 | {name}: {label} | measured - exact = {err:+.3f} | {"PASS" if ok else "FAIL"} |')
    if eraser:
        v = eraser['values']
        (ev, es), (mv, ms) = v[('past_preserving', 2)]['exact'], v[('past_preserving', 2)]['measured']
        nl = v[('no_loop', 2)]
        z = (mv - nl['measured'][0]) / np.nanstd(v[('past_preserving', 2)]['boot'][:, 0] - nl['boot'][:, 0])
        checks = [(f'sorted visibility {mv:.3f} (>= {c["eraser_min_visibility"]})', mv >= c['eraser_min_visibility']),
                  (f'shift {ms:.3f} rad (exact {es:.3f}, tol {c["eraser_shift_tolerance"]})',
                   abs(ms - es) <= c['eraser_shift_tolerance']),
                  (f'visibility over no loop: z = {z:.1f} (>= {c["eraser_min_z_over_no_loop"]})',
                   z >= c['eraser_min_z_over_no_loop'])]
        for text, ok in checks:
            verdicts.append(ok)
            lines.append(f'| C3 | eraser: {text} | | {"PASS" if ok else "FAIL"} |')
    lines += ['', f'**{sum(verdicts)} of {len(verdicts)} checks pass.**', '']
    return lines


def main():
    path = Path(sys.argv[1])
    data = json.loads(path.read_text(encoding='utf-8'))
    text, summary = report(data)
    print(text)
    out = path.with_name(path.stem + '_report.md')
    out.write_text(text + '\n', encoding='utf-8')
    path.with_name(path.stem + '_summary.json').write_text(json.dumps(summary, indent=2, default=float),
                                                           encoding='utf-8')
    print(f'wrote {out}')


if __name__ == '__main__':
    main()
