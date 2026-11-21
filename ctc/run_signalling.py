"""SPDX-License-Identifier: MIT. No-signalling summary and kappa-beta signalling map.

Run from the repository root:  python -B ctc/run_signalling.py
Writes ctc/output/signalling.json and ctc/output/signalling_map.png.
"""
from pathlib import Path
import json
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from circuits import bootstrap, grandfather, interference, kfk  # noqa: E402
from literature import bhw_bb84  # noqa: E402
from signalling import alice_to_bob, attach_partner, bob_to_alice  # noqa: E402

OUT = HERE / 'output'
GRID = np.linspace(0, 1, 41)
RAMP = ['#cde2fb', '#b7d3f6', '#9ec5f4', '#86b6ef', '#6da7ec', '#5598e7', '#3987e5',
        '#2a78d6', '#256abf', '#1c5cab', '#184f95', '#104281', '#0d366b']
INK, MUTED = '#2b2b29', '#6b6a63'
SCENARIOS = [('grandfather', grandfather(0.05), 'jam'), ('kfk_motivated', kfk(0.3, 0.6, 'motivated'), 'bad'),
             ('kfk_unconditional', kfk(0.3, 0.6, 'unconditional'), 'bad'),
             ('interference', interference(0.5, np.pi), 'a'), ('bootstrap', bootstrap(), 'record')]


def r(x):
    return None if x is None else round(float(x), 10) + 0.0


def beta_of(s):
    return np.inf if s >= 1 else -np.log1p(-s)


def summary():
    table = {}
    for name, c, label in SCENARIOS:
        row = {}
        for mode in ('classical', 'entangled'):
            cb = attach_partner(c, label, mode)
            for rule in ('no_loop', 'p_ctc', 'd_ctc'):
                row[f'{rule}_{mode}'] = r(alice_to_bob(cb, rule))
        if name != 'interference':
            cb = attach_partner(c, label, 'classical')
            for kappa, beta, tag in [(0, 0, 'D'), (1, 0, 'per_world'), (0, np.inf, 'typical_consistent'),
                                     (1, np.inf, 'P'), (0.5, 1.0, 'middle')]:
                row[f'branches_{tag}'] = r(alice_to_bob(cb, 'branches', kappa=kappa, beta=beta))
        table[name] = row
    cb = attach_partner(bhw_bb84(np.eye(2) / 2), 'a', 'entangled')
    bob_to_alice_table = {f'{rule}_{pres}_{basis}': [r(x) for x in np.diag(bob_to_alice(cb, rule, basis, pres)).real]
                          for rule in ('p_ctc', 'd_ctc') for pres in ('global', 'per_branch')
                          if not (rule == 'p_ctc' and pres == 'per_branch') for basis in ('Z', 'X')}
    return dict(alice_to_bob_trace_distance=table, bob_to_alice_bb84_alice_outcomes=bob_to_alice_table)


def plot():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    cmap = LinearSegmentedColormap.from_list('ramp', RAMP)
    panels = [('(a) Grandfather, ε = 0.05: Bob holds a copy of the jam bit', grandfather(0.05), 'jam'),
              ('(b) KFK motivated, q = 0.3, r = 0.6: Bob holds a copy of "bad"', kfk(0.3, 0.6, 'motivated'), 'bad')]
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.9), dpi=160)
    for ax, (title, c, label) in zip(axes, panels):
        cb = attach_partner(c, label, 'classical')
        values = np.zeros((len(GRID), len(GRID)))
        for i, s in enumerate(GRID):
            for j, kappa in enumerate(GRID):
                v = alice_to_bob(cb, 'branches', kappa=kappa, beta=beta_of(s))
                values[i, j] = np.nan if v is None else v
        image = ax.imshow(values, origin='lower', extent=(0, 1, 0, 1), cmap=cmap, aspect='auto', vmin=0,
                          vmax=np.nanmax(values))
        bar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.03)
        bar.set_label("Change in Bob's statistics (trace distance)", color=INK, fontsize=9)
        bar.ax.tick_params(labelsize=8, colors=MUTED, labelcolor=INK)
        bar.outline.set_visible(False)
        ax.annotate('s = 0: exactly zero (no signalling)', (0.5, 0.0), xytext=(0, 8), textcoords='offset points',
                    ha='center', va='bottom', fontsize=8, color=INK,
                    bbox=dict(boxstyle='round,pad=0.25', fc='#fcfcfb', ec='none', alpha=0.9))
        ax.set_xlabel('κ: message lands in its own world', color=INK, fontsize=9)
        ax.set_ylabel('s = 1 − e^(−β): preference for consistent branches', color=INK, fontsize=9)
        ax.set_title(title, loc='left', fontsize=10, color=INK)
        ax.tick_params(colors=MUTED, labelcolor=INK, labelsize=8)
        for side in ax.spines.values():
            side.set_visible(False)
    fig.text(0.01, 0.005, 'Alice chooses whether to run the loop; Bob is far away and only shares a correlated bit. '
             'Classical toy model.', color=MUTED, fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT / 'signalling_map.png', facecolor='#fcfcfb')


def main():
    OUT.mkdir(exist_ok=True)
    data = summary()
    (OUT / 'signalling.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    plot()
    print(json.dumps(data, indent=1))


if __name__ == '__main__':
    main()
