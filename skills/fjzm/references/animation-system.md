# Complete animation design system

## Contents

- Runtime boundary and activation
- Animation inventory by asset family
- Rig, clip, state-machine, and event contracts
- Motion, loops, transitions, collisions, and performance
- Workflow, validation, and delivery
- Combat behavior orchestration and runtime ownership

The animation system has two internal authoring backends: `blockbench` and `blender_epicfight`. Blockbench animation timeline does not implement gameplay state machines; Blender does not implement the Minecraft runtime either. Neither authoring application owns AI decisions, damage, hitboxes, particles, sound, projectile spawning, or runtime blending; the target runtime controls states, transitions, and events.

## Main and specialist boundary

`fjzm` remains the approval owner and integration owner. `$fjzm-animation` is the single animation writer for an identity-locked handoff and owns both internal backends. Before animation production, `$fjzm` creates schema-v2 `animation-handoff.json`, locks `project_id`, `asset_id`, `asset_version`, `model_sha256`, `rig_signature`, and `animation_backend`, and runs `fjzm-animation/scripts/validate_animation_handoff.py`.

The specialist writes a new version and `animation-result.json`; it does not overwrite the source. Its result must return to `$fjzm` before integration continues. A geometry or rig-topology change requires a new main approval, a new handoff, and dependent rebinding. Do not bind particles, audio, hitboxes, or projectiles to a changed rig before the result returns.

For `motion_domain: combat`, `$fjzm-animation` also authors and validates `combat-behavior-system.json`. `$fjzm` owns runtime combat selection, target sensing, server-authoritative damage/hitboxes, event binding, networking, and release evidence. The specialist contract may specify the intended behavior but cannot claim the Mod implements it.

## Backend selection

Use `blockbench` for machines, turrets, block entities, orbiting parts, ordinary creature loops, and animation systems whose target runtime consumes Blockbench/GeckoLib-style clips. Use `blender_epicfight` for approved Java humanoids or humanoid-like combat where planted feet, full-body weight transfer, rolls, aerial attacks, long combos, curve control, or Epic Fight integration materially improves the result.

Do not use Blender merely because it is more powerful. For simple mechanisms it adds conversion and export risk without visible benefit. When the Blender route is recommended, explain the expected quality gain, first-project setup cost, reusable-template benefit, required software, and runtime dependency in separate plain-language decisions before image generation. A route change invalidates the animation handoff and requires a new version.

## Activate before concept generation

Use this system when animation is requested or implied by a creature, boss, weapon, machine, door, vehicle, interactive prop, transformation, attack, charge, recoil, orbit, opening, locomotion, or state change.

Before concepts, create a provisional consultation design containing:

- required animation inventory and optional animation tiers;
- visible moving assemblies, hierarchy, joints, pivots, attachment sockets, and clearance needs;
- state graph, legal transitions, priorities, interrupt rules, cooldowns, and return-to-idle behavior;
- important key poses and whether they change the silhouette of A/B/C concepts;
- runtime events for particles, sounds, projectiles, hitboxes, damage windows, footsteps, and gameplay callbacks;
- target runtime support for blending, root motion, procedural look/aim, animation controllers, and event markers.
- for combat assets, weapon profiles, distance and eye-height bands, weighted behavior series, repetition control, hit and whiff branches, interruption cleanup, and boss phase rhythm.

Do not create production rig or animation files before concept approval. After approval, freeze this design as `animation-system.json` and link it from `model-spec.json`.

## Damage and destruction gate

For every entity, boss, machine, vehicle, furniture, block entity, or structure that can plausibly be attacked or broken, ask whether it is destructible. Record one choice: `not applicable | impact reaction only | staged damage | full destruction`. Follow the dialogue contract and ask exactly one question per turn. Do not assume that a death clip is a destruction system.

When enabled, define the visible state path `intact → minor damage → major damage → critical → destroyed`, health/trigger thresholds, legal skips, interruption rules, and what follows: repair, respawn, persistent wreck, or despawn. Put persistence and repair behavior into separate queue items; never ask both in the same turn.

Choose and approve one or more Blockbench-feasible visual strategies:

- texture/emissive swap for cracks, scorch, leaking energy, dimmed eyes, or warning lights;
- revealed damage groups for exposed frames, broken armor, missing covers, and internal cores;
- detachable debris with independent bones, pivots, landing/cleanup policy, and optional runtime-spawned fragment models;
- replacement wreck model when the destroyed topology, collision, or performance budget differs substantially.

Blockbench authors the poses, groups, textures, and clips; it does not implement health or damage calculation. Runtime code owns thresholds, invulnerability, damage sources, collision replacement, fragment spawning, persistence, loot, and removal.

By default, destruction overrides attack and work states unless the user defines an exception. On entry, cancel hitboxes, projectiles, particles, and looping sounds; stop locomotion and active mechanisms; then fire approved debris, impact, loot, wreck-swap, and cleanup events exactly once. Damage reactions may interrupt, layer, queue, or be ignored during protected phases, but the choice must be explicit.

Graybox every stage before texture polish. Validate fragment/crystal/limb clearance, ground contact, debris pivots and swept volumes, replacement-wreck alignment, collision handoff, and no return to an intact idle pose after terminal destruction. Deliver damage-state and destruction previews from actual Blockbench plus runtime evidence when integration is claimed.

## Animation inventory by asset family

### Entity and boss

- Core: default pose, idle, look/turn, walk, run, jump/fall/land, swim/fly when applicable, hurt, stun, death, spawn, despawn, and sleep/sit.
- Combat: anticipation/telegraph, melee or ranged attacks, charge, release, recoil, combo branches, block/parry, special ability, phase transition, cooldown, recovery, and interrupted variants.
- Secondary: breathing, tail/ear/wing motion, armor settling, facial/eye motion, carried equipment, enraged/damaged states, and low-LOD fallback.

### Weapon and held item

- Equip, draw, idle, inspect, use, charge, release, recoil, reload, chamber, overheat, vent, block, parry, combo, transform, repair, holster, and dropped/display states.
- Separate first-person and third-person clips when their cameras, proportions, or hand contacts differ.

### Machine and block entity

- Off/closed, startup/open, ready, active/work loop, charge, fire/process, recoil, cooldown, jam/error, overheat, damaged, repair/reset, shutdown/close, and emergency stop.
- Include material flow, indicators, doors, arms, belts, rotors, fluids, energy carriers, and safety guards only when supported by the approved model.

### Vehicle and mount

- Parked, enter/exit, startup, engine idle, accelerate, cruise, brake, reverse, steer/lean, suspension, jump/land, fly/swim, doors, cargo, weapon aim/fire/reload, damage, destruction, and shutdown.
- Define rider/seat/hand/foot sockets and in-place versus root-motion movement.

### Furniture, door, and structure

- Closed/resting, interact, open/unfold, open hold, close/fold, lock/unlock, occupied/use loop, reset, damaged/broken, repair, trap trigger, puzzle solved, and ambient motion.
- Large structures should animate modular assemblies rather than keyframing an entire Minecraft build as one object.

## Suggested timing ranges

Use these as starting points, not mandatory values: idle 2–4 s, walk 0.8–1.2 s per cycle, run 0.5–0.8 s, normal attack 0.6–1.5 s, hurt 0.25–0.6 s, death 1.2–3 s, startup 0.5–2 s, interact/open 0.4–1.5 s. Adjust for scale, weight, gameplay readability, and target tick rate.

## Combat director contract

For `motion_domain: combat`, Read the animation workshop's [combat behavior orchestration](../../fjzm-animation/references/combat-behavior-orchestration.md) reference. Build individual actions first, then connect them through `combat-behavior-system.json` using weapon profiles, distance and eye-height eligibility, seeded weighted selection, repetition penalty, bounded long combos, per-step speed, hit and whiff branches, interrupt cleanup, and phase transitions.

Run the workshop validator before runtime integration:

```powershell
python -X utf8 ../fjzm-animation/scripts/validate_combat_behavior.py combat-behavior-system.json `
  --action-library action-library.json `
  --events animation-events.json
```

