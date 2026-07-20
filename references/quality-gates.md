# Blockbench model quality gates

## Gate 0: user design approval

- Lock `project_id`, `asset_id`, `asset_version`, display name, and identity-scoped workspace before any artifact or attachment mapping; show the target header at every asset switch.
- Ask for the Windows drive/root, show the absolute per-model folder, obtain path approval, and never merge two model identities into one folder.
- Ask the compact requirements brief before generating a new design.
- Present a tailored related-asset list; record single versus approved-set scope and a separate decision for every suggested companion.
- Generate three clearly labeled, Blockbench-feasible concept previews with comparable views.
- Before imagegen, compile a concept-to-build manifest and apply `concept-prompt.md` without unresolved placeholders.
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

- Use separate groups for every independently moving assembly.
- Place origins at physical joints or declared external pivots before adding detail.
- For animated models, approve the rig hierarchy, default pose, sockets, root-motion policy, state graph, and highest-risk motion grayboxes.
- Check front, side, rear, top, and three-quarter silhouettes.
- Match the concept sheet's scale, part inventory, proportions, and camera views; document any unavoidable deviation and request approval before continuing.
- Check static intersections, floating pieces, coplanar faces, excessive cube count, and scale.

Pass before detailed UVs or textures.

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

- Match the approved atlas size and maintain consistent texel density.
- Check UV bounds, seams, mirrored details, face texture indices, and texture paths.
- Separate material values with value, hue, edge highlights, recess shadows, wear, and emissive masks—not random noise.
- Keep eyes, noses, weapons, cores, and other identity anchors readable at gameplay distance.
- Require efficient UV use; a mostly empty large atlas is not high quality.
- Do not upscale a low-resolution texture or enlarge nearest-neighbor pixels to claim high resolution. Paint natively at the approved density.

For detailed/ultra tiers, require consistent texel density, efficient UV use, readable material separation, deliberate highlights, shadows, and wear, and identity details at gameplay distance. If the extra pixels carry no purposeful information, reduce the resolution.

Pass when detail improves readability without destroying the Minecraft form language.

## Gate 5: actual Blockbench evidence

- Reopen the saved `.bbmodel`; do not rely on the generator's in-memory representation.
- Play every animation at normal speed and inspect critical frames from multiple views.
- Capture actual viewport screenshots for idle and each important state.
- Capture actual damage-state and destruction previews; verify debris pivots, swept volumes, wreck alignment, and the terminal pose.
- Compare screenshots against the selected design anchor, not against a later reinterpretation.
- Run `scripts/validate_bbmodel.py` with task requirements.
- Verify clips and pivots in actual Blockbench, then verify the state controller, blending, root motion, transition matrix, and event synchronization in the actual target runtime.
- For particles, validate attachment, timing, cleanup, budget, LOD, and fallback in the actual target runtime; do not claim the effect works from a Blockbench screenshot.
- For sound, validate registration, spatial origin, timing, volume, loop cleanup, interruption, and multiplayer duplication in the actual target runtime.
- Run `scripts/validate_audio_manifest.py` against the runtime sound registry and central event table. Validate subtitles, visual telegraphs, provenance/license status, performance budgets, and version-specific adapter evidence.
- Cross-check every audio/particle/animation binding against the same model-spec hash, asset ID, version, rig signature, event table, and locator set. Reject cross-model paths or approvals.
- Build `asset-bundle.json` from `asset-bundle.md`; run `scripts/validate_asset_bundle.py` and retain the exact report with resource and evidence hashes.
- Confirm every source and evidence path is inside the approved asset folder; authorized Mod integration copies must map back by asset identity and source hash.

Pass only when structural checks, visual checks, and user-visible previews agree.

## Gate 6: release qualification

- Read `release-qualification.md` and label each target runtime as verified, compatible, or experimental from actual evidence.
- Read `runtime-delivery.md`; create the unverified scaffold, attach exact project/build/Blockbench/E2E evidence, then run `scripts/validate_release_evidence.py`.
- Run the real-project matrix for actual Blockbench, single-player, dedicated server/two clients, two models together, interruption/unload, and projectile collision.
- Never infer runtime success from schemas, unit tests, screenshots, or documentation. Without an authorized target project, keep the deliverable at RC/compatible status.

Pass only when every advertised verified-support row has reproducible archived evidence.

## Runtime boundary

Blockbench source geometry and animation do not automatically implement emissive shaders, particles, projectiles, damage, targeting, sound, cooldown logic, or animation state controllers. Deliver event names and timestamps, then implement or document those behaviors in the selected Minecraft runtime. Use `particle-design.md` for particles and `audio-system.md` for sound.

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
- Unified `asset-bundle.json`, validation report, ordered workflow evidence, `runtime-delivery.json`, and release-qualification matrix
- No overwritten user files; use clear versioned filenames
