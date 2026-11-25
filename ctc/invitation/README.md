# Invitation to future senders: asking whoever has a time machine to send back a block hash

Created 2026-11-25 with AI assistance (Claude). No external review. Protocol `cll-future-reply-v1`.

**Status: published 2026-11-25.** `INVITATION.md` (SHA-256 `3394e6f0cdcf6fde53694bfadf11f044c0c797ee454e9dc91dd54f276e47ce82`) was stamped with OpenTimestamps on 2026-11-25 (all four default calendars answered) and pushed to this repository. The stamp was confirmed in block P = 977531 (hash 00000000000000000000ca5441b76e50df821290d0d2e427263c2fab7f59a21b, block time 2026-11-25T15:44:40+00:00); the preferred window is blocks 977531..977675, closing at block 977686. See STATUS.json. Rules fixed at commit `d5370da`. Tested offline (`ctc/tests/test_invitation.py`, 43 tests), reviewed twice, run end to end on a synthetic chain with attackers, and dry-run on 145 real mainnet blocks (see "Mock run", "Live dry run" and "Review" below).

## In one sentence

Publish, and keep published, a request: "whoever can send information into the past, send us the hash of any Bitcoin block before that block is mined". Nobody can know a block hash in advance, so a single reply that is anchored in the blockchain before the block it names is information from the future. The chance of a lucky guess is about 2⁻¹⁷⁶ per reply.

## How this differs from the loop lottery

| | Loop lottery ([../blockchain/README.md](../blockchain/README.md)) | This invitation |
|---|---|---|
| Who sends to the past | we do, by publishing answers after they exist; nothing is really sent | anyone who has a real time machine |
| What is tested | whether intending a loop is enough for self-consistency to pull answers back | whether a time machine whose past end reaches the present already exists, and someone uses it |
| Prediction of PPS (H2′) | no hits: the guesses are recorded before the answers exist | any reply that arrives is correct, **if** such a machine exists: the arriving message is not a recorded fact, and the block hash is mined later, inside the loop's causal future |
| Cost of running | one session of about 9 hours | publish once, then only check replies; the request can stay open for decades |

## Why a reply can only come from an existing machine

A wormhole time machine cannot send anything to times before it was built: the chronology horizon of `ctc/timeless/wormhole.py` is at lab time 7.5, and before it no closed curve exists. A machine built in 2200 can reach 2200, not 2026. So a reply that reaches us now requires either a machine whose past end already exists now, or closed timelike curves in nature (not made by anyone). The invitation tests exactly that, cheaply. It cannot tell whether time machines will ever be built.

## What is asked

The hash of **any** Bitcoin block, sent so that it is anchored in an earlier block. No height has to be agreed in advance, so a sender with a machine whose exit opens at any date can reply.

**Text reply.** Any file whose plain text contains a line

```text
CLL-FUTURE-REPLY-v1 hash=<the block hash, 64 hex digits>
```

