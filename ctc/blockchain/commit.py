"""SPDX-License-Identifier: MIT. Step 1: draw the guesses, commit to them, timestamp on Bitcoin.

Usage (from the repository root):
  python -B ctc/blockchain/commit.py [--source ibm|os] [--backend NAME]

Writes ctc/blockchain/private/reveal.json (secret until reveal.py; git-ignored) and
ctc/blockchain/public/commitment.txt with its OpenTimestamps proof. Runs only once.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import secrets
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import preregister  # noqa: E402
from ots_support import stamp  # noqa: E402
from protocol import K_BITS, N_TRIALS, PROTOCOL, commitment, guess_hex  # noqa: E402

PRIVATE, PUBLIC = HERE / 'private', HERE / 'public'


def quantum_guesses(backend_name=None):
    """N_TRIALS shots of K_BITS qubits in |+>, measured: one K-bit quantum random number per shot."""
    from qiskit import QuantumCircuit
    from qiskit.transpiler import generate_preset_pass_manager
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    service = QiskitRuntimeService()
    backend = service.backend(backend_name) if backend_name else service.least_busy(operational=True,
                                                                                      simulator=False)
    qc = QuantumCircuit(K_BITS, K_BITS)
    qc.h(range(K_BITS))
    qc.measure(range(K_BITS), range(K_BITS))
    isa = generate_preset_pass_manager(backend=backend, optimization_level=1).run(qc)
    job = SamplerV2(mode=backend).run([isa], shots=N_TRIALS)
    print(f'quantum guesses: job {job.job_id()} on {backend.name}')
    shots = job.result()[0].data.c.get_bitstrings()
    return [int(b, 2) for b in shots], dict(type='ibm-quantum', backend=backend.name, job_id=job.job_id(),
                                            circuit=f'{K_BITS} qubits, H then measure, {N_TRIALS} shots')


def os_guesses():
    return [secrets.randbits(K_BITS) for _ in range(N_TRIALS)], dict(type='os-csprng (python secrets)')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', choices=('ibm', 'os'), default='ibm')
    parser.add_argument('--backend')
    args = parser.parse_args()

    prereg, params = preregister.check()
    if prereg is None:
        sys.exit('PREREGISTRATION.md / params.json missing or out of date: run preregister.py --answer-height H')
    from chain import tip_height
    lead = params['answer_height'] - tip_height()
    if lead < 3 * params['min_lead']:
        sys.exit(f'answer block {params["answer_height"]} is only {lead} blocks away: preregister a later height')
    if (PUBLIC / 'commitment.txt').exists() or (PRIVATE / 'reveal.json').exists():
        sys.exit('a commitment already exists: the protocol allows exactly one')

    values, source = quantum_guesses(args.backend) if args.source == 'ibm' else os_guesses()
    if len(values) != N_TRIALS:
        sys.exit(f'expected {N_TRIALS} guesses, got {len(values)}')
    reveal = dict(protocol=PROTOCOL, preregistration_sha256=prereg, n_trials=N_TRIALS, k_bits=K_BITS,
                  guesses=[guess_hex(v) for v in values], salt=secrets.token_hex(32), guess_source=source,
                  created_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'))
    c = commitment(reveal)

    PRIVATE.mkdir(exist_ok=True)
    PUBLIC.mkdir(exist_ok=True)
    (PRIVATE / 'reveal.json').write_text(json.dumps(reveal, indent=1, sort_keys=True), encoding='utf-8')
    (PUBLIC / 'commitment.txt').write_text(
        f'protocol: {PROTOCOL}\ncommitment: {c}\npreregistration_sha256: {prereg}\n'
        f'created_utc: {reveal["created_utc"]}\n'
        'The guesses behind this commitment stay secret until public/loop_messages.json is published.\n',
        encoding='utf-8', newline='\n')
    stamp(PUBLIC / 'commitment.txt')
    print(f'commitment {c}')
    print('timestamp submitted. Now, well before the answer block:')
    print(f'  1. push public/commitment.txt (and .ots) so it is served at {params["witness_url"]}')
    print('  2. run witness.py so the Internet Archive captures it')
    print('Keep private/reveal.json safe. Run send.py after the send block has confirmations.')


if __name__ == '__main__':
    main()
