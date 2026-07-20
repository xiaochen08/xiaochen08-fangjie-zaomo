#!/usr/bin/env python3
"""Validate one Minecraft asset's shader, lighting, and material compatibility contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


TIERS = {"vanilla_baseline", "common_shader_safe", "specified_shader_pack", "pbr_targeted"}
CLAIMS = {"baseline_only", "named_targets_only"}
LOADERS = {"iris", "optifine", "other"}
MATERIAL_STANDARDS = {"none", "labpbr", "other"}
TRANSLUCENCY = {"opaque", "cutout", "translucent", "mixed"}
WORLD_LIGHT = {"none", "runtime_block_light", "dynamic_light_integration"}
CASE_STATUS = {"not_run", "passed", "failed", "blocked"}
BASE_CASES = {"no_shader_daylight", "no_shader_dark", "side_lighting"}
TARGET_CASES = {"target_shader_daylight", "target_shader_dark"}


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _relative_asset_path(value: Any) -> bool:
    if not _text(value):
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def _valid_source_url(value: Any) -> bool:
    if not _text(value):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"https", "http"} and bool(parsed.netloc)


def validate_contract(payload: dict[str, Any]) -> dict[str, list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for field in ("project_id", "asset_id", "asset_version"):
        if not _text(payload.get(field)):
            errors.append(f"{field} is required")
    if payload.get("edition") not in {"java", "bedrock"}:
        errors.append("edition must be java or bedrock")

    tier = payload.get("compatibility_tier")
    if tier not in TIERS:
        errors.append(f"compatibility_tier must be one of: {', '.join(sorted(TIERS))}")
    claim = payload.get("support_claim")
    if claim not in CLAIMS:
        errors.append("support_claim must be baseline_only or named_targets_only; universal shader-pack claims are forbidden")
    if payload.get("baseline_required") is not True:
        errors.append("baseline_required must be true")

    target = payload.get("target_stack")
    if not isinstance(target, dict):
        errors.append("target_stack must be an object")
        target = {}
    if target.get("minecraft_version_status") != "locked" or not _text(target.get("minecraft_version")):
        errors.append("target_stack requires a locked exact Minecraft version")

    named_target = tier in {"specified_shader_pack", "pbr_targeted"}
    if named_target:
        if claim != "named_targets_only":
            errors.append("specified shader/PBR targets require support_claim named_targets_only")
        if (
            target.get("shader_loader_status") != "locked"
            or target.get("shader_loader") not in LOADERS
            or not _text(target.get("shader_loader_version"))
        ):
            errors.append("named shader targets require a locked shader loader and exact loader version")
        packs = target.get("shader_packs")
        locked_packs = []
        if isinstance(packs, list):
            locked_packs = [
                pack for pack in packs
                if isinstance(pack, dict)
                and pack.get("status") == "locked"
                and _text(pack.get("name"))
                and _text(pack.get("version"))
                and _valid_source_url(pack.get("source_url"))
                and _text(pack.get("checked_at"))
            ]
        if not locked_packs:
            errors.append("named shader targets require at least one locked exact shader pack with version, source_url, and checked_at")

    materials = payload.get("materials")
    if not isinstance(materials, dict):
        errors.append("materials must be an object")
        materials = {}
    if not _relative_asset_path(materials.get("base_texture")):
        errors.append("materials.base_texture must be a contained relative asset path")
    if materials.get("painted_lighting_policy") != "neutral_only":
        errors.append("materials.painted_lighting_policy must be neutral_only to prevent double lighting")
    translucency = materials.get("translucency")
    if translucency not in TRANSLUCENCY:
        errors.append(f"materials.translucency must be one of: {', '.join(sorted(TRANSLUCENCY))}")
    if translucency in {"translucent", "mixed"} and not _text(materials.get("render_layer")):
        errors.append("translucent or mixed materials require an explicit materials.render_layer")
    for field in ("emissive_mask", "normal_map", "specular_map", "roughness_map", "metalness_map"):
        value = materials.get(field)
        if value is not None and not _relative_asset_path(value):
            errors.append(f"materials.{field} must be null or a contained relative asset path")

    if tier == "pbr_targeted":
        if target.get("material_standard") not in MATERIAL_STANDARDS - {"none"} or not _text(target.get("material_standard_version")):
            errors.append("pbr_targeted requires a locked PBR material standard and version")
        has_lab_style = _text(materials.get("normal_map")) and _text(materials.get("specular_map"))
        has_metal_style = _text(materials.get("normal_map")) and _text(materials.get("roughness_map")) and _text(materials.get("metalness_map"))
        if not (has_lab_style or has_metal_style):
            errors.append("pbr_targeted requires normal/specular or roughness/metalness maps")

    emissive = payload.get("emissive")
    if not isinstance(emissive, dict):
        errors.append("emissive must be an object")
        emissive = {}
    if emissive.get("visual_emissive") is True and not _text(materials.get("emissive_mask")):
        errors.append("visual emissive requires materials.emissive_mask")
    if emissive.get("world_light") not in WORLD_LIGHT:
        errors.append(f"emissive.world_light must be one of: {', '.join(sorted(WORLD_LIGHT))}")
    if emissive.get("world_light") in WORLD_LIGHT - {"none"} and not _text(emissive.get("world_light_runtime_owner")):
        errors.append("world-light behavior requires emissive.world_light_runtime_owner; an emissive texture alone does not light the world")
    if emissive.get("bloom_dependency") not in {"none", "optional", "required"}:
        errors.append("emissive.bloom_dependency must be none, optional, or required")

    fallback = payload.get("fallback")
    if not isinstance(fallback, dict):
        errors.append("fallback must be an object")
        fallback = {}
    if fallback.get("no_shader_supported") is not True:
        errors.append("fallback.no_shader_supported must be true")
    if fallback.get("missing_optional_maps") != "base_texture_only":
        errors.append("fallback.missing_optional_maps must be base_texture_only")

    matrix = payload.get("test_matrix")
    if not isinstance(matrix, list):
        errors.append("test_matrix must be a list")
        matrix = []
    cases: dict[str, dict[str, Any]] = {}
    for index, case in enumerate(matrix):
        if not isinstance(case, dict) or not _text(case.get("case_id")):
            errors.append(f"test_matrix[{index}].case_id is required")
            continue
        case_id = case["case_id"]
        if case_id in cases:
            errors.append(f"duplicate test case: {case_id}")
        cases[case_id] = case
        if case.get("status") not in CASE_STATUS:
            errors.append(f"test_matrix[{index}].status is invalid")
        if not isinstance(case.get("evidence"), list):
            errors.append(f"test_matrix[{index}].evidence must be a list")

    required_cases = set(BASE_CASES)
    if named_target:
        required_cases.update(TARGET_CASES)
    if emissive.get("visual_emissive") is True:
        required_cases.add("emissive_dark")
    if emissive.get("bloom_dependency") in {"optional", "required"}:
        required_cases.add("bloom_stress")
    if translucency in {"translucent", "mixed"}:
        required_cases.add("transparency_overlap")
    for case_id in sorted(required_cases - cases.keys()):
        errors.append(f"test_matrix requires case_id {case_id}")

    qualification = payload.get("qualification_status")
    if qualification not in {"unverified", "compatible", "verified"}:
        errors.append("qualification_status must be unverified, compatible, or verified")
    if qualification == "verified":
        for case_id in sorted(required_cases):
            case = cases.get(case_id, {})
            if case.get("required") is not True or case.get("status") != "passed":
                errors.append(f"verified requires all required test cases must be passed: {case_id}")
            evidence = case.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                errors.append(f"verified test case requires evidence: {case_id}")
        if fallback.get("fallback_verified") is not True:
            errors.append("verified requires fallback.fallback_verified true")
    elif qualification == "compatible":
        warnings.append("compatible is not verified; preserve incomplete runtime evidence")

    return {"errors": errors, "warnings": warnings}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        payload = json.loads(args.contract.read_text(encoding="utf-8"))
        result = validate_contract(payload)
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
    print(f"PASS: {args.contract}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
