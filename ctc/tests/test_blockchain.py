"""SPDX-License-Identifier: MIT. Offline checks for the loop lottery in ctc/blockchain/.

Uses real Bitcoin headers saved in ctc/tests/fixtures/btc_headers.json (blocks 0-2 and
977060-977067), so no network is needed. Each known loophole has a test showing the attack is
caught. OpenTimestamps parsing is tested only if the opentimestamps package is installed.

Run from the repository root:  python -B ctc/tests/test_blockchain.py
"""
import json
import math
from pathlib import Path
import random
import shutil
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'blockchain'))
import chain  # noqa: E402
import preregister  # noqa: E402
from protocol import (FIVE_SIGMA, K_BITS, N_TRIALS, PROTOCOL, analyze, answers, binom_sf, chance_table,  # noqa: E402
                      commitment, derive_bits, guess_hex, make_params, send_flags)
from send import loop_messages  # noqa: E402
import verify  # noqa: E402

FIXTURE = {int(h): (b, bytes.fromhex(hd)) for h, (b, hd) in
           json.loads((HERE / 'fixtures' / 'btc_headers.json').read_text()).items()}
B_C, ANSWER_HEIGHT = 977060, 977066          # B_c = ANSWER_HEIGHT - MIN_LEAD: the latest allowed
URL = 'https://example.org/commitment.txt'


def fixture_fetch(height):
    return FIXTURE[height]


class Statistics(unittest.TestCase):
    def test_binomial_tail_matches_brute_force(self):
        for n, p in ((10, 0.3), (20, 0.5), (7, 0.01)):
            for x in range(n + 2):
                brute = sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(x, n + 1))
                self.assertAlmostEqual(binom_sf(x, n, p), brute, places=12)

    def test_tiny_probabilities(self):
        p = 2.0 ** -32
        self.assertAlmostEqual(binom_sf(1, 32, p) / (32 * p), 1.0, places=6)
        self.assertLess(binom_sf(1, 32, p), FIVE_SIGMA)          # one exact match is decisive
        self.assertEqual(next(r for r in chance_table() if r['k'] == 32)['hits_needed'], 1)
        self.assertGreater(next(r for r in chance_table() if r['k'] == 8)['hits_needed'], 1)

    def test_biased_guesses_do_not_change_chance(self):
        """Answers are uniform, so even all-zero guesses match each bit with probability 1/2."""
        a = answers(FIXTURE[977066][0])
        r = analyze([0] * N_TRIALS, a, [True] * N_TRIALS)
        self.assertGreater(r['sent']['bit_p_value'], 1e-3)


class Derivation(unittest.TestCase):
    def test_bits_are_deterministic_in_range_and_index_dependent(self):
        h = FIXTURE[977066][0]
        a = [derive_bits('t', h, i, K_BITS) for i in range(N_TRIALS)]
        self.assertEqual(a, [derive_bits('t', h, i, K_BITS) for i in range(N_TRIALS)])
        self.assertTrue(all(0 <= v < 2 ** K_BITS for v in a))
        self.assertEqual(len(set(a)), N_TRIALS)
        self.assertNotEqual(answers(h), answers(FIXTURE[977067][0]))

    def test_send_flags_are_roughly_balanced(self):
        s = send_flags(FIXTURE[977067][0])
        self.assertEqual(len(s), N_TRIALS)
        self.assertTrue(16 <= sum(s) <= 48)

    def test_commitment_detects_any_change(self):
        reveal = dict(protocol=PROTOCOL, guesses=['00000000'] * 3, salt='ab' * 32)
        c = commitment(reveal)
        changed = dict(reveal, guesses=['00000001', '00000000', '00000000'])
        self.assertNotEqual(c, commitment(changed))
        self.assertEqual(c, commitment(json.loads(json.dumps(reveal))))


class Chain(unittest.TestCase):
    def test_real_headers_verify(self):
        chain.verified_range(0, 2, fixture_fetch)
        chain.verified_range(B_C, ANSWER_HEIGHT + 1, fixture_fetch)

    def test_tampering_is_caught(self):
        h, header = FIXTURE[977062]
        bad = bytearray(header)
        bad[40] ^= 1                                   # flip a merkle-root bit
        with self.assertRaises(ValueError):
            chain.check_header(bytes(bad), h, 977062)
        broken = dict(FIXTURE)
        broken[977063] = FIXTURE[977065]               # valid block, wrong place in the chain
        with self.assertRaises(ValueError):
            chain.verified_range(B_C, ANSWER_HEIGHT + 1, lambda x: broken[x])

    def test_low_difficulty_rejected_for_recent_heights(self):
        h, header = FIXTURE[1]                        # real 2009 block, legitimately easy
        with self.assertRaises(ValueError):
            chain.check_header(header, h, 977000)


