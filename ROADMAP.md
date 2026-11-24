# Research roadmap: causally self-consistent information loops

Created 2026-11-22, last updated 2026-11-24. Written with AI assistance (Claude). No external review.

On 2026-11-22 the repository was renamed Causal Loops Lab and its README rewritten around this research. On 2026-11-24 the repository was translated to English, and the earlier evidence package (`plan-a/`, `plan-b/`, `analysis/` and its hash manifest) was removed from the main tree; it is preserved at the git tag `archive/evidence-package-v0.34`.

## Core hypotheses

Precise statements in [HYPOTHESIS.md](HYPOTHESIS.md).

| | Hypothesis | Plain words |
|---|---|---|
| H1 | Information sent to the past is always self-consistent | The grandfather paradox cannot happen, because contradictory histories do not exist |
| H2 | The loop's observable effect appears in the future | Statistics after the loop differ from a world without it, by a computable amount |
| H3 | Causality is global consistency | Without a loop, H1 reduces to ordinary "cause before effect" |

## What this project does not claim

- It does not claim that people can send information to the past.
- It does not claim that any simulation or experiment can prove information reached the past. Postselected simulations can always be explained in the normal time direction.
- It does not support any personal time-travel claim.

## Main findings so far

These findings changed the content of the hypotheses; details in the linked documents.

