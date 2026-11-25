"""SPDX-License-Identifier: MIT. Invitation to future senders: reply formats and verification.

A reply is valid if it contains the hash of a Bitcoin block and is anchored in an earlier
block of the same chain, at least MIN_LEAD blocks before the block whose hash it contains.
The essential check is descent (check_descent): the named block's header chain leads back to
the anchor, which commits to the reply. The named block's hash then depends on the reply, so a
reply containing it was fixed before that block existed; forging it needs a constrained preimage
or a fixed point of double SHA-256. The lead and confirmation rules are conservative margins.

Two ways to anchor a reply:

- text: any file whose plain text contains a line
      CLL-FUTURE-REPLY-v1 hash=<64 hex digits>      (optionally "height=<h>" before hash=)
  stamped with OpenTimestamps (ctc/blockchain/ots_support.py finds the stamp block);
- transaction: a Bitcoin transaction with an OP_RETURN output whose data is
      b'CLLF' + b'\\x01' + <32-byte block hash, display order>
  (the same 37 bytes anywhere in the txid-covered serialization also count, e.g. a coinbase
  scriptSig). The transaction's block is found from a merkle proof against a verified header.

Header checks (proof of work, two explorers agreeing) reuse ctc/blockchain/chain.py.
Run `python -B ctc/invitation/reply.py --help` for the command-line checker.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'blockchain'))
import chain  # noqa: E402

PROTOCOL = 'cll-future-reply-v1'
TEXT_TAG = 'CLL-FUTURE-REPLY-v1'
MAGIC = b'CLLF'
VERSION = 1
MIN_LEAD = 6          # the anchor block must be at least this many blocks before the answer block
CONFIRMATIONS = 6     # the answer block must be buried this deep before a reply is judged
WINDOW = 144          # preferred: anchor within P..P+WINDOW, P = the invitation's own anchor block
                      # (about one day). A request to senders, not a validity rule.

REPLY_RE = re.compile(TEXT_TAG + r'[ \t]+(?:height=(\d+)[ \t]+)?hash=([0-9A-Fa-f]{64})(?![0-9A-Fa-f])')


class ReplyRejected(Exception):
    """Definitely not a valid reply (for example, it names a block mined before its anchor)."""


class Pending(Exception):
    """Cannot be decided yet: the named block is unknown (it may not exist yet) or not buried enough.

    A reply that names no known block is the most interesting kind: it may name a future block.
    It must be kept and checked again, never discarded as a failed guess.
    """


# ---------------------------------------------------------------- formats

def text_line(block_hash, height=None):
    h = f'height={height} ' if height is not None else ''
    return f'{TEXT_TAG} {h}hash={block_hash.lower()}'


def find_text_replies(text):
    """[(height or None, hash hex lower)] for every reply line in a text."""
    return [(int(h) if h else None, x.lower()) for h, x in REPLY_RE.findall(text)]


def payload(block_hash):
    """OP_RETURN data for a reply: magic, version, the 32-byte hash in display order."""
    raw = bytes.fromhex(block_hash)
    if len(raw) != 32:
        raise ValueError('a block hash has 32 bytes')
    return MAGIC + bytes([VERSION]) + raw


def decode_payload(data):
    """Block hash hex from OP_RETURN data, or None if it is not a reply."""
    if len(data) == 37 and data[:4] == MAGIC and data[4] == VERSION:
        return data[5:].hex()
    return None


def op_return_script(data):
    if len(data) > 75:
        raise ValueError('use a direct push of at most 75 bytes')
    return b'\x6a' + bytes([len(data)]) + data


def op_return_data(script):
    """Concatenated pushes of an OP_RETURN script, or None if the script is not OP_RETURN."""
    if not script or script[0] != 0x6a:
        return None
    out, i = b'', 1
    while i < len(script):
        op = script[i]
        i += 1
        if 1 <= op <= 75:
            n = op
        elif op == 0x4c:
            n, i = script[i], i + 1
        elif op == 0x4d:
            n, i = int.from_bytes(script[i:i + 2], 'little'), i + 2
        elif op == 0:
            n = 0
        else:
            return None
        if i + n > len(script):
            return None
        out += script[i:i + n]
        i += n
    return out


# ---------------------------------------------------------------- transactions and merkle proofs

def dsha(b):
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()


def _varint(b, i):
    v = b[i]
    if v < 0xfd:
        return v, i + 1
    n = {0xfd: 2, 0xfe: 4, 0xff: 8}[v]
    return int.from_bytes(b[i + 1:i + 1 + n], 'little'), i + 1 + n


def parse_tx(raw):
    """{'txid', 'segwit', 'outputs': [script bytes], 'stripped'}; the txid excludes witness data."""
    try:
        tx, end = _parse_tx_at(raw, 0)
    except (IndexError, KeyError) as ex:
        raise ValueError(f'malformed transaction: {ex!r}')
    if end != len(raw):
        raise ValueError('transaction has trailing or missing bytes')
    return tx


def _parse_tx_at(raw, i0):
    """Parse one transaction starting at raw[i0]; returns (tx dict, end offset)."""
    i = i0 + 4
    segwit = raw[i0 + 4] == 0 and raw[i0 + 5] == 1
    if segwit:
        i = i0 + 6
    start_io = i
    n_in, i = _varint(raw, i)
    for _ in range(n_in):
        i += 36
        n, i = _varint(raw, i)
        i += n + 4
    n_out, i = _varint(raw, i)
    outputs = []
    for _ in range(n_out):
        i += 8
        n, i = _varint(raw, i)
        outputs.append(raw[i:i + n])
        i += n
    end_io = i
    if segwit:
        for _ in range(n_in):
            items, i = _varint(raw, i)
            for _ in range(items):
                n, i = _varint(raw, i)
                i += n
    if i + 4 > len(raw):
        raise IndexError('transaction ends early')
    stripped = raw[i0:i0 + 4] + raw[start_io:end_io] + raw[i:i + 4]
    tx = {'txid': dsha(stripped)[::-1].hex(), 'segwit': segwit, 'outputs': outputs, 'stripped': stripped}
    return tx, i + 4


def parse_block(raw):
    """(80-byte header, [tx dicts]) from a raw block."""
    try:
        n, i = _varint(raw, 80)
        txs = []
        for _ in range(n):
            tx, i = _parse_tx_at(raw, i)
            txs.append(tx)
    except (IndexError, KeyError) as ex:
        raise ValueError(f'malformed block: {ex!r}')
    if i != len(raw):
        raise ValueError('block has trailing or missing bytes')
    return raw[:80], txs


def merkle_root_from_branch(txid, branch, pos):
    """Merkle root (internal byte order) from a txid and an Esplora-style branch (display hex)."""
    h = bytes.fromhex(txid)[::-1]
    for sibling in branch:
        s = bytes.fromhex(sibling)[::-1]
        h = dsha(s + h) if pos & 1 else dsha(h + s)
        pos >>= 1
    return h


def merkle_root(txids):
    """Merkle root (internal order) of a list of txids (display hex), as Bitcoin computes it."""
    level = [bytes.fromhex(t)[::-1] for t in txids]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [dsha(level[k] + level[k + 1]) for k in range(0, len(level), 2)]
    return level[0]


def merkle_branch(txids, pos):
    """Branch (display hex) for txids[pos]; inverse of merkle_root_from_branch, for tests."""
    level = [bytes.fromhex(t)[::-1] for t in txids]
    out = []
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        out.append(level[pos ^ 1][::-1].hex())
        level = [dsha(level[k] + level[k + 1]) for k in range(0, len(level), 2)]
        pos >>= 1
    return out


def replies_in_tx(raw):
    """(txid, [block hash hex]) for every reply payload in the part of a transaction the txid covers.

    The recommended place is an OP_RETURN output, but a payload anywhere in the stripped
    serialization counts (for example in a coinbase scriptSig), because the txid, and so the
    block's merkle root, commits to all of it. Witness data is excluded: the txid does not
    commit to it.
    """
    tx = parse_tx(raw)
    return tx['txid'], _payloads(tx['stripped'])


def _payloads(s):
    tag, found, i = MAGIC + bytes([VERSION]), [], 0
    while True:
        i = s.find(tag, i)
        if i < 0 or i + 37 > len(s):
            break
        found.append(s[i + 5:i + 37].hex())
        i += 1
    return found


# ---------------------------------------------------------------- judging a reply

def chance_per_reply(answer_header):
    """Probability that a random guess equals the answer block's hash, in either byte order.

    Only the part below the proof-of-work target is unpredictable: a hash in display order
    starts with about 19 zero hex digits, so a prefix match says almost nothing.
    """
    return 2.0 / chain.target(answer_header)


def window_label(anchor_height, answer_height, invitation_height, window=WINDOW, lead=MIN_LEAD):
    """Where a reply lies relative to the preferred window.

    Preferred: anchored in P..P+window and naming a block no later than P+window+lead, so that
    every reply in the window can be judged once block P+window+lead is confirmed.
    """
    if invitation_height is None:
        return 'unknown (invitation anchor not given)'
    p = invitation_height
    if anchor_height < p:
        return 'before the invitation was anchored'
    if anchor_height > p + window:
        return 'after the preferred window'
    if answer_height > p + window + lead:
        return f'anchored in the preferred window, but names a block after P + {window + lead}'
    return 'inside the preferred window'


def judge(claimed_hash, answer, anchor_height, tip, lead=MIN_LEAD, confirmations=CONFIRMATIONS,
          invitation_height=None):
    """Accept or reject one reply.

    answer = (height, block hash hex, header bytes), already checked by chain.check_header.
    anchor_height = the earliest verified block that commits to the reply.
    invitation_height = P, the invitation's own anchor block, if known; only used to label the
    reply relative to the preferred window, never to accept or reject it.
    Raises ReplyRejected; returns a summary dict if the reply is valid.
    """
    h_height, h_hash, h_header = answer
    claimed = claimed_hash.lower()
    reversed_hash = bytes.fromhex(h_hash)[::-1].hex()
    if claimed not in (h_hash.lower(), reversed_hash):
        raise ReplyRejected(f'claimed hash does not equal block {h_height}')
    if anchor_height is None:
        raise ReplyRejected('the reply is not anchored in any verified block')
    if anchor_height > h_height - lead:
        raise ReplyRejected(f'anchored in block {anchor_height}, but must be <= {h_height - lead}')
    if tip < h_height + confirmations - 1:
        raise Pending(f'block {h_height} has fewer than {confirmations} confirmations; check again later')
    return {'protocol': PROTOCOL, 'answer_height': h_height, 'answer_hash': h_hash, 'anchor_height': anchor_height,
            'lead_blocks': h_height - anchor_height,
            'window': window_label(anchor_height, h_height, invitation_height),
            'chance_probability': chance_per_reply(h_header),
            'chance_log2': math.log2(chance_per_reply(h_header))}


# ---------------------------------------------------------------- network lookups (two explorers must agree)

def height_of(block_hash):
    """Height of a block in the best chain; None if no explorer knows the hash.

    Esplora answers an unknown hash with {"in_best_chain": false, "height": null}, not an
    error, so "unknown" (try the other byte order) and "stale" (a known block outside the best
    chain) must be told apart.
    """
    seen = set()
    for e in chain.EXPLORERS:
        status = json.loads(chain._get(f'{e}/block/{block_hash}/status'))
        seen.add((status.get('in_best_chain'), status.get('height')))
    if len(seen) != 1:
        raise ValueError(f'explorers disagree about block {block_hash}: {seen}')
    best, height = seen.pop()
    if height is None:
        return None
    if not best:
        raise ReplyRejected(f'block {block_hash} is not in the best chain')
    return height


def _not_found(ex):
    return isinstance(ex, LookupError) or (isinstance(ex, urllib.error.HTTPError) and ex.code == 404)


def _get_bytes(url):
    def call():
        req = urllib.request.Request(url, headers={'User-Agent': chain.USER_AGENT})
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read()
    return chain.with_retries(call)


def fetch_raw_block(height, fetch=chain.fetch_header):
    """Raw block at a height. One explorer suffices: scan_block checks it against the header."""
    block_hash, _ = fetch(height)
    last = None
    for e in chain.EXPLORERS:
        try:
            return _get_bytes(f'{e}/block/{block_hash}/raw')
        except Exception as ex:
            last = ex
    raise last


def fetch_tx(txid):
    """(raw bytes, block height, branch, pos); every explorer must return the same."""
    seen = set()
    for e in chain.EXPLORERS:
        raw = chain._get(f'{e}/tx/{txid}/hex').lower()
        proof = json.loads(chain._get(f'{e}/tx/{txid}/merkle-proof'))
        seen.add((raw, proof['block_height'], tuple(proof['merkle']), proof['pos']))
    if len(seen) != 1:
        raise ValueError(f'explorers disagree about transaction {txid}')
    raw, height, branch, pos = seen.pop()
    return bytes.fromhex(raw), height, list(branch), pos


def verified_answer(block_hash, height=None, fetch=chain.fetch_header, locate=height_of):
    """(height, hash, header) for a claimed block hash, in either byte order, checked.

    A height given in the reply is only a hint: if the block there has another hash, the
    hash is looked up instead.
    """
    stale = None
    for candidate in (block_hash.lower(), bytes.fromhex(block_hash)[::-1].hex()):
        tries = ([height] if height is not None else []) + [None]
        for h in tries:
            try:
                h = h if h is not None else locate(candidate)
                if h is None:
                    continue
                found_hash, header = fetch(h)
            except ReplyRejected as ex:          # a known block outside the best chain (margin rule 5)
                stale = ReplyRejected(f'margin rule (best chain only): {ex}; kept on record for manual review')
                continue
            except Exception as ex:
                if _not_found(ex):
                    continue
                raise                            # network or explorer trouble: an error, not a verdict
            chain.check_header(header, found_hash, h)
            if found_hash.lower() == candidate:
                return h, found_hash, header
    if stale:
        raise stale
    raise Pending(f'names no block known so far ({block_hash}); it may name a future block: check again later')


def check_descent(anchor_height, answer, fetch=chain.fetch_header):
    """The essential check: the answer block descends from the anchor block, header by header.

    Every header from the anchor to the answer is fetched, its proof of work recomputed and its
    link to the previous header checked. The anchor commits to the reply, so the answer block's
    hash depends on the reply: if the reply contains that hash, it was fixed before the answer
    block existed, unless someone found a constrained preimage or a fixed point of double SHA-256.
    """
    h_height, h_hash, _ = answer
    try:
        headers = chain.verified_range(anchor_height, h_height, fetch)
    except ValueError as ex:
        raise ReplyRejected(f'answer block does not descend from the anchor block: {ex}')
    if headers[h_height][0].lower() != h_hash.lower():
        raise ReplyRejected('the verified chain ends in another block')


def _judge_all(claims, anchor_height, tip, fetch, locate, descent, invitation_height=None):
    """Judge claims; each result has 'outcome': valid, rejected, pending or error."""
    results = []
    for height, claimed in claims:
        base = {'claimed': claimed, 'anchor_height': anchor_height}
        if anchor_height is None:
            results.append(dict(base, outcome='pending',
                                pending='not yet anchored in a verified block (upgrade the OpenTimestamps proof)'))
            continue
        try:
            answer = verified_answer(claimed, height, fetch, locate)
            r = judge(claimed, answer, anchor_height, tip, invitation_height=invitation_height)
            if descent:
                check_descent(anchor_height, answer, fetch)
                r['descent'] = 'verified header by header'
                r['outcome'] = 'valid'
            else:
                r['descent'] = 'NOT CHECKED: provisional result only'
                r['outcome'] = 'valid (provisional)'
            results.append(dict(base, **r))
        except ReplyRejected as ex:
            results.append(dict(base, outcome='rejected', rejected=str(ex)))
        except Pending as ex:
            results.append(dict(base, outcome='pending', pending=str(ex)))
        except Exception as ex:                  # could not check: neither valid nor rejected
            results.append(dict(base, outcome='error', error=f'{type(ex).__name__}: {ex}'))
    return results


def window_summary(scan, invitation_height, tip, window=WINDOW, lead=MIN_LEAD, confirmations=CONFIRMATIONS):
    """Verdict on the preferred window from a scan of blocks P..P+window.

    The window closes when block P+window+lead is buried `confirmations` deep: from then on no
    reply anchored in the window can still become valid inside it. Pending replies anchored in
    the window stay pending (they may name a later block), but they can no longer count for it.
    """
    p = invitation_height
    closes_at = p + window + lead + confirmations - 1
    covered = scan['scanned_from'] <= p and scan['scanned_to'] >= p + window
    in_window = [r for r in scan['replies'] if p <= r['anchor_height'] <= p + window]
    counts = {}
    for r in in_window:
        counts[r['outcome']] = counts.get(r['outcome'], 0) + 1
    valid_inside = [r for r in in_window if r['outcome'] == 'valid' and r['window'] == 'inside the preferred window']
    if valid_inside:
        verdict = f'VALID REPLY IN THE WINDOW ({len(valid_inside)})'
    elif not covered:
        verdict = 'incomplete: the scan does not cover blocks P..P+%d' % window
    elif tip < closes_at:
        verdict = f'open: the window closes when the tip reaches block {closes_at}'
    elif counts.get('error') or counts.get('valid (provisional)'):
        verdict = 'incomplete: some replies could not be checked fully; rerun'
    else:
        verdict = 'closed: no valid transaction reply anchored in the window'
    return {'verdict': verdict, 'P': p, 'closes_at': closes_at, 'tip': tip,
            'replies_anchored_in_window': counts}


def check_text(path, anchor_height, tip, fetch=chain.fetch_header, locate=height_of, descent=True,
               invitation_height=None):
    """Judge every reply line in a stamped text file; anchor_height from the OTS proof."""
    claims = find_text_replies(Path(path).read_text(encoding='utf-8', errors='replace'))
    return _judge_all(claims, anchor_height, tip, fetch, locate, descent, invitation_height)


def check_tx(raw, height, branch, pos, tip, fetch=chain.fetch_header, locate=height_of, descent=True,
             invitation_height=None):
    """Judge the reply payloads of a transaction mined in block `height`."""
    block_hash, header = fetch(height)
    chain.check_header(header, block_hash, height)
    txid, claims = replies_in_tx(raw)
    if merkle_root_from_branch(txid, branch, pos) != chain.merkle_root(header):
        raise ReplyRejected(f'transaction {txid} is not in block {height}')
    return _judge_all([(None, c) for c in claims], height, tip, fetch, locate, descent, invitation_height)


def scan_block(raw_block, height, fetch=chain.fetch_header):
    """[(txid, [claimed hashes])] for every transaction with a reply payload in a raw block.

    The block body must match the verified header at that height (same header bytes, and the
    merkle root of all its txids), so a scan with no finding proves that the block holds no
    transaction reply.
    """
    header, txs = parse_block(raw_block)
    block_hash, verified = fetch(height)
    chain.check_header(verified, block_hash, height)
    if header != verified:
        raise ValueError(f'raw block is not block {height}')
    if merkle_root([t['txid'] for t in txs]) != chain.merkle_root(header):
        raise ValueError(f'transactions of block {height} do not match its merkle root')
    return [(t['txid'], c) for t in txs for c in [_payloads(t['stripped'])] if c]


def scan_range(first, last, tip, fetch=chain.fetch_header, fetch_raw=None, locate=height_of, descent=True,
               invitation_height=None, index_upto=None):
    """Scan blocks first..last for transaction replies and judge every one found.

    index_upto: look claimed hashes up only among the verified headers first..index_upto,
    fetched once, instead of asking the explorers for every claim. A flood of random payloads
    then costs no network requests. Claims not in that span come out pending (they may name a
    later block), which is all the window verdict needs (index_upto = P + window + lead).
    """
    fetch_raw = fetch_raw or (lambda h: fetch_raw_block(h, fetch))
    lookup = 'explorers, for every claim'
    if index_upto is not None:
        headers = chain.verified_range(first, min(index_upto, tip), fetch)
        index = {b.lower(): h for h, (b, _) in headers.items()}
        locate = index.get
        lookup = f'verified headers {first}..{min(index_upto, tip)} only; claims outside them are pending'
    found = []
    for height in range(first, last + 1):
        for txid, claims in scan_block(fetch_raw(height), height, fetch):
            for r in _judge_all([(None, c) for c in claims], height, tip, fetch, locate, descent,
                                invitation_height):
                found.append(dict(r, txid=txid, block=height))
    return {'scanned_from': first, 'scanned_to': last, 'lookup': lookup, 'replies': found}


def main():
    ap = argparse.ArgumentParser(description='Check a reply to the invitation to future senders.')
    ap.add_argument('--text', help='a text file containing reply lines')
    ap.add_argument('--ots', help='its OpenTimestamps proof (default: <text>.ots)')
    ap.add_argument('--txid', help='a Bitcoin transaction with a reply in an OP_RETURN output')
    ap.add_argument('--show-payload', metavar='BLOCK_HASH', help='print the OP_RETURN data and text line for a hash')
    ap.add_argument('--no-descent', action='store_true',
                    help='skip the header-by-header descent check (quick screening; results are provisional)')
    ap.add_argument('--invitation-height', type=int, metavar='P',
                    help="the invitation's own anchor block, to label replies relative to the preferred window")
    ap.add_argument('--scan', type=int, nargs=2, metavar=('FIRST', 'LAST'),
                    help='download blocks FIRST..LAST, check them against their headers, and judge every '
                         'transaction reply in them (for the window: P and P + 144)')
    a = ap.parse_args()
    if a.show_payload:
        print('OP_RETURN data:', payload(a.show_payload).hex())
        print('text line:     ', text_line(a.show_payload))
        return
    tip = chain.tip_height()
    if a.text:
        import ots_support
        anchor = ots_support.first_verified_block(a.text, a.ots or a.text + '.ots', chain.fetch_header)
        results = check_text(a.text, anchor, tip, descent=not a.no_descent, invitation_height=a.invitation_height)
    elif a.txid:
        raw, height, branch, pos = fetch_tx(a.txid)
        results = check_tx(raw, height, branch, pos, tip, descent=not a.no_descent,
                           invitation_height=a.invitation_height)
    elif a.scan:
        first, last = a.scan
        if last > tip:
            ap.error(f'block {last} does not exist yet (tip {tip})')
        p = a.invitation_height
        scan = scan_range(first, last, tip, descent=not a.no_descent, invitation_height=p,
                          index_upto=None if p is None else p + WINDOW + MIN_LEAD)
        if a.invitation_height is not None:
            scan['window_summary'] = window_summary(scan, a.invitation_height, tip)
        print(json.dumps(scan, indent=1))
        return
    else:
        ap.error('give --text, --txid or --scan')
    print(json.dumps(results, indent=1))
    if not results:
        print('no reply found')


if __name__ == '__main__':
    main()
