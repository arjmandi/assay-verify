#!/usr/bin/env python3
"""Compute ARC-AGI-3 RHAE from run journals — the benchmark's own metric.

WHY THIS EXISTS. Games-cleared, levels-cleared and total-actions are COVERAGE
statistics, not scores. The benchmark scores with RHAE, which penalizes
inefficiency quadratically and gives an unfinished game no efficiency credit
at all. Never state a public score without running this.

THE FORMULA (derived from published scorecard JSONs, not from documentation):

    level score   = min(115, 100 * (baseline_actions / actions_spent) ** 2)
                    (an unattempted / unfinished level scores 0)

    game score, if the run reached WIN:
                  = min(100, sum_i( i * level_score_i ) / sum_i( i ))
                    i.e. levels are weighted by their 1-based index, so late
                    levels dominate; surplus efficiency above the cap is lost

    game score, if the run did NOT reach WIN:
                  = 100 * sum(1..levels_completed) / sum(1..level_count)
                    i.e. weighted progress only — efficiency earns nothing

    set score     = plain mean of the per-game scores

VALIDATION (run `python3 rhae.py --validate <dir-of-scorecard-jsons>`):
reproduces all 25 published per-game scores of a full published cohort exactly
(max error < 0.01), and independently reproduces a second system's published
partial-game score (5 of 10 levels -> 27.27). Both the 115 per-level cap and
the 100 per-game cap are load-bearing; index weighting is what distinguishes
this from a plain mean (a baseline-proportional weighting does not reproduce
the published partial-game scores).

Baselines are a property of each game version, published inside scorecard
JSONs; `baselines.json` here carries them with their instance ids, so any
result below is recomputable without network access.

Usage:
  rhae.py <game> <run-dir> [<game> <run-dir> ...]   # per-run RHAE + set mean
  rhae.py --validate <dir>                          # check formula vs cards
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEVEL_CAP = 115.0
GAME_CAP = 100.0


def level_score(actions: int, baseline: int) -> float:
    """Quadratic efficiency score for one level; 0 if the level was not cleared."""
    if actions <= 0:
        return 0.0
    return min(LEVEL_CAP, 100.0 * (baseline / actions) ** 2)


def game_rhae(level_actions, baselines, levels_completed: int, win: bool) -> float:
    n = len(baselines)
    weight_total = sum(range(1, n + 1))
    if not win:
        return 100.0 * sum(range(1, levels_completed + 1)) / weight_total
    earned = sum((i + 1) * level_score(level_actions[i], baselines[i]) for i in range(n))
    return min(GAME_CAP, earned / weight_total)


def per_level_actions(events, level_count: int) -> list[int]:
    """Attribute every paid action to the level it was spent on.

    A paid action taken while `levels_completed == k` belongs to level k+1 —
    resets and post-GAME_OVER retries included, matching how the published
    cards' level_actions sum to a run's total actions.
    """
    counts = [0] * level_count
    for event in events:
        if not event.get("counts_action"):
            continue
        before = event.get("level_before")
        level = int(before) if before is not None else int(event["levels_completed"])
        if level < level_count:
            counts[level] += 1
    return counts


def load_journal(run_dir: str):
    for state in (".assay", ".arc"):
        path = os.path.join(run_dir, state, "events.jsonl")
        if os.path.exists(path):
            with open(path) as handle:
                return [json.loads(line) for line in handle if line.strip()]
    raise SystemExit(f"no journal under {run_dir}")


def score_run(game: str, run_dir: str, baselines: dict) -> dict:
    entry = baselines[game]
    base = entry["level_baseline_actions"]
    events = load_journal(run_dir)
    actions = per_level_actions(events, len(base))
    final = events[-1]
    win = str(final["state"]) == "WIN"
    done = int(final["levels_completed"])
    return {
        "game": game,
        "instance": entry["instance"],
        "rhae": game_rhae(actions, base, done, win),
        "levels": f"{done}/{len(base)}",
        "state": "WIN" if win else str(final["state"]),
        "paid_actions": sum(actions),
        "level_actions": actions,
        "baselines": base,
    }


def validate(card_dir: str) -> int:
    """Recompute every published per-game score from its own card JSON."""
    import glob

    worst, checked = 0.0, 0
    for path in sorted(glob.glob(os.path.join(card_dir, "**", "scorecard.json"), recursive=True)):
        with open(path) as handle:
            card = json.load(handle)
        for env in card.get("environments", []):
            runs = env.get("runs") or []
            if not runs:
                continue
            run = max(runs, key=lambda r: r.get("actions", 0))
            predicted = game_rhae(
                run["level_actions"], run["level_baseline_actions"],
                run["levels_completed"], run["state"] == "WIN",
            )
            error = abs(predicted - env["score"])
            worst = max(worst, error)
            checked += 1
            if error >= 0.01:
                print(f"MISMATCH {env['id']}: predicted {predicted:.4f} published {env['score']:.4f}")
    print(f"validated {checked} published game scores; worst error {worst:.6f}")
    return 0 if worst < 0.01 else 1


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "--validate":
        return validate(argv[1])
    with open(os.path.join(HERE, "baselines.json")) as handle:
        baselines = json.load(handle)
    if len(argv) < 2 or len(argv) % 2:
        print(__doc__)
        return 2
    results = [score_run(argv[i], argv[i + 1], baselines) for i in range(0, len(argv), 2)]
    print(f"{'game':6}{'RHAE':>8}  {'levels':>7} {'state':<12}{'actions':>8}")
    for r in sorted(results, key=lambda r: r["rhae"]):
        print(f"{r['game']:6}{r['rhae']:8.2f}  {r['levels']:>7} {r['state']:<12}{r['paid_actions']:8}")
    mean = sum(r["rhae"] for r in results) / len(results)
    print(f"\nset RHAE over {len(results)} game(s): {mean:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
