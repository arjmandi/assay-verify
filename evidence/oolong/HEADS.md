# Published chain heads — the OOLONG evidence pack

**The commitment:** the recomputed `assay-journal-v1` chain heads of the
three un-hinted OOLONG synth runs (neutral task framing, Opus 5). Any
shared copy of these runs must verify against its head here:

```bash
python3 ../../assay_verify.py <run-or-journal> --expect-head <head below>
```

Note: `WIN` in this world means all questions were submitted through the
gate. It is a completion state, not a score. Scoring is sealed at finalize
and reported in the paper.

| Task | Events | Paid | Progress | State | Stored chain | Chain head (SHA-256) |
|---|---|---|---|---|---|---|
| synth128k | 51 | 50 | 25/25 | WIN | intact | `2dc2360a10e77f51cbfb82abd6d1ac24ca500806485db8aeee29c7b39f540ec8` |
| synth1m | 51 | 50 | 25/25 | WIN | intact | `93d36427c9f0229e7d2f161454243841ddfdd6e926a6b7908509335718a771a7` |
| synth4m | 41 | 40 | 20/20 | WIN | intact | `2d49db298cc8d2166099f66ec69f002084efd9896f56b2b666d40013d31c96af` |

All three journals are published in this directory as
`journal-synth<rung>.jsonl.gz`. Machine-readable copy: `heads.json`.
