"""SPDX-License-Identifier: MIT. Offline checks for the invitation to future senders (ctc/invitation/).

Uses real Bitcoin headers (ctc/tests/fixtures/btc_headers.json) and two real transactions
(ctc/tests/fixtures/invitation_txs.json: the coinbase of block 977066 and the genesis
coinbase), so no network is needed.

Run from the repository root:  python -B ctc/tests/test_invitation.py
"""
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'invitation'))
sys.path.insert(0, str(HERE.parent / 'blockchain'))
import chain  # noqa: E402
import predictions  # noqa: E402
import simulate  # noqa: E402
from reply import (MIN_LEAD, WINDOW, Pending, ReplyRejected, window_label, chance_per_reply, check_text, check_tx, decode_payload,  # noqa: E402,F401
                   find_text_replies, judge, merkle_branch, merkle_root, merkle_root_from_branch, op_return_data,
                   op_return_script, parse_block, parse_tx, payload, replies_in_tx, scan_block, scan_range,
                   text_line, verified_answer)

HEADERS = {int(h): (b, bytes.fromhex(hd)) for h, (b, hd) in
           json.loads((HERE / 'fixtures' / 'btc_headers.json').read_text()).items()}
TXS = json.loads((HERE / 'fixtures' / 'invitation_txs.json').read_text())
ANSWER = 977066
ANSWER_HASH = HEADERS[ANSWER][0]
TIP = 977071          # ANSWER + CONFIRMATIONS - 1: just buried enough


def fetch(height):
    return HEADERS[height]


def locate(block_hash):
    """Like the explorers: None (not an error) for a hash nobody knows."""
    for h, (b, _) in HEADERS.items():
        if b == block_hash:
            return h
    return None


def answer():
    return verified_answer(ANSWER_HASH, None, fetch, locate)


def synthetic_tx(scripts, segwit=False, witness_item=b'\x00' * 32):
    """A minimal transaction (one dummy input) with the given output scripts."""
    body = b'\x01' + b'\x11' * 32 + b'\x00\x00\x00\x00' + b'\x00' + b'\xff\xff\xff\xff'
    body += bytes([len(scripts)]) + b''.join(b'\x00' * 8 + bytes([len(s)]) + s for s in scripts)
    version, locktime = b'\x02\x00\x00\x00', b'\x00\x00\x00\x00'
    if segwit:
        return version + b'\x00\x01' + body + b'\x01' + bytes([len(witness_item)]) + witness_item + locktime
    return version + body + locktime


class Formats(unittest.TestCase):
    def test_text_lines_are_found(self):
        text = '\n'.join(['hello', text_line(ANSWER_HASH), text_line(ANSWER_HASH.upper(), 977066),
                          'CLL-FUTURE-REPLY-v1 hash=' + 'a' * 63, 'CLL-FUTURE-REPLY-v1 hash=' + 'b' * 65])
        self.assertEqual(find_text_replies(text), [(None, ANSWER_HASH), (977066, ANSWER_HASH)])

    def test_payload_round_trip_and_script(self):
        p = payload(ANSWER_HASH)
        self.assertEqual(len(p), 37)
        self.assertEqual(decode_payload(p), ANSWER_HASH)
        self.assertEqual(op_return_data(op_return_script(p)), p)
        self.assertIsNone(decode_payload(b'XXXX' + p[4:]))
        self.assertIsNone(decode_payload(p[:4] + b'\x02' + p[5:]))
        self.assertIsNone(op_return_data(b'\x76\xa9'))


