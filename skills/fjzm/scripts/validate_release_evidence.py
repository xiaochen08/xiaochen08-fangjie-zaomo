#!/usr/bin/env python3
"""Validate evidence before a Blockbench/Minecraft runtime support claim."""

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
SUPPORT_TIERS = {"verified", "compatible", "experimental"}
REQUIRED_CASES = (
    "actual_blockbench",
    "single_player",
    "dedicated_server_two_clients",
    "two_models_one_project",
    "interrupt_and_unload",
    "projectile_collision",
)
TARGET_FIELDS = (
    "edition",
    "minecraft_version",
    "integration_type",
    "integration_version",
    "animation_runtime",
    "animation_runtime_version",
    "project_commit",
)


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


def _validate_asset_bundle_payload(bundle: dict[str, Any], root: Path) -> dict[str, list[str]]:
    script = Path(__file__).with_name("validate_asset_bundle.py")
    spec = importlib.util.spec_from_file_location("release_asset_bundle_validator", script)
    if spec is None or spec.loader is None:
        return {"errors": ["unified asset-bundle validator is unavailable"], "warnings": []}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_bundle(bundle, root)


def _validate_file_reference(
    root: Path,
    reference: Any,
    label: str,
    errors: list[str],
) -> Path | None:
    if not isinstance(reference, dict):
        errors.append(f"{label} must be an object")
        return None
    path = _contained(root, reference.get("path"))
    if path is None or not path.is_file():
        errors.append(f"{label} file is missing or outside release root")
        return None
    expected = reference.get("sha256")
    if not isinstance(expected, str) or not SHA256.fullmatch(expected):
        errors.append(f"{label} evidence sha256 must be a lowercase SHA-256")
    elif _sha256(path) != expected:
        errors.append(f"{label} SHA-256 mismatch")
    return path


def _validate_verified_target(target: Any, root: Path, errors: list[str]) -> None:
    if not isinstance(target, dict):
        errors.append("verified support requires target metadata")
        return
    project_path = _contained(root, target.get("project_path"))
    if project_path is None or not project_path.is_dir():
        errors.append("verified support requires an authorized project directory")
    for field in TARGET_FIELDS:
        if not isinstance(target.get(field), str) or not target[field].strip():
            errors.append(f"verified support requires target.{field}")
    build = target.get("build")
    if not isinstance(build, dict):
        errors.append("verified support requires a successful build")
        return
    command = build.get("command")
    if not isinstance(command, list) or not command or any(not isinstance(item, str) or not item for item in command):
        errors.append("verified support requires the exact build command as an argument list")
    if build.get("exit_code") != 0:
        errors.append("verified support requires a successful build with exit_code 0")
    if not build.get("built_at"):
        errors.append("verified support requires build.built_at")
    _validate_file_reference(
        root,
        {"path": build.get("artifact_path"), "sha256": build.get("artifact_sha256")},
        "compiled build artifact",
        errors,
    )


def _validate_blockbench(evidence: Any, root: Path, errors: list[str]) -> None:
    if not isinstance(evidence, dict):
        errors.append("verified support requires blockbench_evidence")
        return
    model_path = _contained(root, evidence.get("model_path"))
    if model_path is None or not model_path.is_file() or model_path.suffix.lower() != ".bbmodel":
        errors.append("blockbench_evidence.model_path must reference the exact saved .bbmodel")
        actual_hash = None
    else:
        actual_hash = _sha256(model_path)
    saved = evidence.get("saved_sha256")
    reopened = evidence.get("reopened_sha256")
    if not isinstance(saved, str) or not SHA256.fullmatch(saved) or actual_hash != saved:
        errors.append("saved .bbmodel hash does not match the exact model file")
    if not isinstance(reopened, str) or not SHA256.fullmatch(reopened) or reopened != saved or actual_hash != reopened:
        errors.append("reopened .bbmodel hash does not match the exact saved file")
    if evidence.get("validator_exit_code") != 0:
        errors.append("actual Blockbench evidence requires validator_exit_code 0")
    expected = evidence.get("animations_expected")
    played = evidence.get("animations_played")
    if not isinstance(expected, list) or not expected:
        errors.append("blockbench_evidence.animations_expected must be non-empty")
    elif not isinstance(played, list) or not set(expected).issubset(set(played)):
        errors.append("every expected animation must be played after reopening the .bbmodel")
    captures = evidence.get("viewport_captures")
    if not isinstance(captures, list) or not captures:
        errors.append("actual Blockbench evidence requires viewport captures")
    else:
        for index, capture in enumerate(captures):
            _validate_file_reference(root, capture, f"blockbench_evidence.viewport_captures[{index}]", errors)


