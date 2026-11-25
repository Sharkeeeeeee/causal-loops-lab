"""SPDX-License-Identifier: MIT. Follow-up steps after publishing the invitation, safe to run repeatedly.

    python -B ctc/invitation/followup.py status    what is done and what is next (JSON)
    python -B ctc/invitation/followup.py upgrade   complete the OpenTimestamps proof; once it is in a
                                                   block, record P in STATUS.json
    python -B ctc/invitation/followup.py scan      once block P+155 exists, scan the window P..P+144
                                                   and record the verdict (about 30 minutes)

Every step checks first that INVITATION.md still has its stamped SHA-256, and records its
results in ctc/invitation/STATUS.json. Nothing here commits, pushes or contacts the archive;
that is left to whoever runs it.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'blockchain'))
import chain  # noqa: E402
import ots_support  # noqa: E402
import reply  # noqa: E402

INVITATION = HERE / 'INVITATION.md'
PROOF = HERE / 'INVITATION.md.ots'
STATUS = HERE / 'STATUS.json'
WINDOW_RESULT = HERE / 'window_result.json'
STAMPED_SHA256 = '3394e6f0cdcf6fde53694bfadf11f044c0c797ee454e9dc91dd54f276e47ce82'


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def load():
    return json.loads(STATUS.read_text(encoding='utf-8')) if STATUS.exists() else {}


def save(status):
    STATUS.write_text(json.dumps(status, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')


def check_invitation():
    digest = hashlib.sha256(INVITATION.read_bytes()).hexdigest()
    if digest != STAMPED_SHA256:
        raise SystemExit(f'STOP: INVITATION.md changed (sha256 {digest}, stamped {STAMPED_SHA256})')


def closes_at(p):
    return p + reply.WINDOW + reply.MIN_LEAD + reply.CONFIRMATIONS - 1


def status():
    check_invitation()
    s = load()
    tip = chain.tip_height()
    if 'P' not in s:
        nxt = 'upgrade'
    elif 'window_verdict' not in s:
        nxt = 'scan' if tip >= closes_at(s['P']) else f'wait until block {closes_at(s["P"])} (tip {tip})'
    else:
        nxt = 'done'
    return dict(s, tip=tip, next=nxt)


def upgrade():
    check_invitation()
    s = load()
    if 'P' in s:
        return dict(s, note='P already recorded')
    complete = ots_support.upgrade(PROOF)
    if not complete:
        return {'note': 'the stamp is not in a block yet; try again later', 'checked_at': now()}
    p = ots_support.first_verified_block(INVITATION, PROOF, chain.fetch_header)
    if p is None:
        raise SystemExit('STOP: the proof names a block, but no verified header carries its merkle root')
    block_hash, header = chain.fetch_header(p)
    s.update(P=p, P_block_hash=block_hash, P_block_time=datetime.fromtimestamp(chain.timestamp(header), timezone.utc)
             .isoformat(), invitation_sha256=STAMPED_SHA256, P_recorded_at=now(),
             window=f'anchored in {p}..{p + reply.WINDOW}, naming a block no later than {p + reply.WINDOW + reply.MIN_LEAD}',
             window_closes_at=closes_at(p))
    save(s)
    return s


def scan():
    check_invitation()
    s = load()
    if 'P' not in s:
        raise SystemExit('P is not known yet: run upgrade first')
    if 'window_verdict' in s:
        return dict(s, note='window already judged')
    p, tip = s['P'], chain.tip_height()
    if tip < closes_at(p):
        return {'note': f'too early: the window closes at block {closes_at(p)}, tip is {tip}'}
    cache = {}

    def fetch(h):
        if h not in cache:
            cache[h] = chain.fetch_header(h)
        return cache[h]
    result = reply.scan_range(p, p + reply.WINDOW, tip, fetch, descent=True, invitation_height=p,
                              index_upto=p + reply.WINDOW + reply.MIN_LEAD)
    summary = reply.window_summary(result, p, tip)
    result['window_summary'] = summary
    WINDOW_RESULT.write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8', newline='\n')
    s.update(window_verdict=summary['verdict'], window_replies=summary['replies_anchored_in_window'],
             window_scanned_at=now(), window_scanned_tip=tip)
    save(s)
    return s


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    out = {'status': status, 'upgrade': upgrade, 'scan': scan}[cmd]()
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
