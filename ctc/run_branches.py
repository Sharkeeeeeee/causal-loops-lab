"""SPDX-License-Identifier: MIT. Maps the kappa-beta branch model (branches.py).

Run from the repository root:  python -B ctc/run_branches.py
Writes ctc/output/branches_map.csv and ctc/output/branches_map.png.
Selection strength is plotted as s = 1 - exp(-beta): s = 0 no selection, s = 1 hard selection.
"""
from pathlib import Path
import csv
import json
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from circuits import grandfather, kfk  # noqa: E402
from branches import output_state  # noqa: E402

OUT = HERE / 'output'
EPS, Q, R = 0.05, 0.3, 0.6
GRID = np.linspace(0, 1, 41)
RAMP = ['#cde2fb', '#b7d3f6', '#9ec5f4', '#86b6ef', '#6da7ec', '#5598e7', '#3987e5',
        '#2a78d6', '#256abf', '#1c5cab', '#184f95', '#104281', '#0d366b']  # one hue, light to dark
INK, MUTED = '#2b2b29', '#6b6a63'
SCENARIOS = [('grandfather', f'(a) Grandfather, ε = {EPS}', 'P(action fails)', grandfather(EPS), 'jam'),
             ('kfk_motivated', f'(b) KFK motivated sender, q = {Q}, r = {R}', 'P(bad outcome)',
              kfk(Q, R, 'motivated'), 'outcome')]
CORNERS = [((0, 0), 'D-CTC'), ((1, 1), 'P-CTC'), ((1, 0), 'per-world\nDeutsch'), ((0, 1), 'typical but\nconsistent')]


def beta_of(s):
    return np.inf if s >= 1 else -np.log1p(-s)


def grid_values(circuit, label):
    values = np.full((len(GRID), len(GRID)), np.nan)
    for i, s in enumerate(GRID):
        for j, kappa in enumerate(GRID):
            out = output_state(circuit, kappa, beta_of(s))
            if out is not None:
                values[i, j] = circuit.probability_one(out, label)
    return values


def plot(maps):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    cmap = LinearSegmentedColormap.from_list('ramp', RAMP)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.9), dpi=160)
    for ax, (key, title, quantity, _, _) in zip(axes, SCENARIOS):
        values = maps[key]
        image = ax.imshow(values, origin='lower', extent=(0, 1, 0, 1), cmap=cmap, aspect='auto',
                          vmin=np.nanmin(values), vmax=np.nanmax(values))
        bar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.03)
        bar.set_label(quantity, color=INK, fontsize=9)
        bar.ax.tick_params(labelsize=8, colors=MUTED, labelcolor=INK)
        bar.outline.set_visible(False)
        for (kx, sy), name in CORNERS:
            v = values[-1 if sy else 0, -1 if kx else 0]
            ha = 'right' if kx else 'left'
            va = 'top' if sy else 'bottom'
            ax.annotate(f'{name}\n{v:.3f}', (kx, sy), xytext=(-6 if kx else 6, -6 if sy else 6),
                        textcoords='offset points', ha=ha, va=va, fontsize=8, color=INK,
                        bbox=dict(boxstyle='round,pad=0.25', fc='#fcfcfb', ec='none', alpha=0.9))
        ax.set_xlabel('κ: message lands in its own world (0 = typical world, 1 = own world)', color=INK, fontsize=9)
        ax.set_ylabel('s = 1 − e^(−β): preference for consistent branches', color=INK, fontsize=9)
        ax.set_title(title, loc='left', fontsize=10, color=INK)
        ax.tick_params(colors=MUTED, labelcolor=INK, labelsize=8)
        for side in ax.spines.values():
            side.set_visible(False)
    fig.text(0.01, 0.005, 'Classical toy model built for this project. Bottom edge (s = 0): the world prior is never reweighted.',
             color=MUTED, fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT / 'branches_map.png', facecolor='#fcfcfb')


def main():
    OUT.mkdir(exist_ok=True)
    maps = {key: grid_values(circuit, label) for key, _, _, circuit, label in SCENARIOS}
    with open(OUT / 'branches_map.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(['scenario', 'kappa', 's', 'beta', 'probability'])
        for key in maps:
            for i, s in enumerate(GRID):
                for j, kappa in enumerate(GRID):
                    writer.writerow([key, round(kappa, 4), round(s, 4), beta_of(s), round(float(maps[key][i, j]), 10)])
    plot(maps)
    print(json.dumps({key: {name.replace('\n', ' '): round(float(maps[key][-1 if sy else 0, -1 if kx else 0]), 4)
                            for (kx, sy), name in CORNERS} for key in maps}, indent=1))


if __name__ == '__main__':
    main()
