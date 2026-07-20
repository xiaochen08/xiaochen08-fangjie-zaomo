# Release qualification and runtime support

## Evidence-tiered support

- **verified support**: the named edition, Minecraft version, loader/runtime version, and delivery template passed the full matrix below in an authorized real project; evidence includes hashes, logs, captures, and environment versions.
- **compatible support**: file formats and documented APIs match, and static/unit checks pass, but the full real-project matrix is incomplete. State exactly what was not executed.
- **experimental support**: an unproven adapter, version, loader, or workaround. Expect manual integration and revalidation.

Never promote a runtime by documentation alone. A template or schema can be compatible without being verified. No project means no verified runtime claim.

Shader compatibility follows the same evidence tiers. `baseline_only` proves only the no-shader baseline. `named_targets_only` applies only to the exact Minecraft/loader/shader-pack/material-standard versions and presets recorded in `shader-contract.json`; never claim all-shader compatibility. Emissive appearance is separate from actual world-light behavior, which needs a runtime owner and evidence.

A model-first `runtime_neutral_source` is not a release candidate and is never game-ready by itself. Promotion requires an authorized project, a reconciled `runtime-contract.json`, a complete `integration-map.json`, platform exports, a successful build, and real runtime evidence.

## Formal-release matrix

A formal release requires reproducible evidence from:

1. actual Blockbench: reopen the exact saved `.bbmodel`, validate, play all clips, inspect interpolated frames, and capture the actual viewport;
2. single-player: spawn/use the asset, exercise every state, particle, sound, projectile, hitbox, cooldown, save/reload, and chunk unload;
3. dedicated server with two clients: verify authority, tracking, late join, distance, duplicate suppression, and cleanup;
4. two models in one project: load both simultaneously and prove identities, rigs, locators, audio, particles, exports, and approvals never cross-bind;
5. interrupt and unload: test target loss, stun/cancel, death/destruction, chunk unload/reload, rapid retrigger, and recovery to a valid pose/state;
6. projectile collision: prove spawn ownership, trajectory, collision-position impact effects/audio, damage ownership, and no fixed-timestamp fake impact.
7. shader/lighting/material matrix: pass the no-shader baseline and every applicable named shader, PBR, emissive, bloom, and transparency case with exact versions, settings, asset hashes, and contained visual evidence.

Record project commit/hash, runtime versions, resource hashes, exact test steps, expected/actual result, logs, screenshots/video, tester, timestamp, and failures. A passed unit test is not runtime evidence.

Start with `scripts/scaffold_runtime_delivery.py`; it creates only unverified `not_run` rows. Run `scripts/validate_release_evidence.py` before any support claim. Verified evidence includes the exact saved and reopened `.bbmodel` hash, complete animation/capture evidence, authorized project commit, exact environment versions, successful build command, and hashed compiled build artifact or the target platform's equivalent exported pack.

## RC versus formal release

Use an RC label while any matrix row lacks real-project evidence. Do not describe an RC as production-ready. A formal version may be published only when focused validators including `validate_shader_contract.py`, `validate_asset_bundle.py`, `validate_release_evidence.py`, actual Blockbench review, and every claimed verified-support runtime row pass with archived evidence.

If the user has not supplied or authorized a Minecraft project, deliver contracts, adapters, and an E2E test checklist, label support compatible or experimental, and keep formal release blocked.
