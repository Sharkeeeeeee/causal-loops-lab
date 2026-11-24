"""SPDX-License-Identifier: MIT. Step 5: check everything from scratch and apply the decision rules.

Usage (from the repository root):  python -B ctc/blockchain/verify.py
Anyone can run this with the files in ctc/blockchain/ and an internet connection.
Writes public/report.md and public/report.json.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from chain import fetch_header, timestamp, verified_range  # noqa: E402
from protocol import K_BITS, N_TRIALS, PROTOCOL, analyze, answers, check_params, commitment, sha256_hex, send_flags  # noqa: E402,E501
from witness import check_witness, committed_value, first_capture  # noqa: E402


class CheckFailed(Exception):
    pass


def require(condition, message):
    if not condition:
        raise CheckFailed(message)


def verify(base, fetch=fetch_header, commitment_block=None, capture=first_capture):
    """Run every check on base/{PREREGISTRATION.md, params.json, public/}. `commitment_block`
    overrides the OpenTimestamps lookup (tests only)."""
    import preregister
    public = base / 'public'
    checks = []
    params = json.loads((base / 'params.json').read_text(encoding='utf-8'))
    try:
        check_params(params)
    except ValueError as e:
        raise CheckFailed(str(e))
    prereg_text = (base / 'PREREGISTRATION.md').read_text(encoding='utf-8')
    require(prereg_text == preregister.text(params), 'params.json does not match PREREGISTRATION.md')
    prereg = sha256_hex(prereg_text.encode('utf-8'))
    reveal = json.loads((public / 'reveal.json').read_text(encoding='utf-8'))
    require(reveal['protocol'] == PROTOCOL and reveal['n_trials'] == N_TRIALS and reveal['k_bits'] == K_BITS,
            'protocol parameters differ from this code')
    require(reveal['preregistration_sha256'] == prereg, 'PREREGISTRATION.md differs from the committed one')
    checks.append('preregistration and params match the committed SHA-256')

    c = commitment(reveal)
    require(committed_value((public / 'commitment.txt').read_text(encoding='utf-8')) == c,
            'revealed guesses do not hash to the commitment')
    checks.append(f'reveal hashes to the commitment {c}')

    if commitment_block is None:
        from ots_support import first_verified_block
        commitment_block = first_verified_block(public / 'commitment.txt', public / 'commitment.txt.ots', fetch)
        require(commitment_block is not None, 'no verified Bitcoin attestation for commitment.txt')
        checks.append(f'OpenTimestamps proof verified against block {commitment_block}')
    b_c = commitment_block
    limit = params['answer_height'] - params['min_lead']
    require(b_c <= limit, f'commitment block {b_c} is later than the preregistered limit {limit}')
    checks.append(f'commitment block {b_c} is at or below the limit {limit}')

    headers = verified_range(b_c, params['send_height'], fetch)
    checks.append(f'blocks {b_c}..{params["send_height"]}: explorers agree, proof of work valid, chain linked')

    deadline = timestamp(headers[params['answer_height']][1]) - params['witness_margin_seconds']
    try:
        when = check_witness(params['witness_url'], c, deadline, capture)
    except ValueError as e:
        raise CheckFailed(str(e))
    checks.append(f'first Internet Archive capture ({datetime.fromtimestamp(when, timezone.utc).isoformat()}) '
                  f'holds the commitment and predates the answer block by the margin')

    a = answers(headers[params['answer_height']][0])
    s = send_flags(headers[params['send_height']][0])
    messages = json.loads((public / 'loop_messages.json').read_text(encoding='utf-8'))
    expected = {str(i): format(a[i], f'0{(K_BITS + 3) // 4}x') for i in range(N_TRIALS) if s[i]}
    require(messages['messages'] == expected and messages['commitment_block'] == b_c,
            'loop_messages.json does not match the answers derived from the chain')
    checks.append(f'loop_messages.json carries exactly the derived answers of {len(expected)} sent trials')

    guesses = [int(g, 16) for g in reveal['guesses']]
    result = analyze(guesses, a, s)
    return dict(checks=checks, commitment=c, commitment_block=b_c, params=params,
                answer_block=headers[params['answer_height']][0], send_block=headers[params['send_height']][0],
                guess_source=reveal['guess_source'], analysis=result,
                trials=[dict(i=i, guess=reveal['guesses'][i], answer=format(a[i], '08x'), sent=s[i],
                             exact=guesses[i] == a[i]) for i in range(N_TRIALS)])


def report(r):
    an = r['analysis']
    lines = [f'# Loop lottery: verification report ({PROTOCOL})', '',
             f'verified {datetime.now(timezone.utc).isoformat(timespec="seconds")}', '',
             '## Integrity checks', ''] + [f'- PASS: {c}' for c in r['checks']] + [
             '', '## Results', '', '| arm | trials | exact matches | expected by chance | p (exact) | '
             'matching bits | p (bits) |', '|---|---|---|---|---|---|---|']
    for arm in ('sent', 'unsent'):
        x = an[arm]
        lines.append(f'| {arm} | {x["trials"]} | {x["exact_matches"]} | {x["expected_exact_by_chance"]:.2e} | '
                     f'{x["exact_p_value"]:.3g} | {x["matching_bits"]}/{x["total_bits"]} | {x["bit_p_value"]:.3g} |')
    verdict = ('**Chance rejected at 5 sigma: sent trials match the future answers.** Per the preregistration, '
               'this calls for an error hunt and independent replication before any interpretation.'
               if an['primary_reject_chance'] else
               '**No evidence that answers came back from the future: sent trials match at chance level.** '
               'This is what standard physics and past-preserving selection (H2\') predict.')
    lines += ['', '## Verdict (preregistered primary test)', '', verdict, '',
              f'Secondary bit test rejects chance: {an["secondary_reject_chance"]}. '
              f'Control (unsent trials) at chance: {an["control_clean"]}.', '']
    return '\n'.join(lines)


def main():
    try:
        r = verify(HERE)
    except CheckFailed as e:
        sys.exit(f'VOID (integrity check failed): {e}')
    text = report(r)
    print(text)
    (HERE / 'public' / 'report.md').write_text(text + '\n', encoding='utf-8', newline='\n')
    (HERE / 'public' / 'report.json').write_text(json.dumps(r, indent=1, default=str), encoding='utf-8',
                                                 newline='\n')


if __name__ == '__main__':
    main()