(`height=<h>` may be added before `hash=`; it is only a hint), stamped with [OpenTimestamps](https://opentimestamps.org) and made public together with its `.ots` proof. Any other text in the file is free.

**Transaction reply.** A Bitcoin transaction whose OP_RETURN output carries the 37 bytes

```text
43 4c 4c 46 | 01 | <the 32-byte block hash, as displayed>
 "CLLF"      version
```

The same 37 bytes anywhere in the part of the transaction that its txid commits to also count (for example a miner's coinbase scriptSig); witness data does not, because the txid does not commit to it. A transaction reply needs nobody's server: anyone can find it by scanning the chain, now or in a hundred years. `python -B ctc/invitation/reply.py --show-payload <hash>` prints both forms.

## Preferred window

A reply may arrive at any time, chosen by the sender: with a wormhole, a message entering the future mouth at time T leaves the past mouth at T − Δ, where Δ is fixed by the machine. It may even arrive before the invitation is published, since a sender who reads the invitation can aim earlier. Already-mined blocks are settled, though: under PPS, as in standard physics, a reply never appears in a block whose content is already recorded. So the past part of the answer is fixed now and can be searched (see "Retrospective search").

To give senders a target and the result a date, the invitation asks:

> Please, if you can, anchor your reply in one of the blocks P, P + 1, …, P + 144, and name a block no later than P + 150, where P is the block in which this invitation is first timestamped (its OpenTimestamps proof shows P).

- **P cannot be written into the invitation**, because it is known only after the stamp is confirmed. A sender in the future reads it from the proof. P is also recorded in this repository once known.
- **144 blocks is about one day.** The named block must be at least 6 blocks after the reply's anchor and, for the window, no later than P + 150. Without that upper limit a reply anchored in the window could name a block years ahead, and the window could never be closed.
- **The window is a request, not a rule.** A valid reply outside it, before or after, counts just as much. `reply.py` only labels it ("inside the preferred window", "before the invitation was anchored", "after the preferred window", or "anchored in the preferred window, but names a block after P + 150"; `--invitation-height P`; tested).
- **What it adds.** Without a window, a null result has no date: a reply may still come. With it, a definite statement is possible once block P + 150 has 6 confirmations: `reply.py --scan P P+144 --invitation-height P` downloads every block of the window, checks each against its verified header (same header, merkle root of all its transactions), judges every transaction reply in it, and gives a verdict (`window_summary`: open, closed, incomplete, or a valid reply). Claimed hashes are looked up only among the verified headers P … P + 150, fetched once, so a flood of random payloads costs no extra requests. A scan with no valid finding proves that no valid transaction reply is anchored in the window. Text replies cannot be found this way (an OpenTimestamps stamp is invisible on the chain), so for them the statement covers only those reported. It is still conditional on a willing sender who reads the invitation and has a machine reaching that day.

## Why a valid reply cannot be forged

The anchor block commits to the reply: through the OpenTimestamps proof (text) or through the transaction's merkle proof (transaction). The named block descends from the anchor, so its header contains, through the chain of previous-block hashes, the hash of the anchor header, and therefore depends on the reply. A reply that contains the named block's hash was therefore fixed before that block's header existed. A forger has two options, both infeasible:

- fix the value first, then build a descending header with exactly that hash: a preimage of double SHA-256 for a constrained header, about 2²⁵⁶ hash evaluations (2¹²⁸ with Grover's algorithm);
- choose the value and the header together: a fixed point of double SHA-256 through the chain of headers.

This does not depend on how many blocks lie between, on the proof-of-work difficulty, or on how much hash power a forger has.

So the one essential check is **descent**: every header from the anchor to the named block is fetched, its hash and proof of work recomputed, and its link to the previous header checked. The other rules are conservative margins.

## Validity rules (reply.py)

1. **Full hash** (essential). The claimed value must equal the named block's full hash, in display order or reversed. A prefix does not count: a display-order hash starts with about 19 zero hex digits from proof of work, so only about 177 of its 256 bits are unpredictable (the base-2 logarithm of the proof-of-work target; 177.06 for block 977066, tested).
2. **Anchor** (essential). For a text reply, the earliest block whose verified header carries the file's OpenTimestamps merkle root. For a transaction reply, the block found by the transaction's merkle proof against a verified header. The transaction is parsed from raw bytes and its txid recomputed, witness excluded as in Bitcoin.
3. **Descent** (essential). The named block descends from the anchor, checked header by header (`check_descent`). A run with `--no-descent` is marked provisional.
4. **Lead** (margin). The anchor must be at least 6 blocks before the named block. Descent alone needs only 1. The margin keeps the rule easy to state and costs a real sender nothing.
5. **Confirmations** (margin). The named block must have at least 6 confirmations and be in the best chain when judged, so that the judgment refers to a block that stays in Bitcoin's history.
6. **Headers.** Every header comes from two independent explorers, which must agree byte for byte, with recomputed proof of work and a modern difficulty floor (`ctc/blockchain/chain.py`). Anyone with their own node can rerun the checks without explorers.

One valid reply is decisive; no statistics are needed. Every claim ends in one of four outcomes:

- **valid**: all rules hold ("valid (provisional)" if the descent check was skipped);
- **rejected**, with the reason: it names a block mined too early relative to its anchor, the descent fails, or the named block has left the best chain (margin rule 5; such replies stay on record for manual review);
- **pending**: it names no known block, the named block is not yet buried 6 deep, or a text reply's stamp is not yet in a block. A reply that names no known block may name a block that does not exist yet, the most interesting case, so it is kept and checked again, never discarded;
- **error**: the check could not be completed (for example a network failure). An error is never counted as a rejection.

## Attacks considered

| Attack | Why it fails |
|---|---|
| Guess the leading zeros and claim a prefix match | only the full hash counts (rule 1; tested) |
| Post many random guesses | each has chance ≈ 2⁻¹⁷⁶; even 10¹⁸ posts stay below 2⁻¹¹⁶ |
| Hide many guesses in one OpenTimestamps merkle tree and reveal the winner later (the fatal loophole of the lottery's v1) | needs about 2¹⁷⁶ guesses for one success |
| Insert a reply into an old block after the named block exists (reorganization, any hash power) | the rebuilt chain no longer contains the named block below the reply; descent fails |
| A miner mines the named block to match a posted guess | needs a preimage of double SHA-256 |
| Colluding explorers place a real, fully worked header where it does not belong | the descent check finds the broken link (tested) |
| Change a transaction after the fact | the txid is recomputed and must sit in the verified merkle root (tested); witness changes do not change the txid, and the witness is not searched (tested) |
| A wrong height hint makes a correct hash fail | the height is only a hint; the hash is looked up (tested) |
| A real sender uses some other Bitcoin-anchored channel | the same argument applies; see "Retrospective search" |

## Predictions

Conditional on a time machine whose past end reaches the present. Toy model in `predictions.py`: 64 possible messages or none; the hash depends on what arrived and on later mining randomness; the future sender replies with probability s (all tested).

| Rule | Does a reply arrive? | If one arrives, is it correct? |
|---|---|---|
| No such machine (standard physics, or chronology protection) | no; only hoaxes | by chance (1/64 in the model; 2⁻¹⁷⁶ for real hashes) |
| P-CTC | with probability ≈ s | always |
| PPS, mining randomness unrecorded when the message arrives (the real situation) | with probability ≈ s | always (one world, P-CTC inside it) |
| PPS, if the mining randomness had been recorded before the arrival | less often than s | always if s < 1 ("nothing arrives" is always consistent); if s = 1, only in the ≈ 63% of worlds where some message is its own hash, the D-CTC fallback elsewhere |
| D-CTC (this project's maximum-entropy fixed point, unique here) | with probability ≈ s | by chance only: the loop state is a fixed distribution, uncorrelated with the mining |

What this means:

- **A valid reply** would fit P-CTC and PPS and contradict D-CTC as used here. This is the first protocol in the project in which PPS predicts a positive result, conditional on a loop existing.
- **A wrong reply anchored in advance** is expected from hoaxes, and under D-CTC also from a real sender. The two cannot be told apart, so wrong replies are recorded but count for nothing.
- **Consistency does not force a reply.** Under P-CTC and PPS "nothing arrives and nobody sends" is always a consistent history, so how often a reply arrives depends on the senders' willingness, not on the rule.

## What a null result means

Nothing arriving is consistent with no time machine reaching the present, with chronology protection, or with senders who do not reply or do not know the invitation. It bounds only "a willing sender with a machine reaching our time, using one of these channels". The bound is weak, but the test costs almost nothing and stays open. Two results can be stated: a dated one for the preferred window once P + 144 is confirmed, and an open-ended one ("no valid reply found up to block X") at each later check.

## Retrospective search (not done)

The same argument applies to the whole history of Bitcoin: any data committed in a block that contains the hash of a later, descending block would be a message from the future, whatever its format. A full scan needs the whole chain (hundreds of GB) or a public dataset. Nemiroff and Wilson ([arXiv:1312.7128](https://arxiv.org/abs/1312.7128)) made a similar search of the internet for prescient mentions and found none.

## Mock run (simulate.py)

`python -B ctc/invitation/simulate.py` runs the whole protocol on a synthetic chain: real double SHA-256 and real block, transaction and merkle formats, trivial proof of work. The invitation is anchored at block P, about 180 blocks are mined, and the attacks below are judged by the same code that judges real replies (`SimulatedRun` in the tests):

| Attack | Outcome |
|---|---|
| about 130 random guesses spread over the window | all **pending** (they name no known block) |
| a copy of an earlier block's hash, published after it | **rejected**: anchored too late |
| the same hash in reversed byte order | **rejected**: anchored too late |
| the payload in an ordinary input's scriptSig | found by the scan, then **rejected** like the copy |
| the payload only in a witness | not found (the txid does not commit to it) |
| history rewritten from P + 31 to put in a reply naming block P + 50, already seen | **rejected**: the named block left the best chain, and it does not descend from the new anchor |
| explorers serve a private block, mined afterwards, as a descendant of the anchor | **rejected**: the descent check finds the broken link |
| a block body with its last transaction duplicated (the merkle mutation of CVE-2012-2459) | same payloads found as in the real body: nothing can be hidden this way |
| a block body with a transaction removed | **error**: it no longer matches the merkle root, so the scan stops instead of reporting "no reply" |
| window verdict after P + 155 | closed: no valid transaction reply; the same from the local header index with no explorer lookups |
| window verdict at P + 150 | open |

A genuine reply cannot be part of the mock run: it would be a block containing the hash of its own descendant, which is exactly the forgery the protocol rules out. The acceptance path is tested on real headers instead, by supplying the anchor height directly.

## Live dry run (2026-11-25)

The window scan was run on the real Bitcoin chain, as if the invitation had been anchored at P = 977349 (tip 977514, so the window had closed at 977504). Nothing was published or sent; the run only reads public blocks.

| | |
|---|---|
| blocks downloaded and checked against their headers | 145 (977349 … 977493), 227 MB |
| transactions parsed (all formats on mainnet, including segwit and taproot) | 612,396, with no parse error and every merkle root matching |
| headers verified by two explorers, linked one by one | 151 (977349 … 977499) |
| explorer lookups for claims | none (local header index) |
| run time | 32 minutes |
| replies found | 0 |
| verdict | `closed: no valid transaction reply anchored in the window` |

- **Positive control.** The same byte search finds real OP_RETURN data in real blocks: the segwit witness commitment (`aa21a9ed`) in the coinbase of block 977400 (7394 transactions). So "0 replies" means there were none, not that the scan cannot see them.
- **What it found.** The first attempt died after one header request timed out: a single transient network failure stopped the whole scan. Fixed (problem 17 below), and the second attempt completed.
- **What it means.** In that day of blocks nobody anchored a transaction reply. Since the invitation was not published, this is a test of the machinery, not a result about time travel; but in the protocol's own terms it is a retrospective search of one window, and it is empty.

## Review (2026-11-25)

A first review of the protocol as written earlier the same day found:

| # | Problem | Severity | Fix |
|---|---|---|---|
| 1 | The checker trusted the explorers' heights and checked only the two endpoint headers. Colluding explorers could present a real, fully worked header, mined after the reply, as a descendant of the anchor. | high | descent checked header by header, mandatory unless explicitly skipped (`check_descent`); test with a misplaced real header |
| 2 | The documented security argument ("needs a reorganization of at least 7 blocks") was wrong in kind. The real argument is that the named block's hash depends on the reply: forging needs a constrained preimage or a fixed point of double SHA-256, whatever the hash power. The lead and confirmation rules are margins. | medium (documentation) | "Why a valid reply cannot be forged"; rules marked essential or margin |
| 3 | A wrong `height=` hint made a correct hash fail. | low | the height is a hint; fall back to looking up the hash |
| 4 | Only OP_RETURN outputs were searched, so a payload in a coinbase scriptSig would be missed, although the txid commits to it. | low | search the whole txid-covered serialization; the witness stays excluded |
| 5 | The prediction model forced the future sender to reply, so it said "P-CTC: a hit with probability 1". With an empty message and willingness s, P-CTC gives a reply with probability ≈ s and makes every reply correct. | medium (interpretation) | model and table rewritten |

A second review (2026-11-25, after the preferred window was added) found:

| # | Problem | Severity | Fix |
|---|---|---|---|
| 6 | The explorers answer an unknown hash with `{"in_best_chain": false, "height": null}`, not an error. The checker read that as "stale block" and stopped, so a correct reply in reversed byte order was rejected online. The offline tests missed it because their lookup raised an error for unknown hashes. | high | "unknown" (height null: try the other byte order) is told apart from "stale" (a known block outside the best chain); the test lookup now behaves like the explorers; checked live against both explorers |
| 7 | Every exception during the lookup was treated as "not found", so a network failure could reject a genuine reply. | medium | only "not found" (404, unknown hash) moves on; other failures give the outcome **error**, never **rejected** (tested) |
| 8 | A reply anchored in the window could name a block years ahead, so the window could never be closed. | medium | the window also asks for a named block no later than P + 150 |
| 9 | The window's null result relied on replies being reported; nothing could show that no transaction reply exists in the window. | medium | `--scan`: download each block, check it against its verified header and the merkle root of all its transactions, and judge every payload found (tested on real blocks 0–2 and on synthetic blocks; run live on block 977066) |
| 10 | The invitation said a missing reply would "likely" mean the machine cannot reach back that far, which overstates; and a text reply was not told to publish its `.ots` proof. | low | wording corrected |
| 11 | "Stamp the SHA-256 of this README" would break as soon as P is added to it. | low | name the git commit of the rules instead |

The mock run (2026-11-25, third check) found:

| # | Problem | Severity | Fix |
|---|---|---|---|
| 12 | A reply naming no known block was **rejected** ("no block with hash"). But that is exactly what a genuine reply looks like when it is checked before its block is mined: it would have been thrown away. | high | new outcome **pending**: kept and checked again (tested) |
| 13 | A named block with fewer than 6 confirmations, and a text reply whose stamp was not yet in a block, were also rejected instead of pending. | medium | both pending (tested) |
| 14 | No verdict for the window: the scan listed replies but did not say whether the window was open, closed or complete. | medium | `window_summary` (tested: closed, open when too early, incomplete after errors) |
| 15 | Every claim in a scan triggered explorer lookups, so a flood of random payloads in the window could make the scan very slow. | low | window scans look claims up in a local index of verified headers P … P + 150 (tested with lookups disabled) |
| 16 | A reply naming a block that later left the best chain is rejected by margin rule 5, although a block that still descends from the anchor would prove the same. Only a reorganization after the sender read the block causes this. | low | kept as a conservative rule; such replies are marked "kept on record for manual review" |
| 17 | (found by the live dry run) One timed-out request ended a 30-minute scan, because network calls were not retried. | medium | transient failures (timeouts, connection errors, 429, 5xx) are retried up to 5 times with doubling waits; 404 is not retried (`chain.with_retries`, shared with the lottery; tested) |
| 18 | (found while publishing) The `ots` command does not start on Windows: python-bitcoinlib looks for an OpenSSL DLL. | medium | `ots_support.py` stamps and upgrades through the `opentimestamps` library directly, as the command does |
| 19 | (found while publishing) The Internet Archive replays a capture with its original gzip encoding; `witness.py` compared the compressed bytes, so a correct capture looked different. This would also have voided a correct run of the loop lottery. | high (for the lottery) | decode gzip-encoded responses (tested) |

Checked and not a problem in any review:

- *64-byte transactions* (an inner merkle node read as a transaction): a reply needs at least 37 payload bytes plus a minimal transaction, more than 64 bytes, and the transaction is parsed exactly.
- *Reorganizations, stale blocks, low-difficulty forks:* by the argument above none of them allows a forgery. The best-chain rule only fixes what "a Bitcoin block" means.

A real limit, not a flaw: the protocol is exactly as strong as the preimage resistance of double SHA-256. If that ever breaks, replies anchored after the break are worthless, so each judgment should be made promptly and recorded with a timestamp.

Remaining gaps:

- **Discoverability.** Nothing guarantees that anyone in the future sees the invitation. Mitigations when publishing: OpenTimestamps, the Internet Archive, GitHub (which Software Heritage archives), and optionally a short pointer in a Bitcoin transaction.
- **Rules fixed in advance.** The rules are objective, so changing them later could not validate a forgery. Still, the published invitation should name the git commit of the rules (this README and `reply.py` at that commit), stamped with it. A hash of this README itself would not do, since P is added to it after publication.
- **Scanning is per block range.** `--scan` closes the window completely for transaction replies (about 145 blocks, roughly 25 minutes of downloads). A scan of the whole chain (the retrospective search) is not done.
- **The prediction model is a classical toy.** It fixes D-CTC's fixed point by Cesàro averaging (unique in the model) and treats the mining as one random variable.
- **No external review.**

## Files

| File | Content |
|---|---|
| `reply.py` | reply formats, transaction and block parsing, merkle proofs, descent check, validity rules, the preferred-window label, block scanning, a command-line checker (`--text`, `--txid`, `--scan`, `--show-payload`, `--no-descent`, `--invitation-height`) |
| `predictions.py` | the toy model behind the predictions table |
| `simulate.py` | the mock run on a synthetic chain with attackers |
| `followup.py` | the steps after publishing (`status`, `upgrade`: complete the proof and record P, `scan`: judge the window); results go to `STATUS.json` and `window_result.json` |
| `INVITATION.md` | draft of the public invitation (English and Traditional Chinese); not published |
| `../tests/test_invitation.py` | 46 offline tests (including the mock run and the follow-up phases) on real headers, two real transactions (the coinbase of block 977066, the genesis coinbase) and the raw blocks 0–2 |

## Publishing

1. ~~Fix the text of `INVITATION.md`: remove the draft line, and name the git commit of the rules.~~ Done 2026-11-25: rules fixed at commit `d5370da5c54dcacfeda797b509f9004f02cd5b21`. From the moment it is stamped, `INVITATION.md` must never change by a single byte (the repository's `.gitattributes` already turns off line-ending conversion, so the bytes on GitHub equal the stamped bytes on every platform).
2. ~~Stamp it with OpenTimestamps and push it to the repository.~~ Done 2026-11-25. The `ots` command does not start on Windows (python-bitcoinlib looks for an OpenSSL DLL), so `ctc/blockchain/ots_support.py` now stamps and upgrades through the `opentimestamps` library directly, the way `ots stamp` and `ots upgrade` do (nonce, the same four calendars, at least two answers). **Still to do:** once the stamp is in a block, upgrade `INVITATION.md.ots`, push it (senders read P from it), and record P here.
3. ~~Ask the Internet Archive to capture it.~~ Done: first captures of the raw GitHub URLs at 2026-11-25 13:42:28 UTC (`INVITATION.md`, bytes identical to the stamped file once the archive's gzip encoding is removed) and 13:43:28 UTC (`INVITATION.md.ots`, the pending proof). Optionally post it elsewhere.
4. Once block P + 150 has 6 confirmations, run `reply.py --scan P P+144 --invitation-height P` (the dated window result). Steps 2 (P) and 4 run automatically: a local scheduled task runs `followup.py` every two hours, records P and then the window verdict in `STATUS.json`, and commits and pushes only those records. After that, check from time to time, recording each check with its date: transaction replies by scanning for `434c4c4601`, text replies wherever they are reported.
