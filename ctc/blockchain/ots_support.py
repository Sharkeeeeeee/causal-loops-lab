"""SPDX-License-Identifier: MIT. OpenTimestamps: free Bitcoin timestamps, no wallet needed.

`ots stamp` sends only a SHA-256 digest (plus a random nonce) to public calendar servers, which
aggregate many digests into one Bitcoin transaction. A few hours later `ots upgrade` fetches the
completed proof: a chain of hash operations from the file digest to the merkle root of a
Bitcoin block header. We check that merkle root against headers verified in chain.py, so no
Bitcoin node and no trust in the calendars is needed.

Needs the `opentimestamps-client` package (it installs the `opentimestamps` library used here).
Stamping and upgrading call the library directly, doing what `ots stamp` and `ots upgrade` do,
because the `ots` command fails to start on Windows: python-bitcoinlib, which it imports, looks
for an OpenSSL DLL that a standard Windows Python does not ship (found 2026-11-25).
"""
import hashlib
import os
from pathlib import Path
import shutil
import sys

# The default calendars of `ots stamp` (opentimestamps-client 0.8.0).
CALENDARS = ('https://a.pool.opentimestamps.org', 'https://b.pool.opentimestamps.org',
             'https://a.pool.eternitywall.com', 'https://ots.btc.catallaxy.com')


def ots_command():
    local = Path(sys.executable).parent / ('ots.exe' if sys.platform == 'win32' else 'ots')
    found = str(local) if local.exists() else shutil.which('ots')
    if not found:
        raise RuntimeError('the `ots` command is missing: pip install opentimestamps-client')
    return found


def stamp(path, calendars=CALENDARS, minimum=2, timeout=15):
    """Create <path>.ots as `ots stamp` does (refuses to overwrite).

    The file digest gets a fresh 16-byte nonce and is hashed again, so a calendar learns
    nothing about the file. That commitment is sent to each calendar; at least `minimum` must
    answer. Returns (calendars that answered, errors).
    """
    from opentimestamps.calendar import RemoteCalendar
    from opentimestamps.core.op import OpAppend, OpSHA256
    from opentimestamps.core.serialize import StreamSerializationContext
    from opentimestamps.core.timestamp import DetachedTimestampFile

    path = Path(path)
    out = Path(str(path) + '.ots')
    if out.exists():
        raise FileExistsError(f'{out} already exists')
    with open(path, 'rb') as fd:
        detached = DetachedTimestampFile.from_fd(OpSHA256(), fd)
    tip = detached.timestamp.ops.add(OpAppend(os.urandom(16))).ops.add(OpSHA256())
    answered, errors = [], []
    for url in calendars:
        try:
            tip.merge(RemoteCalendar(url).submit(tip.msg, timeout=timeout))
            answered.append(url)
        except Exception as ex:
            errors.append(f'{url}: {type(ex).__name__}: {ex}')
    if len(answered) < minimum:
        raise RuntimeError(f'only {len(answered)} calendar(s) answered: {errors}')
    with open(out, 'xb') as fd:
        detached.serialize(StreamSerializationContext(fd))
    return answered, errors


def upgrade(ots_path, timeout=15):
    """Ask the calendars for the completed proof, as `ots upgrade` does.

    Only calendars on the library's default whitelist are contacted. The file is rewritten only
    if something new arrived. Returns True once the proof contains a Bitcoin attestation.
    """
    from opentimestamps.calendar import DEFAULT_CALENDAR_WHITELIST, RemoteCalendar
    from opentimestamps.core.notary import BitcoinBlockHeaderAttestation, PendingAttestation
    from opentimestamps.core.serialize import StreamDeserializationContext, StreamSerializationContext
    from opentimestamps.core.timestamp import DetachedTimestampFile

    with open(ots_path, 'rb') as fd:
        detached = DetachedTimestampFile.deserialize(StreamDeserializationContext(fd))

    def walk(stamp_):
        yield stamp_
        for sub in stamp_.ops.values():
            yield from walk(sub)

    changed = False
    for sub in list(walk(detached.timestamp)):
        for att in list(sub.attestations):
            if isinstance(att, PendingAttestation) and att.uri in DEFAULT_CALENDAR_WHITELIST:
                try:
                    upgraded = RemoteCalendar(att.uri).get_timestamp(sub.msg, timeout=timeout)
                except Exception:
                    continue                       # not ready yet, or the calendar is unreachable
                before = {a for _, a in sub.all_attestations()}
                sub.merge(upgraded)
                changed |= {a for _, a in sub.all_attestations()} != before
    if changed:
        tmp = Path(str(ots_path) + '.tmp')
        with open(tmp, 'wb') as fd:
            detached.serialize(StreamSerializationContext(fd))
        os.replace(tmp, ots_path)
    return any(isinstance(a, BitcoinBlockHeaderAttestation) for _, a in detached.timestamp.all_attestations())


def attestations(path, ots_path):
    """(bitcoin [(height, merkle_root_bytes)], pending [calendar uri]) for a stamped file."""
    from opentimestamps.core.notary import BitcoinBlockHeaderAttestation, PendingAttestation
    from opentimestamps.core.op import OpSHA256
    from opentimestamps.core.serialize import StreamDeserializationContext
    from opentimestamps.core.timestamp import DetachedTimestampFile

    with open(ots_path, 'rb') as fd:
        detached = DetachedTimestampFile.deserialize(StreamDeserializationContext(fd))
    if not isinstance(detached.file_hash_op, OpSHA256):
        raise ValueError('timestamp does not use SHA-256')
    if detached.file_digest != hashlib.sha256(Path(path).read_bytes()).digest():
        raise ValueError(f'{ots_path} does not belong to {path}')
    bitcoin, pending = [], []
    for msg, att in detached.timestamp.all_attestations():
        if isinstance(att, BitcoinBlockHeaderAttestation):
            bitcoin.append((att.height, bytes(msg)))
        elif isinstance(att, PendingAttestation):
            pending.append(att.uri)
    return sorted(bitcoin), pending


def first_verified_block(path, ots_path, fetch):
    """Lowest Bitcoin height whose verified header carries this file's merkle root, or None."""
    from chain import check_header, merkle_root
    bitcoin, _ = attestations(path, ots_path)
    for height, root in bitcoin:
        block_hash, header = fetch(height)
        check_header(header, block_hash, height)
        if merkle_root(header) == root:
            return height
    return None
