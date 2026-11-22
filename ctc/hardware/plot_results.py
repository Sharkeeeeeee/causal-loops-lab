"""SPDX-License-Identifier: MIT. Figure of the preregistered hardware run: predicted vs measured.

Reads the summary written by analyze.py and draws one row per rule for each key quantity:
a hollow ring at the exact prediction, a filled dot at the measured value (with +/- 2 std),
joined by a thin line. Writes a light and a dark version for the README.

Usage (from the repository root):
  python -B ctc/hardware/plot_results.py [ctc/hardware/data/<run>_summary.json]
"""
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / 'ctc' / 'hardware' / 'data' / 'ibm_ibm_kingston_dc1j37ts2omc738amaa0_summary.json'
OUT = ROOT / 'ctc' / 'output'

THEMES = {   # validated two-slot categorical palette (dataviz reference palette, slots 1-2)
    'light': dict(surface='#fcfcfb', text='#0b0b0b', secondary='#52514e', muted='#898781', grid='#e1e0d9',
                  pp='#2a78d6', pc='#eb6834'),
    'dark': dict(surface='#1a1a19', text='#f0efec', secondary='#c3c2b7', muted='#898781', grid='#2c2c2a',
                 pp='#3987e5', pc='#d95926'),
}
ROWS = [   # (label, experiment, quantity prefix or eraser key)
    ('Grandfather paradox\nP(gun jams)  [past]', 'grandfather', 'P(jam = 1)'),
    ('Refusal\nP(a = 1)  [past]', 'refusal', 'P(a = 1)'),
    ('Refusal: inconsistent history\nP(message logged | a = 1)', 'refusal', 'P(message logged, given a = 1)'),
    ('One-way control\nP(a = 1)  [loop never acts on a]', 'one_way', 'P(a = 1)'),
    ("Eraser: Bob's own statistics\nP(Bob reads which-path = 0)", 'eraser_z', 'P(Bob idler reads Z = 0)'),
    ('Eraser: fringe visibility\nsorted by Bob X = +', 'eraser_fringe', 'sorted by Bob X = +'),
]


def value(summary, exp, key, rule):
    if exp == 'eraser_fringe':
        v = summary[exp][f'{rule} {key}']
        return v['exact_visibility'], v['measured_visibility'], v['std_visibility']
    for row in summary[exp][rule]:
        if row['quantity'].startswith(key):
            return row['exact'], row['measured'], row['std']
    raise KeyError((exp, key, rule))


def draw(summary, theme, path):
    t = THEMES[theme]
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
    fig, ax = plt.subplots(figsize=(9.6, 6.4), dpi=200)
    fig.patch.set_facecolor(t['surface'])
    ax.set_facecolor(t['surface'])
    rules = [('past_preserving', 'past-preserving', t['pp'], -0.18), ('p_ctc', 'P-CTC', t['pc'], 0.18)]
    for i, (_, exp, key) in enumerate(ROWS):
        for rule, _, color, dy in rules:
            ex, me, sd = value(summary, exp, key, rule)
            y = i + dy
            ax.plot([ex, me], [y, y], color=color, lw=2, alpha=0.5, solid_capstyle='round', zorder=2)
            ax.errorbar(me, y, xerr=2 * sd, fmt='none', ecolor=color, elinewidth=2, capsize=0, zorder=3)
            ax.plot(ex, y, 'o', ms=10, mfc=t['surface'], mec=color, mew=2, zorder=4)
            ax.plot(me, y, 'o', ms=7.5, mfc=color, mec=t['surface'], mew=2, zorder=5)
            ax.annotate(f'{me:.3f}', (me, y), xytext=(0, 7), textcoords='offset points', ha='center',
                        va='bottom', fontsize=7.5, color=t['secondary'], zorder=6)
    ax.set_yticks(range(len(ROWS)))
    ax.set_yticklabels([r[0] for r in ROWS], color=t['text'], fontsize=9)
    ax.set_ylim(len(ROWS) - 0.45, -0.6)
    ax.set_xlim(-0.03, 1.03)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
    ax.tick_params(axis='x', colors=t['muted'], labelsize=9, length=0)
    ax.tick_params(axis='y', length=0, pad=8)
    ax.grid(axis='x', color=t['grid'], lw=1)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlabel('probability (visibility for the last row)', color=t['secondary'], fontsize=9, labelpad=8)

    handles = [Line2D([], [], ls='', marker='o', ms=7.5, mfc=t['pp'], mec=t['surface'], mew=2, label='past-preserving'),
               Line2D([], [], ls='', marker='o', ms=7.5, mfc=t['pc'], mec=t['surface'], mew=2, label='P-CTC'),
               Line2D([], [], ls='', marker='o', ms=10, mfc=t['surface'], mec=t['muted'], mew=2, label='exact prediction'),
               Line2D([], [], ls='', marker='o', ms=7.5, mfc=t['muted'], mec=t['surface'], mew=2,
                      label='measured (± 2 std)')]
    leg = ax.legend(handles=handles, loc='lower left', bbox_to_anchor=(0, 1.0), ncol=4, frameon=False,
                    fontsize=9, handletextpad=0.4, columnspacing=1.6)
    for text in leg.get_texts():
        text.set_color(t['text'])
    fig.suptitle('Time-loop rules on IBM quantum hardware: predicted vs measured', x=0.02, ha='left',
                 color=t['text'], fontsize=13, fontweight='bold', y=0.985)
    fig.text(0.02, 0.935, 'ibm_kingston, job dc1j37ts2omc738amaa0, 16384 shots per circuit, readout-corrected. '
             'Preregistered: 21 of 21 criteria pass.', color=t['secondary'], fontsize=9, ha='left')
    fig.text(0.02, 0.015, 'Both rules are computed from the same shots by postselection: this shows the predictions '
             'are measurable, not which rule nature uses.', color=t['muted'], fontsize=8, ha='left')
    fig.subplots_adjust(left=0.30, right=0.97, top=0.84, bottom=0.12)
    fig.savefig(path, facecolor=t['surface'])
    plt.close(fig)
    print(f'wrote {path}')


def main():
    summary = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT).read_text(encoding='utf-8'))
    OUT.mkdir(exist_ok=True)
    draw(summary, 'light', OUT / 'hardware_results.png')
    draw(summary, 'dark', OUT / 'hardware_results_dark.png')


if __name__ == '__main__':
    main()
