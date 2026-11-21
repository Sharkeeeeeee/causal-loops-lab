"""SPDX-License-Identifier: MIT. Writes the [L11]/[BHW] reproduction numbers and a figure.

Run from the repository root:  python -B ctc/reproduce_literature.py
Outputs ctc/output/literature.json and ctc/output/lloyd_fig4_theory.png.
"""
from pathlib import Path
import json
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from models import d_ctc, p_ctc, p_ctc_success_probability  # noqa: E402
from literature import BB84_CLAIM, KET, bhw_bb84, bhw_two_state, lloyd_grandfather, lloyd_unproved_theorem, pure  # noqa: E402

OUT = HERE / 'output'
COLORS = {'p_ctc': '#eb6834', 'd_ctc': '#1baf7a'}  # same slots as toy_figure.png
INK, MUTED, GRID = '#2b2b29', '#6b6a63', '#e4e3df'


def r(x):
    return round(float(x), 10) + 0.0  # + 0.0 turns -0.0 into 0.0


def collect():
    bb84 = {}
    for label, bits in BB84_CLAIM.items():
        c = bhw_bb84(pure(KET[label]))
        out, tau, mult = d_ctc(c.U, c.rho, c.d_cr, c.d_loop)
        bb84[label] = dict(claimed=''.join(map(str, bits)),
                           outcome_probabilities={f'{i:02b}': r(p) for i, p in enumerate(np.diag(out).real)},
                           fixed_point_dimension=mult)
    two = {}
    for label in ('0', '-'):
        c = bhw_two_state(label)
        out, _, mult = d_ctc(c.U, c.rho, c.d_cr, c.d_loop)
        two[label] = dict(p_outcome_1=r(np.diag(out).real[1]), fixed_point_dimension=mult)
    gun = []
    for deg in range(0, 181, 15):
        c = lloyd_grandfather(np.radians(deg))
        post, _ = p_ctc(c.U, c.rho, c.d_cr, c.d_loop)
        out, _, _ = d_ctc(c.U, c.rho, c.d_cr, c.d_loop)
        gun.append(dict(theta_deg=deg,
                        p_ctc_success_and_same=r(p_ctc_success_probability(c.U, c.rho, c.d_cr, c.d_loop)),
                        p_ctc_opposite_given_success=None if post is None else r(post[1, 1].real + post[2, 2].real),
                        d_ctc_opposite=r(out[1, 1].real + out[2, 2].real)))
    c = lloyd_unproved_theorem()
    post, _ = p_ctc(c.U, c.rho, c.d_cr, c.d_loop)
    out, _, _ = d_ctc(c.U, c.rho, c.d_cr, c.d_loop)
    theorem = dict(p_ctc_state=np.round(post.real, 10).tolist(), d_ctc_state=np.round(out.real, 10).tolist())
    return dict(bhw_fig1=two, bhw_bb84=bb84, lloyd_gun=gun, lloyd_unproved_theorem=theorem)


def plot():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    deg = np.linspace(0, 180, 181)
    p_success = [p_ctc_success_probability(*[getattr(lloyd_grandfather(np.radians(d)), k)
                                            for k in ('U', 'rho', 'd_cr', 'd_loop')]) for d in deg]
    d_kill = []
    for d in deg:
        c = lloyd_grandfather(np.radians(d))
        out, _, _ = d_ctc(c.U, c.rho, c.d_cr, c.d_loop)
        d_kill.append(out[1, 1].real + out[2, 2].real)

    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=160)
    ax.plot(deg, p_success, color=COLORS['p_ctc'], lw=2,
            label='P-CTC: P(teleportation succeeds, probes agree)')
    ax.plot(deg, np.zeros_like(deg), color=COLORS['p_ctc'], lw=2, ls=(0, (1, 2)),
            label='P-CTC: P(probes disagree | success) = 0')
    ax.plot(deg, d_kill, color=COLORS['d_ctc'], lw=2, ls=(0, (4, 3)),
            label='D-CTC: P(probes disagree) (ours)')
    ax.set_xlim(0, 180)
    ax.set_xticks(range(0, 181, 30))
    ax.set_ylim(-0.03, 1.05)
    ax.set_xlabel('Quantum gun angle θ (degrees)', color=INK)
    ax.set_ylabel('Probability', color=INK)
    ax.set_title('Lloyd et al. 2011, Fig. 4 theory curve, re-derived', loc='left', fontsize=10, color=INK)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelcolor=INK, labelsize=9)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=8.5, labelcolor=INK, loc='center left', bbox_to_anchor=(0.0, 0.62))
    fig.text(0.01, 0.005, 'Theory only; the measured points of the paper are not reproduced.', color=MUTED, fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT / 'lloyd_fig4_theory.png', facecolor='#fcfcfb')


def main():
    OUT.mkdir(exist_ok=True)
    data = collect()
    (OUT / 'literature.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    plot()
    print(json.dumps({k: data[k] for k in ('bhw_fig1', 'bhw_bb84')}, indent=1))


if __name__ == '__main__':
    main()
