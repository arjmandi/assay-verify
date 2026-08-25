# The prediction-claim grammar

**Companion to `JOURNAL_SPEC.md` (`assay-journal-v1`).** This document
specifies the claim language that appears in every event's `predict` field
and what each grade in the `grade` list asserts. It defines *meanings at the
journal level* — what a third party reading a graded claim may conclude —
not the grading engine's implementation.

A `predict` string is one or more claims separated by `;`. Free text that
parses as no claim is kept as commentary and graded as the weakest claim,
`change`. Any claim may end with `@within Ns`: it grades only if the world's
result settles within `N` seconds.

## Core claim forms (any world)

| Claim | Graded meaning |
|---|---|
| `noop` | the observation after the action is identical to before |
| `change` | something in the observation differs |
| `level+1` | the action completes the current host progress unit (`levels_completed` increments) |
| `win` | the action reaches the host's goal state (`state` becomes `WIN`) |
| `verify:PATH.py` | the agent-authored program at PATH, run sandboxed by the referee over the raw before/after observations, returns ok — the program's contract is `def verify(before, after) -> (ok, actual)` |
| `ch NAME = V [± TOL]` | the registered channel NAME reads V (within TOL) after the action |
| `ch NAME delta OP V` | the channel moves by an amount satisfying OP ∈ {=, >=, <=} |
| `ch NAME delta sign +`/`-` | the channel moves up / down |
| `ch NAME crosses V [from below\|from above]` | the channel crosses threshold V |

**Channels** are typed extractors over the raw observation: `goal` and
`level` are built in (the host lifecycle and progress of `JOURNAL_SPEC.md`
§7); the agent declares its own — a dotted path into the observation or an
extractor — and every declaration is journaled. A channel claim is graded
against the extractor's value over the world's own response, never against
the agent's account of it.

**Executable verifiers** are the grammar's escape hatch to arbitrary checks:
the agent writes the program, the referee runs it sandboxed and
identity-probes it — a verifier that cannot distinguish a transformed
observation from the original is flagged *vacuous* and its passes earn
nothing.

## Frame-world claim forms (grid worlds only)

Worlds whose observation is a grid (`frames` present) admit four additional
coordinate forms, with `x` = column and `y` = row:

| Claim | Graded meaning |
|---|---|
| `cell X,Y=V` | the cell at (X,Y) becomes value V |
| `move X,Y DX,DY` | the object covering (X,Y) shifts by (DX,DY) and vacates its old cells |
| `vanish X,Y` | every cell of the object covering (X,Y) stops being its color |
| `region X0:X1,Y0:Y1` | all changes fall inside this half-open box, and something changes |

These are meaningless off-grid and absent from non-frame worlds' journals.

## Grades, buckets, and what they assert

Each event's `grade` is a list with one entry per claim:

```json
{"text": "ch temp delta sign +", "kind": "channel_delta", "ok": true,
 "actual": "ch temp 21.0 -> 21.4", "bucket": "world_model"}
```

- `ok` — whether the claim held against the world's response;
- `actual` — the machine's statement of what actually happened (the
  counter-fact when `ok` is false);
- `bucket` — `gamble` for milestone claims (`win`, `level+1`, and channel
  claims on the built-in `goal`/`level` channels) versus `world_model` for
  everything else. The distinction lets a reader separate *predictions about
  progress* from *predictions about mechanics* when computing miss rates.

`predict_ok` on the event is the conjunction of the claim `ok`s.

## What a graded claim licenses

Reading a journal, a third party may conclude: for every paid non-`RESET`
event, a claim in this grammar was registered before the action executed
(else the event would be UNGATED and the run invalid), and each claim's `ok`
was computed by the referee from the world's own response. The grammar is
therefore the unit of *earned belief* in the record: a rule of the agent's
world model is only as supported as the graded claims that exercised it — a
reading this record's operators use themselves (the "coverage audit"
protocol: before accepting an agent-side impossibility conclusion, enumerate
the rules it load-bears on, audit the journal for which were ever exercised
by a graded claim in the relevant regime, and buy graded probes for the
gaps).

Out of scope for v1: re-executing grades. The spec makes every
`predict`/`grade` pair readable; a shared run directory additionally contains
the agent's channel declarations and verifier programs, so grades are
re-derivable in principle, but the reference checker does not re-run them.
