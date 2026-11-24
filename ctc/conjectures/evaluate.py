"""SPDX-License-Identifier: MIT. Conjecture lottery: decide the selected conjectures and score my credences.

Written after credences.json was fixed (SHA-256 1d7ad527ba9ee95d720109fae7fdf1614574343ceafc745babc934e11eb87c9d).
Only conjectures with credence in [LOW, HIGH] are decided; that is the preregistered selection.

Usage (from the repository root):
  python -B ctc/conjectures/evaluate.py [--all]     # --all also decides the rest, labelled exploratory
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from models import d_ctc, no_loop, p_ctc, partial_trace_operator_loop  # noqa: E402
from past_preserving import apply_kraus, past_preserving_kraus  # noqa: E402
from pool import CLASSES, HIGH, LOW, PROPERTIES, TOL, conjecture_ids  # noqa: E402

CREDENCES = HERE / 'credences.json'
EXPECTED_SHA = '1d7ad527ba9ee95d720109fae7fdf1614574343ceafc745babc934e11eb87c9d'


# ---------------------------------------------------------------- circuit classes

def permutations(n_states):
    for perm in itertools.permutations(range(n_states)):
        U = np.zeros((n_states, n_states), complex)
        U[list(perm), list(range(n_states))] = 1
        yield U


def _phase_key(U):
    flat = U.reshape(-1)
    pivot = flat[np.argmax(np.abs(flat) > 1e-9)]
    V = U * (abs(pivot) / pivot)
    key = np.round(V, 6) + (0.0 + 0.0j)          # turns -0.0 into 0.0 so equal matrices get equal keys
    return key.tobytes(), V


def clifford_group():
    """All two-qubit Cliffords up to global phase, by breadth-first search over H, S and CNOTs."""
    H = np.array([[1, 1], [1, -1]], complex) / np.sqrt(2)
    S = np.diag([1, 1j])
    I2 = np.eye(2)
    cnot01 = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], complex)
    cnot10 = np.array([[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0]], complex)
    gens = [np.kron(H, I2), np.kron(I2, H), np.kron(S, I2), np.kron(I2, S), cnot01, cnot10]
    key, start = _phase_key(np.eye(4, dtype=complex))
    seen, frontier = {key: start}, [start]
    while frontier:
        nxt = []
        for U in frontier:
            for g in gens:
                k, V = _phase_key(g @ U)
                if k not in seen:
                    seen[k] = V
                    nxt.append(V)
        frontier = nxt
    return list(seen.values())


def haar(d, rng):
    z = (rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / abs(np.diag(r)))


def controlled(d_cr, d_loop, rng):
    ctrl = sum(np.kron(np.diag(np.eye(d_cr)[k]), haar(d_loop, rng)) for k in range(d_cr))
    return np.kron(haar(d_cr, rng), np.eye(d_loop)) @ ctrl


def unitaries(name, seed):
    c = CLASSES[name]
    if name in ('perm21', 'perm12'):
        yield from permutations(c['d_cr'] * c['d_loop'])
    elif name == 'cliff11':
        group = clifford_group()
        if len(group) != 11520:
            raise RuntimeError(f'Clifford search found {len(group)} elements, expected 11520')
        yield from group
    else:
        rng = np.random.default_rng(seed)
        for _ in range(c['budget']):
            yield controlled(c['d_cr'], c['d_loop'], rng) if name == 'ctrl21' else haar(c['d_cr'] * c['d_loop'], rng)


# ---------------------------------------------------------------- properties

def entropy(rho):
    w = np.clip(np.linalg.eigvalsh((rho + rho.conj().T) / 2), 0, None)
    w = w[w > 1e-12]
    return float(-(w * np.log2(w)).sum())


def trace_distance(a, b):
    return 0.5 * float(np.abs(np.linalg.eigvalsh((a - b + (a - b).conj().T) / 2)).sum())


def basis(d, k):
    rho = np.zeros((d, d), complex)
    rho[k, k] = 1
    return rho


def check(prop, U, d_cr, d_loop):
    """True if U has the property (see pool.PROPERTIES)."""
    mixed_loop = np.eye(d_loop) / d_loop
    kraus = past_preserving_kraus(U, d_cr, d_loop)
    if prop in ('effect_le_pctc', 'unital'):
        rho = np.eye(d_cr, dtype=complex) / d_cr
        pp = apply_kraus(kraus, rho)
        if prop == 'unital':
            return bool(np.allclose(pp, rho, atol=TOL))
        pc, _ = p_ctc(U, rho, d_cr, d_loop)
        if pc is None:
            return True
        nl = no_loop(U, rho, d_cr, d_loop, mixed_loop)
        return trace_distance(pp, nl) <= trace_distance(pc, nl) + TOL
    C = partial_trace_operator_loop(U, d_cr, d_loop)
    for k in range(d_cr):
        rho = basis(d_cr, k)
        pp = apply_kraus(kraus, rho)
        nl = no_loop(U, rho, d_cr, d_loop, mixed_loop)
        if prop == 'exists':
            ok = np.linalg.norm(C[:, k]) > 1e-9
        elif prop == 'pure':
            ok = np.trace(pp @ pp).real >= 1 - TOL
        elif prop == 'entropy':
            ok = entropy(pp) <= entropy(nl) + 1e-7
        elif prop == 'noloop_diag':
            ok = np.allclose(np.diag(pp), np.diag(nl), atol=TOL)
        elif prop in ('dctc_diag', 'dctc_unique_agree'):
            dc, _, mult = d_ctc(U, rho, d_cr, d_loop)
            if prop == 'dctc_diag':
                ok = np.allclose(np.diag(pp), np.diag(dc), atol=TOL)
            else:
                ok = mult != 1 or np.allclose(pp, dc, atol=1e-7)
        elif prop == 'support_subset':
            w, v = np.linalg.eigh((nl + nl.conj().T) / 2)
            outside = v[:, w <= 1e-9]
            ok = np.linalg.norm(outside.conj().T @ pp @ outside) <= 1e-7
        elif prop == 'commute':
            ok = np.linalg.norm(pp @ nl - nl @ pp) <= 1e-7
        else:
            raise KeyError(prop)
        if not ok:
            return False
    return True


# ---------------------------------------------------------------- run

def decide(cid, seed):
    name, prop = cid.split(':')
    c = CLASSES[name]
    start = time.time()
    checked = failures = 0
    first = None
    for U in unitaries(name, seed):
        checked += 1
        if not check(prop, U, c['d_cr'], c['d_loop']):
            failures += 1
            if first is None:
                first = np.round(U, 6)
    if c['kind'] == 'finite':
        verdict = 'PROVED' if failures == 0 else 'REFUTED'
    else:
        verdict = 'NOT REFUTED' if failures == 0 else 'REFUTED'
    return dict(id=cid, verdict=verdict, holds=failures == 0, checked=checked, failures=failures,
                seconds=round(time.time() - start, 1),
                counterexample=None if first is None else [[str(x) for x in row] for row in first])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args()
    raw = CREDENCES.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != EXPECTED_SHA:
        sys.exit(f'credences.json changed after it was fixed ({sha})')
    cred = json.loads(raw)['credences']
    seed = int(sha[:16], 16)
    ids = conjecture_ids()
    selected = [cid for cid in ids if LOW <= cred[cid] <= HIGH]
    todo = ids if args.all else selected
    results = []
    for cid in todo:
        r = decide(cid, seed)
        r['credence'] = cred[cid]
        r['selected'] = cid in selected
        results.append(r)
        print(f'{cid:28s} credence {cred[cid]:.2f}  ->  {r["verdict"]:11s} '
              f'({r["failures"]}/{r["checked"]} counterexamples, {r["seconds"]} s)', flush=True)
    scored = [r for r in results if r['selected']]
    brier = float(np.mean([(r['credence'] - r['holds']) ** 2 for r in scored]))
    print(f'Brier score on the {len(scored)} selected conjectures: {brier:.3f} '
          f'(0.25 = coin flip, 0 = perfect, 1 = always confidently wrong)')
    out = HERE / ('results_all.json' if args.all else 'results.json')
    out.write_text(json.dumps(dict(credences_sha256=sha, brier_selected=brier, properties=PROPERTIES,
                                   classes={k: v['text'] for k, v in CLASSES.items()}, results=results),
                              indent=1), encoding='utf-8')
    print(f'wrote {out}')


if __name__ == '__main__':
    main()
