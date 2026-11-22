backend: ibm_marrakesh   shots per experiment: 8192   job: dc1isqinj2vs73dfdkrg
error suppression: dynamical decoupling (XpXm) + gate and measurement Pauli twirling + readout calibration
measured = readout-corrected (raw = uncorrected); std from a bootstrap over shots and readout calibration

## Grandfather paradox: the gun jams with prior 0.2

| quantity | rule | exact | measured | std | raw |
|---|---|---|---|---|---|
| P(jam = 1)  [past] | no loop | 0.200 | 0.206 | 0.004 | 0.210 |
| P(jam = 1)  [past] | P-CTC | 1.000 | 0.929 | 0.008 | 0.896 |
| P(jam = 1)  [past] | past-preserving | 0.200 | 0.213 | 0.005 | 0.222 |

readout error per clbit, P(1|0): 0.009, 0.008, 0.009, 0.006;  P(0|1): 0.011, 0.007, 0.007, 0.008

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'jam': 0} | 0.023 | 0.000 |
| {'jam': 1} | 0.916 | 1.000 |

## Refusal: if a = 1 the sender never sends a message it received

| quantity | rule | exact | measured | std | raw |
|---|---|---|---|---|---|
| P(a = 1)  [past] | no loop | 0.500 | 0.507 | 0.006 | 0.505 |
| P(message logged, given a = 1)  [future] | no loop | 0.500 | 0.507 | 0.008 | 0.505 |
| P(message logged, given a = 0)  [future] | no loop | 0.500 | 0.490 | 0.008 | 0.489 |
| P(a = 1)  [past] | P-CTC | 0.333 | 0.363 | 0.009 | 0.365 |
| P(message logged, given a = 1)  [future] | P-CTC | 0.000 | 0.095 | 0.010 | 0.117 |
| P(message logged, given a = 0)  [future] | P-CTC | 0.500 | 0.492 | 0.012 | 0.489 |
| P(a = 1)  [past] | past-preserving | 0.500 | 0.507 | 0.006 | 0.505 |
| P(message logged, given a = 1)  [future] | past-preserving | 0.000 | 0.095 | 0.010 | 0.117 |
| P(message logged, given a = 0)  [future] | past-preserving | 0.500 | 0.492 | 0.012 | 0.489 |

readout error per clbit, P(1|0): 0.009, 0.013, 0.009, 0.007, 0.006;  P(0|1): 0.010, 0.016, 0.007, 0.008, 0.009

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'a': 0} | 0.454 | 0.500 |
| {'a': 1} | 0.252 | 0.250 |

## One-way control: a controls the loop, the loop never acts on a

| quantity | rule | exact | measured | std | raw |
|---|---|---|---|---|---|
| P(a = 1)  [past; equals the record held by a partner] | no loop | 0.500 | 0.510 | 0.012 | 0.500 |
| P(a = 1)  [past; equals the record held by a partner] | P-CTC | 0.000 | 0.045 | 0.010 | 0.077 |
| P(a = 1)  [past; equals the record held by a partner] | past-preserving | 0.500 | 0.505 | 0.013 | 0.493 |

readout error per clbit, P(1|0): 0.017, 0.370, 0.020, 0.005;  P(0|1): 0.019, 0.421, 0.018, 0.007

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'a': 0} | 0.944 | 1.000 |
| {'a': 1} | 0.050 | 0.000 |

## Criteria (applied after the fact: this run was not preregistered)

| criterion | quantity | value | result |
|---|---|---|---|
| C1 | grandfather: P(jam = 1)  [past] | PP - P-CTC = -0.716 (exact -0.800), z = -83.7 | PASS |
| C1 | refusal: P(a = 1)  [past] | PP - P-CTC = +0.144 (exact +0.167), z = 20.1 | PASS |
| C1 | one_way: P(a = 1)  [past; equals the record held by a partner] | PP - P-CTC = +0.459 (exact +0.500), z = 30.1 | PASS |
| C2 | grandfather: P(jam = 1)  [past] | measured - exact = +0.013 | PASS |
| C2 | refusal: P(a = 1)  [past] | measured - exact = +0.007 | PASS |
| C2 | refusal: P(message logged, given a = 1)  [future] | measured - exact = +0.095 | FAIL |
| C2 | refusal: P(message logged, given a = 0)  [future] | measured - exact = -0.008 | PASS |
| C2 | one_way: P(a = 1)  [past; equals the record held by a partner] | measured - exact = +0.005 | PASS |

**7 of 8 checks pass.**

