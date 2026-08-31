# Evidence pack №2 — Factorio (FLE)

The second evidence pack under the `assay-journal-v1` standard: the three
canonical Factorio Learning Environment calibration wins (lab tasks
`ironplate`, `irongear`, `circuit`, action cap 64, Opus 5), recorded under
the same journaled, prediction-gated protocol as the ARC-AGI-3 pack.

## Contents

- **`heads.json`** — the commitment artifact: published chain heads,
  paid-action counts, progress, and cost for the three canonical runs
  (generated 2026-08-26, before journal publication).
- **`journal-<task>.jsonl.gz`** — the complete journal of each run: every
  prediction registered before its action, every machine grade, and the
  agent's notes in full.

## What the journals contain

Each paid event's `data.program` field is the exact sandboxed FLE program
that executed, base64-encoded. The world is deterministic under the pinned
setup (fle 0.4.3, server image 2.0.73, map seed 44340, determinism measured
at M0), so the recorded programs replay without any model in the loop.

## Verify a journal

```bash
gunzip -k journal-circuit.jsonl.gz
python3 ../../assay_verify.py journal-circuit.jsonl \
  --expect-head eadd060eb596e48a84541d1fa2dc825ddf5afc970b24e1bf133d8bfde778fca4
```

The other heads are in `heads.json`. The verifier checks the chain, the
zero-ungated-actions property, and the counts from the artifact alone. The
adapter and its sanctioned-interface screen live in the harness, which is
not required for verification.
