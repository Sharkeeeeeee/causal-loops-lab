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
  - if C|k⟩ = 0 (world k has no consistent history): fall back to the open loop. Let σ_k = Tr_L[U(|k⟩⟨k|⊗𝟙/n)U†], the output with the loop cut and fed a uniformly random message (derived in Theorem 8), and σ_k = Σ_j λ_kj |s_kj⟩⟨s_kj|; Kraus operators F_kj = √λ_kj |s_kj⟩⟨k|. Until 2026-11-27 the fallback was the D-CTC fixed point τ_k in place of 𝟙/n; that variant is kept as an alternative (`fallback='dctc'`).
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
2. **In a world with no consistent history, the loop is opened by noise.** If S(x) = ∅, no definite message value is consistent. PPS outputs the open-loop state σ_x = Tr_L[U(|x⟩⟨x|⊗𝟙/n)U†]: the limit of a loop with a little basis-free noise, in which the only consistent histories are those where the noise acted (Theorem 8). With the earlier D-CTC fallback the loop instead sits at a Deutsch fixed point τ_x = Tr_A[U(|x⟩⟨x|⊗τ_x)U†], which exists for every U (Deutsch 1991).
3. **Defined for every input.** P-CTC is undefined when Tr[CρC†] = 0 (for example the grandfather paradox with ε = 0); PPS has no such gap.

*Proof.* (1) By Lemma 1, world x outputs C|x⟩/‖C|x⟩‖ = Σ_y N_xy|y⟩ / (Σ N²)^{1/2}, and measuring in the computational basis gives N_xy²/ΣN². If N_xy = 0 the probability is 0. (2) This is the definition of the fallback, derived in Theorem 8; for the D-CTC variant, existence of the fixed point follows from the fixed-point theorem for CPTP maps on the finite-dimensional state space. (3) Every world falls in one of the two cases, and both are defined. ∎

**Difference from the original H1.** The original H1 said "paradoxical histories do not happen". Under PPS the "grandfather paradox world" does not disappear, because it belongs to the recorded past, whose probabilities PPS may not change. Consistency in that world is reached by the loop message becoming mixed (Deutsch-style), not by deleting the world (P-CTC-style). **Deleting past worlds is exactly why P-CTC signals**, so this rewrite is forced by the no-signalling condition, not an arbitrary choice.

**Remark on the quantum case.** The square N² in (1) means amplitudes add, not history counts. Two consistent histories with the same outcome interfere ("logical consistency ≠ amplitude consistency" in [QUANTUM_EFFECTS.md](QUANTUM_EFFECTS.md)). As long as every consistent history leaves a different record, N_xy is 0 or 1 and the two counts agree; see Theorem 2.

*Check:* `Theorem1_Consistency`: 5 dimensions × 10 random bijections. ⟨y|C|x⟩ = N_xy is checked against an independent enumeration of histories; inconsistent outcomes have probability below 10⁻⁹; the D-CTC fixed-point equation is verified in paradox worlds; for the ε = 0 grandfather paradox P-CTC returns "undefined" while PPS gives a normal output.

### Theorem 1Q: the same statement for any quantum U

Added 2026-11-27. For a loop basis {|b_m⟩} and a world k write A_ym = ⟨y, b_m|U|k, b_m⟩: the amplitude of the history that starts the loop in b_m, finds it in b_m again, and leaves the CR system in y. Since ⟨y|C|k⟩ = Σ_m A_ym in every loop basis (a trace does not depend on the basis), Lemma 1 holds for any U with "number of consistent histories" replaced by "sum of their amplitudes".

**Theorem 1Q.** In a world with a consistent history (C|k⟩ ≠ 0): if in some loop basis no history from k to y returns the loop unchanged (A_ym = 0 for every m), then P(y | k) = 0. The converse fails: returning histories can cancel.

*Proof.* P(y | k) = |⟨y|C|k⟩|² / ‖C|k⟩‖² = |Σ_m A_ym|² / ‖C|k⟩‖². ∎

So H1′ for a quantum U is amplitude consistency, and it can be checked in whichever loop basis is convenient. In the test, U is a classical circuit in a rotated loop basis B with no returning history to y: P(y | k) = 0, while in the computational basis the same U has nonzero returning histories to y that cancel.

*Check:* `ctc/tests/test_quantum_h1h2.py` (Theorem1Q, 2 tests).

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

### Theorem 2Q: the same statement for any quantum U

Added 2026-11-27. Notation of Theorem 1Q. Let P_0(y | k, returned) be the ordinary run without a loop: the loop system prepared in a uniformly random b_m, measured afterwards in the same basis, and kept when it came back as b_m.

**Theorem 2Q.**

P_PPS(y | k) ∝ |Σ_m A_ym|²,  P_0(y | k, returned) ∝ Σ_m |A_ym|²,

so the two differ exactly by the interference terms Σ_{m≠m′} A_ym A*_ym′. They agree whenever the output records which history returned (for each y at most one m with A_ym ≠ 0), the quantum form of N_xy ∈ {0, 1} in Theorem 2(2).

*Proof.* P_0(y, returned | k) = (1/n) Σ_m |⟨y, b_m|U|k, b_m⟩|². Expanding |Σ_m A_ym|² gives the same diagonal sum plus the cross terms. ∎

So the loop's effect for a quantum U is "condition on the loop returning", in any loop basis one likes, plus interference between returning histories that the output does not tell apart. This gives Theorems 1 and 2 quantum content (item 4 of "Not yet proved").

