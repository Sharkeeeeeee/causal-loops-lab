"""SPDX-License-Identifier: MIT. A full mock run of the invitation on a synthetic chain, with attackers.

The chain uses real double SHA-256 and real block, transaction and merkle formats, but trivial
proof of work (regtest difficulty) and heights below chain.RECENT_HEIGHT, so it can be mined
in a moment. The invitation is anchored at block P; blocks are mined past the preferred window;
then every attack below is tried and judged by the same code that judges real replies.

What cannot be simulated is a genuine reply: a block that contains the hash of one of its own
descendants. Building one is exactly the forgery the protocol rules out (a preimage or a fixed
point of double SHA-256). The real-header tests in ctc/tests/test_invitation.py cover the
acceptance path instead, by supplying the anchor height directly.

Run:  python -B ctc/invitation/simulate.py
"""
import hashlib
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'blockchain'))
import chain  # noqa: E402
import reply  # noqa: E402
from reply import MIN_LEAD, WINDOW, CONFIRMATIONS  # noqa: E402

REGTEST_BITS = 0x207fffff
START = 1000          # first height; below chain.RECENT_HEIGHT, so no modern difficulty floor


def tx(outputs=(), script_sig=b'\x00', witness=None, tag=b''):
    """A minimal transaction; `tag` makes otherwise equal transactions distinct."""
    body = b'\x01' + hashlib.sha256(tag).digest() + b'\x00\x00\x00\x00'
    body += bytes([len(script_sig)]) + script_sig + b'\xff\xff\xff\xff'
    body += bytes([len(outputs)]) + b''.join(b'\x00' * 8 + bytes([len(s)]) + s for s in outputs)
    if witness is None:
        return b'\x02\x00\x00\x00' + body + b'\x00\x00\x00\x00'
    return b'\x02\x00\x00\x00\x00\x01' + body + b'\x01' + bytes([len(witness)]) + witness + b'\x00\x00\x00\x00'


def header(prev_hash, merkle, nonce_seed=0):
    prev = bytes.fromhex(prev_hash)[::-1]
    for nonce in range(nonce_seed, nonce_seed + 10000):
        h = (b'\x01\x00\x00\x00' + prev + merkle + b'\x00\x00\x00\x00'
             + REGTEST_BITS.to_bytes(4, 'little') + nonce.to_bytes(4, 'little'))
        if int(chain.header_hash(h), 16) <= chain.target(h):
            return h
    raise RuntimeError('no nonce')


class Chain:
    """Best chain plus known side blocks, served like the two explorers would."""

    def __init__(self, seed=0):
        self.rng = random.Random(seed)
        self.best = {}          # height -> (hash, header, raw block)
        self.side = {}          # hash -> height, for blocks that left the best chain
        self.mine(START, '00' * 32)

    def make_block(self, height, prev_hash, extra=()):
        coinbase = tx([b'\x51'], script_sig=b'\x03' + height.to_bytes(3, 'little') + bytes([self.rng.randrange(256)]),
                      tag=b'cb%d' % height)
        txs = [coinbase] + list(extra)
        txids = [reply.parse_tx(t)['txid'] for t in txs]
        h = header(prev_hash, reply.merkle_root(txids), self.rng.randrange(1 << 20))
        raw = h + bytes([len(txs)]) + b''.join(txs)
        return chain.header_hash(h), h, raw

    def mine(self, height, prev_hash=None, extra=()):
        prev_hash = prev_hash or self.best[height - 1][0]
        self.best[height] = self.make_block(height, prev_hash, extra)
        return self.best[height][0]

    def extend(self, upto):
        for h in range(max(self.best) + 1, upto + 1):
            self.mine(h)

    def reorganize(self, fork_height, upto, extra_at_fork=()):
        """Replace the best chain from fork_height on; the old blocks become side blocks."""
        for h in range(fork_height, max(self.best) + 1):
            self.side[self.best.pop(h)[0]] = h
        self.mine(fork_height, self.best[fork_height - 1][0], extra_at_fork)
        self.extend(upto)

    @property
    def tip(self):
        return max(self.best)

    def fetch(self, height):
        if height not in self.best:
            raise LookupError(height)
        return self.best[height][0], self.best[height][1]

    def fetch_raw(self, height):
        return self.best[height][2]

    def locate(self, block_hash):
        for h, (b, _, _) in self.best.items():
            if b == block_hash:
                return h
        if block_hash in self.side:
            raise reply.ReplyRejected(f'block {block_hash} is not in the best chain')
        return None


