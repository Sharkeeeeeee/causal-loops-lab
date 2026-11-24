# An effect only the quantum version has: interference between consistent histories

Created 2026-11-22 with AI assistance (Claude). The closed-form results were derived in this project and have not been externally reviewed.

```text
python -B ctc/tests/test_quantum_effects.py   # 7 tests
```

The circuits are `interference()` and `phase_only_loop()` in [circuits.py](circuits.py).

## Circuit

A qubit a is in √(1−p)|0⟩ + √p|1⟩. It interacts with the loop message m through a controlled-phase gate: the phase e^{iφ} is applied only when a = 1 and m = 1. For φ = π this is a CZ gate.

**The message m itself is never changed**, so in every branch both histories, m = 0 and m = 1, are logically consistent. There is no paradox. The only difference between them is the extra phase on the m = 1 history.

## Results

| Rule | P(a = 1) | Coherence of a |
|---|---|---|
| No loop (external message unknown) | p | lost |
| D-CTC | p | lost |
| Classical branch model | p (both histories consistent) | n/a |
| **Quantum P-CTC** | **p cos²(φ/2) / ((1 − p) + p cos²(φ/2))** | kept |

- φ = 0: no phase, and P-CTC gives p like every other rule.
- φ = π (CZ): P-CTC gives **0**. The a = 1 branch is deleted completely because the m = 0 and m = 1 histories have amplitudes +1 and −1 and cancel.
- In between, the world is reweighted continuously.

## Three observations

1. **The world can be reweighted without any contradiction.** The classical version of P-CTC only deletes histories that are logically inconsistent. The quantum version also deletes histories whose amplitudes cancel, even when they are logically consistent. So in the quantum setting H1 must first say whether "consistent" means **logically consistent** or **amplitude-consistent**. The two give different predictions.
2. **Making a classical does not prevent it.** The cancellation happens between the two histories of the loop message, not on a. Even when a's input is an ordinary probability mixture (no superposition), P-CTC still deletes the a = 1 branch (test `test_deletion_happens_even_for_a_classical_input`). This corrects an earlier claim: "with classical inputs the quantum version changes no numbers" holds only for circuits **without phases**, i.e. permutation circuits such as the grandfather, KFK and bootstrap circuits.
3. **A phase-only loop leaves P-CTC undefined.** If the message only picks up a phase (Z) and touches nothing else, Tr_loop U = 0 and P-CTC is undefined, even though every history is logically consistent. D-CTC is unaffected. This is the H3 corner case noted in the literature review.

## Effect on other code

`branches.py` used to check only that the entries of U were integers, so it treated the −1 of a CZ as an ordinary classical move and gave wrong results. It now requires U to be a 0/1 permutation matrix and raises an error on phases (test `test_classical_model_refuses_phase_gates`). The grandfather, KFK and bootstrap circuits carry no phases, so earlier results are unaffected.

## Follow-ups

- A quantum κ–β model with decoherence strength as a third parameter: full decoherence should give back the classical model, no decoherence should reproduce the interference effect above.
- No-signalling tests were done afterwards; see [NO_SIGNALLING.md](NO_SIGNALLING.md).
