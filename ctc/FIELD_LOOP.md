# A field mode on a time loop: does the consistency rule change the chronology-protection divergence?

Created 2026-11-26 with AI assistance (Claude). No external review. A toy model, not quantum field theory on a curved spacetime. Code: `ctc/field_loop.py`; checks: `ctc/tests/test_field_loop.py` (7 tests).

## The question

Hawking's chronology-protection argument: as a time machine forms, vacuum fluctuations circle the loop again and again, and their energy diverges at the chronology horizon (Kim and Thorne 1991; Hawking 1992). The calculation sums over images, i.e. over windings around the loop, which is a path-integral prescription. Lloyd et al. 2011 state that P-CTC agrees with path integrals; D-CTC does not. So:

- Does the divergence depend on the consistency rule?
- In particular, what does PPS do? The earlier survey found this question essentially unstudied for P-CTC and PPS.

## Model

One frequency at a time.

- A field mode a (the CR system) meets the loop mode b at a beamsplitter of angle θ.
- b then runs once around the loop and picks up the phase φ = ωΔ, where Δ is the loop's time shift. The chronology horizon is Δ → 0.
- The coupling is passive and conserves frequency, so different frequencies stay independent and every rule factorizes over modes.

**Energy in the loop region.**

- Under P-CTC, and under PPS inside each world (Theorem 6), the loop has no state of its own.
- Its operational value is the weak value of the loop's photon number, ⟨n_b⟩_w = Tr[C_n ρ C†] / Tr[C ρ C†], with C = Tr_b U and C_n = Tr_b[U(𝟙 ⊗ n_b)]. Bishop, Costa and Ralph 2024 assign states to the loop by weak measurements in the same spirit.
- Under D-CTC the loop's state is the fixed point.

## Results

With z = cos θ · e^{iφ}:

| Input | P-CTC (and PPS for a pure input) | PPS, thermal input (worlds = Fock states, Theorem 7) | D-CTC |
|---|---|---|---|
| vacuum | z/(1 − z) (all windings: Σ m z^m / Σ z^m) | — | 0 |
| Fock state k | z/(1 − z) + k sin²θ / \|1 − z\|² | — | — |
| thermal, mean n̄ | global renormalization: differs slightly from PPS (1.619 vs 1.636 at θ = 1.2, φ = 0, n̄ = 0.5) | z/(1 − z) + n̄ sin²θ / \|1 − z\|² | n̄ |

Values are the real parts of ⟨n_b⟩_w, the weak-measurement pointer shift. The formulas are checked against a truncated two-mode calculation.

- **The vacuum term is the same in every world.** It comes from loop photons circling while the field mode enters and leaves empty, so it does not depend on the input. The second term is the classical build-up of real quanta in a ring cavity.
- **The vacuum term can be negative:** off resonance, when cos φ < cos θ.
- **Summed over a continuum of modes** (Abel regularization, mode weight ω) the vacuum term gives
      E_vac(Δ) = Σ_m c^m ∫ ω cos(mωΔ) dω = −Σ_m c^m / (mΔ)² = −Li₂(c) / Δ²,  with c = cos θ.
  - This is a sum over windings m, each damped by c^m, the same structure as the image sum, with c in the role of the defocusing factor.
  - It diverges as Δ → 0, at the chronology horizon, like 1/Δ² (tested: dividing Δ by 4 multiplies E by 16).
  - Li₂(1) = π²/6 is finite, so the divergence comes from Δ, not from the coupling.
- **D-CTC gives zero for the vacuum,** because the fixed point is the vacuum, and gives n̄ for a thermal input, with no resonance at all.

## What this suggests

1. **The divergence depends on the rule.** In this toy, the chronology-protection divergence appears under P-CTC and is absent under D-CTC. This fits the observation that the image sum is a path-integral (P-CTC-like) prescription.
2. **PPS does not remove it.** Theorem 6 forces P-CTC inside every world, and the divergent vacuum term lives inside every world, whatever the worlds are. PPS's worlds change only the finite term from real quanta.
3. **So the superposition principle inside a world, the assumption (U2) that singles out PPS, is also what carries the divergence.** A rule that escapes chronology protection in this way must give up (U2), as D-CTC does. Under PPS, a time machine of this kind would face the same instability as in the semiclassical calculations.
4. **The negative weak energy off resonance** is suggestive, since wormholes need negative energy, but a weak value is not an expectation value in a state. Nothing here says it could support a wormhole.

## Limits

- **A toy:**
  - one beamsplitter coupling per mode;
  - a continuum of modes with weight ω and Abel regularization;
  - no geometry, no defocusing beyond the constant c, and no back-reaction.
  It shows the structure of the divergence, not its size in any real spacetime.
- **Weak values as energy:** the weak value is the natural operational quantity for P-CTC, but semiclassical back-reaction would need an expectation value of the stress tensor, which P-CTC does not define for the loop.
- **The D-CTC result relies on the passive coupling.** Pienaar, Myers and Ralph 2011 (D-CTC for fields) and Tolksdorf and Verch (D-CTC in algebraic quantum field theory) were not read for this comparison.
- **Novelty not checked.**
