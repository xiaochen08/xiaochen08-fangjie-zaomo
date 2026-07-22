#!/usr/bin/env python3
"""Validate an FJZM texture handoff without modifying model assets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


PROTECTED = {"geometry", "uv_layout", "rig", "animations", "bones", "bone_hierarchy", "origins", "locators", "model_scale"}
ALWAYS_IMMUTABLE = {"geometry", "rig", "animations", "bones", "bone_hierarchy", "origins", "locators", "model_scale"}
MODES = {"delegated_production", "standalone_retexture", "delegated_uv_and_texture"}


def _required_text(container: dict[str, Any], key: str, label: str, errors: list[str]) -> None:
    value = container.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} is required")


def _contained(root: Path, value: Any, label: str, errors: list[str]) -> Path | None:
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


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verify_input_hash(root: Path, container: dict[str, Any], path_key: str, hash_key: str, errors: list[str]) -> Path | None:
    path = _contained(root, container.get(path_key), path_key, errors)
    if path is None:
        return None
    if not path.is_file():
        errors.append(f"{path_key} does not exist")
    elif container.get(hash_key) != _hash(path):
        errors.append(f"{hash_key} mismatch")
    return path


def _approval(container: dict[str, Any], label: str, errors: list[str]) -> None:
    if container.get("status") != "approved" or not isinstance(container.get("evidence"), str) or not container.get("evidence", "").strip():
        errors.append(f"{label} approval must be approved with evidence")


def _power_of_two(value: Any) -> bool:
    return isinstance(value, int) and value > 0 and value & (value - 1) == 0


def validate_handoff(payload: dict[str, Any], workspace: Path | str) -> dict[str, list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    root = Path(workspace).resolve()

    if payload.get("protocol_version") != "1.0":
        errors.append("protocol_version must be ContractFlow 1.0")
    if payload.get("message_type") != "handoff":
        errors.append("message_type must be handoff")
    if payload.get("from_skill") != "fjzm" or payload.get("to_skill") != "fjzm-texture" or payload.get("stage") != "texture":
        errors.append("central route must be fjzm to fjzm-texture at texture stage")
    for key in ("message_id", "correlation_id", "idempotency_key"):
        _required_text(payload, key, key, errors)
    if not isinstance(payload.get("attempt"), int) or not 0 <= payload.get("attempt", -1) <= 2:
        errors.append("attempt must be 0, 1, or 2")
    writer_lock = payload.get("writer_lock") if isinstance(payload.get("writer_lock"), dict) else {}
    if writer_lock.get("owner") != "fjzm-texture" or writer_lock.get("surface") != "texture" or not writer_lock.get("output_version"):
        errors.append("writer_lock must assign the texture surface to fjzm-texture with an output version")
    dependencies = payload.get("dependencies")
    if not isinstance(dependencies, list) or not any(dep.get("stage") == "geometry" and dep.get("status") == "passed" for dep in dependencies if isinstance(dep, dict)):
        errors.append("geometry dependency must be passed")

    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for key in ("project_id", "asset_id", "asset_version"):
        _required_text(payload, key, key, errors)

    mode = payload.get("mode")
    if mode not in MODES:
        errors.append("mode must be delegated_production, standalone_retexture, or delegated_uv_and_texture")

    source = payload.get("source") if isinstance(payload.get("source"), dict) else {}
    model_path = _verify_input_hash(root, source, "model_path", "model_sha256", errors)
    _verify_input_hash(root, source, "model_spec_path", "model_spec_sha256", errors)
    for key in ("geometry_signature", "rig_signature", "uv_signature"):
        _required_text(source, key, key, errors)
    if source.get("source_read_only") is not True:
        errors.append("source_read_only must be true")

    references = payload.get("references")
    if not isinstance(references, list) or not references:
        errors.append("references must contain at least one approved reference")
    else:
        for index, reference in enumerate(references):
            if not isinstance(reference, dict):
                errors.append(f"references[{index}] must be an object")
                continue
            path = _contained(root, reference.get("path"), f"references[{index}].path", errors)
            if path is not None:
                if not path.is_file():
                    errors.append(f"references[{index}].path does not exist")
                elif reference.get("sha256") != _hash(path):
                    errors.append(f"references[{index}].sha256 mismatch")
            if reference.get("approval_status") != "approved":
                errors.append(f"references[{index}] must be approved")

    request = payload.get("request") if isinstance(payload.get("request"), dict) else {}
    allowed = request.get("allowed_mutations")
    allowed_set = {str(item).lower() for item in allowed} if isinstance(allowed, list) else set()
    if not isinstance(allowed, list):
        errors.append("allowed_mutations must be a list")
    if mode in {"standalone_retexture", "delegated_production"} and allowed_set & PROTECTED:
        errors.append(f"{mode} cannot allow protected geometry, UV, rig, or animation mutations")
    for surface in sorted(allowed_set & ALWAYS_IMMUTABLE):
        errors.append(f"immutable model surface cannot be changed by texture: {surface}")

    analysis = payload.get("analysis") if isinstance(payload.get("analysis"), dict) else {}
    if analysis.get("reference_scene_lighting_recorded") is not True:
        errors.append("reference scene lighting analysis is required")
    if analysis.get("intrinsic_material_cues_separated") is not True:
        errors.append("intrinsic material cues must be separated from scene lighting")
    if analysis.get("neutral_albedo") is not True:
        errors.append("neutral_albedo must be true")
    if analysis.get("scene_lighting_baked") is not False:
        errors.append("scene_lighting_baked must be false")

    texture = payload.get("texture") if isinstance(payload.get("texture"), dict) else {}
    atlas = texture.get("atlas")
    if not isinstance(atlas, list) or len(atlas) != 2 or not all(_power_of_two(value) for value in atlas):
        errors.append("atlas must contain two power-of-two dimensions")
        atlas_width = atlas_height = 0
    else:
        atlas_width, atlas_height = atlas
    if not isinstance(texture.get("texels_per_unit"), (int, float)) or texture.get("texels_per_unit", 0) <= 0:
        errors.append("texels_per_unit must be positive")
    if texture.get("nearest_neighbor") is not True:
        errors.append("nearest_neighbor must be true")
    if texture.get("antialiasing") is not False:
        errors.append("antialiasing must be false")
    if texture.get("ao_policy") != "local_opaque_contact_only":
        errors.append("ao_policy must be local_opaque_contact_only")
    if texture.get("edge_accent_policy") != "conditional_1_2_px":
        errors.append("edge_accent_policy must be conditional_1_2_px")
    materials = texture.get("material_library")
    if not isinstance(materials, list) or not materials:
        errors.append("material_library must not be empty")
    else:
        for index, material in enumerate(materials):
            ramp = material.get("ramp") if isinstance(material, dict) else None
            if not isinstance(ramp, list) or len(set(ramp)) < 3:
                errors.append(f"material_library[{index}].ramp must contain at least 3 unique colors")

    uv = payload.get("uv") if isinstance(payload.get("uv"), dict) else {}
    if uv.get("uv_signature") != source.get("uv_signature"):
        errors.append("uv_signature must match the frozen source UV signature")
    if uv.get("uniform_texel_density") is not True:
        errors.append("uniform_texel_density must be true or explicitly reapproved")
    if not isinstance(uv.get("padding_pixels"), int) or uv.get("padding_pixels", -1) < 1:
        errors.append("padding_pixels must be at least 1")
    if not isinstance(uv.get("seam_pairs"), list):
        errors.append("seam_pairs must be a list")

    eye = uv.get("eye_region") if isinstance(uv.get("eye_region"), dict) else {}
    eye_mode = eye.get("mode")
    if eye_mode not in {"static", "atlas_frames", "separate_textures", "geometry_eyelid"}:
        errors.append("eye_region.mode is invalid")
    if eye_mode in {"atlas_frames", "separate_textures", "geometry_eyelid"}:
        runtime = eye.get("runtime_support") if isinstance(eye.get("runtime_support"), dict) else {}
        if runtime.get("status") != "supported" or not runtime.get("adapter"):
            errors.append("eye animation runtime support must be supported with a named adapter")
    if eye_mode == "atlas_frames":
        frames = eye.get("frames")
        if not isinstance(frames, list) or len(frames) not in {2, 3}:
            errors.append("atlas_frames requires exactly 2 or 3 eye frames")
        if isinstance(frames, list):
            for index, frame in enumerate(frames):
                if not isinstance(frame, dict):
                    errors.append(f"eye frame {index} must be an object")
                    continue
                values = [frame.get(key) for key in ("x", "y", "w", "h")]
                if not all(isinstance(value, int) for value in values):
                    errors.append(f"eye frame {index} coordinates must be integers")
                    continue
                x, y, width, height = values
                if x < 0 or y < 0 or width <= 0 or height <= 0 or x + width > atlas_width or y + height > atlas_height:
                    errors.append(f"eye frame {index} is outside atlas bounds")

    shader = payload.get("shader") if isinstance(payload.get("shader"), dict) else {}
    _verify_input_hash(root, shader, "contract_path", "contract_sha256", errors)

    approval = payload.get("approval") if isinstance(payload.get("approval"), dict) else {}
    _approval(approval.get("analysis_plan") if isinstance(approval.get("analysis_plan"), dict) else {}, "analysis_plan", errors)
    _approval(approval.get("texture_production") if isinstance(approval.get("texture_production"), dict) else {}, "texture_production", errors)

    ownership = payload.get("ownership") if isinstance(payload.get("ownership"), dict) else {}
    if ownership.get("writer_skill") != "fjzm-texture":
        errors.append("writer_skill must be fjzm-texture")
    if ownership.get("single_writer") is not True:
        errors.append("single_writer must be true")
    _required_text(ownership, "write_lock_id", "write_lock_id", errors)
    output_model = _contained(root, ownership.get("output_model_path"), "output_model_path", errors)
    _contained(root, ownership.get("output_texture_path"), "output_texture_path", errors)
    if model_path is not None and output_model is not None and model_path == output_model:
        errors.append("output_model_path must differ from source model_path")

    integration = payload.get("integration") if isinstance(payload.get("integration"), dict) else {}
    main_approval = integration.get("main_change_approval") if isinstance(integration.get("main_change_approval"), dict) else {}
    if mode == "delegated_uv_and_texture" and "uv_layout" in allowed_set:
        if main_approval.get("status") != "approved" or not main_approval.get("evidence"):
            errors.append("main_change_approval must be approved with evidence for UV changes")

    _contained(root, payload.get("return_contract_path"), "return_contract_path", errors)
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
