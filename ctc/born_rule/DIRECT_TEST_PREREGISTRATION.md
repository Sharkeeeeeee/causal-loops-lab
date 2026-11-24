# Preregistration: direct pure-vs-recorded test

Fixed before the hardware job is submitted; its SHA-256 is stored with the results.

## Circuits

On each of many disjoint qubit pairs (q, r), group A (isolated): RY(theta) on q, measure q and r.
Group B (recorded): RY(theta) on q, CNOT q -> r, measure q and r. theta in {0, +pi/2, -pi/2, +pi, -pi}.
Ten circuits, all pairs in parallel, the same number of shots each. No twirling, no dynamical
decoupling, no readout correction: the signal is built to cancel linear errors instead.

## Signal

Delta(theta) = P_A(q=1) - P_B(q=1);  S = [Delta(+pi/2) + Delta(-pi/2)]/2 - [Delta(0) + (Delta(+pi) + Delta(-pi))/2]/2,
computed per pair and averaged over pairs.

## Predictions

- Standard quantum mechanics, with any linear noise after the preparation: S = 0. A miscalibrated RY
  adds S_prep = (b - a)(p_h - p_pi/2), estimated from group A and reported as prep_systematic; it does
  not enter the decision unless |prep_systematic| exceeds one standard error, in which case S - prep_systematic
  is also reported.
- Loop model with Z-basis coupling (ctc/born_rule/model.py): S = eps [w/(1+w) - 1/2], w = cos^2(phi/2),
  about -/+ eps phi^2/16 (sign depends on which basis state is coupled).

## Decision rules

- Standard error: the larger of (a) pair-to-pair spread / sqrt(pairs) and (b) shot noise.
- |z| < 3.0: no deviation. Report the 95% bound |S| < |S_mean| + 1.96 SE and the resulting
  limit eps < bound / |w/(1+w) - 1/2| for each phi.
- 3.0 <= |z| < 5.0: inconclusive; report as such.
- |z| >= 5.0: anomaly. Before any interpretation: rerun on other qubits and another device, and look
  for nonlinear hardware effects (for example readout saturation, leakage), which this design does not cancel.

## Known limits

- The test probes loops that couple in the Z basis and act while the state is isolated at measurement.
- The model's timing is not fixed: in group B the qubit is also isolated for the short time before the
  CNOT. If loops act then too, the predicted S is reduced by the fraction of exposure B shares with A.
- Nonlinear hardware effects are not cancelled.
