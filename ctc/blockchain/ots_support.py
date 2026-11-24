"""SPDX-License-Identifier: MIT. OpenTimestamps: free Bitcoin timestamps, no wallet needed.

`ots stamp` sends only a SHA-256 digest (plus a random nonce) to public calendar servers, which
aggregate many digests into one Bitcoin transaction. A few hours later `ots upgrade` fetches the
completed proof: a chain of hash operations from the file digest to the merkle root of a
Bitcoin block header. We check that merkle root against headers verified in chain.py, so no
Bitcoin node and no trust in the calendars is needed.

Needs the `opentimestamps-client` package (provides the `ots` command and the parser).
"""
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys


def ots_command():
    local = Path(sys.executable).parent / ('ots.exe' if sys.platform == 'win32' else 'ots')
    found = str(local) if local.exists() else shutil.which('ots')
    if not found:
        raise RuntimeError('the `ots` command is missing: pip install opentimestamps-client')
    return found


def stamp(path):
    """Create <path>.ots (refuses to overwrite)."""
    path = Path(path)
    if Path(str(path) + '.ots').exists():
        raise FileExistsError(f'{path}.ots already exists')
    subprocess.run([ots_command(), 'stamp', str(path)], check=True)


def upgrade(ots_path):
    """Try to complete a pending proof. Returns True if the call reported success."""
    return subprocess.run([ots_command(), 'upgrade', str(ots_path)]).returncode == 0


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