class EndToEnd(unittest.TestCase):
    """Full protocol offline: preregistration, commitment, witness, sending, reveal, verification."""

    def setup_run(self, guesses, capture_offset=-3 * 3600, capture_commitment=None, b_c=B_C):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        params = make_params(ANSWER_HEIGHT, URL)
        (tmp / 'params.json').write_text(json.dumps(params), encoding='utf-8')
        prereg = preregister.text(params)
        (tmp / 'PREREGISTRATION.md').write_text(prereg, encoding='utf-8', newline='\n')
        reveal = dict(protocol=PROTOCOL, preregistration_sha256=preregister.sha256_hex(prereg.encode('utf-8')),
                      n_trials=N_TRIALS, k_bits=K_BITS, guesses=[guess_hex(g) for g in guesses],
                      salt='11' * 32, guess_source=dict(type='test'), created_utc='2026-11-23T00:00:00+00:00')
        public = tmp / 'public'
        public.mkdir()
        c = commitment(reveal)
        (public / 'reveal.json').write_text(json.dumps(reveal), encoding='utf-8')
        (public / 'commitment.txt').write_text(f'commitment: {c}\n', encoding='utf-8')
        headers = chain.verified_range(min(b_c, B_C), ANSWER_HEIGHT + 1, fixture_fetch)
        (public / 'loop_messages.json').write_text(json.dumps(loop_messages(b_c, headers, params)),
                                                   encoding='utf-8')
        answer_time = chain.timestamp(FIXTURE[ANSWER_HEIGHT][1])
        witnessed = capture_commitment or c
        self.capture = lambda url: None if capture_offset is None else (
            answer_time + capture_offset, f'commitment: {witnessed}\n'.encode())
        self.b_c = b_c
        return tmp

    def run_verify(self, base):
        return verify.verify(base, fixture_fetch, commitment_block=self.b_c, capture=self.capture)

    def random_guesses(self, seed):
        rng = random.Random(seed)
        return [rng.getrandbits(K_BITS) for _ in range(N_TRIALS)]

    def test_random_guesses_give_chance(self):
        r = self.run_verify(self.setup_run(self.random_guesses(1)))
        self.assertFalse(r['analysis']['primary_reject_chance'])
        self.assertTrue(r['analysis']['control_clean'])
        self.assertIn('No evidence', verify.report(r))

    def test_perfect_loop_would_be_detected(self):
        a, s = answers(FIXTURE[ANSWER_HEIGHT][0]), send_flags(FIXTURE[ANSWER_HEIGHT + 1][0])
        rng = random.Random(2)
        r = self.run_verify(self.setup_run([a[i] if s[i] else rng.getrandbits(K_BITS) for i in range(N_TRIALS)]))
        self.assertTrue(r['analysis']['primary_reject_chance'])
        self.assertEqual(r['analysis']['sent']['exact_matches'], sum(s))
        self.assertTrue(r['analysis']['control_clean'])

    def test_single_hit_passes_five_sigma(self):
        a, s = answers(FIXTURE[ANSWER_HEIGHT][0]), send_flags(FIXTURE[ANSWER_HEIGHT + 1][0])
        guesses = [a[i] ^ 0xFFFFFFFF for i in range(N_TRIALS)]
        guesses[s.index(True)] = a[s.index(True)]
        r = self.run_verify(self.setup_run(guesses))
        self.assertEqual(r['analysis']['sent']['exact_matches'], 1)
        self.assertTrue(r['analysis']['primary_reject_chance'])

    # ---- attacks -------------------------------------------------------------------------

    def test_attack_swap_guesses_after_commit(self):
        base = self.setup_run(self.random_guesses(3))
        reveal = json.loads((base / 'public' / 'reveal.json').read_text())
        reveal['guesses'][0] = 'deadbeef'
        (base / 'public' / 'reveal.json').write_text(json.dumps(reveal))
        with self.assertRaises(verify.CheckFailed):
            self.run_verify(base)

    def test_attack_change_rules_after_commit(self):
        base = self.setup_run(self.random_guesses(4))
        with open(base / 'PREREGISTRATION.md', 'a', encoding='utf-8') as f:
            f.write('changed later\n')
        with self.assertRaises(verify.CheckFailed):
            self.run_verify(base)

    def test_attack_move_answer_block_in_params(self):
        base = self.setup_run(self.random_guesses(5))
        params = json.loads((base / 'params.json').read_text())
        params['answer_height'] -= 1
        params['send_height'] -= 1
        (base / 'params.json').write_text(json.dumps(params))
        with self.assertRaises(verify.CheckFailed):
            self.run_verify(base)

    def test_attack_rewrite_rules_and_params_together(self):
        """Regenerating a consistent preregistration with another answer block still fails: its hash
        is not the one inside the commitment."""
        base = self.setup_run(self.random_guesses(11))
        params = make_params(ANSWER_HEIGHT - 1, URL)
        (base / 'params.json').write_text(json.dumps(params))
        (base / 'PREREGISTRATION.md').write_text(preregister.text(params), encoding='utf-8', newline='\n')
        with self.assertRaisesRegex(verify.CheckFailed, 'differs from the committed one'):
            self.run_verify(base)

    def test_attack_reroll_by_late_restamp(self):
        """Re-stamping the commitment later cannot pick new answers: a late B_c voids the run."""
        with self.assertRaises(verify.CheckFailed):
            self.run_verify(self.setup_run(self.random_guesses(6), b_c=B_C + 1))

    def test_attack_merkle_tree_of_many_commitments(self):
        """One stamp over 2^30 hidden guess sets would make a fake hit almost certain; the plain-text
        witness pins the single published commitment, so revealing another set fails."""
        p_fake = -math.expm1(2 ** 30 * math.log1p(-binom_sf(1, 32, 2.0 ** -32)))
        self.assertGreater(p_fake, 0.99)
        base = self.setup_run(self.random_guesses(7), capture_commitment='0' * 64)
        with self.assertRaises(verify.CheckFailed):
            self.run_verify(base)

    def test_attack_witness_after_answer(self):
        base = self.setup_run(self.random_guesses(8), capture_offset=-3600)   # inside the 2 h margin
        with self.assertRaises(verify.CheckFailed):
            self.run_verify(base)

    def test_attack_no_witness(self):
        base = self.setup_run(self.random_guesses(9), capture_offset=None)
        with self.assertRaises(verify.CheckFailed):
            self.run_verify(base)

    def test_attack_forged_loop_messages(self):
        base = self.setup_run(self.random_guesses(10))
        msg = json.loads((base / 'public' / 'loop_messages.json').read_text())
        first = next(iter(msg['messages']))
        msg['messages'][first] = 'deadbeef'
        (base / 'public' / 'loop_messages.json').write_text(json.dumps(msg))
        with self.assertRaises(verify.CheckFailed):
            self.run_verify(base)


