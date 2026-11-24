# Past-preserving selection in a timeless universe (Page–Wootters)

Created 2026-11-24 with AI assistance (Claude). No external review. Novelty not established (see the last section).

```text
python -B ctc/tests/test_timeless.py   # 16 tests: one clock, two orderings, the seam
python -B ctc/tests/test_clocks.py     #  8 tests: local clocks, superposed clock
```

Code: [paw.py](paw.py) (one clock), [clocks.py](clocks.py) (local clocks and a superposed clock).

## The question

Past-preserving selection (PPS) protects "the recorded past". Does that need time? Page and Wootters (1983) proposed that the universe as a whole is a static quantum state and that time is only the correlation between a clock subsystem and everything else. If that is right, "past", "present" and "future" are labels we attach to clock readings. Can PPS be written in such a universe, and if so, what must "the past" mean?

## The model

- **One static state for the whole history:** Ψ = Σ_t |t⟩_clock ⊗ ψ_t, with ψ_t = G_t ⋯ G_1 ψ_0. It is the zero-energy state of a Feynman–Kitaev constraint, H_FK Ψ = 0 (tested): nothing in it evolves. "The state at time t" is the conditional state ⟨t|_clock Ψ.
- **The loop is a constraint on the static state,** not a process: the loop qubit and its partner must be found in |Φ⁺⟩ at the end. Lifted to every clock reading, the constraint acts on the whole history at once.
- **The rules contain no time parameter.** P-CTC applies the constraint and normalizes once. PPS splits Ψ into sectors of orthogonal record values, applies the constraint inside each sector, and gives each sector back its weight.
- **Two clocks.** In every hardware experiment the record step and the loop step commute, so they can be read in either order. "Record first" and "loop first" describe the same physics with two different clocks, the way two observers in relativity can disagree on the order of spacelike-separated events.

The six hardware circuits of [../hardware/](../hardware/README.md) are used unchanged.

## Results

**1. PPS can be written without time, and it predicts exactly the same as before.** For all six experiments and both clocks, the timeless versions of no-loop, P-CTC and PPS reproduce the circuit-model predictions to 10⁻¹⁶.

**2. "Past = recorded at an earlier clock reading" fails.** With the record-first clock this definition works. With the loop-first clock the same record counts as "future", nothing is protected, and PPS collapses to P-CTC:

| Experiment | Quantity | No loop | P-CTC | PPS, past by clock (record first) | PPS, past by clock (loop first) | PPS, past by influence (either clock) |
|---|---|---|---|---|---|---|
| one_way | partner's record P(rec = 1) | 0.5 | 0 | 0.5 | **0** | **0.5** |
| grandfather | P(jam = 1) | 0.2 | 1 | 0.2 | **1** | **0.2** |
| refusal | P(a = 1) | 0.5 | 0.333 | 0.5 | **0.333** | **0.5** |

In one_way the record is the copy a distant partner holds, so the loop-first column is signalling. A definition of the past that depends on which clock you use is not physical.

**3. "Past = every record" also fails.** In the refusal experiment the log is a record written by the loop interaction itself. Protecting it freezes P(log | a = 1) at the no-loop 0.5: the loop does nothing at all.

**4. What works: "past = records the loop cannot influence".** A record counts as past if changing the loop's input never changes its reduced state (decided from the dynamics alone; the log is the only record that fails this). This definition:

- needs no clock and gives identical predictions under both clocks (tested for all six experiments);
- protects a recorded fact at every clock reading after it is prepared, **including readings before the record is written**: under the loop-first clock, P(a = 1) stays at its prior at readings 1 and 2, before anything has recorded it;
- is a causal notion, not a temporal one: it is the analogue of "outside the loop's causal future", which is what relativity would require.

**5. P-CTC rewrites the history at clock readings before the loop.** In refusal with the record-first clock, P(a = 1) is already 1/3 at reading 1, before the record is written and before the loop interaction. In the timeless picture this is literal: the constraint acts on the whole history at once.

