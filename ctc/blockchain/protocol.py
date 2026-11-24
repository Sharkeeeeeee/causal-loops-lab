"""SPDX-License-Identifier: MIT. "Loop lottery": a retrocausal answer test anchored on Bitcoin.

Protocol (all parameters fixed in PREREGISTRATION.md and params.json before the run):
  1. Commit. Draw N guesses of K bits each (quantum random numbers from IBM hardware, or the
     OS generator). Hide them with a random salt, hash everything into one commitment, and
     timestamp the commitment on the Bitcoin blockchain with OpenTimestamps. Let B_c be the
     first Bitcoin block that contains the commitment; it must be at least MIN_LEAD blocks
     before the answer block, or the run is void.
  2. Witness. Publish the commitment in plain text at a preregistered URL and have the Internet
     Archive capture it. The first capture of that URL is the commitment; it must predate the
     answer block. (An OpenTimestamps proof alone could hide a merkle tree of many guess sets.)
  3. Answers. The answer to trial i is derived from the hash of the preregistered block
     ANSWER_HEIGHT, fixed before the guesses were drawn (so re-stamping cannot re-roll it):
        a_i = first K bits of SHA-256("<tag>|<block hash>|i").
  4. Send back. Whether trial i's answer is "sent back to the past" is decided by the
     preregistered block SEND_HEIGHT. For sent trials, a sender program publishes a_i and
     timestamps that message on Bitcoin. That is the loop: the message travels back to the
     guess, and the only self-consistent history is guess = answer.
  5. Check. Reveal guesses and salt; anyone can recompute every step (verify.py).

If a self-consistency rule could pull answers back from the future, sent trials would match.
Standard physics, and past-preserving selection (the committed guesses are a recorded past),
both predict chance: an exact 32-bit match has probability 2^-32 per trial.
"""
import hashlib
import json
import math

PROTOCOL = 'cll-loop-lottery-v2'
N_TRIALS = 64
K_BITS = 32
MIN_LEAD = 6                 # B_c must be at least this many blocks before ANSWER_HEIGHT
SEND_CONFIRMATIONS = 6       # send only after SEND_HEIGHT is buried this deep (reorg safety)
WITNESS_MARGIN = 7200        # seconds; Bitcoin timestamps may run up to 2 h ahead of real time
ANSWER_TAG = 'CLL-answer-v1'
SEND_TAG = 'CLL-send-v1'
FIVE_SIGMA = 2.866515718791939e-07     # one-sided p-value of a 5 sigma normal deviation
PARAM_KEYS = ('protocol', 'n_trials', 'k_bits', 'answer_height', 'send_height', 'min_lead',
              'send_confirmations', 'witness_url', 'witness_margin_seconds')


def make_params(answer_height, witness_url):
    return dict(protocol=PROTOCOL, n_trials=N_TRIALS, k_bits=K_BITS, answer_height=answer_height,
                send_height=answer_height + 1, min_lead=MIN_LEAD, send_confirmations=SEND_CONFIRMATIONS,
                witness_url=witness_url, witness_margin_seconds=WITNESS_MARGIN)


def check_params(params):
    if tuple(sorted(params)) != tuple(sorted(PARAM_KEYS)):
        raise ValueError(f'params.json keys differ: {sorted(params)}')
    if (params['protocol'], params['n_trials'], params['k_bits']) != (PROTOCOL, N_TRIALS, K_BITS):
        raise ValueError('params.json does not match this protocol version')
    if params['send_height'] != params['answer_height'] + 1:
        raise ValueError('send_height must be answer_height + 1')


def canonical(obj):
    """Deterministic JSON bytes (sorted keys, no spaces) used for every hash in the protocol."""
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def commitment(reveal):
    """The single value timestamped on Bitcoin."""
    return sha256_hex(canonical(reveal))


def derive_bits(tag, block_hash, index, k):
    """First k bits of SHA-256('<tag>|<block hash hex>|<index>') as an integer."""
    digest = hashlib.sha256(f'{tag}|{block_hash.lower()}|{index}'.encode('ascii')).digest()
    return int.from_bytes(digest, 'big') >> (256 - k)


def answers(block_hash, n=N_TRIALS, k=K_BITS):
    return [derive_bits(ANSWER_TAG, block_hash, i, k) for i in range(n)]


def send_flags(block_hash, n=N_TRIALS):
    return [bool(derive_bits(SEND_TAG, block_hash, i, 1)) for i in range(n)]


def guess_hex(value, k=K_BITS):
    return format(value, f'0{(k + 3) // 4}x')


def binom_sf(x, n, p):
    """Exact P(X >= x) for X ~ Binomial(n, p), summed in log space (fine for p as small as 2^-64)."""
    if x <= 0:
        return 1.0
    if x > n:
        return 0.0
    log_terms = [math.lgamma(n + 1) - math.lgamma(j + 1) - math.lgamma(n - j + 1)
                 + j * math.log(p) + (n - j) * math.log1p(-p) for j in range(x, n + 1)]
    top = max(log_terms)
    return math.exp(top) * sum(math.exp(t - top) for t in log_terms)


def matching_bits(a, b, k=K_BITS):
    return k - bin((a ^ b) & ((1 << k) - 1)).count('1')


def analyze(guesses, answer_values, sent, k=K_BITS, alpha=FIVE_SIGMA):
    """Preregistered analysis. Primary: exact matches among sent trials vs Binomial(n_sent, 2^-k).
    Secondary: matching bits among sent trials vs Binomial(k * n_sent, 1/2). Control: the same
    for unsent trials, where every hypothesis predicts chance."""
    out = {}
    for arm, flag in (('sent', True), ('unsent', False)):
        idx = [i for i, s in enumerate(sent) if s == flag]
        exact = sum(guesses[i] == answer_values[i] for i in idx)
        bits = sum(matching_bits(guesses[i], answer_values[i], k) for i in idx)
        out[arm] = dict(trials=len(idx), exact_matches=exact,
                        exact_p_value=binom_sf(exact, len(idx), 2.0 ** -k),
                        expected_exact_by_chance=len(idx) * 2.0 ** -k,
                        matching_bits=bits, total_bits=k * len(idx),
                        bit_p_value=binom_sf(bits, k * len(idx), 0.5))
    s = out['sent']
    out['primary_reject_chance'] = s['exact_p_value'] < alpha
    out['secondary_reject_chance'] = s['bit_p_value'] < alpha
    out['control_clean'] = out['unsent']['exact_p_value'] >= alpha and out['unsent']['bit_p_value'] >= alpha
    out['alpha'] = alpha
    return out


def chance_table(n_sent=N_TRIALS // 2, ks=(8, 16, 24, 32, 64)):
    """P(at least one exact match by pure chance) and the hits needed to pass 5 sigma."""
    rows = []
    for k in ks:
        p = 2.0 ** -k
        need = next(x for x in range(n_sent + 2) if binom_sf(x, n_sent, p) < FIVE_SIGMA)
        rows.append(dict(k=k, per_trial=p, at_least_one=binom_sf(1, n_sent, p), hits_needed=need))
    return rows
