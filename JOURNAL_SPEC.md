# The ASSAY journal — format specification

**Spec version: `assay-journal-v1`.** The version string is load-bearing: it
is the seed of the hash chain (§4), so a journal's chain commits to the spec
version it was written under.

An ASSAY journal is the auditable record of one agent run in one *world*. A
world is anything attached to the harness through a registry (a JSON contract
of the agent's permitted actions) and an adapter (the observation source):
a game, a simulator, a trading venue, an industrial environment. Nothing in
this format is specific to any benchmark; §7 notes the two field-naming
conventions that date from the harness's first benchmark and their general
semantics.

## 1. Run directory layout

One directory = one run. The journal state lives in a state directory inside
it:

- `.assay/` — the state directory (current name).
- `.arc/` — accepted as a historical alias (runs recorded before the current
  name). Verifiers MUST accept both; a run has exactly one.

Files in scope for this specification:

| File | Required | Contents |
|---|---|---|
| `<state>/events.jsonl` | yes | the journal: one JSON event per line, append-only |
| `<state>/chain.json` | no | the writer's stored chain state `{event_id, head}`; runs recorded before chain support lack it |
| `<state>/mutations.jsonl` | no | the broker's write-ahead spend records, used for crash recovery of orphaned spends |

Every other file in the state directory (notes, verifier programs, channel
definitions, receipts, caches) is operator- and agent-side working state,
**out of scope** for integrity verification, and not required to be present
in a shared run directory.

## 2. The event schema

Each line of `events.jsonl` is one JSON object. Fields, with their writer:

| Field | Writer | Meaning |
|---|---|---|
| `id` | machine | 0-based event index; MUST equal the line's position (§5) |
| `timestamp` | machine | ISO-8601 write time |
| `action` | machine | the executed action's registered name; `START` for the opening observation; `RESET` is the built-in world-reset (§6) |
| `data` | machine | the action's typed parameters as validated, or `null` |
| `counts_action` | machine | `true` iff the event spent one unit of the action budget (`START` does not) |
| `state` | adapter | the world's lifecycle state after the event; `WIN` is the goal-reached terminal (§7) |
| `levels_completed` | adapter | host progress counter after the event (§7) |
| `level_before` | machine | host progress counter before the event (`null` on `START`) |
| `win_levels` | adapter | total host progress units for this world (§7) |
| `available_actions` | adapter | the action names/ids available after the event |
| `frames` + `n_frames` | adapter | frame worlds only: the raw observation as one or more integer grids, rows serialized as strings |
| `observation` | adapter | non-frame worlds only: the raw observation as a JSON object |
| `note` | **agent** | free-text rationale attached to the action |
| `predict` | **agent** | the prediction claim string, registered **before** the action executed (grammar: `CLAIM_GRAMMAR.md`) |
| `predict_ok` | machine | overall grade: `true` iff every claim in `predict` graded ok |
| `grade` | machine | per-claim grades: a list of `{text, kind, ok, actual, bucket, ...}` objects, each grading one claim against the world's own response |
| `mutation_id` | machine | key into `mutations.jsonl` for crash recovery |

Two writer classes matter for interpretation: **machine** and **adapter**
fields are produced by the harness and the world; **agent** fields (`note`,
`predict`) are authored by the agent under evaluation, and `predict` is the
one the gate enforces (§6).

**Secrets guarantee.** The writer redacts the values of registered secret
environment variables from every agent-supplied string before it is written;
a conforming journal contains `[REDACTED:<NAME>]` markers instead. Absence of
plaintext credentials is a property of the write boundary, not of a later
scrub.

## 3. Events are append-only

The journal is append-only. Nothing in this specification updates, rewrites,
or deletes a line. Status of any kind (trust, progress, verdicts) is computed
from the record, never stored over it.

## 4. The hash chain

The chain makes the journal **tamper-evident under stated conditions** — not
unforgeable, and the distinction is deliberate: an operator who controls the
machine can rewrite a whole journal and its chain together. What the chain
guarantees is *commitment*: once a head is published (or anchored outside the
run directory), the journal it commits to cannot be edited, truncated,
reordered, or extended without the recomputed head changing.

    head_0 = SHA-256("assay-chain-v1")                     # hex digest of the seed string
    head_n = SHA-256(hex(head_{n-1}) || line_n)            # hex head string concatenated with the raw line

where `line_n` is the raw journal line exactly as stored (no trailing
newline; blank lines are skipped). The writer maintains `chain.json` as
`{"event_id": <last id>, "head": <hex>}` and periodically anchors heads
outside the run directory. Anchor files are operator-side and out of scope;
**published heads** (e.g. `evidence/<world>/heads.json` in this repository)
are the third-party reference: verify a shared journal with
`--expect-head <published head>`.

A consequence worth stating: the chain covers raw lines, so a journal with
any field redacted after the fact can no longer match its published head.
Under v1, "redacted" and "chain-verified" are mutually exclusive; spec v2
(planned) chains a canonical form in which free-text fields enter as salted
hashes, making agent prose redactable without breaking verification.

## 5. Contiguity

Event `id`s MUST be exactly `0..N-1` in file order. A gap, duplicate, or
out-of-order id is a contiguity violation and invalidates the run for
scoring.

## 6. The gate, and the ungated-event rule

The harness's constitutional rule is **predict-before-act**: a paid action is
admitted only as part of a prediction — a machine-parseable claim about what
the world will report, registered before the action executes and graded by
code against the world's own response afterwards.

An event is **UNGATED** iff:

    counts_action is true
    AND action != "RESET"
    AND it carries none of: predict, predict_ok, grade

`RESET` is the only exemption: it is the built-in whole-world reset, cannot be
registered as an adapter action (the harness refuses the name), and spends
budget without requiring a claim.

**One ungated event invalidates the entire run for scoring**, and the writer
additionally demotes all trust earned after the first one. The rule is
evaluated purely over journal fields, so any third party can check it.

## 7. Host progress and lifecycle — general semantics, historical names

Two conventions date from the harness's first benchmark (ARC-AGI-3, a suite
of grid games) and are kept for compatibility; their semantics are general:

- **`levels_completed` / `win_levels` / `level_before`** — the *host progress
  pair*: how many host-defined progress units the run has completed, out of
  how many. Games instantiate these as levels. A world with no intermediate
  milestones uses `win_levels: 1`, making progress a plain goal-reached bit.
- **`state`** — the host lifecycle: `NOT_FINISHED` (running), `WIN` (the
  pinned goal is reached), with worlds free to report additional terminal
  states (e.g. `GAME_OVER`). "Win" throughout the grammar means *the host's
  goal state is reached*, whatever the world.

Spec v2 reserves general aliases (`progress`, `progress_total`, `status`);
v1 verifiers read the historical names.

## 8. Verdict semantics

A verifier MUST report `INVALID FOR SCORING` if any of the following holds,
and `CLEAN` otherwise:

1. contiguity violated (§5);
2. one or more UNGATED events (§6);
3. a stored chain is present and does not match the recomputed chain;
4. an expected head was supplied and does not match the recomputed head.

An *absent* `chain.json` does not invalidate (pre-chain runs are legitimate);
it downgrades the guarantee from "committed as written" to "committed as of
the published head", which is why publishing heads matters.

Informational (never part of the verdict): paid-action count, per-progress
attribution of paid actions, final state and progress, and events recovered
from the mutation journal after a writer crash.
