#!/usr/bin/env python3
"""Validate one identity-scoped Blockbench/Minecraft asset bundle and its evidence."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


SHA256 = re.compile(r"^[0-9a-f]{64}$")
WORKFLOW_ORDER = [
    "asset_identity_locked",
    "attachments_inventoried",
    "sources_inspected",
    "mapping_proposed",
    "mapping_approved",
    "copies_converted",
    "events_registered",
    "animation_bound",
    "manifest_validated",
    "runtime_tested",
]
EVIDENCE_FIELDS = (
    "step",
    "timestamp",
    "status",
    "input_hashes",
    "output_hashes",
    "approval_evidence",
    "tool_version",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _contained_path(root: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = Path(value)
    candidate = raw.resolve() if raw.is_absolute() else (root / raw).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def _collect_named_values(value: Any, name: str) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key == name and isinstance(child, str):
                found.add(child)
            else:
                found.update(_collect_named_values(child, name))
    elif isinstance(value, list):
        for child in value:
            found.update(_collect_named_values(child, name))
    return found


def _validate_runtime_contract_payload(payload: dict[str, Any]) -> dict[str, list[str]]:
    script = Path(__file__).with_name("validate_runtime_contract.py")
    if not script.is_file():
        return {"errors": ["validate_runtime_contract.py is missing"], "warnings": []}
    spec = importlib.util.spec_from_file_location("bundle_runtime_contract_validator", script)
    if spec is None or spec.loader is None:
        return {"errors": ["cannot load validate_runtime_contract.py"], "warnings": []}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_contract(payload)


def _validate_evidence(items: Any, errors: list[str]) -> None:
    if not isinstance(items, list) or not items:
        errors.append("workflow_evidence must be a non-empty list")
        return
    steps: list[Any] = []
    for index, item in enumerate(items):
        label = f"workflow_evidence[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        steps.append(item.get("step"))
        for field in EVIDENCE_FIELDS:
            if field not in item:
                errors.append(f"{label}.{field} is required")
        if item.get("status") != "verified":
            errors.append(f"{label}.status must be verified")
        for field in ("input_hashes", "output_hashes"):
            hashes = item.get(field)
            if not isinstance(hashes, list) or any(not isinstance(v, str) or not SHA256.fullmatch(v) for v in hashes):
                errors.append(f"{label}.{field} must be a list of lowercase SHA-256 values")
    if steps != WORKFLOW_ORDER[: len(steps)]:
        errors.append("evidence steps are out of order or contain an unknown step")


def validate_bundle(manifest: dict[str, Any], bundle_root: Path | str) -> dict[str, list[str]]:
    root = Path(bundle_root).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    identity = {key: manifest.get(key) for key in ("project_id", "asset_id", "asset_version")}
    if manifest.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for key, value in identity.items():
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{key} is required")
    rig_signature = manifest.get("rig_signature")
    if not isinstance(rig_signature, str) or not rig_signature.strip():
        errors.append("rig_signature is required")

    resources = manifest.get("resources")
    if not isinstance(resources, list) or not resources:
        errors.append("resources must be a non-empty list")
        resources = []
    json_resources: dict[str, Any] = {}
    seen_paths: set[Path] = set()
    for index, resource in enumerate(resources):
        label = f"resources[{index}]"
        if not isinstance(resource, dict):
            errors.append(f"{label} must be an object")
            continue
        path = _contained_path(root, resource.get("path"))
        if path is None:
            errors.append(f"{label}.path is outside bundle root")
            continue
        if path in seen_paths:
            errors.append(f"{label}.path duplicates another resource")
        seen_paths.add(path)
        if not path.is_file():
            errors.append(f"{label}.path is missing: {resource.get('path')}")
            continue
        expected = resource.get("sha256")
        if not isinstance(expected, str) or not SHA256.fullmatch(expected):
            errors.append(f"{label}.sha256 must be a lowercase SHA-256")
        elif _sha256(path) != expected:
            errors.append(f"{label} SHA-256 mismatch")
        if path.suffix.lower() == ".json":
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                errors.append(f"{label} is not valid UTF-8 JSON")
                continue
            json_resources[path.name] = payload
            if isinstance(payload, dict):
                for key, expected_identity in identity.items():
                    if key in payload and payload.get(key) != expected_identity:
                        errors.append(f"{label} cross-model identity: {key} mismatch")
                embedded_rig = payload.get("rig_signature")
                if embedded_rig is None and isinstance(payload.get("animation_system"), dict):
                    embedded_rig = payload["animation_system"].get("rig_signature")
                if embedded_rig is None and isinstance(payload.get("stable_contract"), dict):
                    embedded_rig = payload["stable_contract"].get("rig_signature")
                if embedded_rig is not None and embedded_rig != rig_signature:
                    errors.append(f"{label} rig signature mismatch")

    model_spec = json_resources.get("model-spec.json", {})
    route_choice = None
    if isinstance(model_spec, dict) and isinstance(model_spec.get("mod_project"), dict):
        route_choice = model_spec["mod_project"].get("route_choice")
    runtime_contract = json_resources.get("runtime-contract.json")
    if route_choice == "model_first" and not isinstance(runtime_contract, dict):
        errors.append("model_first bundle requires runtime-contract.json")
    if isinstance(runtime_contract, dict):
        runtime_result = _validate_runtime_contract_payload(runtime_contract)
        errors.extend(f"runtime-contract.json: {message}" for message in runtime_result["errors"])
        warnings.extend(f"runtime-contract.json: {message}" for message in runtime_result["warnings"])

    event_table = json_resources.get("animation-events.json", {})
    sound_targets = _collect_named_values(json_resources.get("audio-manifest.json", {}), "event_id")
    particle_targets = _collect_named_values(json_resources.get("particle-contracts.json", {}), "effect_id")
    for event_id in sorted(_collect_named_values(event_table, "sound_event") - sound_targets):
        errors.append(f"unresolved sound_event: {event_id}")
    for effect_id in sorted(_collect_named_values(event_table, "particle_contract_id") - particle_targets):
        errors.append(f"unresolved particle_contract_id: {effect_id}")

    _validate_evidence(manifest.get("workflow_evidence"), errors)
    return {"errors": errors, "warnings": warnings}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--bundle-root", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = validate_bundle(manifest, args.bundle_root or args.manifest.parent)
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
    print(f"PASS: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
