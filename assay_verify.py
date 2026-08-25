#!/usr/bin/env python3
"""assay-verify — standalone integrity verifier for ASSAY journals.

Spec: JOURNAL_SPEC.md (assay-journal-v1). Python 3.10+, standard library
only. This is a clean reimplementation from the specification and shares no
code with any harness; the independent agreement of the two implementations
is part of the verification story.

Usage:
  assay_verify.py <run-dir> [--expect-head SHA256] [--json]

Exit codes: 0 = CLEAN, 1 = INVALID FOR SCORING, 2 = cannot read a journal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SPEC = "assay-journal-v1"
CHAIN_SEED = "assay-chain-v1"
STATE_DIRS = (".assay", ".arc")  # current name, historical alias


class VerifyError(Exception):
    pass


def find_journal(target: Path) -> tuple[Path, str]:
    """Accept a run directory (holding .assay/ or .arc/) or a journal file."""
    if target.is_file():
        return target, "(file)"
    for name in STATE_DIRS:
        candidate = target / name
        if (candidate / "events.jsonl").is_file():
            return candidate / "events.jsonl", name
    raise VerifyError(
        f"no journal at {target} (expected an events.jsonl file, or a run "
        "directory holding " + " or ".join(f"{d}/events.jsonl" for d in STATE_DIRS) + ")"
    )


def read_lines(events_path: Path) -> list[str]:
    return [line for line in events_path.read_text().splitlines() if line.strip()]


def compute_chain(lines: list[str]) -> str:
    head = hashlib.sha256(CHAIN_SEED.encode()).hexdigest()
    for line in lines:
        head = hashlib.sha256(head.encode() + line.encode()).hexdigest()
    return head


def parse_events(lines: list[str]) -> tuple[list[dict], list[str]]:
    """Return (events, contiguity_problems). Parse errors are contiguity-class."""
    events: list[dict] = []
    problems: list[str] = []
    for index, line in enumerate(lines):
        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            problems.append(f"line {index}: not valid JSON ({error})")
            continue
        events.append(event)
        if event.get("id") != index:
            problems.append(f"line {index}: event id {event.get('id')!r} != position {index}")
    return events, problems


def ungated_events(events: list[dict]) -> list[int]:
    """JOURNAL_SPEC.md section 6: paid, non-RESET, carrying no claim machinery."""
    flagged = []
    for event in events:
        if not event.get("counts_action") or event.get("action") == "RESET":
            continue
        gated = (
            event.get("predict")
            or event.get("predict_ok") is not None
            or event.get("grade")
        )
        if not gated:
            flagged.append(int(event["id"]))
    return flagged


def per_progress_paid(events: list[dict], total_units: int) -> list[int]:
    """Attribute every paid action to the host progress unit it was spent on."""
    counts = [0] * max(total_units, 0)
    for event in events:
        if not event.get("counts_action"):
            continue
        before = event.get("level_before")
        unit = int(before) if before is not None else int(event.get("levels_completed", 0))
        if 0 <= unit < total_units:
            counts[unit] += 1
    return counts


def stored_chain_state(state_dir: Path, last_id: int, head: str) -> str:
    path = state_dir / "chain.json"
    if not path.is_file():
        return "absent"
    try:
        stored = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return "DIVERGED"
    if int(stored.get("event_id", -2)) == last_id and stored.get("head") == head:
        return "intact"
    return "DIVERGED"


def recovered_orphans(events: list[dict]) -> list[int]:
    return [
        int(event["id"])
        for event in events
        if "recovered from broker mutation journal" in str(event.get("note") or "")
    ]


def verify(run_dir: Path, expect_head: str | None = None) -> dict:
    journal, state_name = find_journal(run_dir)
    lines = read_lines(journal)
    events, contiguity_problems = parse_events(lines)
    head = compute_chain(lines)
    last_id = len(lines) - 1
    stored = stored_chain_state(journal.parent, last_id, head)
    ungated = ungated_events(events)
    paid = sum(1 for event in events if event.get("counts_action"))
    final = events[-1] if events else {}
    total_units = int(final.get("win_levels", 0) or 0)
    expect_state = "not-provided"
    if expect_head is not None:
        expect_state = "match" if expect_head.lower() == head else "MISMATCH"
    invalid = (
        bool(contiguity_problems)
        or bool(ungated)
        or stored == "DIVERGED"
        or expect_state == "MISMATCH"
    )
    return {
        "spec": SPEC,
        "run": str(run_dir),
        "state_dir": state_name,
        "events": len(events),
        "paid": paid,
        "contiguous": not contiguity_problems,
        "contiguity_problems": contiguity_problems,
        "chain_head": head,
        "stored_chain": stored,
        "expect_head": expect_state,
        "ungated": ungated,
        "recovered_orphans": recovered_orphans(events),
        "final_state": str(final.get("state", "")),
        "progress": f"{int(final.get('levels_completed', 0) or 0)}/{total_units}",
        "per_progress_paid": per_progress_paid(events, total_units),
        "verdict": "INVALID FOR SCORING" if invalid else "CLEAN",
    }


def human_lines(report: dict) -> list[str]:
    lines = [
        f"assay-verify | spec {report['spec']}",
        f"run      {report['run']} (state dir {report['state_dir']})",
        f"events   {report['events']} (paid {report['paid']}) | "
        f"contiguous {'yes' if report['contiguous'] else 'NO'}",
        f"chain    recomputed head {report['chain_head']}",
        f"stored   chain.json {report['stored_chain']}",
    ]
    if report["expect_head"] != "not-provided":
        lines.append(f"expect   published head {report['expect_head']}")
    lines.append(f"gates    ungated paid events: {len(report['ungated'])}"
                 + (f" {report['ungated'][:8]}" if report["ungated"] else ""))
    lines.append(f"outcome  state {report['final_state']} | progress {report['progress']}"
                 f" | per-unit paid {report['per_progress_paid']}")
    if report["recovered_orphans"]:
        lines.append(f"note     recovered orphan events {report['recovered_orphans'][:8]}")
    for problem in report["contiguity_problems"][:8]:
        lines.append(f"problem  {problem}")
    lines.append(f"verdict  {report['verdict']}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path,
                        help="run directory holding .assay/ or .arc/, or an events.jsonl file")
    parser.add_argument("--expect-head", help="published chain head to verify against")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)
    try:
        report = verify(args.run_dir, args.expect_head)
    except (VerifyError, OSError) as error:
        print(f"assay-verify: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("\n".join(human_lines(report)))
    return 0 if report["verdict"] == "CLEAN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
