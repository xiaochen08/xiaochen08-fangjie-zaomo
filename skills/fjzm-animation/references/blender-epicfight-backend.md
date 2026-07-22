# Blender / Epic Fight backend

Use this internal backend only after `$fjzm` approves `animation_backend: blender_epicfight`. It remains part of `$fjzm-animation`; it is not a separate user-facing skill.

## Hard preflight

Lock these fields from the authorized Java project before opening Blender:

- `minecraft_version`, loader name, and `loader_version`;
- `animation_runtime: epicfight` and exact `animation_runtime_version`;
- exact `blender_version`;
- exporter name and exact `exporter_version`;
- exporter official source URL and date checked;
- source `model_sha256`, `geometry_signature`, `rig_signature`, `uv_signature`, and `locator_signature`;
- target Epic Fight armature, axes, unit scale, root-motion policy, weapon sockets, and approved animation IDs.

Do not guess versions or select an exporter from an unofficial mirror. Do not install, upgrade, or enable Blender add-ons without the user's authorization. Stop on an unsupported version combination.

Use lowercase ASCII identifiers for Mod IDs, bones, actions, sockets, export folders, and runtime files. Chinese may appear in user-facing labels and documentation, but never rename runtime identifiers to Chinese. Keep every generated text file UTF-8 without BOM.

## Deterministic control

Prefer Blender Python for repeatable import, collection creation, armature mapping, action naming, key insertion, curve settings, export selection, and evidence capture. Do not rely on mouse-only automation for production edits. Use interactive Blender for visual inspection and correction after scripted operations.

Never modify the frozen Blockbench source or model-owned rig. Import or convert into a new versioned `.blend` and retain the source hashes. If retargeting requires a new source bone, parent, pivot, locator, geometry part, or UV change, return to `$fjzm`; `$fjzm-model` must publish a new base-rig version first.

## Rig bridge

Create `rig-map.json` before authoring final clips. It records:

- source and target rig signatures;
- every source bone and target bone;
- parent relationship and rest transform;
- axes, handedness, unit scale, root bone, and forward direction;
- hand, weapon, head, foot, effect, and projectile sockets;
- unmapped, synthesized, or intentionally ignored bones;
- source and generated file hashes.

Reject duplicate target mappings, missing required limbs, changed rest poses, left/right swaps, non-finite transforms, or an unmapped weapon socket. A retargeted preview is not approval of the map.

## Action library

Create `action-library.json` as the single action registry. Each row records the ASCII action ID, source clip, duration, frame range, FPS, loop mode, root-motion policy, affected bones, entry/exit pose, event IDs, export path, and SHA-256.

Build combat with readable anticipation, action, follow-through, and recovery. Drive force from planted feet through hips, torso, shoulder, arm, and weapon. Offset joint timing instead of rotating the whole body at once. Lock foot contacts, verify center-of-mass travel, and make a combo's exit pose compatible with the next action's entry pose.

Do not copy or redistribute Epic Fight or third-party animation assets unless their license explicitly permits it. Use official rigs/exporters only as authorized tooling and create original motion.

## Export and round trip

1. Save the versioned `.blend` before export.
2. Export only named approved actions through the locked exporter version.
3. Re-import or parse each exported action and compare action ID, duration, tracks, key counts, root displacement, and event times with `action-library.json`.
4. Register the exports in the authorized Mod project without changing unrelated assets.
5. Build the project and test locomotion, attack chains, interruption, root displacement, weapon alignment, hit timing, sound/particle events, and multiplayer behavior when applicable.
6. Hash the `.blend`, rig map, action library, runtime exports, build artifact, logs, screenshots, and videos in `animation-result.json`.

Blender preview is not runtime proof. Keep `runtime_review: required`; a successful export or a visually correct Blender viewport remains `unverified` until the exact target runtime passes.

## Required evidence

- actual Blender: rest pose, mapped armature, foot/weapon contacts, key poses, curves, loop seam, interruptions, and root trajectory;
- actual target runtime: registered action, state transition, combo branch, displacement, hit window, cleanup, and no missing-bone/export errors;
- failure evidence: unsupported versions, mapping gaps, export differences, runtime logs, and affected action IDs.
