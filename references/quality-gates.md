# Blockbench model quality gates

## Gate 0: user design approval

- Lock `project_id`, `asset_id`, `asset_version`, display name, and identity-scoped workspace before any artifact or attachment mapping; show the target header at every asset switch.
- Follow `user-dialogue.md` for every intake and approval: ask exactly one question per turn, keep the remaining queue internal, and never merge two model identities into one folder.
- When `create_mod_first` is selected, ask the Minecraft version before every other Mod/model/GUI detail.
- Ask only for the Windows drive letter in one turn; derive `X:\FJZM-Projects\<project_id>` automatically and include it in project-creation approval.
- Pass the red host UTF-8 gate before the Mod shell and the red project UTF-8 gate before any custom source or resource.
- Complete the requirements brief through separate single-decision turns before generating a new design.
- Present a tailored related-asset list; record single versus approved-set scope and a separate decision for every suggested companion.
- Confirm multi-asset scope in a text-only manifest; do not generate or show an asset-overview image.
- Make the first user-visible image batch the three clearly labeled, Blockbench-feasible A/B/C concept previews. Generate them with exactly three separate imagegen calls and show no partial batch.
- Hold A, B, and C to the same quality floor. Reject recolors, reduced-detail filler, missing-scope variants, and sacrificial options; regenerate a failed candidate before display.
- Require the final model reference package to include front, back, left, right, top, bottom, three-quarter, and every approved action/keyframe sheet with identical geometry and texture.
- Store every prompt, negative prompt, manifest, image, review, approval, and SHA-256 under immutable `design/image-rounds/`; resume from `design/image-production-index.json` instead of restarting.
- Run `scripts/validate_image_production_index.py`; a broken round ID, dependency, path, hash, or approval record blocks image continuation and delivery.
- When GUI is in scope, generate three Minecraft-faithful GUI theme previews, obtain separate GUI approval, and archive approved model and GUI images in `design/approved-previews/`.
- When a runtime Mod asset is in scope, create `asset-presentation.json`; require the display name, gray italic Mod line, factual colored usage line, approved themed flavor pool, localization keys, and accessible layout. Run `scripts/validate_asset_presentation.py` before final GUI approval or runtime integration.
- Before imagegen, compile a concept-to-build manifest and apply `concept-prompt.md` without unresolved placeholders.
- Before imagegen, read `shader-compatibility.md`; lock the no-shader baseline, exact named shader/PBR targets, emissive/world-light behavior, transparency/render layer, and performance/evidence burden.
- When particles are required, complete the provisional particle contract, emitter plan, event timing, and paired effect-preview prompt before imagegen.
- When audio is attached, inventory every source and obtain approval for the source-to-English-event mapping before conversion or animation binding.
- Keep model concept approval and audio mapping approval independent; re-open only the gate affected by a change unless timing, rig, or event ownership crosses both.
- Audit cross-view consistency and visible-part mappings; if any detail is unbuildable, regenerate the preview before showing it.
- Explain tradeoffs and iterate images when the user requests changes.
- Record the exact message selecting a concept and authorizing model generation.
- Before that message, do not open Blockbench or create model, rig, texture, or animation files.

Pass only on explicit approval. Silence, urgency, delegated taste, and a reference image alone do not pass.

## Gate 1: design anchor

- Confirm the chosen concept or reference and list the traits that must survive simplification.
- Mark which visible effects are geometry, texture, emissive rendering, particles, or post-processing.
- Compare the promised image quality with what Blockbench can actually represent.

Pass when the silhouette, proportions, signature parts, palette, and Minecraft feasibility are explicit. The selected preview and its manifest become the design contract.

## Gate 2: geometry graybox

This is the geometry graybox checkpoint. Delegate through ContractFlow v1 to `$fjzm-model`, require a passing `model-result.json`, and bind all evidence to the model/reference hashes.

- Use separate groups for every independently moving assembly.
- Place origins at physical joints or declared external pivots before adding detail.
- For animated models, approve the rig hierarchy, default pose, sockets, root-motion policy, state graph, and highest-risk motion grayboxes.
- Reopen the saved graybox in actual Blockbench; the legacy minimum was front, side, back, top, and three-quarter. The v5 gate expands this to one summary board plus separate front, back, left, right, top, bottom, three-quarter, and gameplay-distance views at matched scale and neutral lighting. Include a 50% transparent overlay for comparable views.
- Apply the balanced fidelity limits: blocking anchors: 100%; main proportion error: at most 5%; key-part position error: at most 0.5 Blockbench units; symmetric-part error: at most 0.25 Blockbench units; rotation error: at most 3 degrees; declared clearance passes; no missing approved parts, unapproved parts, unintended intersections, floating parts, wrong groups, or identity mismatch.
- Match the concept sheet's scale, part inventory, proportions, and camera views; document any unavoidable deviation and request approval before continuing.
- Check static intersections, floating pieces, coplanar faces, excessive cube count, and scale.
- Present the actual Blockbench graybox views and a reference-anchor checklist to the user. Record explicit user graybox approval naming the accepted version and deviations. Silence is not graybox approval.
- Freeze `geometry_signature` only after that approval. Plan and freeze `uv_signature` before texture delegation; any later geometry or UV change reopens the affected gate.

