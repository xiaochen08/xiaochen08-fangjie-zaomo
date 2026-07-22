# Combat runtime integration

## Boundary

Use this reference only after `$fjzm-animation` returns a passing, identity-matched `combat-behavior-system.json`, `action-library.json`, `animation-events.json`, and `animation-result.json`. The behavior contract is design intent. `$fjzm` owns the runtime adapter, gameplay truth, approval, and evidence.

Never claim implementation from an authoring preview or a passing JSON validator. Record `implementation_status` as `planned | bound | built | runtime_verified`. Only actual target-game evidence permits `runtime_verified`.

## Lock the exact target first

Before writing runtime code, inspect and lock:

- Minecraft edition and exact version;
- loader and exact version;
- animation runtime and exact version;
- mappings, source-set layout, and build tooling;
- action registration API and event callback API from the installed dependency;
- server/client ownership, networking, save format, and reload behavior.

Do not copy an adapter from another loader or Epic Fight/GeckoLib release. If the exact runtime is unavailable, stop at an implementation plan and keep `implementation_status: planned`.

## Runtime decision loop

At one authoritative combat decision point:

1. Read asset identity, current weapon profile, boss phase, target, cooldowns, and recent series history.
2. Build `eligible_series` by filtering weapon category/style, distance, relative eye height, line of sight, grounded/airborne state, phase, cooldown, resource state, and interrupt lock.
3. If empty, play or enter the declared fallback action; never retain a stale previous attack.
4. Apply each candidate's base weight, cooldown modifier, and repetition penalty.
5. Derive the deterministic seed from the contract's seed source, such as entity UUID plus combat-cycle counter. Log the seed for reproduction.
6. Select exactly one series, reserve its cooldown, and begin its first action through the installed action registration mechanism.
7. Advance only through declared transitions and hit/whiff branches.
8. On interruption, execute the referenced cleanup policy before another state owns movement or events.

Selection is server-authoritative. Clients receive the chosen series/action and presentation state; they do not independently roll weights or decide damage.

## Action and event binding

Build an explicit mapping table from every contract `action_id` to one registered runtime action. Missing action registration is a build blocker. Do not fall back silently to idle if an attack action is missing.

Build a second mapping from each `event_id` to one runtime handler. One event has one gameplay owner:

- hitbox enable/disable and damage: server;
- projectile creation: server at the release event;
- projectile impact: collision handler, not a guessed animation delay;
- hit confirm: server collision/damage result;
- particles and positional sound: server broadcast or one deduplicated client presentation path;
- camera/UI-only feedback: local client after the authoritative event is known;
- equipment state changes: server, synchronized to clients.

Audio, particles, camera shake, and damage may share a named event time, but they must not each invent another timestamp.

## Combo state

Track at minimum:

- active series ID and step index;
- action start tick and normalized progress;
- target identity and last valid target state;
- hit confirm / whiff result;
- root-motion ownership;
- interrupt lock and cancel-window status;
- cooldowns and recent-series history;
- boss phase and one-shot transition state;
- active event instances requiring cleanup.

Do not serialize unsafe transient hitboxes or duplicate one-shot events. For save and reload, either restore a specifically supported safe state or cancel to a declared recovery/fallback with cleanup. Document which policy is used.

## Interruption precedence

Evaluate high-priority terminal transitions before ordinary combo continuation. The minimum order begins with death and unload, then approved phase change/knockdown/stun/hurt/target-loss rules. Respect protected contact windows only where the contract permits them.

Cleanup must disable active attack volumes, release root-motion control, cancel unspawned projectiles, stop looping presentation events, clear temporary equipment overrides, and prevent the previous step from firing another callback after ownership changes.

## Backend adapters

### Blender / Epic Fight

- Register exported actions through the exact installed Epic Fight API and verify armature/action compatibility.
- Map contract action IDs to registered Epic Fight animations without reusing third-party asset IDs as placeholders.
- Bind behavior selection through a supported mob-patch/AI/custom runtime route for that version.
- Verify root movement, speed, transitions, hitbox windows, interruption, and multiplayer synchronization in-game.

### Blockbench / GeckoLib or custom controller

- Export the approved Blockbench clips in the format supported by the exact runtime version.
- Use a controller/custom server state to select series and steps; do not ask the client animation controller to own damage truth.
- Forward authoritative event state to presentation callbacks and deduplicate them.
- Verify that transition and speed features actually exist in the chosen runtime; document any downgraded behavior and obtain approval.

## Debug trace

For each decision record a compact trace:

```text
entity, combat_cycle, weapon_profile, phase, target_distance, target_eye_height,
eligible_series, rejected_series_with_reason, deterministic_seed, selected_series,
step, action_id, branch_result, interrupt_reason, cleanup_events
```

This trace is evidence and a diagnosis tool. It makes “为什么又放同一招”“为什么隔着墙攻击”“为什么死亡后还有判定” reproducible instead of subjective.

## Runtime acceptance matrix

Test at least:

- each weapon profile and every registered action;
- minimum, middle, maximum, and just-outside distance/height boundaries;
- line-of-sight loss, target death, target swap, and target unload;
- hit confirm and deliberate whiff for every branching step;
- cooldown and repetition behavior over a long seeded run;
- hurt, stun, knockdown, phase change, death, and unload at startup/contact/recovery;
- root motion against walls, ledges, stairs, water, and knockback where relevant;
- particle/audio/projectile duplication and cleanup;
- single player, dedicated server, latency, reconnect, chunk unload/reload, and multiplayer observers;
- save and reload during idle, combo, recovery, phase transition, and death;
- low-performance/LOD behavior without changing gameplay event timing.

Store video/log evidence with exact build hashes and runtime versions. A successful build is not runtime proof; a single-player preview is not multiplayer proof.

## Delivery

Return the versioned runtime adapter, registered-action map, registered-event map, build output, debug traces, acceptance matrix, save/reload policy, multiplayer evidence, known limitations, and updated `implementation_status`. Re-run the asset bundle and release-evidence validators before any formal compatibility claim.
