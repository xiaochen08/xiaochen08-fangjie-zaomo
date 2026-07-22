#!/usr/bin/env python3
"""Deterministically simulate an FJZM combat behavior contract.

This proves contract selection/branch/interrupt logic only. It never reports
Minecraft, Blender, Epic Fight, hitbox, networking, or rendering verification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any


def phase_for_health(contract: dict[str, Any], health_ratio: float) -> dict[str, Any]:
    for phase in contract["phase_profiles"]:
        minimum, maximum = phase["health_range"]
        if minimum <= health_ratio < maximum or (maximum == 1.0 and health_ratio == 1.0):
            return phase
    raise ValueError(f"health ratio {health_ratio} is outside all phase ranges")


def eligible_series(
    contract: dict[str, Any], state: dict[str, Any], cooldowns: dict[str, int]
) -> list[dict[str, Any]]:
    phase = phase_for_health(contract, float(state["health_ratio"]))
    allowed = set(phase["allowed_series_ids"])
    result = []
    for series in contract["behavior_series"]:
        series_id = series["series_id"]
        if series_id not in allowed:
            continue
        if series["weapon_profile_id"] != state["weapon_profile_id"]:
            continue
        if cooldowns.get(series_id, 0) > 0:
            continue
        conditions = series["conditions"]
        distance = conditions["distance"]
        eye_height = conditions["eye_height"]
        if not distance["min"] <= float(state["distance"]) <= distance["max"]:
            continue
        if not eye_height["min"] <= float(state["eye_height"]) <= eye_height["max"]:
            continue
        if not all(bool(state.get(required, False)) for required in conditions["required_states"]):
            continue
        result.append(series)
    return result


def effective_weights(
    contract: dict[str, Any], candidates: list[dict[str, Any]], history: list[str]
) -> dict[str, float]:
    penalty = float(contract["selection_policy"]["repetition_penalty"])
    recent = Counter(history[-int(contract["selection_policy"]["history_size"]):])
    return {
        series["series_id"]: float(series["weight"]) * (penalty ** recent[series["series_id"]])
        for series in candidates
    }


def _seed(state: dict[str, Any]) -> int:
    material = f'{state["entity_id"]}:{int(state["combat_cycle"])}'.encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def select_series(
    contract: dict[str, Any],
    state: dict[str, Any],
    history: list[str],
    cooldowns: dict[str, int],
) -> dict[str, Any]:
    candidates = eligible_series(contract, state, cooldowns)
    seed = _seed(state)
    if not candidates:
        return {
            "fallback": True,
            "series_id": None,
            "action_id": contract["selection_policy"]["fallback_action_id"],
            "eligible_series": [],
            "weights": {},
            "seed": seed,
        }
    weights = effective_weights(contract, candidates, history)
    ordered = sorted(candidates, key=lambda item: item["series_id"])
    rng = random.Random(seed)
    chosen = rng.choices(ordered, weights=[weights[item["series_id"]] for item in ordered], k=1)[0]
    return {
        "fallback": False,
        "series_id": chosen["series_id"],
        "action_id": chosen["steps"][0]["action_id"],
        "eligible_series": [item["series_id"] for item in ordered],
        "weights": weights,
        "seed": seed,
    }


def resolve_branch(step: dict[str, Any], outcome: str) -> str:
    key = {"hit": "on_hit", "whiff": "on_whiff"}.get(outcome)
    if key is None:
        raise ValueError("outcome must be hit or whiff")
    return step["branch"][key]


def resolve_interrupt(policy: dict[str, Any], reason: str) -> dict[str, Any]:
    if reason not in policy["allowed_interrupts"]:
        raise ValueError(f"interrupt is not allowed: {reason}")
    return {
        "reason": reason,
        "priority_index": policy["priority"].index(reason),
        "cleanup_event_ids": list(policy["cleanup_event_ids"]),
    }


def run_acceptance(contract: dict[str, Any], cycles: int = 600) -> dict[str, Any]:
    if cycles < 4:
        raise ValueError("cycles must be at least 4")
    scenarios = [
        {"health_ratio": 0.8, "distance": 2.0},
        {"health_ratio": 0.3, "distance": 2.0},
        {"health_ratio": 0.8, "distance": 4.0},
        {"health_ratio": 0.3, "distance": 7.0},
    ]
    base_state = {
        "entity_id": "iron-vanguard-acceptance",
        "weapon_profile_id": "greatsword_two_hand",
        "eye_height": 0.0,
        "grounded": True,
        "line_of_sight": True,
    }
    counts = {series["series_id"]: 0 for series in contract["behavior_series"]}
    fallback_count = 0
    immediate_repeat_count = 0
    last_selected = None
    history: list[str] = []
    cooldowns: dict[str, int] = {}
    traces = []
    history_size = int(contract["selection_policy"]["history_size"])
    for cycle in range(cycles):
        cooldowns = {key: max(0, value - 1) for key, value in cooldowns.items()}
        state = dict(base_state, combat_cycle=cycle, **scenarios[cycle % len(scenarios)])
        result = select_series(contract, state, history, cooldowns)
        if not result["fallback"]:
            series_id = result["series_id"]
            if series_id == last_selected:
                immediate_repeat_count += 1
            last_selected = series_id
            counts[series_id] += 1
            history.append(series_id)
            history = history[-history_size:]
            series = next(item for item in contract["behavior_series"] if item["series_id"] == series_id)
            cooldowns[series_id] = int(series["cooldown_ticks"])
        else:
            fallback_count += 1
            last_selected = None
        if cycle < 16:
            traces.append({"cycle": cycle, "state": state, "selection": result})

    branch_checks = {"hit": 0, "whiff": 0}
    for series in contract["behavior_series"]:
        for step in series["steps"]:
            resolve_branch(step, "hit")
            resolve_branch(step, "whiff")
            branch_checks["hit"] += 1
            branch_checks["whiff"] += 1

    policy = contract["interrupt_policies"][0]
    interrupt_checks = {
        reason: resolve_interrupt(policy, reason) for reason in policy["allowed_interrupts"]
    }
    deterministic_state = dict(base_state, combat_cycle=99, health_ratio=0.3, distance=2.55)
    deterministic_a = select_series(contract, deterministic_state, [], {})
    deterministic_b = select_series(contract, deterministic_state, [], {})
    fallback_state = dict(base_state, combat_cycle=100, health_ratio=0.8, distance=2.0, line_of_sight=False)
    fallback = select_series(contract, fallback_state, [], {})
    phase_1_mid = eligible_series(
        contract,
        dict(base_state, combat_cycle=101, health_ratio=0.8, distance=5.0),
        {},
    )
    phase_2_far = eligible_series(
        contract,
        dict(base_state, combat_cycle=102, health_ratio=0.3, distance=7.0),
        {},
    )
    overlap = eligible_series(
        contract,
        dict(base_state, combat_cycle=103, health_ratio=0.3, distance=2.55),
        {},
    )
    penalized = effective_weights(contract, overlap, ["close_combo_a"])
    checks = {
        "range_and_phase_filters": [item["series_id"] for item in phase_1_mid] == ["mid_gap_close"]
        and [item["series_id"] for item in phase_2_far] == ["far_leap"],
        "fallback_on_invalid_target": fallback["fallback"],
        "deterministic_selection": deterministic_a == deterministic_b,
        "repetition_penalty": penalized["close_combo_a"] < penalized["close_spin_finisher"],
        "all_series_selected": all(value > 0 for value in counts.values()),
        "hit_and_whiff_branches": branch_checks["hit"] == branch_checks["whiff"] > 0,
        "interrupt_cleanup": all(item["cleanup_event_ids"] for item in interrupt_checks.values()),
        "terminal_interrupt_priority": interrupt_checks["death"]["priority_index"]
        < interrupt_checks["hurt"]["priority_index"],
    }
    return {
        "schema_version": 1,
        "project_id": contract["project_id"],
        "asset_id": contract["asset_id"],
        "asset_version": contract["asset_version"],
        "implementation_status": "contract_simulated",
        "runtime_verified": False,
        "cycles": cycles,
        "checks": checks,
        "selection_counts": counts,
        "fallback_count": fallback_count,
        "immediate_repeat_count": immediate_repeat_count,
        "branch_checks": branch_checks,
        "interrupt_checks": interrupt_checks,
        "sample_traces": traces,
        "limitations": [
            "No .blend or .bbmodel action curves were rendered in this simulation.",
            "No Minecraft, Epic Fight, hitbox, networking, save/reload, audio, or particle runtime was executed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--cycles", type=int, default=600)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    report = run_acceptance(contract, args.cycles)
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        if args.output.exists():
            raise FileExistsError(f"refusing to overwrite existing report: {args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    print(encoded, end="")
    return 0 if all(report["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
