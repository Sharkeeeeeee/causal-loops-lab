# Theorem versions of H1–H3, with proofs (past-preserving selection)

Created 2026-11-23 with AI assistance (Claude). No external review.

```text
python -B ctc/tests/test_theorems.py    # 11 numerical checks; every theorem is verified on random circuits
python -B ctc/tests/test_hardware.py    # circuit and estimator checks for the hardware experiments
```

## What this document proves

It proves conditional statements: **if the consistency rule is past-preserving selection (PPS, defined in [PAST_PRESERVING.md](PAST_PRESERVING.md)), then H1–H3 hold under the conditions written below.** It does not prove that nature has time loops, or that nature uses PPS. No simulation or hardware experiment can show that, because postselection can always be explained in the normal time direction.

Why PPS and not P-CTC: under P-CTC, H2's "reweighting" is faster-than-light signalling ([NO_SIGNALLING.md](NO_SIGNALLING.md)), and H3 has a counterexample (see the remark after Theorem 3). PPS is a rule under which all three hypotheses can hold together while staying compatible with relativity. The choice has a price: all three hypotheses must be rewritten as primed versions (H1′, H2′, H3′). The differences are explained after each theorem.

**Prior work.** The rule PPS applies inside each recorded world is Hartle 1994, Eq. (5.6); PPS differs from Hartle's framework by not reweighting the recorded past. See [NOVELTY_CHECK.md](NOVELTY_CHECK.md), third round.

## Setting and notation

- CR system A (dimension d), loop system L (dimension n), interaction a unitary U on A⊗L.
- C = Tr_L U, the partial trace of the operator itself.
- Record basis {|k⟩}: the past facts in A's input that have already been recorded.
- The PPS rule, for each world k:
  - if C|k⟩ ≠ 0 (world k has a consistent history): Kraus operator K_k = C|k⟩⟨k| / ‖C|k⟩‖;
  - if C|k⟩ = 0 (world k has no consistent history): fall back to D-CTC. Let σ_k = Tr_L[U(|k⟩⟨k|⊗τ_k)U†], where τ_k is the D-CTC fixed point, and σ_k = Σ_j λ_kj |s_kj⟩⟨s_kj|; Kraus operators F_kj = √λ_kj |s_kj⟩⟨k|.
  - Φ(ρ) = Σ K ρ K†, summing over all the Kraus operators above.
- **Classical reversible circuit:** U|x, m⟩ = |f(x,m), g(x,m)⟩, where f and g together form a bijection. A history (x, m) is **consistent** if the loop message is unchanged after one round: g(x, m) = m. The consistent messages of world x are S(x) = {m : g(x,m) = m}. N_xy = #{m ∈ S(x) : f(x,m) = y}.
- **No-loop baseline P_0:** the same U, with the loop input replaced by a uniformly random external message (the maximally mixed state 𝟙/n).

**Lemma 1.** For a classical reversible circuit, ⟨y|C|x⟩ = N_xy, i.e. C|x⟩ = Σ_{m∈S(x)} |f(x,m)⟩.

*Proof.* ⟨y|C|x⟩ = Σ_m ⟨y, m|U|x, m⟩ = Σ_m [f(x,m) = y]·[g(x,m) = m] = N_xy. ∎

So "C|x⟩ = 0" is exactly "world x has no consistent history", and the two cases of PPS are "has a consistent history" and "has none".

## Theorem 0: PPS cannot signal

**Statement.** For any U and any record basis, Σ K†K = 𝟙. So Φ is a linear, completely positive, trace-preserving quantum channel. For any Alice–Bob state ρ_AB, Tr_A[(Φ⊗id)(ρ_AB)] = ρ_B (no signalling Alice → Bob), and no operation Bob performs before the loop changes Alice's output statistics (no signalling Bob → Alice).

*Proof.* For the C terms, K_k†K_k = |k⟩⟨k|·‖C|k⟩‖²/‖C|k⟩‖² = |k⟩⟨k|; the fallback terms give Σ_j λ_kj |k⟩⟨k| = |k⟩⟨k|, since Tr σ_k = 1. Summing over k gives 𝟙. A trace-preserving local channel cannot change the other party's reduced state, and since Φ is linear, Bob's operation and Alice's channel commute. ∎

*Check:* `Theorem0_NoSignalling`: 5 dimensions × 4 random U, random record bases, random entangled states.

