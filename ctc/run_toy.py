"""SPDX-License-Identifier: MIT. Phase-1 toy sweep: how each CTC rule changes the future.

Run from the repository root:  python -B ctc/run_toy.py
Writes ctc/output/toy_results.csv, ctc/output/bootstrap.json and ctc/output/toy_figure.png.
"""
from pathlib import Path
import csv
import json
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from models import d_ctc, no_loop, p_ctc  # noqa: E402
from circuits import bootstrap, grandfather, kfk  # noqa: E402

OUT = HERE / 'output'
Q = 0.3  # prior probability that the person chooses badly without a reminder

# Categorical slots 1-4 in fixed order; colour follows the rule, never the rank.
COLORS = {'no_loop': '#2a78d6', 'p_ctc': '#eb6834', 'd_ctc': '#1baf7a', 'unconditional': '#eda100'}
INK, MUTED, GRID = '#2b2b29', '#6b6a63', '#e4e3df'


def evaluate(c, label):
    base = no_loop(c.U, c.rho, c.d_cr, c.d_loop, c.baseline_loop)
    post, weight = p_ctc(c.U, c.rho, c.d_cr, c.d_loop)
    deutsch, _, _ = d_ctc(c.U, c.rho, c.d_cr, c.d_loop)
    return dict(no_loop=c.probability_one(base, label),
                p_ctc=None if post is None else c.probability_one(post, label),
                p_ctc_weight=weight,
                d_ctc=c.probability_one(deutsch, label))


def sweep():
    rows = []
    for eps in np.geomspace(1e-4, 0.5, 41):
        rows.append(dict(scenario='grandfather', parameter='eps', value=float(eps),
                         **evaluate(grandfather(eps), 'jam')))
    for r in np.linspace(0, 1, 41):
        for mode in ('motivated', 'unconditional'):
            rows.append(dict(scenario='kfk_' + mode, parameter='r', value=float(r),
                             **evaluate(kfk(Q, r, mode), 'outcome')))
    return rows


def bootstrap_summary():
    c = bootstrap()
    base = no_loop(c.U, c.rho, c.d_cr, c.d_loop, c.baseline_loop)
    post, _ = p_ctc(c.U, c.rho, c.d_cr, c.d_loop)
    deutsch, _, _ = d_ctc(c.U, c.rho, c.d_cr, c.d_loop)
    return {name: dict(p_record_1=round(c.probability_one(s, 'record'), 12),
                       x_expectation=round(c.expectation_x(s, 'record'), 12))
            for name, s in [('no_loop', base), ('p_ctc', post), ('d_ctc', deutsch)]}


def style(ax):
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelcolor=INK, labelsize=9)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def plot(rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.4), dpi=160)
    g = [r for r in rows if r['scenario'] == 'grandfather']
    x = [r['value'] for r in g]
    a.plot(x, [r['no_loop'] for r in g], color=COLORS['no_loop'], lw=2, label='No loop')
    a.plot(x, [r['p_ctc'] for r in g], color=COLORS['p_ctc'], lw=2, label='P-CTC')
    a.plot(x, [r['d_ctc'] for r in g], color=COLORS['d_ctc'], lw=2, ls=(0, (4, 3)),
           marker='o', ms=4, markevery=5, label='D-CTC (same as no loop)')
    a.set_xscale('log')
    a.set_ylim(-0.03, 1.08)
    a.set_xlabel('Prior failure probability ε', color=INK)
    a.set_ylabel('P(action fails)', color=INK)
    a.set_title('(a) Grandfather paradox: send back NOT of what you received',
                loc='left', fontsize=10, color=INK)
    a.annotate('P-CTC: failure becomes certain', (1.3e-4, 1.0), (1.3e-4, 0.86),
               color=INK, fontsize=8.5)
    a.annotate('No loop / D-CTC: failure stays at ε', (1.3e-4, 0.0), (1.3e-4, 0.07),
               color=INK, fontsize=8.5)

    m = [r for r in rows if r['scenario'] == 'kfk_motivated']
    u = [r for r in rows if r['scenario'] == 'kfk_unconditional']
    x = [r['value'] for r in m]
    b.plot(x, [r['no_loop'] for r in m], color=COLORS['no_loop'], lw=2, label='No message (baseline)')
    b.plot(x, [r['p_ctc'] for r in m], color=COLORS['p_ctc'], lw=2, label='Motivated sender, P-CTC')
    b.plot(x, [r['d_ctc'] for r in m], color=COLORS['d_ctc'], lw=2, ls=(0, (4, 3)),
           marker='o', ms=4, markevery=5, label='Motivated sender, D-CTC')
    b.plot(x, [r['p_ctc'] for r in u], color=COLORS['unconditional'], lw=2, ls=(0, (1, 2)),
           label='Unconditional sender (both rules)')
    b.set_ylim(-0.02, 0.36)
    b.set_xlabel('Reminder effectiveness r', color=INK)
    b.set_ylabel('P(bad outcome)', color=INK)
    b.set_title(f'(b) KFK-type reminder to one person (prior q = {Q})',
                loc='left', fontsize=10, color=INK)
    b.annotate('motivated, D-CTC', (1.0, Q / (1 + Q)), (0.70, 0.255), color=INK, fontsize=8.5)

    for ax in (a, b):
        style(ax)
        ax.legend(frameon=False, fontsize=8.5, labelcolor=INK, loc='center left' if ax is a else 'lower left')
    fig.text(0.01, 0.005, 'Toy models, exact numerics. Not evidence that information can reach the past.',
             color=MUTED, fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT / 'toy_figure.png', facecolor='#fcfcfb')


def main():
    OUT.mkdir(exist_ok=True)
    rows = sweep()
    with open(OUT / 'toy_results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    boot = bootstrap_summary()
    (OUT / 'bootstrap.json').write_text(json.dumps(boot, indent=2) + '\n', encoding='utf-8')
    plot(rows)
    print(json.dumps({'rows': len(rows), 'bootstrap': boot}, indent=2))


if __name__ == '__main__':
    main()
