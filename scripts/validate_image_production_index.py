#!/usr/bin/env python3
"""Validate the persistent FJZM image-production queue and traceability index."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import PurePosixPath, Path
from typing import Any


ROUND_PATTERN = re.compile(r"^round-\d{3}$")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")
STATUSES = {"queued", "generated", "shown", "revision_requested", "approved", "superseded"}
HASHED_STATUSES = STATUSES - {"queued"}
PATH_FIELDS = ("prompt_path", "negative_prompt_path", "manifest_path")
VISIBLE_STATUSES = {"shown", "revision_requested", "approved", "superseded"}


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _round_path(value: Any) -> bool:
    if not _text(value):
        return False
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    return (
        not path.is_absolute()
        and ".." not in path.parts
        and len(path.parts) >= 4
        and path.parts[0:2] == ("design", "image-rounds")
    )


def validate_index(payload: dict[str, Any]) -> dict[str, list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    project_id = payload.get("project_id")
    if not _text(project_id) or not ID_PATTERN.fullmatch(project_id):
        errors.append("project_id must be a lowercase ASCII identifier")

    rounds = payload.get("rounds")
    if not isinstance(rounds, list) or not rounds:
        errors.append("rounds must be a non-empty list")
        rounds = []

    round_ids = [entry.get("round_id") for entry in rounds if isinstance(entry, dict)]
    if len(round_ids) != len(set(round_ids)):
        errors.append("round_id values must be unique")

    known_ids = {value for value in round_ids if isinstance(value, str)}
    positions = {value: index for index, value in enumerate(round_ids) if isinstance(value, str)}

    for index, entry in enumerate(rounds):
        path = f"rounds[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{path} must be an object")
            continue
        round_id = entry.get("round_id")
        if not _text(round_id) or not ROUND_PATTERN.fullmatch(round_id):
            errors.append(f"{path}.round_id must match round-NNN")
        if not _text(entry.get("round_type")):
            errors.append(f"{path}.round_type is required")
        status = entry.get("status")
        if status not in STATUSES:
            errors.append(f"{path}.status must be one of: {', '.join(sorted(STATUSES))}")

        for identity in ("asset_id", "screen_id"):
            value = entry.get(identity)
            if value is not None and (not _text(value) or not ID_PATTERN.fullmatch(value)):
                errors.append(f"{path}.{identity} must be null or a lowercase ASCII identifier")

        for field in PATH_FIELDS:
            if not _round_path(entry.get(field)):
                errors.append(f"{path}.{field} must stay under design/image-rounds/<round-folder>/")

        dependencies = entry.get("depends_on")
        if not isinstance(dependencies, list):
            errors.append(f"{path}.depends_on must be a list")
            dependencies = []
        for dependency in dependencies:
            if dependency not in known_ids:
                errors.append(f"{path}.depends_on contains unknown dependency {dependency!r}")
            elif isinstance(round_id, str) and positions.get(dependency, index) >= index:
                errors.append(f"{path}.depends_on must reference an earlier round")

        hashes = entry.get("image_sha256")
        valid_hashes = isinstance(hashes, list) and bool(hashes) and all(
            isinstance(value, str) and bool(SHA256_PATTERN.fullmatch(value)) for value in hashes
        )
        if status in HASHED_STATUSES and not valid_hashes:
            errors.append(f"{path}.image_sha256 requires one or more valid SHA-256 hashes for status {status}")

        if status == "approved" and not _text(entry.get("approval_evidence")):
            errors.append(f"{path}.approval_evidence is required for an approved round")

        if entry.get("round_type") == "concept_choice":
            if entry.get("generation_mode") != "separate_calls":
                errors.append(f"{path}.generation_mode must be separate_calls for a concept_choice round")

            calls = entry.get("variant_calls")
            valid_calls = isinstance(calls, list) and len(calls) == 3
            if not valid_calls:
                errors.append(f"{path}.variant_calls must contain exactly three A/B/C calls")
                calls = []

            variants: list[str] = []
            all_quality_passed = True
            call_ids: list[str] = []
            call_hashes: list[str] = []
            for call_index, call in enumerate(calls):
                call_path = f"{path}.variant_calls[{call_index}]"
                if not isinstance(call, dict):
                    errors.append(f"{call_path} must be an object")
                    all_quality_passed = False
                    continue
                variant = call.get("variant")
                variants.append(variant)
                call_id = call.get("call_id")
                if not _text(call_id):
                    errors.append(f"{call_path}.call_id is required")
                else:
                    call_ids.append(call_id)
                if call.get("quality_status") != "passed":
                    all_quality_passed = False
                image_hash = call.get("image_sha256")
                if not isinstance(image_hash, str) or not SHA256_PATTERN.fullmatch(image_hash):
                    errors.append(f"{call_path}.image_sha256 must be a valid SHA-256 hash")
                else:
                    call_hashes.append(image_hash.lower())

            if valid_calls and variants != ["A", "B", "C"]:
                errors.append(f"{path}.variant_calls must be ordered exactly as A, B, C")
            if len(call_ids) != len(set(call_ids)):
                errors.append(f"{path}.variant_calls call_id values must be unique")
            if len(call_hashes) != len(set(call_hashes)):
                errors.append(f"{path}.variant_calls image hashes must be unique")
            if status in VISIBLE_STATUSES and not all_quality_passed:
                errors.append(f"{path}: all A/B/C candidates must pass quality review before showing")

    active_round_id = payload.get("active_round_id")
    if active_round_id is not None and active_round_id not in known_ids:
        errors.append("active_round_id must reference an existing round")
    elif active_round_id is not None:
        active = next((entry for entry in rounds if isinstance(entry, dict) and entry.get("round_id") == active_round_id), None)
        if active and active.get("status") in {"approved", "superseded"}:
            warnings.append("active_round_id points to a closed round")

    return {"errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index", type=Path, help="Path to design/image-production-index.json")
    args = parser.parse_args()

    try:
        with args.index.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"errors": [str(exc)], "warnings": []}, ensure_ascii=False, indent=2))
        return 2

    if not isinstance(payload, dict):
        result = {"errors": ["index root must be an object"], "warnings": []}
    else:
        result = validate_index(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
