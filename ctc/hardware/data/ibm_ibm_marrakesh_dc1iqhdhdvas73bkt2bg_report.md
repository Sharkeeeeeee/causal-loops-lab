backend: ibm_marrakesh   shots per experiment: 8192   job: dc1iqhdhdvas73bkt2bg
error suppression: none
measured = readout-corrected (raw = uncorrected); std from a bootstrap over shots

## Grandfather paradox: the gun jams with prior 0.2

| quantity | rule | exact | measured | std |
|---|---|---|---|---|
| P(jam = 1)  [past] | no loop | 0.200 | 0.198 | 0.004 |
| P(jam = 1)  [past] | P-CTC | 1.000 | 0.880 | 0.007 |
| P(jam = 1)  [past] | past-preserving | 0.200 | 0.204 | 0.004 |

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'jam': 0} | 0.034 | 0.000 |
| {'jam': 1} | 0.918 | 1.000 |

## Refusal: if a = 1 the sender never sends a message it received

| quantity | rule | exact | measured | std |
|---|---|---|---|---|
| P(a = 1)  [past] | no loop | 0.500 | 0.476 | 0.006 |
| P(message logged, given a = 1)  [future] | no loop | 0.500 | 0.485 | 0.008 |
| P(message logged, given a = 0)  [future] | no loop | 0.500 | 0.470 | 0.007 |
| P(a = 1)  [past] | P-CTC | 0.333 | 0.352 | 0.008 |
| P(message logged, given a = 1)  [future] | P-CTC | 0.000 | 0.112 | 0.010 |
| P(message logged, given a = 0)  [future] | P-CTC | 0.500 | 0.459 | 0.012 |
| P(a = 1)  [past] | past-preserving | 0.500 | 0.476 | 0.006 |
| P(message logged, given a = 1)  [future] | past-preserving | 0.000 | 0.112 | 0.010 |
| P(message logged, given a = 0)  [future] | past-preserving | 0.500 | 0.459 | 0.012 |

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'a': 0} | 0.451 | 0.500 |
| {'a': 1} | 0.270 | 0.250 |

## One-way control: a controls the loop, the loop never acts on a

| quantity | rule | exact | measured | std |
|---|---|---|---|---|
| P(a = 1)  [past; equals the record held by a partner] | no loop | 0.500 | 0.485 | 0.006 |
| P(a = 1)  [past; equals the record held by a partner] | P-CTC | 0.000 | 0.061 | 0.006 |
| P(a = 1)  [past; equals the record held by a partner] | past-preserving | 0.500 | 0.478 | 0.006 |

| recorded world | Bell test passed (measured) | exact |
|---|---|---|
| {'a': 0} | 0.383 | 1.000 |
| {'a': 1} | 0.028 | 0.000 |

## Criteria (applied after the fact: this run was not preregistered)

| criterion | quantity | value | result |
|---|---|---|---|
| C1 | grandfather: P(jam = 1)  [past] | PP - P-CTC = -0.676 (exact -0.800), z = -96.0 | PASS |
| C1 | refusal: P(a = 1)  [past] | PP - P-CTC = +0.124 (exact +0.167), z = 17.7 | PASS |
| C1 | one_way: P(a = 1)  [past; equals the record held by a partner] | PP - P-CTC = +0.417 (exact +0.500), z = 64.6 | PASS |
| C2 | grandfather: P(jam = 1)  [past] | measured - exact = +0.004 | PASS |
| C2 | refusal: P(a = 1)  [past] | measured - exact = -0.024 | PASS |
| C2 | refusal: P(message logged, given a = 1)  [future] | measured - exact = +0.112 | FAIL |
| C2 | refusal: P(message logged, given a = 0)  [future] | measured - exact = -0.041 | PASS |
| C2 | one_way: P(a = 1)  [past; equals the record held by a partner] | measured - exact = -0.022 | PASS |

**7 of 8 checks pass.**

