"""SPDX-License-Identifier: MIT. Bitcoin block headers, checked from first principles.

Every header is fetched from two independent public explorers and must agree byte for byte.
Then the verifier recomputes each block hash (double SHA-256), checks its proof of work
against the target encoded in the header, and checks that each header points to the previous
one. So the order of blocks rests on Bitcoin's proof of work, not on trusting an explorer.
"""
import hashlib
import json
import time
import urllib.error
import urllib.request

EXPLORERS = ('https://mempool.space/api', 'https://blockstream.info/api')
USER_AGENT = 'causal-loops-lab-verifier/1'
RECENT_HEIGHT = 900000          # blocks above this height must carry modern difficulty
RECENT_MAX_TARGET = 1 << 182    # sanity floor: today's targets are around 2^177 (32x margin)


RETRIES = 5                     # transient failures (timeouts, 429, 5xx) are retried with backoff


def transient(ex):
    """Worth retrying: timeouts, connection trouble, rate limits and server errors (not 404)."""
    if isinstance(ex, urllib.error.HTTPError):
        return ex.code == 429 or ex.code >= 500
    return isinstance(ex, (urllib.error.URLError, TimeoutError, ConnectionError, OSError))


def with_retries(call, retries=RETRIES, wait=2.0, sleep=time.sleep):
    for attempt in range(retries + 1):
        try:
            return call()
        except Exception as ex:
            if attempt == retries or not transient(ex):
                raise
            sleep(wait * 2 ** attempt)


def _get(url):
    def call():
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode('ascii').strip()
    return with_retries(call)


def tip_height():
    heights = {int(_get(f'{e}/blocks/tip/height')) for e in EXPLORERS}
    return min(heights)


def fetch_header(height):
    """(block hash hex, header bytes) at a height; every explorer must return the same."""
    seen = set()
    for e in EXPLORERS:
        block_hash = _get(f'{e}/block-height/{height}')
        header = _get(f'{e}/block/{block_hash}/header')
        seen.add((block_hash.lower(), header.lower()))
    if len(seen) != 1:
        raise ValueError(f'explorers disagree at height {height}: {seen}')
    block_hash, header = seen.pop()
    return block_hash, bytes.fromhex(header)


def header_hash(header):
    """Block hash in the usual display order (big-endian hex)."""
    return hashlib.sha256(hashlib.sha256(header).digest()).digest()[::-1].hex()


def prev_hash(header):
    return header[4:36][::-1].hex()


def merkle_root(header):
    """Merkle root in internal byte order, as OpenTimestamps attests it."""
    return header[36:68]


def timestamp(header):
    return int.from_bytes(header[68:72], 'little')


def target(header):
    bits = int.from_bytes(header[72:76], 'little')
    exponent, mantissa = bits >> 24, bits & 0xFFFFFF
    return mantissa << (8 * (exponent - 3))


def check_header(header, expected_hash, height):
    if len(header) != 80:
        raise ValueError(f'header at {height} has {len(header)} bytes')
    h = header_hash(header)
    if h != expected_hash.lower():
        raise ValueError(f'header at {height} hashes to {h}, explorer said {expected_hash}')
    if int(h, 16) > target(header):
        raise ValueError(f'block {height} fails proof of work')
    if height > RECENT_HEIGHT and target(header) > RECENT_MAX_TARGET:
        raise ValueError(f'block {height} has implausibly low difficulty')


def verified_range(first, last, fetch=fetch_header):
    """Fetch and verify headers first..last; returns {height: (hash, header)}."""
    out = {}
    for height in range(first, last + 1):
        block_hash, header = fetch(height)
        check_header(header, block_hash, height)
        if height - 1 in out and prev_hash(header) != out[height - 1][0]:
            raise ValueError(f'block {height} does not point to block {height - 1}')
        out[height] = (block_hash, header)
    return out


def save_headers(headers, path):
    path.write_text(json.dumps({str(h): [b, hd.hex()] for h, (b, hd) in sorted(headers.items())}, indent=1),
                    encoding='utf-8')
