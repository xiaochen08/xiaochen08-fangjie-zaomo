#!/usr/bin/env python3
"""Create an identity-scoped, explicitly unverified runtime-delivery evidence scaffold."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


SHA256 = re.compile(r"^[0-9a-f]{64}$")
CASES = (
    "actual_blockbench",
    "single_player",
    "dedicated_server_two_clients",
    "two_models_one_project",
    "interrupt_and_unload",
    "projectile_collision",
)
COMPATIBLE_TARGET_FIELDS = (
    "edition",
    "minecraft_version",
    "integration_type",
    "integration_version",
    "animation_runtime",
    "animation_runtime_version",
    "project_path",
    "project_commit",
)


class ScaffoldError(RuntimeError):
    """Raised when a runtime-delivery scaffold cannot be safely identified."""


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_scaffold(
    bundle: dict[str, Any],
    target: dict[str, Any],
    *,
    bundle_path: str,
    bundle_sha256: str,
) -> dict[str, Any]:
    if not isinstance(bundle, dict) or not isinstance(target, dict):
        raise ScaffoldError("bundle and target must be JSON objects")
    identity = {key: bundle.get(key) for key in ("project_id", "asset_id", "asset_version", "rig_signature")}
    for key, value in identity.items():
        if not isinstance(value, str) or not value.strip():
            raise ScaffoldError(f"bundle {key} is required")
    if not isinstance(bundle_path, str) or not bundle_path.strip() or not SHA256.fullmatch(bundle_sha256):
        raise ScaffoldError("bundle_path and lowercase bundle_sha256 are required")
    for field in ("edition", "minecraft_version", "integration_type"):
        if not isinstance(target.get(field), str) or not target[field].strip():
            raise ScaffoldError(f"target.{field} is required")
    complete_target = all(isinstance(target.get(field), str) and target[field].strip() for field in COMPATIBLE_TARGET_FIELDS)
    return {
        "schema_version": 1,
        **identity,
        "asset_bundle": {"path": bundle_path, "sha256": bundle_sha256},
        "support_tier": "compatible" if complete_target else "experimental",
        "qualification_status": "unverified",
        "target": copy.deepcopy(target),
        "runtime_artifacts": [],
        "blockbench_evidence": {
            "model_path": "",
            "saved_sha256": "",
            "reopened_sha256": "",
            "validator_exit_code": None,
            "animations_expected": [],
            "animations_played": [],
            "viewport_captures": [],
        },
        "test_matrix": [
            {
                "case_id": case_id,
                "status": "not_run",
                "timestamp": "",
                "tester": "",
                "steps": [],
                "expected": "",
                "actual": "",
                "evidence": [],
            }
            for case_id in CASES
        ],
        "scaffold_note": "This file contains no runtime success evidence. Change support_tier to verified only after validation passes.",
    }


def write_versioned_json(payload: Any, folder: Path | str, stem: str) -> Path:
    destination_folder = Path(folder)
    destination_folder.mkdir(parents=True, exist_ok=True)
    destination = destination_folder / f"{stem}.json"
    version = 2
    while destination.exists():
        destination = destination_folder / f"{stem}_v{version}.json"
        version += 1
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return destination


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("asset_bundle", type=Path)
    parser.add_argument("--edition", required=True)
    parser.add_argument("--minecraft-version", required=True)
    parser.add_argument("--integration-type", required=True)
    parser.add_argument("--integration-version", default="")
    parser.add_argument("--animation-runtime", default="")
    parser.add_argument("--animation-runtime-version", default="")
    parser.add_argument("--project-path", default="")
    parser.add_argument("--project-commit", default="")
    parser.add_argument("--write-dir", type=Path)
    parser.add_argument("--output-stem", default="runtime-delivery")
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        bundle = json.loads(args.asset_bundle.read_text(encoding="utf-8"))
        target = {
            "edition": args.edition,
            "minecraft_version": args.minecraft_version,
            "integration_type": args.integration_type,
            "integration_version": args.integration_version,
            "animation_runtime": args.animation_runtime,
            "animation_runtime_version": args.animation_runtime_version,
            "project_path": args.project_path,
            "project_commit": args.project_commit,
        }
        scaffold = build_scaffold(
            bundle,
            target,
            bundle_path=args.asset_bundle.name,
            bundle_sha256=file_sha256(args.asset_bundle),
        )
        if args.write_dir:
            print(write_versioned_json(scaffold, args.write_dir, args.output_stem))
        else:
            sys.stdout.write(json.dumps(scaffold, ensure_ascii=False, indent=2) + "\n")
    except (OSError, UnicodeError, json.JSONDecodeError, ScaffoldError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
