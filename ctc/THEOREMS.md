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

## Hardware experiments

These examples were all run on IBM quantum computers; code and full results are in [hardware/](hardware/README.md). The last column is the PPS value measured in the third run (ibm_kingston, predictions and criteria fixed before submission, 21 of 21 criteria pass):

| Experiment | Theorem | No loop | P-CTC | PPS | Measured |
|---|---|---|---|---|---|
| Grandfather paradox, P(gun jams) | Thm 1(2)(3), Thm 2(1) | 0.2 | 1 | **0.2** | 0.211 |
| Refusal to send, P(a = 1) (past) | Thm 2(1) | 0.5 | 1/3 | **0.5** | 0.503 |
| Refusal to send, P(message recorded \| a = 1) (future) | Thm 1(1), Thm 2(2) | 0.5 | 0 | **0** | 0.035 |
| One-way control, P(a = 1) | Thm 3, P-CTC counterexample | 0.5 | 0 | **0.5** | 0.495 |
| Quantum eraser, Bob's which-path statistics | Thm 0 | 0.5 | 0.667 | **0.5** | 0.501 |
| Quantum eraser, fringe visibility sorted by Bob | PAST_PRESERVING.md | 0.707 | 0.943 | **0.943** | 0.870 |

The numbers for all rules come from the same shots, so the hardware results show that the predictions are measurable, not that nature uses PPS. The values are standard quantum mechanics applied to postselected circuits.

## Not yet proved

1. **Theorem 3 covers only controlled-form U.** Whether every unitary in which "the loop does not affect A" can be written this way is not proved here.
2. **Choice of record basis.** In Theorem 3 the record basis is fixed naturally, but in general (for example the entangled double slit in PAST_PRESERVING.md) different record bases give different predictions. This is still the largest open problem of PPS.
3. **Falling back to D-CTC in paradox worlds is a seam.** Theorem 1(2) says what it does in those worlds, not why nature should do it.
4. **The main statements of Theorems 1 and 2 are for classical reversible circuits only.** For a general quantum U the corresponding statement is "world k outputs the state of successful Bell postselection", which is the definition of PPS and has less content.
5. **Computational power.** On definite inputs PPS equals P-CTC, so it is at least as powerful as P-CTC (PostBQP); no upper bound is proved ([PERSPECTIVES.md](../PERSPECTIVES.md), 1.5; `tests/test_computational_power.py`).