A passing contract is required but not sufficient. `$fjzm` must implement or bind the decisions in the exact target Mod/runtime and collect server-authoritative evidence for targeting, selection, damage, hitboxes, events, cooldown, interruption, death, unload, multiplayer, and reload. Never copy another project's animation assets or treat its runtime IDs and timing values as a preset.

## Rig contract

```json
{
  "root_group": "root",
  "bone_hierarchy": [{"bone": "body", "parent": "root"}],
  "pivot": {"bone": "body", "origin": [0, 12, 0], "joint_role": "center_of_mass"},
  "default_pose": "neutral_idle_contact_pose",
  "attachment_sockets": [{"name": "socket_weapon_r", "parent": "hand_r", "origin": [0, 0, 0], "rotation": [0, 0, 0]}],
  "root_motion_policy": "in_place | authored_displacement | runtime_driven",
  "coordinate_system": {"up": "+Y", "forward": "-Z"},
  "constraints": ["feet remain grounded", "shield clears crystal"],
  "lod_bones": {"high": [], "medium_disabled": [], "low_disabled": []}
}
```

Use one stable root, deterministic names, correct parent-child transforms, and origins placed at physical joints or declared external pivots. Avoid animating cubes directly when a reusable group/bone should own them.

## Clip contract

Create one contract per animation:

```json
{
  "animation_id": "animation.tower.attack",
  "role": "primary_attack",
  "length_seconds": 1.6,
  "loop_mode": "once | loop | hold_on_last_frame",
  "priority": 70,
  "interruptible": true,
  "interrupt_window": [0.0, 0.3],
  "blend_in_seconds": 0.1,
  "blend_out_seconds": 0.15,
  "root_motion_policy": "in_place",
  "phases": [
    {"name": "anticipation", "start": 0.0, "end": 0.45},
    {"name": "action", "start": 0.45, "end": 0.7},
    {"name": "follow_through", "start": 0.7, "end": 1.0},
    {"name": "recovery", "start": 1.0, "end": 1.6}
  ],
  "tracks": [{"bone": "crystal", "channel": "rotation", "axis": "Y", "interpolation": "catmullrom"}],
  "events": ["event.tower.fire"],
  "contact_constraints": [{"part": "base", "target": "ground", "from": 0.0, "to": 1.6}],
  "clearance_constraints": [{"part": "shield_left", "against": "crystal", "minimum_units": 2}],
  "acceptance": ["clear attack pose", "returns to ready pose", "no interpolated clipping"]
}
```

Each clip must define affected bones, channels, axes, key poses, interpolation, timing, contacts, clearances, events, entry pose, exit pose, and relation to the default pose.

## State machine and transition contract

```json
{
  "states": [
    {"id": "idle", "clip": "animation.tower.idle", "priority": 0},
    {"id": "attack", "clip": "animation.tower.attack", "priority": 70},
    {"id": "cooldown", "clip": "animation.tower.cooldown", "priority": 40}
  ],
  "transitions": [
    {
      "from": "idle",
      "to": "attack",
      "trigger": "target_in_range_and_fire_ready",
      "guard": "not_stunned",
      "exit_time": null,
      "blend_seconds": 0.1,
      "cooldown_seconds": 0,
      "priority": 70,
      "interruptible": false,
      "retrigger_rule": "ignore_until_release",
      "pose_policy": "blend_from_current_pose",
      "cleanup_events": []
    }
  ]
}
```

Define every legal transition, not only the happy path. Cover target loss, repeated input, stun, damage, death, unload, phase change, low-LOD switch, and animation cancellation. A cooldown/hold state remains active for its declared duration instead of snapping immediately to idle.

## Central animation event table

```json
{
  "event_id": "event.tower.fire",
  "animation_id": "animation.tower.attack",
  "time_seconds": 0.62,
  "normalized_time": 0.3875,
  "particle_contract_id": "tower_muzzle_cyan",
  "sound_event": "tower.fire",
  "projectile_event": "spawn_tower_energy_bolt",
  "damage_window": {"start": 0.62, "end": 0.7},
  "hitbox_event": "enable_tower_attack_volume",
  "camera_event": null,
  "gameplay_callback": "consume_charge",
  "cleanup_event": "fx.tower.fire.stop"
}
```

