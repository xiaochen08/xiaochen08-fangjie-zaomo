# Related asset ecosystem intake

## Opening decision

After locking the primary asset and category, ask whether the user wants a single asset or an approved asset set. Briefly explain that related assets can make the design usable in-game, then present a compact, subject-specific suggestion list. The user may approve, decline, defer, rename, or add entries.

Do not auto-add related assets. Do not treat “make it complete,” silence, urgency, a concept choice, or permission for the primary model as approval for surrounding assets. Record every suggestion as `suggested`, then obtain a separate `approved | declined | deferred` decision. A suggestion is not production approval.

## Expansion map

Suggest only relevant options, normally no more than eight at once:

- Combat: weapons, ammunition, projectiles, shields, traps, attack attachments, hit carriers, and impact objects.
- Function: bases, mounts, controllers, containers, power cores, cables, upgrade modules, interaction parts, and repair tools.
- Character/world: armor, pets, summons, minions, drops, loot, spawn objects, trophies, biome props, and faction variants.
- Presentation/state: damaged variants, detachable debris, effect carriers, sound emitters, wrecks, transformation shells, and display/inventory variants.
- Structures/interiors: doors, windows, lamps, signs, furniture, storage, machinery, rubble, and modular building pieces.
- Vehicles: seats, wheels/tracks, mounted weapons, cargo, fuel/energy units, trailers, wrecks, and rider equipment.

Tailor the list to the primary asset. For example, a boss may need a projectile, summon, weapon, drop, trophy, spawn object, and wreck; a turret may need an energy bolt, base, power core, controller, upgrade module, debris, and destroyed state. Do not dump the full taxonomy on the user.

## Scope and identity contract

Keep the primary asset first. For each related entry record:

```json
{
  "display_name_zh": "能量弹",
  "relationship": "projectile_of",
  "category": "magic_projectile",
  "scope_status": "suggested | approved | declined | deferred",
  "scope_approval_evidence": "verbatim user decision or null",
  "asset_id": "tower_energy_bolt or null"
}
```

Every approved related model receives an independent asset_id, identity-scoped directory, `model-spec.json`, concept manifest, concept approval, rig signature, and bundle validation. Record relationship and scope approval evidence in the project index. Never reuse the primary model's approval for another asset.

Do not create files, concept geometry, audio bindings, animation IDs, or runtime registrations for declined, deferred, or merely suggested entries. If one approved asset changes another asset's silhouette, socket, event timing, collision, texture budget, or rig, reopen only the affected approvals.

## Pre-image confirmation gate

Before image generation, show the user a confirmation table containing:

| Required row | Value |
|---|---|
| primary asset | Locked name and identity |
| asset storage folder | User-approved drive and absolute per-model folder |
| scope mode | Single asset or approved set |
| approved related assets | Exact list, relationships, and relative scale |
| declined/deferred suggestions | Listed as excluded from images |
| damage/destruction scope | Not applicable, impact-only, staged damage, or full destruction plus states and terminal route |
| required image sheets | Primary, related-assets, damage/destruction keyframes, and optional effect sheet |

Wait for confirmation or correction. “No related assets” and “non-destructible/not applicable” are valid only when explicitly answered not applicable; never infer them from silence. Freeze the table as the image-generation scope and inject its approved values into every A/B/C prompt. Any correction reopens this gate before regeneration.

## Concept boundary

Concept previews may show only the primary asset plus explicitly approved related assets. Label which item is the primary asset and list every approved companion outside the image. Unapproved suggestions remain text-only. If the user approves multiple assets, decide whether they need separate A/B/C sheets or one scale-comparison sheet plus individual manifests; never hide an asset inside another model's manifest.