**Scope.** Theorem 0 needs a record basis that does not depend on the state. The decoherence-defined rule of [DECOHERENCE.md](DECOHERENCE.md) picks the basis from the state, which makes it nonlinear, so Theorem 0 does not cover it (see [PERSPECTIVES.md](../PERSPECTIVES.md), 3.1).

## Theorem 1 (H1′: every world is self-consistent)

**Statement.** For a classical reversible circuit with the input recorded in the computational basis:

1. **A world with a consistent history shows only outcomes of consistent histories.** If S(x) ≠ ∅, then P(y | x) > 0 only if some m ∈ S(x) has f(x,m) = y. More precisely, P(y | x) = N_xy² / Σ_y′ N_xy′².
2. **In a world with no consistent history, the loop sits at a Deutsch fixed point.** If S(x) = ∅, no definite message value is consistent; PPS puts the loop in a mixed state τ_x with τ_x = Tr_A[U(|x⟩⟨x|⊗τ_x)U†]. Such a fixed point exists for every U (Deutsch 1991).
3. **Defined for every input.** P-CTC is undefined when Tr[CρC†] = 0 (for example the grandfather paradox with ε = 0); PPS has no such gap.

*Proof.* (1) By Lemma 1, world x outputs C|x⟩/‖C|x⟩‖ = Σ_y N_xy|y⟩ / (Σ N²)^{1/2}, and measuring in the computational basis gives N_xy²/ΣN². If N_xy = 0 the probability is 0. (2) This is the definition of the fallback; existence of the fixed point follows from the fixed-point theorem for CPTP maps on the finite-dimensional state space. (3) Every world falls in one of the two cases, and both are defined. ∎

**Difference from the original H1.** The original H1 said "paradoxical histories do not happen". Under PPS the "grandfather paradox world" does not disappear, because it belongs to the recorded past, whose probabilities PPS may not change. Consistency in that world is reached by the loop message becoming mixed (Deutsch-style), not by deleting the world (P-CTC-style). **Deleting past worlds is exactly why P-CTC signals**, so this rewrite is forced by the no-signalling condition, not an arbitrary choice.

**Remark on the quantum case.** The square N² in (1) means amplitudes add, not history counts. Two consistent histories with the same outcome interfere ("logical consistency ≠ amplitude consistency" in [QUANTUM_EFFECTS.md](QUANTUM_EFFECTS.md)). As long as every consistent history leaves a different record, N_xy is 0 or 1 and the two counts agree; see Theorem 2.

*Check:* `Theorem1_Consistency`: 5 dimensions × 10 random bijections. ⟨y|C|x⟩ = N_xy is checked against an independent enumeration of histories; inconsistent outcomes have probability below 10⁻⁹; the D-CTC fixed-point equation is verified in paradox worlds; for the ε = 0 grandfather paradox P-CTC returns "undefined" while PPS gives a normal output.

## Theorem 2 (H2′: the loop changes the future, not the past)

**Statement.**

1. **The past is unchanged.** For any U and any ρ = Σ p_k|k⟩⟨k| diagonal in the record basis, world k still has probability p_k after PPS.
2. **The future changes, entirely by consistency.** For a classical reversible circuit in which the loop message is recorded (every consistent history has a different output, i.e. N_xy ∈ {0, 1}), for every world x with a consistent history:

   P_PPS(y | x) = P_0(y | x, history is consistent)

   That is, the loop's effect is exactly "inside each past world, remove the inconsistent histories and renormalize".
3. **The effect is observable but cannot signal.** Whenever, in some world with p_x > 0, the distribution conditioned on consistency differs from the unconditioned one, P_PPS ≠ P_0, and the difference can be measured (Theorem 0 guarantees it cannot be used to signal).

*Proof.* (1) The Kraus operators of each world k satisfy Σ K†K = 1 on |k⟩ (proof of Theorem 0), so Tr Φ(p_k|k⟩⟨k|) = p_k. (2) With a uniformly random message, P_0(y, m | x) = [f(x,m) = y]/n, so P_0(y | x, m ∈ S(x)) = N_xy/|S(x)|. By Theorem 1, when N_xy ∈ {0,1}, P_PPS(y|x) = N_xy/Σ N = N_xy/|S(x)|. The two are equal. (3) Follows directly from (2). ∎

**Difference from the original H2.** The original H2 said the difference comes from "removing inconsistent histories and renormalizing". That is kept, but renormalization happens only **inside** each recorded past world; the weights between worlds do not change. For systems correlated with the outside, the loop's effect therefore appears only in conditional statistics (for example sorted by another party's measurement result; see the double slit in [PAST_PRESERVING.md](PAST_PRESERVING.md)).

