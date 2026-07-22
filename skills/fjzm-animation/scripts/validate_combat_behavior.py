import argparse
import json
import math
import re
import sys
from pathlib import Path


ASCII_ID = re.compile(r"^[A-Za-z0-9_.:/-]+$")
IDENTITY_FIELDS = ("project_id", "asset_id", "asset_version", "model_sha256", "rig_signature")
BRANCH_TARGETS = {"continue", "recover", "fallback", "end", "next"}
TRANSITIONS = {"direct", "blend", "conditional"}
ROOT_MOTION = {"authored", "in_place", "hybrid", "runtime_driven"}


def _ids(document, field, id_field):
    values = document.get(field)
    if not isinstance(values, list):
        return set()
    return {
        item.get(id_field)
        for item in values
        if isinstance(item, dict) and isinstance(item.get(id_field), str)
    }


def _ascii(value, label, errors):
    if not isinstance(value, str) or not value or not ASCII_ID.fullmatch(value):
        errors.append(f"{label} must be a non-empty ASCII runtime ID")


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _identity_errors(payload, other, label, errors):
    for field in IDENTITY_FIELDS:
        if other.get(field) != payload.get(field):
            errors.append(f"{label} {field} does not match combat-behavior-system.json")


def _validate_range(value, label, errors, lower=None, upper=None):
    if not isinstance(value, dict) or not _number(value.get("min")) or not _number(value.get("max")):
        errors.append(f"{label} must contain numeric min and max")
        return
    minimum, maximum = value["min"], value["max"]
    if minimum >= maximum:
        errors.append(f"{label} min must be less than max")
    if lower is not None and minimum < lower:
        errors.append(f"{label} min must be at least {lower}")
    if upper is not None and maximum > upper:
        errors.append(f"{label} max must be at most {upper}")


