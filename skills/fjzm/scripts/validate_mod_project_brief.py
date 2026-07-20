#!/usr/bin/env python3
"""Validate a locked Mod-project creation brief before any project files are created."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


ASCII_ID = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
CREATE_TARGET_FIELDS = (
    "minecraft_version",
    "loader",
    "loader_version",
    "mappings",
    "animation_runtime",
    "animation_runtime_version",
    "java_version",
    "gradle_version",
)
ROUTE_BY_STATUS = {
    "existing": "use_existing",
    "create": "create_mod_first",
    "runtime_deferred": "model_first",
}


def validate_brief(brief: dict[str, Any]) -> dict[str, list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if brief.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    status = brief.get("project_status")
    if status not in {"existing", "create", "runtime_deferred"}:
        errors.append("project_status must be existing, create, or runtime_deferred")
        return {"errors": errors, "warnings": warnings}
    if brief.get("edition") != "java":
        errors.append("this Mod project bootstrap requires edition java")

    route_choice = brief.get("route_choice")
    route_evidence = brief.get("route_choice_evidence")
    if route_choice not in set(ROUTE_BY_STATUS.values()) or not isinstance(route_evidence, str) or not route_evidence.strip():
        errors.append("explicit project route choice and verbatim route_choice_evidence are required")
    elif route_choice != ROUTE_BY_STATUS[status]:
        errors.append("route_choice does not match project_status")

    if status == "runtime_deferred":
        if not isinstance(brief.get("deferred_reason"), str) or not brief["deferred_reason"].strip():
            errors.append("runtime_deferred requires deferred_reason")
        restrictions = brief.get("restrictions")
        if not isinstance(restrictions, list) or "no runtime integration claim" not in restrictions:
            errors.append("runtime_deferred requires a no runtime integration claim restriction")
        if brief.get("qualification_status") == "verified" or brief.get("creation_status") == "created":
            errors.append("runtime_deferred cannot be verified or marked created")
        if brief.get("runtime_contract_path") != "runtime-contract.json" or brief.get("runtime_contract_status") != "validated":
            errors.append("runtime_deferred requires a validated runtime-contract.json reference")
        risk = brief.get("runtime_risk")
        if risk not in {"low", "medium", "high"}:
            errors.append("runtime_deferred requires runtime_risk low, medium, or high")
        if brief.get("production_ceiling") not in {"concept_only", "graybox_only", "runtime_neutral_source"}:
            errors.append("runtime_deferred requires a non-platform production_ceiling")
        if risk in {"medium", "high"}:
            recommendation = brief.get("mod_first_recommendation")
            if not isinstance(recommendation, dict) or recommendation.get("status") != "declined" or not recommendation.get("evidence"):
                errors.append("medium/high model_first requires evidence of declining create_mod_first")
            acceptance = brief.get("risk_acceptance")
            if not isinstance(acceptance, dict) or acceptance.get("status") != "approved" or not acceptance.get("evidence"):
                errors.append("medium/high model_first requires explicit risk acceptance evidence")
        return {"errors": errors, "warnings": warnings}

    if status == "existing":
        path = Path(str(brief.get("project_path", "")))
        if not path.is_absolute() or not path.is_dir():
            errors.append("existing project requires an absolute existing project_path")
        return {"errors": errors, "warnings": warnings}

    target = brief.get("target")
    if not isinstance(target, dict):
        errors.append("target object is required")
        target = {}
    for field in CREATE_TARGET_FIELDS:
        if not isinstance(target.get(field), str) or not target[field].strip():
            errors.append(f"target.{field} is required before project creation")

    identity = brief.get("identity")
    if not isinstance(identity, dict):
        errors.append("identity object is required")
    else:
        for field in ("namespace", "mod_id"):
            value = identity.get(field)
            if not isinstance(value, str) or not ASCII_ID.fullmatch(value):
                errors.append(f"identity.{field} must be a stable lowercase ASCII identifier")
        if not isinstance(identity.get("display_name"), str) or not identity["display_name"].strip():
            errors.append("identity.display_name is required")

    destination_value = brief.get("destination_path")
    destination = Path(destination_value) if isinstance(destination_value, str) and destination_value else None
    if destination is None or not destination.is_absolute():
        errors.append("project creation requires an absolute destination path")
    elif destination.exists():
        errors.append("destination already exists; refusing to overwrite or merge during bootstrap")

    evidence = brief.get("compatibility_evidence")
    valid_evidence = False
    if isinstance(evidence, list):
        for item in evidence:
            if (
                isinstance(item, dict)
                and item.get("source_type") == "official_primary"
                and isinstance(item.get("url"), str)
                and item["url"].startswith(("https://", "http://"))
                and item.get("checked_at")
            ):
                valid_evidence = True
    if not valid_evidence:
        errors.append("official primary-source compatibility evidence is required")

    approval = brief.get("creation_approval")
    if not isinstance(approval, dict) or approval.get("status") != "approved" or not approval.get("evidence"):
        errors.append("explicit project-creation approval with evidence is required")

    toolchain = brief.get("toolchain")
    if not isinstance(toolchain, dict):
        errors.append("toolchain object is required")
    else:
        if toolchain.get("shell") != "powershell7":
            errors.append("toolchain.shell must be powershell7 on Windows")
        if toolchain.get("wrapper") != "gradlew.bat":
            errors.append("toolchain.wrapper must be gradlew.bat")
        if toolchain.get("global_install_allowed") is not False:
            errors.append("global installation must remain disabled unless separately approved")
    return {"errors": errors, "warnings": warnings}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        payload = json.loads(args.brief.read_text(encoding="utf-8"))
        result = validate_brief(payload)
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
    print(f"PASS: {args.brief}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
