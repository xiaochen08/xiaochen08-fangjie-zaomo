# ContractFlow v1

ContractFlow v1 is the suite's deterministic handoff protocol. `$fjzm` is the sole approval owner, identity owner, pipeline-state writer, router, integrator, and release owner. Specialists never send peer-to-peer handoffs; every handoff begins at `$fjzm` and every result returns to `$fjzm`.

## Envelope

Every message contains:

- `protocol_version: "1.0"`;
- `message_type: handoff | result | blocked`;
- globally unique `message_id` and stable `correlation_id`;
- `from_skill`, `to_skill`, and `stage`;
- deterministic `idempotency_key` containing project, asset, version, stage, and attempt;
- identity lock: `project_id`, `asset_id`, `asset_version`;
- `attempt` from 0 through 2;
- a single `writer_lock` naming the owner, surface, and new output version;
- passed DAG `dependencies` for a handoff;
- large artifacts as workspace-relative paths plus SHA-256; never embed them in JSON.

Use immutable messages and versioned outputs. Preserve the exact tool/skill version, input/output hashes, timestamps, approvals, and evidence paths as provenance. The main `pipeline-state.json` records `queued`, `running`, `passed`, `failed`, or `blocked`; only `$fjzm` may change it.

## Stage DAG and writers

1. `concept_approval` — `$fjzm`
2. `geometry` — `$fjzm-model`
3. `texture` — `$fjzm-texture`, after geometry passes
4. `animation` — `$fjzm-animation`, after geometry passes; it may run beside texture only on distinct immutable copies and declared surfaces
5. `integration` — `$fjzm`, after applicable specialist results pass
6. `blockbench_validation` — three checkpoints owned by `$fjzm`
7. `runtime_validation` — Minecraft checkpoint owned by `$fjzm`
8. `release` — `$fjzm`

Before routing, validate `capability-index.json`. Protocol major version, suite major version, required skill set, and required capability must match. A missing or incompatible specialist blocks its production stage; it is never silently replaced.

## Retry and hard stop

Use the initial attempt plus at most two internal retries. Retry only technical, deterministic, reversible failures and use a new output version/idempotency key each time. Never lower the approved quality target, loosen thresholds, remove approved scope, or overwrite an earlier attempt.

Hard-stop immediately on identity mismatch, hash mismatch, wrong asset, approval ambiguity, design ambiguity, changed user scope, protocol/capability mismatch, missing source, or a peer-to-peer route. Mark these non-retryable and return control to `$fjzm`; preserve every attempt and its evidence.
