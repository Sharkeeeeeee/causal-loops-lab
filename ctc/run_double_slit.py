"""SPDX-License-Identifier: MIT. Double slit with a time loop under five rules.

Run from the repository root:  python -B ctc/run_double_slit.py
Writes ctc/output/double_slit.json and ctc/output/double_slit.png.
"""
from pathlib import Path
import json
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from double_slit import (THETAS, ctc_double_slit, idler_conditional, pattern, run_entangled, run_fresh,  # noqa: E402
                         summarize, trace_out_last)

OUT = HERE / 'output'
INK, MUTED, GRID_INK, SURFACE = '#2b2b29', '#6b6a63', '#e4e3dd', '#fcfcfb'
# Color follows the rule in both panels (validated categorical slots 1-6; secondary encoding: line style + legend).
STYLE = {'no_loop': ('No time machine', '#2a78d6', '-'),
         'd_ctc': ('D-CTC', '#eb6834', '-'),
         't_ctc': ('T-CTC', '#1baf7a', '-'),
         'p_ctc': ('P-CTC', '#eda100', '-'),
         'past_X': ('Past-preserving (record basis X)', '#e87ba4', (0, (5, 3))),
         'past_Z': ('Past-preserving (record basis Z)', '#008300', (0, (1, 2)))}
PHI = np.pi / 2


def r(x):
    if x is None:
        return None
    if isinstance(x, dict):
        return {k: r(v) for k, v in x.items()}
    return round(float(x), 10) + 0.0


def plot():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    c = ctc_double_slit(0.5, PHI)
    x = THETAS / np.pi
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.9), dpi=160, sharey=True)
    fig.patch.set_facecolor(SURFACE)
    panels = [(axes[0], '(a) Fresh photon: the whole screen', ('no_loop', 'd_ctc', 't_ctc', 'p_ctc'),
               lambda rule: run_fresh(c, rule)),
              (axes[1], "(b) Photon entangled with Bob's idler: hits where Bob later finds X = +",
               ('no_loop', 'd_ctc', 'p_ctc', 'past_X', 'past_Z'),
               lambda rule: idler_conditional(run_entangled(c, rule), 'X+'))]
    for ax, title, rules, get in panels:
        ax.set_facecolor(SURFACE)
        for rule in rules:
            label, color, ls = STYLE[rule]
            if ax is axes[0] and rule == 'p_ctc':
                label = 'P-CTC = past-preserving (pure photon)'
            ax.plot(x, pattern(get(rule)), color=color, lw=2, ls=ls, label=label, zorder=3)
        ax.set_title(title, loc='left', fontsize=10, color=INK)
        ax.set_xlabel('Screen position (phase between the two paths, in units of π)', color=INK, fontsize=9)
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 1.34)
        ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        ax.grid(True, axis='y', color=GRID_INK, lw=0.8)
        ax.tick_params(colors=MUTED, labelcolor=INK, labelsize=8)
        for side in ax.spines.values():
            side.set_visible(False)
        legend = ax.legend(loc='upper center', fontsize=7.8, frameon=False, ncol=2)
        for text in legend.get_texts():
            text.set_color(INK)
    axes[0].set_ylabel('Probability of a hit here (relative)', color=INK, fontsize=9)
    marginal = pattern(trace_out_last(run_entangled(c, 'past_X'), 2, 2))
    axes[1].plot(x, marginal, color=MUTED, lw=1, zorder=2)
    axes[1].annotate('all hits, every rule: flat (gray)', (1.15, 0.5), xytext=(0, 5),
                     textcoords='offset points', ha='center', va='bottom', fontsize=8, color=MUTED)
    fig.text(0.01, 0.035, "Panel (b): P-CTC (yellow) and past-preserving X (pink dashed) give the same sorted fringes, "
             "but P-CTC also changes Bob's own statistics by 0.167 (signalling); past-preserving changes them by 0.",
             color=INK, fontsize=8)
    fig.text(0.01, 0.008, 'Loop: a message from the future adds a phase π/2 to the right path. Qubit toy model; '
             'numbers in ctc/output/double_slit.json.', color=MUTED, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.065, 1, 1))
    fig.savefig(OUT / 'double_slit.png', facecolor=SURFACE)


def main():
    OUT.mkdir(exist_ok=True)
    data = {}
    for key, phi in (('phi=pi/2', np.pi / 2), ('phi=pi', np.pi)):
        s = summarize(phi)
        data[key] = {part: {rule: r(v) for rule, v in rows.items()} for part, rows in s.items()}
    (OUT / 'double_slit.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    plot()
    print(json.dumps(data['phi=pi/2'], indent=1))


if __name__ == '__main__':
    main()
