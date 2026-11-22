backend: qiskit StatevectorSampler (ideal)   shots per experiment: 16384
error suppression: ideal simulator; readout calibration path exercised with ideal calibration
measured = readout-corrected (raw = uncorrected); std from a bootstrap over shots and readout calibration

## Grandfather paradox: the gun jams with prior 0.2

| quantity | rule | exact | measured | std | raw |
|---|---|---|---|---|---|
| P(jam = 1)  [past] | no loop | 0.200 | 0.199 | 0.003 | 0.199 |
| P(jam = 1)  [past] | P-CTC | 1.000 | 1.000 | 0.000 | 1.000 |
| P(jam = 1)  [past] | past-preserving | 0.200 | 0.199 | 0.003 | 0.199 |

readout error per clbit, P(1|0): 0.000, 0.000, 0.000, 0.000;  P(0|1): 0.000, 0.000, 0.000, 0.000

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'jam': 0} | 0.000 | 0.000 |
| {'jam': 1} | 1.000 | 1.000 |

## Refusal: if a = 1 the sender never sends a message it received

| quantity | rule | exact | measured | std | raw |
|---|---|---|---|---|---|
| P(a = 1)  [past] | no loop | 0.500 | 0.498 | 0.004 | 0.498 |
| P(message logged, given a = 1)  [future] | no loop | 0.500 | 0.502 | 0.005 | 0.502 |
| P(message logged, given a = 0)  [future] | no loop | 0.500 | 0.498 | 0.005 | 0.498 |
| P(a = 1)  [past] | P-CTC | 0.333 | 0.338 | 0.006 | 0.338 |
| P(message logged, given a = 1)  [future] | P-CTC | 0.000 | 0.000 | 0.000 | 0.000 |
| P(message logged, given a = 0)  [future] | P-CTC | 0.500 | 0.496 | 0.008 | 0.496 |
| P(a = 1)  [past] | past-preserving | 0.500 | 0.498 | 0.004 | 0.498 |
| P(message logged, given a = 1)  [future] | past-preserving | 0.000 | 0.000 | 0.000 | 0.000 |
| P(message logged, given a = 0)  [future] | past-preserving | 0.500 | 0.496 | 0.008 | 0.496 |

readout error per clbit, P(1|0): 0.000, 0.000, 0.000, 0.000, 0.000;  P(0|1): 0.000, 0.000, 0.000, 0.000, 0.000

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'a': 0} | 0.502 | 0.500 |
| {'a': 1} | 0.258 | 0.250 |

## One-way control: a controls the loop, the loop never acts on a

| quantity | rule | exact | measured | std | raw |
|---|---|---|---|---|---|
| P(a = 1)  [past; equals the record held by a partner] | no loop | 0.500 | 0.498 | 0.004 | 0.498 |
| P(a = 1)  [past; equals the record held by a partner] | P-CTC | 0.000 | 0.000 | 0.000 | 0.000 |
| P(a = 1)  [past; equals the record held by a partner] | past-preserving | 0.500 | 0.498 | 0.004 | 0.498 |

readout error per clbit, P(1|0): 0.000, 0.000, 0.000, 0.000;  P(0|1): 0.000, 0.000, 0.000, 0.000

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'a': 0} | 1.000 | 1.000 |
| {'a': 1} | 0.000 | 0.000 |

## Delayed-choice eraser with a loop: path measured in X