def validate_combat_behavior(payload, action_library, animation_events):
    errors = []
    warnings = []

    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for field in IDENTITY_FIELDS:
        value = payload.get(field)
        if not isinstance(value, str) or not value:
            errors.append(f"{field} is required")
    model_hash = payload.get("model_sha256")
    if isinstance(model_hash, str) and not re.fullmatch(r"[0-9a-f]{64}", model_hash):
        errors.append("model_sha256 must be a lowercase SHA-256 hex digest")
    if payload.get("animation_backend") not in {"blockbench", "blender_epicfight"}:
        errors.append("animation_backend must be blockbench or blender_epicfight")

    _identity_errors(payload, action_library, "action-library.json", errors)
    _identity_errors(payload, animation_events, "animation-events.json", errors)
    action_ids = _ids(action_library, "actions", "action_id")
    event_ids = _ids(animation_events, "events", "event_id")
    if not action_ids:
        errors.append("action-library.json must contain actions")
    if not event_ids:
        errors.append("animation-events.json must contain events")

    ownership = payload.get("runtime_ownership", {})
    if ownership.get("owner_skill") != "fjzm":
        errors.append("runtime_ownership.owner_skill must be fjzm")
    if ownership.get("server_authoritative") is not True:
        errors.append("runtime_ownership.server_authoritative must be true")
    if ownership.get("animation_workshop_role") != "author_and_validate_contract":
        errors.append("animation_workshop_role must be author_and_validate_contract")

    selection = payload.get("selection_policy", {})
    if selection.get("mode") != "seeded_weighted":
        errors.append("selection_policy.mode must be seeded_weighted")
    if not selection.get("seed_source"):
        errors.append("selection_policy.seed_source is required")
    penalty = selection.get("repetition_penalty")
    if not _number(penalty) or not 0 < penalty <= 1:
        errors.append("selection_policy.repetition_penalty must be greater than 0 and at most 1")
    history = selection.get("history_size")
    if not isinstance(history, int) or isinstance(history, bool) or history < 1:
        errors.append("selection_policy.history_size must be at least 1")
    fallback = selection.get("fallback_action_id")
    _ascii(fallback, "selection_policy.fallback_action_id", errors)
    if fallback not in action_ids:
        errors.append("selection_policy.fallback_action_id is missing from action-library.json")

    profiles = payload.get("weapon_profiles")
    if not isinstance(profiles, list) or not profiles:
        errors.append("weapon_profiles must be a non-empty list")
        profiles = []
    profiles_by_id = {}
    for index, profile in enumerate(profiles):
        label = f"weapon_profiles[{index}]"
        if not isinstance(profile, dict):
            errors.append(f"{label} must be an object")
            continue
        profile_id = profile.get("weapon_profile_id")
        _ascii(profile_id, f"{label}.weapon_profile_id", errors)
        if profile_id in profiles_by_id:
            errors.append(f"duplicate weapon_profile_id: {profile_id}")
        profiles_by_id[profile_id] = profile
        for field in ("category", "style"):
            _ascii(profile.get(field), f"{label}.{field}", errors)
        allowed = profile.get("allowed_action_ids")
        if not isinstance(allowed, list) or not allowed:
            errors.append(f"{label}.allowed_action_ids must be non-empty")
            continue
        for action_id in allowed:
            _ascii(action_id, f"{label}.allowed_action_ids", errors)
            if action_id not in action_ids:
                errors.append(f"{label} action {action_id} is missing from action-library.json")

    policies = payload.get("interrupt_policies")
    if not isinstance(policies, list) or not policies:
        errors.append("interrupt_policies must be a non-empty list")
        policies = []
    policies_by_id = {}
    for index, policy in enumerate(policies):
        label = f"interrupt_policies[{index}]"
        if not isinstance(policy, dict):
            errors.append(f"{label} must be an object")
            continue
        policy_id = policy.get("interrupt_policy_id")
        _ascii(policy_id, f"{label}.interrupt_policy_id", errors)
        policies_by_id[policy_id] = policy
        allowed = policy.get("allowed_interrupts")
        if not isinstance(allowed, list):
            allowed = []
        for required in ("death", "unload"):
            if required not in allowed:
                errors.append(f"{label}.allowed_interrupts must include {required}")
        priority = policy.get("priority")
        if not isinstance(priority, list):
            priority = []
        for required in ("death", "unload"):
            if required not in priority:
                errors.append(f"{label}.priority must include {required}")
        cleanup = policy.get("cleanup_event_ids")
        if not isinstance(cleanup, list) or not cleanup:
            errors.append(f"{label}.cleanup_event_ids must be non-empty")
        else:
            for event_id in cleanup:
                if event_id not in event_ids:
                    errors.append(f"{label} cleanup event {event_id} is missing from animation-events.json")

    series_list = payload.get("behavior_series")
    if not isinstance(series_list, list) or not series_list:
        errors.append("behavior_series must be a non-empty list")
        series_list = []
    series_ids = set()
    for index, series in enumerate(series_list):
        label = f"behavior_series[{index}]"
        if not isinstance(series, dict):
            errors.append(f"{label} must be an object")
            continue
        series_id = series.get("series_id")
        _ascii(series_id, f"{label}.series_id", errors)
        if series_id in series_ids:
            errors.append(f"duplicate series_id: {series_id}")
        series_ids.add(series_id)
        profile_id = series.get("weapon_profile_id")
        if profile_id not in profiles_by_id:
            errors.append(f"{label}.weapon_profile_id does not exist")
            profile_actions = set()
        else:
            profile_actions = set(profiles_by_id[profile_id].get("allowed_action_ids", []))
        weight = series.get("weight")
        if not _number(weight) or weight <= 0:
            errors.append(f"{label}.weight must be greater than 0")
        cooldown = series.get("cooldown_ticks")
        if not isinstance(cooldown, int) or isinstance(cooldown, bool) or cooldown < 0:
            errors.append(f"{label}.cooldown_ticks must be a non-negative integer")
        loop = series.get("loop", {})
        iterations = loop.get("max_iterations")
        if not isinstance(loop.get("enabled"), bool):
            errors.append(f"{label}.loop.enabled must be boolean")
        if not isinstance(iterations, int) or isinstance(iterations, bool) or not 1 <= iterations <= 8:
            errors.append(f"{label}.loop.max_iterations must be between 1 and 8; unbounded loops are forbidden")
        if series.get("interrupt_policy_id") not in policies_by_id:
            errors.append(f"{label}.interrupt_policy_id does not exist")
        conditions = series.get("conditions", {})
        _validate_range(conditions.get("distance"), f"{label}.conditions.distance", errors, lower=0)
        _validate_range(conditions.get("eye_height"), f"{label}.conditions.eye_height", errors)
        states = conditions.get("required_states")
        if not isinstance(states, list) or not states:
            errors.append(f"{label}.conditions.required_states must be non-empty")

        steps = series.get("steps")
        if not isinstance(steps, list) or not steps:
            errors.append(f"{label}.steps must be non-empty")
            continue
        if len(steps) > 32:
            errors.append(f"{label}.steps exceeds the 32-step safety limit")
        for step_index, step in enumerate(steps):
            step_label = f"{label}.steps[{step_index}]"
            if not isinstance(step, dict):
                errors.append(f"{step_label} must be an object")
                continue
            action_id = step.get("action_id")
            _ascii(action_id, f"{step_label}.action_id", errors)
            if action_id not in action_ids:
                errors.append(f"{step_label}.action_id is missing from action-library.json")
            if profile_actions and action_id not in profile_actions:
                errors.append(f"{step_label}.action_id is not allowed by its weapon profile")
            speed = step.get("play_speed")
            if not _number(speed) or not 0.25 <= speed <= 2.5:
                errors.append(f"{step_label}.play_speed must be between 0.25 and 2.5")
            if step.get("transition") not in TRANSITIONS:
                errors.append(f"{step_label}.transition must be direct, blend, or conditional")
            if step.get("root_motion") not in ROOT_MOTION:
                errors.append(f"{step_label}.root_motion is unsupported")
            cancel = step.get("cancel_window")
            if (
                not isinstance(cancel, list)
                or len(cancel) != 2
                or not all(_number(value) for value in cancel)
                or not 0 <= cancel[0] <= cancel[1] <= 1
            ):
                errors.append(f"{step_label}.cancel_window must be normalized and ordered")
            step_events = step.get("event_ids")
            if not isinstance(step_events, list):
                errors.append(f"{step_label}.event_ids must be a list")
            else:
                for event_id in step_events:
                    if event_id not in event_ids:
                        errors.append(f"{step_label} event {event_id} is missing from animation-events.json")
            branch = step.get("branch")
            if not isinstance(branch, dict):
                errors.append(f"{step_label}.branch must define on_hit and on_whiff")
            else:
                for outcome in ("on_hit", "on_whiff"):
                    if outcome not in branch:
                        errors.append(f"{step_label}.branch requires {outcome}")
                        continue
                    target = branch[outcome]
                    if target not in BRANCH_TARGETS and target not in action_ids:
                        errors.append(f"{step_label}.branch.{outcome} target is invalid")

    phases = payload.get("phase_profiles")
    if not isinstance(phases, list) or not phases:
        errors.append("phase_profiles must be a non-empty list")
        phases = []
    ranges = []
    for index, phase in enumerate(phases):
        label = f"phase_profiles[{index}]"
        if not isinstance(phase, dict):
            errors.append(f"{label} must be an object")
            continue
        _ascii(phase.get("phase_id"), f"{label}.phase_id", errors)
        health = phase.get("health_range")
        if (
            not isinstance(health, list)
            or len(health) != 2
            or not all(_number(value) for value in health)
            or not 0 <= health[0] < health[1] <= 1
        ):
            errors.append(f"{label}.health_range must be [min, max] within 0..1")
        else:
            ranges.append((health[0], health[1], label))
        allowed_series = phase.get("allowed_series_ids")
        if not isinstance(allowed_series, list) or not allowed_series:
            errors.append(f"{label}.allowed_series_ids must be non-empty")
        else:
            for series_id in allowed_series:
                if series_id not in series_ids:
                    errors.append(f"{label} references unknown series_id {series_id}")
        transition_action = phase.get("transition_action_id")
        if transition_action not in action_ids:
            errors.append(f"{label}.transition_action_id is missing from action-library.json")
    if ranges:
        ranges.sort(key=lambda item: item[0])
        complete = abs(ranges[0][0]) <= 1e-9 and abs(ranges[-1][1] - 1.0) <= 1e-9
        contiguous = all(abs(ranges[i][1] - ranges[i + 1][0]) <= 1e-9 for i in range(len(ranges) - 1))
        if not complete or not contiguous:
            errors.append("phase_profiles.health_range must cover 0..1 exactly with no gaps or overlaps")

    acceptance = payload.get("acceptance", {})
    for field in (
        "all_transitions_previewed",
        "hit_and_whiff_branches_tested",
        "interrupt_cleanup_tested",
        "actual_runtime_evidence_required",
    ):
        if acceptance.get(field) is not True:
            errors.append(f"acceptance.{field} must be true")

    if len(series_list) == 1:
        warnings.append("only one behavior series is available; weighted choice cannot create variety")
    return {"errors": errors, "warnings": warnings, "valid": not errors}


def _load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid UTF-8 JSON at {path}: {exc}") from exc


def main():
    parser = argparse.ArgumentParser(description="Validate an FJZM combat behavior orchestration contract")
    parser.add_argument("contract", type=Path)
    parser.add_argument("--action-library", required=True, type=Path)
    parser.add_argument("--events", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = validate_combat_behavior(
            _load_json(args.contract),
            _load_json(args.action_library),
            _load_json(args.events),
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    for warning in result["warnings"]:
        print(f"WARNING: {warning}")
    if result["errors"]:
        for error in result["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OK: combat behavior contract is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