class RealTransactions(unittest.TestCase):
    def test_segwit_coinbase_parses_and_sits_in_its_block(self):
        c = TXS['coinbase_977066']
        tx = parse_tx(bytes.fromhex(c['raw']))
        self.assertTrue(tx['segwit'])
        self.assertEqual(tx['txid'], c['txid'])
        commitments = [op_return_data(s) for s in tx['outputs'] if op_return_data(s) is not None]
        self.assertTrue(any(d.startswith(bytes.fromhex('aa21a9ed')) for d in commitments))  # witness commitment
        root = merkle_root_from_branch(c['txid'], c['merkle'], c['pos'])
        self.assertEqual(root, chain.merkle_root(HEADERS[c['block_height']][1]))

    def test_genesis_coinbase(self):
        g = TXS['genesis_coinbase']
        raw = bytes.fromhex(g['raw'])
        tx = parse_tx(raw)
        self.assertFalse(tx['segwit'])
        self.assertEqual(tx['txid'], g['txid'])
        self.assertEqual(merkle_root_from_branch(g['txid'], [], 0), chain.merkle_root(HEADERS[0][1]))
        self.assertIn(b'Chancellor on brink of second bailout', raw)

    def test_tampered_transaction_is_not_in_the_block(self):
        c = TXS['coinbase_977066']
        raw = bytearray(bytes.fromhex(c['raw']))
        raw[0] ^= 1
        with self.assertRaises(ReplyRejected):
            check_tx(bytes(raw), c['block_height'], c['merkle'], c['pos'], TIP, fetch, locate)
        # The witness is not part of the txid; changing it leaves the outputs, and so any reply, intact.
        witness_changed = bytearray(bytes.fromhex(c['raw']))
        witness_changed[-10] ^= 1
        self.assertEqual(parse_tx(bytes(witness_changed))['txid'], c['txid'])


class Merkle(unittest.TestCase):
    def test_branch_and_root_agree_for_every_position(self):
        txids = [synthetic_tx([op_return_script(bytes([k]))]) for k in range(7)]
        txids = [parse_tx(t)['txid'] for t in txids]
        root = merkle_root(txids)
        for pos in range(7):
            self.assertEqual(merkle_root_from_branch(txids[pos], merkle_branch(txids, pos), pos), root)
        self.assertNotEqual(merkle_root_from_branch(txids[0], merkle_branch(txids, 1), 1), root)

    def test_reply_payload_in_a_synthetic_transaction(self):
        for segwit in (False, True):
            raw = synthetic_tx([b'\x00\x14' + b'\x22' * 20, op_return_script(payload(ANSWER_HASH))], segwit)
            txid, claims = replies_in_tx(raw)
            self.assertEqual(claims, [ANSWER_HASH])
            self.assertEqual(txid, parse_tx(synthetic_tx([b'\x00\x14' + b'\x22' * 20,
                                                          op_return_script(payload(ANSWER_HASH))]))['txid'])