1. **H2 needs a separate assumption: the universe prefers consistent branches.** In the κ–β model, without consistency selection (β = 0) the world's probabilities never change, wherever the message comes from. ([ctc/BRANCHES.md](ctc/BRANCHES.md))
2. **Different selection rules can give opposite results.** Lloyd's gun never kills under P-CTC but kills with probability sin²(θ/2) under D-CTC. For the motivated KFK sender, the lowest bad-outcome probability is at the new "typical but consistent" corner, not at P-CTC. ([ctc/LITERATURE_REPRODUCTION.md](ctc/LITERATURE_REPRODUCTION.md), [ctc/BRANCHES.md](ctc/BRANCHES.md))
3. **What changes the future can be the selection itself, not the message.** Under P-CTC, when the warning always works the bad outcome disappears, but the only remaining history is "no warning arrives, and the person happens to choose well". ([ctc/README.md](ctc/README.md))
4. **In the quantum version, H1's "consistency" has two incompatible meanings.** Logical and amplitude consistency differ: two logically consistent histories can cancel by interference and delete a whole branch. ([ctc/QUANTUM_EFFECTS.md](ctc/QUANTUM_EFFECTS.md))
5. **H3 has a corner case under P-CTC.** When the loop message only picks up a phase, P-CTC is undefined although nothing is contradictory. ([ctc/QUANTUM_EFFECTS.md](ctc/QUANTUM_EFFECTS.md))
6. **An unconditional message looks like an ordinary one.** From the receiver's side alone one cannot tell whether a message came from the future. D-CTC and P-CTC agree; under T-CTC it behaves like an ordinary message that is only partly delivered, but still does not reweight the world. ([ctc/README.md](ctc/README.md), [ctc/T_CTC.md](ctc/T_CTC.md))
7. **H2 as first stated violates no-signalling.** In every rule tested, "the loop reweights Alice's world" equals "Alice can signal faster than light to a distant Bob who shares correlations", by exactly the reweighted amount. Only non-reweighting rules (D-CTC on the reduced state, β = 0) cannot signal. P-CTC cannot signal if and only if C†C ∝ 𝟙. D-CTC applied separately to each of Bob's outcomes lets Bob signal perfectly to Alice. ([ctc/NO_SIGNALLING.md](ctc/NO_SIGNALLING.md))
8. **Past-preserving selection (PPS) is a viable way out for H2.** Past probabilities are unchanged; consistency selection acts only inside each recorded past world. It is an ordinary quantum channel and so cannot signal; the grandfather paradox is unchanged, and the KFK bad outcome drops from 0.30 to 0.21. In a double slit with a time loop, the loop's effect appears only in fringes sorted by the idler, isomorphic to a quantum eraser. Open: what fixes the "record" basis, since different choices predict different things. ([ctc/PAST_PRESERVING.md](ctc/PAST_PRESERVING.md))
9. **Under PPS, H1–H3 can be proved as theorems in modified form (H1′–H3′).** Every recorded world is self-consistent; the loop never changes recorded past probabilities and inside each past world conditions the future on consistency; when the loop does not act back, ordinary quantum mechanics is recovered exactly. The original H3 has a counterexample under P-CTC. Each theorem is checked on random circuits. ([ctc/THEOREMS.md](ctc/THEOREMS.md))
10. **The predictions are measurable on IBM quantum computers.** Three runs (two on ibm_marrakesh, one on ibm_kingston); the third had preregistered predictions and criteria, and all 21 pass: P-CTC changes the recorded past and a distant Bob's which-path statistics (0.5 → 0.662), PPS does not (0.501); inconsistent histories are suppressed to 0.035; the eraser's Bob-sorted fringe visibility is 0.870 (theory 0.943) with a shift of 0.774 rad (theory π/4). All rules come from the same shots, so this shows the predictions are measurable, **not** which rule nature uses, and not that loops exist. ([ctc/hardware/README.md](ctc/hardware/README.md))
11. **PPS is computationally at least as powerful as P-CTC.** On definite inputs the two give identical outputs, so PPS inherits P-CTC's PostBQP power; no upper bound is proved. Raised in the outside reading of 2026-11-24. ([PERSPECTIVES.md](PERSPECTIVES.md) 1.5, `ctc/tests/test_computational_power.py`)
12. **PPS is a causal modification of Hartle 1994.** Its within-world rule is Hartle's Eq. (5.6); the only difference is that PPS does not reweight the recorded past. PPS cannot be claimed as a new rule as a whole. ([ctc/NOVELTY_CHECK.md](ctc/NOVELTY_CHECK.md), third round)
13. **Strong, common microscopic loops are ruled out.** If every particle coupled to a loop (Z-basis model), the loop phase would have to be below 0.136 rad: a direct pure-vs-recorded test on ibm_kingston bounds the population shift at |S| < 1.16×10⁻³ (95%), stronger than existing Born-rule data for φ between 0.14 and 0.98 rad. A first run's 10σ "anomaly" was traced, with a preregistered control, to CNOT crosstalk that the design failed to cancel because ±π/2 compiled to the same physical pulse. ([ctc/born_rule/README.md](ctc/born_rule/README.md))
14. **Two intuitive conjectures about PPS are false in general.** In a preregistered "conjecture lottery" (credences hashed before any checking code existed), "the PPS effect never exceeds P-CTC's" holds for single-qubit CR systems but fails for two qubits, and "PPS never increases entropy" fails for classical circuits. Brier score 0.213, close to chance, as intended. ([ctc/conjectures/README.md](ctc/conjectures/README.md))

15. **PPS works in a timeless universe, if "the past" is defined by influence, not by time.** Written as a constraint on a static Page–Wootters history state, PPS reproduces every circuit prediction exactly. "Past = recorded at an earlier clock reading" depends on the choice of clock (with one ordering of two commuting steps PPS collapses to P-CTC and signals); "past = every record" switches the loop off; "past = records the loop cannot influence" works and is clock independent. The same holds with local clocks (one static state, many frames) and with a superposed clock (indefinite order of record and loop): where the order is recorded the definitions agree; where it is not, the clock definition disturbs the order's interference and the influence definition does not. The unrecorded initial condition is kept by putting the rule's seam at the loop event (finding 17). ([ctc/timeless/README.md](ctc/timeless/README.md))

