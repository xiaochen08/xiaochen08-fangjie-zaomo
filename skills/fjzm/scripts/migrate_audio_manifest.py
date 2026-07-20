#!/usr/bin/env python3
"""Safely migrate a legacy audio manifest into the identity-scoped v11 RC profile."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


SHA256 = re.compile(r"^[0-9a-f]{64}$")
BASE_STEPS = [
    "asset_identity_locked",
    "attachments_inventoried",
    "sources_inspected",
    "mapping_proposed",
]


class MigrationError(RuntimeError):
    """Raised when a migration would be ambiguous or destructive."""


def migrate_manifest(
    source: dict[str, Any],
    *,
    project_id: str,
    asset_id: str,
    asset_version: str,
    model_spec_path: str,
    model_spec_sha256: str,
    rig_signature: str,
) -> dict[str, Any]:
    """Return a migrated deep copy while preserving gaps as review requirements."""
    if not isinstance(source, dict):
        raise MigrationError("source manifest must be a JSON object")
    if not all(isinstance(value, str) and value.strip() for value in (project_id, asset_id, asset_version, model_spec_path, rig_signature)):
        raise MigrationError("project, asset, version, model-spec path, and rig signature are required")
    if not SHA256.fullmatch(model_spec_sha256):
        raise MigrationError("model_spec_sha256 must be a lowercase SHA-256")

    migrated = copy.deepcopy(source)
    prior_schema = migrated.get("schema_version")
    migrated["schema_version"] = 1
    migrated["project_id"] = project_id
    migrated["asset_id"] = asset_id
    migrated["asset_version"] = asset_version
    migrated["model_binding"] = {
        "model_spec_path": model_spec_path,
        "model_spec_sha256": model_spec_sha256,
        "rig_signature": rig_signature,
    }
    mappings = migrated.get("mappings")
    if not isinstance(mappings, list):
        mappings = []
        migrated["mappings"] = mappings
    for mapping in mappings:
        if isinstance(mapping, dict):
            mapping["asset_id"] = asset_id

    completed_steps = list(BASE_STEPS)
    approval = migrated.get("audio_mapping_approval")
    if isinstance(approval, dict) and approval.get("status") == "approved" and approval.get("evidence"):
        completed_steps.append("mapping_approved")
    migrated["workflow"] = {"completed_steps": completed_steps}

    missing_evidence = [
        "processed-copy hashes and DSP report",
        "sound registry evidence",
        "animation binding evidence",
        "unified asset-bundle validation",
        "runtime test evidence",
    ]
    if "mapping_approved" not in completed_steps:
        missing_evidence.insert(0, "explicit audio mapping approval")
    migrated["migration"] = {
        "from_schema_version": prior_schema,
        "to_profile": "v11-rc",
        "status": "review_required",
        "missing_evidence": missing_evidence,
        "note": "Migration adds identity only; it does not certify conversion, registration, binding, or runtime testing.",
    }
    return migrated


def write_versioned_json(payload: Any, folder: Path | str, stem: str) -> Path:
    """Write UTF-8 JSON to a new versioned path without overwriting any file."""
    destination_folder = Path(folder)
    destination_folder.mkdir(parents=True, exist_ok=True)
    destination = destination_folder / f"{stem}.json"
    version = 2
    while destination.exists():
        destination = destination_folder / f"{stem}_v{version}.json"
        version += 1
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    destination.write_text(text, encoding="utf-8", newline="\n")
    return destination


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--asset-version", required=True)
    parser.add_argument("--model-spec-path", required=True)
    parser.add_argument("--model-spec-sha256", required=True)
    parser.add_argument("--rig-signature", required=True)
    parser.add_argument("--write-dir", type=Path, help="Opt in to a versioned output; otherwise print a dry-run")
    parser.add_argument("--output-stem", default="audio-manifest-v11")
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        source = json.loads(args.manifest.read_text(encoding="utf-8"))
        migrated = migrate_manifest(
            source,
            project_id=args.project_id,
            asset_id=args.asset_id,
            asset_version=args.asset_version,
            model_spec_path=args.model_spec_path,
            model_spec_sha256=args.model_spec_sha256,
            rig_signature=args.rig_signature,
        )
        if args.write_dir:
            print(write_versioned_json(migrated, args.write_dir, args.output_stem))
        else:
            sys.stdout.write(json.dumps(migrated, ensure_ascii=False, indent=2) + "\n")
    except (OSError, UnicodeError, json.JSONDecodeError, MigrationError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