**Example (hardware experiment 2, "refusal to send"):** P(message recorded | a = 1) goes from 0.5 without the loop to 0; P(a = 1) stays at 0.5. P-CTC instead changes P(a = 1) to 1/3, i.e. it changes the past.

*Check:* `Theorem2_FutureNotPast`: world probabilities unchanged (random U); on random bijections with records, PPS equals the conditional distribution computed by enumerating histories; without records, the general N²/ΣN² formula is verified.

## Theorem 3 (H3′: when the loop does not act back, ordinary quantum mechanics returns)

**Statement.** Suppose the loop does not act back on the CR system: U = (V⊗𝟙) Σ_k |k⟩⟨k| ⊗ W_k, i.e. A controls the loop in the basis {|k⟩} and the loop never affects A. Take {|k⟩} as the record basis. Then:

1. For any ρ diagonal in the record basis and any external loop input τ_0, Φ(ρ) = Tr_L[U(ρ⊗τ_0)U†]: **exactly ordinary quantum mechanics without a loop.** Whether the W_k have zero trace does not matter.
2. For any ρ (not necessarily diagonal), the two give the same measurement statistics in the basis {V|k⟩}.
3. Special case: no interaction at all, U = V⊗W, with the eigenbasis of ρ as the record basis: Φ(ρ) = VρV†, **including when Tr W = 0**, where P-CTC is undefined.

*Proof.* C = Tr_L U = Σ_k Tr(W_k) V|k⟩⟨k|, so C|k⟩ = Tr(W_k) V|k⟩.

- If Tr W_k ≠ 0: K_k = e^{iθ} V|k⟩⟨k|, and K_k ρ K_k† = ρ_kk V|k⟩⟨k|V†.
- If Tr W_k = 0: fall back to D-CTC. For any τ, Tr_L[U(|k⟩⟨k|⊗τ)U†] = V|k⟩⟨k|V†·Tr(W_kτW_k†) = V|k⟩⟨k|V†, so σ_k = V|k⟩⟨k|V† and the contribution is again ρ_kk V|k⟩⟨k|V†.

So Φ(ρ) = V Δ(ρ) V†, where Δ removes the off-diagonal terms in {|k⟩}. Without the loop, Tr_L[U(ρ⊗τ_0)U†] = V Σ_{k,k′} ρ_kk′ Tr(W_k τ_0 W_k′†) |k⟩⟨k′| V†, whose diagonal terms are ρ_kk (since Tr(W_kτ_0W_k†) = 1). For diagonal ρ the two agree, which is (1); for general ρ the diagonals agree, which is (2). (3) is the case W_k = W for all k, with the basis chosen as the eigenbasis of ρ so that Δ(ρ) = ρ. ∎

**The record basis is fixed naturally here:** it is the basis in which the loop reads A. The loop itself is a record of A in that basis.

**P-CTC counterexample.** Take V = 𝟙, W_0 = 𝟙, W_1 = X (A controls a NOT on the loop), ρ = 𝟙/2. The loop never acts on A, yet C = 2|0⟩⟨0|, and P-CTC deletes the a = 1 world entirely: P(a = 1) = 0, while ordinary quantum mechanics gives 0.5. With U = 𝟙⊗Z (the loop only picks up a phase), C = 0 and P-CTC is undefined. So the original H3 fails under P-CTC and holds under PPS.

*Check:* `Theorem3_CausalityRecovered`: 5 dimensions, W_k a random mix of generic and zero-trace unitaries, always including at least one paradox world; random V, random external input; plus the P-CTC counterexample above.

## Theorem 4: the record basis comes from the interaction, and then PPS cannot signal

Added 2026-11-24. Theorem 0 needs a record basis that does not depend on the state, but did not say where the basis comes from. Without an answer, the definition of "the past" can quietly fail (see the counterexamples below).

**Setting.** Alice's loop input A (dimension d), the loop L, and an outside system O: everything the loop cannot influence (a distant Bob, an environment). A interaction V on A ⊗ O **reads A in the basis {|k⟩}** if it has the controlled form V = Σ_k |k⟩⟨k| ⊗ V_k, with V_k acting on O. Then O ends up holding a record of k (a perfect one when the states V_k|o⟩ are orthogonal). Call {|k⟩} the **pointer basis** of V (Zurek's einselection).

