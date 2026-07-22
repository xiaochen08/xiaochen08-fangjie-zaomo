import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SKILLS = {"fjzm", "fjzm-model", "fjzm-texture", "fjzm-animation"}
SPECIALISTS = SKILLS - {"fjzm"}
STAGE_OWNER = {"geometry": "fjzm-model", "texture": "fjzm-texture", "animation": "fjzm-animation"}
HARD_STOPS = {
    "identity_mismatch", "hash_mismatch", "wrong_asset", "approval_ambiguity", "design_ambiguity",
    "scope_changed", "protocol_mismatch", "capability_mismatch", "missing_source", "peer_to_peer",
}


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid UTF-8 JSON: {exc}") from exc


def require(data, keys, label="contract"):
    missing = [key for key in keys if key not in data]
    if missing:
        raise ValueError(f"{label} missing fields: {', '.join(missing)}")


def artifact_path(workspace, value):
    path = (workspace / value).resolve()
    try:
        path.relative_to(workspace)
    except ValueError as exc:
        raise ValueError("artifact path escapes workspace") from exc
    if not path.is_file():
        raise ValueError(f"artifact does not exist: {value}")
    return path


def validate(data, workspace):
    require(data, [
        "protocol_version", "message_type", "message_id", "correlation_id", "from_skill",
        "to_skill", "stage", "idempotency_key", "identity", "attempt", "writer_lock",
        "dependencies", "artifacts", "retry",
    ])
    if data["protocol_version"] != "1.0":
        raise ValueError("protocol version must be ContractFlow 1.0")
    if data["from_skill"] not in SKILLS or data["to_skill"] not in SKILLS:
        raise ValueError("unknown skill route")
    if data["from_skill"] in SPECIALISTS and data["to_skill"] in SPECIALISTS:
        raise ValueError("central routing violation: specialist peer-to-peer messages are forbidden")
    if data["message_type"] == "handoff":
        if data["from_skill"] != "fjzm" or data["to_skill"] not in SPECIALISTS:
            raise ValueError("central handoff must route from fjzm to a specialist")
    elif data["message_type"] in {"result", "blocked"}:
        if data["from_skill"] not in SPECIALISTS or data["to_skill"] != "fjzm":
            raise ValueError("central result must return from a specialist to fjzm")
    else:
        raise ValueError("message_type must be handoff, result, or blocked")
    require(data["identity"], ["project_id", "asset_id", "asset_version"], "identity")
    if not all(isinstance(value, str) and value.strip() for value in data["identity"].values()):
        raise ValueError("identity values must be non-empty strings")
    if not isinstance(data["attempt"], int) or not 0 <= data["attempt"] <= 2:
        raise ValueError("attempt must be 0, 1, or 2")
    if not isinstance(data["idempotency_key"], str) or not data["idempotency_key"].strip():
        raise ValueError("idempotency_key is required")
    lock = data["writer_lock"]
    require(lock, ["owner", "surface", "output_version"], "writer_lock")
    expected_owner = STAGE_OWNER.get(data["stage"])
    if expected_owner and (lock["owner"] != expected_owner or data["to_skill"] != expected_owner):
        raise ValueError("writer lock owner does not match stage owner")
    if data["message_type"] == "handoff":
        if not data["dependencies"] or any(dep.get("status") != "passed" for dep in data["dependencies"]):
            raise ValueError("dependency gate is not passed")
    for index, artifact in enumerate(data["artifacts"]):
        require(artifact, ["path", "sha256"], f"artifact[{index}]")
        if not SHA256_RE.fullmatch(artifact["sha256"]):
            raise ValueError(f"artifact[{index}] sha256 is invalid")
        path = artifact_path(workspace, artifact["path"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
            raise ValueError(f"artifact[{index}] sha256 mismatch")
    retry = data["retry"]
    require(retry, ["retryable", "reason_code"], "retry")
    if retry["reason_code"] in HARD_STOPS and retry["retryable"] is True:
        raise ValueError(f"hard-stop reason cannot be retryable: {retry['reason_code']}")


def main():
    parser = argparse.ArgumentParser(description="Validate an FJZM ContractFlow v1 message")
    parser.add_argument("contract", type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    args = parser.parse_args()
    try:
        validate(load_json(args.contract), args.workspace.resolve())
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("OK: ContractFlow message is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