**6. The beginning: solved by putting the seam at the loop event.** Spreading a rule back over the whole history moves clock reading 0 (all registers reset, nothing recorded): under P-CTC, under PPS where the loop has an effect, and, once PPS sectors are combined as a mixture (as Theorem 4 requires), even where it has none, because each sector's history goes back to a different reading 0. The fix is to keep every reading before the loop interaction as the forward history and apply the rule from the loop event on (`Model.state_seam`). Then (all tested, for all six experiments and both clocks):

- the initial condition holds exactly, and the only break in the transport between readings is at the loop event, for every rule;
- final predictions are unchanged;
- **under PPS nothing outside the loop interaction changes across the seam**: no record, no other register. The discontinuity is local to the loop event;
- **under P-CTC, existing records the loop never touches jump at the seam** (one_way 0.5, grandfather 0.8, refusal 1/6). P-CTC cannot be made local: it has to rewrite the past.

An earlier version of result 6 called the moved beginning an open problem. With the seam it is not one; the moved beginning was an artifact of propagating the rule backwards past the loop event.

**7. Two corrections from Theorem 4 (same day).** The record sectors now use the pointer basis of the CNOT that wrote each record (Z), not the hardware design's measurement basis (X for eraser_x/y); and sectors are combined as a mixture, not as amplitudes, since an amplitude sum is not a channel and can signal. With these, PPS in the timeless model equals the circuit rule in the pointer basis as a full density matrix (tested).

**Correction (2026-11-24, later the same day).** "Records the loop cannot influence" must include every outside system that holds information about the input, not only designated record registers: with a bare entangled partner and no record register, the definition protects nothing, collapses to P-CTC and signals. The fix is Theorem 4 in [THEOREMS.md](../THEOREMS.md): split Alice's input in the pointer basis of the interaction that correlated it with the outside.

## Fuller clocks: local clocks and a superposed clock

Results 1–6 used one clock and two orderings of commuting steps. [clocks.py](clocks.py) replaces that with two more complete clock systems.

### Local clocks (one static state, many frames)

Alice (input a, loop, partner) and Bob (b, his record) each carry their own clock register, with a and b in |Φ⁺⟩. The static state is Σ |t_A⟩|t_B⟩ ⊗ A^{t_A} B^{t_B} ψ₀. It satisfies one constraint per clock, J_A Ψ = J_B Ψ = 0 with [J_A, J_B] = 0, plus the initial condition (all tested). A global "now" is a frame: a staircase path through the (t_A, t_B) lattice. "Bob first" and "Alice first" are both inside the same static state; nothing outside it picks one. This is the toy version of relativity of simultaneity.

| Bob's record P(rec_b = 1) | No loop | P-CTC | PPS, past by clock (Bob-first frame) | PPS, past by clock (Alice-first frame) | PPS, past by influence |
|---|---|---|---|---|---|
| Alice's loop: one_way | 0.5 | 0 | 0.5 | **0** | **0.5** |
| Alice's loop: eraser phase | 0.5 | 0.333 | 0.5 | **0.333** | **0.5** |

- P-CTC gives the same number in every frame. In the Bob-first frame it changes a record that already exists before Alice's loop (at lattice point (0, 1)), which reads as "rewriting the past". In the Alice-first frame it reads as "signalling". The words depend on the frame; the physics does not.
- The clock definition of the past depends on the frame. The influence definition does not use a frame and protects Bob's record in all of them.

### A superposed clock (indefinite order)

A control qubit c in |+⟩ decides whether Alice records her input before or after her loop interaction. This is a quantum switch: relative to the loop, the clock reading of the record is in superposition. The loop here also writes onto the input (|a, m⟩ → |m, a ⊕ m⟩; a = 1 has no consistent history), so a record made after the loop is influenced by it.

| Case | Clock definition | Influence definition |
|---|---|---|
| Order recorded (c copied into rec_c) | protects the record in the "record first" branch | same sectors and same predictions (tested) |
| Order not recorded, Bob holds an earlier copy of a | protects Bob's copy; no signalling; but **splits by c**, so the order's interference P(c = +) drops from 0.750 to 0.500 | protects Bob's copy; no signalling; P(c = +) stays 0.750. P-CTC changes Bob's copy from 0.3 to 0 |
| Order not recorded, nobody holds a copy ("fresh" qubit) | **must split the state by c, which nothing recorded.** The order's interference P(c = +) drops from 0.750 to 0.500, exactly as if the order had been measured | **no split**: the record is written by the loop in one branch, so it is not past in any branch. The fresh qubit is selected (P(rec = 1 \| c = 0) = 0, as under P-CTC) and P(c = +) stays 0.750 |

