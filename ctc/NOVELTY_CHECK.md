# Novelty check: no-signalling tests, the κ–β model and past-preserving selection

First round 2026-11-22; second round the same day; third round 2026-11-24 (past-preserving selection vs. Hartle 1994). Written with AI assistance (Claude). Scope is limited: a few rounds of web search, with five papers read in the original (Bub–Stairs in full; Araújo–Guérin–Baumeler Sections I–III; most of Allen 2014; Silva et al. 2017 in full; Hartle 1994, see the third round). Other judgments rest on abstracts. No expert has confirmed any of this, so "not found" does not mean "nobody has done it".

## Summary

| Result of this project | In the literature? | Judgment |
|---|---|---|
| P-CTC lets Alice signal faster than light to a Bob who shares entanglement | **Yes.** Bub & Stairs 2014, Section III, argue explicitly that P-CTCs allow superluminal signalling | not new |
| Whether D-CTC signals depends on how the rule is applied (reduced state vs. branch by branch) | **Largely yes.** Cavalcanti–Menicucci–Pienaar 2012 (the preparation problem) and Bennett et al. 2009 (the linearity trap) show that D-CTC's predictions depend on how a mixed input is decomposed. Bub & Stairs 2014, Section II, discuss a related issue in different terms: D-CTC's outcome depends on the reference frame in which the state is regarded as entangled. None of them states the "reduced state vs. branch by branch" contrast exactly as here | not new in substance |
| P-CTC does not signal ⇔ C†C ∝ 𝟙 | **In substance.** Araújo–Guérin–Baumeler 2017, Section III: the P-CTC map is linear if and only if the postselection probability is constant for all local operations and inputs, which is exactly the process-matrix case. They prove the linearity condition but do not discuss signalling; the C†C form is not stated but is the direct single-party consequence | very little new |
| Classical κ–β two-parameter model (P-CTC and D-CTC as corners) | No continuous family interpolating the two was found. **Closest prior work: Allen 2014**, who writes T-CTC as a weighted mixture of P-CTC and an ordinary quantum channel (Eq. 33) and says transition-probability theories form a class with no unique integration measure. He gives one point, not a continuous family, and does not connect it to D-CTC (second round, original read) | possibly new, but less new than first estimated; any paper must cite Allen 2014 and explain the difference |
| In the κ–β family, "reweighting" and "signalling" are the same thing (Proposition 1) | No explicit statement found. Implicit in spirit in the Baumeler–Wolf definition of classical process functions (a unique, normalized consistent solution for every local operation, i.e. no reweighting allowed) | low to moderate novelty |
| Past-preserving selection (PPS) | **Partly.** The rule inside each recorded world is Hartle 1994, Eq. (5.6). Hartle's framework reweights the recorded past; PPS does not, and Hartle does not propose that version (third round) | the within-world rule is known; only the "do not reweight the recorded past" modification may be new |

**Overall:** the core no-signalling conclusions (reweighting implies signalling; P-CTC signals; D-CTC's signalling depends on interpretation) are known. This project reproduces them independently. What may be new is the κ–β interpolation with its signalling map, and the causal modification of Hartle's rule (PPS) with the theorems H1′–H3′.

## What this means for the project

1. **Good news:** the code independently reaches conclusions consistent with Bub–Stairs and Araújo et al., which is external support for its correctness.
2. **Bad news:** "H2 and no-signalling exclude each other" cannot be the main contribution of a research note; it is already known that nonlinear P-CTC signals and that its linear version (the process matrix) does not reweight.
3. **Araújo et al. clarify H2's position:** non-signalling P-CTC is exactly the process matrix. So the route "keep consistency, give up reweighting" already has a complete framework in the literature (phase 2's process matrices). If H2 is rewritten, the question is: what observable future effect can a loop still leave in the process-matrix framework?

## Sources read

