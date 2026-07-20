#!/usr/bin/env python3
"""Validate a model-first runtime contract before detailed Blockbench production."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


ASCII_ID = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
STABLE_ID = re.compile(r"^[a-z0-9][a-z0-9_.:-]*$")
TARGET_STATUSES = {"locked", "provisional", "unresolved", "not_applicable"}
ASSET_ROLES = {
    "block", "item", "structure", "furniture", "display", "wearable",
    "entity", "block_entity", "projectile", "vehicle", "environment",
}
DYNAMIC_ROLES = {"entity", "block_entity", "projectile", "vehicle"}
RUNTIME_HEAVY_FEATURES = {
    "animation", "particles", "audio", "projectile", "targeting", "damage",
    "networking", "custom_renderer", "shader_specific", "destruction",
}
REQUIRED_RISK_CONSEQUENCES = {
    "runtime exports deferred",
    "integration rework may be required",
    "no game-ready claim",
}
STAGES = {"concept_only", "graybox_only", "runtime_neutral_source", "platform_export"}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_target_pair(profile: dict[str, Any], stem: str, errors: list[str]) -> str | None:
    status = profile.get(f"{stem}_status")
    value = profile.get(stem)
    if status not in TARGET_STATUSES:
        errors.append(f"target_profile.{stem}_status is invalid")
        return None
    if status in {"locked", "provisional"} and not _nonempty(value):
        errors.append(f"target_profile.{stem} is required when status is {status}")
    if status in {"unresolved", "not_applicable"} and value not in {None, ""}:
        errors.append(f"target_profile.{stem} must be null when status is {status}")
    return status


def _validate_id_list(stable: dict[str, Any], field: str, errors: list[str]) -> list[str]:
    values = stable.get(field)
    if not isinstance(values, list):
        errors.append(f"stable_contract.{field} must be a list of stable lowercase IDs")
        return []
    if any(not isinstance(value, str) or not STABLE_ID.fullmatch(value) for value in values):
        errors.append(f"stable_contract.{field} must contain stable lowercase IDs")
    if len(values) != len(set(values)):
        errors.append(f"stable_contract.{field} must not contain duplicate IDs")
    return [value for value in values if isinstance(value, str)]


def validate_contract(contract: dict[str, Any]) -> dict[str, list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if contract.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for field in ("project_id", "asset_id"):
        value = contract.get(field)
        if not isinstance(value, str) or not ASCII_ID.fullmatch(value):
            errors.append(f"{field} must be a stable lowercase ASCII identifier")
    if not _nonempty(contract.get("asset_version")):
        errors.append("asset_version is required")
    if contract.get("edition") != "java":
        errors.append("model-first Mod runtime contract currently requires edition java")
    if contract.get("route_choice") != "model_first" or contract.get("project_status") != "runtime_deferred":
        errors.append("runtime contract requires model_first and runtime_deferred")

    role = contract.get("asset_role")
    if role not in ASSET_ROLES:
        errors.append("asset_role is invalid")
    risk = contract.get("runtime_risk")
    if risk not in {"low", "medium", "high"}:
        errors.append("runtime_risk must be low, medium, or high")
    features = contract.get("runtime_features")
    if not isinstance(features, list) or any(not isinstance(value, str) or not STABLE_ID.fullmatch(value) for value in features):
        errors.append("runtime_features must be a list of stable lowercase IDs")
        features = []
    if len(features) != len(set(features)):
        errors.append("runtime_features must not contain duplicates")
    if risk == "low" and (role in DYNAMIC_ROLES or set(features) & RUNTIME_HEAVY_FEATURES):
        errors.append("dynamic or runtime-heavy assets cannot be classified low risk")

    profile = contract.get("target_profile")
    if not isinstance(profile, dict):
        errors.append("target_profile is required")
        profile = {}
    version_status = _validate_target_pair(profile, "minecraft_version", errors)
    loader_status = _validate_target_pair(profile, "loader", errors)
    mappings_status = _validate_target_pair(profile, "mappings", errors)
    animation_status = _validate_target_pair(profile, "animation_runtime", errors)
    render_status = _validate_target_pair(profile, "render_path", errors)
    if not isinstance(profile.get("multiplayer_required"), bool):
        errors.append("target_profile.multiplayer_required must be true or false")
    if any(status in {"provisional", "unresolved"} for status in (version_status, loader_status, mappings_status)):
        warnings.append("target profile remains provisional; project inspection may require migration")

    stable = contract.get("stable_contract")
    if not isinstance(stable, dict):
        errors.append("stable_contract is required")
        stable = {}
    if not _nonempty(stable.get("rig_signature")) or not STABLE_ID.fullmatch(str(stable.get("rig_signature", ""))):
        errors.append("stable_contract.rig_signature must be a stable lowercase ID")
    animation_ids = _validate_id_list(stable, "animation_ids", errors)
    event_ids = _validate_id_list(stable, "event_ids", errors)
    locator_ids = _validate_id_list(stable, "locator_ids", errors)
    _validate_id_list(stable, "texture_ids", errors)
    if "animation" in features and not animation_ids:
        errors.append("animation feature requires at least one animation_id")
    if set(features) & {"particles", "audio", "projectile"} and not event_ids:
        errors.append("runtime effects require at least one event_id")
    if "projectile" in features and "projectile_spawn" not in locator_ids:
        errors.append("projectile feature requires locator_id projectile_spawn")

    recommendation = contract.get("mod_first_recommendation")
    acceptance = contract.get("risk_acceptance")
    if risk in {"medium", "high"}:
        if not isinstance(recommendation, dict) or recommendation.get("required") is not True or recommendation.get("status") != "declined" or not _nonempty(recommendation.get("evidence")):
            errors.append("medium/high model_first requires verbatim decline evidence after recommending create_mod_first")
        if not isinstance(acceptance, dict) or acceptance.get("required") is not True or acceptance.get("status") != "approved" or not _nonempty(acceptance.get("evidence")):
            errors.append("medium/high model_first requires explicit risk acceptance evidence")
        consequences = set(acceptance.get("accepted_consequences", [])) if isinstance(acceptance, dict) else set()
        if not REQUIRED_RISK_CONSEQUENCES.issubset(consequences):
            errors.append("risk acceptance must include all deferred-runtime consequences")

    gate = contract.get("production_gate")
    if not isinstance(gate, dict):
        errors.append("production_gate is required")
        gate = {}
    stage = gate.get("allowed_stage")
    if stage not in STAGES:
        errors.append("production_gate.allowed_stage is invalid")
    blockers = gate.get("blockers")
    if not isinstance(blockers, list):
        errors.append("production_gate.blockers must be a list")
    critical_unresolved = render_status == "unresolved" or ("animation" in features and animation_status == "unresolved")
    if critical_unresolved and stage not in {"concept_only", "graybox_only"}:
        errors.append("unresolved critical runtime fields require graybox_only or concept_only")

    handoff = contract.get("integration_handoff")
    if not isinstance(handoff, dict):
        errors.append("integration_handoff is required")
        handoff = {}
    if stage == "platform_export" or handoff.get("export_status") != "deferred" or handoff.get("project_path") not in {None, ""}:
        errors.append("platform-specific export requires an inspected project")
    if handoff.get("source_format") != "bbmodel":
        errors.append("integration_handoff.source_format must be bbmodel")
    if handoff.get("adapter_status") != "not_started":
        errors.append("model_first adapter_status must remain not_started")
    if contract.get("qualification_status") != "unverified":
        errors.append("runtime_deferred cannot be verified")
    return {"errors": errors, "warnings": warnings}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        payload = json.loads(args.contract.read_text(encoding="utf-8"))
        result = validate_contract(payload)
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for warning in result["warnings"]:
        print(f"WARNING: {warning}")
    for error in result["errors"]:
        print(f"ERROR: {error}")
    if result["errors"]:
        print(f"FAIL: {len(result['errors'])} error(s)")
        return 1
    print(f"PASS: {args.contract}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