**Lemma 2 (the pointer basis is found from V alone).** Write V = Σ_i A_i ⊗ B_i (operator Schmidt decomposition). V reads A in some basis if and only if the A_i are normal and commute; the basis is their joint eigenbasis. If the readout is fine (the V_k are distinct), the basis is unique up to order and phases.

*Proof.* (⇒) If V = Σ_k |k⟩⟨k| ⊗ V_k, every V_k lies in the span of the B_i, so each A_i is a linear combination of the projectors |k⟩⟨k|: diagonal in {|k⟩}, hence normal and commuting. (⇐) Commuting normal operators have a joint eigenbasis; with A_i = Σ_k a_ik |k⟩⟨k|, V = Σ_k |k⟩⟨k| ⊗ (Σ_i a_ik B_i). If the V_k = Σ_i a_ik B_i are distinct, the signatures (a_ik)_i are distinct, so the joint eigenspaces are one-dimensional. ∎

A SWAP or a generic entangling unitary has non-commuting A_i: it reads A in no single basis.

**Theorem 4.** Suppose every interaction that correlates A with the outside reads A in the same basis {|k⟩}, and take {|k⟩} as the record basis. Then PPS is the fixed-basis channel of Theorem 0 on A, so:

1. for every joint state produced this way, the outside party's reduced state is unchanged (no signalling Alice → Bob);
2. no operation on O before the loop changes Alice's output (no signalling Bob → Alice);
3. the basis is set by the dynamics, not by the state, so the rule is linear and has no preparation problem.

*Proof.* The basis is a function of the interactions only, so it is the same for every state and every outside operation; Theorem 0 applies as stated. ∎

The proof is one line; the content is the choice. It replaces the state-dependent basis of [DECOHERENCE.md](DECOHERENCE.md) (an eigenbasis of the conditional state, which makes the rule nonlinear) with one fixed by who interacted with what.

**Fresh inputs.** If nothing outside has interacted with A (A is pure and uncorrelated), no basis is singled out. Any choice is safe, since there is nobody to signal to; the natural one, a basis containing the state, gives P-CTC, as for the fresh photon in PAST_PRESERVING.md.

**Three definitions of "the past" that signal.** Alice's loop is one_way (C = diag(2, 0)); a and Bob's b are in |Φ⁺⟩, made by CNOT a → b; nobody wrote a separate record register.

| Definition | What goes wrong | Numbers |
|---|---|---|
| Only explicit record registers count | Bob's qubit is not a "register", so nothing is protected and the rule is P-CTC | Bob's P(Z = 0): 0.5 → 1 |
| Split on Bob's side, sectors added as amplitudes | Bob's sectors interfere when he measures in another basis | X split: Bob's P(Z = 0): 0.5 → 1 |
| Split on Bob's side, sectors mixed | Alice → Bob is fine, but Bob's earlier measurement changes what each sector contains | Bob measures b in X first: Alice's P(a = 0): 0.5 → 1 |
| **Split on Alice's side, in the pointer basis of CNOT (Z)** | nothing | Bob 0.5, Alice 0.5, whatever Bob does |

So the past must be split **on Alice's side**, in a basis **fixed by the interaction**. The first counterexample also corrects [timeless/README.md](timeless/README.md): "records the loop cannot influence" must include every outside system that holds information about A, not only designated record registers.

**The basis matters for Alice's predictions, not for signalling.** Input with P(1) = 0.3, eraser loop (C = diag(2, 1 + i)). If an outside system read A in Z, PPS gives P(a = 1) = 0.3; if it read A in X, 1/3. Neither changes the outside party's statistics. This is the earlier qualitative result "the basis is set by what the environment monitors" (DECOHERENCE.md), now without any dependence on the state.

*Checks:* `ctc/tests/test_records.py`, 11 tests: Lemma 2 on known and random interactions (dimensions 2–4) and on partial records; Theorem 4 on 24 random combinations of loop, readout interaction and outside operation (unitaries and measurements), including paradox worlds; the three counterexamples; the Z-versus-X example.

**Sectors must be mixed, not added as amplitudes.** The second counterexample also applies to the timeless models of [timeless/](timeless/README.md), which first combined record sectors as amplitudes. They now combine them as a mixture; this changed one reported number (the superposed clock, 0.709 → 0.500) and none of the conclusions.

### 4a. Several readouts in incompatible bases

