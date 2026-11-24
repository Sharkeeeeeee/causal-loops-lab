# Time-loop rules on IBM quantum computers

Created 2026-11-23 with AI assistance (Claude). No external review.

**These experiments send nothing to the past.** They implement loop rules by postselected teleportation (the method of Lloyd et al. 2011), and postselection can always be explained in the normal time direction. What they test is whether the predictions in [THEOREMS.md](../THEOREMS.md) are measurable on real, noisy hardware.

## Summary

The third run (2026-11-23, `ibm_kingston`, job `dc1j37ts2omc738amaa0`) had its predictions and criteria fixed before submission ([PREREGISTRATION.md](PREREGISTRATION.md), SHA-256 `956fe5a6…`). **All 21 criteria pass:**

| Quantity | Rule | Exact prediction | Measured (std) |
|---|---|---|---|
| Grandfather paradox, P(gun jams) | P-CTC | 1 | 0.935 (0.008) |
| | PPS | 0.2 | 0.211 (0.004) |
| Refusal to send, P(a = 1) (past) | P-CTC | 0.333 | 0.344 (0.006) |
| | PPS | 0.5 | 0.503 (0.004) |
| Refusal to send, P(message recorded \| a = 1) (inconsistent history) | no loop | 0.5 | 0.504 (0.006) |
| | PPS | 0 | 0.035 (0.005) |
| One-way control, P(a = 1) | P-CTC | 0 | 0.021 (0.005) |
| | PPS | 0.5 | 0.495 (0.005) |
| Quantum eraser: Bob's own which-path statistics P(Z = 0) | P-CTC | 0.667 | 0.662 (0.004) |
| | PPS | 0.5 | 0.501 (0.004) |
| Quantum eraser: fringe visibility sorted by Bob's X = + | no loop | 0.707 | 0.645 (0.013) |
| | PPS | 0.943 | 0.870 (0.014) |
| Quantum eraser: fringe phase shift (rad) | PPS | 0.785 (π/4) | 0.774 (0.017) |

Full table: [data/ibm_ibm_kingston_dc1j37ts2omc738amaa0_report.md](data/ibm_ibm_kingston_dc1j37ts2omc738amaa0_report.md). PPS = past-preserving selection.

**What this shows:** every effect predicted by the theorems was measured on hardware, in agreement with theory: P-CTC changes the past and PPS does not; inconsistent histories are suppressed to 3.5%; P-CTC deletes a world the loop does not even affect; P-CTC changes a distant Bob's statistics (signalling) and PPS does not; the eraser's fringes appear only after sorting by Bob's result, with a π/4 shift.

