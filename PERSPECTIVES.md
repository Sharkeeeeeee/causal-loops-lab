# Outside perspectives and suggestions

Created 2026-11-24 with AI assistance (Claude). These are notes from a reading of the project from an outside angle. They are **not peer review**, and no researcher familiar with the CTC literature has confirmed them.

Scope of the reading: the root README, ROADMAP and HYPOTHESIS, every document and program in `ctc/`, and the data of the three IBM runs in `ctc/hardware/`. All tests were run on Python 3.13 with NumPy 2.5, and the analysis of the third hardware run was recomputed from raw counts (section 2).

Abbreviation: PPS = past-preserving selection (renamed from "PP" to avoid a clash with the complexity class PP; see 1.5).

## 1. Three layers of hypotheses

H1–H3 ([HYPOTHESIS.md](HYPOTHESIS.md)) and H1′–H3′ ([ctc/THEOREMS.md](ctc/THEOREMS.md)) live in two documents, and their relation is hard to see. Sorting the hypotheses by distance from what has been proved gives three layers:

| | Inner layer: proved theorems | Middle layer: general finite-dimensional quantum systems | Outer layer: the real universe |
|---|---|---|---|
| Statement | under PPS, H1′–H3′ hold | the same conclusions hold for any quantum interaction, and PPS is the only reasonable rule | if the universe has time loops, H1–H3 describe what actually happens |
| Scope | finite dimension; classical reversible circuits; controlled-form U; fixed record basis | finite dimension; any U, any entanglement; record basis set by the dynamics | curved spacetime, quantum fields, gravity |
| Nature | mathematical theorems | mathematical problems plus some physical choices | physical claim |
| Status | proved, checked numerically, measurable on hardware | partly done; open problems at the end of THEOREMS.md | not testable at present |
| How to test | proofs, numerical checks, formalization (Lean) | proofs, counterexample search | needs a theory of quantum gravity, or an actual time loop |

How the layers relate:

- **Extending outward is not automatic.** The inner layer holding does not mean the universe works this way.
- **The outer layer's answer cannot overturn the inner layer.** Even if the universe has no time loops, the inner layer is correct mathematics: it says what would happen if there were loops and the rule were PPS.
- **Moving inward, the hypotheses were rewritten, and the no-signalling condition forced it.** H1 went from "paradox worlds disappear" to "in a paradox world the loop is mixed"; H2 from "reweight the world" to "reweight only inside each past world". This rewriting is itself one of the project's main findings and deserves to be explained in outward-facing documents.

(The table is now in HYPOTHESIS.md.)

### 1.1 More columns per layer

| Field | Inner | Middle | Outer |
|---|---|---|---|
| Assumptions | fixed record basis; classical reversible circuits (Theorems 1, 2); controlled-form U (Theorem 3) | finite dimension; record basis set by the interaction | time loops exist; some theory of quantum gravity |
| Falsified by | an error in a proof, or a numerical counterexample | another rule meeting the same conditions that is not PPS (refutes uniqueness); or an example where a state-independent record basis still signals | chronology protection being proved; or quantum gravity giving a different rule |
| Versions already refuted | the original H3 has a counterexample under P-CTC (THEOREMS.md, remark after Theorem 3) | the original H2, "reweight the whole world", equals superluminal signalling (NO_SIGNALLING.md) | none |
| Evidence | proofs, numerical checks, measurable on hardware | partial proofs, numerical exploration | literature |

The "versions already refuted" row is worth keeping: these negative results are outcomes of the project and should not stay scattered across documents.

### 1.2 Layers crossed with H1–H3

