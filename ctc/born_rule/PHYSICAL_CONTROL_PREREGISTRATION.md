# Preregistration: physical-coherence control for the direct test

Fixed before submission; SHA-256 stored with the results.

## Why

The first direct test (job dc1k4l5hdvas73bkumqg) gave S = +0.0161 +/- 0.00155 (z about 10), positive on all
24 pairs. Its +/- pi/2 preparations were the same physical pulse; the sign was a virtual frame change.
Errors that turn physical coherence into population were therefore not cancelled.

## Design

Same qubit pairs and groups as before (A isolated; B recorded by CNOT q -> r). Preparations in native
gates, transpiled at optimization level 0: '0' none; '+h' sx; '-h' x then sx (opposite physical coherence,
same population); 'pi' x. S = [Delta(+h) + Delta(-h)]/2 - [Delta(0) + Delta(pi)]/2, where
Delta = P_A(q=1) - P_B(q=1). Also reported: odd part O = [Delta(+h) - Delta(-h)]/2.

## Predictions

| hypothesis | S | O |
|---|---|---|
| coherence-to-population hardware error (crosstalk) | about 0 | about +0.016 (carries the old signal) |
| loop model (population-only reweighting of isolated superpositions) | about +0.016 | about 0 |
| standard QM, no such error | 0 | 0 |

## Decision rules

Standard error = larger of pair spread / sqrt(pairs) and shot noise.
- |z(S)| < 3.0: no deviation; the first result is attributed to the uncancelled coherence error if O
  is also significant (|O| / SE_O >= 5) with the old sign.
- |z(S)| >= 5.0: the anomaly persists; then replicate on another device before any interpretation.
- In between: inconclusive.
