"""SPDX-License-Identifier: MIT. Compare the loop model with published Born-rule (Sorkin) tests.

For each published bound on |kappa_3| and each loop phase phi (one of three paths coupled), find the
largest fraction eps of particles that could couple to a loop without exceeding the bound. Also
show what a direct two-path population test would reach (projection, not existing data).

Usage (from the repository root):  python -B ctc/born_rule/compare.py
Writes ctc/born_rule/results.json and ctc/output/born_rule_bounds.png (+ _dark.png).
"""
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from model import BOUNDS, max_eps, sorkin_kappa, two_path_shift  # noqa: E402

OUT = HERE.parents[1] / 'ctc' / 'output'
PHIS = np.linspace(0.02, np.pi - 1e-3, 160)
PROJECTED = [1e-4]                # precision of a future, better direct test
CONTROL = HERE / 'data' / 'control_ibm_kingston_dc1k84ts2omc738anop0.json'   # this work, physical control


def two_path_max_eps(precision, phi):
    shift = abs(two_path_shift(0.5, phi, 1.0))
    return min(1.0, precision / shift) if shift > 0 else 1.0


def compute():
    small = [sorkin_kappa(1.0, [0, 0, p]) / p ** 4 for p in (1e-2, 3e-2)]
    curves = {b['name']: [max_eps(b['value'], [0, 0, p]) for p in PHIS] for b in BOUNDS}
    projected = {f'direct population test at {pr:g}': [two_path_max_eps(pr, p) for p in PHIS] for pr in PROJECTED}
    measured = None
    if CONTROL.exists():
        a = json.loads(CONTROL.read_text(encoding='utf-8'))['analysis']
        measured = dict(bound95=a['S_bound95'], S=a['S_mean'], se=a['se_used'],
                        curve=[two_path_max_eps(a['S_bound95'], p) for p in PHIS])
        kauten = np.array(curves[BOUNDS[0]['name']])
        better = np.array(measured['curve']) < kauten
        measured['phi_unconstrained_at_eps1'] = float(np.sqrt(16 * a['S_bound95']))
        measured['stronger_than_kauten_phi_range'] = ([float(PHIS[better].min()), float(PHIS[better].max())]
                                                      if better.any() else None)
    table = []
    for phi in (np.pi / 4, np.pi / 2, 3 * np.pi / 4, np.pi - 1e-3):
        row = dict(phi=float(phi), kappa_at_eps1=sorkin_kappa(1.0, [0, 0, phi]),
                   two_path_shift_at_eps1=two_path_shift(0.5, phi, 1.0))
        row.update({b['name']: max_eps(b['value'], [0, 0, phi]) for b in BOUNDS})
        table.append(row)
    unconstrained = {b['name']: float(next(p for p, e in zip(PHIS, curves[b['name']]) if e < 1.0))
                     for b in BOUNDS if min(curves[b['name']]) < 1.0}
    return dict(kappa_small_phi_coefficient=float(np.mean(small)), phis=PHIS.tolist(), curves=curves,
                projected=projected, measured=measured, table=table, phi_where_bound_starts=unconstrained,
                bounds=BOUNDS)


THEMES = {
    'light': dict(surface='#fcfcfb', text='#0b0b0b', secondary='#52514e', muted='#898781', grid='#e1e0d9',
                  series=['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4']),
    'dark': dict(surface='#1a1a19', text='#f0efec', secondary='#c3c2b7', muted='#898781', grid='#2c2c2a',
                 series=['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181']),
}


def plot(res, theme, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    t = THEMES[theme]
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
    fig, ax = plt.subplots(figsize=(9.6, 6.0), dpi=200)
    fig.patch.set_facecolor(t['surface'])
    ax.set_facecolor(t['surface'])
    phis = np.array(res['phis'])
    labels = ['Kauten 2017, laser', 'Kauten 2017, single photons', 'NV spin / NMR (~1e-3)', 'Sinha 2010']
    for (name, eps), color, label in zip(res['curves'].items(), t['series'], labels):
        eps = np.array(eps)
        ax.plot(phis, eps, color=color, lw=2, label=label, zorder=3)
    if res.get('measured'):
        ax.plot(phis, res['measured']['curve'], color=t['series'][4], lw=2.8, zorder=4,
                label='this work: IBM pure-vs-recorded test (95%)')
    for (name, eps), ls in zip(res['projected'].items(), ('--', ':')):
        ax.plot(phis, eps, color=t['muted'], lw=2, ls=ls, zorder=2,
                label=name.replace('direct population test at', 'projected: pure-vs-recorded test, precision'))
    ax.fill_between(phis, np.array(res['curves'][BOUNDS[0]['name']]), 1.0, color=t['series'][0], alpha=0.10, lw=0)
    ax.text(2.55, 0.25, 'excluded by\nKauten 2017 (laser)', color=t['secondary'], fontsize=9, ha='center')
    ax.set_yscale('log')
    ax.set_ylim(1e-4, 1.4)
    ax.set_xlim(0, np.pi)
    ax.set_xticks([0, np.pi / 4, np.pi / 2, 3 * np.pi / 4, np.pi])
    ax.set_xticklabels(['0', 'π/4', 'π/2', '3π/4', 'π'])
    ax.set_xlabel('loop phase φ on one path', color=t['secondary'])
    ax.set_ylabel('largest allowed fraction ε of particles\ncoupled to a loop', color=t['secondary'])
    ax.tick_params(colors=t['muted'], length=0)
    ax.grid(color=t['grid'], lw=1)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)
    leg = ax.legend(loc='lower left', frameon=False, fontsize=8.5)
    for txt in leg.get_texts():
        txt.set_color(t['text'])
    fig.suptitle('Isolated pure states: microscopic loops vs Born-rule tests', x=0.02, ha='left',
                 color=t['text'], fontsize=13, fontweight='bold', y=0.98)
    fig.text(0.02, 0.925, 'Solid: published Sorkin bounds (2σ) and the direct test of this work (95%). '
             'Area above a line is excluded. Dashed: a future test.', color=t['secondary'], fontsize=8.5)
    fig.text(0.02, 0.015, 'Model: with probability ε a path couples to a loop with phase φ; past-preserving '
             'selection acts like P-CTC on isolated pure states. Hypothesis, not established physics.',
             color=t['muted'], fontsize=7.5)
    fig.subplots_adjust(left=0.13, right=0.97, top=0.88, bottom=0.14)
    fig.savefig(path, facecolor=t['surface'])
    plt.close(fig)
    print(f'wrote {path}')


def main():
    res = compute()
    (HERE / 'results.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
    print(f'small-phi: kappa_3 ~ {res["kappa_small_phi_coefficient"]:.4f} * eps * phi^4')
    print('phi where each bound starts to constrain eps < 1:', {k: round(v, 3) for k, v in res['phi_where_bound_starts'].items()})
    if res['measured']:
        m = res['measured']
        print(f"this work: |S| < {m['bound95']:.2e} (95%); eps = 1 allowed only for phi < {m['phi_unconstrained_at_eps1']:.3f} rad; "
              f"stronger than Kauten laser for phi in {m['stronger_than_kauten_phi_range']} rad")
    for row in res['table']:
        print(f"phi={row['phi']:.3f}: " + ', '.join(f"{b['name'].split(',')[0]} eps<{row[b['name']]:.2e}" for b in BOUNDS))
    OUT.mkdir(exist_ok=True)
    plot(res, 'light', OUT / 'born_rule_bounds.png')
    plot(res, 'dark', OUT / 'born_rule_bounds_dark.png')


if __name__ == '__main__':
    main()
