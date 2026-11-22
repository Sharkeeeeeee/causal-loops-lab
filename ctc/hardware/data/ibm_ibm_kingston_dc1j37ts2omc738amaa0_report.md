backend: ibm_kingston   shots per experiment: 16384   job: dc1j37ts2omc738amaa0
error suppression: dynamical decoupling (XpXm) + gate and measurement Pauli twirling + readout calibration
measured = readout-corrected (raw = uncorrected); std from a bootstrap over shots and readout calibration

preregistration SHA-256: 956fe5a64aabd5e7723580a0e7d45c2a8874bef3c757bd3896044b486732fd0b

physical qubits: grandfather [147, 148, 149, 137]; refusal [36, 40, 41, 42, 21]; one_way [147, 148, 149, 137]; eraser_x [147, 148, 149, 137]; eraser_y [147, 148, 149, 137]; eraser_z [147, 148, 149, 137]

## Grandfather paradox: the gun jams with prior 0.2

| quantity | rule | exact | measured | std | raw |
|---|---|---|---|---|---|
| P(jam = 1)  [past] | no loop | 0.200 | 0.204 | 0.003 | 0.253 |
| P(jam = 1)  [past] | P-CTC | 1.000 | 0.935 | 0.008 | 0.854 |
| P(jam = 1)  [past] | past-preserving | 0.200 | 0.211 | 0.004 | 0.263 |

readout error per clbit, P(1|0): 0.087, 0.004, 0.005, 0.007;  P(0|1): 0.079, 0.005, 0.005, 0.006

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'jam': 0} | 0.018 | 0.000 |
| {'jam': 1} | 0.949 | 1.000 |

## Refusal: if a = 1 the sender never sends a message it received

| quantity | rule | exact | measured | std | raw |
|---|---|---|---|---|---|
| P(a = 1)  [past] | no loop | 0.500 | 0.503 | 0.004 | 0.502 |
| P(message logged, given a = 1)  [future] | no loop | 0.500 | 0.504 | 0.006 | 0.503 |
| P(message logged, given a = 0)  [future] | no loop | 0.500 | 0.506 | 0.006 | 0.505 |
| P(a = 1)  [past] | P-CTC | 0.333 | 0.344 | 0.006 | 0.347 |
| P(message logged, given a = 1)  [future] | P-CTC | 0.000 | 0.035 | 0.005 | 0.052 |
| P(message logged, given a = 0)  [future] | P-CTC | 0.500 | 0.497 | 0.008 | 0.495 |
| P(a = 1)  [past] | past-preserving | 0.500 | 0.503 | 0.004 | 0.502 |
| P(message logged, given a = 1)  [future] | past-preserving | 0.000 | 0.035 | 0.005 | 0.052 |
| P(message logged, given a = 0)  [future] | past-preserving | 0.500 | 0.497 | 0.008 | 0.495 |

readout error per clbit, P(1|0): 0.011, 0.009, 0.008, 0.004, 0.006;  P(0|1): 0.016, 0.011, 0.006, 0.004, 0.006

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'a': 0} | 0.481 | 0.500 |
| {'a': 1} | 0.250 | 0.250 |

## One-way control: a controls the loop, the loop never acts on a

| quantity | rule | exact | measured | std | raw |
|---|---|---|---|---|---|
| P(a = 1)  [past; equals the record held by a partner] | no loop | 0.500 | 0.501 | 0.005 | 0.501 |
| P(a = 1)  [past; equals the record held by a partner] | P-CTC | 0.000 | 0.021 | 0.005 | 0.107 |
| P(a = 1)  [past; equals the record held by a partner] | past-preserving | 0.500 | 0.495 | 0.005 | 0.494 |

readout error per clbit, P(1|0): 0.086, 0.003, 0.004, 0.005;  P(0|1): 0.086, 0.003, 0.005, 0.006

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'a': 0} | 0.970 | 1.000 |
| {'a': 1} | 0.021 | 0.000 |

## Delayed-choice eraser with a loop: path measured in X