So when the order is a recorded fact the two definitions agree, and when it is not, only the influence definition stays within PPS's own principle (only records are facts). (Corrected 2026-11-24: the first version combined PPS sectors as amplitudes and reported 0.709; combined as a mixture, as Theorem 4 requires, the clock definition removes the order's interference completely.) In this example no rule signals even if c has a distant entangled partner (checked: the partner stays at 0.5 in Z and X). That is one example, not a proof.

To make this work, influence is decided sector by sector: a record can be past inside one sector of other protected records (order recorded as "record first") and not in another.

## Is this "event-driven"?

In a sense, yes. In this picture there is no clock that drives anything. What exists are events (a record being written, a loop interaction) and relations between them: which records the loop can influence. "The past of the loop" is defined by those relations, not by a time coordinate. This is close in spirit to causal-set and relational approaches, where the causal order of events is basic and time is derived from it. The difference from an event-driven program is that here nothing "fires" in sequence: all events sit together in one static state, and the order is a structure inside it.

## What this says about the user's thesis

"Time does not really exist; past, present and future are definitions" is consistent with PPS, with one correction. Labels taken from a clock cannot define the past: the clock is a convention, and a rule built on it changes its predictions when the clock changes. What PPS needs instead is a causal relation: a fact belongs to the past of the loop if it is recorded and the loop cannot influence it. With that definition PPS works in a static universe, gives the same predictions as before, and does not depend on the choice of clock.

This also gives a toy-model answer to the open problem in [PERSPECTIVES.md](../../PERSPECTIVES.md) 1.3 (how to define "the recorded past" in relativity): use influence, not time order. It does not solve the record-basis problem of PERSPECTIVES.md 3.1; sectors are still taken in a chosen basis.

## Limitations

- Finite, discrete clocks (Feynman–Kitaev history states), not continuous Page–Wootters clocks with a Hamiltonian constraint; the clocks are ideal (orthogonal readings, no finite resolution).
- Local clocks give relativity of simultaneity in a toy form only: no spacetime, no time dilation, one step per clock.
- The superposed clock is a single quantum switch of two operations, with c assumed not to be held by anyone else. If an outside system recorded c in some basis, which basis counts is the record-basis problem again (PERSPECTIVES.md 3.1).
- The influence criterion uses the no-loop dynamics with four loop inputs (|0⟩, |1⟩, |+⟩, |+i⟩); for these circuits that is exact, but it is not a general definition of causal influence in a timeless universe.
- The predictions are identical to the circuit model by construction (result 1). The new content is conceptual: which definitions of "past" survive. Nothing here can be tested on hardware beyond what [../hardware/](../hardware/README.md) already did.

## Prior work

- D. N. Page, W. K. Wootters, "Evolution without evolution", Phys. Rev. D 27, 2885 (1983) [not read here].
- V. Giovannetti, S. Lloyd, L. Maccone, "Quantum time", Phys. Rev. D 92, 045033 (2015), [arXiv:1504.04215](https://arxiv.org/abs/1504.04215) [abstract]: a consistent modern formulation of Page–Wootters.
- E. Alonso-Serrano, S. Schuster, M. Visser, "Emergent Time and Time Travel in Quantum Physics", Universe 10, 73 (2024), [arXiv:2312.05202](https://arxiv.org/abs/2312.05202) [search snippet]: the closest work found. It makes the emergent time parameter periodic (a cyclic universe) and argues periodicity alone is not enough for meaningful time travel. It does not treat a local loop with D-CTC/P-CTC-type rules or record-defined pasts.
- One web search (2026-11-24) found no paper combining Page–Wootters with past-preserving or record-based loop rules. That is "not found", not "not done".