class Judging(unittest.TestCase):
    def test_valid_reply(self):
        r = judge(ANSWER_HASH, answer(), ANSWER - MIN_LEAD, TIP)
        self.assertEqual(r['lead_blocks'], MIN_LEAD)
        self.assertLess(r['chance_log2'], -150)

    def test_reversed_byte_order_is_accepted(self):
        judge(bytes.fromhex(ANSWER_HASH)[::-1].hex(), answer(), ANSWER - MIN_LEAD, TIP)
        h, _, _ = verified_answer(bytes.fromhex(ANSWER_HASH)[::-1].hex(), None, fetch, locate)
        self.assertEqual(h, ANSWER)

    def test_anchor_too_late(self):
        with self.assertRaises(ReplyRejected):
            judge(ANSWER_HASH, answer(), ANSWER - MIN_LEAD + 1, TIP)
        with self.assertRaises(ReplyRejected):
            judge(ANSWER_HASH, answer(), ANSWER + 1, TIP)

    def test_wrong_hash(self):
        wrong = ANSWER_HASH[:-1] + ('0' if ANSWER_HASH[-1] != '0' else '1')
        with self.assertRaises(ReplyRejected):
            judge(wrong, answer(), ANSWER - MIN_LEAD, TIP)

    def test_unanchored_or_unconfirmed(self):
        with self.assertRaises(ReplyRejected):
            judge(ANSWER_HASH, answer(), None, TIP)
        with self.assertRaises(Pending):              # too early to judge is not a rejection
            judge(ANSWER_HASH, answer(), ANSWER - MIN_LEAD, TIP - 1)
        with tempfile.TemporaryDirectory() as d:     # an OpenTimestamps proof not yet in a block
            p = Path(d) / 'reply.txt'
            p.write_text(text_line(ANSWER_HASH), encoding='utf-8')
            self.assertEqual(check_text(p, None, TIP, fetch, locate)[0]['outcome'], 'pending')

    def test_unknown_hash_is_pending_not_rejected(self):
        """It may name a block that does not exist yet: keep it and check again later."""
        with self.assertRaises(Pending):
            verified_answer('ab' * 32, None, fetch, locate)

    def test_leading_zeros_make_prefixes_worthless(self):
        """A display-order hash starts with ~19 zero hex digits: only the full hash counts."""
        zeros = len(ANSWER_HASH) - len(ANSWER_HASH.lstrip('0'))
        self.assertGreaterEqual(zeros, 19)
        guess = ANSWER_HASH[:zeros] + 'f' * (64 - zeros)
        with self.assertRaises(ReplyRejected):
            judge(guess, answer(), ANSWER - MIN_LEAD, TIP)
        bits = -math.log2(chance_per_reply(HEADERS[ANSWER][1]))
        self.assertTrue(170 < bits < 185, bits)        # about 256 - 4*19 unpredictable bits

    def test_text_file_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'reply.txt'
            p.write_text('From 2200, greetings.\n' + text_line(ANSWER_HASH) + '\n'
                         + text_line('00' * 32) + '\n', encoding='utf-8')
            r = check_text(p, ANSWER - MIN_LEAD, TIP, fetch, locate)
            self.assertEqual(r[0]['answer_height'], ANSWER)
            self.assertEqual(r[0]['outcome'], 'valid')
            self.assertEqual(r[1]['outcome'], 'pending')
            late = check_text(p, ANSWER - 1, TIP, fetch, locate)
            self.assertIn('rejected', late[0])


