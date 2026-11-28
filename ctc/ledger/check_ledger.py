"""SPDX-License-Identifier: MIT. Check the theorem ledger against the repository.

Run from the repository root:

    python -B ctc/ledger/check_ledger.py                 # validate every row (static, fast)
    python -B ctc/ledger/check_ledger.py --run           # also run each row's test classes
    python -B ctc/ledger/check_ledger.py --impact DEF-fallback   # what depends on an item
    python -B ctc/ledger/check_ledger.py --since af66bc1 # rows whose files changed since a commit
    python -B ctc/ledger/check_ledger.py --graph         # Mermaid dependency graph

Exit status 1 if any static check fails (or, with --run, any test fails).
"""
import argparse
import ast
import csv
import io
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STATUSES = {'definition', 'proved', 'proved-ext', 'numerical', 'open'}
SOURCE_CHECKS = {'read_in_full', 'partial', 'not_compared', 'classical', 'n/a'}


def split(cell):
    return [x.strip() for x in cell.replace(';', ',').split(',') if x.strip()]


def refs(cell):
    return [x.strip() for x in cell.split(';') if x.strip()]


def load(name):
    with open(HERE / name, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def symbols(path):
    """Map 'Name' and 'Class.method' to the number of test_ methods (classes) or 0."""
    tree = ast.parse((ROOT / path).read_text(encoding='utf-8'))
    out = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            out[node.name] = 0
        if isinstance(node, ast.ClassDef):
            tests = 0
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef):
                    out[f'{node.name}.{sub.name}'] = 0
                    tests += sub.name.startswith('test_')
            out[node.name] = tests
    return out


def deps_of(row):
    return split(row.get('depends_on', '')) + split(row.get('external', '')) + split(row.get('assumptions', ''))


def validate(theorems, inputs):
    errors, cache = [], {}
    ids = [r['id'] for r in theorems] + [r['id'] for r in inputs]
    known = set(ids)
    for dup in {i for i in ids if ids.count(i) > 1}:
        errors.append(f'duplicate id {dup}')

    def sym(path):
        if path not in cache:
            cache[path] = symbols(path) if (ROOT / path).exists() else None
        return cache[path]

    docs = {}
    for r in theorems:
        rid = r['id']
        if r['status'] not in STATUSES:
            errors.append(f'{rid}: unknown status {r["status"]!r}')
        for d in deps_of(r):
            if d not in known:
                errors.append(f'{rid}: unknown dependency {d}')
        doc = r['doc_file']
        if doc not in docs:
            p = ROOT / doc
            docs[doc] = p.read_text(encoding='utf-8') if p.exists() else None
        if docs[doc] is None:
            errors.append(f'{rid}: missing doc {doc}')
        elif r['doc_anchor'] and r['doc_anchor'] not in docs[doc]:
            errors.append(f'{rid}: anchor not found in {doc}: {r["doc_anchor"]!r}')
        for kind in ('code', 'tests'):
            for ref in refs(r[kind]):
                path, _, name = ref.partition('::')
                table = sym(path)
                if table is None:
                    errors.append(f'{rid}: missing file {path}')
                elif name and name not in table:
                    errors.append(f'{rid}: {name} not defined in {path}')
                elif kind == 'tests' and name and table[name] == 0:
                    errors.append(f'{rid}: {path}::{name} has no test_ methods')
        if r['status'] in {'proved', 'proved-ext', 'numerical'} and not refs(r['tests']):
            errors.append(f'{rid}: status {r["status"]} but no tests listed')
    for r in inputs:
        if r['source_check'] not in SOURCE_CHECKS:
            errors.append(f'{r["id"]}: unknown source_check {r["source_check"]!r}')
        for u in split(r['used_by']):
            if u not in known:
                errors.append(f'{r["id"]}: used_by unknown id {u}')
    # cycles among theorem rows
    graph = {r['id']: [d for d in split(r['depends_on'])] for r in theorems}
    state = {}

    def visit(n, stack):
        state[n] = 1
        for m in graph.get(n, []):
            if state.get(m) == 1:
                errors.append('dependency cycle: ' + ' -> '.join(stack + [n, m]))
            elif m in graph and not state.get(m):
                visit(m, stack + [n])
        state[n] = 2
    for n in graph:
        if not state.get(n):
            visit(n, [])
    return errors


def dependents(theorems, inputs, target):
    rev = {}
    for r in theorems:
        for d in deps_of(r):
            rev.setdefault(d, set()).add(r['id'])
    for r in inputs:  # an input used_by a row also makes that row depend on it
        for u in split(r['used_by']):
            rev.setdefault(r['id'], set()).add(u)
    seen, todo = set(), [target]
    while todo:
        for m in rev.get(todo.pop(), ()):
            if m not in seen:
                seen.add(m)
                todo.append(m)
    order = [r['id'] for r in theorems]
    return sorted(seen, key=lambda i: order.index(i) if i in order else len(order))


