"""SPDX-License-Identifier: MIT. Fix the loop-lottery protocol and decision rules before the run.

Writes ctc/blockchain/params.json and ctc/blockchain/PREREGISTRATION.md. The SHA-256 of
PREREGISTRATION.md goes inside the commitment, so the rules (including the answer block height
and the witness URL) are bound to the guesses on the Bitcoin blockchain.

Usage (from the repository root):
  python -B ctc/blockchain/preregister.py --answer-height H [--witness-url URL]
Pick H about 48 blocks (8 hours) above the current tip, right before running commit.py.
"""
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from protocol import (ANSWER_TAG, FIVE_SIGMA, K_BITS, N_TRIALS, PROTOCOL, SEND_TAG, chance_table,  # noqa: E402
                      check_params, make_params, sha256_hex)

PATH = HERE / 'PREREGISTRATION.md'
PARAMS = HERE / 'params.json'
DEFAULT_URL = 'https://raw.githubusercontent.com/Sharkeeeeeee/causal-loops-lab/main/ctc/blockchain/public/commitment.txt'


def text(p):
    rows = '\n'.join(f'| {r["k"]} | {r["per_trial"]:.3g} | {r["at_least_one"]:.3g} | {r["hits_needed"]} |'
                     for r in chance_table())
    return f"""# Preregistration: loop lottery ({PROTOCOL})

Fixed before any guess is drawn. The SHA-256 of this file is part of the commitment that is
timestamped on Bitcoin, so these rules cannot be changed after the answers are known.

## Parameters

| parameter | value |
|---|---|
| trials | {p['n_trials']} |
| bits per guess | {p['k_bits']} |
| answer block height | **{p['answer_height']}** |
| send block height | **{p['send_height']}** |
| commitment must be in a block at or below | {p['answer_height'] - p['min_lead']} |
| sending waits until the send block has confirmations | {p['send_confirmations']} |
| witness URL (first Internet Archive capture counts) | {p['witness_url']} |
| witness capture must be earlier than the answer block's timestamp minus | {p['witness_margin_seconds']} s |

## Question

If a message carrying the answer is sent back in time, does self-consistency force the earlier
guess to equal the answer?

## Protocol

1. **Guesses.** {N_TRIALS} guesses of {K_BITS} bits each, from quantum measurements on IBM hardware
   (32 qubits in |+>, {N_TRIALS} shots; the operating-system generator only if the hardware is
   unavailable). A 256-bit random salt hides them.
2. **Commitment.** C = SHA-256 of the canonical JSON of (protocol, this file's SHA-256, guesses, salt,
   guess source). C is written to `public/commitment.txt`, which is timestamped with OpenTimestamps.
   B_c is the lowest Bitcoin block whose verified header contains the timestamp. B_c must be at or
   below block {p['answer_height'] - p['min_lead']}, otherwise the run is void.
3. **Witness.** `commitment.txt` is pushed to the repository and captured by the Internet Archive at
   the witness URL above. The **first** successful capture of that URL defines the commitment: it must
   contain C, and it must be earlier than the timestamp of block {p['answer_height']} minus
   {p['witness_margin_seconds']} s (Bitcoin block timestamps can run up to 2 hours ahead of real time).
   Without this, one OpenTimestamps proof could hide a merkle tree of billions of guess sets and the
   best one could be revealed afterwards.
4. **Answers.** a_i = first {K_BITS} bits of SHA-256("{ANSWER_TAG}|<hash of block {p['answer_height']}>|i").
   The height is fixed here, so stamping the same commitment again cannot re-roll the answers.
5. **Sending back.** Trial i is sent iff the first bit of SHA-256("{SEND_TAG}|<hash of block {p['send_height']}>|i")
   is 1. After block {p['send_height']} has {p['send_confirmations']} confirmations, `send.py` publishes a_i for
   the sent trials in `public/loop_messages.json` and timestamps it. This is the message to the past;
   a self-consistent loop requires guess = answer.
6. **Reveal and check.** Guesses and salt are published; `verify.py` recomputes everything from
   Bitcoin headers fetched from two explorers and checked for proof of work and linkage.

## Predictions

| hypothesis | exact matches among sent trials |
|---|---|
| no retrocausality (standard physics) | chance: about {N_TRIALS // 2} x 2^-{K_BITS} = {N_TRIALS / 2 * 2.0 ** -K_BITS:.1e} |
| past-preserving selection (this project's H2') | chance: the guesses are recorded on Bitcoin before the answer exists, and a recorded past keeps its probabilities |
| a working self-consistency rule that reweights the past (P-CTC-like) | every sent trial matches; unsent trials at chance |

## Decision rules

- **Primary:** exact matches X among sent trials. Reject "chance" if P(Binomial(n_sent, 2^-{K_BITS}) >= X)
  < {FIVE_SIGMA:.3g} (5 sigma). With about {N_TRIALS // 2} sent trials, **a single exact match passes**.
- **Secondary:** matching bits among sent trials vs Binomial({K_BITS} n_sent, 1/2), same threshold.
- **Control:** unsent trials must stay at chance (both tests above their thresholds). A hit there points
  to a bug or tampering, not to a loop.
- **Void run:** if any integrity check below fails, there is no result, positive or negative.
- No other test decides the outcome. Any other analysis is labelled exploratory.

## How many matches rule out coincidence

P(at least one exact match by pure chance) with {N_TRIALS // 2} sent trials, and matches needed for 5 sigma:

| bits per answer | chance per trial | P(>= 1 match) | matches needed |
|---|---|---|---|
{rows}

## Integrity checks (all automatic in verify.py)

1. This file's SHA-256 equals the one inside the revealed commitment, and params.json matches this file.
2. SHA-256(canonical reveal) equals the committed value in `public/commitment.txt`.
3. The OpenTimestamps proof leads from `commitment.txt` to the merkle root of block B_c, and
   B_c <= {p['answer_height'] - p['min_lead']}.
4. The first Internet Archive capture of the witness URL contains the same commitment and predates
   block {p['answer_height']} by the margin above.
5. Headers B_c ... {p['send_height']} agree between two explorers, hash correctly, meet their proof-of-work
   targets, carry modern difficulty, and each points to the previous one.
6. Answers and send flags are rederived; `loop_messages.json` must equal the derived answers.

## Known limits, stated in advance

- Nothing in this setup sends information to the past. "Sending" is publishing the answer after it
  exists. The experiment tests whether intending a loop, plus self-consistency, can pull an answer
  back; every established theory, and this project's own H2', predicts that it cannot.
- One experimenter can still run several separate public experiments (separate repositories, URLs
  and preregistrations) and promote the luckiest. Each one is public and timestamped, so this is
  visible, but independent replication is the real defence.
- The verifier is this project's own code. The protocol is short enough to reimplement; an independent
  reimplementation should reach the same numbers.
- A positive result would contradict this project's own theorems (H2' and no-signalling), so it would
  call for an error hunt and replication before any interpretation.
"""


def load_params():
    params = json.loads(PARAMS.read_text(encoding='utf-8'))
    check_params(params)
    return params


def check():
    """(SHA-256 of PREREGISTRATION.md, params) if both files exist and agree, else (None, None)."""
    if not (PATH.exists() and PARAMS.exists()):
        return None, None
    params = load_params()
    content = PATH.read_text(encoding='utf-8')
    return (sha256_hex(content.encode('utf-8')), params) if content == text(params) else (None, None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--answer-height', type=int, required=True)
    parser.add_argument('--witness-url', default=DEFAULT_URL)
    args = parser.parse_args()
    params = make_params(args.answer_height, args.witness_url)
    PARAMS.write_text(json.dumps(params, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
    content = text(params)
    PATH.write_text(content, encoding='utf-8', newline='\n')
    print(content)
    print(f'SHA-256 {sha256_hex(content.encode("utf-8"))}  ({PATH})')


if __name__ == '__main__':
    main()
