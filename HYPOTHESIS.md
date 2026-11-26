# Precise statement of the hypotheses

Written with AI assistance (Claude). This is a working draft, not a proven result.

The original hypotheses H1–H3 below are kept as first stated. Later work rewrote them into the provable forms H1′–H3′ ([ctc/THEOREMS.md](ctc/THEOREMS.md)); how the two relate is summarized in "Current status: three layers" below.

## Setting

Split the world into two parts:

- **CR system** (chronology-respecting): an ordinary system whose time runs forward, with initial state ρ.
- **Loop system**: a system that travels along a closed timelike curve back to the past, for example a message.

Their interaction is a unitary U. The loop system's state at the end of the loop must equal its state at the start. This is "self-consistency".

## Two known consistency rules

**D-CTC (Deutsch 1991)**

The loop state τ must be a fixed point:

    τ = Tr_CR[ U (ρ ⊗ τ) U† ]

The CR output is Tr_loop[ U (ρ ⊗ τ) U† ]. There can be several fixed points. This project picks one by Cesàro averaging from the maximally mixed state. In the examples in `ctc/` this gives the maximum-entropy fixed point, but that is not guaranteed in general.

**P-CTC (Lloyd et al. 2011, based on Bennett's and Svetlichny's postselected teleportation)**

Let C = Tr_loop[U], the partial trace of the operator itself. The CR output is

    ρ_out = C ρ C† / Tr[C ρ C†]

If Tr[C ρ C†] = 0 there is no consistent history at all: a true paradox, and the rule is undefined.

## Hypotheses

**H1 (self-consistency):** only histories that satisfy the consistency condition occur.

**H2 (effect in the future):** let P_loop(o) be the distribution of a CR observable o with the loop, and P_0(o) the distribution for the same U with the loop input replaced by an ordinary external input. H2 claims:

1. the difference between them is observable;
2. the difference is fully determined by "removing inconsistent histories and renormalizing".

Under P-CTC, for classical reversible circuits, this reweighting is

    P_loop(history) ∝ P_0(history) × [history is consistent]

Under D-CTC, consistency is reached by the loop system becoming mixed, and the future is not necessarily reweighted. The grandfather-paradox example in `ctc/` shows exactly this difference.

**H3 (recovery of causality):** when U does not let the loop system influence the CR system, P_loop = P_0, i.e. ordinary causal quantum mechanics.

## Current status: three layers

Sorted by distance from what has been proved, the hypotheses fall into three layers. Assumptions and falsification conditions for each layer are in [PERSPECTIVES.md](PERSPECTIVES.md), section 1.

| | Inner layer: proved theorems | Middle layer: general finite-dimensional quantum systems | Outer layer: the real universe |
|---|---|---|---|
| Statement | Under past-preserving selection (PPS), H1′–H3′ hold | The same conclusions hold for any quantum interaction, and PPS is the only reasonable rule | If the universe has time loops, H1–H3 describe what actually happens |
| Scope | finite dimension; classical reversible circuits; controlled-form U; record basis from readout interactions; any finite causal order of events (discrete spacetime, flat or curved, any dimension) | finite dimension; any U, any entanglement; record basis set by the dynamics | continuous curved spacetime, quantum fields, gravity |
| Nature | mathematical theorems | mathematical problems plus some physical choices | physical claim |
| Status | proved, checked numerically, measurable on hardware | partly done; "PPS is the only reasonable rule" proved under the superposition principle inside a world, composition and loop-relabelling invariance (Theorem 6; false without the superposition principle) | not testable at present |

How far each hypothesis has got:

