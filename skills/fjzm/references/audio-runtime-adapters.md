# Minecraft audio runtime adapters

## Contents

- Target selection and version evidence
- Shared ownership rules
- Java Fabric, NeoForge, Forge, GeckoLib 4/5
- Bedrock resource and behavior packs
- MCreator workspaces
- Runtime verification matrix

## Target selection gate

Before writing integration files, record:

- Minecraft edition and exact version;
- Java loader and version: Fabric, NeoForge, or Forge;
- animation runtime and installed version: vanilla/custom, GeckoLib 4, or GeckoLib 5;
- asset type: entity, block entity, item, projectile, UI, structure, or ambience;
- available project/resource-pack root and package namespace.

Inspect the existing build files, dependencies, mappings, and generated sources. Never infer APIs from a different version. If the project is absent or the target is unspecified, stop at `audio-manifest.json`, exported audio, and an adapter plan.

## Shared ownership contract

For every event choose one playback owner. A server-authoritative gameplay event owns attacks, damage, projectile creation, collision truth, death, and persistent state. A client presentation event owns local spatial playback, subtitles, and visual timing after receiving synchronized state.

Animation keyframes may own cosmetic events whose timing exists only inside the clip. A projectile collision owns the impact position and impact sound. Prevent a multiplayer duplicate by ensuring a sound is not emitted once by the server broadcast and again by every client's animation callback. Record the one playback owner in the manifest and central event table.

## Java adapter

### Required project evidence

Confirm loader, Minecraft version, mappings, mod namespace, GeckoLib version, and whether common/client source sets are separated. Do not copy imports or registry code between Fabric, NeoForge, and Forge without verifying the installed API.

### Resource delivery

Place approved resources under the mod namespace:

```text
src/main/resources/assets/<namespace>/
├─ sounds.json
├─ sounds/<asset>/<event>.ogg
└─ lang/en_us.json
   lang/zh_cn.json
```

Register each custom `SoundEvent` using the loader's installed registry API. `sounds.json` maps the event path to one or more versioned resources; language files define subtitles. Short positional SFX normally use mono and memory loading. Long ambience/music may use the loader/runtime's verified streaming option.

### GeckoLib integration

- GeckoLib 4: inspect the installed GeckoLib 4 documentation/API and register the supported sound keyframe handler on the correct animation controller.
- GeckoLib 5: inspect the installed GeckoLib 5 API; use its supported sound handler or auto-playing handler only when identifier, volume, and pitch syntax matches that version.
- Never assume a Blockbench sound keyframe registers the `SoundEvent`.
- Use a custom instruction/gameplay callback instead of a sound keyframe when the server must own the action.
- Keep impact sounds on projectile collision; do not estimate travel time in the attack clip.

### Java loop lifecycle

Use a state-owned client sound instance when a loop must stop on state exit, unload, destruction, distance, mute/category change, or interruption. Keyframe repetition is not a loop manager. Deduplicate by entity/block position plus event ID and enforce `max_simultaneous_instances`.

### Java delivery evidence

Deliver `sounds.json`, OGG resources, localized subtitle keys, loader-specific `SoundEvent` registration, animation handler/controller changes, packet or synchronized-data path when needed, and an in-game multiplayer test log/video.

## Bedrock adapter

### Resource pack

Deliver:

```text
resource_pack/
├─ sounds/sound_definitions.json
├─ sounds/<asset>/<event>.ogg
├─ entity/<asset>.entity.json
├─ animations/<asset>.animation.json
├─ animation_controllers/<asset>.animation_controllers.json
└─ texts/<locale>.lang
```

Register full events in `sound_definitions.json`. Map short sound names in the client entity `sound_effects` section. Animation `sound_effects` keyframes may reference the short name and locator. Use an animation controller state for entry/exit-driven sound and visual behavior. Verify the selected Bedrock format version supports every field used.

### Behavior pack

Use behavior events, components, commands, or Script API only when gameplay truth is required. The behavior pack owns server-authoritative state; the resource pack owns presentation. Avoid playing the same event from both a behavior event and client animation controller unless one is explicitly suppressed.

### Bedrock delivery evidence

Deliver resource/behavior pack manifests, `sound_definitions.json`, client entity mapping, animation/controller references, locators, localized text, behavior/script trigger when authorized, and an actual multiplayer world test.

## MCreator adapter

Inspect the workspace version, generator type, target Minecraft version, loader, installed plugins, and whether GeckoLib support is built in or plugin-provided. Never assume a tutorial for another MCreator release applies.

Import versioned OGG resources through the workspace resource manager, create the custom sound event using supported UI/generated registry facilities, and bind it through a workspace procedure at the declared gameplay event. For GeckoLib animation callbacks, use only the plugin/version's supported procedure or generated extension point. Preserve generated-code boundaries; do not hand-edit regenerated files unless the workspace explicitly supports it.

Deliver the imported resource, sound registry entry, workspace procedure, trigger assignment, animation/plugin configuration, and an exported build test. If a required extension point is unavailable, document the limitation instead of silently generating unsupported Java.

## Runtime verification matrix

Test each applicable row:

| Case | Required observation |
|---|---|
| Single player | Correct origin, timing, subtitle, volume, stop behavior |
| Dedicated server + two clients | One audible event per listener; no multiplayer duplicate |
| Rapid retrigger | Budget enforced; variants and cooldown behave correctly |
| Interrupt/stun/death | Loops and queued cues clean up |
| Projectile near/far target | Launch fixed to release; impact fixed to collision |
| Chunk unload/reload | No ghost loop; persistent state restores correctly |
| Many nearby emitters | Attenuation, priority, and simultaneous-instance budget hold |
| Audio disabled | Critical visual_telegraph still communicates gameplay |

Do not claim Java, Bedrock, or MCreator integration from Blockbench playback alone.
