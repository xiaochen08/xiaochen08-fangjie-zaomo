import argparse
import json
import sys
from pathlib import Path


REQUIRED = {
    "fjzm": {"orchestration", "combat_runtime_integration"},
    "fjzm-model": {"geometry"},
    "fjzm-texture": {"texture"},
    "fjzm-animation": {"animation", "blender_epicfight_backend", "combat_behavior_orchestration"},
}


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid UTF-8 JSON: {exc}") from exc


def validate(data):
    if data.get("suite_name") != "fjzm-suite" or data.get("suite_version") != "5.2.0":
        raise ValueError("suite name/version must be fjzm-suite 5.2.0")
    if data.get("protocol_version") != "1.0":
        raise ValueError("protocol version must be ContractFlow 1.0")
    skills = data.get("skills")
    if not isinstance(skills, list):
        raise ValueError("skills must be a list")
    by_name = {skill.get("name"): skill for skill in skills}
    missing = set(REQUIRED) - set(by_name)
    if missing:
        raise ValueError(f"missing required skills: {', '.join(sorted(missing))}")
    if set(by_name) != set(REQUIRED):
        raise ValueError("capability index contains an unexpected skill")
    capability_errors = []
    for name, capabilities in REQUIRED.items():
        skill = by_name[name]
        if skill.get("version") != "5.2.0":
            raise ValueError(f"skill version mismatch: {name}")
        available = set(skill.get("capabilities", []))
        missing_capabilities = capabilities - available
        if missing_capabilities:
            capability_errors.append(f"missing required capability {', '.join(sorted(missing_capabilities))}: {name}")
    if capability_errors:
        raise ValueError("; ".join(capability_errors))


def main():
    parser = argparse.ArgumentParser(description="Validate FJZM v5.2 suite capabilities")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        validate(load_json(args.manifest))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("OK: FJZM v5.2 four-skill capability index is compatible")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
