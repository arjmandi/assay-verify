# assay-verify

An open, world-agnostic standard for **auditable agent runs**, and a
standalone checker. The checker requires no harness and no trust in the
operator.

An [ASSAY](https://arjmandi.github.io/assay-site/) journal records an agent
run as an append-only sequence of events under a rolling hash chain: every
paid action carries a prediction registered *before* the action executed, and
every prediction is graded in code against the environment's own response.
This repository lets anyone check those properties on any journal they are
given.

- **`JOURNAL_SPEC.md`** — the journal format (`assay-journal-v1`): run
  directory layout, the event schema, the chain rule, the ungated-event rule,
  and the verdict semantics.
- **`CLAIM_GRAMMAR.md`** — the prediction-claim grammar and what a graded
  claim in a journal asserts.
- **`assay_verify.py`** — the checker. Single file, Python 3.10+ standard
  library only, reimplemented from the spec (it shares no code with the
  harness; the two implementations agreeing is part of the point).
- **`evidence/arcagi/`** — the first evidence pack: published chain heads and
  paid-action counts for the 25-game ARC-AGI-3 record, the complete journals
  of all 25 runs, the benchmark's scoring function (`rhae.py`, validated
  against 25/25 published scores), and the public scorecard links.
- **`evidence/factorio/`, `evidence/oolong/`** — the second and third
  evidence packs: published heads and complete journals for the Factorio
  (FLE) calibration wins and for the un-hinted OOLONG runs behind the
  paper's numbers.

## Verify a journal

```bash
python3 assay_verify.py <run-directory>
python3 assay_verify.py <run-directory> --expect-head <sha256>   # against a published head
python3 assay_verify.py <run-directory> --json
```

The verdict is `CLEAN` or `INVALID FOR SCORING`, computed from the artifacts
alone. `--expect-head` checks the journal against a head published in
`evidence/<world>/heads.json`: if the recomputed chain head matches, the
journal you hold is byte-identical to the one whose head was published —
nothing edited, deleted, or reordered since.

To confirm the checker actually rejects tampering, decompress the sample `evidence/arcagi/journal-dc22.jsonl.gz`, flip one byte in it, and run it again with the published `--expect-head`: the recomputed head no longer matches and the verdict becomes `INVALID FOR SCORING`.

Run the checker's own tests (they use a synthetic non-game world; no
benchmark data is involved anywhere in the tool or its tests):

```bash
python3 -m unittest discover -s tests -v
```

## What this proves — and what it deliberately does not

With a run directory and this checker, a third party can verify:

1. **Tamper-evidence** — the journal matches its published chain head; any
   edit, deletion, or reordering breaks the chain and the verdict says so.
2. **Gate compliance** — zero ungated events: every paid action in the record
   carries a prediction that was registered before the action executed, and a
   machine grade against the environment's response.
3. **Contiguity and counts** — nothing is missing; paid actions and their
   per-level attribution recompute exactly, which makes published scores
   recomputable (for ARC-AGI-3, via `evidence/arcagi/rhae.py`).

Deliberate limits, stated plainly: the checker does **not** re-execute claim
grading (the grammar spec makes every predict/grade pair in a journal
readable, but re-grading is out of scope for v1); it cannot prove anything
about *live reasoning* — no post-hoc tool can; and outcome truth for
benchmark runs rests with the benchmark's own public scorecards, linked in
the evidence pack. The complete journals of all three evidence packs are
published in `evidence/`, and each verifies against its already-published
head.

## Versioning

The spec is versioned (`assay-journal-v1`; the chain seed string carries the
version). A planned v2 chains a canonical line form in which free-text fields
are represented by salted hashes, so agent prose can be redacted from a
shared journal without breaking chain verification.

MIT license.