Bob reads A in Z, then Carol reads it in X. The two interactions act on the same system and do not commute, so their order is physical, not a choice of clock. **Rule:** the last readout fixes the record basis; an earlier readout refines it only if it commutes with it. Reason: the loop finds A as the last readout left it (in each world A is in an X eigenstate; the Z information now lives only in Bob's record). Every earlier record stays protected anyway, because the rule is a channel on A and never touches the outside.

Since the basis is again fixed by the interactions, Theorem 0 applies: no signalling. Example (one_way loop, input P(1) = 0.3): with Bob's Z readout alone PPS leaves P(a = 0) at 0.7; after Carol's X readout both worlds |±⟩ are sent to |0⟩, so P(a = 0) = 1, while Bob's record stays 0.7/0.3 and the joint Bob–Carol statistics are unchanged.

### 4b. Coarse readouts

A readout that only tells which block of states A is in (for example {|0⟩} versus {|1⟩, |2⟩}) has blocks instead of a basis; `pointer_blocks` finds them from V. **Rule:** inside each block, the loop acts on A's pre-readout state projected into the block, P ψ / ‖P ψ‖, because nothing distinguished the alternatives inside it. With no readout at all (one block) this is P-CTC on the fresh input.

**Proposition 4b.** If A's state before the readouts is pure and every correlation with the outside comes from the readouts, the rule is a fixed channel given that pre-readout state (Kraus operators C|φ_b⟩⟨φ_b| / ‖Cφ_b‖ per block plus the identity on the unread remainder), so no operation on the outside, unitary or measurement, changes Alice's output, and the outside's marginal never changes.

*Proof.* Within block b the joint state is |φ_b⟩⟨φ_b| ⊗ β_b with φ_b fixed by ψ; an operation on the outside only changes β_b and the block weights cannot change (they are Alice-side probabilities). The Kraus operators depend on ψ, not on the current state, so Theorem 0 applies. ∎

**The premise matters.** If A was entangled beforehand with a hidden partner D by an interaction that read no basis, there is no fixed state inside a block. Applying P-CTC to whatever the block holds then changes D's statistics: the P-CTC signalling mechanism, confined to the block (tested). Such interactions are the remaining open case.

### 4c. Weak readouts

A readout with record overlap c = |⟨V_0 o|V_1 o⟩| (c = 1: no record, c = 0: perfect) still has a pointer basis. Three candidate rules, compared on an input with P(1) = 0.3 and the eraser loop:

| Overlap c | 1 (no record) | 0.995 | 0.825 | 0.540 | 0 (perfect) | Signals? |
|---|---|---|---|---|---|---|
| Pointer basis (Theorem 4 as stated) | 0.176 | **0.300** | 0.300 | 0.300 | 0.300 | no |
| Eigenbasis of A's reduced state | 0.176 | 0.177 | 0.184 | 0.209 | 0.300 | no |
| Worlds = the outside's record states | 0.176 | 0.177 | 0.203 | 0.249 | 0.300 | **yes** (Bob's prior measurement shifts Alice's output by up to 0.046) |

Values are P(a = 1). Findings:

- **No-signalling does not force all-or-nothing.** The eigenbasis rule is continuous (no jump at the first trace of a record) and safe: its basis comes from A's reduced state, which nothing done to the outside can change, so it is a fixed channel with respect to every outside operation.
- **What does signal is splitting on the outside's side,** as in the third counterexample above.
- **The two safe rules disagree on what a weak record means.** The pointer rule says any readout, however weak, fixes the past in its basis. The eigenbasis rule says a weak readout only partly does, and ignores the record's basis where A's spectrum is degenerate (the all-or-nothing case of DECOHERENCE.md is exactly such a degeneracy, ρ = 𝟙/2). They predict different outputs for weak records; which one nature would use is not decided by any principle found here.

*Checks:* `ctc/tests/test_readouts.py`, 10 tests (4a: basis, no signalling under all operations of both outside parties, the one_way example; 4b: block finding, no signalling for random inputs, loops and outside operations, the fresh limit, the premise counterexample; 4c: the table above).

**A consequence for the eraser.** The idler is made by a CNOT, which reads the path in Z. Under Theorem 4 the record basis of the eraser is therefore Z, not the X basis used in [PAST_PRESERVING.md](PAST_PRESERVING.md) and in the hardware design. With Z, PPS makes the loop act like a which-path measurement: the Bob-sorted fringes disappear instead of shifting by π/4. The hardware PPS values for the eraser (visibility 0.870, shift 0.774) are measured values of the X-basis variant, which Theorem 4 does not support.

**Still open.** Interactions that correlate A with the outside without reading any basis (4b premise); the choice between the pointer and eigenbasis rules for weak records (4c); a superposed order of two incompatible readouts (which one is "last" is then indefinite).

## Theorem 5: in spacetime, PPS acts only inside the loop's causal future

Added 2026-11-25. Theorem 4 needs "the outside". In spacetime, this section makes it precise as everything outside the loop's causal future, and shows that PPS then changes nothing outside that future on any slice, in any frame.

**Setting.**

- *Events.* A finite set of events with a causal order, each a unitary on the qubits present at it. Events with no causal relation act on different qubits. Only the order is used, so the background may be flat or curved, in any dimension.
- *The loop.* The past mouth M makes (m, p) in |Φ⁺⟩. The future mouth F closes the loop with the constraint "(m, p) in |Φ⁺⟩", i.e. a causal edge F → M.
- *The loop region* R = J⁺(M) ∩ J⁻(F). These are exactly the events that lie in their own causal past once the loop is closed.
- *Inputs.* The qubits other than m and p that enter R. Every event of an input before it enters R lies outside J⁺(M): an event of J⁺(M) that precedes an event of R lies in J⁻(F), hence in R.
- *The outside slice* σ_out is the set of all events outside J⁺(M). It is a slice, because the complement of the up-set J⁺(M) is a down-set. On it every input stands at its entry into R.

**Rule.** PPS with "the outside" taken to be the complement of J⁺(M):

- split every input in the pointer blocks of the interactions that read it before it entered R (Lemma 2; with several readouts, 4a);
- apply P-CTC inside each joint block, with the D-CTC fallback, and keep each block's weight.

In the timeless picture, slices that contain all of R carry the rule's state, and slices that contain none of R keep the forward history. With the loop closed no Cauchy slice passes through R, so no physical claim is made about slices that split R.

**Theorem 5.** Suppose:

- every interaction of an input with another qubit before R is a readout of the input (Lemma 2);
- the readouts leave rank-one blocks, or none (the input was never read);
- inputs do not interact with each other before R.

Then on every slice σ that contains all of R or none of it, the joint state of all qubits whose latest event in σ lies outside J⁺(M) equals the state without the loop. In particular, a record in the loop's past or spacelike to it is never changed, in any frame.

*Proof.*

1. A slice without R carries the forward history by construction. Let σ contain R.
2. *Inside a joint block, the inputs are in a fixed pure product state.* A read input is in its pure pointer state. A never-read input never interacted, so it is in its own fixed pure state. Inside joint block b the inputs of R are therefore in a fixed pure product state, uncorrelated with everything else.
3. *The rule is a channel on the inputs.* Inside block b the rule runs R and postselects (m, p) on |Φ⁺⟩. After renormalization this is an operation on the qubits of R whose result depends only on that fixed state, and the block keeps its weight. So the rule is a trace-preserving channel Φ on the qubits entering R, with Theorem 0's Kraus form. The timeless construction (sector projectors at σ_out, the constraint at F, everything propagated back from the last slice by unitaries) equals inserting Φ there.
4. *σ can be built with the outside events first.* No event outside J⁺(M) follows an event inside it, because J⁺(M) is an up-set. So the events of σ can be ordered with those outside J⁺(M) first, then Φ, then those of J⁺(M) ∩ σ. Every input's pre-entry events are in σ, because σ is a down-set containing R.
5. *The outside qubits are untouched.* Let O be the qubits whose latest event in σ lies outside J⁺(M). No event of J⁺(M) ∩ σ touches O. Φ and those events act on other qubits, and a trace-preserving map on other systems leaves O's reduced state unchanged. ∎

**What fails without the theorem's rule.**

- *P-CTC* renormalizes once over all blocks. The block weights then move whenever the postselection probability depends on a read input, and the outside holds a record of that input, so its state changes. In a black hole the change crosses the horizon: P-CTC lets information out (tested).
- *Protecting record registers only* fails when a walker read an input and kept no permanent record (tested), as in Theorem 4's first counterexample.
- *Protecting records inside J⁺(M)* that the loop cannot change (the "influence" definition of timeless/README.md) lets a later choice change earlier statistics. Alice reads her log after the loop, then decides whether to copy her input; P(log = 1) is 1/4 or 1/3 depending on a choice made after the log was read.
- *The causal past* contains R itself once the loop is closed, and still misses spacelike records.

*Checks:* `ctc/tests/test_lightcone.py`, 26 tests:

- light cones, boosts and the static state on hand-built spacetimes;
- the five definitions of the past;
- Theorem 5 on 18 random spacetimes in 1, 2 and 3 spatial dimensions (17–27 events, the time traveller meeting up to 11 events in R), on sampled slices, to 10⁻¹⁵;
- a 1 + 1 black hole;
- the backward-signal example.

**On a general-relativistic time machine.** In the wormhole time machine of Morris, Thorne and Yurtsever, time dilation of one mouth creates the loop. The edge F → M is then the wormhole throat, checked from the mouths' clocks. The theorem holds there too (`ctc/tests/test_wormhole.py`). Bob's record lies outside the causal future of every loop event, counting every path through the wormhole, yet P-CTC changes it (0.5 → 1/3) and PPS does not.

### Relation to Gell-Mann and Hartle's generalized records

Added 2026-11-25, after reading M. Gell-Mann and J. Hartle, "Alternative decohering histories in quantum mechanics" ([arXiv:1905.05859](https://arxiv.org/abs/1905.05859); a 1990 conference paper, posted in 2019), in full.

**Their setting.**

- A history is a chain C_α of projections at successive times.
- A set of histories is *strongly decoherent* if C_α ρ = R_α ρ for mutually orthogonal projections R_α.
- They call the R_α *generalized records*: data at some later time T, fully correlated with the history.
- Strong decoherence implies their medium and weak decoherence, so the histories get probabilities.
- They note that the records are not unique, and that singling out a quasiclassical set needs the Hamiltonian, not only ρ. They give only tentative measures for doing so.
- They work on a fixed background and set aside wormholes and topology change.

**How it maps onto Theorems 4 and 5** (checked in `ctc/tests/test_decoherent_histories.py`, 5 tests):

| Gell-Mann–Hartle | This project | Check |
|---|---|---|
| history "A had value k before the loop" | a PPS world k | — |
| generalized record R_k | the outside record of k (Bob's register, in the pointer basis of the readout) | — |
| strong decoherence C_α ρ = R_α ρ | a perfect readout V = Σ_k \|k⟩⟨k\| ⊗ V_k | holds **for every input state**, which is why PPS is a fixed channel (Theorem 4); Lemma 2 finds the same basis |
| "singling out the set needs the Hamiltonian, not only ρ" | the record basis comes from the interaction, not from the state (Lemma 2; the state-dependent basis of DECOHERENCE.md is rejected) | — |
| probabilities only as good as decoherence | weak records (4c) | with record overlap c, the off-diagonal element of the decoherence functional is c/4, so the world split is not decoherent unless c = 0 |
| records at any later time T | records outside J⁺(M) only (Theorem 5) | see below |

**The difference that matters.**

- *Their records may lie anywhere later, including in the loop's future.* Two examples are accepted as generalized records (tested):
  - a copy of a made after the loop;
  - a's own final value, since the refusal loop never changes a's Z.
- *Without a loop this is harmless.* With one, protecting such records is the "influence" or "all" definition. The first allows a backward signal (Theorem 5, the P(log) example); the second switches the loop off.
- *What a loop adds.* The generalized records must lie outside the loop's causal future. Their framework never needed this restriction, because it excludes wormholes and closed timelike curves.

**Combined statement.** PPS is Hartle's 1994 rule inside each world, where the worlds form a strongly decoherent set (Gell-Mann–Hartle) whose generalized records lie outside the loop's causal future, in the pointer basis of the interactions that wrote them.

**Weak records.** The comparison bears on 4c without settling it. A weak record gives only approximate decoherence, so in their terms the world probabilities are only approximate. The pointer rule treats the split as exact at the first trace of a record, which over-claims. That tilts toward a continuous rule, but does not single out the eigenbasis rule.

### Is PPS linear in the loop's own operation? (process matrices)

Added 2026-11-25. Araújo, Guérin and Baumeler (PRA 96, 052315, 2017) showed that a P-CTC that does not signal is a process matrix. Process matrices are linear in every party's operation. If a coin picks operation U₁ with probability p and U₂ otherwise, the output must be p·out(U₁) + (1 − p)·out(U₂). PPS is linear in states (Theorem 0). Is it also linear in the loop's operation?

**The check** (`ctc/tests/test_operation_linearity.py`, 5 tests, 6 random pairs U₁, U₂):

- *Setup.* Alice's input a is read by Bob (|Φ⁺⟩, Bob records). Alice's coin c (P(c = 0) = 0.3) decides whether the loop applies U₁ or U₂ to (a, m).
- *Coin recorded outside the loop's causal future* (Alice writes it in a notebook before the loop). Theorem 5 splits on the coin. **PPS is exactly linear**: the output equals the mixture.
- *Coin recorded by nobody.* The coin is then a fresh input of the loop region, and it is selected like any fresh input.
  - P(c = 0) moves from 0.3 to between 0.15 and 0.52.
  - The output differs from the mixture by 0.018 to 0.163.
  - **PPS is not linear** for such operations.
- *No signalling either way.* Bob's record keeps its no-loop state; P-CTC changes it.
- *P-CTC* is not linear even with a recorded coin (0.009 to 0.087), because it normalizes once over everything. This is Araújo et al.'s condition: P-CTC is linear only when the postselection probability is constant.

**What this means.**

- *PPS is not a process matrix.* Its output is not a function of the CP map of the loop's operation alone. It also depends on whether the randomness in that operation is recorded outside the loop's causal future. The CP map p·U₁(·)U₁† + (1 − p)·U₂(·)U₂† is the same in both cases above, but the predictions differ.
- *This is the same dependence PPS already has on states.* Theorem 4 makes the result depend on whether an input was read, not only on its reduced state. Here the same holds for the operation. In both cases PPS treats a recorded variable as a fact and an unrecorded one as part of what the loop can select.
- *For classical randomness in practice, PPS is linear.* A classical coin is decohered, i.e. read by its environment. Whenever that environment lies outside the loop's causal future, PPS is linear in the resulting mixture. Linearity fails only for randomness that nothing outside has recorded, for example a coherent quantum control.
- *A new point or a flaw?* Both readings are possible.
  - In favour of a new point: PPS would then be a loop rule that does not signal to any outside party, yet lies outside the process-matrix framework.
  - Against: it gives up a principle that framework takes as basic, namely that a party's operation enters only through its CP map.
  - Neither reading has been checked in a setting with several parties.

**Open.** Non-readout interactions (as in 4b). Weak records (4c) in spacetime. A continuum of events. Exact vacuum spacetimes with closed timelike curves (the wormhole needs exotic matter), and quantum back-reaction at the chronology horizon.

## Hardware experiments

These examples were all run on IBM quantum computers; code and full results are in [hardware/](hardware/README.md). The last column is the PPS value measured in the third run (ibm_kingston, predictions and criteria fixed before submission, 21 of 21 criteria pass):

| Experiment | Theorem | No loop | P-CTC | PPS | Measured |
|---|---|---|---|---|---|
| Grandfather paradox, P(gun jams) | Thm 1(2)(3), Thm 2(1) | 0.2 | 1 | **0.2** | 0.211 |
| Refusal to send, P(a = 1) (past) | Thm 2(1) | 0.5 | 1/3 | **0.5** | 0.503 |
| Refusal to send, P(message recorded \| a = 1) (future) | Thm 1(1), Thm 2(2) | 0.5 | 0 | **0** | 0.035 |
| One-way control, P(a = 1) | Thm 3, P-CTC counterexample | 0.5 | 0 | **0.5** | 0.495 |
| Quantum eraser, Bob's which-path statistics | Thm 0 | 0.5 | 0.667 | **0.5** | 0.501 |
| Quantum eraser, fringe visibility sorted by Bob | PAST_PRESERVING.md | 0.707 | 0.943 | **0.943** (X record basis; Theorem 4's Z basis gives no fringes) | 0.870 |

The numbers for all rules come from the same shots, so the hardware results show that the predictions are measurable, not that nature uses PPS. The values are standard quantum mechanics applied to postselected circuits.

## Not yet proved

1. **Theorem 3 covers only controlled-form U.** Whether every unitary in which "the loop does not affect A" can be written this way is not proved here.
2. **Choice of record basis.** Partly answered by Theorem 4: the basis is the pointer basis of the interactions that correlated the input with the outside. Open: incompatible readouts, partial and coarse records (see the end of Theorem 4).
3. **Falling back to D-CTC in paradox worlds is a seam.** Theorem 1(2) says what it does in those worlds, not why nature should do it.
4. **The main statements of Theorems 1 and 2 are for classical reversible circuits only.** For a general quantum U the corresponding statement is "world k outputs the state of successful Bell postselection", which is the definition of PPS and has less content.
5. **Computational power.** On definite inputs PPS equals P-CTC, so it is at least as powerful as P-CTC (PostBQP); no upper bound is proved ([PERSPECTIVES.md](../PERSPECTIVES.md), 1.5; `tests/test_computational_power.py`).
