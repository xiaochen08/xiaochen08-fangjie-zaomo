#!/usr/bin/env python3
"""Audit structural invariants in a Blockbench .bbmodel file."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


class Issue:
    def __init__(self, code: str, message: str, path: str = "$") -> None:
        self.code = code
        self.message = message
        self.path = path

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message, "path": self.path}

    def __repr__(self) -> str:
        return f"Issue(code={self.code!r}, path={self.path!r})"


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _vector(value: Any, size: int = 3) -> bool:
    return isinstance(value, list) and len(value) == size and all(_finite_number(item) for item in value)


def _add(issues: list[Issue], code: str, message: str, path: str) -> None:
    issues.append(Issue(code, message, path))


def _validate_required_animations(
    issues: list[Issue], animations: list[dict[str, Any]], requirements: dict[str, Any]
) -> None:
    by_name = {
        item.get("name"): item
        for item in animations
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    for index, requirement in enumerate(requirements.get("required_animations", [])):
        rule = {"name": requirement} if isinstance(requirement, str) else requirement
        if not isinstance(rule, dict) or not isinstance(rule.get("name"), str):
            _add(
                issues,
                "invalid-requirement",
                "Required animation entries must be names or objects with a name.",
                f"$.requirements.required_animations[{index}]",
            )
            continue
        name = rule["name"]
        animation = by_name.get(name)
        if animation is None:
            _add(
                issues,
                "missing-required-animation",
                f"Required animation {name!r} is missing.",
                "$.animations",
            )
            continue
        expected_loop = rule.get("loop")
        if expected_loop is not None and animation.get("loop") != expected_loop:
            _add(
                issues,
                "animation-loop-mismatch",
                f"Animation {name!r} must use loop={expected_loop!r}.",
                "$.animations",
            )
        minimum = rule.get("min_length")
        if _finite_number(minimum) and animation.get("length", 0) < minimum:
            _add(
                issues,
                "animation-too-short",
                f"Animation {name!r} must be at least {minimum} seconds long.",
                "$.animations",
            )


def _validate_required_groups(
    issues: list[Issue], groups: list[dict[str, Any]], requirements: dict[str, Any]
) -> None:
    by_name = {
        item.get("name"): item
        for item in groups
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    for index, requirement in enumerate(requirements.get("required_groups", [])):
        rule = {"name": requirement} if isinstance(requirement, str) else requirement
        if not isinstance(rule, dict) or not isinstance(rule.get("name"), str):
            _add(
                issues,
                "invalid-requirement",
                "Required group entries must be names or objects with a name.",
                f"$.requirements.required_groups[{index}]",
            )
            continue
        name = rule["name"]
        group = by_name.get(name)
        if group is None:
            _add(
                issues,
                "missing-required-group",
                f"Required group {name!r} is missing.",
                "$.groups",
            )
            continue
        expected_origin = rule.get("origin")
        if expected_origin is not None:
            tolerance = rule.get("tolerance", 0.001)
            actual_origin = group.get("origin")
            if not _vector(expected_origin) or not _finite_number(tolerance) or tolerance < 0:
                _add(
                    issues,
                    "invalid-requirement",
                    f"Origin requirement for group {name!r} is invalid.",
                    f"$.requirements.required_groups[{index}]",
                )
            elif not _vector(actual_origin) or any(
                abs(actual - expected) > tolerance
                for actual, expected in zip(actual_origin, expected_origin)
            ):
                _add(
                    issues,
                    "group-origin-mismatch",
                    f"Group {name!r} origin must be {expected_origin!r} ± {tolerance}.",
                    "$.groups",
                )


def validate_model(
    model: Any, requirements: dict[str, Any] | None = None
) -> list[Issue]:
    issues: list[Issue] = []
    requirements = requirements or {}

    if not isinstance(model, dict):
        return [Issue("invalid-root", "The .bbmodel root must be a JSON object.")]

    meta = model.get("meta")
    if not isinstance(meta, dict) or not isinstance(meta.get("format_version"), str):
        _add(issues, "invalid-meta", "meta.format_version must be a string.", "$.meta")
    if not isinstance(meta, dict) or not isinstance(meta.get("model_format"), str):
        _add(issues, "invalid-meta", "meta.model_format must be a string.", "$.meta")

    resolution = model.get("resolution")
    if (
        not isinstance(resolution, dict)
        or not _finite_number(resolution.get("width"))
        or not _finite_number(resolution.get("height"))
        or resolution["width"] <= 0
        or resolution["height"] <= 0
    ):
        _add(
            issues,
            "invalid-resolution",
            "resolution.width and resolution.height must be positive numbers.",
            "$.resolution",
        )

    collection_names = ("elements", "groups", "outliner", "textures", "animations")
    collections: dict[str, list[Any]] = {}
    for name in collection_names:
        value = model.get(name)
        if not isinstance(value, list):
            _add(issues, "invalid-collection", f"{name} must be an array.", f"$.{name}")
            collections[name] = []
        else:
            collections[name] = value

    elements = collections["elements"]
    groups = collections["groups"]
    animations = collections["animations"]

    seen: dict[str, str] = {}
    element_ids: set[str] = set()
    group_ids: set[str] = set()

    for kind, items, destination in (
        ("elements", elements, element_ids),
        ("groups", groups, group_ids),
    ):
        for index, item in enumerate(items):
            path = f"$.{kind}[{index}]"
            if not isinstance(item, dict):
                _add(issues, "invalid-object", f"{kind} entries must be objects.", path)
                continue
            uuid = item.get("uuid")
            if not isinstance(uuid, str) or not uuid:
                _add(issues, "missing-uuid", f"{kind} entry has no UUID.", path)
            else:
                if uuid in seen:
                    _add(
                        issues,
                        "duplicate-uuid",
                        f"UUID {uuid!r} duplicates {seen[uuid]}.",
                        f"{path}.uuid",
                    )
                else:
                    seen[uuid] = path
                destination.add(uuid)
            if not isinstance(item.get("name"), str) or not item.get("name"):
                _add(issues, "missing-name", f"{kind} entry has no name.", path)

    for index, element in enumerate(elements):
        if not isinstance(element, dict):
            continue
        path = f"$.elements[{index}]"
        for coordinate in ("from", "to", "origin"):
            if coordinate in element and not _vector(element[coordinate]):
                _add(
                    issues,
                    "invalid-vector",
                    f"Element {coordinate} must be a finite three-number vector.",
                    f"{path}.{coordinate}",
                )
        if _vector(element.get("from")) and _vector(element.get("to")):
            if any(start > end for start, end in zip(element["from"], element["to"])):
                _add(
                    issues,
                    "inverted-element-bounds",
                    "Element from coordinates must not exceed to coordinates.",
                    path,
                )

    for index, group in enumerate(groups):
        if isinstance(group, dict) and not _vector(group.get("origin")):
            _add(
                issues,
                "invalid-group-origin",
                "Group origin must be a finite three-number vector.",
                f"$.groups[{index}].origin",
            )

    known_outliner_ids = element_ids | group_ids

    def check_outliner(nodes: list[Any], path: str) -> None:
        for index, node in enumerate(nodes):
            node_path = f"{path}[{index}]"
            if isinstance(node, str):
                if node not in known_outliner_ids:
                    _add(
                        issues,
                        "dangling-outliner-reference",
                        f"Outliner references unknown UUID {node!r}.",
                        node_path,
                    )
            elif isinstance(node, dict):
                uuid = node.get("uuid")
                if uuid not in group_ids:
                    _add(
                        issues,
                        "dangling-outliner-reference",
                        f"Outliner group references unknown UUID {uuid!r}.",
                        f"{node_path}.uuid",
                    )
                children = node.get("children", [])
                if not isinstance(children, list):
                    _add(
                        issues,
                        "invalid-outliner-children",
                        "Outliner children must be an array.",
                        f"{node_path}.children",
                    )
                else:
                    check_outliner(children, f"{node_path}.children")
            else:
                _add(
                    issues,
                    "invalid-outliner-node",
                    "Outliner entries must be UUID strings or group objects.",
                    node_path,
                )

    check_outliner(collections["outliner"], "$.outliner")

    animation_names: set[str] = set()
    for animation_index, animation in enumerate(animations):
        path = f"$.animations[{animation_index}]"
        if not isinstance(animation, dict):
            _add(issues, "invalid-animation", "Animation must be an object.", path)
            continue
        name = animation.get("name")
        if not isinstance(name, str) or not name:
            _add(issues, "missing-animation-name", "Animation has no name.", path)
        elif name in animation_names:
            _add(issues, "duplicate-animation-name", f"Duplicate animation {name!r}.", path)
        else:
            animation_names.add(name)
        length = animation.get("length")
        if not _finite_number(length) or length < 0:
            _add(issues, "invalid-animation-length", "Animation length must be non-negative.", path)
            length = 0
        animators = animation.get("animators", {})
        if not isinstance(animators, dict):
            _add(issues, "invalid-animators", "Animation animators must be an object.", path)
            continue
        for target, animator in animators.items():
            animator_path = f"{path}.animators.{target}"
            if not isinstance(animator, dict):
                _add(issues, "invalid-animator", "Animator must be an object.", animator_path)
                continue
            if animator.get("type", "bone") == "bone" and target not in group_ids:
                _add(
                    issues,
                    "unknown-animator-target",
                    f"Bone animator targets unknown group UUID {target!r}.",
                    animator_path,
                )
            keyframes = animator.get("keyframes", [])
            if not isinstance(keyframes, list):
                _add(issues, "invalid-keyframes", "Animator keyframes must be an array.", animator_path)
                continue
            for keyframe_index, keyframe in enumerate(keyframes):
                keyframe_path = f"{animator_path}.keyframes[{keyframe_index}]"
                if not isinstance(keyframe, dict):
                    _add(issues, "invalid-keyframe", "Keyframe must be an object.", keyframe_path)
                    continue
                time = keyframe.get("time")
                if not _finite_number(time) or time < 0:
                    _add(issues, "invalid-keyframe-time", "Keyframe time must be non-negative.", keyframe_path)
                elif time > length + 1e-6:
                    _add(
                        issues,
                        "keyframe-after-animation",
                        f"Keyframe at {time} exceeds animation length {length}.",
                        keyframe_path,
                    )

    _validate_required_animations(issues, animations, requirements)
    _validate_required_groups(issues, groups, requirements)
    return issues


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path, help="Path to the .bbmodel file")
    parser.add_argument("--requirements", type=Path, help="Optional JSON requirements file")
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable JSON report")
    args = parser.parse_args(argv)

    try:
        model = _load_json(args.model)
        requirements = _load_json(args.requirements) if args.requirements else None
        issues = validate_model(model, requirements)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        issues = [Issue("read-error", str(error), str(args.model))]

    report = {
        "ok": not issues,
        "model": str(args.model.resolve()),
        "issues": [issue.to_dict() for issue in issues],
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif issues:
        print(f"FAIL: {args.model} ({len(issues)} issue(s))")
        for issue in issues:
            print(f"- [{issue.code}] {issue.path}: {issue.message}")
    else:
        print(f"PASS: {args.model}")
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