| | Inner | Middle | Outer |
|---|---|---|---|
| **H1 consistency** | Theorem 1: a world with a consistent history shows only consistent outcomes; a paradox world sits at the Deutsch fixed point | the quantum case must decide between logical and amplitude consistency; for general U the current statement is almost the definition of PPS and needs a version with more content | Novikov's principle; the classical "billiard-ball paradox" studies (Echeverria–Klinkhammer–Thorne 1991) found that one initial condition can have several consistent solutions |
| **H2 effect in the future** | Theorem 2: past unchanged, conditioning on consistency inside each world | how the record basis is fixed (3.1); for entangled systems the effect appears only in sorted data | whether loop effects could be observed in a real environment |
| **H3 causality recovered** | Theorem 3: controlled-form U | general U "that does not act back" (open problem 1 in THEOREMS.md) | regions without loops must reduce to ordinary QFT; quantum fields are not well defined at a loop boundary (Kay–Radzikowski–Wald 1997) |

The billiard-ball paradox is the most direct prior work for the outer layer of H1. It is in the comparison table of `LITERATURE_REVIEW.md` at abstract level; the original should be read.

### 1.3 Bridges between layers

What has to be proved to move a conclusion one layer outward:

**Inner → middle**
1. a record basis set by the interaction, independent of the state (3.1);
2. Theorem 3 extended to general U;
3. Theorems 1 and 2 extended from classical to quantum circuits while keeping real content;
4. uniqueness of PPS (3.2).

**Middle → outer**
1. infinite dimensions: continuous variables, photons; D-CTC fixed points need not exist in infinite dimensions;
2. **relativistic covariance.** PPS needs to know which facts "have been recorded", i.e. it needs a time order. In relativity, spacelike-separated events have no absolute order, so the "recorded past" must be defined by light cones for the result to be frame independent. But in a region with time loops, the light-cone past may cover the whole region, and the definition may not be usable at all. The project's documents do not yet mention this;
3. connecting to general-relativistic solutions with closed timelike curves, and to Hawking's chronology-protection conjecture.

### 1.4 A second axis: rules

Besides the "scope" axis, the project has a "rule" axis: no loop, D-CTC, P-CTC, T-CTC, κ–β, PPS. Crossing them shows where each rule fails:

| Rule | Inner | Middle |
|---|---|---|
| P-CTC | H3 counterexample; the ε = 0 grandfather paradox is undefined | signals |
| T-CTC | reproduced against Allen 2014 | signals, same criterion as P-CTC |
| D-CTC (reduced state) | no reweighting, so H2 fails in the grandfather paradox | does not signal; applied branch by branch, it does |
| κ–β | two corners equal P-CTC and D-CTC | only the β = 0 edge does not signal |
| PPS | H1′–H3′ hold | no signalling with a fixed basis; unproved for a state-dependent basis (3.1); computationally at least as powerful as P-CTC (1.5) |

### 1.5 Computational power: PPS is at least as powerful as P-CTC

This is part of T4 in phase 3 of the roadmap; nobody had computed the computational power of PPS.

**Argument.** By the definition in THEOREMS.md, when the input is a definite record |k⟩ and C|k⟩ ≠ 0, PPS outputs C|k⟩/‖C|k⟩‖, exactly like P-CTC. (The docstring of `ctc/past_preserving.py` also notes that for a pure input with a record basis containing it, PPS is P-CTC.) A computation starts from a definite classical input, so whatever P-CTC can do on classical inputs, PPS can too. P-CTC's computational power is known to equal PostBQP (Lloyd et al. 2011), and PostBQP equals the complexity class PP (Aaronson 2005).

**Conclusion.** PPS has computational power **at least** PostBQP. No upper bound is proved. PPS cannot signal, but its computational power is just as unusually strong: in principle it could solve NP-complete problems in a single call. Aaronson and others treat such power as evidence that a rule is unlikely to be physical, so this should be listed as one of PPS's costs.

**Why "protecting the past" does not stop it.** PPS only protects the record at the input. The superposition the computation needs is created by U after the record; PPS does not constrain that part.

**Numerical checks:** `ctc/tests/test_computational_power.py`, 5 tests, all pass:
- random U, definite basis input: PPS equals P-CTC (5 dimensions × 5 U × all inputs);
- pure input with a record basis containing it: PPS equals P-CTC;
- mixed input: the two differ (P-CTC reweights worlds, PPS does not);
- search problem: 6 qubits and one loop qubit. Input |000000⟩ is the only recorded past; U applies Hadamards, then flips the loop qubit when "x is not a solution". PPS and P-CTC both output a solution with probability 1; without the loop the success rate is (number of solutions) / 64;
- no solution: P-CTC is undefined; PPS falls back to D-CTC and still gives an output.

