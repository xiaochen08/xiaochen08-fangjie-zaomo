#!/usr/bin/env python3
"""Read runtime project markers and report exact Minecraft integration evidence without writing."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _properties(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _version(value: Any) -> str | None:
    if isinstance(value, list) and all(isinstance(part, int) for part in value):
        return ".".join(str(part) for part in value)
    if not isinstance(value, str):
        return None
    match = re.search(r"\d+(?:\.\d+)+(?:[-+._a-zA-Z0-9]*)?", value)
    return match.group(0) if match else None


def _evidence(root: Path, paths: set[Path]) -> list[dict[str, str]]:
    return [
        {"path": path.relative_to(root).as_posix(), "sha256": _sha256(path)}
        for path in sorted(paths, key=lambda item: item.as_posix().lower())
    ]


def inspect_project(project_root: Path | str) -> dict[str, Any]:
    root = Path(project_root).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    if not root.is_dir():
        return {"errors": ["project root is missing"], "warnings": [], "profile": {}, "evidence": []}

    mcreator_files = set(root.glob("*.mcreator"))
    fabric_files = set(root.rglob("fabric.mod.json"))
    forge_files = set(root.rglob("neoforge.mods.toml")) | set(root.rglob("mods.toml"))
    bedrock_files: set[Path] = set()
    bedrock_payloads: list[tuple[Path, dict[str, Any]]] = []
    for path in root.rglob("manifest.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        module_types = {module.get("type") for module in payload.get("modules", []) if isinstance(module, dict)}
        if module_types & {"resources", "data", "script"} and isinstance(payload.get("header"), dict):
            bedrock_files.add(path)
            bedrock_payloads.append((path, payload))

    detected: set[str] = set()
    if mcreator_files:
        detected.add("mcreator")
    if fabric_files:
        detected.add("fabric")
    if forge_files and not mcreator_files:
        detected.add("forge")
    if bedrock_files:
        detected.add("bedrock_packs")
    if not detected:
        return {"errors": ["no supported runtime project markers were found"], "warnings": [], "profile": {}, "evidence": []}
    if len(detected) > 1:
        markers = mcreator_files | fabric_files | forge_files | bedrock_files
        return {
            "errors": [f"multiple runtime project types detected: {', '.join(sorted(detected))}"],
            "warnings": [],
            "profile": {},
            "evidence": _evidence(root, markers),
        }

    kind = next(iter(detected))
    marker_paths: set[Path] = set()
    profile: dict[str, Any] = {"project_path": str(root), "confidence": "detected"}
    properties_path = root / "gradle.properties"
    properties = _properties(properties_path) if properties_path.is_file() else {}
    if properties_path.is_file():
        marker_paths.add(properties_path)

    if kind == "fabric":
        marker = sorted(fabric_files)[0]
        marker_paths.add(marker)
        payload = json.loads(marker.read_text(encoding="utf-8"))
        depends = payload.get("depends") if isinstance(payload.get("depends"), dict) else {}
        versions = {
            value for value in (_version(properties.get("minecraft_version")), _version(depends.get("minecraft"))) if value
        }
        if len(versions) > 1:
            errors.append(f"conflicting minecraft_version evidence: {sorted(versions)}")
        build_files = set(root.glob("build.gradle*"))
        marker_paths.update(build_files)
        gecko_version = None
        for build_file in build_files:
            text = build_file.read_text(encoding="utf-8")
            match = re.search(r"geckolib[^\"']*:([0-9][A-Za-z0-9+_.-]*)[\"']", text)
            if match:
                gecko_version = match.group(1)
                break
        profile.update({
            "edition": "java",
            "integration_type": "fabric",
            "minecraft_version": next(iter(versions)) if len(versions) == 1 else None,
            "integration_version": _version(properties.get("loader_version")) or _version(depends.get("fabricloader")),
            "animation_runtime": "geckolib" if gecko_version else "vanilla_or_custom",
            "animation_runtime_version": gecko_version,
        })
    elif kind == "mcreator":
        marker = sorted(mcreator_files)[0]
        marker_paths.add(marker)
        payload = json.loads(marker.read_text(encoding="utf-8"))
        generator = payload.get("generator", "")
        profile.update({
            "edition": "java",
            "integration_type": "mcreator",
            "minecraft_version": _version(generator),
            "integration_version": str(payload.get("generator_version", "")) or None,
            "animation_runtime": "geckolib" if payload.get("geckolib_version") else "generator_defined",
            "animation_runtime_version": str(payload.get("geckolib_version", "")) or None,
            "generator": generator,
        })
    elif kind == "bedrock_packs":
        marker_paths.update(bedrock_files)
        versions = {_version(payload.get("header", {}).get("min_engine_version")) for _, payload in bedrock_payloads}
        versions.discard(None)
        if len(versions) > 1:
            errors.append(f"conflicting minecraft_version evidence: {sorted(versions)}")
        formats = {str(payload.get("format_version")) for _, payload in bedrock_payloads}
        profile.update({
            "edition": "bedrock",
            "integration_type": "bedrock_packs",
            "minecraft_version": next(iter(versions)) if len(versions) == 1 else None,
            "integration_version": next(iter(formats)) if len(formats) == 1 else None,
            "animation_runtime": "bedrock_animation_controller",
            "animation_runtime_version": next(iter(versions)) if len(versions) == 1 else None,
        })
    else:
        marker_paths.update(forge_files)
        integration_type = "neoforge" if any(path.name == "neoforge.mods.toml" for path in forge_files) else "forge"
        profile.update({
            "edition": "java",
            "integration_type": integration_type,
            "minecraft_version": _version(properties.get("minecraft_version")),
            "integration_version": _version(
                properties.get("neo_version") or properties.get("neoforge_version") or properties.get("forge_version")
            ),
            "animation_runtime": "unknown",
            "animation_runtime_version": None,
        })

    for field in ("minecraft_version", "integration_version"):
        if not profile.get(field):
            errors.append(f"exact {field} could not be detected")
    return {"errors": errors, "warnings": warnings, "profile": profile, "evidence": _evidence(root, marker_paths)}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        result = inspect_project(args.project_root)
        text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.json_out:
            if args.json_out.exists():
                raise OSError(f"refusing to overwrite existing report: {args.json_out}")
            args.json_out.write_text(text, encoding="utf-8", newline="\n")
        else:
            sys.stdout.write(text)
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
