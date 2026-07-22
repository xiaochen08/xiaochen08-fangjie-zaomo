---
name: fjzm-animation
description: "Use when creating, rigging, previewing, diagnosing, retargeting, exporting, or revising Minecraft animations for 方界造模/FJZM assets in Blockbench or Blender/Epic Fight, including combat motion, pivots, bone binding, timing, transitions, root motion, collision clearance, events, and destruction clips."
---

# 方界造模·动画工坊

`$fjzm-animation` is the only user-facing animation specialist for 方界造模. It contains a Blockbench backend and a Blender / Epic Fight backend. Do not create a separate user-facing Blender skill. Under ContractFlow v1 it accepts production only from `$fjzm`; a user-requested `standalone revision` first routes through `$fjzm` for identity and approval. `$fjzm` remains the sole approval, pipeline-state, identity, integration, and release owner. This skill never sends work directly to `$fjzm-model` or `$fjzm-texture`.

## User conversation protocol

When talking directly to the user, Ask exactly one user-facing question per turn. Never combine clip choice, timing, movement, pivot, collision clearance, events, and approval decisions in one message. Keep the remaining question queue internal and skip anything the user has already answered.

Use plain Chinese and an internet-friendly conversational tone. Explain the current choice and its direct impact in one or two short sentences. Offer 2 or 3 numbered choices for the same decision, put the recommended choice first with `（推荐）`, and accept a number, option name, or free-text reply. Avoid raw terms such as pivot, interpolation, rig signature, and root motion; when unavoidable, explain them in everyday words first. End every active question with: `回复序号就行，也可以直接说你的想法。`

Approval is one question too. Present a short result summary, then ask only whether to approve or revise. Silence is not approval.

## Hard gate

Read [animation-handoff.md](references/animation-handoff.md) before editing any model. Read [animation-revision.md](references/animation-revision.md) for every optimization or repair request. When `animation_backend` is `blender_epicfight`, Read [blender-epicfight-backend.md](references/blender-epicfight-backend.md) before opening Blender, converting a rig, or exporting an action. When `motion_domain` is `combat`, Read [combat-behavior-orchestration.md](references/combat-behavior-orchestration.md) before planning clips, combos, or runtime events.

Require `animation-handoff.json`, then run:

```powershell
python -X utf8 scripts/validate_animation_handoff.py animation-handoff.json --workspace <approved-model-folder>
```

Stop when validation reports an error. Lock the ContractFlow envelope, `project_id`, `asset_id`, `asset_version`, `model_sha256`, `geometry_signature`, `rig_signature`, `uv_signature`, `locator_signature`, and approved `animation_backend` from the passed `model-result.json` and handoff before opening or changing the model. Never infer the target from an open Blockbench or Blender window.

## Internal backend routing

- `blockbench`: use for machines, turrets, block entities, restrained creatures, orbiting assemblies, ordinary loops, and GeckoLib-style clips. Preserve a versioned `.bbmodel` and verify it in actual Blockbench.
- `blender_epicfight`: use only for approved Java humanoids or humanoid-like combat that materially benefits from planted feet, body-weight transfer, chained attacks, rolls, aerial motion, precise curves, or Epic Fight. Preserve the `.bbmodel`; create a versioned `.blend`, `rig-map.json`, `action-library.json`, and runtime exports.

The backend is a production contract, not an implementation preference. `$fjzm` selects it before the animation handoff using the approved model family, target runtime, quality requirement, schedule impact, and user decision. Do not silently upgrade, downgrade, or mix backends. A backend change requires a new approved handoff and output version.

## Supported modes

- `delegated production`: `$fjzm` has approved the concept and delegates a named animation set against a frozen model interface.
- `standalone revision`: diagnose and revise approved animation behavior without changing protected model content.
- `delegated_rig_and_animation`: legacy input only; v5 blocks production and returns the required rig change to `$fjzm`, which must delegate a new geometry/base-rig version to `$fjzm-model` first.

In every mode, geometry, UV, base bone hierarchy, bone names, origins, and locators are immutable. If a request needs any of them changed, stop and return to `$fjzm`. Do not disguise a model-geometry issue as an animation fix.

## Revision approval gate

For an existing animation, inspect and explain the defect before editing. Build the affected clips, diagnosis, proposed key-pose/timing/interpolation/pivot/clearance changes, protected parts, output version, and validation plan internally. Present a short plain-language summary, then obtain explicit revision approval as one numbered approval question. Silence is not approval.

Approval to improve one clip does not authorize changes to other clips, geometry, textures, events, or gameplay behavior.

## Production workflow

1. Verify the source and specification hashes; verify the identity and rig signature.
2. Keep the source read-only. Never overwrite the source `.bbmodel`; create a route-specific versioned output copy or project at the path in the handoff.
3. Take the handoff's single-writer lock. Do not let `$fjzm`, another skill, a script, or a second Blockbench/Blender session write the same animation version concurrently.
4. Build or inspect bone ownership, hierarchy, default pose, pivots, sockets, moving planes, orbit centers, and clearance envelopes.
5. Create `animation-system.json` with clip, state, transition, interruption, cooldown, root-motion, and acceptance contracts.
6. Author readable anticipation, action, follow-through, recovery, secondary motion, loops, and transitions only for approved animation IDs.
7. Create `animation-events.json` for event timing. Do not directly implement particles, audio, hitboxes, damage, or projectile spawning here.
8. For `motion_domain: combat`, create `combat-behavior-system.json`, match it to `action-library.json` and `animation-events.json`, then run `python -X utf8 scripts/validate_combat_behavior.py combat-behavior-system.json --action-library action-library.json --events animation-events.json`. Stop on any error. The workshop defines weapon/stance profiles, sensors, weighted series, combo branches, interruption, phases, and evidence requirements; it does not implement runtime AI.
9. For `blockbench`, reopen the saved output in actual Blockbench. For `blender_epicfight`, use Blender Python for deterministic edits, reopen the saved `.blend` in actual Blender, verify the rig map and exported actions, then test the exports in the actual target runtime. Preview each clip at normal speed and inspect key poses, planted contacts, root displacement, the loop seam, every transition, and sampled interpolated frames every 0.05 seconds; sample more densely for fast or narrow-clearance motion.
10. Write `animation-result.json` containing identity, source/output hashes, rig signature before/after, changed clips, changed bones, event changes, combat-behavior contract hash when applicable, evidence, warnings, rebind requirements, and pass/fail status.
11. Return the result to `$fjzm`. The main skill decides whether combat selection, particles, audio, hitboxes, projectiles, Mod controllers, exports, and release evidence may now bind to it.

## Required outputs

- `blockbench`: versioned `.bbmodel`; source remains untouched
- `blender_epicfight`: versioned `.blend`, `rig-map.json`, `action-library.json`, and versioned Epic Fight runtime exports; source `.bbmodel` remains untouched
- `animation-system.json`
- `animation-events.json`
- `combat-behavior-system.json` and passing validator evidence when `motion_domain: combat`
- `animation-result.json`
- Route-specific authoring evidence from actual Blockbench or actual Blender for normal-speed clips, key poses, pivots/joints, contacts, transitions, interpolated clearance, and loop seam
- Actual target runtime evidence for Blender / Epic Fight exports, animation registration, transitions, displacement, events, and interruption behavior

Do not claim runtime behavior from Blockbench or Blender preview alone. Runtime state machines, blending, hitboxes, damage, particles, sound, projectiles, and Epic Fight registration require the target Mod/runtime and remain owned by `$fjzm`.