**Name clash.** The project used "PP" for past-preserving selection, which clashes with the complexity class PP, and `LITERATURE_REVIEW.md` cites "the computational power of P-CTC is in PP". The documentation now uses **PPS**.

### 1.6 Topics not yet in the framework

- **Thermodynamics and no-cloning** (the other half of T4, middle layer): can PPS clone unknown quantum states or violate the second law?
- **The bootstrap paradox under PPS** (inner layer): where does the information come from? `ctc/output/bootstrap.json` covers only D-CTC and P-CTC; adding PPS is easy. By the argument of 1.5, with a definite input the result equals P-CTC's.
- **Interfaces with other frameworks:** Baumeler–Wolf classical process functions (inner), process matrices (middle), Gell-Mann–Hartle decoherent histories (middle to outer, see 3.3).

## 2. Observations on the hardware experiments

### 2.1 Independent recomputation: the numbers reproduce

Recomputing with `ctc/hardware/analyze.py` from the raw counts in `data/ibm_ibm_kingston_dc1j37ts2omc738amaa0.json`:

- every measured value matches the repository's report;
- all 21 criteria pass;
- only a few bootstrap standard errors and z values differ in the third decimal (for example the eraser_z z value goes from −58.3 to −57.9), presumably from the NumPy version (2.3 vs 2.5); no criterion is affected;
- the SHA-256 of `PREREGISTRATION.md` equals the `956fe5a6…` recorded in the results file.

### 2.2 The preregistration has no external timestamp

- The results file records retrieval at 2026-11-22T18:18:36Z.
- `PREREGISTRATION.md` and the results data were added to git in **the same commit** (`e8e1ede`, 2026-11-22T18:26:27Z), 8 minutes after retrieval.
- The hash in the results file is written by `run_ibm.py` itself; it proves what the preregistration said when the results were saved, not that it existed in that form before submission.

This does not suggest anything improper, and `ctc/hardware/README.md` already says the criteria were set after the first two runs. But "preregistration" usually implies a timestamp a third party can verify. **Suggestion:** before the next run, commit and push the preregistration to GitHub (or a timestamped store such as OSF or Zenodo) before submitting the job, and record IBM's job creation time in the results file.

### 2.3 What the experiment can and cannot show

The project already states that "all rules come from the same shots". A more direct wording, suggested for the README:

> The hardware experiment does not compare the rules; it tests whether a postselected circuit reaches theoretical precision on real hardware. The rules are three ways of sorting the same data, so whatever the hardware result, it cannot support one rule over another.

Also, `ctc/hardware/` is not the first P-CTC implementation on a programmable quantum computer: a 2025 experiment on IBM and Quantinuum cloud processors interprets scrambled-information decoding with P-CTCs (arXiv 2501.16335, added to `LITERATURE_REVIEW.md`, content not read). Lloyd et al. 2011 and Ringbauer et al. 2014 were optical.

By that wording, the README badge "IBM hardware 21/21 preregistered checks" could be read as "the experiment supports PPS". (Done: the badge now reads "predictions measurable, 21/21 checks".)

### 2.4 The results depend on readout correction

- The PPS grandfather value is 0.211 corrected and 0.263 uncorrected; with uncorrected numbers, C2 (error ≤ 0.05) would fail. The README discloses this.
- Qubit 147's readout error was 0.46% in the preflight and about 8% in the main job a few minutes later.

**Suggestion:** state the readout-correction method in the preregistration (the criteria currently say only that the bootstrap resamples calibration data, not that corrected numbers are the primary analysis); report the uncorrected criteria as a secondary analysis; interleave calibration circuits with the experiment circuits instead of grouping them.

### 2.5 The eraser only just passes

