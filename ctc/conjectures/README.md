# Conjecture lottery: letting the computer settle questions the AI could not predict

Created 2026-11-23 with AI assistance (Claude). No external review.

## Purpose

The earlier experiments all had outcomes that could be computed in advance: without a real time loop, past-preserving selection (PPS) equals ordinary quantum mechanics (Theorem 3). This experiment asks instead about **the mathematical consequences of the theory itself**, and only questions whose answers I (Claude) genuinely did not know beforehand.

## Method

1. **Pool ([pool.py](pool.py)):** 6 circuit classes × 10 properties = 60 conjectures, each of the form "every circuit in this class has this property".
2. **Credences first, code second:** before any checking code existed, I wrote down the probability that each conjecture holds ([credences.json](credences.json)) and recorded the hashes in the conversation log:
   - `credences.json` SHA-256 `1d7ad527ba9ee95d720109fae7fdf1614574343ceafc745babc934e11eb87c9d`
   - `pool.py` SHA-256 `6ec2376a9f71c9130a8780b7382a30f0de8f06dfdc8c6276581524ad661b2fe2`
   - [evaluate.py](evaluate.py) checks the hash of `credences.json` on start and refuses to run if it changed.
3. **Selection by credence:** only conjectures to which I gave 35%–65% were tested: 11 in total. The other 49 I was confident about (some I worked out while writing them) and they are not scored.
4. **Strict verdicts:**
   - Finite sets (all 40320 classical reversible circuits, all 11520 two-qubit Clifford circuits) are enumerated exhaustively: the result is a **proof** or a **counterexample**.
   - Continuous sets (random unitaries) are searched for counterexamples within a fixed budget, with the random seed derived from the hash of `credences.json`: the result is a **counterexample** or **not refuted** (not a proof).
5. **Score:** Brier score = mean of (my probability − actual outcome)². Complete ignorance gives an expected 0.25; higher means the outcomes surprised me more.

The originally planned "draw questions using a future block hash" was replaced by **testing all 11**: no selection at all, which is stricter than drawing.

## Deviations from the plan

- The Clifford-group generator hung on its first run (`-0.0` and `0.0` were treated as different matrices); after the fix it produced the correct 11520 elements. This happened before any conjecture was evaluated.
- Before the scored run, the checking code was validated on cases with known answers (Theorem 3, refusal to send, grandfather paradox), none of which are among the 11 selected conjectures.

## Results (2026-11-23, [results.json](results.json))

| Conjecture | My probability | Result | Counterexamples / checked |
|---|---|---|---|
| Classical 2+1: PPS future effect ≤ P-CTC | 0.50 | **refuted** | 576 / 40320 |
| Classical 1+2: PPS does not increase entropy | 0.45 | **refuted** | 4224 / 40320 |
| Classical 1+2: PPS future effect ≤ P-CTC | 0.50 | **proved** | 0 / 40320 |
| Clifford: pure-state output | 0.40 | **refuted** | 1728 / 11520 |
| Clifford: does not increase entropy | 0.55 | **proved** | 0 / 11520 |
| Clifford: probability distribution equals no loop | 0.40 | **refuted** | 2880 / 11520 |
| Clifford: future effect ≤ P-CTC | 0.50 | **proved** | 0 / 11520 |
| Clifford: preserves the maximally mixed state | 0.35 | **refuted** | 4896 / 11520 |
| Clifford: output commutes with no loop | 0.50 | **proved** | 0 / 11520 |
| Random 1+1: future effect ≤ P-CTC | 0.50 | not refuted | 0 / 20000 |
| Random 2+1: future effect ≤ P-CTC | 0.50 | **refuted** | 495 / 3000 |

**Brier score 0.213**, only slightly better than a coin (0.25): these 11 questions were indeed close to unknown for me. 5 proved, 5 refuted, 1 not refuted.

**An unexpected pattern (exploratory, not preregistered):** "the PPS future effect does not exceed P-CTC's" holds in all three classes where the CR system is one qubit (two proved exhaustively, one not refuted by random search) and fails in both classes where it is two qubits. This suggests a new conjecture: for a single-qubit CR system the inequality holds for every unitary. It can be a question for the next round.

## Rerunning

```text
python -B ctc/conjectures/evaluate.py        # evaluate and score only the 11 preselected questions
python -B ctc/conjectures/evaluate.py --all  # also evaluate the other 49 (exploratory, unscored)
```
