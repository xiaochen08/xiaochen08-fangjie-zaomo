# Model-first runtime readiness gate

Use this gate when the user has no authorized Mod project and selects `model_first`. The purpose is to preserve a useful Blockbench source while preventing a visually complete but technically unusable asset.

## Decision principle

Do not force Mod creation for every asset. Classify runtime risk before concept generation, recommend the safest route, and cap production at the highest reversible stage supported by confirmed facts.

| Risk | Typical assets | Default route | Model-first ceiling |
|---|---|---|---|
| low | static decorative block, simple item, furniture, display prop | model-first is acceptable | `runtime_neutral_source` |
| medium | simple animated entity, wearable with states, modest vehicle | recommend `create_mod_first` | validated `runtime_neutral_source` |
| high | complex animated entity or Boss, animated block entity, projectile weapon/turret, targeting/damage, particles/audio, custom renderer/shader, destruction, multiplayer synchronization | `create_mod_first is the default recommendation` | `concept_only`, `graybox_only`, or validated `runtime_neutral_source` only |

Complexity outranks appearance. A static ornate statue may be low risk; a visually simple cube with inventory, networking, dynamic rendering, or projectiles is not.

## Mandatory intake before images

Ask and record:

1. Java edition target, intended `asset_role`, in-game scale, collision/hitbox owner, and whether it is a block, item, entity, block entity, projectile, wearable, structure, or display.
2. Required runtime features: animation, AI/targeting, damage, projectile, particles, audio, emissive/shader behavior, destruction, persistence, inventory, networking, and multiplayer synchronization.
3. Minecraft version constraint, loader preference, mappings, animation runtime, render path, server requirement, and whether each value is locked, provisional, unresolved, or not applicable.

Do not guess a runtime value. A user who does not know may keep a value provisional, but provisional and unresolved values lower the production ceiling.

## Route and consent gate

For medium/high risk, explain why a minimal Mod shell reduces rework and present `create_mod_first` first. If the user still chooses model-first, record:

- verbatim decline evidence for the Mod-first recommendation;
- explicit risk acceptance evidence;
- the consequences `runtime exports deferred`, `integration rework may be required`, and `no game-ready claim`;
- the exact production ceiling and unresolved blockers.

Silence, urgency, “先做出来再说,” concept approval, or permission to model is not decline evidence or risk acceptance.

## Production ceilings

- `concept_only`: requirements or asset role are unresolved; generate only the approved A/B/C concept process.
- `graybox_only`: critical render path, animation runtime, scale/hitbox ownership, or dynamic role remains unresolved; create only reversible proportions, hierarchy candidates, and motion feasibility tests.
- `runtime_neutral_source`: create an editable `.bbmodel`, textures, adapter-safe groups/origins, provisional clips, and stable event/locator contracts; do not create platform-specific exports or claim game readiness.
- `platform_export`: prohibited for `runtime_deferred`; it requires an inspected authorized project and a reconciled target profile.

Do not create a final rig, irreversible platform-specific animation export, generated Java model class, controller, registry, or compiled artifact above the allowed stage.

## Required `runtime-contract.json`

After concept approval and before detailed production, create one identity-scoped contract containing:

- `project_id`, `asset_id`, `asset_version`, `edition`, `route_choice`, and `project_status`;
- `asset_role`, `runtime_risk`, and `runtime_features`;
- target status/value pairs for Minecraft, loader, mappings, animation runtime, and `render_path`;
- multiplayer requirement and server/client ownership assumptions;
- stable `rig_signature`, `animation_ids`, `event_ids`, `locator_ids`, and texture IDs;
- Mod-first recommendation/decline evidence, risk acceptance, production ceiling, blockers, and deferred handoff state.

Use `projectile_spawn` as the stable projectile locator when a projectile is required. Use separate stable IDs for every model; never reuse a generic attack, muzzle, sound, particle, or animation ID across unrelated assets.

Run:

```powershell
python -X utf8 scripts/validate_runtime_contract.py '.\runtime-contract.json'
```

Do not proceed beyond the validated stage while the command reports an error.

## Runtime-neutral source rules

- Keep `.bbmodel` as the editable source of truth; export copies later.
- Use clean named groups, correct origins, stable pivots, and a recorded rig signature.
- Separate visual animation from gameplay ownership. Preview projectiles may demonstrate timing, but the future server owns real spawn, collision, damage, cooldown, and persistence.
- Record exact animation-event timestamps and locators without pretending the event is implemented.
- Separate base textures, emissive masks, particle contracts, and audio contracts.
- Mark loader/runtime-specific files as deferred instead of inventing them.

## Connecting the later Mod

When an authorized project becomes available:

1. Inspect and hash its version/loader/mappings/runtime markers.
2. Compare the detected target with `runtime-contract.json`; do not silently rewrite the source.
3. If values differ, produce a migration impact report for format, rig, animation, rendering, networking, and resources; obtain approval before changing the model.
4. Create `integration-map.json` mapping every model ID to the runtime owner: model/texture path, renderer, entity or block-entity registration, animation controller, event callback, particle, sound, projectile, state sync, and save/load behavior.
5. Generate platform exports into the authorized project, build, launch, and run the complete runtime evidence matrix.

The adapter should absorb loader/version naming differences whenever possible. Change the approved geometry or rig only when an evidence-backed runtime constraint makes adaptation impossible.

## Red flags

- “The `.bbmodel` exists, so it is game-ready.”
- “We can decide entity versus block entity later.”
- “The animation itself can deal damage or perform networking.”
- “A preview projectile proves collision.”
- “Any GeckoLib/loader/Minecraft version will be compatible.”
- “We can rename bones and events during integration without a migration record.”

All of these require stopping at the current ceiling and resolving the runtime contract.