Visibility 0.870 against a threshold of 0.85. The project already notes that the no-loop visibility drops by the same factor (about 0.92), consistent with ordinary decoherence. That is a reasonable explanation, but a future run can preregister "visibility relative to no-loop" as the criterion, which is less sensitive to hardware noise and reflects the rule better than an absolute threshold.

## 3. Theoretical perspectives

### 3.1 Once the record basis depends on the state, the rule becomes nonlinear

This is the point I consider most important.

- **Theorem 0 assumes a fixed record basis.** With a fixed basis, PPS is a linear quantum channel and so cannot signal.
- **The rule in `ctc/DECOHERENCE.md` does not use a fixed basis.** It takes the eigenbasis of the conditional state ρ_{S|e} as the record basis, so the basis follows the input state. Such a rule is nonlinear in ρ, and the proof of Theorem 0 does not apply directly.
- DECOHERENCE.md argues no-signalling from "Bob cannot change the reduced state of S and the environment", and the numerical tests pass. That argument handles the Bob → Alice direction but not the "linearity trap" of Bennett et al. 2009 or the "preparation problem" of Cavalcanti–Menicucci–Pienaar 2012: the same mixed state can be prepared from different ensembles of pure states, and a nonlinear rule gives different answers for "the mixture" and for "acting on each component, then mixing". PAST_PRESERVING.md already points out the preparation problem, but the decoherence version of the rule does not yet answer it.
- **The "all-or-nothing" behaviour seen in DECOHERENCE.md is probably a symptom of this nonlinearity.** Eigenvectors are discontinuous at degenerate eigenvalues: near a conditional state of 𝟙/2, an arbitrarily small perturbation can turn the eigenbasis in any direction. That a record of s = 0.01 fixes the basis completely is exactly this.