16. **The record basis comes from the interaction (Theorem 4).** Take as the record basis the pointer basis of the interactions that correlated Alice's input with the outside, read off from the interaction alone (operator Schmidt decomposition). Then PPS is a fixed channel and cannot signal in either direction, for any state and any outside operation. Three other definitions signal: counting only explicit record registers (collapses to P-CTC), splitting on Bob's side coherently, and splitting on Bob's side as a mixture (Bob → Alice). The basis changes Alice's predictions (0.3 vs 1/3 in an example), not the outside statistics. Open: incompatible readouts, weak and coarse records. ([ctc/THEOREMS.md](ctc/THEOREMS.md), `ctc/tests/test_records.py`)

17. **Theorem 4 extended, and the initial-condition problem solved.** Incompatible readouts: the last readout fixes the record basis (still a fixed channel). Coarse readouts: inside each block the loop acts on the pre-readout state projected into the block; no signalling for any outside operation, provided the input was pure before the readouts. Weak readouts: no-signalling does not force all-or-nothing; a rule taking the basis from the input's reduced state is continuous and safe, the pointer rule jumps at the first trace of a record, and splitting on the outside's record states signals. Timeless model: with the seam at the loop event the initial condition holds, PPS changes nothing outside the loop interaction, and P-CTC makes untouched records jump. Corrections: timeless PPS sectors now use the pointer basis and are mixed (the superposed-clock number changed from 0.709 to 0.500); the eraser's PPS prediction under Theorem 4 is the Z-basis one (no Bob-sorted fringes). ([ctc/THEOREMS.md](ctc/THEOREMS.md) 4a–4c, [ctc/timeless/README.md](ctc/timeless/README.md))

## Phases

### Phase 0: project setup ✅
- [x] ROADMAP.md and HYPOTHESIS.md
- [x] git version control, pushed to GitHub
- [x] literature review, see [LITERATURE_REVIEW.md](LITERATURE_REVIEW.md) (most papers read at abstract level; check originals before citing)
- [x] update the rows of LITERATURE_REVIEW.md resolved by later work (2026-11-24)
- [x] repository cleanup: English throughout, legacy evidence package moved to a tag (2026-11-24)

### Phase 1: toy-model simulator, code in `ctc/`
Done:
- [x] three rules: no loop, P-CTC, D-CTC, plus an independent check by direct simulation of postselected teleportation
- [x] three scenarios: grandfather paradox with failure probability ε, KFK-type warning, bootstrap paradox
- [x] reproduce 6 claims of Lloyd et al. 2011 and 3 of Brun–Harrington–Wilde 2009 ([ctc/LITERATURE_REPRODUCTION.md](ctc/LITERATURE_REPRODUCTION.md))
- [x] classical κ–β branch model with P-CTC and D-CTC as corners, and two new corners ([ctc/BRANCHES.md](ctc/BRANCHES.md))
- [x] quantum interference: a controlled phase makes P-CTC delete a branch with no contradiction ([ctc/QUANTUM_EFFECTS.md](ctc/QUANTUM_EFFECTS.md))
- [x] no-signalling tests for P-CTC, D-CTC and the classical κ–β model, both directions ([ctc/NO_SIGNALLING.md](ctc/NO_SIGNALLING.md))
- [x] a fourth rule, T-CTC (Allen 2014), reproducing Allen's Eqs. 33, 35, 38 and 40; it also signals, with the same criterion as P-CTC ([ctc/T_CTC.md](ctc/T_CTC.md))
- [x] the H2 way out "past-preserving selection", with a double slit and quantum eraser with a time loop ([ctc/PAST_PRESERVING.md](ctc/PAST_PRESERVING.md))
- [x] decoherence-defined record basis: a fresh photon's past becomes fixed continuously with record strength; in the eraser the basis is set by what the environment monitors, but all-or-nothing ([ctc/DECOHERENCE.md](ctc/DECOHERENCE.md))
- [x] **choose a way out for H2:** PPS chosen; H2 rewritten as H2′ (reweighting only inside each recorded past world) and proved as a theorem ([ctc/THEOREMS.md](ctc/THEOREMS.md)). Other candidates (global non-local rules, D-CTC-like effects on the message only) are not pursued; see [ctc/NO_SIGNALLING.md](ctc/NO_SIGNALLING.md)
- [x] **decision point:** only rules that do not reweight the world are compatible with relativity. Decision: keep no-signalling, rewrite H2 as H2′, adopt PPS (it still reweights the future inside each past world, but weights between worlds do not change)
- [x] novelty checks, rounds 1–3 ([ctc/NOVELTY_CHECK.md](ctc/NOVELTY_CHECK.md)): P-CTC signalling and D-CTC's interpretation dependence are known (Bub–Stairs 2014 and others); the C†C criterion is essentially Araújo–Guérin–Baumeler 2017's linearity condition; Allen 2014 is the closest prior work to the κ–β model; PPS's within-world rule is Hartle 1994 Eq. (5.6)
- [x] 180 tests, all passing (2026-11-24; 3 gate-level hardware tests are skipped without qiskit)