| | Inner layer | Middle layer | Outer layer |
|---|---|---|---|
| **H1** | Theorem 1: a world with a consistent history shows only consistent outcomes; a paradox world gets the open-loop output, the limit of a loop with a little basis-free noise (Theorem 8; the Deutsch fixed point was the earlier choice). Theorem 1Q: the same for any quantum U, as amplitude consistency in any loop basis. In spacetime, consistency is imposed only on the loop region R = J⁺(M) ∩ J⁻(F) (Theorem 5). Randomness in the loop's operation that nothing outside has recorded is selected like any unrecorded input | the quantum case must first choose logical or amplitude consistency | Novikov's self-consistency principle; consistent solutions of the billiard-ball paradox are not unique. A concrete general-relativistic stage: the Morris–Thorne–Yurtsever wormhole time machine (simulated in `ctc/timeless/wormhole.py`), which needs exotic matter |
| **H2** | Theorem 2: the past is unchanged; inside each world the future is conditioned on consistency. Theorem 5: in spacetime, "the past" is everything outside the causal future J⁺(M) of the loop's past mouth, and it is unchanged on every slice, in every frame | how the record basis is fixed. Theorem 4 settles it for readout interactions; its records are Gell-Mann–Hartle generalized records restricted to lie outside J⁺(M). Theorem 7: under state completeness, the eigenbasis of the input's reduced state, for every interaction and for weak records | whether the effect is observable in a real environment |
| **H3** | Theorem 3: controlled-form U, which is exactly the class of U that cannot change A's record (Lemmas 3.1–3.2), with the controlled value recorded outside. Theorem 5: wherever no causal path connects to the loop, the state is exactly the no-loop state; P-CTC fails this (a record with no causal curve to the loop still changes, 0.5 → 1/3) | settled for every U that does not act back (Lemmas 3.1–3.2); remaining: PPS treats the loop's own weak reading of A as perfect | quantum fields at the loop boundary (Kay–Radzikowski–Wald 1997); chronology protection (Hawking 1992). If spacetime is emergent (Wolfram model, causal sets), the loop may exist only in the effective description (Wüthrich 2019) |

**Moving inward, the hypotheses were rewritten, and the no-signalling condition forced the rewrite:**

- H1 went from "paradoxical histories do not happen" to "a paradox world survives, and the loop message becomes mixed". Deleting recorded past worlds is exactly why P-CTC signals.
- H2 went from "remove inconsistent histories and renormalize" to "renormalize only inside each recorded past world". Reweighting the whole world is equivalent to faster-than-light signalling ([ctc/NO_SIGNALLING.md](ctc/NO_SIGNALLING.md)).
- The original H3 has a counterexample under P-CTC: a bit that only controls the loop, and is not affected by it, still has a branch deleted (THEOREMS.md, remark after Theorem 3). It holds under PPS.
- H2's "past" went from "earlier in time" to "outside the loop's causal future J⁺(M)" (Theorem 5). In relativity there is no single "earlier". Of the definitions tried in [ctc/timeless/README.md](ctc/timeless/README.md), a time slice depends on the frame, the causal past contains the loop region itself once the loop is closed, and "records the loop cannot change" lets a later choice change earlier statistics. Only the complement of J⁺(M) works for every observer without signalling into the past.
- H2's "effect" depends on more than states. Whether randomness in the loop's operation was recorded outside J⁺(M) changes the prediction, even when the operation's CP map is the same ([ctc/THEOREMS.md](ctc/THEOREMS.md), "Is PPS linear in the loop's own operation?").

**Between the layers:** the inner layer holding does not mean the universe works this way. Conversely, even if the universe has no time loops, the inner layer is still correct mathematics: it says what would happen if there were loops and the rule were PPS.

## Choice of time picture

| | A: single timeline | B: branching timelines |
|---|---|---|
| Matching rule | P-CTC | D-CTC (Deutsch's many-worlds reading) |
| Grandfather paradox | events that would make the paradox happen get probability zero; the rest is renormalized | the loop message becomes mixed |
| KFK-type warning | the warner's own future must also be consistent | the warning arrives in another branch |

## Open questions

1. If nature allows loops, which rule does it use? Or a third one?
2. Is there an experimental signature that separates a real loop from ordinary postselection?
3. What mathematical condition does H2 correspond to in the process-matrix framework?
   *Partial answer (2026-11-25):* none. Process matrices are linear in each party's operation; H2′ under PPS is linear only when the randomness in the loop's operation is recorded outside the loop's causal future, so PPS is not a process matrix. Whether this is a new kind of non-signalling loop rule or a flaw has not been checked with several parties, and no literature search was made ([ctc/THEOREMS.md](ctc/THEOREMS.md), "Is PPS linear in the loop's own operation?").
