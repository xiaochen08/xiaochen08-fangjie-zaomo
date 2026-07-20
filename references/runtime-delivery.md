# Runtime delivery and release evidence

Use this contract after `asset-bundle.json` passes. It records what was actually integrated and tested; it is not permission to modify an unspecified project.

For a model-first bundle, load and validate `runtime-contract.json` first. Compare its provisional/locked target profile with the read-only project inspection. Record every mismatch; do not silently rename bones, animations, events, locators, textures, or asset identity.

Before writing adapters, create `integration-map.json` that maps the stable model contract to actual runtime owners: resource/model paths, renderer and model layer, block/entity/block-entity/projectile registration, animation controller/state, server-owned gameplay event, client particle/audio event, networking/synchronization field, collision/hitbox, persistence, and save/load behavior. Missing owners remain blockers.

## Safe scaffold

First run `scripts/inspect_runtime_project.py` against the authorized project and preserve its project inspection report. Do not type version fields from memory. Conflicting or missing evidence blocks adapter selection and verified support.

If the inspected project differs from the provisional Minecraft version, loader, mappings, animation runtime, or render path, produce a migration impact report and obtain approval before changing the source model or rig. Prefer an adapter-layer change when the approved source can remain stable.

Create a dry-run JSON first:

```powershell
python -X utf8 scripts/scaffold_runtime_delivery.py '.\asset-bundle.json' --edition java --minecraft-version 1.21.1 --integration-type fabric
```

Add exact integration/runtime versions, project path, and project commit only after inspecting an authorized project. Use `--write-dir` to create a versioned `runtime-delivery.json`; existing files are never overwritten.

Every scaffold starts with:

```yaml
qualification_status: unverified
support_tier: experimental | compatible
test_matrix:
  - status: not_run
```

Never invent a project version, project commit, build result, Blockbench capture, tester, timestamp, or passed case. A scaffold cannot start as verified.

## Exact Blockbench evidence

Record:

- `model_path`, `saved_sha256`, and `reopened_sha256` for the same exact `.bbmodel`;
- validator exit code after reopening;
- complete expected and played animation lists;
- hashed actual viewport captures showing required states and critical frames.

Changing the model after capture invalidates the hashes and dependent evidence.

## Target and build evidence

Record edition, Minecraft version, integration type/version, animation runtime/version, authorized project path, and project commit. A verified Java/MCreator target needs the exact build command, exit code 0, build timestamp, and hashed compiled build artifact. Bedrock targets need the exported pack artifact and equivalent validation/import evidence; record it as the build artifact rather than pretending a Java build occurred.

## Stable E2E case IDs

Do not rename or merge these machine-readable rows:

| `case_id` | Required surface |
|---|---|
| `actual_blockbench` | Exact saved/reopened model, clips, pivots, views |
| `single_player` | Complete behavior, reload, particles, audio, state |
| `dedicated_server_two_clients` | Authority, tracking, late join, duplicates, cleanup |
| `two_models_one_project` | Simultaneous cross-model isolation |
| `interrupt_and_unload` | Cancel, death/destruction, unload/reload, recovery |
| `projectile_collision` | Spawn, trajectory, collision-position impact and damage ownership |

Each passed row requires timestamp, tester, exact steps, expected result, actual result, and at least one contained evidence file with SHA-256. Text saying “tested” is not evidence.

## Qualification

Run:

```powershell
python -X utf8 scripts/validate_release_evidence.py '.\runtime-delivery.json' --release-root '.\'
```

`verified` requires all exact target/build/Blockbench fields and all six passed rows. `compatible` or `experimental` may remain incomplete, but the validator emits an explicit not-verified warning. Preserve the validation report beside the release evidence.