class Descent(unittest.TestCase):
    """The essential check: the named block descends from the anchor, header by header."""

    def test_descent_verified(self):
        r = check_text_reply(ANSWER - MIN_LEAD)
        self.assertEqual(r[0]['descent'], 'verified header by header')

    def test_forged_answer_header_that_does_not_descend(self):
        """Colluding explorers place a real, valid header at a height where it does not belong."""
        def lying_fetch(height):
            return HEADERS[977067] if height == ANSWER - 3 else HEADERS[height]   # full work, wrong link
        r = check_descent_result(lying_fetch)
        self.assertIn('rejected', r[0])
        self.assertIn('descend', r[0]['rejected'])

    def test_skipping_descent_marks_the_result_provisional(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'reply.txt'
            p.write_text(text_line(ANSWER_HASH), encoding='utf-8')
            r = check_text(p, ANSWER - MIN_LEAD, TIP, fetch, locate, descent=False)
            self.assertIn('NOT CHECKED', r[0]['descent'])

    def test_wrong_height_hint_falls_back_to_lookup(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'reply.txt'
            p.write_text(text_line(ANSWER_HASH, height=ANSWER + 1), encoding='utf-8')
            r = check_text(p, ANSWER - MIN_LEAD, TIP, fetch, locate)
            self.assertEqual(r[0]['answer_height'], ANSWER)

    def test_payload_in_a_coinbase_script_sig_counts(self):
        """Anywhere in the txid-covered bytes counts; the witness does not."""
        raw = synthetic_tx([b'\x00\x14' + b'\x22' * 20])
        script_sig = b'\x03\x01\x02\x03' + payload(ANSWER_HASH)
        raw_cb = raw[:4] + b'\x01' + b'\x00' * 32 + b'\xff\xff\xff\xff' + bytes([len(script_sig)]) + script_sig \
            + b'\xff\xff\xff\xff' + raw[4 + 1 + 32 + 4 + 1 + 4:]
        self.assertEqual(replies_in_tx(raw_cb)[1], [ANSWER_HASH])
        in_witness = synthetic_tx([b'\x6a\x01\x00'], segwit=True, witness_item=payload(ANSWER_HASH))
        self.assertIn(payload(ANSWER_HASH), in_witness)
        self.assertEqual(replies_in_tx(in_witness)[1], [])


class PreferredWindow(unittest.TestCase):
    """The window P..P+144 labels replies; it never decides validity."""

    def test_labels(self):
        p = 1000
        self.assertEqual(window_label(p, p + 6, p), 'inside the preferred window')
        self.assertEqual(window_label(p + WINDOW, p + WINDOW + MIN_LEAD, p), 'inside the preferred window')
        self.assertIn('names a block after', window_label(p + 1, p + WINDOW + MIN_LEAD + 1, p))
        self.assertEqual(window_label(p + WINDOW + 1, p + WINDOW + 7, p), 'after the preferred window')
        self.assertEqual(window_label(p - 1, p + 5, p), 'before the invitation was anchored')
        self.assertIn('unknown', window_label(p, p + 6, None))

    def test_replies_outside_the_window_stay_valid(self):
        anchor = ANSWER - MIN_LEAD
        for invitation in (anchor, anchor + 1, anchor - WINDOW - 1):
            with tempfile.TemporaryDirectory() as d:
                path = Path(d) / 'reply.txt'
                path.write_text(text_line(ANSWER_HASH), encoding='utf-8')
                r = check_text(path, anchor, TIP, fetch, locate, invitation_height=invitation)
                self.assertEqual(r[0]['answer_height'], ANSWER)
                self.assertNotIn('rejected', r[0])
        self.assertEqual(r[0]['window'], 'after the preferred window')


class Lookups(unittest.TestCase):
    """Unknown, stale and unreachable blocks must give different outcomes."""

    def test_unknown_display_order_falls_through_to_reversed(self):
        """Explorers answer an unknown hash with height null; the reversed order must still be tried."""
        h, _, _ = verified_answer(bytes.fromhex(ANSWER_HASH)[::-1].hex(), None, fetch, locate)
        self.assertEqual(h, ANSWER)

    def test_stale_block_is_rejected(self):
        def stale_locate(block_hash):
            if block_hash == ANSWER_HASH:
                raise ReplyRejected(f'block {block_hash} is not in the best chain')
            return None
        with self.assertRaises(ReplyRejected) as cm:
            verified_answer(ANSWER_HASH, None, fetch, stale_locate)
        self.assertIn('best chain', str(cm.exception))

    def test_transient_failures_are_retried_but_404_is_not(self):
        """The first live scan died on one timed-out request; transient failures are now retried."""
        import urllib.error
        calls, waits = [], []

        def flaky():
            calls.append(1)
            if len(calls) < 3:
                raise TimeoutError('The read operation timed out')
            return 'ok'
        self.assertEqual(chain.with_retries(flaky, sleep=waits.append), 'ok')
        self.assertEqual((len(calls), waits), (3, [2.0, 4.0]))

        def missing():
            calls.append(1)
            raise urllib.error.HTTPError('u', 404, 'Not Found', None, None)
        calls.clear()
        with self.assertRaises(urllib.error.HTTPError):
            chain.with_retries(missing, sleep=waits.append)
        self.assertEqual(len(calls), 1)

        def always_down():
            raise urllib.error.HTTPError('u', 503, 'Unavailable', None, None)
        with self.assertRaises(urllib.error.HTTPError):
            chain.with_retries(always_down, retries=2, sleep=lambda s: None)

    def test_network_trouble_is_an_error_not_a_rejection(self):
        def broken(block_hash):
            raise OSError('connection reset')
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'reply.txt'
            p.write_text(text_line(ANSWER_HASH), encoding='utf-8')
            r = check_text(p, ANSWER - MIN_LEAD, TIP, fetch, broken)
        self.assertIn('error', r[0])
        self.assertNotIn('rejected', r[0])


def synthetic_header(merkle, bits=0x207fffff):
    """A header with trivial proof of work (regtest difficulty) for a given merkle root."""
    for nonce in range(1000):
        header = (b'\x01\x00\x00\x00' + b'\x00' * 32 + merkle + b'\x00\x00\x00\x00'
                  + bits.to_bytes(4, 'little') + nonce.to_bytes(4, 'little'))
        if int(chain.header_hash(header), 16) <= chain.target(header):
            return header
    raise RuntimeError('no nonce found')


def synthetic_block(txs):
    txids = [parse_tx(t)['txid'] for t in txs]
    header = synthetic_header(merkle_root(txids))
    body = bytes([len(txs)]) + b''.join(txs)
    return header, header + body


class BlockScan(unittest.TestCase):
    RAW = {int(h): bytes.fromhex(x) for h, x in TXS['raw_blocks_0_to_2'].items()}

    def test_real_blocks_parse_and_hold_no_reply(self):
        for h, raw in self.RAW.items():
            header, txs = parse_block(raw)
            self.assertEqual(header, HEADERS[h][1])
            self.assertEqual(merkle_root([t['txid'] for t in txs]), chain.merkle_root(header))
            self.assertEqual(scan_block(raw, h, fetch), [])
        r = scan_range(0, 2, TIP, fetch, lambda h: self.RAW[h], locate)
        self.assertEqual((r['scanned_from'], r['scanned_to'], r['replies']), (0, 2, []))

    def test_raw_block_must_match_its_header(self):
        raw = bytearray(self.RAW[1])
        raw[-10] ^= 1                                  # change the coinbase output script
        with self.assertRaises(ValueError):
            scan_block(bytes(raw), 1, fetch)
        with self.assertRaises(ValueError):
            scan_block(self.RAW[2], 1, fetch)          # right format, wrong block

    def test_reply_found_in_a_block_and_hidden_ones_impossible(self):
        coinbase = synthetic_tx([b'\x51'])
        reply_tx = synthetic_tx([b'\x00\x14' + b'\x33' * 20, op_return_script(payload(ANSWER_HASH))], segwit=True)
        header, raw = synthetic_block([coinbase, reply_tx])
        fake = {5: (chain.header_hash(header), header)}
        found = scan_block(raw, 5, lambda h: fake[h])
        self.assertEqual(found, [(parse_tx(reply_tx)['txid'], [ANSWER_HASH])])
        dropped = header + b'\x01' + coinbase           # the same header with the reply removed
        with self.assertRaises(ValueError):
            scan_block(dropped, 5, lambda h: fake[h])

    def test_scan_range_judges_what_it_finds(self):
        coinbase = synthetic_tx([b'\x51'])
        reply_tx = synthetic_tx([op_return_script(payload(ANSWER_HASH))])
        header, raw = synthetic_block([coinbase, reply_tx])
        both = dict(HEADERS)
        both[5] = (chain.header_hash(header), header)
        r = scan_range(5, 5, TIP, lambda h: both[h], lambda h: raw, locate, descent=False)
        self.assertEqual(r['replies'][0]['answer_height'], ANSWER)
        self.assertIn('NOT CHECKED', r['replies'][0]['descent'])
        r = scan_range(5, 5, TIP, lambda h: both.get(h, HEADERS[977061]), lambda h: raw, locate, descent=True)
        self.assertIn('does not descend', r['replies'][0]['rejected'])   # block 5 here is no real ancestor


class SimulatedRun(unittest.TestCase):
    """A full mock run on a synthetic chain (simulate.py): every attack must fail, as expected."""

    @classmethod
    def setUpClass(cls):
        cls.res = simulate.run(seed=3, n_guesses=160)

    def outcomes(self, name):
        return [simulate.outcome(r) for r in self.res[name]]

    def test_random_guesses_stay_pending(self):
        o = self.outcomes('random guesses')
        self.assertGreater(len(o), 50)
        self.assertEqual(set(o), {'pending'})

    def test_copies_of_earlier_blocks_are_rejected(self):
        for name in ('copy-cat (names an earlier block)', 'reversed byte order of an earlier block',
                     'payload in an input scriptSig'):
            self.assertEqual(self.outcomes(name), ['rejected'], name)
            self.assertIn('anchored in block', self.res[name][0]['rejected'])

    def test_witness_payload_is_invisible(self):
        self.assertEqual(self.res['payload hidden in a witness'], [])

    def test_history_rewrite_fails(self):
        self.assertEqual(self.outcomes('history rewritten to name a block already seen'), ['rejected'])

    def test_lying_explorers_fail(self):
        self.assertIn('descend', self.res['explorers serve a private block as a descendant'][0]['rejected'])

    def test_block_bodies_cannot_hide_or_lose_replies(self):
        self.assertEqual(self.outcomes('duplicated transactions (merkle mutation)'), ['nothing hidden'])
        self.assertIn('merkle root', self.res['tampered block served to the scanner'][0]['error'])

    def test_window_verdicts(self):
        self.assertTrue(self.res['_window']['verdict'].startswith('closed: no valid'))
        self.assertEqual(self.res['_window_indexed']['verdict'], self.res['_window']['verdict'])
        self.assertTrue(self.res['_window_early']['verdict'].startswith('open'))


def check_text_reply(anchor, fetch_fn=fetch):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / 'reply.txt'
        p.write_text(text_line(ANSWER_HASH), encoding='utf-8')
        return check_text(p, anchor, TIP, fetch_fn, locate)


def check_descent_result(fetch_fn):
    return check_text_reply(ANSWER - MIN_LEAD, fetch_fn)


class RulePredictions(unittest.TestCase):
    """Conditional on a time machine whose past end reaches the present."""

    N = 64

    def models(self, k=6, r=200):
        return [predictions.model(self.N, r, seed) for seed in range(k)]

    def test_no_loop_only_hoaxes_correct_by_chance(self):
        c = np.mean([predictions.no_loop(g)['correct_if_arrives'] for g in self.models(10)])
        self.assertAlmostEqual(c, 1 / self.N, delta=0.004)

    def test_p_ctc_every_arrival_is_correct_and_arrivals_follow_willingness(self):
        for s in (1.0, 0.5, 0.1):
            out = [predictions.p_ctc(g, s) for g in self.models()]
            self.assertTrue(all(o['correct_if_arrives'] == 1.0 for o in out))
            self.assertAlmostEqual(np.mean([o['arrives'] for o in out]), s, delta=0.06)

    def test_pps_unrecorded_mining_equals_p_ctc(self):
        g = predictions.model(self.N, 200, 1)
        self.assertEqual(predictions.pps(g, 0.5, mining_recorded=False), predictions.p_ctc(g, 0.5))

    def test_d_ctc_messages_arrive_but_are_random(self):
        for s in (1.0, 0.5):
            out = [predictions.d_ctc(g, s) for g in self.models()]
            self.assertAlmostEqual(np.mean([o['arrives'] for o in out]), s, delta=0.01)
            self.assertAlmostEqual(np.mean([o['correct_if_arrives'] for o in out]), 1 / self.N, delta=0.005)

    def test_d_ctc_fixed_point_is_unique(self):
        t = predictions.transition(predictions.model(32, 100, 3), 0.5)
        ev = sorted(np.abs(np.linalg.eigvals(t)))[::-1]
        self.assertAlmostEqual(ev[0], 1.0, places=10)
        self.assertLess(ev[1], 0.5)
        tau = predictions.cesaro(t)
        self.assertLess(np.max(np.abs(t @ tau - tau)), 1e-3)

    def test_pps_recorded_mining(self):
        """Always-willing sender: correct only in worlds with a consistent message (about 63%).
        Partly willing: "nothing arrives" is always consistent, so every arrival is correct."""
        n = self.N
        full = [predictions.pps(g, 1.0, mining_recorded=True) for g in self.models(3, 400)]
        self.assertAlmostEqual(np.mean([o['correct_if_arrives'] for o in full]), 1 - (1 - 1 / n) ** n, delta=0.05)
        half = predictions.pps(predictions.model(n, 400, 0), 0.5, mining_recorded=True)
        self.assertEqual(half['correct_if_arrives'], 1.0)
        self.assertLess(half['arrives'], 0.5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
