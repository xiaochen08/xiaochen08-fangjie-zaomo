#!/usr/bin/env python3
"""Validate multiple identity-scoped asset bundles and reject cross-model collisions."""

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


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _contained(root: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = Path(value)
    candidate = raw.resolve() if raw.is_absolute() else (root / raw).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def _bundle_validator():
    script = Path(__file__).with_name("validate_asset_bundle.py")
    spec = importlib.util.spec_from_file_location("project_index_bundle_validator", script)
    if spec is None or spec.loader is None:
        raise RuntimeError("unified asset-bundle validator is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_bundle


def _collect(value: Any, field: str) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key == field and isinstance(child, str):
                found.add(child)
            else:
                found.update(_collect(child, field))
    elif isinstance(value, list):
        for child in value:
            found.update(_collect(child, field))
    return found


def validate_project_index(index: dict[str, Any], project_root: Path | str) -> dict[str, list[str]]:
    root = Path(project_root).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    if index.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    project_id = index.get("project_id")
    if not isinstance(project_id, str) or not project_id.strip():
        errors.append("project_id is required")
    assets = index.get("assets")
    if not isinstance(assets, list) or not assets:
        return {"errors": errors + ["assets must be a non-empty list"], "warnings": warnings}

    ids = [entry.get("asset_id") for entry in assets if isinstance(entry, dict)]
    for asset_id in sorted({value for value in ids if ids.count(value) > 1 and isinstance(value, str)}):
        errors.append(f"duplicate asset_id in project index: {asset_id}")

    claims: dict[str, dict[str, list[dict[str, Any]]]] = {
        "animation_id": {}, "event_id": {}, "effect_id": {}, "output_file": {}
    }
    validate_bundle = _bundle_validator()
    seen_bundle_paths: set[Path] = set()
    for index_number, entry in enumerate(assets):
        label = f"assets[{index_number}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        asset_id = entry.get("asset_id")
        bundle_path = _contained(root, entry.get("bundle_path"))
        if bundle_path is None:
            errors.append(f"{label}.bundle_path is outside project root")
            continue
        if bundle_path in seen_bundle_paths:
            errors.append(f"{label}.bundle_path duplicates another asset")
        seen_bundle_paths.add(bundle_path)
        if not bundle_path.is_file():
            errors.append(f"{label}.bundle_path is missing")
            continue
        expected_hash = entry.get("bundle_sha256")
        if not isinstance(expected_hash, str) or not SHA256.fullmatch(expected_hash):
            errors.append(f"{label}.bundle_sha256 must be a lowercase SHA-256")
        elif _sha256(bundle_path) != expected_hash:
            errors.append(f"{label}.bundle_sha256 mismatch")
        try:
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            errors.append(f"{label} bundle is not valid UTF-8 JSON")
            continue
        bundle_result = validate_bundle(bundle, bundle_path.parent)
        errors.extend(f"{label} bundle validation: {message}" for message in bundle_result["errors"])
        warnings.extend(f"{label} bundle validation: {message}" for message in bundle_result["warnings"])
        for field, expected in (
            ("project_id", project_id),
            ("asset_id", asset_id),
            ("asset_version", entry.get("asset_version")),
            ("rig_signature", entry.get("rig_signature")),
        ):
            if bundle.get(field) != expected:
                errors.append(f"{label} cross-model identity: bundle {field} mismatch")

        for resource in bundle.get("resources", []):
            if not isinstance(resource, dict):
                continue
            resource_path = _contained(bundle_path.parent, resource.get("path"))
            if resource_path is None or not resource_path.is_file() or resource_path.suffix.lower() != ".json":
                continue
            try:
                payload = json.loads(resource_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                continue
            for field in ("animation_id", "effect_id", "output_file"):
                for value in _collect(payload, field):
                    claims[field].setdefault(value, []).append({"asset_id": asset_id})
            if isinstance(payload, dict) and isinstance(payload.get("mappings"), list):
                for mapping in payload["mappings"]:
                    if not isinstance(mapping, dict) or not isinstance(mapping.get("event_id"), str):
                        continue
                    claims["event_id"].setdefault(mapping["event_id"], []).append({
                        "asset_id": asset_id,
                        "library": mapping.get("shared_audio_library"),
                        "approved": mapping.get("shared_audio_approved") is True,
                    })

    known_assets = {value for value in ids if isinstance(value, str) and value}
    for field, values in claims.items():
        for value, owners in values.items():
            for owner in owners:
                owner_id = owner.get("asset_id")
                foreign = sorted(asset for asset in known_assets if asset != owner_id and asset in value)
                shared_event = field == "event_id" and owner.get("library") and owner.get("approved")
                if foreign and not shared_event:
                    errors.append(
                        f"{field} is scoped to another asset {foreign} for owner {owner_id}: {value}"
                    )

    for field in ("animation_id", "effect_id", "output_file"):
        for value, owners in claims[field].items():
            distinct = {owner["asset_id"] for owner in owners}
            if len(distinct) > 1:
                errors.append(f"{field} collision across assets {sorted(distinct)}: {value}")
    for value, owners in claims["event_id"].items():
        distinct = {owner["asset_id"] for owner in owners}
        if len(distinct) <= 1:
            continue
        libraries = {owner.get("library") for owner in owners}
        shared_allowed = len(libraries) == 1 and None not in libraries and all(owner.get("approved") for owner in owners)
        if not shared_allowed:
            errors.append(f"event_id collision across assets {sorted(distinct)}: {value}")
    return {"errors": errors, "warnings": warnings}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_index", type=Path)
    parser.add_argument("--project-root", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        payload = json.loads(args.project_index.read_text(encoding="utf-8"))
        result = validate_project_index(payload, args.project_root or args.project_index.parent)
    except (OSError, UnicodeError, json.JSONDecodeError, RuntimeError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for warning in result["warnings"]:
        print(f"WARNING: {warning}")
    for error in result["errors"]:
        print(f"ERROR: {error}")
    if result["errors"]:
        print(f"FAIL: {len(result['errors'])} error(s)")
        return 1
    print(f"PASS: {args.project_index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
