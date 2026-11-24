# Letting decoherence fix the "record basis"

Created 2026-11-22 with AI assistance (Claude). The rule is a candidate proposed in this project; its novelty has not been checked. No external review.

```text
python -B ctc/tests/test_decoherence.py   # 6 tests
python -B ctc/run_decoherence.py          # writes output/decoherence.json and output/decoherence.png
```

The code is in [decoherence.py](decoherence.py). The previous step is [PAST_PRESERVING.md](PAST_PRESERVING.md).

## The problem

Past-preserving selection (PPS) needs to know which basis counts as the "recorded past". In the entangled double slit, Z and X are equally reasonable choices but give different predictions. Here we try to let the environment decide: **what the environment has recorded is the past.**

## Model

- Photon path S (left slit |0⟩, right slit |1⟩).
- Bob's idler B (optional): copies the path with a CNOT.
- Environment E: one to three qubits, each making a **partial** record of the path: |a⟩|0⟩ → |a⟩|E_a⟩ with ⟨E_0|E_1⟩ = 1 − s. s = 0 means no record, s = 1 a perfect copy. The environment can monitor Z (the path) or X.
- All of this happens before the loop. The loop then sends back a bit from the future that adds a phase π/2 to the right path.

## The decoherence-defined rule

1. **Worlds:** each outcome e of the environment read out in its readout basis. The probability of each world is fixed, because the environment's record is the past.
2. **Record basis of S in world e:** the eigenbasis of the conditional state ρ_{S|e}. Bob's idler is traced out in this step, because it belongs to Bob, who can still erase it later.
3. Apply PPS in that basis.

Everything the rule uses (the split into worlds and the basis) depends only on the state of S and the environment, which Bob cannot change, and within each world it is an ordinary channel on S. So **it cannot signal** in either direction. Tests cover both environment bases, four record strengths, two values of p, and two environment qubits.

**Caveat added 2026-11-24:** because the basis depends on the state, the rule is nonlinear in ρ, and Theorem 0 (which needs a fixed basis) does not apply directly. The numerical tests do not settle the preparation problem for nonlinear rules. See [PERSPECTIVES.md](../PERSPECTIVES.md), section 3.1, for the proposed fix: let the interaction, not the state, fix the basis.

## Result 1: a fresh photon — how much of the past is fixed

The photon is entangled with nothing; only the environment records its path (monitoring Z).

![decoherence](output/decoherence.png)

| Record strength s | No time machine | P-CTC | **Decoherence-defined rule** |
|---|---|---|---|
| 0 (no record) | 0.5 | 1/3 | **1/3**: the past can be fully selected |
| 0.1 | 0.5 | 1/3 | **0.356** |
| 0.5 | 0.5 | 1/3 | **0.444** |
| 1 (perfect record) | 0.5 | 1/3 | **0.5**: the past is fully fixed |

The table gives P(photon through the right slit). For one environment qubit the closed form is

```text
P(right) = d²/2 + (1 + c²)/2 · c²/(2 + c²),   c = 1 − s,  d² = 1 − c²
```

- **The degree of decoherence continuously sets how much of the past is fixed** and how much can still be selected by the future.
- **More copies fix the past faster:** with three environment qubits the past is almost fully fixed at s ≈ 0.5 (green dashed line in panel a). This matches the intuition of Zurek's quantum Darwinism: information copied many times is the objective past.
- **P-CTC rewrites the environment's record:** at s = 1 the recorded probability of "right slit" changes from 1/2 to 1/3. If part of the environment is far away, that is signalling. The decoherence-defined rule never changes the record's probabilities (tested).

## Result 2: quantum eraser — the basis is set by what is monitored

The photon is entangled with Bob's idler, and one environment qubit makes a partial record.

| Case | Fringes sorted by Bob's X = + | Change in Bob's statistics |
|---|---|---|
| No time machine, Z environment | visibility 1 − s | 0 |
| P-CTC, Z environment | visibility ≈ 0.943(1 − s), shift π/4 | 0.167 (signalling) |
| **Decoherence rule, Z environment, s > 0** | **no fringes** (the loop acts as a path measurement) | 0 |
| **Decoherence rule, X environment, s > 0** | **visibility 0.943, shift π/4** | 0 |
| Decoherence rule, no environment, p = 0.5 | **basis undetermined** | 0 |
| Decoherence rule, no environment, p = 0.3 | no fringes (Bob's idler itself picks Z) | 0 |

- **The basis is set by who monitors what.** If the environment monitors the path (Z), the loop behaves like a path measurement; if it monitors X, the loop produces the fringe shift that appears only in sorted data. This is Zurek's einselection: the pointer basis is fixed by the interaction.
- **Only one undetermined point remains:** no environment at all and p exactly 0.5. Any environment, or any p ≠ 0.5, fixes the basis.

## Problems found

1. **In the eraser the effect is all-or-nothing.** A tiny record (s = 0.01) fixes the basis completely: a Z environment makes the sorted fringes vanish entirely, even though without the time machine their visibility is still 0.99. The fresh-photon case is continuous; the eraser is not. The cause is that the rule takes an eigenbasis of a mixed conditional state, where a tiny perturbation decides the whole basis (eigenvectors are discontinuous at degenerate eigenvalues). This is suspicious and suggests the rule needs changing. A related phenomenon in the literature: adding arbitrarily small but nonzero decoherence to D-CTC selects a unique fixed point (work by Ralph, Myers and others).
2. **The rule erases the environment's coherences outside its readout basis.** The record probabilities are unchanged, but off-diagonal terms are removed (fresh photon at s = 0.1: from 0.39 to 0). So someone with full control of the environment, measuring it in another basis, could detect the loop. The rule is therefore consistent only when the record is irreversible in practice ("for all practical purposes", as decoherence theory puts it).
3. **The environment's readout basis is chosen by hand.** Here it is the computational basis of the environment qubits. In reality it should follow from the environment's own dynamics; there is no model of that yet.

## What this says about the original question

"Do we see an unchangeable past, or a past compatible with the future?" In this model the answer becomes a computable quantity:

> **The more completely, and the more times, the environment has recorded the past, the more fixed it is; only what has not been recorded is selected by the loop into a version compatible with the future.** The transition between the two is continuous.

Problem 1 shows that for entangled systems this boundary is not yet smooth, and the rule needs further work.