Next, in priority order:
- [x] **make the record basis state independent:** done as Theorem 4 (2026-11-24): the pointer basis of the interaction fixes the basis, the rule is linear, Theorem 0 applies
- [x] incompatible and coarse readouts (Theorem 4a, 4b, 2026-11-24)
- [ ] weak records: choose between the pointer rule (all-or-nothing) and the eigenbasis rule (continuous); both are safe (Theorem 4c)
- [ ] interactions that correlate the input with the outside without reading any basis (the premise of 4b)
- [ ] let the environment's readout basis follow from its own dynamics instead of being chosen by hand
- [ ] citation tracking forward from Hartle 1994, Lloyd 2011 and Allen 2014 (INSPIRE / Semantic Scholar), and ask researchers familiar with the CTC literature whether PPS and the κ–β model have precedents
- [ ] **quantum κ–β model:** decoherence strength as a third parameter. Full decoherence should give back the classical model, none should reproduce the interference effect; possibly built on Gell-Mann–Hartle decoherent histories
- [ ] Brun–Harrington–Wilde's general N-state construction

### Phase 1b: IBM quantum hardware ✅, code in `ctc/hardware/`
Done:
- [x] postselected-teleportation circuits: the same shots give the no-loop, P-CTC and PPS results
- [x] five scenarios: grandfather paradox, refusal to send, one-way control (the P-CTC counterexample to H3), and a delayed-choice quantum eraser with a time loop (Bob reads X or Z)
- [x] error suppression: dynamical decoupling, Pauli twirling of gates and measurements, readout calibration in the same job; the refusal circuit uses a relative-phase Toffoli, cutting two-qubit gates from 13 to 7
- [x] layout chosen from preflight-measured readout errors of all qubits (published calibration data was badly off once)
- [x] predictions and criteria fixed and hashed before submission ([ctc/hardware/PREREGISTRATION.md](ctc/hardware/PREREGISTRATION.md)); run 3 passes all 21 criteria

Next:
- [ ] **repeat the preregistered experiment on a second device** (for example ibm_fez), with the preregistration pushed to GitHub before submission
- [ ] find out why qubit 147's readout error went from 0.46% to about 8% within minutes (drift, or related to measurement twirling)
- [ ] zero-noise extrapolation or similar mitigation to push the inconsistent history (now 0.035) further down
- [ ] a full fringe scan of the eraser (several screen phases), not just X and Y settings
- [ ] the hardware experiment cannot tell the rules apart (all from the same shots); treat it as a demonstration of measurability and do not expand it

### Phase 1c: testing for loops in nature ✅ (first round), code in `ctc/born_rule/`, `ctc/conjectures/`, `ctc/blockchain/`
Done:
- [x] loop model vs published Sorkin (three-slit) bounds: small loop phases were untested because κ₃ scales as φ⁴ while the two-path shift is second order
- [x] direct pure-vs-recorded test on ibm_kingston, preregistered; the first run's anomaly was traced to crosstalk by a preregistered physical-coherence control; new bound |S| < 1.16×10⁻³
- [x] conjecture lottery: 11 conjectures at 35–65% credence settled by exhaustive enumeration or counterexample search
- [x] blockchain loop lottery: protocol v2 designed, loophole-reviewed, 22 offline tests