This animation event table is the source of truth. Particle contracts, sounds, projectiles, and gameplay code reference its `event_id`; do not maintain conflicting duplicate times.

## Motion quality rules

- Build readable key poses using anticipation, action, follow-through, and recovery. Use overshoot and settle only when they communicate weight or mechanism.
- Preserve Minecraft form language: intentional stepped poses, clean axes, restrained curves, and no accidental rubbery scale deformation.
- Keep balance and weight believable. Lock planted feet, wheels, bases, grips, seats, and tool contacts during declared contact windows.
- For paired limbs or orbiting parts, specify direction, phase offset, radius, plane, symmetry/asymmetry, and shared versus separate pivots.
- Secondary motion follows the primary action with controlled delay; it never obscures attacks, gameplay telegraphs, or identity features.

## Loop, locomotion, and root motion

- Make first and last loop poses match in transform and motion direction; inspect the seam at normal speed and frame-by-frame.
- Prevent accumulated translation/rotation drift. Match foot contacts and phase for walk/run cycles.
- Record stride length and intended movement speed. If runtime drives movement, animate in place; if it supports authored root motion, record exact displacement and orientation change.
- Test look/aim/additive layers against locomotion when the runtime supports layering; otherwise author explicit combined clips or document the limitation.

## Transition, interruption, and cleanup

- Preview every transition matrix entry, including mid-clip interrupts and return from the current pose rather than only from ideal endpoints.
- Define blend duration, exit time, priority, pose policy, event cancellation, particle/sound cleanup, hitbox disable, and cooldown preservation.
- Never interpolate across unrelated external pivots without a planned transition path. Use staging keys when needed to avoid sweeping through geometry.
- A retrigger may restart, extend, ignore, queue, or stack; choose explicitly per transition.

## Collision and performance validation

- Check keyframes and sample every 0.05 seconds, plus denser samples for fast rotations, long limbs, projectiles, or narrow clearance.
- Test self-collision, environment clearance, rider/held-item contacts, orbit radius, ground penetration, camera obstruction, and swept volume.
- Budget active bones, animated channels, keyframes, simultaneous clips, procedural layers, and particle events. Provide high/medium/low animation tiers when targets need them.
- Low tiers may remove secondary motion or reduce update frequency but must preserve gameplay timing, event times, contacts, and silhouette.

## Production workflow

1. Confirm runtime capabilities, animation inventory, and approved `animation_backend`.
2. Create and validate the identity-scoped animation handoff; grant one write lock to `$fjzm-animation`.
3. Freeze the approved silhouette, moving assemblies, and provisional state graph.
4. Build rig hierarchy, pivots, sockets, default pose, and root-motion policy only within the approved handoff.
5. Graybox the highest-risk clips and transitions before texture detail.
6. Author primary poses, timing, interpolation, contacts, clearances, and secondary motion.
7. Add the central event table, but defer particle, sound, projectile, hitbox, and gameplay binding until the specialist result returns.
8. Test loops, every legal transition, interruption, retrigger, cleanup, collision, and LOD.
9. For combat, create and validate `combat-behavior-system.json` against the action library and central event table.
10. Reopen the saved project in actual Blockbench or actual Blender according to the locked backend; return `animation-result.json` to `$fjzm`, then test approved controllers, events, behavior selection, branches, blending, exports, and root motion in the actual target runtime.

## Acceptance and delivery

- Route-specific authoring evidence: actual Blockbench or actual Blender captures for each full clip at normal speed, key poses, loop seam, transition prototypes, damage-state and destruction previews, hierarchy, pivots/joints, and contacts.
- Runtime evidence: state changes, transition matrix, priorities, blends, interruptions, event synchronization, hitboxes, particles/sounds, root motion, and cleanup.
- Deliver the immutable `.bbmodel` plus the route-owned `.bbmodel` or `.blend`, runtime exports, `rig-map.json` and `action-library.json` when applicable, `animation-system.json`, animation event table, `combat-behavior-system.json` when applicable, authorized controller files, previews, validator evidence, collision report, and known limitations.
