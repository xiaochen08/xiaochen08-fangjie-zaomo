# Combat behavior orchestration

## Purpose and ownership

This contract turns good individual clips into a readable combat performance. It applies to `motion_domain: combat` on either animation backend. `$fjzm-animation` authors and validates `combat-behavior-system.json`; it does not write gameplay AI, damage, hit detection, target selection, or network authority. `$fjzm` owns runtime AI, runtime binding, approval, and release.

The design borrows only general, publicly observable structure from high-quality Minecraft combat projects: weapon-driven action pools, condition-gated behavior series, weighted selection, interruptibility, variable play speed, long combo sequencing, and timed audiovisual/gameplay events. Do not copy third-party animation files, exported actions, keyframes, animation IDs, or proprietary curves. Every FJZM asset requires original key poses, original timing, original spacing, and project-owned runtime IDs.

Public-reference evidence may be recorded with repository URL, commit, and inspected file paths. It is research evidence, not a runtime dependency and not permission to redistribute assets.

## Public Annoying Villagers research incorporated

The v5.2 design was checked against the public [IAFEnvoy/AnnoyingVillagers](https://github.com/IAFEnvoy/AnnoyingVillagers) source. Its observable mob-patch files use behavior series selected by equipment/weapon context, positive weights, interrupt/loop flags, distance and eye-height predicates, ordered multi-action sequences, and per-action speed. Its entity code also coordinates sounds, particles, equipment changes, and projectiles over timed gameplay sequences. FJZM generalizes those ideas into a stricter original-asset contract with identity hashes, anti-repetition history, hit/whiff branches, bounded loops, phase coverage, centralized events, cleanup, and runtime evidence.

This research does not establish that the public repository contains the original animation-authoring projects, nor does it justify redistributing Epic Fight, WOM, or Annoying Villagers animation assets. Use it to understand orchestration, then create project-owned movement and timing.

## Three-layer combat director

1. **Action layer** — original clips in `action-library.json`: stance, locomotion, guard, attack, dodge, aerial, hurt, phase-change, recovery, and death actions.
2. **Behavior layer** — `combat-behavior-system.json`: weapon category and style, distance and eye-height gates, weighted selection, repetition penalty, cooldown, long combo order, hit and whiff branches, play_speed, interruption, and phase transition rules.
3. **Runtime layer** — Mod code/controllers owned by `$fjzm`: authoritative target sensing, weighted choice, damage/hitbox truth, event dispatch, networking, cleanup, and actual runtime evidence.

The action layer says how one move looks. The behavior layer says when and why it may play. The runtime layer makes that decision true in the game. Never collapse all three into a single animation timeline.

## Required contract

Create one identity-locked `combat-behavior-system.json` per `project_id / asset_id / asset_version`. It must repeat `model_sha256`, `rig_signature`, and `animation_backend`, and it must match both `action-library.json` and `animation-events.json`.

Minimum top-level sections:

- `runtime_ownership`
- `selection_policy`
- `weapon_profiles`
- `interrupt_policies`
- `behavior_series`
- `phase_profiles`
- `acceptance`

All runtime-facing IDs are ASCII-safe. Chinese display names belong in localization, design notes, and user-facing previews, not registry IDs.

## Weapon profiles and stance identity

Define a profile for every meaningful equipment posture, not merely every item name. A sword-and-shield stance, two-handed greatsword stance, empty-hand style, bow stance, and spellcasting stance may share a skeleton but must not silently share incompatible actions.

Each profile declares:

- stable `weapon_profile_id`, `category`, and `style`;
- allowed actions and required hand/socket contacts;
- preferred range and locomotion posture in design notes;
- guard, recovery, and fallback actions;
- whether a weapon swap requires a transition action or equipment event.

An action outside the profile's allowlist is an error. This prevents a creature from firing a bow action while holding a greatsword or using a one-handed recovery after a two-handed strike.

## Sensors and eligibility

Every behavior series declares conditions before it can enter:

- horizontal distance band;
- relative eye-height or vertical band;
- grounded, airborne, swimming, mounted, or climbing state;
- line of sight and target validity;
- self state such as stamina, cooldown, health phase, enraged state, or weapon readiness;
- optional target state such as blocking, stunned, airborne, or recovering.

Distance and eye-height are gates, not animation decoration. Validate them in the actual runtime because authoring previews cannot prove target sensing or navigation. Every reachable combat state needs a safe fallback when no attack series qualifies.

## Weighted selection without slot-machine repetition

Use `seeded_weighted` selection. Weight expresses relative preference among currently valid series, not a fixed percentage. Apply a repetition penalty based on recent history, enforce cooldowns, and provide a fallback action. The seed source must be reproducible enough for debugging while remaining varied across entities or combat cycles.

Do not select a series only because it has the highest weight. First filter by weapon profile, phase, range, height, line of sight, state, cooldown, and interrupt lock. Then apply weight and repetition control. Log the eligible set, seed, chosen series, rejected reasons, and recent history in debug evidence.

## Combo construction

A long combo is an ordered dramatic sentence, not many attacks glued together. It may contain anticipation, approach, first commitment, continuation, reposition, finisher, and recovery. There is no required fixed combo length; use the shortest sequence that communicates intent and remains readable. The machine safety ceiling is 32 steps and any loop is explicitly bounded.

Each step declares:

- `action_id` from `action-library.json`;
- per-step `play_speed` in the validated safe range rather than one global copied value;
- direct, blended, or conditional transition;
- root-motion policy and contact expectations;
- normalized cancel window;
- event IDs from `animation-events.json`;
- explicit hit and whiff branches.

On hit, a combo may continue, branch to a finisher, reposition, or recover. On whiff, it usually recovers, retreats, or chooses a safer branch. Do not grant identical outcomes automatically: readable commitment and punishment are part of the action design.

## Motion design standard

Every combat action follows an intentional force path:

1. readable anticipation and eye/head lead;
2. center-of-mass shift before limb acceleration;
3. planted or deliberately released foot contact;
4. hip-to-torso-to-shoulder-to-weapon overlap;
5. decisive contact pose and event window;
6. follow-through that respects momentum;
7. recovery that exposes weight, fatigue, or tactical intent.

Preserve the Minecraft silhouette and block language while using whole-body weight transfer. Use asymmetry, overlap, controlled overshoot, and secondary motion to avoid robotic action, but do not introduce rubbery scaling or unreadable blur. Dash, roll, leap, aerial, and knockback actions require explicit displacement, landing, wall/ground clearance, and camera-readability checks.

## Interruptions, priorities, and cleanup

Each series references one interrupt policy. At minimum it covers hurt, stun, knockdown, target loss, phase change, death, and unload. Death and unload must always be represented. Protected startup or contact windows may restrict ordinary hurt interruption, but cannot trap the entity in an infinite series.

An interrupt policy declares priority, current-pose blend behavior, cooldown preservation, and cleanup events. Cleanup disables hitboxes, cancels unspawned projectiles, stops loops, releases root-motion locks, clears temporary equipment states, and prevents duplicate particle/audio events. Preview the visual transition, then verify the actual event cleanup in the target runtime.

## Boss phases

Boss phase health ranges must cover `0..1` exactly with no gap or overlap. Each phase declares allowed series and an original phase transition action. Phase changes may replace weights, add new actions, alter safe speed ranges within the approved action contract, or unlock aerial/area control, but they do not silently mutate the rig or geometry.

The phase transition is higher priority than ordinary attacks and lower only than terminal death/unload rules unless the approved design states otherwise. Fire one-shot audiovisual events once and prove they do not duplicate after save/reload or network resynchronization.

## Timed event choreography

Animation events are named synchronization points. Audio, particles, projectiles, equipment swaps, camera effects, and damage windows reference those points; gameplay truth remains server-authoritative. Projectile spawn belongs to the release/contact event, impact belongs to collision, and a looping effect has an explicit stop and interruption path.

Do not use scattered delay calls as the only source of truth. Runtime adapters may schedule work in ticks, but their event IDs and intended normalized times must trace back to `animation-events.json` and the approved combat behavior step.

## Validation command

```powershell
python -X utf8 scripts/validate_combat_behavior.py combat-behavior-system.json `
  --action-library action-library.json `
  --events animation-events.json
```

Stop on any error. A passing document proves contract consistency only; it does not prove visual quality or game behavior.

## Evidence matrix

For every behavior series capture:

- normal-speed authoring preview and key-pose sheet;
- entry from every legal locomotion/stance state;
- hit and whiff branch;
- minimum/maximum range and eye-height boundary;
- each allowed interrupt and its cleanup;
- repeated-selection run showing weights, cooldown, and repetition penalty;
- phase transition entry/exit;
- root displacement, contacts, swept clearance, and landing where relevant;
- actual runtime evidence for selection, events, hitboxes, damage, projectiles, audio, particles, multiplayer, death, unload, and reload.

Do not claim runtime evidence from Blockbench or Blender. If the Mod runtime is unavailable, deliver the validated contract and clearly mark runtime integration and evidence as pending.

## Common failure patterns

| Failure | Root cause | Required correction |
|---|---|---|
| Good clips but dull combat | No behavior director | Add conditions, selection history, branches, and phase rhythm |
| Same combo repeats | Pure random/one large weight | Seeded weighted selection plus repetition penalty and cooldown |
| Attack plays out of range | Preview treated as AI | Add distance/height eligibility and runtime boundary tests |
| Combo continues after target leaves | Missing interrupt route | Add target-loss branch and cleanup |
| Weapon and motion disagree | No stance profile | Bind actions to weapon category and style allowlists |
| Fast move looks floaty | Limbs lead the body | Rebuild force path and center-of-mass transfer |
| Effects double-fire | Two timing authorities | Use one animation event ID and server-authoritative dispatch |
| Death leaves hitboxes or loops alive | Weak priority/cleanup | Death/unload override and mandatory cleanup events |