try:
    import opentimestamps  # noqa: F401
    HAVE_OTS = True
except ImportError:
    HAVE_OTS = False


@unittest.skipUnless(HAVE_OTS, 'opentimestamps not installed')
class OpenTimestamps(unittest.TestCase):
    def test_parse_synthetic_proof(self):
        """Build a proof by hand (file digest -> append -> sha256 -> Bitcoin attestation) and parse it."""
        import hashlib
        import io
        from opentimestamps.core.notary import BitcoinBlockHeaderAttestation
        from opentimestamps.core.op import OpAppend, OpSHA256
        from opentimestamps.core.serialize import StreamSerializationContext
        from opentimestamps.core.timestamp import DetachedTimestampFile, Timestamp
        from ots_support import attestations
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        f = tmp / 'commitment.txt'
        f.write_bytes(b'hello loop\n')
        digest = hashlib.sha256(f.read_bytes()).digest()
        ts = Timestamp(digest)
        root = ts.ops.add(OpAppend(b'\x01' * 16)).ops.add(OpSHA256())
        root.attestations.add(BitcoinBlockHeaderAttestation(977060))
        buf = io.BytesIO()
        DetachedTimestampFile(OpSHA256(), ts).serialize(StreamSerializationContext(buf))
        (tmp / 'commitment.txt.ots').write_bytes(buf.getvalue())
        bitcoin, pending = attestations(f, tmp / 'commitment.txt.ots')
        self.assertEqual(bitcoin, [(977060, hashlib.sha256(digest + b'\x01' * 16).digest())])
        self.assertEqual(pending, [])


if __name__ == '__main__':
    unittest.main(verbosity=1)