- J. Bub, A. Stairs, "Quantum Interactions with Closed Timelike Curves and Superluminal Signaling", [arXiv:1309.4751](https://arxiv.org/abs/1309.4751) (full text). Their signalling conclusion rests on a consistency condition they propose; Bennett et al. disagree.
- M. Araújo, P. A. Guérin, Ä. Baumeler, "Quantum computation with indefinite causal structures", Phys. Rev. A 96, 052315 (2017), [arXiv:1706.09854](https://arxiv.org/abs/1706.09854) (Sections I–III in the original; Section VI onward not read). Sections I–III do not mention signalling.
- E. Cavalcanti, N. Menicucci, J. Pienaar, "The preparation problem in nonlinear extensions of quantum theory", [arXiv:1206.2725](https://arxiv.org/abs/1206.2725) (abstract only).
- J.-M. A. Allen, "Treating Time Travel Quantum Mechanically", Phys. Rev. A 90, 042107 (2014), [arXiv:1401.4933](https://arxiv.org/abs/1401.4933) (original read up to Section V; only the last ~19,000 characters not read).
- R. Silva et al., "Connecting processes with indefinite causal order and multi-time quantum states", New J. Phys. 19, 103022 (2017), [arXiv:1701.08638](https://arxiv.org/abs/1701.08638) (full text).
- J. B. Hartle, "Unitarity and causality in generalized quantum mechanics for nonchronal spacetimes", Phys. Rev. D 49, 6543 (1994), [arXiv:gr-qc/9309012](https://arxiv.org/abs/gr-qc/9309012) (full text; see the third round).
- T. C. Ralph, "Problems with modelling closed timelike curves as post-selected teleportation", [arXiv:1107.4675](https://arxiv.org/abs/1107.4675); S. Ghosh et al., "Quantum Signaling to the Past Using P-CTCs", [arXiv:1708.03521](https://arxiv.org/abs/1708.03521) (search snippets only; both concern signalling to the past, not spacelike signalling).
- The Baumeler–Wolf papers on classical process functions, and [arXiv:2512.23599](https://arxiv.org/abs/2512.23599) (search snippets only).

## Second round (same day)

**Allen 2014, Section IV C to most of Section V read in the original:**

- Definition of T-CTC (Eqs. 24–26): a Haar integral over all pure loop states. The closed form (Eq. 33) is a P-CTC term plus d times the "fully random loop" channel. Allen notes that T-CTC is a weighted mixture of P-CTC and an ordinary channel, which makes it tempting to see it as "noisy P-CTC".
- Transition-probability theories are "a class of theories", because the integration measure has no unique natural choice (§IV E.6).
- "Weighted D-CTC" (§IV C): when D-CTC has several fixed points, give each a weight. This is a selection rule inside D-CTC, not an interpolation towards P-CTC.
- Signalling: §IV E.5 says T-CTC's nonlinearity makes an "entanglement detector" possible, as for D-CTC and P-CTC.
- This project implements T-CTC as a fourth rule and reproduces Eqs. 33, 35, 38 and 40; see [T_CTC.md](T_CTC.md).

**Silva et al. 2017 (full text):** process matrices correspond to a class of "linear" two-time states, for which normalization holds automatically for every local operation, with no measurement-dependent renormalization (Eqs. 19, 21, 29). This is the same as the linearity condition of Araújo et al., but the paper does not discuss CTCs or signalling.

**Search for interpolating families:** several rounds of searches with different keywords found no continuous family interpolating D-CTC and P-CTC. Results were single models, D-CTC plus decoherence (used to select a unique fixed point), or generalizations of P-CTC.

**Updated judgment:** the κ–β model may still be new, but Allen 2014 already took the step "P-CTC mixed with a non-selecting channel", so it is less new than first estimated. The real differences: κ–β is a continuous two-parameter family, its other corner is D-CTC, and it comes with a full signalling map.

## Third round (2026-11-24): past-preserving selection vs. Hartle 1994

**Source:** J. B. Hartle, Phys. Rev. D 49, 6543 (1994), [arXiv:gr-qc/9309012](https://arxiv.org/abs/gr-qc/9309012). **Read in full** (arXiv v1 PDF converted to text, 41 pages, Sections I–VIII and appendix; some formula symbols were damaged in the conversion, and the formulas below were reconstructed from context). Equation numbers follow the PDF's section numbering; the arXiv HTML rendering numbers equations sequentially (for example Eq. (5.5)–(5.6) appear there as (39)–(40)). A second, independent reading on 2026-11-24 confirmed Sections I–III verbatim and Section V at summary level.

### What Hartle does

In a fixed background spacetime with a nonchronal region NC, he uses generalized quantum mechanics (decoherence functionals) to treat a non-unitary evolution X through NC. The central formula is Eq. (3.12):

    D(β′, α′; β, α) = Tr(C_β′ X C_α′ ρ C_α† X† C_β†) / Tr(XρX†)

C_α is a chain of projections before NC, C_β a chain after NC. Whole histories are normalized by one constant, Tr(XρX†).

### Point-by-point comparison

| Item | Hartle 1994 | Past-preserving selection (PPS) |
|---|---|---|
| State after NC | ρ̄ = XρX† / Tr(XρX†) (Eq. 6.7), the P-CTC formula (X corresponds to C). Hartle does not regard it as a state on a spacelike surface | each world k separately: C\|k⟩/‖C\|k⟩‖ |
| Probabilities before NC | p(α) = N·Tr(X C_α ρ C_α† X†) (Eq. 4.1), **changed by the future NC**. Hartle calls this acausal and says comparing (4.1) with (4.2) experimentally could detect a future NC | p(k) = ⟨k\|ρ\|k⟩, **unchanged** |
| Conditional probability given a recorded initial state | §V measurement model: when the initial alternatives α are decohered by a persistent record of an apparatus (Eq. 5.4), p(β\|α) = \|⟨β\|X\|α⟩\|² / Σ_β′ \|⟨β′\|X\|α⟩\|² (Eq. 5.6) | identical (X corresponds to C) |
| Joint probability given a recorded initial state | p(β, α) = N·\|⟨β\|X\|α⟩\|²·⟨α\|ρ\|α⟩ (Eq. 5.5), so p(α) ∝ ⟨α\|ρ\|α⟩·‖X\|α⟩‖², the P-CTC reweighting | p(α) = ⟨α\|ρ\|α⟩ |
| World with no consistent history (X\|α⟩ = 0) | not discussed; (5.6) is 0/0 | falls back to D-CTC |
| Is there a "state"? | explicitly no: no ρ_eff can be defined on a spacelike surface (Section IV) | yes: PPS is an ordinary quantum channel |
| No superluminal signalling | proved in Section VII, assuming the two regions are **initially uncorrelated** and that **their common future contains no NC** (Eqs. 7.6–7.7). Hartle remarks that correlations produced by an NC in the common future deserve study | holds for every shared state (Theorem 0, fixed record basis) |
| Does it propose a version that does not reweight the past? | **No.** Reweighting is treated as a feature of the theory, not a defect to remove | this is the definition of PPS |

### Conclusions

1. **The within-world rule of PPS is not new.** It is Hartle 1994, Eq. (5.6): the conditional probability when the initial state is decohered by a persistent record. It also equals P-CTC acting on a definite input (see [PERSPECTIVES.md](../PERSPECTIVES.md), 1.5).
2. **PPS differs from Hartle in exactly one place, by a deliberately opposite choice:** the probabilities of the recorded past. In Hartle's framework they are reweighted by ‖X\|α⟩‖² (which he calls acausal); PPS keeps them fixed. In Hartle's terms, PPS keeps the conditional probabilities of Eq. (5.6) but replaces the world weights in the joint probability by the causal version of Eq. (4.2).
3. **This causal version does not appear in Hartle 1994.** That is one paper. Later work citing Hartle 1994 has not been checked, and the structure "each recorded world normalized separately" may appear in the decoherent-histories literature.
4. **Relation to this project's no-signalling results.** Hartle's no-signalling proof excludes initial entanglement. The P-CTC signalling examples in [NO_SIGNALLING.md](NO_SIGNALLING.md) use initial entanglement, so there is no contradiction: the project's results fall into the case Hartle explicitly excludes and calls worth studying.
5. **A hint for the record-basis problem.** In Hartle's framework only **decoherent** past alternatives can be assigned probabilities, and when X is non-unitary, which alternatives decohere can itself depend on the future NC (Eq. 4.7). He also notes that real decoherence mechanisms are local in time and largely unaffected by a future NC. This gives PPS a candidate record basis with support in the literature: **the past alternatives decohered by local environmental mechanisms**, in line with the suggestion in PERSPECTIVES.md 3.1 that the basis should be fixed by the interaction, not the state.

**Updated judgment:** PPS cannot be claimed as a new rule as a whole. What may be new reduces to one sentence: in a Hartle-type generalized quantum mechanics, fix the probabilities of recorded past alternatives at their causal values and apply Hartle/P-CTC conditioning only inside each record; the result is a non-signalling quantum channel for which H1′–H3′ hold. Any research note using PPS **must cite Hartle 1994, Eqs. (5.5)–(5.6), and present PPS as a causal modification of Hartle's framework**, not as a new rule.

## Fourth round (2026-11-25): Gell-Mann–Hartle generalized records

Read in full: M. Gell-Mann, J. Hartle, "Alternative decohering histories in quantum mechanics", [arXiv:1905.05859](https://arxiv.org/abs/1905.05859) (a 1990 conference paper posted in 2019).

- **Strong decoherence** (C_α ρ = R_α ρ, with orthogonal "generalized records" R_α) is the same structure as Theorem 4's record sectors. A perfect readout gives it for every input state (tested).
- **Their records are not restricted in time** (any later T), and they set wormholes aside. The restriction to records outside the loop's causal future (Theorem 5) is not in their paper; it is needed only when a loop is present.
- **They say singling out a set needs the Hamiltonian**, but give no rule. Theorem 4's pointer basis is one concrete answer for readouts. It is close to Zurek's einselection, so it is not new as an idea.
- **Judgment:** the record structure is known (Gell-Mann–Hartle, Zurek). What may be new is only its combination with a loop: the causal restriction, and Hartle 1994's within-world rule applied to the resulting worlds.
- A statement attributed to these authors in an earlier search summary, that "persistence of the past is not guaranteed by quantum mechanics alone", was not found in arXiv:1905.05859, 0806.3776 or quant-ph/0609190. It is not used.

## Fifth round (2026-11-25): PPS and process matrices

- Araújo–Guérin–Baumeler 2017 (Sections I–III read earlier): a P-CTC is a process matrix exactly when it is linear in the parties' operations.
- Checked here (`ctc/tests/test_operation_linearity.py`): PPS is linear in a mixture of loop operations if the mixing coin is recorded outside the loop's causal future, and not linear if it is unrecorded. So PPS is not a process matrix.
- No search was made for earlier work on loop rules that are linear in states but not in operations. "Possibly new" here means only "not looked for".

## Not yet checked

- Full citation tracking forward from Lloyd 2011, Allen 2014 and **Hartle 1994** (needs a database with citation lists, such as INSPIRE or Semantic Scholar). Work citing Hartle 1994 is the next step for the novelty of PPS.
- Asking researchers familiar with the CTC literature directly. This is the most reliable way to settle novelty.
