#!/usr/bin/env python3
"""Validate an FJZM animation handoff without changing project files."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


PROTECTED = {
    "geometry",
    "uv",
    "texture",
    "textures",
    "bone_topology",
    "bone_names",
    "bone_hierarchy",
    "locators",
}


def _contained_path(root: Path, value: Any, label: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} is required")
        return None
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        errors.append(f"{label} must stay inside the approved workspace")
        return None
    return candidate


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _required_text(container: dict[str, Any], key: str, label: str, errors: list[str]) -> None:
    value = container.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} is required")


def validate_handoff(payload: dict[str, Any], workspace: Path | str) -> dict[str, list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    root = Path(workspace).resolve()

    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for key in ("project_id", "asset_id", "asset_version"):
        _required_text(payload, key, key, errors)

    mode = payload.get("mode")
    if mode not in {"delegated_production", "standalone_revision", "delegated_rig_and_animation"}:
        errors.append("mode must be delegated_production, standalone_revision, or delegated_rig_and_animation")

    source = payload.get("source") if isinstance(payload.get("source"), dict) else {}
    _required_text(source, "rig_signature", "rig_signature", errors)
    if source.get("source_read_only") is not True:
        errors.append("source_read_only must be true")

    model_path = _contained_path(root, source.get("model_path"), "model_path", errors)
    spec_path = _contained_path(root, source.get("model_spec_path"), "model_spec_path", errors)
    if model_path is not None:
        if not model_path.is_file():
            errors.append("model_path does not exist")
        elif source.get("model_sha256") != _sha256(model_path):
            errors.append("model_sha256 mismatch")
    if spec_path is not None:
        if not spec_path.is_file():
            errors.append("model_spec_path does not exist")
        elif source.get("model_spec_sha256") != _sha256(spec_path):
            errors.append("model_spec_sha256 mismatch")

    request = payload.get("request") if isinstance(payload.get("request"), dict) else {}
    animation_ids = request.get("animation_ids")
    if not isinstance(animation_ids, list) or not animation_ids or not all(isinstance(item, str) and item.strip() for item in animation_ids):
        errors.append("animation_ids must contain at least one named animation")
    allowed = request.get("allowed_mutations")
    if not isinstance(allowed, list):
        errors.append("allowed_mutations must be a list")
        allowed_set: set[str] = set()
    else:
        allowed_set = {str(item).lower() for item in allowed}
    if mode == "standalone_revision" and allowed_set & PROTECTED:
        errors.append("standalone_revision cannot allow protected geometry or bone-topology mutations")

    approval = payload.get("approval") if isinstance(payload.get("approval"), dict) else {}
    if approval.get("status") != "approved" or not isinstance(approval.get("evidence"), str) or not approval.get("evidence", "").strip():
        errors.append("approval must be explicitly approved with evidence")

    ownership = payload.get("ownership") if isinstance(payload.get("ownership"), dict) else {}
    if ownership.get("writer_skill") != "fjzm-animation":
        errors.append("writer_skill must be fjzm-animation")
    if ownership.get("single_writer") is not True:
        errors.append("single_writer must be true")
    _required_text(ownership, "write_lock_id", "write_lock_id", errors)
    output_path = _contained_path(root, ownership.get("output_model_path"), "output_model_path", errors)
    if model_path is not None and output_path is not None and model_path == output_path:
        errors.append("output_model_path must differ from source model_path")

    integration = payload.get("integration") if isinstance(payload.get("integration"), dict) else {}
    main_approval = integration.get("main_change_approval") if isinstance(integration.get("main_change_approval"), dict) else {}
    if "bone_topology" in allowed_set:
        if mode != "delegated_rig_and_animation":
            errors.append("bone_topology requires delegated_rig_and_animation mode")
        if main_approval.get("status") != "approved" or not main_approval.get("evidence"):
            errors.append("main_change_approval must be approved with evidence")
        if integration.get("dependent_rebind_required") is not True:
            errors.append("dependent_rebind_required must be true for rig-topology changes")

    _contained_path(root, payload.get("return_contract_path"), "return_contract_path", errors)
    return {"errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handoff", type=Path)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(args.handoff.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"errors": [str(exc)], "warnings": []}, ensure_ascii=False, indent=2))
        return 2
    result = validate_handoff(payload, args.workspace)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