def _validate_matrix(matrix: Any, root: Path, errors: list[str]) -> None:
    if not isinstance(matrix, list):
        errors.append("verified support requires test_matrix")
        return
    by_case: dict[str, Any] = {}
    for index, row in enumerate(matrix):
        if not isinstance(row, dict):
            errors.append(f"test_matrix[{index}] must be an object")
            continue
        case_id = row.get("case_id")
        if case_id in by_case:
            errors.append(f"duplicate test case: {case_id}")
        elif isinstance(case_id, str):
            by_case[case_id] = row
    for case_id in REQUIRED_CASES:
        row = by_case.get(case_id)
        if row is None:
            errors.append(f"missing required test case: {case_id}")
            continue
        label = f"test case {case_id}"
        if row.get("status") != "passed":
            errors.append(f"{label} must have status passed")
        for field in ("timestamp", "tester", "expected", "actual"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                errors.append(f"{label}.{field} is required")
        if not isinstance(row.get("steps"), list) or not row["steps"]:
            errors.append(f"{label}.steps must be non-empty")
        references = row.get("evidence")
        if not isinstance(references, list) or not references:
            errors.append(f"{label} requires file evidence")
        else:
            for index, reference in enumerate(references):
                _validate_file_reference(root, reference, f"{label}.evidence[{index}]", errors)


def validate_release_evidence(manifest: dict[str, Any], release_root: Path | str) -> dict[str, list[str]]:
    root = Path(release_root).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    if manifest.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    identity = {key: manifest.get(key) for key in ("project_id", "asset_id", "asset_version", "rig_signature")}
    for key, value in identity.items():
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{key} is required")

    bundle_reference = manifest.get("asset_bundle")
    bundle_path = _validate_file_reference(root, bundle_reference, "asset_bundle", errors)
    if bundle_path is not None:
        try:
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            errors.append("asset_bundle is not valid UTF-8 JSON")
        else:
            for key, expected in identity.items():
                if bundle.get(key) != expected:
                    errors.append(f"cross-model bundle identity: {key} mismatch")
            bundle_result = _validate_asset_bundle_payload(bundle, root)
            errors.extend(f"asset_bundle validation: {message}" for message in bundle_result["errors"])
            warnings.extend(f"asset_bundle validation: {message}" for message in bundle_result["warnings"])

    support_tier = manifest.get("support_tier")
    target = manifest.get("target")
    if not isinstance(target, dict):
        errors.append("target object is required")
    else:
        for field in ("edition", "minecraft_version", "integration_type"):
            if not isinstance(target.get(field), str) or not target[field].strip():
                errors.append(f"target.{field} is required for every support tier")
    qualification_status = manifest.get("qualification_status")
    if support_tier not in SUPPORT_TIERS:
        errors.append("support_tier must be verified, compatible, or experimental")
    elif support_tier == "verified":
        if qualification_status != "verified":
            errors.append("verified support requires qualification_status verified")
        _validate_verified_target(target, root, errors)
        _validate_blockbench(manifest.get("blockbench_evidence"), root, errors)
        _validate_matrix(manifest.get("test_matrix"), root, errors)
    else:
        if qualification_status == "verified":
            errors.append("qualification_status cannot be verified for a nonverified support tier")
        elif qualification_status not in {"unverified", "review_required"}:
            errors.append("nonverified support requires qualification_status unverified or review_required")
        warnings.append(f"support tier is not verified: {support_tier}; incomplete runtime evidence remains")
    return {"errors": errors, "warnings": warnings}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--release-root", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = validate_release_evidence(manifest, args.release_root or args.manifest.parent)
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
    print(f"PASS: {args.manifest} ({len(result['warnings'])} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
