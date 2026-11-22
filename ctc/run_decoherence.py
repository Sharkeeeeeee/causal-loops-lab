"""SPDX-License-Identifier: MIT. Decoherence choosing the record basis: sweeps and figure.

Run from the repository root:  python -B ctc/run_decoherence.py
Writes ctc/output/decoherence.json and ctc/output/decoherence.png.
"""
from pathlib import Path
import json
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from decoherence import (environment_coherence, fringe_shift, marginal, record_probabilities, run,  # noqa: E402
                         sorted_by_bob, visibility)

OUT = HERE / 'output'
INK, MUTED, GRID_INK, SURFACE = '#2b2b29', '#6b6a63', '#e4e3dd', '#fcfcfb'
BLUE, AQUA, YELLOW, PINK, GREEN = '#2a78d6', '#1baf7a', '#eda100', '#e87ba4', '#008300'
PHI = np.pi / 2
S_GRID = np.linspace(0, 1, 101)


def r(x):
    return None if x is None else round(float(x), 10) + 0.0


def fresh_curve(rule, n_env):
    vals = []
    for s in S_GRID:
        out, _, d_b, d_e = run(rule, PHI, bob=False, s=s, n_env=n_env)
        vals.append(marginal(out, d_b, d_e, 'S')[1, 1].real)
    return np.array(vals)


def eraser_curve(rule, pointer):
    vals, amb_at = [], []
    for s in S_GRID:
        out, amb, d_b, d_e = run(rule, PHI, s=s, pointer=pointer)
        vals.append(visibility(sorted_by_bob(out, d_b, d_e)))
        amb_at.append(bool(amb))
    return np.array(vals), amb_at


def table():
    rows = {}
    for s in (0.0, 0.01, 0.1, 0.5, 1.0):
        row = {}
        for rule in ('no_loop', 'p_ctc', 'env_record'):
            base, _, d_b, d_e = run('no_loop', PHI, bob=False, s=s)
            out, amb, _, _ = run(rule, PHI, bob=False, s=s)
            row[f'fresh_{rule}'] = dict(
                P_right=r(marginal(out, d_b, d_e, 'S')[1, 1].real),
                record_change=r(0.5 * np.sum(abs(record_probabilities(out, d_b, d_e)
                                                 - record_probabilities(base, d_b, d_e)))),
                environment_coherence=r(environment_coherence(out, d_b, d_e)))
            for pointer in ('Z', 'X'):
                base, _, d_b, d_e = run('no_loop', PHI, s=s, pointer=pointer)
                out, amb, _, _ = run(rule, PHI, s=s, pointer=pointer)
                hits = sorted_by_bob(out, d_b, d_e)
                bob = marginal(out, d_b, d_e, 'B') - marginal(base, d_b, d_e, 'B')
                row[f'eraser_{pointer}env_{rule}'] = dict(
                    sorted_visibility=r(visibility(hits)), sorted_shift=r(fringe_shift(hits)),
                    bob_change=r(0.5 * np.sum(abs(np.linalg.eigvalsh(bob)))), ambiguous=amb)
        rows[f's={s}'] = row
    return rows


def plot():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.9), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    for ax in (a, b):
        ax.set_facecolor(SURFACE)
        ax.grid(True, axis='y', color=GRID_INK, lw=0.8)
        ax.tick_params(colors=MUTED, labelcolor=INK, labelsize=8)
        for side in ax.spines.values():
            side.set_visible(False)
        ax.set_xlim(-0.025, 1)
        ax.set_xlabel('s: strength of the environment\'s which-path record  (0 = none, 1 = perfect copy)',
                      color=INK, fontsize=9)

    a.axhline(0.5, color=BLUE, lw=2, label='No time machine')
    a.axhline(1 / 3, color=YELLOW, lw=2, label='P-CTC (ignores records)')
    for n, color, ls in ((1, PINK, '-'), (3, GREEN, (0, (5, 3)))):
        a.plot(S_GRID, fresh_curve('env_record', n), color=color, lw=2, ls=ls,
               label=f'Decoherence-defined rule, {n} environment qubit{"s" if n > 1 else ""}')
    a.set_ylim(0.25, 0.62)
    a.set_ylabel('P(photon went through the right slit)', color=INK, fontsize=9)
    a.set_title('(a) Fresh photon: how much of the past is still selectable', loc='left', fontsize=10, color=INK)
    a.annotate('past selectable', (0.01, 1 / 3), xytext=(2, -13), textcoords='offset points', fontsize=8, color=MUTED)
    a.annotate('past fixed', (0.99, 0.5), xytext=(-2, 6), textcoords='offset points', ha='right', fontsize=8,
               color=MUTED)

    no_loop_z, _ = eraser_curve('no_loop', 'Z')
    pctc_z, _ = eraser_curve('p_ctc', 'Z')
    rule_z, _ = eraser_curve('env_record', 'Z')
    rule_x, _ = eraser_curve('env_record', 'X')
    b.plot(S_GRID, no_loop_z, color=BLUE, lw=2, label='No time machine (Z environment)')
    b.plot(S_GRID, pctc_z, color=YELLOW, lw=2, label="P-CTC (Z environment): also changes Bob's statistics")
    b.plot(S_GRID[1:], rule_x[1:], color=PINK, lw=2, ls=(0, (5, 3)), label='Decoherence-defined rule, X environment')
    b.plot(S_GRID[1:], rule_z[1:], color=GREEN, lw=2, label='Decoherence-defined rule, Z environment')
    b.plot([0, 0], [0, rule_x[1]], color=INK, lw=1, ls=(0, (1, 2)), zorder=4)
    b.plot([0, 0], [0, rule_x[1]], 'o', ms=8, mfc=SURFACE, mec=INK, mew=1.5, zorder=5)
    b.annotate('s = 0: basis undetermined,\neither value', (0, 0.47), xytext=(8, 0), textcoords='offset points',
               fontsize=8, color=INK, va='center')
    b.set_xlim(-0.025, 1)
    b.set_ylim(-0.03, 1.3)
    b.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    b.set_ylabel("Fringe visibility in hits sorted by Bob's idler (X = +)", color=INK, fontsize=9)
    b.set_title("(b) Photon entangled with Bob's idler (eraser)", loc='left', fontsize=10, color=INK)
    for ax in (a, b):
        legend = ax.legend(loc='upper left' if ax is b else 'upper right', fontsize=7.8, frameon=False)
        for text in legend.get_texts():
            text.set_color(INK)
    fig.text(0.01, 0.01, 'Loop: a message from the future adds a phase π/2 to the right path. The decoherence-defined '
             'rule never changes Bob\'s statistics or the environment\'s record probabilities. Qubit toy model.',
             color=MUTED, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(OUT / 'decoherence.png', facecolor=SURFACE)


def main():
    OUT.mkdir(exist_ok=True)
    data = dict(table=table(), fresh_sweep=dict(s=[r(s) for s in S_GRID],
                                                n_env_1=[r(v) for v in fresh_curve('env_record', 1)],
                                                n_env_3=[r(v) for v in fresh_curve('env_record', 3)]))
    (OUT / 'decoherence.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    plot()
    print(json.dumps(data['table']['s=0.1'], indent=1))


if __name__ == '__main__':
    main()
