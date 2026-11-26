# Literature review: where H1, H2, H3 and the ctc/ toy results sit in the P-CTC / D-CTC literature

Created 2026-11-22, last updated 2026-11-24. Written with AI assistance (Claude); no external review. This is the outcome of phase 0 of the roadmap ("literature review"), not a published survey.

**2026-11-24 update:** cells resolved by later work are marked as such ((a) quantitative comparison, (c) "completely mixed", the reading level of Brun–Harrington–Wilde); an experiment simulating P-CTCs on cloud quantum computers was added; Hartle 1994 was read in full; each gap in section 3 now has a status line. Everything else is as written on 11-22.

**Reading levels** (every claim should be traceable to one of these):

- **[full]**: the PDF was converted to text and the relevant passages were read (not necessarily every word). Lloyd et al. PRL (1005.2219) and PRD (1007.2615), Ralph's comment (1107.4675), Allen (1401.4933), Bennett–Leung–Smith–Smolin (0908.3023). For the PRD, Allen and BLSS, passages were located by keyword.
- **[HTML/abstract+]**: the beginning of the arXiv HTML version was read; the rest is a model-generated summary (may be wrong; check the original before citing). Baumeler et al. 2019 (1703.00779), Tobar–Costa (2001.02511).
- **[abstract]**: only the arXiv abstract page or a search snippet. All other papers.
- **[unverified]**: no primary source seen; memory or second-hand. Marked explicitly, with no arXiv number given.

The project's own numbers (P-CTC and D-CTC) are taken from `ctc/README.md`; this document did not rerun the code in `ctc/`.

---

## 1. Comparison table