Pass before detailed UVs or textures only on explicit user graybox approval.

## Gate 3: motion prototype

- Write the complete state sequence and duration table.
- Verify every required clip, loop seam, and legal transition matrix entry, including priority, blend, interruption, retrigger, cooldown, and return-pose policy.
- Check event synchronization across particles, sound, projectiles, hitboxes, damage windows, and gameplay callbacks; use one central event time.
- Verify every approved audio event against `audio-manifest.json`; loops need start, stop, interruption, distance, and duplicate-playback rules.
- Run `scripts/audio_pipeline.py inspect`; record source hashes, waveform/metadata findings, mapping status, and variant grouping before conversion.
- Test interruption cleanup so particles, sounds, hitboxes, contacts, and cooldown states cannot remain stuck.
- Verify activation, anticipation, attack event, follow-through, cooldown/hold, recovery, and idle handoff.
- For destructible assets, verify every approved damage stage, destruction priority, event cancellation, debris clearance, terminal state, and repair/respawn/wreck/despawn route.
- For paired parts, test direction and phase independently; symmetry does not prove correct motion.
- Sample the timeline densely enough to catch interpolation collisions. A useful starting point is every 0.05 seconds plus every keyframe.
- Add task-specific assertions for shared origins, monotonic rotations, phase separation, minimum radius, and final-pose equality.
- Validate each particle emitter group/socket, its local origin and axes, animation event time, stop/interrupt behavior, and clearance at interpolated frames.

Pass before material polish.

## Gate 4: texture and detail

This is the textured final checkpoint. Compare the actual saved Blockbench result against the approved reference using the same eight-view and overlay evidence set before user approval.

`fjzm` remains the texture approval owner and integration owner. `$fjzm-texture` is the single texture writer for one identity-locked, versioned output. Create `texture-handoff.json`, lock `project_id`, `asset_id`, `asset_version`, `model_sha256`, `geometry_signature`, `uv_signature`, approved reference hashes, and shader-contract hash, then run `fjzm-texture/scripts/validate_texture_handoff.py`.

The specialist must return to `$fjzm` with `texture-result.json`, `texture-spec.json`, `reference-fidelity-report.json`, texture maps, and actual Blockbench evidence. Do not qualify shaders, bundle, or release the asset before the texture result returns. Geometry, rig, animation, locator, or unapproved UV changes must stop and reopen the owning gate.

- Match the approved atlas size and maintain consistent texel density.
- Check UV bounds, seams, mirrored details, face texture indices, and texture paths.
- Separate material values with value, hue, edge highlights, recess shadows, wear, and emissive masks—not random noise.
- Keep eyes, noses, weapons, cores, and other identity anchors readable at gameplay distance.
- Require efficient UV use; a mostly empty large atlas is not high quality.
- Do not upscale a low-resolution texture or enlarge nearest-neighbor pixels to claim high resolution. Paint natively at the approved density.
- Keep albedo neutral: reject painted-in directional light, cast shadows, bloom halos, or environment tint that create double lighting in-game.
- Keep emissive/PBR maps separate and follow only the locked material standard/version. Translucent or mixed materials require an explicit render layer and overlap/sorting evidence.

For detailed/ultra tiers, require consistent texel density, efficient UV use, readable material separation, deliberate highlights, shadows, and wear, and identity details at gameplay distance. If the extra pixels carry no purposeful information, reduce the resolution.

Pass only after the user gives explicit texture-preview approval for the actual Blockbench result and detail improves readability without destroying the Minecraft form language.

## Gate 5: actual Blockbench evidence

The animation movement checkpoint compares each planned key pose, actual Blockbench pose, and overlay. Sample every 0.05 seconds or more densely for fast/narrow motion; validate direction, phase, clearance, loop seam, cooldown, return pose, and actual movement rather than keyframe presence alone.

