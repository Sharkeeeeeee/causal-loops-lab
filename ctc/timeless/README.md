# Past-preserving selection in a timeless universe (Page–Wootters)

Created 2026-11-24 with AI assistance (Claude). No external review. Novelty not established (see the last section).

```text
python -B ctc/tests/test_timeless.py   # 16 tests: one clock, two orderings, the seam
python -B ctc/tests/test_clocks.py     #  8 tests: local clocks, superposed clock
python -B ctc/tests/test_lightcone.py  # 26 tests: light cones, boosts, the loop's future cone; random 1-3D spacetimes, a black hole
python -B ctc/tests/test_wormhole.py   # 10 tests: time dilation with light clocks, a wormhole time machine, the loop on it
```

Code: [paw.py](paw.py) (one clock), [clocks.py](clocks.py) (local clocks and a superposed clock), [lightcone.py](lightcone.py) (a light-cone lattice), [wormhole.py](wormhole.py) (a time loop made by time dilation).

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

In one_way the record is the copy a distant partner holds, so the loop-first column is signalling. (Qualified 2026-11-25: in spacetime a copy of a made after the loop lies in the loop's future cone, so this reading needs a partner correlated outside the cone, as in the local-clock and light-cone models below.) A definition of the past that depends on which clock you use is not physical.

**3. "Past = every record" also fails.** In the refusal experiment the log is a record written by the loop interaction itself. Protecting it freezes P(log | a = 1) at the no-loop 0.5: the loop does nothing at all.

**4. What works: "past = records the loop cannot influence".** A record counts as past if changing the loop's input never changes its reduced state (decided from the dynamics alone; the log is the only record that fails this). This definition:

- needs no clock and gives identical predictions under both clocks (tested for all six experiments);
- protects a recorded fact at every clock reading after it is prepared, **including readings before the record is written**: under the loop-first clock, P(a = 1) stays at its prior at readings 1 and 2, before anything has recorded it;
- is a causal notion, not a temporal one: it is the analogue of "outside the loop's causal future", which is what relativity would require.

(Corrected 2026-11-25: in spacetime the two differ. The influence definition also protects records made after the loop that the loop cannot change, and that lets a later choice change earlier statistics. The light-cone section below replaces it with "outside the loop's causal future" plus Theorem 4's basis, which is Theorem 5.)

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

## A light-cone lattice (added 2026-11-25)

The local clocks above have no space. [lightcone.py](lightcone.py) puts the same question into a 1 + 1 dimensional spacetime.

**The model.**

- Every qubit has a worldline that moves at most one site per step, and every event is a contact interaction: all its qubits sit at one site at that moment. Nothing else is assumed. The causal order of events is the order along shared worldlines, and locality alone turns it into a light cone: every causal relation satisfies |Δx| ≤ Δt, and events with no causal relation act on different qubits (tested).
- The timeless state is a many-fingered-time history: one state for every cut (every spacelike slice through the events), the same whichever frame builds it, with one Feynman–Kitaev constraint per event (tested).
- A frame is a Lorentz boost, t′ = t − βx with |β| < 1. Every boost respects every causal relation, and boosts with β = −0.6 and β = +0.6 disagree on whether Bob's record or Alice's loop comes first (tested).

**The spacetime.**

- A source at x = 2 sends one half of |Φ⁺⟩ (a) to Alice at x = 4 and the other (b) to Bob at x = 0.
- Bob copies b into rec_b at t = 2.
- Alice's loop:
  - the time-travelling qubit m emerges with its partner p at the past mouth M (t = 0);
  - m meets a, and a log qubit, at the loop event L (t = 3);
  - the constraint "(m, p) in |Φ⁺⟩" closes the loop at the future mouth F (t = 5).
- Alice copies a after the loop (rec_late, t = 4), and optionally before it (rec_a, t = 2.5).
- Bob's record is spacelike to both M and L.

**Closing the loop.** With the loop closed (an edge F → M), M, L and F lie in their own causal past (tested). This is the worry in [PERSPECTIVES.md](../../PERSPECTIVES.md) 1.3, item 2: inside a time loop the causal past stops being a usable notion. The causal future does not have this problem. The loop's future J⁺(M) is the same set of events with the loop open or closed (tested).

**Five definitions of the past.** The loop is refusal (it writes the log; a is only a control). Bob's record has P(rec_b = 1) = 0.5 without a loop and 1/3 under P-CTC.

| "The past of the loop" | Records protected | Bob's P(rec_b = 1) | Verdict |
|---|---|---|---|
| Before the simultaneity slice through L, frame β = −0.6 | rec_b | 0.5 | depends on the frame |
| The same, frame β = +0.6 | none | **1/3** | signalling |
| Causal past J⁻(L), loop open | none | **1/3** | misses spacelike records: signalling |
| Causal past J⁻(L), loop closed | the log (written at L, which is now in its own past) | **0.25** | protects the loop's own output, still misses Bob: signalling |
| **Outside the causal future J⁺(M)** | rec_b (and rec_a) | **0.5** | no frame, no signalling |
| Not influenced by the loop (result 4) | rec_b, rec_late (and rec_a) | **0.5** | no frame, no signalling to Bob; but see below |
| **Theorem 4 with "outside" = outside J⁺(M)** (Theorem 5) | a, split in Z (the source's CNOT read it) | **0.5** | no frame, no signalling; needs no record registers |

The same pattern holds when the loop writes onto a (swap_write; P-CTC then gives Bob 0).

**The loop stays inside its future cone (tested on every slice, for every spacetime here).**

- *Without any rule:* no loop input changes the joint state of everything outside J⁺(M). This is ordinary causality on the lattice.
- *Under PPS (any of the last three definitions, seam at L):* on every slice the joint state of everything outside J⁺(M) is exactly the no-loop one. The rule acts only inside the loop's future light cone.
- *Under P-CTC:* outside qubits do change. On a slice where Bob has not yet recorded, P-CTC moves Bob's qubit b to 1/3, which reads as signalling. On a slice where he has, it moves his record rec_b to 1/3, which reads as rewriting the past. The words depend on the slice; in both cases the change is outside the loop's future cone.
- *The seam:* under every rule the initial condition holds, and the transport is unbroken at every event except L.

**"Not influenced" versus "outside the future cone".** The conjecture behind this step was that the two definitions coincide. They do not quite:

- *One direction always holds.* Every record the loop can influence lies in J⁺(M) (locality), so everything outside the cone is protected by both definitions.
- *The converse fails* for records inside the cone that the loop cannot affect. rec_late is a copy of a made after the loop, and refusal uses a only as a control. "Not influenced" protects rec_late; "outside the cone" does not.
- *When does the difference matter?*
  - If the loop acts on the recorded input (swap_write), the two definitions pick the same records (tested).
  - If a record outside the cone already fixes the input (Bob's copy), the extra sector changes nothing: both give the same final state (tested).
  - The difference shows up only when the sole record is inside the cone.
- *Where it shows up, the two rules disagree.* Alice prepares a herself and copies it once, before or after her loop. For refusal the copy commutes with the loop, so the two spacetimes have the same overall unitary for every loop input (tested). "Outside the cone" gives P(a = 1) = 0.5 with the copy before and 1/3 with the copy after. "Not influenced" gives 0.5 for both.
- *"Not influenced" lets a later choice change earlier statistics (tested).* Alice reads her log right after the loop, and only afterwards decides whether to copy a. Under "not influenced", copying protects a, so P(log = 1) is 1/4 if she will copy and 1/3 if she will not. The log is read before the choice is made, so her choice signals into her own past. This happens in the ordinary region after the loop, not through the loop. Under "outside the cone" (and Theorem 5) the log reads 1/3 either way.

**Conclusion (corrected 2026-11-25, same day).** The first version of this section preferred "not influenced", arguing that the light-cone rule "depends on how the circuit is drawn". That was wrong:

- A copy made before the loop and one made after it are different events in spacetime. A rule that treats them differently is not depending on the drawing; it is depending on whether the record lies in the loop's past or in its future.
- "Not influenced" does the opposite, and it pays for it with the backward signal above.
- What survives:
  - "The past of the loop" is everything outside its causal future J⁺(M), and nothing inside it.
  - Inside that region, the record basis comes from the interactions that read the loop's inputs. This is Theorem 4 with "the outside" made precise, stated as Theorem 5 in [THEOREMS.md](../THEOREMS.md).
- This answers PERSPECTIVES.md 1.3, item 2, in the lattice:
  - use the complement of the causal future, which closing the loop does not change;
  - do not use the causal past, which closing the loop makes contain the loop itself.
- It also qualifies results 2 and 4 above (one clock). There, "loop first" puts the record of a after the loop on a's own worldline, and in spacetime that record is inside the loop's future cone:
  - its change under the clock definition is not signalling to a distant partner; that reading needs a partner correlated outside the cone, as Bob is here;
  - protecting it, as the influence definition does, is what leads to the backward signal.
  The one-clock conclusion that clock order cannot define the past still stands, through the local-clock and light-cone models.

### Beyond 1 + 1 dimensions, a few events and a flat background

The same code ([lightcone.py](lightcone.py)) also runs on general spacetimes.

- **Random spacetimes in 1, 2 and 3 spatial dimensions (18 of them, 17–27 events each).**
  - Five walkers move at most one grid step per unit time and interact when they meet, through controlled gates (readouts) with random direction and random target unitaries.
  - The loop mouth sits at the origin. The time traveller m meets whichever walkers visit it, through CNOT, controlled unitaries in either direction, swap_write, or a generic two-qubit unitary. The loop region R = J⁺(M) ∩ J⁻(F) can therefore contain many events, including interactions between walkers on their way back to m.
  - Tested in all 18:
    - every causal relation lies inside the light cone;
    - boosts in random directions respect causality;
    - closing the loop makes exactly R and F chronology violating;
    - no loop input changes anything outside J⁺(M).
  - **Theorem 5 holds in all 18**, on randomly sampled slices containing all of R or none of it: under PPS with Theorem 4's split, the joint state of everything outside J⁺(M) is the no-loop one, to 10⁻¹⁵.
  - P-CTC changes it in at least 80% of the spacetimes where a loop input was read.
  - Protecting record registers alone fails in some spacetimes. A walker that read an input and kept no permanent record is still part of the outside.
- **A black hole (1 + 1, river form).** Space flows inward at 1.5 times the speed of light inside a horizon, so light cones tilt and nothing inside can stand still or get out (tested from the local cones).
  - Alice's loop falls in; Bob stays outside.
  - P-CTC changes Bob's record from 0.5 to 1/3, so information leaves the black hole.
  - PPS (outside the cone, or Theorem 5's split) keeps 0.5, and changes nothing outside J⁺(M) on any slice.
- **Why this covers curved and discrete backgrounds in general.** Every surviving definition and Theorem 5 use only the causal order of events, so any background enters only through which events can influence which. The random spacetimes and the black hole are different causal orders on which the same statement is tested. Theorem 5 is proved for any finite causal order. What is not covered is a continuum limit (infinitely many events), quantum fields, and a time loop that is a solution of general relativity rather than an added edge F → M.

### A time loop made by time dilation (added 2026-11-25)

So far the time loop was an edge F → M put in by hand. [wormhole.py](wormhole.py) builds it instead from the wormhole time machine of Morris, Thorne and Yurtsever (1988), a known construction in general relativity, and the loop's edge becomes the wormhole itself.

**Time dilation, simulated.** A transverse light clock (two mirrors, one photon) is carried along a path. The only rule used is that the photon moves at speed 1 in the lab while keeping up with its mirrors.

- Every photon segment is checked to be lightlike (tested).
- A clock moving at speed v ticks √(1 − v²) times as fast as one at rest, for v = 0.3, 0.6, 0.8, 0.95 (within 1%, tested).
- Over a twin-paradox trip (out and back at 0.8 for 10 time units), the clock at home ticks 199 times and the travelling clock 159 times (one tick = 0.1). The travelling clock ends 4.0 behind, as the proper-time integral says (tested).

**The time machine.**

- *The mouths.* A short wormhole has two mouths. A stays at x = 0; B starts at x = 1 and makes exactly that trip.
- *The throat.* It joins the two mouths at equal proper time: enter B when B's clock reads τ, come out of A when A's clock reads τ. After the trip B's clock is 4 behind, so the wormhole sends you 4 units into the past.
- *The chronology horizon.* Once that shift exceeds the time light needs to go from A to B, closed causal curves exist.
  - The first closed curve appears at lab time 7.5 on mouth B and 4.5 on mouth A, the same surface seen through the throat.
  - The scan matches the closed form t = (d₀ + vT)/(1 − √(1 − v²) + v) for v = 0.5, 0.8, 0.95 (tested).
  - Points on A are chronology violating exactly after 4.5 (tested).
- *Dilation is what makes it.* Without enough dilation (v = 0 or 0.3, where the final shift 0.46 is less than the distance 1) no closed curve ever forms (tested). Its causal structure, including every path through the wormhole any number of times, is computed exactly.

**The loop on it.**

- *The time traveller.* m comes out of mouth A at M = (t 7, x 0), meets Alice's input and log at L = (10, 0.5), and goes into mouth B at F = (11, 1), where B's clock reads 7. So F → M is the wormhole, checked from the clocks to 10⁻¹⁵, and m really travels 4 units into the past (tested).
- *Bob.* A source at (6, −3) shares |Φ⁺⟩ between a and Bob; Bob copies his half at (9.5, −6).
- *Causal structure.*
  - Every causal relation of the circuit, the loop edge included, is a causal relation of the wormhole spacetime.
  - The loop's causal future is the same set of events in both.
  - The circuit's chronology-violating events {M, L, F} are exactly the events with a closed causal curve through them (tested).
- *Bob's record lies outside the causal future of every loop event, even counting every path through the wormhole (tested).*
  - P-CTC still changes it, from 0.5 to 1/3, so in this spacetime P-CTC acts on an event that no causal curve connects to the loop.
  - PPS keeps 0.5, with either the record definition or Theorem 5's split, and changes nothing outside the loop's future on any slice (tested). The only seam is the loop event.

**What this does and does not show.**

- *It is a real general-relativistic mechanism for a time loop, in the idealization of its original paper:*
  - flat spacetime outside the mouths;
  - a point-like throat;
  - a wormhole that needs exotic matter (it violates the null energy condition) to stay open.
- *Theorem 5 needed only the causal order.* This spacetime supplies one in which the loop is the wormhole, and the theorem holds on it.
- *Not tested:* Hawking's chronology-protection conjecture. Quantum fields pile up at the chronology horizon and may destroy the machine (Kim and Thorne 1991; Hawking 1992). Exact vacuum solutions with closed timelike curves, such as Misner space or the Gödel universe, are not modelled either.

## Is this "event-driven"?

In a sense, yes. In this picture there is no clock that drives anything. What exists are events (a record being written, a loop interaction) and relations between them: which records the loop can influence. "The past of the loop" is defined by those relations, not by a time coordinate. This is close in spirit to causal-set and relational approaches, where the causal order of events is basic and time is derived from it. The difference from an event-driven program is that here nothing "fires" in sequence: all events sit together in one static state, and the order is a structure inside it.

## What this says about the user's thesis

"Time does not really exist; past, present and future are definitions" is consistent with PPS, with one correction. Labels taken from a clock cannot define the past: the clock is a convention, and a rule built on it changes its predictions when the clock changes. What PPS needs instead is a causal relation: a fact belongs to the past of the loop if it is recorded and the loop cannot influence it. With that definition PPS works in a static universe, gives the same predictions as before, and does not depend on the choice of clock.

This also gives a toy-model answer to the open problem in [PERSPECTIVES.md](../../PERSPECTIVES.md) 1.3 (how to define "the recorded past" in relativity): use influence, not time order. The light-cone models above sharpen this: the past is everything outside the loop's causal future, with the record basis from Theorem 4 (Theorem 5); protecting uninfluenced records inside the future cone allows a backward signal. It does not solve the record-basis problem of PERSPECTIVES.md 3.1; sectors are still taken in a chosen basis.

## Limitations

- Finite, discrete clocks (Feynman–Kitaev history states), not continuous Page–Wootters clocks with a Hamiltonian constraint; the clocks are ideal (orthogonal readings, no finite resolution).
- Spacetimes are finite and discrete (up to 27 events, 7 qubits), with fixed backgrounds (flat in 1–3 spatial dimensions, one 1 + 1 black hole); no continuum limit, no quantum fields, no metric dynamics. In the light-cone models the time loop is an edge F → M put in by hand. The wormhole model derives it from time dilation (Morris–Thorne–Yurtsever), but in that construction's idealization: 1 + 1 dimensions, a point-like throat, exotic matter assumed, no quantum back-reaction (chronology protection untested). Theorem 5 assumes every interaction that touches a loop input before the loop is a readout (Theorem 4's scope); non-readout interactions remain open.
- The superposed clock is a single quantum switch of two operations, with c assumed not to be held by anyone else. If an outside system recorded c in some basis, which basis counts is the record-basis problem again (PERSPECTIVES.md 3.1).
- The influence criterion uses the no-loop dynamics with four loop inputs (|0⟩, |1⟩, |+⟩, |+i⟩); for these circuits that is exact, but it is not a general definition of causal influence in a timeless universe.
- The predictions are identical to the circuit model by construction (result 1). The new content is conceptual: which definitions of "past" survive. Nothing here can be tested on hardware beyond what [../hardware/](../hardware/README.md) already did.

## Prior work

- D. N. Page, W. K. Wootters, "Evolution without evolution", Phys. Rev. D 27, 2885 (1983) [not read here].
- V. Giovannetti, S. Lloyd, L. Maccone, "Quantum time", Phys. Rev. D 92, 045033 (2015), [arXiv:1504.04215](https://arxiv.org/abs/1504.04215) [abstract]: a consistent modern formulation of Page–Wootters.
- E. Alonso-Serrano, S. Schuster, M. Visser, "Emergent Time and Time Travel in Quantum Physics", Universe 10, 73 (2024), [arXiv:2312.05202](https://arxiv.org/abs/2312.05202) [search snippet]: the closest work found. It makes the emergent time parameter periodic (a cyclic universe) and argues periodicity alone is not enough for meaningful time travel. It does not treat a local loop with D-CTC/P-CTC-type rules or record-defined pasts.
- One web search (2026-11-24) found no paper combining Page–Wootters with past-preserving or record-based loop rules. That is "not found", not "not done".
- M. S. Morris, K. S. Thorne, U. Yurtsever, "Wormholes, time machines, and the weak energy condition", Phys. Rev. Lett. 61, 1446 (1988) [not read here]: the wormhole time machine used in wormhole.py.
- Discrete and emergent spacetime (the Wolfram model, whose 2020 paper allows loops in the causal graph for some rules but reads them as repeated states rather than time travel; Gorard's FAQ answer that causal invariance forbids closed timelike curves; Wüthrich 2019 on time travel in emergent spacetime, quantum gates from multiway rewriting 2025): see [LITERATURE_REVIEW.md](../../LITERATURE_REVIEW.md), section 2, "Added 2026-11-25".
- S.-W. Kim, K. S. Thorne, Phys. Rev. D 43, 3929 (1991), and S. W. Hawking, "Chronology protection conjecture", Phys. Rev. D 46, 603 (1992) [not read here]: quantum instability at the chronology horizon.
