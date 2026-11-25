"""SPDX-License-Identifier: MIT. Plain-text public witness of the one commitment (Internet Archive).

Why: an OpenTimestamps proof shows that *some* data existed, but the proof path can hide a merkle
tree. One stamp could cover a billion guess sets, and the best could be revealed afterwards.
The defence is to publish the commitment itself, in plain text, at a URL fixed in the
preregistration, and let the Internet Archive capture it. The first capture of that URL is
the commitment; later edits do not count.

Usage (from the repository root), after pushing public/commitment.txt to the witness URL:
  python -B ctc/blockchain/witness.py
"""
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import sys
import time
import urllib.parse
import urllib.request

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
USER_AGENT = 'causal-loops-lab-verifier/1'


def _get(url, timeout=60):
    """Body of a URL, decoded if the server sent it gzip-compressed.

    The Internet Archive replays a capture with its original Content-Encoding, so the raw
    bytes of a gzip-served page are compressed; comparing them unopened with the file would
    fail (found 2026-11-25 on the invitation's first capture).
    """
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
        if (r.headers.get('Content-Encoding') or '').lower() == 'gzip':
            body = gzip.decompress(body)
        return body


def request_capture(url):
    _get('https://web.archive.org/save/' + url, timeout=180)


def first_capture(url):
    """(capture time as unix seconds, captured bytes) of the earliest HTTP-200 capture, or None."""
    query = urllib.parse.urlencode(dict(url=url, output='json', fl='timestamp,statuscode',
                                        filter='statuscode:200'))
    rows = json.loads(_get('https://web.archive.org/cdx/search/cdx?' + query) or b'[]')
    if len(rows) < 2:
        return None
    stamp = min(r[0] for r in rows[1:])
    when = datetime.strptime(stamp, '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc).timestamp()
    return when, _get(f'https://web.archive.org/web/{stamp}id_/{url}')


def committed_value(text):
    for line in text.splitlines():
        if line.startswith('commitment: '):
            return line.split(': ', 1)[1].strip()
    return None


def check_witness(url, commitment, deadline, capture=first_capture):
    """Raise ValueError unless the first capture of `url` holds `commitment` and predates `deadline`."""
    found = capture(url)
    if found is None:
        raise ValueError(f'no Internet Archive capture of {url}')
    when, body = found
    value = committed_value(body.decode('utf-8', 'replace'))
    if value != commitment:
        raise ValueError(f'first capture of {url} holds {value}, not {commitment}')
    if when >= deadline:
        raise ValueError(f'first capture at {when:.0f} is not before the deadline {deadline:.0f}')
    return when


def main():
    import preregister
    _, params = preregister.check()
    if params is None:
        sys.exit('PREREGISTRATION.md / params.json missing or out of date')
    url = params['witness_url']
    local = committed_value((HERE / 'public' / 'commitment.txt').read_text(encoding='utf-8'))
    online = committed_value(_get(url).decode('utf-8', 'replace'))
    if online != local:
        sys.exit(f'{url} does not serve the local commitment yet (push it first)')
    existing = first_capture(url)
    if existing is None:
        print(f'asking the Internet Archive to capture {url}')
        request_capture(url)
        for _ in range(30):
            time.sleep(20)
            existing = first_capture(url)
            if existing:
                break
    if existing is None:
        sys.exit('no capture yet; run again in a few minutes')
    when, body = existing
    ok = committed_value(body.decode('utf-8', 'replace')) == local
    stamp = datetime.fromtimestamp(when, timezone.utc).isoformat()
    print(f'first capture {stamp}: {"holds the commitment" if ok else "DOES NOT hold the commitment"}')
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
