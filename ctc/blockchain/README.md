# Loop lottery: testing on the Bitcoin blockchain whether self-consistency can pull answers back from the future

Created 2026-11-23 with AI assistance (Claude). No external review. Protocol version `cll-loop-lottery-v2` (v1 was revised after a loophole review; see the last sections). Before a real run, `preregister.py` generates `PREREGISTRATION.md` and `params.json` with the protocol and criteria.

**Status: designed and tested offline; not yet run.**

## In one sentence

Lock guesses into the blockchain first, with answers determined by a pre-specified block that has not yet been mined; once the answers exist, "send them back to the past". If self-consistency really could force answers, the questions that are sent back would be guessed correctly. **With 32-bit answers, a single correct guess has a chance probability of about 7×10⁻⁹, beyond 5σ.**

## Why a blockchain

| Requirement | How |
|---|---|
| The guesses were really fixed before the answers | write the commitment into Bitcoin block B_c with [OpenTimestamps](https://opentimestamps.org); free, no wallet or cryptocurrency needed |
| Only **one** set of guesses (no hiding many and picking afterwards) | the commitment is published in plain text at a pre-specified URL and archived by the Internet Archive; only the **first** capture counts |
| The answers do not exist and cannot be predicted at guessing time | answers come from the hash of the block at pre-specified height H; the commitment must be in block H−6 or earlier |
| The rules were not changed afterwards | the SHA-256 of the preregistration (including H and the URL) is part of the commitment and goes on-chain with it |

## Procedure

```text
 0. preregister.py     fix the answer block H (about now + 48 blocks, 8 hours ahead) and the witness URL
 1. commit.py          an IBM quantum computer produces 64 guesses of 32 bits → commitment → OpenTimestamps
 2. push + witness.py  push the commitment file to GitHub and ask the Internet Archive to capture it
                       (at least two hours before block H)
        ⋯ wait: the commitment enters block B_c (≤ H−6), blocks H and H+1 are mined, then 6 confirmations ⋯
 3. send.py            the future sender: compute the answers from block H, use block H+1 to pick about half
                       of the questions, and "send back" their answers on-chain
 4. reveal.py          only after sending, publish the guesses and the salt
 5. verify.py          anyone can rerun every check from scratch and apply the preregistered criteria
```

- The sender never sees the guesses; the guesser cannot see the answers (the answer block does not exist yet).
- **Control group:** the half of the questions that are not sent back stay at chance under every hypothesis. "Sent-back questions hit, others do not" is the signature of a loop effect. A bias in the quantum random numbers would affect both groups, and since the answers are uniform, no bias in the guesses changes the hit probability (tested).

## How the computer checks (verify.py)

1. `params.json` agrees with `PREREGISTRATION.md`, and the preregistration's SHA-256 equals the one recorded in the commitment.
2. The published guesses and salt hash to the on-chain commitment.
3. The OpenTimestamps proof leads from the commitment file to the merkle root of block B_c, and B_c ≤ H−6.
4. The first Internet Archive capture of the witness URL contains the same commitment and is earlier than "timestamp of block H − 2 hours". Bitcoin allows a block timestamp to run at most 2 hours ahead of real time, so this guarantees the capture happened before block H was mined.
5. Block headers from B_c to H+1 are fetched from two independent sources, mempool.space and blockstream.info, and compared byte by byte; each block's double SHA-256, proof of work, modern difficulty floor and linkage to the previous block are recomputed.
6. The answers and the sent-back list are recomputed from the block hashes, and `loop_messages.json` must match exactly.

If any check fails, the run is **void**: neither positive nor negative.

## How many hits rule out chance

With about 32 questions sent back:

| Bits per answer | Chance hit probability per question | Probability of at least one hit | Hits needed for 5σ |
|---|---|---|---|
| 8 | 0.0039 | 0.12 | 5 |
| 16 | 1.5×10⁻⁵ | 4.9×10⁻⁴ | 2 |
| 24 | 6.0×10⁻⁸ | 1.9×10⁻⁶ | 2 |
| **32 (this experiment)** | **2.3×10⁻¹⁰** | **7.5×10⁻⁹** | **1** |
| 64 | 5.4×10⁻²⁰ | 1.7×10⁻¹⁸ | 1 |

- **Primary criterion:** X = number of exact hits among the sent-back questions; reject "pure chance" if P(Binomial(≈32, 2⁻³²) ≥ X) < 2.87×10⁻⁷ (5σ).
- **Secondary criterion:** bit hits among the sent-back questions, against Binomial(32 × number of questions, 1/2).
- **Control:** questions not sent back must stay at chance; hits there mean a bug or tampering.

## Predictions of each hypothesis

| Hypothesis | Sent-back questions |
|---|---|
| No retrocausality (standard physics) | chance level |
| Past-preserving selection (this project's H2′) | chance level: the guesses are recorded on the blockchain before the answers exist, and the recorded past does not change |
| A consistency rule that reweights the past (P-CTC-like), and the loop really exists | all hit; those not sent back stay at chance |

**Honest note:** nothing in this setup is really sent to the past; "sending back" just means publishing the answer after it exists. The experiment tests the strongest claim: "intending to form a loop is enough for self-consistency to pull the answers back". Standard physics and this project's own H2′ both predict **no hits**. A hit would contradict the project's own theorems; by the preregistered rules, the first steps would be a bug hunt and independent replication.

## Loophole review (2026-11-23)

The v1 design was attacked step by step, and the problems below were found. Each has an automated test confirming that verify.py catches the attack (`ctc/tests/test_blockchain.py`, 22 tests).

| # | Loophole | Severity | Problem in v1 | Fix in v2 |
|---|---|---|---|---|
| 1 | **A merkle tree hiding many guess sets** | fatal | an OpenTimestamps proof path can hide a merkle tree of one's own. One stamp can cover 2³⁰ guess sets, and the winning one is revealed afterwards; the probability of faking a hit exceeds 99% | the commitment is published in plain text at a pre-specified URL; only the **first** Internet Archive capture counts, and it must precede the answer block |
| 2 | **Re-stamping to change the answer** | high | the answer block was "B_c + 6". Stamping the same commitment several times gives different B_c and different answers to choose from | answer height H is fixed in the preregistration; the commitment must be in H−6 or earlier, otherwise the run is void |
| 3 | Block reorganization | medium | sending as soon as the answer block appears; a later reorganization would change the answer | wait for 6 confirmations before sending |
| 4 | Difficulty floor too loose | low | with a target floor of 2¹⁹⁰, a funded attacker might mine fake headers (still having to fool two explorers) | tightened to 2¹⁸² (currently about 2¹⁷⁷, a 32× margin) |
| 5 | The verifier is self-written | low | a malicious repo could ship a lying verifier | the protocol is short enough to reimplement independently; stated in the preregistration |

Confirmed **not** to be loopholes: choosing among quantum random numbers when guessing (the answers do not exist yet, so choosing does not help); biased quantum random numbers (the answers are uniform, so the hit probability does not change); miners manipulating the answer block (the guesses are hidden by the salt, so there is no direction to push); leaking the guesses early (the answer block is fixed, so a leak cannot change the answers).

**What remains and cannot be removed by protocol:** one person could run many independent public experiments (different repos, URLs and preregistrations) and advertise only the luckiest. Each is public and timestamped, so this is detectable, but the real defense is independent replication.

## How to run

Needs `opentimestamps-client` (stamping); quantum guesses also need `qiskit-ibm-runtime` and your IBM Quantum account.

```text
python -B ctc/tests/test_blockchain.py                    # offline tests (22)
python -B ctc/blockchain/preregister.py --answer-height H # H ≈ current block height + 48
python -B ctc/blockchain/commit.py                        # guess and stamp (only once)
git add ctc/blockchain && git commit && git push          # make the commitment file appear at the witness URL
python -B ctc/blockchain/witness.py                       # Internet Archive capture
python -B ctc/blockchain/send.py                          # about 9 hours later: send back the answers
python -B ctc/blockchain/reveal.py                        # publish the guesses
python -B ctc/blockchain/verify.py                        # verify and apply the criteria
```

`private/reveal.json` is secret until the reveal and is excluded by `.gitignore`; do not commit or share it before revealing. The default witness URL is `ctc/blockchain/public/commitment.txt` on this repo's `main` branch, so the commitment file must be pushed to `main`.