**What this does not show:** all rules are computed from **the same shots**, sorted differently. So the experiment cannot tell which rule nature uses, let alone show that time loops exist. Under PPS the world weights (including Bob's own statistics) are taken from all shots by construction; their agreement with the predictions tests the hardware, not the rule. All predicted values follow from standard quantum mechanics.

## One circuit, three rules

Each circuit has at most 6 qubits:

1. A random CR input is prepared with RY and copied by a CNOT to a record qubit. The record qubit is the "recorded past"; in the eraser it is Bob's idler.
2. Loop qubit m and partner qubit p start in the Bell state |Φ⁺⟩.
3. U acts on CR⊗m.
4. A Bell measurement on (m, p); outcome 00 means the loop closed consistently.

| Rule | How it is computed from the data |
|---|---|
| No loop (unknown external message) | ignore the Bell outcome; m alone is maximally mixed |
| P-CTC | keep only shots with Bell outcome 00 |
| PPS | weight of each world from all shots; within a world keep only 00 shots. Worlds with no consistent history fall back to D-CTC; for these circuits the D-CTC fixed point is maximally mixed, so this equals ignoring the Bell outcome (verified exactly by `fallback_matches_no_loop`) |

## Experiments

| Experiment | Story | Theorems tested |
|---|---|---|
| `grandfather` | on receiving m, send back NOT m; when the gun jams (probability 0.2), do nothing | Thm 1(2)(3), Thm 2(1) |
| `refusal` | the receiver writes the message in a log; if a = 1, the sender refuses to send a message already received | Thm 1(1), Thm 2 |
| `one_way` | a controls a NOT on the loop; the loop never acts on a | Thm 3 and the P-CTC counterexample |
| `eraser_x`, `eraser_y` | the double-slit path is entangled with Bob's idler; the message from the future adds a π/2 phase to the right slit. Bob reads X (erasure); the path is read in X and Y, together giving the fringe | Thm 0; the double-slit result of PAST_PRESERVING.md |
| `eraser_z` | as above, but Bob reads Z (which-path) | direct demonstration of P-CTC signalling |

## How to run

Needs Python 3.11 and `qiskit`. Real hardware also needs `qiskit-ibm-runtime` and an IBM Quantum account (the free plan currently gives 10 minutes of QPU time per month; the third run used 83 seconds).

```text
python -B ctc/tests/test_hardware.py      # circuit, estimator and readout-correction checks
python -B ctc/hardware/run_local.py       # ideal simulator, full analysis pipeline
python -B ctc/hardware/preregister.py     # fix predictions and criteria before submission
python -B ctc/hardware/run_ibm.py --dry-run
python -B ctc/hardware/run_ibm.py --backend ibm_kingston
```

Saving your account (once; the code never asks for or stores your key):

```python
from qiskit_ibm_runtime import QiskitRuntimeService
QiskitRuntimeService.save_account(channel='ibm_quantum_platform', token='<your API key>', set_as_default=True)
```

What `run_ibm.py` does:

1. **Preflight:** a few seconds to measure the readout error of every qubit (published calibration data is not always reliable; see runs 1 and 2 below).
2. **Layout:** exclude qubits with measured readout error above 3%; enumerate every placement of each circuit on the coupling graph with VF2, and pick the one with the smallest readout plus two-qubit gate error. No SWAPs are needed.
3. **Main job:** all experiments plus readout-calibration circuits for each set of qubits, with dynamical decoupling (XpXm) and Pauli twirling of gates and measurements.
4. **Analysis:** readout correction, then bootstrap standard errors (resampling both experiment shots and calibration data), then evaluation of each preregistered criterion.

## Caveats

- **Readout correction matters.** In the third run, qubit 147 (the CR qubit of the grandfather, one-way and eraser experiments) had a measured readout error of 0.46% in the preflight and about 8% a few minutes later in the main job's calibration circuits. The cause is unknown: drift, or something related to measurement twirling. Calibration in the same job caught it, the correction matrix is well conditioned (1 − e₀ − e₁ ≈ 0.83), and the standard errors include the calibration uncertainty. But the uncorrected numbers are clearly worse: the PPS grandfather value is 0.263 uncorrected, which would fail criterion C2.
- **The eraser visibility only just passes:** 0.870 against a threshold of 0.85. The no-loop visibility drops by the same factor (0.645 vs 0.707); both ratios are about 0.92, consistent with ordinary decoherence rather than a deviation of the rule itself. A future run should preregister the visibility relative to no-loop instead of an absolute threshold.
- **The preregistration has no external timestamp.** The results file records retrieval at 2026-11-22T18:18:36Z, and `PREREGISTRATION.md` and the results were added to git in the same commit (2026-11-22T18:26:27Z). The SHA-256 in the results file is written by `run_ibm.py` itself, so it proves what the preregistration said when the results were saved, not that it existed before submission. The next run should push the preregistration to GitHub or another timestamped store before submitting ([PERSPECTIVES.md](../../PERSPECTIVES.md), 2.2).
- **Not the first P-CTC experiment on a programmable quantum computer.** A 2025 experiment ran on IBM and Quantinuum processors (arXiv:2501.16335, see [LITERATURE_REVIEW.md](../../LITERATURE_REVIEW.md)); Lloyd et al. 2011 and Ringbauer et al. 2014 were optical experiments.
- **The eraser's record basis.** The eraser's PPS values use the X record basis ("Bob reads X"). Theorem 4 (THEOREMS.md, added 2026-11-24) takes the record basis from the interaction instead; the idler's CNOT reads the path in Z, and in the Z basis PPS predicts no Bob-sorted fringes. The X-basis numbers here remain correct measurements of that variant.
- **The criteria were set after the first two runs.** The thresholds therefore took the noise level of those runs into account; the eraser circuits were run for the first time.
- **Quantities that "should be 0" are limited by two-qubit gate errors.** The inconsistent history in the refusal experiment fell from 0.112 (13 two-qubit gates) to 0.035 (7), and readout correction cannot fix that part.

## Run history

| Run | Device | Improvements | Inconsistent history (should be 0) | One-way control, P-CTC (should be 0) |
|---|---|---|---|---|
| 1. `dc1iqhdhdvas73bkt2bg` | ibm_marrakesh | none | 0.112 | 0.061 |
| 2. `dc1isqinj2vs73dfdkrg` | ibm_marrakesh | DD, twirling, readout correction | 0.095 | 0.045 |
| 3. `dc1j37ts2omc738amaa0` | ibm_kingston | the above + shorter circuits, measured-error layout, quantum eraser, preregistration | **0.035** | **0.021** |

- In run 1 the a = 0 world of the one-way experiment had a Bell pass rate of only 0.383. I interpreted this as a phase error at the time, **which was wrong**: readout correction in run 2 showed that qubit 42, holding the loop qubit, had a readout error of about 40%, against a published 0.66%. This is why run 3 chose its layout from measured errors.
- The data files of runs 1 and 2 were produced by an older version of the code; `analyze.py` still reads them, but those runs had no eraser experiment.