def run_tests(theorems):
    sys.path.insert(0, str(ROOT / 'ctc'))
    sys.path.insert(0, str(ROOT / 'ctc' / 'tests'))
    results, failed = {}, False
    loader = unittest.defaultTestLoader
    for r in theorems:
        for ref in refs(r['tests']):
            if ref in results:
                continue
            path, _, cls = ref.partition('::')
            module = Path(path).stem
            suite = loader.loadTestsFromName(f'{module}.{cls}')
            res = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
            ok = res.wasSuccessful()
            results[ref] = (ok, res.testsRun)
            failed |= not ok
    for r in theorems:
        rs = [results[x] for x in refs(r['tests'])]
        if rs:
            n = sum(k for _, k in rs)
            mark = 'PASS' if all(ok for ok, _ in rs) else 'FAIL'
            print(f'  {mark}  {r["id"]:<18} {n:>3} tests')
    return failed


def changed_since(commit):
    """Files that differ between COMMIT and the working tree (uncommitted edits included)."""
    res = subprocess.run(['git', 'diff', '--name-only', commit], cwd=ROOT, capture_output=True, text=True)
    if res.returncode:
        sys.exit(f'git diff failed for {commit!r}: {res.stderr.strip()}')
    return {line.strip() for line in res.stdout.splitlines() if line.strip()}


def files_of(row):
    fs = set()
    for kind in ('code', 'tests'):
        fs |= {ref.partition('::')[0] for ref in refs(row.get(kind, ''))}
    return fs


def changed_doc_rows(theorems, commit, changed):
    """Rows whose own section of the doc changed. A section runs from the row's anchor
    to the next anchor in the same file (rows sharing an anchor share the section)."""
    hit = set()
    for doc in {r['doc_file'] for r in theorems} & changed:
        text = (ROOT / doc).read_text(encoding='utf-8')
        line_of = {}
        for r in theorems:
            if r['doc_file'] == doc and r['doc_anchor'] in text:
                line_of[r['id']] = text[:text.index(r['doc_anchor'])].count('\n') + 1
        starts = sorted(set(line_of.values()))
        diff = subprocess.run(['git', 'diff', '-U0', commit, '--', doc], cwd=ROOT,
                              capture_output=True, text=True).stdout
        lines = set()
        for h in diff.splitlines():
            if h.startswith('@@'):
                new = h.split('+')[1].split(' ')[0]
                a, _, b = new.partition(',')
                a, b = int(a), int(b or 1)
                lines |= set(range(a, a + max(b, 1)))
        for rid, s in line_of.items():
            nxt = next((x for x in starts if x > s), 10 ** 9)
            if any(s <= ln < nxt for ln in lines):
                hit.add(rid)
    return hit


def mermaid(theorems):
    lines = ['graph BT']
    for r in theorems:
        node = r['id'].replace('.', '_').replace('-', '_')
        lines.append(f'  {node}["{r["id"]}"]')
        for d in split(r['depends_on']):
            lines.append(f'  {node} --> {d.replace(".", "_").replace("-", "_")}')
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', action='store_true', help="run each row's test classes")
    ap.add_argument('--impact', metavar='ID', help='list everything that depends on ID')
    ap.add_argument('--since', metavar='COMMIT', help='rows whose files changed since COMMIT, plus their dependents')
    ap.add_argument('--graph', action='store_true', help='print a Mermaid dependency graph')
    a = ap.parse_args()
    theorems, inputs = load('theorems.tsv'), load('inputs.tsv')

    if a.graph:
        print(mermaid(theorems))
        return 0
    if a.impact:
        hit = dependents(theorems, inputs, a.impact)
        print(f'{len(hit)} items depend on {a.impact}:')
        print('  ' + ', '.join(hit) if hit else '  (none)')
        return 0
    if a.since:
        changed = changed_since(a.since)
        doc_hit = changed_doc_rows(theorems, a.since, changed)
        direct = [r['id'] for r in theorems if files_of(r) & changed or r['id'] in doc_hit]
        extra = sorted({d for i in direct for d in dependents(theorems, inputs, i)} - set(direct))
        print(f'{len(changed)} files changed since {a.since}.')
        print('Rows touching them: ' + (', '.join(direct) or '(none)'))
        print('Their dependents, to recheck: ' + (', '.join(extra) or '(none)'))
        return 0

    errors = validate(theorems, inputs)
    counts = {}
    for r in theorems:
        counts[r['status']] = counts.get(r['status'], 0) + 1
    print(f'{len(theorems)} rows ({", ".join(f"{k} {v}" for k, v in sorted(counts.items()))}), {len(inputs)} inputs')
    for e in errors:
        print('  ERROR ' + e)
    print('static checks: ' + ('OK' if not errors else f'{len(errors)} errors'))
    failed = False
    if a.run:
        print('running tests:')
        failed = run_tests(theorems)
    return 1 if errors or failed else 0


if __name__ == '__main__':
    sys.exit(main())
