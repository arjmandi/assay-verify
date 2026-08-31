# Evidence pack №3 — OOLONG

The third evidence pack under the `assay-journal-v1` standard: the three
un-hinted ASSAY runs on the OOLONG long-context benchmark (synth rungs 128K,
1M, and 4M tokens), the runs behind the numbers reported in the paper. The
task framing was neutral (no retrieval-strategy hint) for parity with the
comparator harnesses.

## Contents

- **`heads.json`** — the commitment artifact: published chain heads and
  counts for the three runs.
- **`journal-synth<rung>.jsonl.gz`** — the complete journal of each run.

## What the journals contain, and one reading note

The adapter is a corpus pack: the corpus stays on disk and is never placed
in the observation. Each observation instead carries `corpus_path` and
`corpus_sha256`. The corpora derive from the public OOLONG dataset
(`oolongbench/oolong-synth`), so anyone can rebuild them and check the
hash. Facts are banked through a span gate (a banked fact must be a
verbatim substring of the corpus) and answers go through SUBMIT under a
census gate.

The reading note: in this world `state: WIN` means every question was
submitted through the gate. It is a completion state, not a score.
Correctness is computed only at finalize, sealed, by the benchmark's own
scorer (vendored byte-identical, sha256 `247583a3…`), and the resulting
scores are reported in the paper. This pack makes the process record
checkable: predictions before actions, span-gated claims, an intact chain,
zero ungated events.

## Verify a journal

```bash
gunzip -k journal-synth128k.jsonl.gz
python3 ../../assay_verify.py journal-synth128k.jsonl \
  --expect-head 2dc2360a10e77f51cbfb82abd6d1ac24ca500806485db8aeee29c7b39f540ec8
```

The other heads are in `heads.json`.
