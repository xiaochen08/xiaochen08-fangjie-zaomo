#!/usr/bin/env python3
"""Validate an FJZM animation handoff without changing project files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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
    "origins",
    "locators",
}

SUPPORTED_BACKENDS = {"blockbench", "blender_epicfight"}
SUPPORTED_MOTION_DOMAINS = {"ambient", "mechanism", "locomotion", "combat", "interaction", "destruction"}
ASCII_ID = re.compile(r"^[a-z0-9][a-z0-9_.:/-]*$")


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


def _ascii_text(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip() or not value.isascii():
        errors.append(f"{label} must use ASCII-safe names")


def _version_locked(container: dict[str, Any], key: str, errors: list[str]) -> None:
    _required_text(container, key, key, errors)


def _validate_blender_contract(
    payload: dict[str, Any], source: dict[str, Any], ownership: dict[str, Any], root: Path, errors: list[str]
) -> None:
    contract = payload.get("backend_contract") if isinstance(payload.get("backend_contract"), dict) else {}
    target = contract.get("target") if isinstance(contract.get("target"), dict) else {}
    if target.get("edition") != "java":
        errors.append("Blender / Epic Fight backend requires Java edition")
    for key in (
        "minecraft_version",
        "loader",
        "loader_version",
        "animation_runtime",
        "animation_runtime_version",
    ):
        _version_locked(target, key, errors)
    if target.get("animation_runtime") != "epicfight":
        errors.append("animation_runtime must be epicfight for blender_epicfight")

    toolchain = contract.get("toolchain") if isinstance(contract.get("toolchain"), dict) else {}
    for key in ("blender_version", "exporter_name", "exporter_version", "checked_at"):
        _version_locked(toolchain, key, errors)
    source_url = toolchain.get("exporter_source_url")
    if not isinstance(source_url, str) or not source_url.startswith("https://"):
        errors.append("exporter_source_url must be an official HTTPS source")

    bridge = contract.get("rig_bridge") if isinstance(contract.get("rig_bridge"), dict) else {}
    if bridge.get("source_rig_signature") != source.get("rig_signature"):
        errors.append("source_rig_signature must match the locked source rig_signature")
    _required_text(bridge, "target_armature", "target_armature", errors)
    if bridge.get("mapping_policy") != "create_versioned_map":
        errors.append("mapping_policy must be create_versioned_map")
    coordinate_system = bridge.get("coordinate_system") if isinstance(bridge.get("coordinate_system"), dict) else {}
    _required_text(coordinate_system, "up", "coordinate_system.up", errors)
    _required_text(coordinate_system, "forward", "coordinate_system.forward", errors)
    unit_scale = bridge.get("unit_scale")
    if not isinstance(unit_scale, (int, float)) or unit_scale <= 0:
        errors.append("unit_scale must be a positive number")

    control = contract.get("control") if isinstance(contract.get("control"), dict) else {}
    if control.get("authoring_mode") != "blender_python":
        errors.append("authoring_mode must be blender_python")
    if control.get("visual_review") != "interactive_blender":
        errors.append("visual_review must be interactive_blender")
    if control.get("runtime_review") != "required":
        errors.append("runtime_review must be required")

    output_project = ownership.get("output_project_path")
    if isinstance(output_project, str) and Path(output_project).suffix.lower() != ".blend":
        errors.append("output_project_path must end in .blend for blender_epicfight")
    for key in ("output_runtime_directory", "rig_map_path", "action_library_path"):
        path = _contained_path(root, ownership.get(key), key, errors)
        if path is not None:
            _ascii_text(ownership.get(key), key, errors)


def validate_handoff(payload: dict[str, Any], workspace: Path | str) -> dict[str, list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    root = Path(workspace).resolve()

    if payload.get("protocol_version") != "1.0":
        errors.append("protocol_version must be ContractFlow 1.0")
    if payload.get("message_type") != "handoff":
        errors.append("message_type must be handoff")
    if payload.get("from_skill") != "fjzm" or payload.get("to_skill") != "fjzm-animation" or payload.get("stage") != "animation":
        errors.append("central route must be fjzm to fjzm-animation at animation stage")
    for key in ("message_id", "correlation_id", "idempotency_key"):
        _required_text(payload, key, key, errors)
    if not isinstance(payload.get("attempt"), int) or not 0 <= payload.get("attempt", -1) <= 2:
        errors.append("attempt must be 0, 1, or 2")
    writer_lock = payload.get("writer_lock") if isinstance(payload.get("writer_lock"), dict) else {}
    if writer_lock.get("owner") != "fjzm-animation" or writer_lock.get("surface") != "animation" or not writer_lock.get("output_version"):
        errors.append("writer_lock must assign the animation surface to fjzm-animation with an output version")
    dependencies = payload.get("dependencies")
    if not isinstance(dependencies, list) or not any(dep.get("stage") == "geometry" and dep.get("status") == "passed" for dep in dependencies if isinstance(dep, dict)):
        errors.append("geometry dependency must be passed")

    if payload.get("schema_version") != 2:
        errors.append("schema_version must be 2")
    for key in ("project_id", "asset_id", "asset_version"):
        _required_text(payload, key, key, errors)

    mode = payload.get("mode")
    if mode not in {"delegated_production", "standalone_revision", "delegated_rig_and_animation"}:
        errors.append("mode must be delegated_production, standalone_revision, or delegated_rig_and_animation")

    backend = payload.get("animation_backend")
    if backend not in SUPPORTED_BACKENDS:
        errors.append("animation_backend must be blockbench or blender_epicfight")
    motion_domain = payload.get("motion_domain")
    if motion_domain not in SUPPORTED_MOTION_DOMAINS:
        errors.append("motion_domain must be ambient, mechanism, locomotion, combat, interaction, or destruction")

    source = payload.get("source") if isinstance(payload.get("source"), dict) else {}
    for key in ("geometry_signature", "rig_signature", "uv_signature", "locator_signature"):
        _required_text(source, key, key, errors)
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
    else:
        for animation_id in animation_ids:
            if not ASCII_ID.fullmatch(animation_id):
                errors.append("animation_ids must use lowercase ASCII-safe runtime identifiers")
    allowed = request.get("allowed_mutations")
    if not isinstance(allowed, list):
        errors.append("allowed_mutations must be a list")
        allowed_set: set[str] = set()
    else:
        allowed_set = {str(item).lower() for item in allowed}
    if mode == "standalone_revision" and allowed_set & PROTECTED:
        errors.append("standalone_revision cannot allow protected geometry or bone-topology mutations")
    for surface in sorted(allowed_set & PROTECTED):
        errors.append(f"immutable model surface cannot be changed by animation: {surface}")

    approval = payload.get("approval") if isinstance(payload.get("approval"), dict) else {}
    if approval.get("status") != "approved" or not isinstance(approval.get("evidence"), str) or not approval.get("evidence", "").strip():
        errors.append("approval must be explicitly approved with evidence")

    ownership = payload.get("ownership") if isinstance(payload.get("ownership"), dict) else {}
    if ownership.get("writer_skill") != "fjzm-animation":
        errors.append("writer_skill must be fjzm-animation")
    if ownership.get("single_writer") is not True:
        errors.append("single_writer must be true")
    _required_text(ownership, "write_lock_id", "write_lock_id", errors)
    output_path = _contained_path(root, ownership.get("output_project_path"), "output_project_path", errors)
    if output_path is not None:
        _ascii_text(ownership.get("output_project_path"), "output_project_path", errors)
    if model_path is not None and output_path is not None and model_path == output_path:
        errors.append("output_project_path must differ from source model_path")
    if backend == "blockbench" and output_path is not None and output_path.suffix.lower() != ".bbmodel":
        errors.append("output_project_path must end in .bbmodel for blockbench")
    if backend == "blender_epicfight":
        _validate_blender_contract(payload, source, ownership, root, errors)
    if motion_domain == "combat":
        if request.get("combat_behavior_required") is not True:
            errors.append("request.combat_behavior_required must be true for motion_domain combat")
        combat_path = _contained_path(root, ownership.get("combat_behavior_path"), "combat_behavior_path", errors)
        if combat_path is not None:
            _ascii_text(ownership.get("combat_behavior_path"), "combat_behavior_path", errors)

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
