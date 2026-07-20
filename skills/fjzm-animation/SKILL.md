---
name: fjzm-animation
description: "Use when creating, rigging, previewing, diagnosing, or revising Minecraft Blockbench animations for 方界造模/FJZM assets, including pivots, bone binding, timing, interpolation, loops, transitions, orbit motion, collision clearance, animation events, and damage or destruction clips."
---

# 方界造模·动画工坊

`$fjzm-animation` is the animation specialist for 方界造模. It accepts either `delegated production` from `$fjzm` or a user-requested `standalone revision` of an existing approved model. It does not replace the main skill's concept, model identity, texture, shader, particle, audio, Mod, or release decisions.

## Hard gate

Read [animation-handoff.md](references/animation-handoff.md) before editing any model. Read [animation-revision.md](references/animation-revision.md) for every optimization or repair request.

Require `animation-handoff.json`, then run:

```powershell
python -X utf8 scripts/validate_animation_handoff.py animation-handoff.json --workspace <approved-model-folder>
```

Stop when validation reports an error. Lock `project_id`, `asset_id`, `asset_version`, `model_sha256`, and `rig_signature` before opening or changing the model. Never infer the target from the currently open Blockbench tab.

## Supported modes

- `delegated production`: `$fjzm` has approved the concept and delegates a named animation set. The handoff defines whether rig creation is authorized.
- `standalone revision`: diagnose and revise approved animation behavior without changing protected model content.
- `delegated_rig_and_animation`: allowed only when `$fjzm` explicitly approves the rig-topology change and marks dependent rebinding as required.

If a request needs geometry, UV, texture, bone topology, bone names, hierarchy, or locator changes outside the approved handoff, stop and return to `$fjzm`. Do not disguise a model-geometry issue as an animation fix.

## Revision approval gate

For an existing animation, inspect and explain the defect before editing. Present the affected clips, diagnosis, proposed key-pose/timing/interpolation/pivot/clearance changes, protected parts, output version, and validation plan. Obtain explicit revision approval. Silence is not approval.

Approval to improve one clip does not authorize changes to other clips, geometry, textures, events, or gameplay behavior.

## Production workflow

1. Verify the source and specification hashes; verify the identity and rig signature.
2. Keep the source read-only. Never overwrite the source `.bbmodel`; create a versioned output copy at the path in the handoff.
3. Take the handoff's single-writer lock. Do not let `$fjzm`, another skill, a script, or a second Blockbench session write the same animation version concurrently.
4. Build or inspect bone ownership, hierarchy, default pose, pivots, sockets, moving planes, orbit centers, and clearance envelopes.
5. Create `animation-system.json` with clip, state, transition, interruption, cooldown, root-motion, and acceptance contracts.
6. Author readable anticipation, action, follow-through, recovery, secondary motion, loops, and transitions only for approved animation IDs.
7. Create `animation-events.json` for event timing. Do not directly implement particles, audio, hitboxes, damage, or projectile spawning here.
8. Reopen the saved output in actual Blockbench. Preview each clip at normal speed and inspect key poses, the loop seam, every transition, and sampled interpolated frames every 0.05 seconds; sample more densely for fast or narrow-clearance motion.
9. Write `animation-result.json` containing identity, source/output hashes, rig signature before/after, changed clips, changed bones, event changes, evidence, warnings, rebind requirements, and pass/fail status.
10. Return the result to `$fjzm`. The main skill decides whether particles, audio, hitboxes, projectiles, Mod controllers, exports, and release evidence may now bind to it.

## Required outputs

- Versioned `.bbmodel` output; source remains untouched
- `animation-system.json`
- `animation-events.json`
- `animation-result.json`
- Actual Blockbench evidence for normal-speed clips, key poses, pivots, transitions, interpolated clearance, and loop seam

Do not claim runtime behavior from Blockbench preview alone. Runtime state machines, blending, hitboxes, damage, particles, sound, and projectile logic require the target Mod/runtime and remain owned by `$fjzm`.