*Check:* `ctc/tests/test_quantum_h1h2.py` (Theorem2Q, 2 tests): equality for recording circuits in random loop bases; the general formula and its interference terms for random U.

## Theorem 3 (H3′: when the loop does not act back, ordinary quantum mechanics returns)

**Statement.** Suppose the loop does not act back on the CR system: U = (V⊗𝟙) Σ_k |k⟩⟨k| ⊗ W_k, i.e. A controls the loop in the basis {|k⟩} and the loop never affects A. Take {|k⟩} as the record basis. Then:

1. For any ρ diagonal in the record basis and any external loop input τ_0, Φ(ρ) = Tr_L[U(ρ⊗τ_0)U†]: **exactly ordinary quantum mechanics without a loop.** Whether the W_k have zero trace does not matter.
2. For any ρ (not necessarily diagonal), the two give the same measurement statistics in the basis {V|k⟩}.
3. Special case: no interaction at all, U = V⊗W, with the eigenbasis of ρ as the record basis: Φ(ρ) = VρV†, **including when Tr W = 0**, where P-CTC is undefined.

*Proof.* C = Tr_L U = Σ_k Tr(W_k) V|k⟩⟨k|, so C|k⟩ = Tr(W_k) V|k⟩.

- If Tr W_k ≠ 0: K_k = e^{iθ} V|k⟩⟨k|, and K_k ρ K_k† = ρ_kk V|k⟩⟨k|V†.
- If Tr W_k = 0: fall back (open loop or D-CTC: both give the same here). For any τ, Tr_L[U(|k⟩⟨k|⊗τ)U†] = V|k⟩⟨k|V†·Tr(W_kτW_k†) = V|k⟩⟨k|V†, so σ_k = V|k⟩⟨k|V† and the contribution is again ρ_kk V|k⟩⟨k|V†.

So Φ(ρ) = V Δ(ρ) V†, where Δ removes the off-diagonal terms in {|k⟩}. Without the loop, Tr_L[U(ρ⊗τ_0)U†] = V Σ_{k,k′} ρ_kk′ Tr(W_k τ_0 W_k′†) |k⟩⟨k′| V†, whose diagonal terms are ρ_kk (since Tr(W_kτ_0W_k†) = 1). For diagonal ρ the two agree, which is (1); for general ρ the diagonals agree, which is (2). (3) is the case W_k = W for all k, with the basis chosen as the eigenbasis of ρ so that Δ(ρ) = ρ. ∎

**Where the record basis comes from.** The theorem assumes that A's value in the basis {|k⟩} is recorded outside the loop's causal future (Theorem 4). The loop's own reading of A does not count, because it lies inside J⁺(M). If nothing outside recorded A, the world is the fresh state and the loop selects among the values of k: the P-CTC counterexample below then applies to PPS as well (a fresh |+⟩ controlling a NOT on the loop gives P(a = 1) = 0). The first version of this paragraph said "the loop itself is a record of A in that basis"; that conflicts with Theorems 4–7 and is withdrawn.

**P-CTC counterexample.** Take V = 𝟙, W_0 = 𝟙, W_1 = X (A controls a NOT on the loop), ρ = 𝟙/2. The loop never acts on A, yet C = 2|0⟩⟨0|, and P-CTC deletes the a = 1 world entirely: P(a = 1) = 0, while ordinary quantum mechanics gives 0.5. With U = 𝟙⊗Z (the loop only picks up a phase), C = 0 and P-CTC is undefined. So the original H3 fails under P-CTC and holds under PPS.

*Check:* `Theorem3_CausalityRecovered`: 5 dimensions, W_k a random mix of generic and zero-trace unitaries, always including at least one paradox world; random V, random external input; plus the P-CTC counterexample above.

### Theorem 3 for every U that does not act back (Lemmas 3.1 and 3.2)

Added 2026-11-27. Item 1 of "Not yet proved" asked whether every unitary in which "the loop does not affect A" has the controlled form. There are two readings of the phrase; both are settled.

**Lemma 3.1 (the loop cannot signal to A at all).** If A's output Tr_L[U(ρ⊗τ)U†] never depends on the loop input τ, then U = V⊗W.

*Proof.* Independence of τ for every ρ means U†(X⊗𝟙)U = α(X)⊗𝟙 for every operator X on A. The map X ↦ U†(X⊗𝟙)U is an injective *-homomorphism of the d×d matrices into themselves, hence an automorphism, hence α(X) = V†XV for a unitary V (every automorphism of a full matrix algebra is inner). So (V⊗𝟙)U† commutes with every X⊗𝟙 and equals 𝟙⊗W′, and U = V⊗W′†. ∎ For unitaries this is the known fact that a non-signalling bipartite unitary is a product (Beckman–Gottesman–Nielsen–Preskill 2001).

