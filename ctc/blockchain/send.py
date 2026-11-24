"""SPDX-License-Identifier: MIT. Step 3: the future sender sends the answers back.

Usage (from the repository root):  python -B ctc/blockchain/send.py

Completes the commitment's timestamp, checks that it landed early enough, waits until the
preregistered send block has enough confirmations, derives the answers and send flags, and
publishes the answers of the sent trials in public/loop_messages.json, itself timestamped on
Bitcoin. The sender never sees the guesses.
"""
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from chain import fetch_header, save_headers, tip_height, verified_range  # noqa: E402
from ots_support import first_verified_block, stamp, upgrade  # noqa: E402
import preregister  # noqa: E402
from protocol import PROTOCOL, answers, guess_hex, send_flags  # noqa: E402

PUBLIC = HERE / 'public'


def loop_messages(b_c, headers, params):
    answer_hash = headers[params['answer_height']][0]
    send_hash = headers[params['send_height']][0]
    a, s = answers(answer_hash), send_flags(send_hash)
    return dict(protocol=PROTOCOL, commitment_block=b_c,
                answer_block=dict(height=params['answer_height'], hash=answer_hash),
                send_block=dict(height=params['send_height'], hash=send_hash),
                messages={str(i): guess_hex(a[i]) for i in range(len(a)) if s[i]})


def main():
    _, params = preregister.check()
    if params is None:
        sys.exit('PREREGISTRATION.md / params.json missing or out of date')
    commit_file = PUBLIC / 'commitment.txt'
    upgrade(str(commit_file) + '.ots')
    b_c = first_verified_block(commit_file, str(commit_file) + '.ots', fetch_header)
    if b_c is None:
        sys.exit('the commitment is not in a Bitcoin block yet; try again later')
    if b_c > params['answer_height'] - params['min_lead']:
        sys.exit(f'VOID: commitment landed in block {b_c}, later than {params["answer_height"] - params["min_lead"]}')
    tip = tip_height()
    ready = params['send_height'] + params['send_confirmations']
    print(f'commitment is in block {b_c}; tip is {tip}')
    if tip < ready:
        sys.exit(f'waiting for block {ready} ({ready - tip} more)')
    out = PUBLIC / 'loop_messages.json'
    if out.exists():
        sys.exit('loop_messages.json already exists')
    headers = verified_range(b_c, params['send_height'])
    save_headers(headers, PUBLIC / 'headers.json')
    msg = loop_messages(b_c, headers, params)
    out.write_text(json.dumps(msg, indent=1, sort_keys=True), encoding='utf-8', newline='\n')
    stamp(out)
    print(f'sent {len(msg["messages"])} answers back; run reveal.py, then verify.py')


if __name__ == '__main__':
    main()
