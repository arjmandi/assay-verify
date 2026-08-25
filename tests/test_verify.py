"""Conformance and tamper tests for assay_verify.

The fixture world is a synthetic thermostat — a non-game world with a JSON
observation, exercising the general (non-frame) journal shape. No benchmark
data appears anywhere in these tests (JOURNAL_SPEC.md is the only source of
truth), which is itself a spec property under test: the standard stands alone.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from assay_verify import CHAIN_SEED, verify  # noqa: E402


def _event(i: int, action: str, temp: float, done: bool, paid: bool = True,
           predict: str | None = "ch temp delta sign +", note: str = "") -> dict:
    graded = predict is not None and action != "RESET"
    event = {
        "id": i,
        "timestamp": f"2026-08-25T20:00:{i:02d}+00:00",
        "action": action,
        "data": {"amount": 1} if action == "HEAT" else None,
        "note": note or f"step {i}",
        "state": "WIN" if done else "NOT_FINISHED",
        "levels_completed": 1 if done else 0,
        "level_before": None if action == "START" else 0,
        "win_levels": 1,
        "available_actions": ["HEAT", "COOL"],
        "counts_action": paid and action != "START",
        "observation": {"temp": temp, "setpoint": 22.0},
    }
    if graded and action != "START":
        event["predict"] = predict
        event["predict_ok"] = True
        event["grade"] = [{
            "text": predict, "kind": "channel_delta", "ok": True,
            "actual": f"ch temp -> {temp}", "bucket": "world_model",
        }]
        event["mutation_id"] = i
    return event


def build_run(root: Path, events: list[dict], with_chain: bool = True) -> Path:
    state = root / ".assay"
    state.mkdir(parents=True)
    lines = [json.dumps(event, sort_keys=True) for event in events]
    (state / "events.jsonl").write_text("\n".join(lines) + "\n")
    head = hashlib.sha256(CHAIN_SEED.encode()).hexdigest()
    for line in lines:
        head = hashlib.sha256(head.encode() + line.encode()).hexdigest()
    if with_chain:
        (state / "chain.json").write_text(
            json.dumps({"event_id": len(lines) - 1, "head": head}))
    return root


def thermostat_events() -> list[dict]:
    events = [_event(0, "START", 20.0, False, paid=False, predict=None,
                     note="initial observation")]
    for i, temp in enumerate((20.5, 21.0, 21.5), start=1):
        events.append(_event(i, "HEAT", temp, False))
    events.append(_event(4, "RESET", 20.0, False, predict=None,
                         note="reset is gate-exempt by spec"))
    for i, temp in enumerate((20.5, 21.0, 21.5), start=5):
        events.append(_event(i, "HEAT", temp, False))
    events.append(_event(8, "HEAT", 22.0, True,
                         predict="ch temp = 22.0; win"))
    return events


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="assay-verify-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def fresh(self, name: str, mutate=None, with_chain: bool = True) -> Path:
        events = thermostat_events()
        if mutate:
            events = mutate(events)
        return build_run(self.tmp / name, events, with_chain=with_chain)

    # -- conformance ---------------------------------------------------------
    def test_pristine_is_clean(self):
        report = verify(self.fresh("pristine"))
        self.assertEqual(report["verdict"], "CLEAN")
        self.assertEqual(report["paid"], 8)
        self.assertEqual(report["ungated"], [])
        self.assertEqual(report["stored_chain"], "intact")
        self.assertEqual(report["progress"], "1/1")
        self.assertEqual(report["per_progress_paid"], [8])

    def test_expect_head_match(self):
        run = self.fresh("expect")
        head = verify(run)["chain_head"]
        report = verify(run, expect_head=head)
        self.assertEqual(report["expect_head"], "match")
        self.assertEqual(report["verdict"], "CLEAN")

    def test_absent_chain_is_clean_but_downgraded(self):
        report = verify(self.fresh("prechain", with_chain=False))
        self.assertEqual(report["stored_chain"], "absent")
        self.assertEqual(report["verdict"], "CLEAN")

    def test_arc_alias_state_dir(self):
        run = self.fresh("alias")
        (run / ".assay").rename(run / ".arc")
        report = verify(run)
        self.assertEqual(report["state_dir"], ".arc")
        self.assertEqual(report["verdict"], "CLEAN")

    # -- tamper detection (each variant must flip the verdict) ---------------
    def test_edited_line_diverges(self):
        run = self.fresh("edited")
        events_path = run / ".assay" / "events.jsonl"
        text = events_path.read_text().replace('"temp": 21.0', '"temp": 19.0', 1)
        events_path.write_text(text)
        report = verify(run)
        self.assertEqual(report["stored_chain"], "DIVERGED")
        self.assertEqual(report["verdict"], "INVALID FOR SCORING")

    def test_deleted_line_detected(self):
        run = self.fresh("deleted")
        events_path = run / ".assay" / "events.jsonl"
        lines = events_path.read_text().splitlines()
        events_path.write_text("\n".join(lines[:3] + lines[4:]) + "\n")
        report = verify(run)
        self.assertFalse(report["contiguous"])
        self.assertEqual(report["verdict"], "INVALID FOR SCORING")

    def test_reordered_lines_detected(self):
        run = self.fresh("reordered")
        events_path = run / ".assay" / "events.jsonl"
        lines = events_path.read_text().splitlines()
        lines[2], lines[3] = lines[3], lines[2]
        events_path.write_text("\n".join(lines) + "\n")
        report = verify(run)
        self.assertFalse(report["contiguous"])
        self.assertEqual(report["verdict"], "INVALID FOR SCORING")

    def test_injected_ungated_caught_even_with_consistent_chain(self):
        # The attacker appends a paid, claim-free action AND recomputes the
        # chain — gate compliance must fail independently of tamper-evidence.
        def mutate(events):
            events.append(_event(9, "HEAT", 23.0, True, predict=None))
            return events
        report = verify(self.fresh("ungated", mutate=mutate))
        self.assertEqual(report["stored_chain"], "intact")
        self.assertEqual(report["ungated"], [9])
        self.assertEqual(report["verdict"], "INVALID FOR SCORING")

    def test_wrong_expect_head(self):
        report = verify(self.fresh("wronghead"), expect_head="0" * 64)
        self.assertEqual(report["expect_head"], "MISMATCH")
        self.assertEqual(report["verdict"], "INVALID FOR SCORING")

    def test_bare_journal_file_input(self):
        run = self.fresh("filemode")
        report = verify(run / ".assay" / "events.jsonl")
        self.assertEqual(report["state_dir"], "(file)")
        self.assertEqual(report["verdict"], "CLEAN")
        self.assertEqual(report["paid"], 8)

    def test_reset_is_gate_exempt(self):
        report = verify(self.fresh("resetok"))
        self.assertEqual(report["ungated"], [])  # event 4 is a claim-free RESET


if __name__ == "__main__":
    unittest.main()
