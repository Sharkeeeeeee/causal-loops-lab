# Interference of isolated pure states: quantifying the prediction and comparing with data

Created 2026-11-23 with AI assistance (Claude). No external review.

```text
python -B ctc/tests/test_born_rule.py     # 6 checks, including an independent cross-check against past_preserving.py
python -B ctc/tests/test_born_direct.py   # 8 checks of the direct-test design
python -B ctc/born_rule/compare.py        # writes results.json and ../output/born_rule_bounds.png
```

![Born-rule bounds](../output/born_rule_bounds.png)

## Latest result: a direct test on IBM hardware (2026-11-23)

**No loop effect found.** 95% bound |S| < 1.16×10⁻³. For the model with Z-basis coupling:
- if every particle is affected (ε = 1), the loop phase must be below **0.136 rad** (existing data only constrained it to 0.37 rad);
- for φ between 0.14 and 0.98 rad this is the strongest constraint (pink line in the figure); for larger φ, Kauten et al. 2017 remains strongest.

There was one false alarm along the way, fully recorded below:

| Step | Result |
|---|---|
| 1. Direct test (job `dc1k4l5hdvas73bkumqg`, preregistration `7a44cf36…`) | S = +0.0161 ± 0.0016, z = 10.3, all 24 pairs in the same direction: "anomaly" by the criteria |
| 2. Investigation | a design flaw: IBM compiles ±π/2 into **the same physical pulse** (`sx`); the sign is only a virtual frame change. So hardware errors that turn coherence into population (for example crosstalk from the CNOT's pulses) were not cancelled. A crosstalk rotation of about 2° produces a fake signal of 0.017 (simulation in [test_born_direct.py](../tests/test_born_direct.py)) |
| 3. Preregistered control (job `dc1k84ts2omc738anop0`, preregistration `3a2a3a38…`) | pulses that really flip the physical coherence (`sx` vs `x`+`sx`): **S = −0.00014 ± 0.00052, z = −0.27**. The separated odd part O = +0.0150 ± 0.0018, positive on all 24 pairs. Exactly what crosstalk predicts, not what the loop model predicts |
| Conclusion | by the criteria, the first anomaly is attributed to an uncancelled coherence error. The control's S is a valid measurement and sets the bound above |

Code: [direct_test.py](direct_test.py) (first version), [physical_control.py](physical_control.py) (the control, and the current valid design). Data in [data/](data/).

**Lesson:** on a quantum computer, the "sign" of a gate is often only a software frame change, not a physical flip. Any design that relies on symmetry to cancel errors must check the pulses actually executed.

**Preregistration timing:** the preregistration files were hashed into the results but not published before submission, so there is no external timestamp (same limitation as the hardware runs; see [PERSPECTIVES.md](../../PERSPECTIVES.md), 2.2).

## Summary of the literature comparison

1. **Large loop couplings are already excluded.** If a loop adds a phase φ = π/2 to one path, the best three-slit experiment (Kauten et al. 2017, laser light) requires the affected fraction ε to be **below 0.28%**; below 0.04% near φ = π.
2. **Small loop couplings had not been tested.** For φ below about 0.37 rad, existing data could not exclude even ε = 1 (every particle affected).
3. **The reason is that existing experiments measure the wrong quantity.** They measure third-order interference (the Sorkin parameter κ); in this model κ scales only as φ⁴ (κ ≈ 0.0035 ε φ⁴), while the largest effect is **second order**: the population of a two-path superposition shifts directly by ε φ²/16.
4. **Hence the direct test above,** which had not been done before as far as we found: the same superposition, one group measured directly without a record, one group first entangled with an ancilla (recorded) and then measured; compare the two groups' probabilities. Ordinary quantum mechanics predicts no difference; the model predicts a shift in the unrecorded group.

**This is a constraint, not support.** Ordinary quantum mechanics predicts zero for every deviation, and all data agree with zero. This analysis asks: if the theory plus the assumption "nature contains microscopic loops" were true, how strong could the loops be?

## Model

This is a **hypothesis**, not known physics:

- With probability ε, a particle's path couples to a microscopic loop. When the particle takes path j, the loop qubit picks up a phase φ_j: U = Σ_j |j⟩⟨j| ⊗ diag(1, e^{iφ_j}).
- Then C = Tr_loop U, and each path amplitude is multiplied by c_j = (1 + e^{iφ_j})/2.
- For an **isolated pure state**, past-preserving selection equals P-CTC: ψ → Cψ/‖Cψ‖ (see "fresh photon" in [PAST_PRESERVING.md](../PAST_PRESERVING.md)).
- Whether a particle passed an open slit is a recorded fact (blocked particles are absorbed), so the probability of passing is unchanged; renormalization happens only within the passing worlds (tested).
- If all paths get the same phase, C is proportional to the identity and there is no effect. An effect needs the loop to couple **differently** to different paths. The comparison uses the simplest case: one path with phase φ.

### Two predictions

| Observable | Formula | Small φ |
|---|---|---|
| Population shift of a two-path superposition (\|β\|² = p) | ε [p w/(1 − p + p w) − p], w = cos²(φ/2) | −ε p(1−p) φ²/4 (−ε φ²/16 at p = 1/2) |
| Three-path Sorkin parameter κ₃ | numerical ([model.py](model.py)) | ≈ 0.0035 ε φ⁴ |

## Existing data

κ₃ follows Kauten et al. 2017: ε₃ = p_ABC − p_AB − p_AC − p_BC + p_A + p_B + p_C, δ₃ = |I_AB| + |I_AC| + |I_BC| with I_kl = p_kl − p_k − p_l, κ₃ = ε₃/δ₃, evaluated at the point of fully constructive interference.

| Experiment | System | Published result | \|κ₃\| bound used |
|---|---|---|---|
| Kauten et al. 2017, New J. Phys. 19, 033017 (arXiv:1508.03253) | five-path interferometer, laser light | κ₃ = 0.0 ± 3.1×10⁻⁵ | 6.2×10⁻⁵ (2σ) |
| same | heralded single photons | κ₃ = 0.0 ± 1.6×10⁻³ | 3.2×10⁻³ (2σ) |
| Jin et al. 2017, PRA 95, 012107 (arXiv:1612.08563); Park et al. 2012, NJP 14, 113025 (arXiv:1207.2321) | single NV-centre spin; liquid-state NMR | order 10⁻³ | 10⁻³ |
| Sinha et al. 2010, Science 329, 418 (arXiv:1007.4193) | three-slit photons | below 10⁻² | 10⁻² |

**Direct tests of the two-path population shift:** our search found **no** published dedicated bound (this does not mean nobody has done one, only that this search did not find it).

## Result: the largest ε each experiment allows

| Loop phase φ | Kauten (laser) | Kauten (single photons) | NV / NMR | Sinha |
|---|---|---|---|---|
| π/4 | 4.6×10⁻² | unconstrained | 0.71 | unconstrained |
| π/2 | **2.8×10⁻³** | 0.14 | 4.5×10⁻² | 0.41 |
| 3π/4 | 6.3×10⁻⁴ | 3.2×10⁻² | 1.0×10⁻² | 9.7×10⁻² |
| ≈ π | 3.7×10⁻⁴ | 1.9×10⁻² | 6.0×10⁻³ | 5.8×10⁻² |

The φ at which each experiment starts to constrain (ε < 1): Kauten laser 0.37, NV/NMR 0.73, Kauten single photons 0.96, Sinha 1.26 rad.

## Caveats

- **Model choices affect the numbers.** Coupling only one path, coupling in the path basis, and each particle being affected independently with probability ε are all choices. Other couplings change the numbers, but the structure "κ is a high-order effect, the two-path shift is second order" should remain (random-phase check: median |κ| about 0.065, but in 5% of cases below 6×10⁻⁴).
- **Whether laser light counts as an "isolated pure state".** Here the loop is assumed to act on every photon, so the laser data apply. If loops act only on genuine single-particle states, the single-photon bound (about 50 times weaker) should be used.
- **Reliability of the data.** Kauten 2017's definition and numbers were read from the original, but the table extraction was messy and splitting values from errors is our interpretation. Sinha, Jin and Park were read only at abstract level, using the orders of magnitude given there. Kauten cites Park's result as 0.001 ± 0.003, which does not exactly match Park's abstract. Cotter et al. 2017 (molecule interference) could not be obtained and is not included.
- **Corrected references.** The arXiv numbers first given for Jin, Park and Cotter were wrong and have been replaced by verified ones (no arXiv version of Cotter was found).
- **IBM qubits are only approximately isolated,** and the test checks the class of models with Z-basis loop coupling.
- **This is not direct evidence about time loops.** Even if a deviation were measured one day, many mundane explanations (detector nonlinearity, calibration errors) would have to be excluded first.

## The direct pure-vs-recorded test (done; see the top)

The original idea; the actual runs added endpoint subtraction and the physical-coherence control described at the top:

1. Prepare the superposition √(1−p)|0⟩ + √p|1⟩ (for example p = 1/2).
2. **Group A (isolated):** measure directly.
3. **Group B (recorded):** copy the state to an ancilla with a CNOT (a record), then measure.
4. Compare P(1) between the groups. The preparation pulses are identical, so calibration errors cancel between the groups.

Ordinary quantum mechanics predicts a difference of 0; the model predicts ε[p w/(1 − p + p w) − p]. A few hundred thousand shots reach a precision of about 10⁻³.