def reply_output(block_hash):
    return reply.op_return_script(reply.payload(block_hash))


def run(seed=0, n_guesses=300):
    """Mock run. Returns {scenario: list of outcomes} plus the window summary."""
    c = Chain(seed)
    rng = random.Random(seed + 1)
    c.extend(START + 20)
    P = START + 21
    c.mine(P)                                 # block P: the invitation's own stamp
    out = {}
    guesses_at = {}                           # 1. random guesses, spread over the window below
    c.extend(P + 9)
    # 2. copy-cat: name block P+10 from a block mined after it
    c.mine(P + 10)
    copy_target = c.best[P + 10][0]
    extras = {P + 20: [tx([reply_output(copy_target)], tag=b'copy')],
              # 3. reversed byte order of an earlier block
              P + 21: [tx([reply_output(bytes.fromhex(c.best[P + 5][0])[::-1].hex())], tag=b'rev')],
              # 4. payload in a witness only (not covered by the txid): must not be found
              P + 22: [tx([b'\x51'], witness=reply.payload(copy_target), tag=b'wit')],
              # 5. payload in an ordinary input's scriptSig (covered by the txid): must be found
              P + 23: [tx([b'\x51'], script_sig=b'\x25' + reply.payload(copy_target), tag=b'sig')],
              # 6b. three transactions (odd), for the merkle-mutation check below
              P + 25: [tx([reply_output('%064x' % rng.getrandbits(256))], tag=b'mut1'), tx([b'\x51'], tag=b'mut2')]}
    for h in range(P + 11, P + 60):
        extra = list(extras.get(h, []))
        if h % 3 == 0:                       # spread the random guesses over the window
            for k in range(n_guesses // 16):
                extra.append(tx([reply_output('%064x' % rng.getrandbits(256))], tag=b'g%d.%d' % (h, k)))
                guesses_at.setdefault(h, 0)
                guesses_at[h] += 1
        c.mine(h, extra=extra)

    # 6. history rewrite: after seeing block P+50, rebuild from P+31 with a reply naming it
    seen = c.best[P + 50][0]
    c.reorganize(P + 31, P + 60, extra_at_fork=[tx([reply_output(seen)], tag=b'reorg')])
    c.extend(P + WINDOW + MIN_LEAD + CONFIRMATIONS + 5)

    scan = reply.scan_range(P, P + WINDOW, c.tip, c.fetch, c.fetch_raw, c.locate, descent=True,
                            invitation_height=P)
    reversed_hash = bytes.fromhex(c.best[P + 5][0])[::-1].hex()
    for name in ('random guesses', 'copy-cat (names an earlier block)', 'reversed byte order of an earlier block',
                 'payload hidden in a witness', 'payload in an input scriptSig',
                 'history rewritten to name a block already seen'):
        out[name] = []
    for r in scan['replies']:
        if r['claimed'] == copy_target:
            name = 'copy-cat (names an earlier block)' if r['block'] == P + 20 else \
                'payload in an input scriptSig' if r['block'] == P + 23 else 'payload hidden in a witness'
        elif r['claimed'] == reversed_hash:
            name = 'reversed byte order of an earlier block'
        elif r['claimed'] == seen:
            name = 'history rewritten to name a block already seen'
        else:
            name = 'random guesses'
        out[name].append(r)

    # 6b. a block body with its last transactions duplicated (CVE-2012-2459): same merkle root
    h = P + 25
    hdr, txs_ = reply.parse_block(c.best[h][2])
    raw_txs = c.best[h][2][81:]
    assert len(txs_) == 3 and not txs_[-1]['segwit']
    mutated = hdr + bytes([4]) + raw_txs + raw_txs[-len(txs_[-1]['stripped']):]
    real, dup = reply.scan_block(c.best[h][2], h, c.fetch), reply.scan_block(mutated, h, c.fetch)
    out['duplicated transactions (merkle mutation)'] = [
        {'outcome': 'nothing hidden' if set(map(str, real)) == set(map(str, dup)) else 'DIFFERENT',
         'note': f'real body {len(real)} payload transactions, mutated body {len(dup)}, same merkle root'}]

    # 7. lying explorers: a reply names a private block, and the explorers pretend it is in the best chain
    anchor = P + 40
    private_prev = c.best[P + 45][0]
    fake_hash, fake_header, _ = c.make_block(P + 46, private_prev)   # a private block, mined after the fact

    def lying_fetch(h):
        return (fake_hash, fake_header) if h == P + 52 else c.fetch(h)

    def lying_locate(b):
        return P + 52 if b == fake_hash else c.locate(b)
    answer_rejects = []
    try:
        ans = reply.verified_answer(fake_hash, None, lying_fetch, lying_locate)
        reply.judge(fake_hash, ans, anchor, c.tip)
        reply.check_descent(anchor, ans, lying_fetch)
        answer_rejects.append({'valid': True})
    except reply.ReplyRejected as ex:
        answer_rejects.append({'rejected': str(ex)})
    out['explorers serve a private block as a descendant'] = answer_rejects

    # 8. a tampered block body served for the scan (a transaction removed)
    h = P + 20
    raw = c.best[h][2]
    hdr, txs = reply.parse_block(raw)
    body = b'\x01' + raw[81:81 + len(txs[0]['stripped'])]   # keep only the coinbase (a legacy transaction)
    try:
        reply.scan_block(hdr + body, h, c.fetch)
        out['tampered block served to the scanner'] = [{'valid': True}]
    except ValueError as ex:
        out['tampered block served to the scanner'] = [{'error': str(ex)}]

    out['_window'] = reply.window_summary(scan, P, c.tip)

    # 9. the same window judged from a local index of headers, with no explorer lookups at all
    def no_network(_):
        raise AssertionError('explorer lookup in index mode')
    indexed = reply.scan_range(P, P + WINDOW, c.tip, c.fetch, c.fetch_raw, no_network, descent=True,
                               invitation_height=P, index_upto=P + WINDOW + MIN_LEAD)
    out['_window_indexed'] = reply.window_summary(indexed, P, c.tip)
    # 10. judged too early: the window must still be open
    out['_window_early'] = reply.window_summary(scan, P, P + WINDOW + MIN_LEAD)
    out['_guesses'] = sum(guesses_at.values())
    out['_P'] = P
    return out


def outcome(r):
    if 'outcome' in r:
        return r['outcome']
    return 'valid' if r.get('valid') else 'rejected' if 'rejected' in r else 'error' if 'error' in r else '?'


def main():
    res = run()
    for name, rs in res.items():
        if name.startswith('_'):
            continue
        counts = {}
        for r in rs:
            counts[outcome(r)] = counts.get(outcome(r), 0) + 1
        reason = next((r.get('rejected') or r.get('pending') or r.get('error') for r in rs
                       if outcome(r) != 'valid'), '')
        print(f'{name:50s} {counts or "nothing found"}  {reason[:90] if reason else ""}')
    print('window:          ', res['_window'])
    print('window (indexed):', res['_window_indexed'])
    print('window (early):  ', res['_window_early'])


if __name__ == '__main__':
    main()