| quantity | rule | exact | measured | std | raw |
|---|---|---|---|---|---|
| P(Bob idler reads X = +)  [Bob's own statistics] | no loop | 0.500 | 0.503 | 0.004 | 0.502 |
| P(path reads X = +)  [whole screen] | no loop | 0.500 | 0.498 | 0.005 | 0.504 |
| P(path reads X = +, given Bob X = +)  [sorted fringe] | no loop | 0.750 | 0.732 | 0.006 | 0.697 |
| P(Bob idler reads X = +)  [Bob's own statistics] | P-CTC | 0.500 | 0.502 | 0.004 | 0.501 |
| P(path reads X = +)  [whole screen] | P-CTC | 0.500 | 0.500 | 0.006 | 0.506 |
| P(path reads X = +, given Bob X = +)  [sorted fringe] | P-CTC | 0.833 | 0.811 | 0.007 | 0.762 |
| P(Bob idler reads X = +)  [Bob's own statistics] | past-preserving | 0.500 | 0.503 | 0.004 | 0.502 |
| P(path reads X = +)  [whole screen] | past-preserving | 0.500 | 0.501 | 0.006 | 0.507 |
| P(path reads X = +, given Bob X = +)  [sorted fringe] | past-preserving | 0.833 | 0.811 | 0.007 | 0.762 |

readout error per clbit, P(1|0): 0.078, 0.003, 0.004, 0.007;  P(0|1): 0.090, 0.003, 0.004, 0.005

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'a': 0} | 0.731 | 0.750 |
| {'a': 1} | 0.734 | 0.750 |

## Delayed-choice eraser with a loop: path measured in Y

| quantity | rule | exact | measured | std | raw |
|---|---|---|---|---|---|
| P(Bob idler reads X = +)  [Bob's own statistics] | no loop | 0.500 | 0.503 | 0.004 | 0.503 |
| P(path reads Y = +)  [whole screen] | no loop | 0.500 | 0.493 | 0.005 | 0.491 |
| P(path reads Y = +, given Bob X = +)  [sorted fringe] | no loop | 0.750 | 0.724 | 0.006 | 0.683 |
| P(Bob idler reads X = +)  [Bob's own statistics] | P-CTC | 0.500 | 0.502 | 0.004 | 0.502 |
| P(path reads Y = +)  [whole screen] | P-CTC | 0.500 | 0.493 | 0.006 | 0.491 |
| P(path reads Y = +, given Bob X = +)  [sorted fringe] | P-CTC | 0.833 | 0.804 | 0.007 | 0.749 |
| P(Bob idler reads X = +)  [Bob's own statistics] | past-preserving | 0.500 | 0.503 | 0.004 | 0.503 |
| P(path reads Y = +)  [whole screen] | past-preserving | 0.500 | 0.493 | 0.005 | 0.492 |
| P(path reads Y = +, given Bob X = +)  [sorted fringe] | past-preserving | 0.833 | 0.804 | 0.007 | 0.749 |

readout error per clbit, P(1|0): 0.083, 0.003, 0.005, 0.006;  P(0|1): 0.078, 0.004, 0.005, 0.006

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'a': 0} | 0.732 | 0.750 |
| {'a': 1} | 0.735 | 0.750 |

## Eraser, Bob reads which-path (Z): P-CTC changes Bob's own statistics

| quantity | rule | exact | measured | std | raw |
|---|---|---|---|---|---|
| P(Bob idler reads Z = 0)  [Bob's own statistics] | no loop | 0.500 | 0.501 | 0.004 | 0.503 |
| P(path reads Z = 1, right slit) | no loop | 0.500 | 0.515 | 0.005 | 0.514 |
| P(Bob idler reads Z = 0)  [Bob's own statistics] | P-CTC | 0.667 | 0.662 | 0.004 | 0.659 |
| P(path reads Z = 1, right slit) | P-CTC | 0.333 | 0.356 | 0.005 | 0.379 |
| P(Bob idler reads Z = 0)  [Bob's own statistics] | past-preserving | 0.500 | 0.501 | 0.004 | 0.503 |
| P(path reads Z = 1, right slit) | past-preserving | 0.500 | 0.513 | 0.005 | 0.505 |

readout error per clbit, P(1|0): 0.078, 0.003, 0.004, 0.006;  P(0|1): 0.080, 0.003, 0.004, 0.006

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'a': 0} | 0.966 | 1.000 |
| {'a': 1} | 0.496 | 0.500 |

## Eraser fringe (from the X and Y circuits)

| fringe | rule | exact V | measured V | std | exact shift | measured shift | std |
|---|---|---|---|---|---|---|---|
| sorted by Bob X = + | no loop | 0.707 | 0.645 | 0.013 | 0.785 | 0.769 | 0.020 |
| whole screen | no loop | 0.000 | 0.015 | 0.009 | n/a | -1.844 | 1.081 |
| sorted by Bob X = + | P-CTC | 0.943 | 0.870 | 0.014 | 0.785 | 0.774 | 0.017 |
| whole screen | P-CTC | 0.000 | 0.015 | 0.009 | n/a | -1.552 | 1.151 |
| sorted by Bob X = + | past-preserving | 0.943 | 0.870 | 0.014 | 0.785 | 0.774 | 0.017 |
| whole screen | past-preserving | 0.000 | 0.013 | 0.009 | n/a | -1.452 | 1.150 |

## Preregistered criteria

| criterion | quantity | value | result |
|---|---|---|---|
| C1 | grandfather: P(jam = 1)  [past] | PP - P-CTC = -0.725 (exact -0.800), z = -100.9 | PASS |
| C1 | refusal: P(a = 1)  [past] | PP - P-CTC = +0.158 (exact +0.167), z = 30.9 | PASS |
| C1 | one_way: P(a = 1)  [past; equals the record held by a partner] | PP - P-CTC = +0.474 (exact +0.500), z = 98.2 | PASS |
| C1 | eraser_z: P(Bob idler reads Z = 0)  [Bob's own statistics] | PP - P-CTC = -0.161 (exact -0.167), z = -58.3 | PASS |
| C1 | eraser_z: P(path reads Z = 1, right slit) | PP - P-CTC = +0.156 (exact +0.167), z = 54.2 | PASS |
| C2 | grandfather: P(jam = 1)  [past] | measured - exact = +0.011 | PASS |
| C2 | refusal: P(a = 1)  [past] | measured - exact = +0.003 | PASS |
| C2 | refusal: P(message logged, given a = 1)  [future] | measured - exact = +0.035 | PASS |
| C2 | refusal: P(message logged, given a = 0)  [future] | measured - exact = -0.003 | PASS |
| C2 | one_way: P(a = 1)  [past; equals the record held by a partner] | measured - exact = -0.005 | PASS |
| C2 | eraser_x: P(Bob idler reads X = +)  [Bob's own statistics] | measured - exact = +0.003 | PASS |
| C2 | eraser_x: P(path reads X = +)  [whole screen] | measured - exact = +0.001 | PASS |
| C2 | eraser_x: P(path reads X = +, given Bob X = +)  [sorted fringe] | measured - exact = -0.022 | PASS |
| C2 | eraser_y: P(Bob idler reads X = +)  [Bob's own statistics] | measured - exact = +0.003 | PASS |
| C2 | eraser_y: P(path reads Y = +)  [whole screen] | measured - exact = -0.007 | PASS |
| C2 | eraser_y: P(path reads Y = +, given Bob X = +)  [sorted fringe] | measured - exact = -0.029 | PASS |
| C2 | eraser_z: P(Bob idler reads Z = 0)  [Bob's own statistics] | measured - exact = +0.001 | PASS |
| C2 | eraser_z: P(path reads Z = 1, right slit) | measured - exact = +0.013 | PASS |
| C3 | eraser: sorted visibility 0.870 (>= 0.85) | | PASS |
| C3 | eraser: shift 0.774 rad (exact 0.785, tol 0.15) | | PASS |
| C3 | eraser: visibility over no loop: z = 25.7 (>= 5.0) | | PASS |

**21 of 21 checks pass.**