| quantity | rule | exact | measured | std | raw |
|---|---|---|---|---|---|
| P(Bob idler reads X = +)  [Bob's own statistics] | no loop | 0.500 | 0.502 | 0.004 | 0.502 |
| P(path reads X = +)  [whole screen] | no loop | 0.500 | 0.501 | 0.004 | 0.501 |
| P(path reads X = +, given Bob X = +)  [sorted fringe] | no loop | 0.750 | 0.752 | 0.005 | 0.752 |
| P(Bob idler reads X = +)  [Bob's own statistics] | P-CTC | 0.500 | 0.503 | 0.005 | 0.503 |
| P(path reads X = +)  [whole screen] | P-CTC | 0.500 | 0.504 | 0.004 | 0.504 |
| P(path reads X = +, given Bob X = +)  [sorted fringe] | P-CTC | 0.833 | 0.836 | 0.005 | 0.836 |
| P(Bob idler reads X = +)  [Bob's own statistics] | past-preserving | 0.500 | 0.502 | 0.004 | 0.502 |
| P(path reads X = +)  [whole screen] | past-preserving | 0.500 | 0.504 | 0.004 | 0.504 |
| P(path reads X = +, given Bob X = +)  [sorted fringe] | past-preserving | 0.833 | 0.836 | 0.005 | 0.836 |

readout error per clbit, P(1|0): 0.000, 0.000, 0.000, 0.000;  P(0|1): 0.000, 0.000, 0.000, 0.000

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'a': 0} | 0.750 | 0.750 |
| {'a': 1} | 0.748 | 0.750 |

## Delayed-choice eraser with a loop: path measured in Y

| quantity | rule | exact | measured | std | raw |
|---|---|---|---|---|---|
| P(Bob idler reads X = +)  [Bob's own statistics] | no loop | 0.500 | 0.502 | 0.004 | 0.502 |
| P(path reads Y = +)  [whole screen] | no loop | 0.500 | 0.501 | 0.004 | 0.501 |
| P(path reads Y = +, given Bob X = +)  [sorted fringe] | no loop | 0.750 | 0.752 | 0.005 | 0.752 |
| P(Bob idler reads X = +)  [Bob's own statistics] | P-CTC | 0.500 | 0.503 | 0.005 | 0.503 |
| P(path reads Y = +)  [whole screen] | P-CTC | 0.500 | 0.504 | 0.004 | 0.504 |
| P(path reads Y = +, given Bob X = +)  [sorted fringe] | P-CTC | 0.833 | 0.836 | 0.005 | 0.836 |
| P(Bob idler reads X = +)  [Bob's own statistics] | past-preserving | 0.500 | 0.502 | 0.004 | 0.502 |
| P(path reads Y = +)  [whole screen] | past-preserving | 0.500 | 0.504 | 0.004 | 0.504 |
| P(path reads Y = +, given Bob X = +)  [sorted fringe] | past-preserving | 0.833 | 0.836 | 0.005 | 0.836 |

readout error per clbit, P(1|0): 0.000, 0.000, 0.000, 0.000;  P(0|1): 0.000, 0.000, 0.000, 0.000

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'a': 0} | 0.750 | 0.750 |
| {'a': 1} | 0.748 | 0.750 |

## Eraser, Bob reads which-path (Z): P-CTC changes Bob's own statistics

| quantity | rule | exact | measured | std | raw |
|---|---|---|---|---|---|
| P(Bob idler reads Z = 0)  [Bob's own statistics] | no loop | 0.500 | 0.502 | 0.004 | 0.502 |
| P(path reads Z = 1, right slit) | no loop | 0.500 | 0.498 | 0.004 | 0.498 |
| P(Bob idler reads Z = 0)  [Bob's own statistics] | P-CTC | 0.667 | 0.670 | 0.004 | 0.670 |
| P(path reads Z = 1, right slit) | P-CTC | 0.333 | 0.330 | 0.004 | 0.330 |
| P(Bob idler reads Z = 0)  [Bob's own statistics] | past-preserving | 0.500 | 0.502 | 0.004 | 0.502 |
| P(path reads Z = 1, right slit) | past-preserving | 0.500 | 0.498 | 0.004 | 0.498 |

readout error per clbit, P(1|0): 0.000, 0.000, 0.000, 0.000;  P(0|1): 0.000, 0.000, 0.000, 0.000

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'a': 0} | 1.000 | 1.000 |
| {'a': 1} | 0.498 | 0.500 |

## Eraser fringe (from the X and Y circuits)

| fringe | rule | exact V | measured V | std | exact shift | measured shift | std |
|---|---|---|---|---|---|---|---|
| sorted by Bob X = + | no loop | 0.707 | 0.712 | 0.009 | 0.785 | 0.785 | 0.015 |
| whole screen | no loop | 0.000 | 0.004 | 0.005 | n/a | 0.785 | 1.484 |
| sorted by Bob X = + | P-CTC | 0.943 | 0.951 | 0.010 | 0.785 | 0.785 | 0.011 |
| whole screen | P-CTC | 0.000 | 0.012 | 0.007 | n/a | 0.785 | 0.923 |
| sorted by Bob X = + | past-preserving | 0.943 | 0.951 | 0.010 | 0.785 | 0.785 | 0.011 |
| whole screen | past-preserving | 0.000 | 0.011 | 0.007 | n/a | 0.785 | 1.048 |

## Criteria (applied after the fact: this run was not preregistered)

| criterion | quantity | value | result |
|---|---|---|---|
| C1 | grandfather: P(jam = 1)  [past] | PP - P-CTC = -0.801 (exact -0.800), z = -259.1 | PASS |
| C1 | refusal: P(a = 1)  [past] | PP - P-CTC = +0.160 (exact +0.167), z = 34.6 | PASS |
| C1 | one_way: P(a = 1)  [past; equals the record held by a partner] | PP - P-CTC = +0.498 (exact +0.500), z = 127.9 | PASS |
| C1 | eraser_z: P(Bob idler reads Z = 0)  [Bob's own statistics] | PP - P-CTC = -0.167 (exact -0.167), z = -71.1 | PASS |
| C1 | eraser_z: P(path reads Z = 1, right slit) | PP - P-CTC = +0.167 (exact +0.167), z = 71.1 | PASS |
| C2 | grandfather: P(jam = 1)  [past] | measured - exact = -0.001 | PASS |
| C2 | refusal: P(a = 1)  [past] | measured - exact = -0.002 | PASS |
| C2 | refusal: P(message logged, given a = 1)  [future] | measured - exact = +0.000 | PASS |
| C2 | refusal: P(message logged, given a = 0)  [future] | measured - exact = -0.004 | PASS |
| C2 | one_way: P(a = 1)  [past; equals the record held by a partner] | measured - exact = -0.002 | PASS |
| C2 | eraser_x: P(Bob idler reads X = +)  [Bob's own statistics] | measured - exact = +0.002 | PASS |
| C2 | eraser_x: P(path reads X = +)  [whole screen] | measured - exact = +0.004 | PASS |
| C2 | eraser_x: P(path reads X = +, given Bob X = +)  [sorted fringe] | measured - exact = +0.003 | PASS |
| C2 | eraser_y: P(Bob idler reads X = +)  [Bob's own statistics] | measured - exact = +0.002 | PASS |
| C2 | eraser_y: P(path reads Y = +)  [whole screen] | measured - exact = +0.004 | PASS |
| C2 | eraser_y: P(path reads Y = +, given Bob X = +)  [sorted fringe] | measured - exact = +0.003 | PASS |
| C2 | eraser_z: P(Bob idler reads Z = 0)  [Bob's own statistics] | measured - exact = +0.002 | PASS |
| C2 | eraser_z: P(path reads Z = 1, right slit) | measured - exact = -0.002 | PASS |
| C3 | eraser: sorted visibility 0.951 (>= 0.85) | | PASS |
| C3 | eraser: shift 0.785 rad (exact 0.785, tol 0.15) | | PASS |
| C3 | eraser: visibility over no loop: z = 35.2 (>= 5.0) | | PASS |

**21 of 21 checks pass.**

