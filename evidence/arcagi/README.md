# Evidence pack №1 — ARC-AGI-3

The first evidence pack published under the `assay-journal-v1` standard: the
25-game public-set record of the ASSAY referee harness, made independently
checkable.

**The result, and where to check it without trusting anyone:** set RHAE
**96.54**, computed by the ARC server itself on public scorecard
[`702ccd4f`](https://arcprize.org/scorecards/702ccd4f-df1f-4118-bc8b-d79d3f4a1a32)
— 24/25 games, 177/183 levels, 8,157 actions, per-game rows on the card.
Provenance, stated exactly: the agents played locally under a journaled,
hard-capped protocol; scorecard ids were not captured during those runs, so
the recorded action sequences were re-issued verbatim against the live ARC
API to mint verifiable cards. The card is therefore a **verification replay
of recorded action sequences** — the server confirms what each sequence
achieves on the same game instances; wall-clock on the card is machine replay
time, not agent time.

## Contents

- **`HEADS.md` / `heads.json`** — published chain heads and paid-action
  counts for all 25 canonical run journals (the commitment artifact; see
  HEADS.md for how to verify a shared run directory against them).
- **`rhae.py` + `baselines.json`** — the benchmark's scoring function,
  reverse-derived from published scorecard JSONs and validated to reproduce
  **25/25 published game scores exactly** (worst error 0.000000):
  `python3 rhae.py --validate <dir-of-scorecard-jsons>`. Score a shared run:
  `python3 rhae.py <game> <run-dir>`.

## Comparator scorecards (public, each system's own)

| System | Backbone | Set RHAE | Scorecard |
|---|---|---|---|
| arc-skill | Opus 5, uncapped | 100.00 | [`24ddb219`](https://arcprize.org/scorecards/24ddb219-987e-464f-9050-6398a29cf5ac) |
| **ASSAY** | Opus 5, hard caps, gated | **96.54** | [`702ccd4f`](https://arcprize.org/scorecards/702ccd4f-df1f-4118-bc8b-d79d3f4a1a32) |
| Prime Agent (median card) | Opus 5, uncapped | 95.24 | [`2af780b4`](https://arcprize.org/scorecards/2af780b4-f2a1-43e9-a794-b23da3cd3f9f) |
| PRO-LONG | Fable 5, uncapped | 94.71 | 25 per-game cards (ids in their release; their per-level baselines are the source of `baselines.json`) |

Same 25 game instances throughout, verified by id. Coverage statistics
(games, levels, actions) are not scores; RHAE is the score.

Further domains publish under this identical standard as `evidence/<world>/`.

## The journals

All 25 canonical journals are published in this directory, one per game, as
`journal-<game>.jsonl.gz`. Each is the complete journal of its run and
includes the agent's predictions, grades, and notes in full. Decompress any
of them and verify it against its head in `heads.json` exactly as in the
worked example below. lf52, the one open game, is published with the rest.

The worked example: `journal-dc22.jsonl.gz` is the complete journal of the
dc22 run, 1,043 events, 1,042 paid actions, WIN 6/6. Verify it against its
published head:

```bash
gunzip -k journal-dc22.jsonl.gz
python3 ../../assay_verify.py journal-dc22.jsonl \
  --expect-head f7a0991384f645d42280949e1946f6a33bd59373012f6a9c47b46d0ef4a0561d
```