| Item | Status | Literature and notes |
|---|---|---|
| **H1** information sent to the past is always self-consistent (no grandfather paradox) | **known** | Classical: Novikov's self-consistency principle; the billiard-ball analysis of Echeverria–Klinkhammer–Thorne 1991 (seen only through second-hand abstract-level descriptions; it found that consistent solutions are **not unique**, [abstract]). Quantum: Deutsch 1991 guarantees consistency with a density-matrix fixed point; Lloyd et al. 2011 implement the Novikov principle directly by postselection, "events with zero amplitude do not happen" [full]. The two notions of consistency differ in strength: Deutsch only requires the loop system's own density matrix to be consistent and **does not preserve** its correlations with CR variables; P-CTC requires consistency including correlations (Lloyd et al. PRD §I [full]). H1 has definite content only once "which consistency" is specified. |
| **H2(1)** the loop's effect is observable and appears in future statistics | **partly known, and disputed** | Under P-CTC, Lloyd et al. PRL state explicitly that contradictory events get probability zero and the rest is renormalized (nonlinear) [full]. But Ralph 2011 (1107.4675) [full] argues that with entanglement P-CTC allows "signals to before the CTC was created"; the reply by Lloyd et al. (1108.0153) [abstract + ar5iv summary] and Bub–Stairs (1309.4751) [abstract] consider Ralph's construction incomplete or flawed. So "the effect appears only in the future" is disputed under P-CTC, not settled. Under D-CTC the effect on the CR system is a nonlinear fixed-point channel, not a simple reweighting. |
| **H2(2)** the difference is fully determined by "removing inconsistent histories and renormalizing" | **known (formally) under P-CTC; no general statement seen** | The P-CTC rule is itself "project, then normalize", which for classical reversible circuits is conditioning on consistent histories (Lloyd et al. [full]; Svetlichny's "probabilistic simulation" [abstract]). I did **not** find a general statement written as `P_loop ∝ P_0 × [consistent]` with a term-by-term comparison to D-CTC, but this negative conclusion is limited to my search. (Proved for PPS as Theorem 2 in [ctc/THEOREMS.md](ctc/THEOREMS.md).) |
| **H3** reduces to ordinary causal QM when the loop has no influence | **known but trivial, with one corner case** | Follows directly from the form of both rules: if U = V ⊗ W (loop and CR uncoupled), then C = V·Tr[W], P-CTC outputs VρV†, and so does D-CTC. **Derived here, not checked against the literature.** Corner case: if Tr[W] = 0 (for example the loop system alone undergoes Z), the P-CTC rule is undefined, so H3 under P-CTC needs an extra "the loop itself is consistent" condition. In the process-matrix framework the analogue is causal separability, or the causal order emerging in the classical limit (Oreshkov–Costa–Brukner abstract [abstract]). (Later: Theorem 3 in THEOREMS.md, with a P-CTC counterexample.) |
| **(a)** grandfather paradox with failure probability ε: P-CTC makes failure certain, D-CTC keeps ε | **known** | This is the circuit of Fig. 2a and the text of Lloyd et al. PRL: with an ideal NOT, the contradictory event has probability zero under P-CTC; with an imperfect NOT (rotation angle off π), the nonlinear postselection amplifies the deviation and only the "gun fails" history remains; under D-CTC she "always succeeds" and the loop bit becomes completely mixed. A photonic experiment (quantum-dot single photons) tested the P-CTC prediction [full]. **Resolved (11-22):** the Fig. 4 theory curve and the numbers in the text are compared item by item in [ctc/LITERATURE_REPRODUCTION.md](ctc/LITERATURE_REPRODUCTION.md) (theory only, not the experimental data points). |
| **(b)** KFK-type warning: an unconditional sender = an ordinary message | **known (implicitly)** | With an unconditional sender, U only copies onto the loop bit; P-CTC and D-CTC agree and give an ordinary channel. A special case of H3; no dedicated discussion found. |
| **(b)** KFK-type warning: motivated sender, P-CTC gives q(1−r)/(1−qr), D-CTC gives q/(1+qr) | **apparently open** | This is a "probabilistic motive" version of the grandfather paradox with the same structure as (a), so it is **qualitatively** known (P-CTC removes contradictory histories, D-CTC mixes). But I did not find this "single receiver + motivated sender + closed-form comparison of both rules" in the literature I searched. "Not found", not "certainly not done". |
| **(c)** bootstrap paradox: same Z statistics; P-CTC coherent (⟨X⟩ = 1), D-CTC mixed (⟨X⟩ = 0) | **partly known** | Lloyd et al. PRL: P-CTC sends pure states to pure states and produces no entropy; D-CTC needs an extra "maximum entropy" assumption to resolve the unproved-theorem paradox [full]. This agrees with (c). The same PRL says the circuit "automatically assigns a completely mixed value" (Fig. 2b caption). **Resolved (11-22):** this refers to the reduced state I/2 of the proof bit, which is maximally entangled with the bit leaving the loop; the overall output is the pure state (\|00⟩ + \|11⟩)/√2, so there is no contradiction (see gap 3). Ralph 2011 objects to P-CTC using the unproved theorem, and Lloyd et al. reply that he missed a step (Bob reading the book) [abstract level]. |

---

## 2. Key papers and what they establish

Each paragraph is marked with its reading level.

**Deutsch 1991, Quantum mechanics near closed timelike lines, Phys. Rev. D 44, 3197 (DOI 10.1103/PhysRevD.44.3197) [abstract / second-hand].** Proposes D-CTC: the loop state ρ_CTC = Tr_CR[U(ρ_CR⊗ρ_CTC)U†] always has at least one fixed point; if it is not unique, Deutsch additionally assumes the maximum-entropy one (as described by Lloyd et al. PRD, [full]). His rule makes the loop's output uncorrelated with CR variables, so memories are "no longer valid". I have not read Deutsch's original; everything about it comes through Lloyd et al. and other papers.

**Bennett & Schumacher 2005 talk; Svetlichny, Time travel: Deutsch vs. teleportation, Int. J. Theor. Phys. 50, 3903 (2011; DOI 10.1007/s10773-011-0973-x; arXiv version 0902.4898, titled Effective Quantum Time Travel) [abstract].** Uses teleportation plus postselection to simulate, probabilistically, quantum circuits with "backward wires"; the abstract says the probabilistic nature "resolves any paradox". The Bennett–Schumacher talk is unpublished (known through Svetlichny's citation; content not seen, [unverified]). This is the origin of the project's P-CTC rule.

**Lloyd et al. 2011 PRL, Closed timelike curves via postselection: theory and experimental test of consistency (arXiv 1005.2219, PRL 106, 040403) [full].** Defines P-CTC, physically inequivalent to Deutsch; the grandfather-paradox circuit, nonlinear amplification by an imperfect "gun", a photonic experiment; P-CTC maps pure states to pure states; the unproved-theorem paradox is resolved as "an unbiased circuit gives an unbiased mixture of all proofs"; the computational power of P-CTC is in PP. For this project: the conceptual prototype of results (a) and (c), and the most direct source for H2 under P-CTC.

**Lloyd et al. 2011 PRD, The quantum mechanics of time travel through post-selected teleportation (arXiv 1007.2615, PRD 84, 025007) [full, keyword-located].** The long version of the PRL: Hilbert-space formulation, agreement with path integrals, comparison with Deutsch's rule. It says plainly that it is currently impossible to decide between P-CTC and D-CTC, perhaps not until a theory of quantum gravity, and calls P-CTC "less pathological" (no maximum-entropy rule needed, weaker computational power). The nonlinear "renormalized probabilities" are the source of both the computational power and the amplification. This is the literature basis for the project's stance that "the selection rule is not decided".

**Brun, Harrington, Wilde 2009, Localized closed timelike curves can perfectly distinguish quantum states (arXiv 0811.1209, PRL 102, 210402) [abstract; after 11-22: Figs. 1–2, Eq. (3) and the related text checked against the arXiv PDF, see [ctc/LITERATURE_REPRODUCTION.md](ctc/LITERATURE_REPRODUCTION.md)].** Under D-CTC, a localized CTC can perfectly distinguish non-orthogonal states, breaking BB84 and similar QKD and violating the Holevo bound.

**Bennett, Leung, Smith, Smolin 2009, Can closed timelike curves or nonlinear quantum mechanics improve quantum state discrimination or help solve hard problems? (arXiv 0908.3023, PRL 103, 170502) [full, keyword-located].** Introduces the linearity trap: a nonlinear map acting on a mixed state is not the mixture of its action on the pure components, so "discriminating an unknown mixture" and "computing on labelled mixtures" must be defined carefully. They propose defining computation as correct evaluation on "labelled mixtures of orthogonal inputs"; under that definition it is unclear whether CTCs help, and the CTC discrimination advantage can be reproduced by solving the fixed-point equation directly. A debate with Brun–Harrington–Wilde. For this project: D-CTC results depend on whether the input is an "unknown mixture" or a "labelled mixture"; `ctc/` always uses a simple version of the former, and reports should say so.

**Aaronson & Watrous 2009, Closed timelike curves make quantum and classical computing equivalent (arXiv 0808.2669, Proc. R. Soc. A 465, 631) [abstract, plus the PDF's table of contents].** Under Deutsch's model, classical and quantum computers with CTCs both equal PSPACE. How it handles non-unique fixed points (maximum entropy or not) I **did not read**; marked unverified.

**Brun & Wilde 2012, Perfect state distinguishability and computational speedups with postselected closed timelike curves (arXiv 1008.0433, Found. Phys. 42, 341, DOI 10.1007/s10701-011-9601-0) [abstract, plus section titles].** Under P-CTC a single qubit through a CTC can perform any postselected measurement with probability 1 (abstract level), and P-CTCs can solve hard problems. That P-CTC computational power equals PP I saw in the abstracts of Lloyd et al. PRL and Araújo–Guérin–Baumeler (1706.09854), not in the body of Brun–Wilde.

**Ralph & Myers 2010, Information flow of quantum states interacting with closed timelike curves (arXiv 1003.1987, PRA 82, 062330) [abstract].** Traces information flow, derives an "equivalent circuit" with a unique solution to compare CTC models objectively, and says CTCs, if they existed, would be a powerful quantum information resource. In his comment Ralph says Deutsch's maximum-entropy conjecture "has been derived independently" and cites this paper (last paragraph of 1107.4675, [full]), but I have not read the derivation. Allen 2014's abstract says this "equivalent circuit model" contains an error [abstract]; Brun–Wilde also mention its ambiguity (second-hand). **Details of Ralph & Myers / Ralph et al. event-CTCs are not verified**: a paper on "event-CTCs" I meant to check was not clearly found, so it is not used in any conclusion.

**Pienaar, Ralph, Myers 2013, Open timelike curves violate Heisenberg's uncertainty principle (arXiv 1206.5485, PRL 110, 060501) [abstract]; Ringbauer et al. 2014, Experimental simulation of closed timelike curves (Nat. Commun. 5, 4145; arXiv 1501.05014) [abstract].** The former models "open timelike curves" with no interaction inside the loop; the latter simulates a single-qubit D-CTC circuit with photons (observing perfect discrimination of non-orthogonal states). These are D-CTC-side experiments and extensions; not read in full.

**(Added 11-24) Experimental simulation of postselected closed timelike curves for decoding scrambled quantum information (arXiv 2501.16335, 2025; search results show later versions up to 2026-04) [search results only].** According to search results, this ran a 4-qubit circuit on IBM and Quantinuum cloud processors, casting the decoding of scrambled quantum information as postselected teleportation interpreted as a P-CTC, with success probability set by an OTOC. For this project: `ctc/hardware/` is not the first P-CTC implementation on a programmable quantum computer; Lloyd et al. 2011 and Ringbauer et al. 2014 were optical, and this is the programmable-processor precedent. Content not read; check device names and numbers against the original before citing.

**Ralph 2011, Problems with modelling closed timelike curves as post-selected teleportation (arXiv 1107.4675) [full], and the reply by Lloyd et al. (arXiv 1108.0153) [abstract + ar5iv summary].** Ralph sends one arm of an entangled state through a wormhole, with Bob signalling by phase flips, and argues that P-CTC allows signals to before the CTC was created; he also reproduces the unproved-theorem paradox. The reply says Ralph missed the step of Bob "reading the book" (the phase flip must be controlled by Alice's book); with it, the whole process has zero amplitude or only a trivial fixed point. Bub–Stairs 2014 (1309.4751) [abstract] also consider Ralph's approach flawed (because entanglement is frame dependent). **This dispute bears directly on whether H2's "only the future is affected" holds**, and I saw no resolution.

**Allen 2014, Treating time travel quantum mechanically (arXiv 1401.4933, PRA 90, 042107) [full, T-CTC part].** Reviews the strengths and weaknesses of D-CTC and P-CTC and proposes "transition probability" CTCs (T-CTC): a mixture over all pure states |ψ⟩ weighted by p(ψ) = |⟨ψ|U|i⟩|², with the CR output obtained by partial projection; it simplifies to "a weighted mixture of the P-CTC equation of motion and an ordinary quantum channel" (Eq. 33). The abstract claims T-CTC has no paradoxes, cannot perfectly distinguish non-orthogonal states, and cannot clone or delete arbitrary pure states; the text says its computational power is at most PP and that it cannot perform arbitrary postselected measurements. (Later implemented as the fourth rule; see [ctc/T_CTC.md](ctc/T_CTC.md).)

**Brun et al. and Dunlap (many-worlds readings).** Dunlap 2015 (arXiv 1510.02742) [abstract] argues that D-CTC needs a stronger metaphysical supplement than Everett (several identical copies of worlds), so it is not a "purely quantum" resolution of paradoxes. This relates to HYPOTHESIS.md pairing D-CTC with time picture B, "branching timelines"; I found no dedicated many-worlds reading of P-CTC (limited search).

**Novikov / Echeverria–Klinkhammer–Thorne 1991.** Only an OSTI record (https://www.osti.gov/biblio/5219973) confirms the paper's existence and title; volume and pages **unverified**; no primary source found for Novikov's original paper, so no reference number is given. Second-hand descriptions say Echeverria and Klinkhammer found more than one consistent solution [abstract level]. For this project: "consistency does not guarantee uniqueness" at the classical level is a fact H1 must face classically, and it is the classical precursor of D-CTC's non-unique fixed points.

**Politzer (hep-th/9207076) [abstract]; Hartle (gr-qc/9309012) [abstract; after 11-24: full text, compared in [ctc/NOVELTY_CHECK.md](ctc/NOVELTY_CHECK.md), third round].** Path-integral / generalized-quantum-mechanics treatments of nonchronal spacetimes: Hartle's framework keeps a probability rule under non-unitary evolution; Lloyd et al. state that P-CTC agrees with these path-integral approaches [full]. Hartle's Eq. (5.6) is the within-world rule of past-preserving selection.

**Oreshkov–Costa–Brukner 2012, Quantum correlations with no causal order (arXiv 1105.4464, Nat. Commun. 3, 1092) [abstract].** Assuming only that local quantum mechanics holds, builds the process-matrix framework with no predefined causal order and finds correlations violating causal inequalities. **Araújo–Feix–Navascués–Brukner 2017, A purification postulate for quantum mechanics with indefinite causal order (arXiv 1611.08535, Quantum 1, 10) [abstract]:** only purifiable processes count as physical, and some known processes fail this; the abstract does not say whether the original OCB process is among them and does not discuss postselection.

**Baumeler & Wolf 2014/2016.** Perfect signaling among three parties violating predefined causal order (arXiv 1312.5916) [abstract]; The space of logically consistent classical processes without causal order (I saw the number 1507.01714 only in ar5iv results, **unconfirmed**; check before citing); Baumeler & Wolf, Computational tameness of classical non-causal models (arXiv 1611.05641, Proc. R. Soc. A 474, 20170698) [abstract]: logically consistent classical non-causal circuit models correspond exactly to UP ∩ coUP, weaker than other CTC models.

**Baumeler–Costa–Ralph–Wolf–Zych 2019, Reversible time travel with freedom of choice (arXiv 1703.00779, CQG 36, 224002) [HTML/abstract+].** Authors: Baumeler, Costa, Ralph, Wolf, Zych. Result: for classical deterministic dynamics compatible with arbitrary local operations, all such dynamics can be realized by reversible interactions; three parties can each be in the others' past and future while keeping free local choices. **Entirely deterministic; no probabilistic "reweighting of the future".** On a quantum extension, it says whether quantization is possible remains unclear, and leaves the D-CTC / P-CTC comparison to later work (model-summary level; check the original).

**Tobar & Costa 2020, Reversible dynamics with closed time-like curves and freedom of choice (arXiv 2001.02511, CQG 37, 205011) [HTML/abstract+].** Extends the characterization of deterministic CTC processes to any N regions and finds a four-party process that cannot be reduced to three parties. Also classical and deterministic, with no probabilistic reweighting. **Note:** a comment on the arXiv page says the counterexample in 2512.23599 (Dourdent et al., December 2025) affects the characterization theorem of 1703.00779 (possibly an erratum); I have not read the counterexample and do not know its scope, so any reproduction of Baumeler–Wolf examples that relies on the theorem must check this first.

**Araújo–Guérin–Baumeler 2017, Quantum computation with indefinite causal structures (arXiv 1706.09854, PRA 96, 052315) [abstract; Sections I–III later read in the original, see NOVELTY_CHECK.md].** Process matrices correspond to a linear special case of P-CTC, so their computational power is bounded by PP. The most direct link between process matrices and P-CTC, and the primary reference for phase 2.

**Jean–Silva–Vilasini 2025, An equivalence between time-symmetry and cyclic causality in quantum theory (arXiv 2508.02463) [abstract].** Proves that the multi-time-state (pre- and postselection) formalism and P-CTC are operationally equivalent. This supports "P-CTC can be seen as a restatement of postselection" and suggests that whether P-CTC is a "real loop" is a matter of interpretation.

**Arvidsson-Shukur et al. 2023, Nonclassical advantage in metrology established via quantum simulations of hypothetical closed timelike curves (arXiv 2207.07666, PRL 131, 150202) [abstract].** Treats P-CTC as a resource that can be simulated by postselected teleportation and shows a metrology advantage. Consistent with this project's stance of not claiming that information reaches the past: it simulates, and makes no time-travel claim.

**Other.** Aaronson–Bavarian–Gueltrini, Computability theory of closed timelike curves (arXiv 1609.05507) [abstract level, seen only in search results]: the 2008 work was restricted to polynomial size, giving PSPACE.

### Added 2026-11-26: forward citations of Hartle 1994

Sixth round of [ctc/NOVELTY_CHECK.md](ctc/NOVELTY_CHECK.md): all 100 papers citing Hartle 1994 screened, 209 citing Lloyd 2011 or Allen 2014 screened by keyword, seven read in full. Closest prior work to PPS: **Anderson 1995** (makes Hartle's rule causal by keeping only the unitary part of the evolution through the CTC region, which removes the consistency selection) and **Kent 2002** (nonlinear evolution that depends only on outcomes recorded in the past light cone cannot signal; PPS needs the larger region outside J⁺(M) because it renormalizes). Rosenberg 1997 quantifies the acausality of Hartle's rule; Shepelin et al. 2021 (S-CTC) uses worlds of recorded outcomes inside the loop but avoids signalling only by averaging two loop topologies.

### Added 2026-11-25: discrete and emergent spacetime, Wolfram model

These bear on the light-cone and wormhole models in [ctc/timeless/README.md](ctc/timeless/README.md) and on Theorem 5 ([ctc/THEOREMS.md](ctc/THEOREMS.md)). Theorem 5 is a statement about any finite causal order, which is why discrete and emergent spacetime programmes are relevant.

**Wolfram 2020, A class of models with the potential to represent fundamental physics, arXiv:2004.08210, Complex Systems 29(2), 107–536 [Sections 8.1, 8.3 (translation table), 8.6, 8.11–8.14 read on wolframphysics.org, 2026-11-25, plus passages of 5.19, 6.9 and a keyword search of Sections 5, 6 and 8; Sections 2–4 and the rest not read].**

- *The model.* Hypergraph rewriting. Space emerges from the hypergraph and spacetime from the causal graph of update events. The analogue of a light cone is the set of events reachable in that graph; events that cannot reach each other are spacelike.
- *Relativity.* If the rule is causally invariant, every foliation (update order) gives the same causal graph. The paper argues that the Lorentz transformation is then the unique straight-line relabelling that preserves the causal order, so special relativity "can be derived" from the model (8.6).
- *Its own caveat.* Section 8.1 calls the correspondence with physics "merely an indication—and sometimes a speculative one".

*Closed timelike curves (8.11, 6.9, 8.3).*
- They correspond to **loops in the causal graph, "only possible in some rules"**. They "do not represent any real form of 'time travel'", only exactly repeated states.
- Loops make a progressive foliation impossible; 6.9 likens this to a failure of strong hyperbolicity.
- Wormholes and effective faster-than-light travel are "not specifically excluded". Where general relativity is the limit, they occur only where it allows them.
- *Weights with loops (5.19).* Path counting in a weighted multiway graph becomes ill-defined with loops; the paper suggests the convention of counting paths only up to the first encounter with a state. **That convention is the slot where a loop's consistency rule (D-CTC, P-CTC, PPS) would go; the paper leaves it as a convention.**

*Quantum mechanics (8.12–8.14).*
- The model is deterministic. All histories sit in one multiway graph, described as an objective reality. Probabilities are said to come from "the locality of our experience".
- An observer is a foliation of the multiway graph (a "quantum observation frame"). A measurement is a foliation that "freezes time" on a generational state.
- Causal invariance makes branches reconverge. An observer can also conflate branches by "adding lemmas" (completions).
- Decoherence is the forced spreading of the frozen region.
- Amplitudes: magnitudes come from path counts. Phases come from the "turning" of paths in branchial space, taken to be proportional to energy times time, which gives e^{iHt} and e^{iS}.
- **No probability rule is given.** The words "probability" and "Born" do not occur in 8.13–8.14. There are no quantitative predictions, and the paper has drawn strong criticism (for example Aaronson: too flexible to be tested).

*Relation to this project.*
- The interface would be the causal graph. Theorem 5 uses only the causal order, so it would carry over.
- Their observer-chosen frame and our records play similar roles: both decide what counts as definite. But their frames are a description chosen by the observer, while our records are physical interactions (Theorem 4).

**Gorard, answer in the Wolfram Physics Project FAQ, "Spacetime / Relativity" (2020) [search snippet].**
- It states that closed timelike curves are forbidden by causal invariance, and that one would appear as a cycle in the multiway evolution graph.
- This is **in tension with the 2020 paper itself**, which says loops in the causal graph occur with some rules (see above). A 2020 working notebook on foliations still lists "can a causal graph have closed timelike curves?" as open.
- Relation: whether loops at the bottom layer are impossible (FAQ) or possible but only as repeated states (paper) is unsettled in the programme's own sources. In either reading, a time loop of our kind (information sent to an earlier event) would have to be emergent. Its consistency rule would then come from the weighting convention for multiway paths, which no paper found here derives.

**Wüthrich 2019, Time travelling in emergent spacetime, arXiv:1907.11167 (in Madarász and Székely (eds.), Hajnal Andréka and István Németi on Unity of Science, Springer 2021) [abstract].** Argues that a fundamental theory may forbid closed timelike curves while the spacetime emerging from it still allows them, and discusses causal set theory among the candidates. Philosophy of physics; no calculation. Relation: this is the layered scenario in which the wormhole model of ctc/timeless/wormhole.py would be an effective description.

**Dündar, Arsiwalla, Elshatlawy 2025, Quantum gates from Wolfram model multiway rewriting systems, arXiv:2512.20587 [abstract].** Multiway systems of cyclic character strings with a neighbourhood constraint ("Leibnizian strings"). Their S-matrices give explicit qubit and qudit gates, including CNOT, Hadamard and π/8, which form a universal set. Relation: every circuit in this project uses gates from such a set, so in principle its causal graphs could be generated by rewriting. Not checked here.

**Gorard 2020, Algorithmic causal sets and the Wolfram model, arXiv:2011.12174 [abstract].** Treats hypergraph rewriting as a dynamics for causal sets, and argues that causal invariance gives conformal invariance of the induced causal order. Relation: it confirms that the causal order is the common language of these programmes and of Theorem 5.

**Gell-Mann and Hartle 2019, Alternative decohering histories in quantum mechanics, arXiv:1905.05859 [full].** Strong decoherence through generalized records. Compared with Theorem 4 in [ctc/THEOREMS.md](ctc/THEOREMS.md): it has the same record structure, without the restriction to the outside of the loop's causal future.


---

## 3. Possible gaps (in priority order)

Ranking: how much existing code is reused, whether a checkable result is reachable in 1–2 months, and confidence that the question is apparently open. **Every "not found" means only "not found in this search".**

### Gap 1: closed-form comparison for the "motivated sender" family, and a general theorem (b′)

- **Why it may be open:** (a) is known; the motivated sender of (b) is (a) plus probabilities and a receiver, and I found no paper on it. Most P-CTC/D-CTC comparisons in the literature concern computational power or state discrimination, not "how much future statistics differ in probabilistic scenarios".
- **What a first result looks like:** a proposition that for classical reversible circuits with classical random inputs, the P-CTC output distribution equals P_0 conditioned on "a fixed-point history exists" (the precise version of H2(2)), while the D-CTC output equals the fixed-point channel; plus a full (q, r) phase diagram of (b) marking where the rules differ most (including the boundary qr = 1 where P-CTC is undefined).
- **Status (11-24):** the PPS version is proved as Theorem 2 in [ctc/THEOREMS.md](ctc/THEOREMS.md); the KFK closed forms are in [ctc/BRANCHES.md](ctc/BRANCHES.md) and [ctc/PAST_PRESERVING.md](ctc/PAST_PRESERVING.md). The full phase diagram has not been drawn.

### Gap 2: "freedom of choice" as a criterion for H2, connecting to process matrices

- **Why it may be open:** process matrices and the deterministic framework of Baumeler et al. require consistency for every local operation, so no renormalization is needed and there is **no H2-style reweighting**; P-CTC's reweighting is exactly the price: conditioning on consistent events changes the distribution of the CR input itself. Araújo et al. say process matrices are a linear special case of P-CTC. I found no discussion using "does P_loop change the CR input distribution?" as the criterion separating "freedom of choice preserved" from "postselection".
- **What a first result looks like:** define Δ = change of the CR input marginal (P_loop vs P_0); show that Δ = 0 is equivalent to the process being consistent for all inputs (no normalization needed), and Δ > 0 is P-CTC's reweighting.
- **Status (11-24):** largely superseded. [ctc/NO_SIGNALLING.md](ctc/NO_SIGNALLING.md) showed that Δ > 0 is equivalent to signalling, and past-preserving selection keeps Δ = 0 by construction (Theorem 2(1)). The process-matrix restatement is still open (roadmap phase 2).

### Gap 3: observables separating P-CTC and D-CTC, aligned with the Lloyd/Ralph dispute

- **Why it may be open:** (c) agrees with Lloyd's description, but the "completely mixed" wording needed reconciling (**resolved 11-22**, see the table); the Ralph–Lloyd dispute (signalling to the past, the unproved theorem) stopped at mutual replies, and I found no decisive later analysis.
- **What a first result looks like:** a table giving, for (c) and for Ralph's entangled construction, the values of {Z, X, correlation with a reference system} under P-CTC, D-CTC and T-CTC, marking which differences come from the rule and which from the choice of baseline.
- **Status (11-24):** the bootstrap observables for all four rules are in [ctc/T_CTC.md](ctc/T_CTC.md); Ralph's construction has not been implemented.

### Gap 4: sensitivity to the choice of D-CTC fixed point

- **Why it may be open:** Deutsch's maximum-entropy rule is an extra assumption (Lloyd et al. PRD [full]); Ralph says it has been derived independently (citation [full], derivation not read); the project uses the Cesàro average from the maximally mixed state, which is not guaranteed to be the maximum-entropy one. I found no systematic comparison of selection rules on circuits with non-unique fixed points.
- **What a first result looks like:** a small circuit where the Cesàro limit and the maximum-entropy fixed point differ (if one exists), or a proof that they agree on a class of circuits (such as classical reversible ones).
- **Status (11-24):** not started.

### Gap 5: adding T-CTC as a third rule and rerunning (a)(b)(c)

- **Status (11-22): done.** T-CTC is implemented with Allen's Eqs. 24, 33, 35, 38 and 40 reproduced, and compared on every scenario; see [ctc/T_CTC.md](ctc/T_CTC.md).

### Gap 6 (higher risk, longer): probabilistic "freedom of choice + consistency"

- **Why it may be open:** Baumeler et al. and Tobar–Costa are deterministic; Baumeler et al. say it is unclear whether quantization is possible ([HTML/abstract+]). The relation between probabilistic, non-deterministic processes and P-CTC's reweighting does not appear in what I read.
- **What a first result looks like:** a small example showing whether a classical probabilistic process conditioned on its consistent set can still preserve freedom of choice, or a counterexample.
- **Note:** the counterexample in 2512.23599 to the characterization theorem may affect the starting point; read it first.
- **Status (11-24):** not started.

---

## 4. References

Only entries for which I actually saw an identifier or DOI. Levels as defined at the top.

| Entry | Link | Level |
|---|---|---|
| Deutsch 1991, Phys. Rev. D 44, 3197 | https://doi.org/10.1103/PhysRevD.44.3197 | bibliographic only |
| Lloyd et al. 2011, PRL 106, 040403 (arXiv:1005.2219) | https://arxiv.org/abs/1005.2219 ; https://doi.org/10.1103/PhysRevLett.106.040403 | full |
| Lloyd et al. 2011, PRD 84, 025007 (arXiv:1007.2615) | https://arxiv.org/abs/1007.2615 ; https://doi.org/10.1103/PhysRevD.84.025007 | full (partial) |
| Lloyd et al. reply (arXiv:1108.0153) | https://arxiv.org/abs/1108.0153 | abstract + ar5iv summary |
| Ralph comment (arXiv:1107.4675) | https://arxiv.org/abs/1107.4675 | full |
| Svetlichny, Int. J. Theor. Phys. 50, 3903 (arXiv:0902.4898) | https://doi.org/10.1007/s10773-011-0973-x ; https://arxiv.org/abs/0902.4898 | abstract |
| Bennett & Schumacher 2005 talk | none (known through Svetlichny's citation, not read) | unverified content |
| Brun, Harrington, Wilde 2009 (arXiv:0811.1209) | https://arxiv.org/abs/0811.1209 | figures and related text (after 11-22) |
| Bennett, Leung, Smith, Smolin 2009 (arXiv:0908.3023) | https://arxiv.org/abs/0908.3023 | full (partial) |
| Aaronson & Watrous 2009 (arXiv:0808.2669) | https://arxiv.org/abs/0808.2669 | abstract + contents |
| Brun & Wilde 2012 (arXiv:1008.0433) | https://arxiv.org/abs/1008.0433 ; https://doi.org/10.1007/s10701-011-9601-0 | abstract + section titles |
| Ralph & Myers 2010 (arXiv:1003.1987) | https://arxiv.org/abs/1003.1987 | abstract |
| Pienaar, Ralph, Myers 2013 (arXiv:1206.5485) | https://arxiv.org/abs/1206.5485 | abstract |
| P-CTC scrambling decoding on IBM / Quantinuum (arXiv:2501.16335) | https://arxiv.org/abs/2501.16335 | search results only (added 11-24) |
| Ringbauer et al. 2014 (arXiv:1501.05014) | https://arxiv.org/abs/1501.05014 ; https://doi.org/10.1038/ncomms5145 | abstract |
| Allen 2014 (arXiv:1401.4933) | https://arxiv.org/abs/1401.4933 | full (partial) |
| Bub & Stairs 2014 (arXiv:1309.4751) | https://arxiv.org/abs/1309.4751 | full (later, see NOVELTY_CHECK.md) |
| Dunlap 2015 (arXiv:1510.02742) | https://arxiv.org/abs/1510.02742 | abstract |
| Echeverria, Klinkhammer, Thorne 1991 | https://www.osti.gov/biblio/5219973 | bibliographic record only |
| Politzer (hep-th/9207076); Hartle (gr-qc/9309012) | https://arxiv.org/abs/hep-th/9207076 ; https://arxiv.org/abs/gr-qc/9309012 | Politzer abstract; Hartle full (11-24) |
| Oreshkov, Costa, Brukner 2012 (arXiv:1105.4464) | https://arxiv.org/abs/1105.4464 ; https://doi.org/10.1038/ncomms2076 | abstract |
| Araújo, Feix, Navascués, Brukner 2017 (arXiv:1611.08535) | https://arxiv.org/abs/1611.08535 ; https://doi.org/10.22331/q-2017-04-26-10 | abstract |
| Baumeler & Wolf 2014 (arXiv:1312.5916) | https://arxiv.org/abs/1312.5916 | abstract |
| Baumeler & Wolf, Computational tameness (arXiv:1611.05641) | https://arxiv.org/abs/1611.05641 | abstract |
| Baumeler, Feix, Wolf (arXiv:1403.7333) | https://arxiv.org/abs/1403.7333 | search results only |
| Baumeler et al. 2019 (arXiv:1703.00779) | https://arxiv.org/abs/1703.00779 | HTML/abstract+ |
| Tobar & Costa 2020 (arXiv:2001.02511) | https://arxiv.org/abs/2001.02511 ; https://doi.org/10.1088/1361-6382/aba4bc | HTML/abstract+ |
| Araújo, Guérin, Baumeler 2017 (arXiv:1706.09854) | https://arxiv.org/abs/1706.09854 | Sections I–III (later) |
| Dourdent et al. 2025 (arXiv:2512.23599) | https://arxiv.org/abs/2512.23599 | abstract |
| Jean, Silva, Vilasini 2025 (arXiv:2508.02463) | https://arxiv.org/abs/2508.02463 | abstract |
| Arvidsson-Shukur et al. 2023 (arXiv:2207.07666) | https://arxiv.org/abs/2207.07666 | abstract |
| Aaronson, Bavarian, Gueltrini (arXiv:1609.05507) | https://arxiv.org/abs/1609.05507 | search results only |
| Wolfram 2020 (arXiv:2004.08210), Complex Systems 29(2) 107–536 | https://arxiv.org/abs/2004.08210 ; https://wolframphysics.org/technical-introduction/ | Sections 8.1, 8.3, 8.6, 8.11–8.14; passages of 5.19, 6.9 (2026-11-25) |
| Gorard, Wolfram Physics FAQ: Spacetime / Relativity | https://wolframphysics.org/questions/spacetime-relativity | search snippet |
| Wüthrich 2019 (arXiv:1907.11167) | https://arxiv.org/abs/1907.11167 | abstract |
| Dündar, Arsiwalla, Elshatlawy 2025 (arXiv:2512.20587) | https://arxiv.org/abs/2512.20587 | abstract |
| Gorard 2020, Algorithmic causal sets (arXiv:2011.12174) | https://arxiv.org/abs/2011.12174 | abstract |
| Gell-Mann & Hartle 2019 (arXiv:1905.05859) | https://arxiv.org/abs/1905.05859 | full (2026-11-25) |
| Morris, Thorne, Yurtsever 1988, PRL 61, 1446 | https://doi.org/10.1103/PhysRevLett.61.1446 | bibliographic only |
| Anderson 1995, Unitarity restoration with CTCs (gr-qc/9405058) | https://arxiv.org/abs/gr-qc/9405058 | full (2026-11-26) |
| Rosenberg 1997, Testing causality violation with CTCs (hep-th/9707103) | https://arxiv.org/abs/hep-th/9707103 | full (2026-11-26) |
| Kent 2002, Nonlinearity without superluminality (quant-ph/0204106) | https://arxiv.org/abs/quant-ph/0204106 | full (2026-11-26) |
| Hartle 1997, Quantum pasts and the utility of history (gr-qc/9712001) | https://arxiv.org/abs/gr-qc/9712001 | full (2026-11-26) |
| Shepelin et al. 2021, Multiworld motives by CTCs, J. Phys. Conf. Ser. 2081, 012029 | https://doi.org/10.1088/1742-6596/2081/1/012029 | full (2026-11-26) |
| Lee 2011, A finite state model for time travel (arXiv:1101.1927) | https://arxiv.org/abs/1101.1927 | full (2026-11-26) |
| Paganini 2020, No events on closed causal curves (arXiv:2005.05748) | https://arxiv.org/abs/2005.05748 | full (2026-11-26) |
| Bishop, Costa, Ralph 2024 (arXiv:2407.14577) | https://arxiv.org/abs/2407.14577 | partly (2026-11-26) |

---

## 5. Limitations

- **Most papers were not read in full.** Only 5 had their PDF text extracted and relevant passages read when this review was written, and only Lloyd et al. PRL was read fairly completely; most entries rest on abstracts or search snippets. Anything marked "[abstract]" represents only what the abstract says, not what the paper proves.
- **PDF extraction:** the web fetcher returned compressed streams for PDFs, so text was extracted locally with `pdftotext`. The converted text has damaged formula symbols (ψ, ρ, † and so on), so formulas were read from context and should not be copied directly.
- **Not read or not verified:** Deutsch 1991, Novikov's original paper, the Bennett–Schumacher talk, Aaronson–Watrous on multiple fixed points, Ralph–Myers' maximum-entropy derivation, the general N-state construction of Brun–Harrington–Wilde, Brun–Wilde's PP result itself, the discussion after Ralph's comment and Lloyd's reply, the bodies of Oreshkov–Costa–Brukner and Araújo et al. (including whether the original process is purifiable), and the contents of 1403.7333 and 1507.01714. No primary source was found for Hawking's chronology protection or the Deutsch–Lockwood popular article, so they are not cited.
- **"Apparently open" does not mean "not done".** The judgments rest on a limited search (about 20 searches, about 10 PDF text extractions), without sweeping all later work citing these papers, conference papers or theses. Each gap needs targeted citation tracking before work starts.
- **Two derivations of our own were not checked against the literature:** the Tr[W] = 0 corner case of H3, and the Δ indicator of gap 2. Both are ideas derived directly from the formulas in HYPOTHESIS.md, not literature results.
- **`ctc/` was not rerun** for this review, and the numbers in ctc/README were not checked; the (a)(b)(c) numbers in the table are quoted from that README.
- **Method:** web search and page fetching, with subagents fetching pages; their reports were treated as data, and their content was cross-checked against PDF text I read myself before being written down (Lloyd, Ralph, Allen, BLSS). Other details (for example of 2508.02463, 2512.23599 and 1108.0153) rest only on subagent summaries and were not independently checked.
- **AI assistance:** written by Claude, with no external review. Do not treat any cell as a verified literature fact until it has been checked against the original by a person.
- This document does not claim that information can be sent to the past; all discussion concerns the behaviour of mathematical models.
