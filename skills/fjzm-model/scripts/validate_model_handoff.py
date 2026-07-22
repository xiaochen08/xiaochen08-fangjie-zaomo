import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_SURFACES = {"geometry", "base_rig_interface", "placeholder_uv"}


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid UTF-8 JSON: {exc}") from exc


def require(data, keys, prefix="contract"):
    missing = [key for key in keys if key not in data]
    if missing:
        raise ValueError(f"{prefix} missing fields: {', '.join(missing)}")


def safe_path(workspace, value, label, must_exist=True):
    path = (workspace / value).resolve()
    try:
        path.relative_to(workspace)
    except ValueError as exc:
        raise ValueError(f"{label} escapes workspace") from exc
    if must_exist and not path.is_file():
        raise ValueError(f"{label} does not exist: {value}")
    return path


def verify_artifact(workspace, artifact, label):
    require(artifact, ["path", "sha256"], label)
    if not SHA256_RE.fullmatch(artifact["sha256"]):
        raise ValueError(f"{label} sha256 must be 64 lowercase hex characters")
    path = safe_path(workspace, artifact["path"], label)
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != artifact["sha256"]:
        raise ValueError(f"{label} sha256 mismatch")


def validate(data, workspace):
    require(data, [
        "protocol_version", "message_type", "message_id", "correlation_id", "from_skill",
        "to_skill", "stage", "idempotency_key", "identity", "attempt", "writer_lock",
        "dependencies", "approved_design", "reference_artifacts", "geometry_blueprint",
        "authorized_surfaces", "output_path", "fidelity_thresholds",
    ])
    if data["protocol_version"] != "1.0" or data["message_type"] != "handoff":
        raise ValueError("model handoff requires ContractFlow protocol 1.0 handoff")
    if data["from_skill"] != "fjzm" or data["to_skill"] != "fjzm-model" or data["stage"] != "geometry":
        raise ValueError("model handoff must route centrally from fjzm to fjzm-model at geometry stage")
    require(data["identity"], ["project_id", "asset_id", "asset_version"], "identity")
    if not all(isinstance(data["identity"][key], str) and data["identity"][key].strip() for key in data["identity"]):
        raise ValueError("identity values must be non-empty strings")
    if not isinstance(data["attempt"], int) or not 0 <= data["attempt"] <= 2:
        raise ValueError("attempt must be 0, 1, or 2")
    lock = data["writer_lock"]
    require(lock, ["owner", "surface", "output_version"], "writer_lock")
    if lock["owner"] != "fjzm-model" or lock["surface"] != "geometry":
        raise ValueError("geometry writer lock must belong to fjzm-model")
    if not data["dependencies"] or any(dep.get("status") != "passed" for dep in data["dependencies"]):
        raise ValueError("every dependency must be passed")
    require(data["approved_design"], ["approval_id", "approval_sha256"], "approved_design")
    if not SHA256_RE.fullmatch(data["approved_design"]["approval_sha256"]):
        raise ValueError("approved_design approval_sha256 is invalid")
    if not data["reference_artifacts"]:
        raise ValueError("at least one reference artifact is required")
    for index, artifact in enumerate(data["reference_artifacts"]):
        verify_artifact(workspace, artifact, f"reference_artifacts[{index}]")
    verify_artifact(workspace, data["geometry_blueprint"], "geometry_blueprint")
    surfaces = set(data["authorized_surfaces"])
    if not surfaces or not surfaces <= ALLOWED_SURFACES:
        raise ValueError("authorized surface exceeds model-workshop ownership")
    output = safe_path(workspace, data["output_path"], "output_path", must_exist=False)
    if output.suffix.lower() != ".bbmodel":
        raise ValueError("output_path must end in .bbmodel")
    if output.exists():
        raise ValueError("output_path already exists; use a new versioned output")
    thresholds = data["fidelity_thresholds"]
    expected = {
        "blocking_anchor_pass_percent": 100,
        "main_proportion_error_percent_max": 5,
        "key_part_position_error_bbu_max": 0.5,
        "symmetric_part_error_bbu_max": 0.25,
        "rotation_error_degrees_max": 3,
    }
    require(thresholds, expected.keys(), "fidelity_thresholds")
    if thresholds["blocking_anchor_pass_percent"] != 100:
        raise ValueError("blocking anchor pass threshold must be 100%")
    for key, maximum in expected.items():
        if key != "blocking_anchor_pass_percent" and thresholds[key] > maximum:
            raise ValueError(f"{key} is looser than the suite gate")


def main():
    parser = argparse.ArgumentParser(description="Validate an FJZM model-workshop handoff")
    parser.add_argument("contract", type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    args = parser.parse_args()
    try:
        workspace = args.workspace.resolve()
        validate(load_json(args.contract), workspace)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("OK: model handoff is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
