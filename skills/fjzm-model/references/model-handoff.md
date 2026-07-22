# Model handoff

The only valid production route is `$fjzm` → `$fjzm-model` → `$fjzm`. A specialist-to-specialist message is invalid even when both assets appear related.

`model-handoff.json` uses ContractFlow v1 and must include:

- envelope: `protocol_version`, `message_type`, `message_id`, `correlation_id`, `from_skill`, `to_skill`, `stage`, `idempotency_key`;
- identity: `project_id`, `asset_id`, `asset_version`;
- safety: `attempt`, `writer_lock`, passed `dependencies`;
- approval: approval ID and SHA-256;
- inputs: immutable reference artifact paths/hashes and geometry-blueprint path/hash;
- scope: only `geometry`, `base_rig_interface`, and `placeholder_uv`;
- output: a new versioned `.bbmodel` path;
- fidelity thresholds.

Reject missing/mismatched hashes, path traversal, duplicate identity, wrong stage, output overwrite, attempt above 2, failed dependencies, or a writer other than `fjzm-model` on the geometry surface.

The result message mirrors the same identity and correlation ID. Return `model-result.json` to `$fjzm`; never bypass central validation.
