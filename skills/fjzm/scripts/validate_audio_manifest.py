#!/usr/bin/env python3
"""Validate audio-manifest.json and optional runtime/event registrations."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


EVENT_ID = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_.-]+$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
NUMBER_ONLY = re.compile(r"^\d+$")
ASSET_ID = re.compile(r"^[a-z0-9_-]+$")
OWNERS = {"animation_keyframe", "state_lifecycle", "gameplay_event", "projectile_collision"}
WORKFLOW_ORDER = [
    "asset_identity_locked",
    "attachments_inventoried",
    "sources_inspected",
    "mapping_proposed",
    "mapping_approved",
    "copies_converted",
    "events_registered",
    "animation_bound",
    "manifest_validated",
    "runtime_tested",
]


def _reference_path(base: Path, value: str, *, contain: bool) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = Path(value)
    candidate = raw.resolve() if raw.is_absolute() else (base / raw).resolve()
    if contain:
        try:
            candidate.relative_to(base.resolve())
        except ValueError:
            return None
    return candidate


def _event_aliases(event_id: str) -> set[str]:
    if ":" not in event_id:
        return {event_id}
    namespace, path = event_id.split(":", 1)
    return {event_id, path, f"{namespace}:{path}"}


def _registry_keys(sounds_data: dict[str, Any]) -> set[str]:
    definitions = sounds_data.get("sound_definitions")
    if isinstance(definitions, dict):
        return set(definitions)
    return {key for key in sounds_data if key != "format_version"}


def _collect_sound_events(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "sound_event" and isinstance(child, str):
                found.add(child)
            else:
                found.update(_collect_sound_events(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_collect_sound_events(child))
    return found


def _collect_event_values(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"event_id", "sound_event", "visual_event", "visual_telegraph"} and isinstance(child, str):
                found.add(child)
            else:
                found.update(_collect_event_values(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_collect_event_values(child))
    return found


def _shared_values(value: Any, key: str) -> set[str]:
    if not isinstance(value, list):
        return set()
    found: set[str] = set()
    for item in value:
        if isinstance(item, str):
            found.add(item)
        elif isinstance(item, dict) and isinstance(item.get(key), str):
            found.add(item[key])
    return found


def _actual_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_manifest(
    manifest: dict[str, Any],
    base_dir: Path | str,
    sounds_data: dict[str, Any] | None = None,
    event_table: Any | None = None,
    model_spec_data: dict[str, Any] | None = None,
    localizations: dict[str, Any] | None = None,
    visual_events: Any | None = None,
    shared_library_data: dict[str, Any] | None = None,
) -> dict[str, list[str]]:
    base = Path(base_dir).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if manifest.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    project_id = manifest.get("project_id")
    asset_id = manifest.get("asset_id")
    asset_version = manifest.get("asset_version")
    if not isinstance(project_id, str) or not ASSET_ID.fullmatch(project_id):
        errors.append("project_id must be lowercase ASCII")
    if not isinstance(asset_id, str) or not ASSET_ID.fullmatch(asset_id):
        errors.append("asset_id must be lowercase ASCII")
    if not isinstance(asset_version, str) or not asset_version.strip():
        errors.append("asset_version is required")

    model_binding = manifest.get("model_binding")
    if not isinstance(model_binding, dict):
        errors.append("model_binding object is required")
        model_binding = {}
    model_spec_path = _reference_path(base, model_binding.get("model_spec_path", ""), contain=True)
    expected_model_hash = model_binding.get("model_spec_sha256", "")
    rig_signature = model_binding.get("rig_signature")
    if model_spec_path is None or not model_spec_path.is_file():
        errors.append("model_binding model-spec file is missing or outside the project root")
    else:
        actual_model_hash = _actual_sha256(model_spec_path)
        if not isinstance(expected_model_hash, str) or not SHA256.fullmatch(expected_model_hash):
            errors.append("model_binding.model_spec_sha256 must be a lowercase SHA-256")
        elif actual_model_hash != expected_model_hash:
            errors.append("model_binding.model_spec_sha256 does not match model-spec file")
        if model_spec_data is None:
            try:
                model_spec_data = json.loads(model_spec_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                errors.append("model-spec file cannot be read as UTF-8 JSON")
    if not isinstance(rig_signature, str) or not rig_signature.strip():
        errors.append("model_binding.rig_signature is required")

    if isinstance(model_spec_data, dict):
        if model_spec_data.get("project_id") != project_id:
            errors.append("model-spec project_id mismatch")
        if model_spec_data.get("asset_id") != asset_id:
            errors.append("model-spec asset_id mismatch; cross-model binding is forbidden")
        if model_spec_data.get("asset_version") != asset_version:
            errors.append("model-spec asset_version mismatch")
        spec_rig = (model_spec_data.get("animation_system") or {}).get("rig_signature")
        if spec_rig != rig_signature:
            errors.append("model-spec rig_signature mismatch")

    workflow = manifest.get("workflow")
    completed_steps = workflow.get("completed_steps") if isinstance(workflow, dict) else None
    if not isinstance(completed_steps, list):
        errors.append("workflow.completed_steps list is required")
    elif completed_steps != WORKFLOW_ORDER[: len(completed_steps)]:
        errors.append("workflow steps are out of order or contain an unknown step")
    target = manifest.get("target")
    if not isinstance(target, dict):
        errors.append("target object is required")
    else:
        for field in ("edition", "minecraft_version", "animation_runtime"):
            if not target.get(field):
                errors.append(f"target.{field} is required")
    approval = manifest.get("audio_mapping_approval")
    if not isinstance(approval, dict) or approval.get("status") != "approved" or not approval.get("evidence"):
        errors.append("audio_mapping_approval requires approved status and evidence")
    budgets = manifest.get("budgets")
    if not isinstance(budgets, dict):
        errors.append("budgets object is required")
    else:
        for field in ("max_simultaneous_instances", "attenuation_distance", "streaming_policy"):
            if budgets.get(field) in (None, ""):
                errors.append(f"budgets.{field} is required")

    mappings = manifest.get("mappings")
    if not isinstance(mappings, list) or not mappings:
        errors.append("mappings must be a non-empty list")
        return {"errors": errors, "warnings": warnings}

    registered = _registry_keys(sounds_data) if sounds_data is not None else None
    event_sounds = _collect_sound_events(event_table) if event_table is not None else None
    visual_event_ids = _collect_event_values(visual_events) if visual_events is not None else None
    output_paths: set[Path] = set()
    variant_groups: dict[str, list[tuple[str, float | None, str]]] = {}

    for index, mapping in enumerate(mappings):
        label = f"mappings[{index}]"
        if not isinstance(mapping, dict):
            errors.append(f"{label} must be an object")
            continue
        source_name = mapping.get("source_file", "")
        user_label = mapping.get("user_label_zh", "")
        mapping_asset = mapping.get("asset_id")
        if mapping_asset != asset_id:
            errors.append(f"{label} cross-model binding: mapping asset_id must equal manifest asset_id")
        if NUMBER_ONLY.fullmatch(Path(source_name).stem or "") and not str(user_label).strip():
            errors.append(f"{label} numbered source is unassigned; user_label_zh is required")

        event_id = mapping.get("event_id", "")
        if not isinstance(event_id, str) or not EVENT_ID.fullmatch(event_id):
            errors.append(f"{label}.event_id must be lowercase ASCII namespace:path")
        elif not mapping.get("shared_audio_library"):
            event_path = event_id.split(":", 1)[1]
            if not (event_path == asset_id or event_path.startswith(f"{asset_id}.") or event_path.startswith(f"{asset_id}/")):
                errors.append(f"{label}.event_id must be scoped to asset_id '{asset_id}'")
        elif mapping.get("shared_audio_approved") is not True:
            errors.append(f"{label} shared_audio_library requires explicit approval")
        if mapping.get("shared_audio_library") and shared_library_data is not None:
            library_id = mapping.get("shared_audio_library")
            if shared_library_data.get("library_id") != library_id:
                errors.append(f"{label} shared library_id mismatch")
            consumers = _shared_values(shared_library_data.get("consumers"), "asset_id")
            if asset_id not in consumers:
                errors.append(f"{label} asset is not an authorized shared-library consumer")
            shared_events = _shared_values(shared_library_data.get("events"), "event_id")
            if event_id not in shared_events:
                errors.append(f"{label} event is absent from shared library")
        source_hash = mapping.get("source_sha256", "")
        if not isinstance(source_hash, str) or not SHA256.fullmatch(source_hash):
            errors.append(f"{label}.source_sha256 must be a lowercase SHA-256")

        source_path = _reference_path(base, source_name, contain=False)
        if source_path is None or not source_path.is_file():
            errors.append(f"{label} source file is missing: {source_name}")
        elif SHA256.fullmatch(str(source_hash)) and _actual_sha256(source_path) != source_hash:
            errors.append(f"{label}.source_sha256 does not match source file")

        output_name = mapping.get("output_file", "")
        output_path = _reference_path(base, output_name, contain=True)
        if output_path is None:
            errors.append(f"{label}.output_file must stay inside the project root")
        else:
            if mapping.get("approved") is True and not output_path.is_file():
                errors.append(f"{label} approved output file is missing: {output_name}")
            if output_path in output_paths:
                errors.append(f"{label}.output_file duplicates another mapping")
            output_paths.add(output_path)
            relative_parts = output_path.relative_to(base).parts
            if mapping.get("shared_audio_library"):
                if len(relative_parts) < 3 or relative_parts[0] != "sounds" or relative_parts[1] != "shared":
                    errors.append(f"{label}.output_file for shared audio must be scoped under sounds/shared/")
            elif len(relative_parts) < 3 or relative_parts[0] != "sounds" or relative_parts[1] != asset_id:
                errors.append(f"{label}.output_file must be scoped under sounds/{asset_id}/")

        owner = mapping.get("owner")
        if owner not in OWNERS:
            errors.append(f"{label}.owner must be one of {sorted(OWNERS)}")
        if owner == "animation_keyframe":
            if not mapping.get("animation_id") or not isinstance(mapping.get("time_seconds"), (int, float)):
                errors.append(f"{label} animation_keyframe requires animation_id and time_seconds")
        if mapping.get("role") == "loop":
            if not mapping.get("stop_event"):
                errors.append(f"{label} loop requires stop_event")
            if not mapping.get("interruption_rule"):
                errors.append(f"{label} loop requires interruption_rule")
        if "projectile_impact" in str(event_id) and owner != "projectile_collision":
            errors.append(f"{label} projectile impact must use owner projectile_collision")

        if mapping.get("critical_cue") is True:
            subtitle_key = mapping.get("subtitle_key")
            if not subtitle_key:
                errors.append(f"{label} critical cue requires subtitle_key")
            if not mapping.get("visual_telegraph"):
                errors.append(f"{label} critical cue requires visual_telegraph")
            if localizations is not None and subtitle_key:
                for locale in ("zh_cn", "en_us"):
                    table = localizations.get(locale)
                    if not isinstance(table, dict) or subtitle_key not in table:
                        errors.append(f"{label} subtitle key missing from {locale}: {subtitle_key}")
            if visual_event_ids is not None and isinstance(event_id, str):
                aliases = _event_aliases(event_id)
                telegraph = mapping.get("visual_telegraph")
                if aliases.isdisjoint(visual_event_ids) and telegraph not in visual_event_ids:
                    errors.append(f"{label} visual telegraph event missing: {event_id}")

        if mapping.get("origin") == "ai_generated":
            provenance = mapping.get("provenance")
            required = ("provider", "generation_model", "prompt", "generated_at", "license_status", "attribution")
            if not isinstance(provenance, dict) or any(not provenance.get(field) for field in required):
                errors.append(f"{label} AI-generated audio requires complete provenance and license fields")

        if isinstance(event_id, str) and EVENT_ID.fullmatch(event_id):
            aliases = _event_aliases(event_id)
            if registered is not None and aliases.isdisjoint(registered):
                errors.append(f"{label} event_id is absent from sounds registry")
            if owner == "animation_keyframe" and event_sounds is not None and aliases.isdisjoint(event_sounds):
                errors.append(f"{label} event_id is absent from animation event table")

        variant_group = mapping.get("variant_group")
        if isinstance(variant_group, str) and variant_group.strip():
            qa = mapping.get("qa")
            rms = qa.get("rms_dbfs") if isinstance(qa, dict) else None
            variant_groups.setdefault(variant_group, []).append(
                (event_id, float(rms) if isinstance(rms, (int, float)) else None, label)
            )

    for group, variants in variant_groups.items():
        events = {event for event, _, _ in variants}
        if len(events) != 1:
            errors.append(f"variant_group must share one event_id: {group}")
        levels = [level for _, level, _ in variants if level is not None]
        if len(levels) != len(variants):
            errors.append(f"variant_group requires qa.rms_dbfs for every variant: {group}")
        elif levels and max(levels) - min(levels) > 3.0:
            errors.append(f"variant_group level spread exceeds 3 dB: {group}")

    return {"errors": errors, "warnings": warnings}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--sounds-json", type=Path)
    parser.add_argument("--event-table", type=Path)
    parser.add_argument("--model-spec", type=Path)
    parser.add_argument("--localizations", type=Path)
    parser.add_argument("--visual-events", type=Path)
    parser.add_argument("--shared-library", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        manifest = _load_json(args.manifest)
        root = (args.project_root or args.manifest.parent).resolve()
        sounds = _load_json(args.sounds_json) if args.sounds_json else None
        events = _load_json(args.event_table) if args.event_table else None
        model_spec = _load_json(args.model_spec) if args.model_spec else None
        localizations = _load_json(args.localizations) if args.localizations else None
        visual_events = _load_json(args.visual_events) if args.visual_events else None
        shared_library = _load_json(args.shared_library) if args.shared_library else None
        result = validate_manifest(
            manifest,
            root,
            sounds,
            events,
            model_spec,
            localizations,
            visual_events,
            shared_library,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for warning in result["warnings"]:
        print(f"WARNING: {warning}")
    for error in result["errors"]:
        print(f"ERROR: {error}")
    if result["errors"]:
        print(f"FAIL: {len(result['errors'])} error(s), {len(result['warnings'])} warning(s)")
        return 1
    print(f"PASS: {args.manifest} ({len(result['warnings'])} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
