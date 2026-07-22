import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_VIEWS = {"front", "back", "left", "right", "top", "bottom", "three-quarter", "gameplay-distance"}
ALLOWED_SURFACES = {"geometry", "base_rig_interface", "placeholder_uv"}


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid UTF-8 JSON: {exc}") from exc


def require(data, keys, prefix="document"):
    missing = [key for key in keys if key not in data]
    if missing:
        raise ValueError(f"{prefix} missing fields: {', '.join(missing)}")


def safe_path(workspace, value, label):
    path = (workspace / value).resolve()
    try:
        path.relative_to(workspace)
    except ValueError as exc:
        raise ValueError(f"{label} escapes workspace") from exc
    if not path.is_file():
        raise ValueError(f"{label} does not exist: {value}")
    return path


def verify_artifact(workspace, artifact, label):
    require(artifact, ["path", "sha256"], label)
    if not SHA256_RE.fullmatch(artifact["sha256"]):
        raise ValueError(f"{label} sha256 is invalid")
    path = safe_path(workspace, artifact["path"], label)
    if hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
        raise ValueError(f"{label} sha256 mismatch")
    return path


def validate_report(report, workspace, model_sha):
    require(report, [
        "schema_version", "model_sha256", "reference_sha256", "summary_board", "overlay",
        "views", "blocking_anchors", "unapproved_parts", "missing_approved_parts", "metrics",
        "unintended_intersections", "floating_parts", "wrong_groups", "identity_mismatch", "status",
    ], "fidelity report")
    if report["model_sha256"] != model_sha:
        raise ValueError("fidelity report model sha256 mismatch")
    if not SHA256_RE.fullmatch(report["reference_sha256"]):
        raise ValueError("fidelity report reference sha256 is invalid")
    verify_artifact(workspace, report["summary_board"], "summary_board")
    verify_artifact(workspace, report["overlay"], "overlay")
    if report["overlay"].get("opacity_percent") != 50:
        raise ValueError("overlay opacity must be 50 percent")
    view_names = {view.get("name") for view in report["views"]}
    missing_views = REQUIRED_VIEWS - view_names
    if missing_views:
        raise ValueError(f"missing required views: {', '.join(sorted(missing_views))}")
    if len(report["views"]) != len(REQUIRED_VIEWS):
        raise ValueError("fidelity report must contain exactly eight separate views")
    for view in report["views"]:
        verify_artifact(workspace, view, f"view {view.get('name', '?')}")
        if view.get("camera") not in {"orthographic", "perspective"}:
            raise ValueError("every view must declare its camera")
    if not report["blocking_anchors"] or any(anchor.get("status") != "passed" for anchor in report["blocking_anchors"]):
        raise ValueError("every blocking anchor must pass")
    if report["unapproved_parts"] or report["missing_approved_parts"]:
        raise ValueError("approved part inventory mismatch")
    metrics = report["metrics"]
    limits = {
        "main_proportion_error_percent": 5,
        "key_part_position_error_bbu": 0.5,
        "symmetric_part_error_bbu": 0.25,
        "rotation_error_degrees": 3,
    }
    require(metrics, [*limits, "clearance_pass"], "metrics")
    for key, maximum in limits.items():
        if not isinstance(metrics[key], (int, float)) or metrics[key] > maximum or metrics[key] < 0:
            label = key.replace("main_", "").replace("_error_percent", "").replace("_", " ")
            raise ValueError(f"{label} threshold failed")
    if metrics["clearance_pass"] is not True:
        raise ValueError("clearance gate failed")
    if any(report[key] != 0 for key in ("unintended_intersections", "floating_parts", "wrong_groups")):
        raise ValueError("geometry contains unintended intersection, floating part, or wrong group")
    if report["identity_mismatch"] is not False or report["status"] != "passed":
        raise ValueError("identity/status gate failed")


def validate(data, workspace):
    require(data, [
        "protocol_version", "message_type", "message_id", "correlation_id", "from_skill",
        "to_skill", "stage", "idempotency_key", "identity", "attempt", "output_model",
        "fidelity_report", "geometry_signature", "rig_signature", "changed_surfaces", "status",
    ], "model result")
    if data["protocol_version"] != "1.0" or data["message_type"] != "result":
        raise ValueError("model result requires ContractFlow protocol 1.0 result")
    if data["from_skill"] != "fjzm-model" or data["to_skill"] != "fjzm" or data["stage"] != "geometry":
        raise ValueError("model result must return centrally from fjzm-model to fjzm")
    require(data["identity"], ["project_id", "asset_id", "asset_version"], "identity")
    if not isinstance(data["attempt"], int) or not 0 <= data["attempt"] <= 2:
        raise ValueError("attempt must be 0, 1, or 2")
    surfaces = set(data["changed_surfaces"])
    if not surfaces or not surfaces <= ALLOWED_SURFACES:
        raise ValueError("changed surface exceeds model-workshop ownership")
    model_path = verify_artifact(workspace, data["output_model"], "output_model")
    if model_path.suffix.lower() != ".bbmodel":
        raise ValueError("output_model must be a .bbmodel")
    report_path = verify_artifact(workspace, data["fidelity_report"], "fidelity_report")
    validate_report(load_json(report_path), workspace, data["output_model"]["sha256"])
    if not data["geometry_signature"] or not data["rig_signature"]:
        raise ValueError("geometry_signature and rig_signature are required")
    if data["status"] != "passed":
        raise ValueError("model result status must be passed")


def main():
    parser = argparse.ArgumentParser(description="Validate an FJZM model-workshop result")
    parser.add_argument("result", type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    args = parser.parse_args()
    try:
        validate(load_json(args.result), args.workspace.resolve())
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("OK: model result and fidelity evidence are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