- Reopen the saved `.bbmodel`; do not rely on the generator's in-memory representation.
- Play every animation at normal speed and inspect critical frames from multiple views.
- Capture actual viewport screenshots for idle and each important state.
- Capture actual damage-state and destruction previews; verify debris pivots, swept volumes, wreck alignment, and the terminal pose.
- Compare screenshots against the selected design anchor, not against a later reinterpretation.
- Run `scripts/validate_bbmodel.py` with task requirements.
- Verify clips and pivots in actual Blockbench, then verify the state controller, blending, root motion, transition matrix, and event synchronization in the actual target runtime.
- For particles, validate attachment, timing, cleanup, budget, LOD, and fallback in the actual target runtime; do not claim the effect works from a Blockbench screenshot.
- Validate `shader-contract.json` and execute applicable `no_shader_daylight`, `no_shader_dark`, `side_lighting`, `target_shader_daylight`, `target_shader_dark`, `emissive_dark`, `bloom_stress`, and `transparency_overlap` rows in-game. Inspect for crushed blacks, blown highlights, double lighting, inverted normals, noisy PBR response, transparency sorting/halos, Z-fighting, culling, and light leaks.
- For sound, validate registration, spatial origin, timing, volume, loop cleanup, interruption, and multiplayer duplication in the actual target runtime.
- Run `scripts/validate_audio_manifest.py` against the runtime sound registry and central event table. Validate subtitles, visual telegraphs, provenance/license status, performance budgets, and version-specific adapter evidence.
- Cross-check every audio/particle/animation binding against the same model-spec hash, asset ID, version, rig signature, event table, and locator set. Reject cross-model paths or approvals.
- Build `asset-bundle.json` from `asset-bundle.md`; run `scripts/validate_asset_bundle.py` and retain the exact report with resource and evidence hashes.
- Preserve exact Minecraft/loader/shader-pack versions, preset, model/map hashes, screenshots/video hashes, tester, timestamp, and expected/actual results for every passed shader row. Blockbench preview is not runtime proof.
- Confirm every source and evidence path is inside the approved asset folder; authorized Mod integration copies must map back by asset identity and source hash.

Pass only when structural checks, visual checks, and user-visible previews agree.

## Gate 6: release qualification

The Minecraft runtime checkpoint must exercise the exact exported asset in the authorized target project: scale/render/collision, state transitions, particles, projectile, audio, damage/destruction, unload/reload, and multiplayer. Run the mandatory no-shader baseline first, then one exact user-named shader pack/version/loader/preset. Never claim universal shader compatibility.

- Read `release-qualification.md` and label each target runtime as verified, compatible, or experimental from actual evidence.
- Read `runtime-delivery.md`; create the unverified scaffold, attach exact project/build/Blockbench/E2E evidence, then run `scripts/validate_release_evidence.py`.
- Run the real-project matrix for actual Blockbench, single-player, dedicated server/two clients, two models together, interruption/unload, and projectile collision.
- Never infer runtime success from schemas, unit tests, screenshots, or documentation. Without an authorized target project, keep the deliverable at RC/compatible status.

Pass only when every advertised verified-support row has reproducible archived evidence.

## Runtime boundary

Blockbench source geometry and animation do not automatically implement emissive shaders, world lighting, PBR material decoding, particles, projectiles, damage, targeting, sound, cooldown logic, or animation state controllers. Deliver event names and timestamps, then implement or document those behaviors in the selected Minecraft runtime. Use `shader-compatibility.md` for lighting/materials, `particle-design.md` for particles, and `audio-system.md` for sound.

For `model_first`, run `scripts/validate_runtime_contract.py` before detailed production and again before bundling. Treat its production ceiling as a hard maximum: a concept/graybox/runtime-neutral source cannot be relabeled as a platform export, compatible Mod asset, or game-ready deliverable.

## Delivery checklist

- Editable `.bbmodel`
- PNG texture and optional emissive mask
- Approved atlas dimensions, texels per Blockbench unit, and necessity rationale
- Required runtime exports
- Static multi-view preview
- Full animation preview and critical Blockbench screenshots
- Animation names, lengths, loop modes, and event times
- Approved `audio-manifest.json`, converted OGG files when authorized, sound registrations, and runtime binding evidence
- Audio inspection report, source hashes, localized subtitles, provenance/license records, and multiplayer/interrupt/performance results
- Model specification, assumptions, and unresolved runtime work
- Validated `shader-contract.json`, base texture plus approved emissive/PBR maps, no-shader fallback, named-target matrix, and hashed runtime evidence
- Unified `asset-bundle.json`, validation report, ordered workflow evidence, `runtime-delivery.json`, and release-qualification matrix
- No overwritten user files; use clear versioned filenames
- Validated `encoding-preflight.json` with `project_passed` status for Java Mod production
- Approved GUI preview, `screen-to-texture` manifest, `approval-index.json`, and actual in-game GUI screenshots when GUI is in scope
- Complete `design/image-production-index.json`, all immutable image rounds, full model view matrices, action/keyframe sheets, prompts, hashes, reviews, and approval evidence
- Validated `asset-presentation.json` for every player-facing asset, localization entries, four-line information hierarchy, approved flavor pool, stable selection rule, and GUI-scale/readability evidence