**Lemma 3.2 (the loop never changes A's record in some basis).** If A's output statistics in the basis {V|k⟩} equal the input statistics in {|k⟩} for every ρ and τ, then U = (V⊗𝟙) Σ_k |k⟩⟨k|⊗W_k.

*Proof.* The condition is U†(VP_kV†⊗𝟙)U = P_k⊗𝟙 for every k, with P_k = |k⟩⟨k|. So (V†⊗𝟙)U commutes with every P_k⊗𝟙 and is block diagonal, Σ_k P_k⊗W_k. ∎

So Theorem 3 covers exactly the unitaries that cannot change A's record, and the strictly non-signalling ones are the products, W_k = W.

**A product is not a loop input.** If U = V⊗W, A does not interact with the loop. The loop's inputs are the systems on which U acts non-trivially (operator Schmidt rank above 1), so A is not one of them and PPS leaves it alone: A goes through V, entanglement included. This has to be stated, because splitting A into worlds anyway would do damage. For half of a Bell pair beside a loop it never touches, the pointer rule would leave only classical correlation and the state rule a separable Werner state (Bell fidelity 0.5 in both cases, instead of 1).

**Two caveats for controlled U.**

1. *PPS treats the loop's reading of A as perfect.* Every statistic diagonal in {|k⟩} agrees with ordinary quantum mechanics. The coherence between A and its outside record, visible only to a joint measurement that undoes the record, is multiplied by Tr(W_k τ W_k′†) in ordinary quantum mechanics and set to 0 by PPS. This is the all-or-nothing of the pointer rule (4c) again, now for the loop's own possibly weak reading. It cannot be seen when the outside record is irreversible.
2. *The controlled value must be recorded outside* (see above).

*Checks:* `ctc/tests/test_theorem3_general.py`, 9 tests: Lemma 3.1 (products do not signal, controlled and generic unitaries do; the Heisenberg form); Lemma 3.2 (controlled form preserves the record, decomposition recovered, generic unitaries move it in every basis); the product case with a Bell pair; both caveats.

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

**The premise matters.** If A was entangled beforehand with a hidden partner D by an interaction that read no basis, there is no fixed state inside a block. Applying P-CTC to whatever the block holds then changes D's statistics: the P-CTC signalling mechanism, confined to the block (tested). Such interactions are the remaining open case. **Settled by Theorem 7:** worlds from the eigenvectors of ρ_A cover every interaction.

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
- **The two safe rules disagree on what a weak record means.** The pointer rule says any readout, however weak, fixes the past in its basis. The eigenbasis rule says a weak readout only partly does, and ignores the record's basis where A's spectrum is degenerate (the all-or-nothing case of DECOHERENCE.md is exactly such a degeneracy, ρ = 𝟙/2). They predict different outputs for weak records; which one nature would use is not decided by any principle found here. **Settled by Theorem 7:** under state completeness only the eigenbasis rule is allowed.

*Checks:* `ctc/tests/test_readouts.py`, 10 tests (4a: basis, no signalling under all operations of both outside parties, the one_way example; 4b: block finding, no signalling for random inputs, loops and outside operations, the fresh limit, the premise counterexample; 4c: the table above).

**A consequence for the eraser.** The idler is made by a CNOT, which reads the path in Z. Under Theorem 4 the record basis of the eraser is therefore Z, not the X basis used in [PAST_PRESERVING.md](PAST_PRESERVING.md) and in the hardware design. With Z, PPS makes the loop act like a which-path measurement: the Bob-sorted fringes disappear instead of shifting by π/4. The hardware PPS values for the eraser (visibility 0.870, shift 0.774) are measured values of the X-basis variant, which Theorem 4 does not support.

**Still open.** ~~Interactions that read no basis (4b premise); the choice between the pointer and eigenbasis rules for weak records (4c).~~ Both settled by Theorem 7, under state completeness. Still open: a superposed order of two incompatible readouts. Under Theorem 7 this question disappears, since the rule needs only ρ_A.

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
- apply P-CTC inside each joint block, with the fallback (in these circuits the open loop, the D-CTC fixed point and the no-loop state coincide), and keep each block's weight.

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
- *Under Theorem 7* (worlds from the inputs' reduced state) the same conclusions hold for P(c = 0) ≠ 1/2, with different numbers; for a fair recorded coin linearity fails as well (Theorem 7, recheck).
- *A new point or a flaw?* Both readings are possible.
  - In favour of a new point: PPS would then be a loop rule that does not signal to any outside party, yet lies outside the process-matrix framework.
  - Against: it gives up a principle that framework takes as basic, namely that a party's operation enters only through its CP map.
  - Neither reading has been checked in a setting with several parties.

**Open.** Non-readout interactions (as in 4b). Weak records (4c) in spacetime. A continuum of events. Exact vacuum spacetimes with closed timelike curves (the wormhole needs exotic matter), and quantum back-reaction at the chronology horizon.

## Theorem 6: inside a world the selection is forced; the earlier uniqueness conjecture is false as stated

Added 2026-11-26. [PERSPECTIVES.md](../PERSPECTIVES.md), 3.2, conjectured that PPS is the only rule satisfying:

- (a) linear, completely positive and trace preserving (so no signalling);
- (b) unchanged probabilities in the record basis;
- (c) only consistent outcomes in worlds that have a consistent history;
- (d) ordinary quantum mechanics when the loop does not act back.

### The conjecture as stated is false

*History counting.* In a world x with S(x) ≠ ∅, output y with probability N_xy / Σ_y′ N_xy′, instead of PPS's N_xy² / Σ_y′ N_xy′² (Theorem 1). In a world with S(x) = ∅, fall back as PPS does.

- It is a measure-and-prepare channel in the record basis, so it satisfies (a) and (b).
- Its outcomes are those of consistent histories, so it satisfies (c).
- In controlled form, N_xy is nonzero only for y = f(x), so it satisfies (d).
- It differs from PPS whenever a world's nonzero counts N_xy are not all equal. Example (`three_way_circuit`): a CR bit and a two-bit loop. In world 0 the loop values 0 and 1 give output 0, the value 2 gives output 1, and the value 3 is inconsistent. Then C|0⟩ = 2|0⟩ + |1⟩, so:
  - PPS gives P(0) = 4/5;
  - history counting gives 2/3;
  - D-CTC gives 3/4.
- Among random reversible circuits, 38 of 750 worlds differ.

**Why (a)–(d) leave this freedom.** Inside a world, every input is in a fixed pure state (Theorem 5, step 2). Linearity of the channel therefore says nothing about what happens within a world, and any state on the consistent outcomes passes (a)–(d).

### What does single out PPS

**Setting.** One world, its inputs in a fixed pure state ψ, interaction U on CR ⊗ L (CR includes the fresh inputs).

**Assumptions.**

- (U1) *Past preservation:* the world keeps its no-loop weight.
- (U2) *Amplitude form:* the world's output is L(U)ψ / ‖L(U)ψ‖, with L : B(H_CR ⊗ H_L) → B(H_CR) linear. This is the superposition principle for interaction histories: amplitudes of alternative histories add, as in a sum over histories.
- (U3) *Composition:* L((W₁⊗𝟙) U (W₂⊗𝟙)) = W₁ L(U) W₂ for all unitaries W₁, W₂ on CR. Evolving the CR system before or after the loop region is ordinary quantum mechanics.
- (U4) *Relabelling:* L((𝟙⊗V) U (𝟙⊗V†)) = L(U) for all unitaries V on the loop. Renaming the loop's states in the same way at both mouths is a change of description, not of physics.

**Theorem 6.** Under (U2)–(U4), L(U) = c·Tr_L U for a constant c ≠ 0. With (U1), the rule is PPS in every world where Cψ ≠ 0. In worlds where Cψ = 0 the assumptions are silent: the paradox-world fallback is the only freedom left.

*Proof.*

1. *(U3) extends to all operators.* Both sides are bilinear in (W₁, W₂), and unitaries span B(H_CR), so L((A⊗𝟙) X (B⊗𝟙)) = A L(X) B for all A, B.
2. *L acts as the identity on CR.* Let E_ij be the matrix units of CR. Then E_11 ⊗ Y = (E_11⊗𝟙)(E_11⊗Y)(E_11⊗𝟙), so L(E_11⊗Y) = E_11 L(E_11⊗Y) E_11 = ℓ(Y) E_11 for a linear functional ℓ. From E_ij ⊗ Y = (E_i1⊗𝟙)(E_11⊗Y)(E_1j⊗𝟙) follows L(E_ij⊗Y) = ℓ(Y) E_ij, that is L = id ⊗ ℓ.
3. *ℓ is the trace.* Write ℓ(Y) = Tr(ZY). (U4) gives Tr(V†ZV Y) = Tr(ZY) for all Y and unitary V, so Z commutes with every unitary and Z = c𝟙. Hence L(U) = c·Tr_L U.
4. *c ≠ 0*, or the output is undefined; normalization removes c. The world's output is Cψ/‖Cψ‖, which is PPS's Kraus operator K_k (Setting), and (U1) gives the world its weight. ∎

**What each assumption excludes** (numerical checks in brackets):

| Dropped | What becomes possible |
|---|---|
| (U1) | Hartle's framework / P-CTC with global normalization (it satisfies (U2)–(U4)); it reweights the recorded past and signals |
| (U2) | history counting, D-CTC restricted to a world, Anderson 1995's unitary part of the polar decomposition (not linear in U), the κ–β corners |
| (U3) | a large space of linear maps [`test_without_composition_the_space_is_large`] |
| (U4) | L(U) = Tr_L[U(𝟙⊗Z)] for any Z, for example "the loop is held at one basis value" [9 solutions for a qutrit loop] |
| (U4) restricted to permutations of loop basis states | a second solution, ℓ(Y) = Σ_ij Y_ij [2 solutions]; adding phases (the monomial group) is already enough [1 solution] |

### What this means

- **PPS is now forced, not chosen, given its two ingredients:** no reweighting of the recorded past (U1), and quantum superposition of histories inside a world (U2) with the two natural covariances (U3, U4).
- **The square N² of Theorem 1 is forced.** History counting is a classical rule: it needs a preferred loop basis, so it breaks (U4). A Hadamard relabelling of the loop turns the three-way circuit into one whose loop amplitudes interfere; PPS is unchanged, and history counting is not even defined there (tested).
- **The seam is isolated.** The only freedom left is the output of worlds with no consistent history, which answers the second part of PERSPECTIVES 3.2: "why fall back to D-CTC" is now a question on its own (Not yet proved, item 3). Theorem 8 answers it with a different fallback.

**Limits.**

- (U2) is the substantive assumption. It is the superposition principle applied to interaction histories, not something derived from no-signalling.
- The theorem concerns rules that act world by world, with the worlds of Theorem 4. It does not choose the record basis (Theorem 4 does) and says nothing about weak records (4c).
- A rule whose output inside a world is mixed (D-CTC-like) is excluded by (U2), not by a separate argument.

*Checks:* `ctc/tests/test_uniqueness.py`, 11 tests:

- history counting meets (a)–(d) on random circuits and differs from PPS;
- the three-way circuit's three answers;
- the solution space of (U3)–(U4), computed numerically, is one-dimensional and spanned by Tr_L, for loop dimensions 2 and 3;
- the solution spaces when an assumption is dropped or weakened;
- PPS's invariance under relabelling and composition;
- a paradox world, where two different fallbacks both pass.

## Theorem 7: worlds from the state alone (weak records, and interactions that read no basis)

Added 2026-11-26. Theorem 4 takes the worlds from the history of interactions (the pointer basis). It left two cases open: weak records, where 4c found two safe rules and no reason to choose, and interactions that read no basis (the premise of 4b). One principle settles both.

**Principle (state completeness).** The worlds are a function of the quantum state on the outside slice σ_out, not of how that state was produced.

**Lemma 7.1.** If the worlds are a function of the state on σ_out, and the rule never signals whatever is done outside J⁺(M), then they depend on that state only through ρ_A, the reduced state of the loop's inputs.

*Proof.*

1. The global state on σ_out can be taken pure: fresh inputs are pure, evolution is unitary, and ignorance can be purified by systems outside J⁺(M).
2. Two global states with the same ρ_A are purifications of it. By Uhlmann's theorem they are related by a unitary acting only on the outside systems.
3. Applying that unitary is an outside operation. If the two states had different worlds, an outside party could switch Alice's statistics by applying it or not: a signal. ∎

The proof assumes that any unitary on the outside systems is a possible outside operation (an agent may gather them anywhere outside J⁺(M)).

**Theorem 7.** Assume state completeness, no signalling, and the world-by-world form of Theorem 6: orthogonal worlds on the inputs, each a pure state that keeps its weight. Assume also:

- (R) when the state determines a basis in which the outside holds perfect records, those are the worlds.

Then the worlds are the eigenvectors of ρ_A. In a degenerate eigenspace the state singles out no basis, and the rule averages over all of them.

*Proof.*

1. By Lemma 7.1 the worlds are a function of ρ_A.
2. Purify: |Ψ⟩ = Σ_s √λ_s |s⟩|f_s⟩ (Schmidt decomposition). The f_s are orthonormal, so the outside holds a perfect record of s.
3. If the spectrum is non-degenerate, the Schmidt basis is unique, and (R) makes it the worlds.
4. If an eigenvalue is degenerate, every basis of its eigenspace is the Schmidt basis of some purification with the same ρ_A. A function of ρ_A cannot pick one of them. The rule that treats them all alike averages over them, each world of each basis with equal weight. ∎

**What it settles.**

- **Weak records (4c):** the eigenbasis rule. Of the three rows of the 4c table, it is the only one that is a function of ρ_A; the table's values are reproduced.
- **Interactions that read no basis (4b premise):** the rule is a fixed channel given ρ_A, and no outside operation changes ρ_A. This holds for any interaction, including entanglement with a hidden partner D.
  - Tested on random non-readout interactions, with outside unitaries and measurements: no signalling in either direction.
  - By contrast, P-CTC applied to whatever A holds shifts the outside's statistics by more than 0.01.

**Agreement with earlier results.**

- A fresh pure input gives P-CTC.
- A perfect readout with distinct weights gives Theorem 4.
- A coarse readout with distinct block weights gives 4b: the eigenvectors are the block's projected states.
- 4a's one_way example is reproduced: after the X readout ρ_A = 𝟙/2, and every world goes to |0⟩.
- Theorem 5 still holds, because its proof needs only a fixed channel on the inputs.
- Inside each world the rule is Theorem 6.

**Not the rule of DECOHERENCE.md.** That rule used the conditional state ρ_{S|e}, which depends on the outside's record e and therefore on outside choices; ρ_A does not. The state rule is nonlinear in ρ_A, but it has no preparation problem, because it is a function of ρ_A itself, whatever ensemble produced it.

**The price, on each side.** The two safe rules disagree only where records are weak or ρ_A is degenerate.

- *History dependence (pointer rule):* the same global state can get two predictions. A CNOT reading |+⟩ in Z, and an X readout of |0⟩ followed by Bob's Hadamard, end in the same global state. With the one_way loop the pointer rule gives P(a = 0) = 0.5 for the first and 1 for the second (tested).
- *Degenerate spectra (state rule):* Theorem 4's Bell example changes. CNOT reads |+⟩, so ρ_A = 𝟙/2.
  - The pointer rule keeps the paradox world a = 1 and gives P(a = 0) = 0.5.
  - The state rule averages over bases, every world goes to |0⟩, and P(a = 0) = 1.
  - Bob's statistics stay 0.5 under both rules.
- A symmetric superposition that is perfectly recorded is a common case. Copying the record redundantly into the environment does not change ρ_A, so it does not break the degeneracy under the state rule.

**Recheck of earlier results (2026-11-26).** Results first computed with the pointer rule on degenerate inputs were recomputed under the state rule (`lightcone.py`, `Lattice.theorem7_split`).

| Result | Pointer rule (Theorem 4) | State rule (Theorem 7) |
|---|---|---|
| Theorem 4's Bell example (one_way loop): Alice's P(a = 0) | 0.5 | 1 |
| Light cone, black hole and wormhole time machine with the refusal loop: Alice's P(a = 1), P(log = 1) | 0.5, 0.25 | 2 ln 2 − 1 ≈ 0.386, 1 − ln 2 ≈ 0.307 |
| Same, swap_write loop | 0.5, 0 | 0.5, 0 |
| Bob's record, every case | 0.5 | 0.5 |
| Theorem 5 (outside unchanged) on random spacetimes | holds (10⁻¹⁵) | holds (5×10⁻¹⁵, 18 spacetimes) |
| Linearity: recorded coin, P(c = 0) = 0.3 | linear | linear (residual 3.5×10⁻³ with 60 bases, 2.5×10⁻⁴ with 240: discretization) |
| Linearity: unrecorded coin | not linear (0.018–0.163; P(c = 0) 0.15–0.52) | not linear (0.032–0.107; P(c = 0) 0.15–0.50) |
| **Linearity: recorded coin, P(c = 0) = 1/2** | linear | **not linear (0.02–0.06)** |

- **What survives:** every no-signalling statement (Bob's record, Theorem 5), and the conclusions of the linearity check for P(c = 0) ≠ 1/2.
- **What changes:** Alice's own outputs, wherever her input is half of a Bell pair.
- **What is new, a second cost of the state rule.** With a fair recorded coin and Alice's a maximally mixed, the inputs' joint spectrum is fully degenerate. The rule then averages over all joint bases, entangled ones included, and no longer splits on the coin. So a perfectly recorded fair bit is not treated as a fact, and the output jumps at P(c = 0) = 1/2.

**Decision (revised after the recheck).** The choice between the two safe rules of 4c is the choice between state completeness and history dependence, and each has one discontinuity:

- the pointer rule jumps at the first trace of a record (overlap c → 1);
- the state rule jumps at degenerate spectra, which arise in ordinary situations such as a fair coin or a Bell pair.

The first version of this section adopted the state rule. The recheck shows that its cost is larger than first stated, so neither rule is adopted as the default. Theorem 4 and Theorem 7 are kept as the two candidates, and where they differ results are reported under both. What Theorem 7 does settle unconditionally: under state completeness the eigenbasis rule is the only safe choice, and it covers interactions that read no basis, which the pointer rule does not.

**Earlier draft of the decision, kept for the record.** The choice between the two safe rules of 4c is the choice between state completeness and history dependence. This project adopts the state rule, for three reasons:

- it is the only rule found that covers every interaction;
- it follows from a standard principle (the quantum state is a complete description);
- Theorem 6 already rests on the same idea, that renaming is description, not physics.

The pointer rule of Theorem 4 remains as the history-dependent variant. Earlier numbers computed with the pointer rule on degenerate inputs need rechecking under the state rule; this applies to Alice's side only, since no-signalling holds under both rules. Affected: the Bell example of Theorem 4, the light-cone and wormhole models (Alice's input a is half of |Φ⁺⟩), and the linearity check.

*Checks:* `ctc/tests/test_worlds.py`, 15 tests:

- Lemma 7.1: two histories that end in the same global state; purifications related by an outside unitary;
- random non-readout interactions: no signalling either way, while P-CTC on A signals;
- the limits: fresh input, perfect readout, coarse readout, the 4c table;
- the Bell example;
- convergence of the basis average;
- the recheck: light cone and wormhole, Theorem 5 on random spacetimes, linearity including the fair recorded coin.

## Theorem 8: worlds with no consistent history (the fallback, derived)

Added 2026-11-27. Theorem 6 left one freedom: the output of a world |k⟩ with C|k⟩ = 0. The project used the D-CTC fixed point there, without a reason (Not yet proved, item 3).

**Regularization.** Give the loop a little noise: after U the loop system goes through N_ε = (1 − ε)·id + ε·N. P-CTC with a noisy loop of Kraus operators E_j outputs Σ_j C_j ρ C_j† (normalized), with C_j = Tr_L E_j: postselected teleportation through a noisy channel. Applied inside each recorded world, call this PPS_ε.

**Theorem 8.**

1. *Limit.* As ε → 0, PPS_ε tends to PPS in every world with C|k⟩ ≠ 0, with trace distance at most ε / ((1 − ε)‖C|k⟩‖²). In a world with C|k⟩ = 0, PPS_ε does not depend on ε: it outputs what the noise alone lets through.
2. *Uniqueness.* If the noise has no preferred loop basis, N(WXW†) = W N(X) W† for every loop unitary W (the relabelling invariance (U4) of Theorem 6, applied to the noise), then N is depolarizing, and the paradox-world output is the **open loop**: σ_k = Tr_L[U(|k⟩⟨k|⊗𝟙/n)U†], the loop cut and fed a uniformly random message.
3. *Computational power.* For decision problems with a classical (recorded) input, one loop, and gates with algebraic amplitudes such as Hadamard and Toffoli: with the open-loop fallback PPS decides exactly **PP** (= PostBQP); with the D-CTC fallback, exactly **PSPACE**.

*Proof.*

1. Noise on the CR system adds terms (Q⊗𝟙)U with Tr_L[(Q⊗𝟙)U]|k⟩ = QC|k⟩, which vanish with C|k⟩, so only loop noise matters. With E_0 = √(1 − ε)U and E_j = √ε (𝟙⊗N_j)U, Σ_j C_j ρ C_j† = (1 − ε)CρC† + ε Σ_j C_{N_j} ρ C_{N_j}†. If C|k⟩ = 0 the first term vanishes and ε cancels in the normalization. Otherwise the output is ((1 − ε)‖C|k⟩‖² P + ε σ′) / ((1 − ε)‖C|k⟩‖² + ε) with P the PPS state, which gives the bound.
2. A channel covariant under every unitary is X ↦ (1 − p)X + p Tr(X)𝟙/n (by Schur's lemma the covariant linear maps are spanned by the identity and X ↦ Tr(X)𝟙). The depolarizing part has Kraus operators P/n over the n² Weyl operators P, and since these form an operator basis, Σ_P n⁻² Tr_L[(𝟙⊗P)U] ρ Tr_L[(𝟙⊗P)U]† = Tr_L[U(ρ⊗𝟙/n)U†].
3. *Lower bounds.* On a recorded input there is one world, and PPS is P-CTC there whenever C|x⟩ ≠ 0; Lloyd et al. 2011 show P-CTC simulates PostBQP = PP (Aaronson 2005), and their construction postselects on an event of nonzero probability, so C|x⟩ ≠ 0. With the D-CTC fallback, put a grandfather bit (flipped every round) beside any loop: then C = 0 for every input, and the D-CTC fixed point of the pair is the loop's own fixed point times 𝟙/2, so the paradox world runs a D-CTC computation. D-CTC computers decide PSPACE, whichever fixed point is taken (Aaronson–Watrous 2009). *Upper bounds.* Open fallback: with h Hadamard gates every amplitude is an integer over 2^{h/2}, so a nonzero ‖C|x⟩‖² is at least 2^{−h}. One P-CTC run with a depolarized loop at ε = 2^{−(h+10)} then reproduces PPS within trace distance 2^{−9} by (1), exactly in a paradox world. That run is a postselected circuit (the noise is a coin of bias 2^{−(h+10)}, an AND of fair coins), so it is in PostBQP = PP. D-CTC fallback: each world's output is a P-CTC output (PP ⊆ PSPACE) or a D-CTC output (PSPACE), and whether C|x⟩ = 0 can be decided in PSPACE. ∎

**What this changes.**

- **The open loop replaces D-CTC as the default fallback** (code: `fallback='open'`; `fallback='dctc'` keeps the old rule). The whole test suite passes with either. In every example reported so far the paradox worlds give the same output under both: the classical grandfather paradox, Theorem 3's zero-trace blocks, and the hardware circuits, where the fallback had already been found to equal the no-loop output.
- **H1′ in a paradox world** now reads: the history is consistent only through a noise event in the loop. This is Novikov's "banana peel", which Lloyd et al. 2011 already describe for P-CTC; under PPS the world cannot be deleted, so in that world the unlikely event happens for certain.
- **No convention is needed.** The D-CTC fallback also needed a choice when several fixed points exist (the code takes the limit from the maximally mixed seed); the open loop is unique.
- **Paradox worlds get no extra power.** With the D-CTC fallback, a deliberately built paradox world is a PSPACE computer; with the open loop, PPS stays at P-CTC's PP.
- **Cost.** In a paradox world the loop is not self-consistent in the clean sense (its output need not equal its input 𝟙/n); consistency holds only for the regularized loop.
- **Not removed.** PPS is still discontinuous as C|k⟩ → 0 (the direction C|k⟩/‖C|k⟩‖ has no limit). What is gained is that the paradox-world output follows from one assumption (noise without a preferred basis) instead of being chosen.
- **Scope of 3.** Several loops in sequence with records made between them are not covered.

*Checks:* `ctc/tests/test_fallback.py`, 8 tests: the limit in consistent and paradox worlds (generic U made paradoxical by a grandfather bit); a noise with a preferred operation gives another limit; only the depolarizing noise is basis-free; D-CTC differs from the open loop in generic paradox worlds and agrees in the earlier examples; a paradox world running Deutsch's fixed-point search finds the target under D-CTC and outputs noise under the open loop; one postselected run with ε = 2^{−(h+10)} reproduces the open rule on random Hadamard–CNOT–Toffoli circuits (`ctc/fallback.py`).

## Theorem 9: choosing the world rule (jumps are forced; a mixed rule avoids them)

Added 2026-11-27. The pointer rule (Theorem 4) and the state rule (Theorem 7) each jump once (Theorem 7, recheck). This theorem says which jumps are forced, and gives a third rule.

**Theorem 9.**

1. *A state-only rule must jump.* If a rule depends only on ρ_A, never signals, and satisfies (R) of Theorem 7, it is discontinuous at ρ_A = 𝟙/d, for every loop whose output depends on the basis of worlds.
2. *A single-basis history rule must jump.* Take a qubit input in a pure state ψ before a readout of record overlap c in the pointer basis Z. No rule that assigns one orthonormal basis, continuously in (ψ, c), can give the basis {ψ, ψ⊥} at c = 1 (no record: the fresh rule) and the pointer basis at c = 0 (perfect record: (R)).
3. *A mixed rule does not jump on this family.* Φ = (1 − c)·Φ_pointer + c·Φ_state never signals, equals the fresh rule (P-CTC) at c = 1 and the pointer rule at c = 0, and is continuous in (ψ, c).

*Proof.*

1. For t ≠ 0, ρ_A = 𝟙/d + tΔ, with Δ diagonal in a basis B with distinct entries, can be purified by perfect outside records in B; by state completeness and (R) the worlds are B. Approaching 𝟙/d along two bases B ≠ B′ gives two limits of the output, and no value at 𝟙/d matches both.
2. An unordered orthonormal basis of a qubit is an axis, a point of RP². At c = 1 the rule is the map S² → RP², ψ ↦ axis(ψ), the double cover; at c = 0 it is constant. A continuous rule on S² × [0, 1] would be a homotopy between the two. By the covering homotopy property it would lift to a homotopy on S² from the identity or the antipodal map (degree ±1) to a constant map (degree 0), which is impossible.
3. Both parts are fixed channels on A given the history (the readout fixes the pointer basis and c, and nothing done outside changes ρ_A), so their mixture is one too, and Theorem 0 applies. Under the premise of 4b, ρ_A = (1 − c)Δ_Z(ψψ†) + c ψψ†. At c = 1 the state part is P-CTC in a basis containing ψ; at c = 0 it has no weight. ρ_A is degenerate only at c = 0 with ψ unbiased, where the state part has weight 0; elsewhere its eigenvectors, and so the state part, vary continuously. ∎

Mixing is what escapes 2: the space of mixtures of splits is convex, so the topological obstruction disappears. 1 − c has a reading: it is the probability that an unambiguous measurement of the record would succeed (Ivanovic–Dieks–Peres). A weak record counts as a fact exactly as often as it could be read without error.

**Numbers** (eraser loop C = diag(2, 1 + i); P(a = 1) after the loop):

| Input | Rule | c = 1 | 0.995 | 0.825 | 0.540 | 0.1 | 0 |
|---|---|---|---|---|---|---|---|
| P(1) = 0.3 | pointer | 0.176 (fresh) | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 |
| | state | 0.176 | 0.177 | 0.184 | 0.209 | 0.292 | 0.300 |
| | mixed | 0.176 | 0.177 | 0.205 | 0.251 | 0.299 | 0.300 |
| P(1) = 0.5 | pointer | 0.333 (fresh) | 0.500 | 0.500 | 0.500 | 0.500 | 0.500 |
| | state | 0.333 | 0.333 | 0.333 | 0.333 | 0.333 | **0.386** |
| | mixed | 0.333 | 0.334 | 0.363 | 0.410 | 0.483 | 0.500 |

For a fair coin the state rule takes the X basis for every c > 0 (the weak record's coherence picks it) and jumps to the basis average at c = 0. The mixed rule moves smoothly to the pointer answer.

**What the mixed rule keeps and what it costs.**

- *Keeps:* no jump at the first trace of a record; a perfectly recorded fair coin is split on, so linearity in recorded mixtures holds as under the pointer rule; Theorem 4's Bell example gives 0.5.
- *Costs:* it is history dependent, so it gives up state completeness, as the pointer rule does. It is defined only for readouts whose record states share one overlap (all two-outcome readouts), not for unequal overlaps or several readouts. With no record at all it is the state rule, so it inherits that rule's jump for unrecorded degenerate inputs (an input entangled with a hidden partner by an interaction that read no basis); by 1, a state-only treatment of those must jump.

**Decision.** The mixed rule is the only one of the three without a jump on the weak-readout family, and it agrees with the pointer rule on every perfect record. It is the preferred candidate for the readouts it covers. It is not yet a general rule, so results are still reported under the pointer and state rules where they differ.

*Checks:* `ctc/tests/test_mixed_rule.py`, 6 tests: the two directional limits at 𝟙/2 under the state rule; the record overlap; no signalling for random loops, records and outside operations; continuity from no record to a perfect one (steps below 0.01 on a grid of 101), with the fresh and pointer endpoints; the jumps of the single-basis rules on the same family; perfect records as under the pointer rule (`ctc/mixed_rule.py`).

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

1. ~~**Theorem 3 covers only controlled-form U.**~~ Settled (Lemmas 3.1–3.2): a unitary that cannot change A's record is controlled, one that cannot signal to A at all is a product, and a product is not a loop input. Remaining: PPS treats the loop's own weak reading of A as perfect.
2. **Choice of record basis.** Theorem 4 takes the pointer basis of the interactions; Theorem 7 takes the eigenbasis of the input's reduced state, and shows that this is the only safe choice under state completeness. Open: whether state completeness or history dependence is right (they differ only for weak records and degenerate spectra; each has one discontinuity). Theorem 9: a state-only rule must jump, a single-basis history rule must jump, and a mixed rule (1 − c)Φ_pointer + cΦ_state does not, for two-outcome readouts. A general mixed rule (unequal overlaps, several readouts) is open. The earlier degenerate-input numbers were rechecked under Theorem 7 (no-signalling results unchanged; Alice's outputs change).
3. **The paradox-world fallback.** Theorem 6 shows it is the only freedom left once (U1)–(U4) hold. Theorem 8 derives it as the limit of a loop with noise that has no preferred basis: the open loop, which replaces D-CTC. Remaining: the derivation needs that assumption on the noise, and PPS is still discontinuous as C|k⟩ → 0.
4. ~~**The main statements of Theorems 1 and 2 are for classical reversible circuits only.**~~ Theorems 1Q and 2Q: for any U, outcomes with no returning history in some loop basis never occur, and PPS is conditioning on the loop returning plus explicit interference terms.
5. **Computational power.** Theorem 8(3): with one loop and a recorded input, PPS decides exactly PP with the open-loop fallback, and exactly PSPACE with the D-CTC fallback ([PERSPECTIVES.md](../PERSPECTIVES.md), 1.5). Several loops with records between them: open.
6. **Quantum fields.** In a field toy ([FIELD_LOOP.md](FIELD_LOOP.md)) PPS inherits P-CTC's chronology-protection divergence (−Li₂(c)/Δ² from vacuum windings inside every world), while D-CTC gives none. A real QFT calculation on a curved spacetime has not been done.
