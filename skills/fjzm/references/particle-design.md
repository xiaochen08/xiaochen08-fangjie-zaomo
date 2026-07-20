# Particle effect key design

Blockbench .bbmodel does not implement runtime particles. It can provide model geometry, bones/groups, origins, animations, and event timing; the selected Minecraft runtime must spawn, update, and render the effect.

## When to activate this design

Use this contract when particles or runtime effects are requested or implied by charging, firing, impact, magic, smoke, steam, sparks, aura, trails, transformation, teleportation, damage, death, weather, or environmental activity.

Before concept generation, ask compactly about:

- particle purpose/state: idle ambience, activation, charge, attack, projectile, impact, cooldown, damage, death, or environment;
- emitter bone/group or socket, approximate location, direction, whether it follows the animated part, and required clearance;
- trigger animation and event time, duration, stop condition, interruption, and retrigger behavior;
- spawn mode: burst, continuous, trail, orbit, beam carrier, volume, surface, or impact;
- visual language: sprite/mesh carrier, palette, emissive appearance, size/alpha curve, speed, spread, gravity, drag, collision, and lighting;
- particle budget and LOD, gameplay distance, target hardware, accessibility, and fallback;
- runtime implementation: Bedrock particle/controller, Java mod animation event, custom renderer, command/datapack approximation, or unspecified.

## Particle contract

Record one object per effect in the consultation brief, then freeze it in `model-spec.json` after concept approval:

```json
{
  "effect_id": "tower_charge_cyan",
  "role": "charge_telegraph",
  "runtime_implementation": "bedrock | java_mod | custom | command | unspecified",
  "emitter_group": "fx_core_charge",
  "local_position": [0, 48, 0],
  "local_rotation": [0, 0, 0],
  "space": "local | world",
  "follow": "core_crystal | none",
  "event": "fx.tower.charge.start",
  "animation": "animation.tower.attack",
  "time_seconds": 0.35,
  "spawn_mode": "burst | continuous | trail | orbit | volume | impact",
  "stop_event": "fx.tower.charge.stop",
  "retrigger_rule": "restart | extend | ignore | stack",
  "sprite_or_material": "particles/tower_charge",
  "palette": ["#7ff6ff", "#2ac9e8"],
  "emissive": true,
  "rate_per_second": 24,
  "burst_count": 0,
  "lifetime_seconds": 0.7,
  "size_curve": [[0, 0.15], [0.4, 0.3], [1, 0]],
  "alpha_curve": [[0, 0], [0.1, 1], [1, 0]],
  "velocity": [0, 1.5, 0],
  "spread_degrees": 12,
  "gravity": 0,
  "drag": 0.08,
  "collision": "none | world | model_proxy",
  "max_active_particles": 24,
  "lod": {"high": 1.0, "medium": 0.5, "low": 0.25, "cull_distance_blocks": 48},
  "fallback": "emissive texture pulse only"
}
```

Unknown values remain explicit blockers. Do not invent platform-specific particle files while runtime implementation is unspecified.

## Model-side anchors

- Create a stable empty group/bone named `fx_<effect_id>_<role>` at each emitter. Add it to validator `required_groups` with its exact origin.
- Define local forward/up axes and whether the emitter follows a moving bone or remains in world space.
- Use separate emitters for muzzle, core, feet, impact, trails, or orbit paths; never animate one ambiguous origin between unrelated locations.
- Keep emitter offsets outside solid geometry when required. Sample animated frames to prevent trails, muzzle flashes, or orbit particles from spawning inside the model.
- Add no visible cube to an emitter group unless the selected design includes a physical nozzle, rune, crystal, vent, or other carrier.

## Timing and state rules

- Bind each start/burst/stop event to a named animation and exact `time_seconds`; document normalized time too when the runtime needs it.
- Reference the central `animation-system.md` event ID; its animation event table is the source of truth for timing.
- Separate telegraph, release, projectile spawn, hit, lingering field, cooldown, and cleanup events.
- Specify what happens on animation interruption, target loss, repeated attack, death, unload, and low-LOD culling.
- Damage and hitboxes are gameplay logic; synchronize them to the visual event without treating particles as collision truth.

## Effect preview prompt

The clean model sheet remains particle-free. For every concept whose identity depends on an effect, generate a separate effect keyframe preview using the clean sheet as the geometry reference:

```text
Use the supplied Blockbench-faithful model sheet as an immutable geometry reference. Show the exact same model, proportions, parts, texture, camera, and lighting at {ANIMATION} time {TIME_SECONDS}s. Add only the contracted {EFFECT_ID} particles from emitter {EMITTER_GROUP}: {SPAWN_MODE}, {PALETTE}, {RATE_OR_BURST}, {SIZE_ALPHA}, {VELOCITY_SPREAD}, and {LIFETIME}. The effect must not alter model geometry, hide important parts, add cinematic lighting, or invent extra glows, smoke, debris, weapons, armor, or scenery. Render one clean gameplay-readable keyframe.
```

Label the separate effect keyframe preview outside the image. Explain that it represents the runtime effect, not geometry stored inside `.bbmodel`.

## Acceptance and delivery

- Check visual readability, timing, attachment, interruption, cleanup, and LOD in the actual target runtime.
- Verify high/medium/low particle budgets and a no-particle fallback.
- Deliver emitter group names/transforms, animation event table, particle contract, particle textures/materials, runtime files when authorized, and a runtime capture.
- A Blockbench screenshot proves only the model and anchors; it does not prove the particle system works.
