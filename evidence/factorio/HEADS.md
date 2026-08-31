# Published chain heads — the Factorio (FLE) evidence pack

**The commitment:** the recomputed `assay-journal-v1` chain heads of the
three canonical Factorio lab-task wins (M2 calibration, action cap 64,
Opus 5, connect_entities-fixed adapter). Any shared copy of these runs must
verify against its head here:

```bash
python3 ../../assay_verify.py <run-or-journal> --expect-head <head below>
```

| Task | Events | Paid | Progress | State | Stored chain | Chain head (SHA-256) |
|---|---|---|---|---|---|---|
| ironplate | 6 | 5 | 4/4 | WIN | intact | `1c484356fc5ed31c09779aa716e44b8540fd2a0c190bf0a007bda0dfe3c26f11` |
| irongear | 10 | 9 | 4/4 | WIN | intact | `dc78ff02e0cc00e13188b656ab97f38e877ea586701f4226e0c02dd8ee04486b` |
| circuit | 10 | 9 | 4/4 | WIN | intact | `eadd060eb596e48a84541d1fa2dc825ddf5afc970b24e1bf133d8bfde778fca4` |

All three journals are published in this directory as
`journal-<task>.jsonl.gz`. Machine-readable copy: `heads.json`.