**Suggestion:** let the record basis be fixed by the **interaction**, not the **state**; for example the pointer basis of the system–environment interaction Hamiltonian (which is how Zurek's einselection is defined). Then the rule is linear for each fixed interaction, Theorem 0 applies directly, and there is no eigenvector discontinuity. The roadmap already lists "let the environment's readout basis be set by its own dynamics"; this should be raised in priority, with the explicit requirement that the basis not depend on the state.

### 3.2 The most valuable middle-layer target: uniqueness of PPS

At present PPS is "one rule under which the three hypotheses hold together". A statement like the following would turn PPS from a choice into a forced answer, which would be the project's strongest theoretical result:

> On finite-dimensional systems, the only rules satisfying (a) linear, completely positive and trace preserving (so no signalling), (b) unchanged probabilities in the record basis, (c) only consistent outcomes in worlds that have a consistent history, and (d) ordinary quantum mechanics when the loop does not act back, are PPS (possibly up to the fallback in paradox worlds).

This would also sharpen the "seam" problem in THEOREMS.md: if the only freedom is the fallback in paradox worlds, then "why fall back to D-CTC" becomes a question that can be discussed on its own.

### 3.3 Novelty: full-text comparison with Hartle 1994 (done 2026-11-24)

Hartle 1994 (gr-qc/9309012) was read in full; the comparison is in `ctc/NOVELTY_CHECK.md`, third round, with a numerical check in `ctc/tests/test_hartle.py`. Conclusions:

- **The within-world rule of PPS is not new.** It is Hartle's Eq. (5.6): the conditional probability when the initial state is decohered by a persistent record. Hartle's post-NC state XρX†/Tr(XρX†) (Eq. 6.7) is the P-CTC formula.
- **The only difference is the probability of the recorded past.** Hartle's framework reweights it by ‖X|α⟩‖² (Eqs. 4.1, 5.5), which he calls acausal and treats as a feature; PPS keeps it fixed. Hartle 1994 does not propose this causal version.
- **Research notes must present PPS as "a causal modification of Hartle's framework" and cite Eqs. (5.5)–(5.6)**, not claim a new rule.
- Hartle's no-signalling proof excludes initial entanglement, so it does not contradict the P-CTC signalling results of NO_SIGNALLING.md.
- Hartle notes that only decoherent past alternatives can be assigned probabilities, and that real decoherence mechanisms are local in time. This supports the suggestion of 3.1: a record basis fixed by local environmental interactions.

**Next step:** later work citing Hartle 1994 has not been checked; someone may have written the same causal version there. This needs a database with citation lists (INSPIRE or Semantic Scholar).

## 4. Project management and reproducibility

### 4.1 Documents lagging behind (fixed 2026-11-24)

The roadmap's date and test count, ctc/README's "no hardware runs", the inconsistent Chinese and English versions of README finding 6, and the unfinished literature-review update were all fixed on 2026-11-24. (On the same day the repository was translated to English and the legacy evidence package was removed from the main tree.)

### 4.2 Rerunning the analysis overwrites committed data files

`analyze.py` writes its report straight back into `ctc/hardware/data/`. A rerun therefore:

1. may change reported numbers in the third decimal because of the NumPy version (see 2.1);
2. rewrites every line, because the committed report files use CRLF line endings and the program writes LF.

**Suggestion:** give `analyze.py` an output-directory option, defaulting to a location outside the repository or an ignored folder; update committed result files only for genuinely new runs.

### 4.3 Environment and automation

- **Pin dependency versions.** Add a `requirements.txt` (NumPy, matplotlib; hardware: qiskit, qiskit-ibm-runtime). The tests pass on Python 3.13 and NumPy 2.5, but versions affect bootstrap decimals.
- **Continuous integration.** A GitHub Actions workflow running `ctc/tests/` on every push would give the "tests passing" badge a real source instead of a hand-maintained number.

### 4.4 Formalization (Lean)

The project's theorems are finite-dimensional linear algebra and counting; formalizing them is estimated at a few thousand lines, mostly for quantum-channel infrastructure rather than the project's own content. In 2026 there are Mathlib-compatible quantum-information libraries (for example Lean-Quantum, arXiv 2607.05492, covering partial traces, Kraus and Stinespring) that would lower the cost a lot.

But the value is limited: the proofs are short and already checked numerically, and the main risks are in the definitions and the physical interpretation, which Lean cannot check. If done, formalize only the cleanest parts (Lemma 1, Theorem 1(1), Theorem 2(2) with Mathlib alone, plus Theorem 0 with an existing library) as an appendix.

## 5. Suggested priorities

1. ~~Fix document inconsistencies (4.1) and add the three-layer table to `HYPOTHESIS.md` (section 1).~~ **Done 2026-11-24.**
2. ~~Adjust the README's wording about the hardware experiments (2.3).~~ **Done 2026-11-24:** badge reads "predictions measurable, 21/21 checks"; the README and honesty statement add "results are fixed by standard quantum mechanics", "the preregistration has no external timestamp" and the prior work; `ctc/hardware/README.md` caveats add the same two points.
3. ~~Read Hartle 1994 in full and check the novelty of PPS (3.3).~~ **Done 2026-11-24:** the within-world rule is known (Hartle Eq. 5.6); the difference is only not reweighting the past. Remaining: citation tracking, and reading the billiard-ball paradox originals (1.2).
4. ~~**Make the record basis state independent** (3.1).~~ **Done 2026-11-24 as Theorem 4** (THEOREMS.md): the pointer basis of the interaction. Open: incompatible readouts, weak and coarse records.
5. **State PPS's computational power honestly in any research note** (1.5). ~~Rename the abbreviation.~~ Done: PPS.
6. **Try to prove uniqueness of PPS** (3.2), or at least extend Theorem 3 to general U.
7. **Think about how "the recorded past" is defined in relativity** (1.3). This is the first problem the outer layer meets.
8. **Add requirements.txt and CI; fix analyze.py's output location** (4.2, 4.3).
9. **Ask a researcher familiar with the CTC literature to look at it**, then write an arXiv research note.
10. For the next hardware run, use a preregistration with an external timestamp (2.2) and a relative-visibility criterion (2.5).
11. Optional Lean formalization (4.4).
