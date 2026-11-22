"""SPDX-License-Identifier: MIT. T-CTC (Allen 2014) on every scenario, and the t family.

Run from the repository root:  python -B ctc/run_t_ctc.py
Writes ctc/output/t_ctc.json and ctc/output/t_ctc_signalling.png.
"""
from pathlib import Path
import json
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from circuits import bootstrap, grandfather, interference, kfk  # noqa: E402
from literature import KET, bhw_bb84, lloyd_grandfather  # noqa: E402
from signalling import alice_to_bob, attach_partner, output  # noqa: E402

OUT = HERE / 'output'
INK, MUTED, GRID_INK, SURFACE = '#2b2b29', '#6b6a63', '#e4e3dd', '#fcfcfb'
SERIES = ['#2a78d6', '#eb6834', '#1baf7a']
RULES = ('no_loop', 'd_ctc', 't_ctc', 'p_ctc')


def r(x):
    return None if x is None else round(float(x), 10) + 0.0


def observables():
    """One headline number per scenario under each rule."""
    rows = {}

    def add(name, circuit, read):
        rows[name] = {rule: (None if (out := output(circuit, rule)) is None else r(read(circuit, out)))
                      for rule in RULES}

    add('grandfather eps=0.05: P(gun jams)', grandfather(0.05), lambda c, o: c.probability_one(o, 'jam'))
    add('KFK motivated q=0.3 r=0.6: P(bad outcome)', kfk(0.3, 0.6, 'motivated'),
        lambda c, o: c.probability_one(o, 'outcome'))
    add('KFK unconditional q=0.3 r=0.6: P(bad outcome)', kfk(0.3, 0.6, 'unconditional'),
        lambda c, o: c.probability_one(o, 'outcome'))
    add('interference p=0.5 phi=pi: P(a=1)', interference(0.5, np.pi), lambda c, o: c.probability_one(o, 'a'))
    add('bootstrap: <X> of record', bootstrap(), lambda c, o: c.expectation_x(o, 'record'))
    add('Lloyd gun theta=pi/2: P(probes agree)', lloyd_grandfather(np.pi / 2),
        lambda c, o: o[0, 0].real + o[3, 3].real)
    add('BHW BB84, input |0>: P(correct label 00)', bhw_bb84(np.outer(KET['0'], KET['0'].conj())),
        lambda c, o: o[0, 0].real)
    return rows


def signalling_rows():
    cases = [('grandfather', grandfather(0.05), 'jam'), ('kfk_motivated', kfk(0.3, 0.6, 'motivated'), 'bad'),
             ('kfk_unconditional', kfk(0.3, 0.6, 'unconditional'), 'bad'),
             ('interference', interference(0.5, np.pi), 'a'), ('bootstrap', bootstrap(), 'record')]
    return {name: {rule: r(alice_to_bob(attach_partner(c, label, 'entangled'), rule)) for rule in RULES}
            for name, c, label in cases}


SWEEP = [('Grandfather, ε = 0.05', grandfather(0.05), 'jam'),
         ('Quantum interference, φ = π', interference(0.5, np.pi), 'a'),
         ('KFK motivated sender', kfk(0.3, 0.6, 'motivated'), 'bad')]
T_GRID = np.logspace(-2, 2, 161)


def sweep():
    return {name: [r(alice_to_bob(attach_partner(c, label, 'entangled'), 't_ctc', t=t)) for t in T_GRID]
            for name, c, label in SWEEP}


def plot(curves):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8.6, 4.8), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.axvline(1.0, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=1)
    ax.text(1.06, 0.97, 'T-CTC (Allen 2014), t = 1', transform=ax.get_xaxis_transform(), color=INK, fontsize=8.5,
            va='top')
    for (name, _, _), color in zip(SWEEP, SERIES):
        y = np.array(curves[name], float)
        ax.plot(T_GRID, y, color=color, lw=2, label=name, zorder=3)
        at_one = y[np.argmin(abs(T_GRID - 1.0))]
        ax.plot([1.0], [at_one], 'o', ms=8, color=color, mec=SURFACE, mew=2, zorder=4)
        ax.annotate(f'{at_one:.3f}', (1.0, at_one), xytext=(-8, 4), textcoords='offset points', ha='right',
                    fontsize=8, color=INK)
        ax.annotate(name, (T_GRID[0], y[0]), xytext=(4, 5), textcoords='offset points', fontsize=8.5, color=INK)
    ax.set_xscale('log')
    ax.set_xlim(T_GRID[0], T_GRID[-1])
    ax.set_ylim(0, 1.0)
    ax.set_xlabel('t: weight of the non-selecting channel term   (t → 0: P-CTC,  t → ∞: maximally mixed loop)',
                  color=INK, fontsize=9)
    ax.set_ylabel("Change in Bob's statistics (trace distance)", color=INK, fontsize=9)
    ax.set_title('Alice → Bob signalling along the P-CTC ↔ T-CTC ↔ no-selection line', loc='left', fontsize=10.5,
                 color=INK)
    ax.grid(True, axis='y', color=GRID_INK, lw=0.8)
    ax.tick_params(colors=MUTED, labelcolor=INK, labelsize=8)
    for side in ax.spines.values():
        side.set_visible(False)
    legend = ax.legend(loc='upper right', fontsize=8, frameon=False)
    for text in legend.get_texts():
        text.set_color(INK)
    fig.text(0.01, 0.01, 'Bob shares an entangled bit with Alice. Signalling vanishes only in the limit t → ∞. '
             'Values t ≠ 1 are this project\'s generalisation.', color=MUTED, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(OUT / 't_ctc_signalling.png', facecolor=SURFACE)


def main():
    OUT.mkdir(exist_ok=True)
    curves = sweep()
    data = dict(observables=observables(), alice_to_bob_trace_distance=signalling_rows(),
                t_sweep=dict(t=[r(t) for t in T_GRID], curves=curves))
    (OUT / 't_ctc.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    plot(curves)
    print(json.dumps({k: data[k] for k in ('observables', 'alice_to_bob_trace_distance')}, indent=1,
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