Next:
- [ ] **GHZ amplification:** if loops couple to a collective quantity, an N-qubit GHZ state picks up phase Nφ; the same pure-vs-recorded test on GHZ states would tighten the φ bound by up to N (limited by GHZ fidelity)
- [ ] **isolation-time dependence:** add delays (with dynamical decoupling) between preparation and measurement to bound a loop "encounter rate"
- [ ] other coupling bases (X basis) for the direct test
- [ ] next conjecture-lottery round, including "for a single-qubit CR system, the PPS effect never exceeds P-CTC's"
- [ ] run the blockchain lottery (needs `opentimestamps-client`; standard physics and H2′ both predict no hits)
- [ ] bounds from published molecule-interference data, for a model where the loop phase scales with mass

### Phase 2: formal framework (about 2–4 months)
- [ ] restate H1–H3 in the process-matrix framework (Oreshkov–Costa–Brukner 2012). Araújo–Guérin–Baumeler 2017 show that process matrices are a linear special case of P-CTC; this is the primary reference
- [ ] check causal inequalities by semidefinite programming (needs a new dependency such as `cvxpy`)
- [ ] reproduce Baumeler–Wolf classical non-causal consistent examples. **Note:** arXiv 2512.23599 (December 2025) gives a counterexample that may affect the characterization theorem of Baumeler–Costa–Ralph–Wolf–Zych 2019; read it before relying on the theorem
- [x] write "the past is unchanged, the future is reweighted" as a mathematical condition: Theorem 2 (H2′) in [ctc/THEOREMS.md](ctc/THEOREMS.md)
- [ ] write an arXiv research note. Candidate core: PPS as a causal modification of Hartle's framework, with H1′–H3′ and its computational power; and the κ–β interpolation with its signalling map. "H2 and no-signalling are incompatible" is known and can only be background

### Phase 3: theorems (6–12 months or more)
The rule X is chosen as PPS, and first versions of T1–T3 are done in [ctc/THEOREMS.md](ctc/THEOREMS.md), but only for restricted cases.
- [ ] T1 no paradox: under rule X, any local operation in the past produces only consistent histories; logical vs amplitude consistency must be specified. **Partly done (11-23):** proved for classical reversible circuits under PPS (Theorem 1)
- [ ] T2 effect only in the future: the loop's only observable effect is a reweighting of future statistics, with an explicit formula. **Partly done (11-23):** proved under PPS, with reweighting only inside each past world (Theorem 2)
- [ ] T3 causality recovered: without a loop, rule X reduces to standard causal quantum mechanics, including phase-only loops. **Partly done (11-23):** proved for controlled-form U, including phase-only loops (Theorem 3); general U open
- [ ] T4 consequences: computational power, thermodynamics, no-cloning, no-signalling. **Partly done:** no signalling with a fixed record basis (Theorem 0); computational power at least PostBQP (PERSPECTIVES.md 1.5)
- [ ] uniqueness of PPS: the only rule that is CPTP, keeps recorded probabilities, gives consistent outcomes and recovers ordinary QM (PERSPECTIVES.md 3.2)
- [ ] the seam of falling back to D-CTC in paradox worlds: justify it or find a rule without a seam
- [ ] how "the recorded past" is defined in relativity (PERSPECTIVES.md 1.3). **Toy-model step (11-24):** in a Page–Wootters universe the past must be "records the loop cannot influence"; clock order fails ([ctc/timeless/README.md](ctc/timeless/README.md)). Local clocks and a superposed clock done the same day. Next: continuous clocks with finite resolution. (The initial condition is handled by putting the seam at the loop event, 11-24.)
- [ ] optional: formalize one or two small theorems in Lean

### Phase 4: publication and collaboration
- [ ] a one-page summary to groups such as Brukner, Costa and Ralph, asking whether the results are known. Attach the code, the κ–β map, THEOREMS.md and the hardware figure, and ask specifically about precedents for PPS
- [ ] post the phase 2 note on arXiv
- [ ] keep disclosing AI assistance and the lack of external review, and keep failed results

### Not in scope (better as separate projects)
- Page–Wootters simulations: time emerging from entanglement in a static universe. Related, but a different question
- Subjective time and states of consciousness: psychology and neuroscience, with completely different methods; mixing them into this repository would confuse the physical claims
- The earlier evidence package (finite SYK model, cost checks): archived at the tag `archive/evidence-package-v0.34`; the former phase-4 idea of reusing it was dropped with the cleanup

## Novelty assessment

Things not seen in the literature read so far that might be new. "Not seen" refers only to this search.

| Candidate | Chance it is new | Value |
|---|---|---|
| PPS as a causal modification of Hartle 1994, with H1′–H3′ | moderate (Hartle does not propose it; later work unchecked) | moderate to high |
| Direct pure-vs-recorded Born-rule test and its bound | moderate (no dedicated published bound found) | moderate |
| "Reweighting equals signalling" in a continuous family of rules | low (known for P-CTC; implicit for classical families in process functions) | moderate |
| The κ–β two-parameter model itself (closest prior work: Allen 2014's T-CTC) | low to moderate | moderate |
| "No selection, no reweighting" | low to moderate | moderate |
| "Typical but consistent" changes the future more than P-CTC | depends on the previous item | low to moderate |
| The logical vs amplitude consistency distinction | low | moderate |
| Closed forms for the motivated sender | low | low to moderate |

## Risks

| Risk | Response |
|---|---|
| The results are already known | novelty checks, full-text reading, asking experts directly (round 3 found Hartle 1994) |
| No-signalling allows only β = 0, refuting H2 (**happened**, at least in the models tested) | still a valuable conclusion, recorded as is; H2 was rescued in modified form (H2′) |
| The selection rule has consequences too strong for known physics | T4; PPS's PostBQP power is one such cost |
| Errors in code or derivations | every result has an independent check; this caught two code errors and one misread hardware result so far |
| Hardware results read as evidence that loops exist or that nature uses PPS | every result file says the rules come from the same shots; criteria preregistered; failed or doubtful numbers kept |
| Symmetry-based error cancellation fooled by compiler frame changes | check the physical pulses actually executed (lesson of the first direct Born-rule test) |
| Reviewers stop reading at "time travel" | use terms such as "causal structure", "process matrix", "CTC models" |
| Too much for one person | use the current results to find collaborators |

## Corrected errors

- The partial trace in the teleportation check was wrong, doubling the success rate. Fixed; the first commit's results were unaffected.
- `branches.py` used to misread circuits with phases as classical moves. It now raises an error on phases; earlier results were unaffected.
- The claim "with classical inputs the quantum version changes no numbers" holds only for circuits without phases.
- When commissioning the literature review, the authors of Baumeler et al. 2019 were given as including Woods; the correct name is Zych.
- In the first hardware run, the low Bell pass rate (0.383) of the one-way circuit was read as a phase error. Readout correction in the second run showed the real cause: about 40% readout error on qubit 42, which held the loop qubit (published value 0.66%). The results file and [ctc/hardware/README.md](ctc/hardware/README.md) were corrected, and layouts are now chosen from measured readout errors.
- NOVELTY_CHECK.md overstated two citations: Bub & Stairs 2014 discuss frame dependence, not "reduced state vs. branch by branch" directly; Araújo et al. 2017 prove the linearity condition but do not discuss signalling. Corrected on 2026-11-24.
- In the direct Born-rule test design, over-rotation of the preparation pulse was first assumed to be a second-order effect; it is first order. The ±π endpoints and the `prep_systematic` estimator were added before the hardware run.
- The first direct Born-rule run reported a 10σ anomaly; a preregistered control traced it to uncancelled CNOT crosstalk (see finding 13).
