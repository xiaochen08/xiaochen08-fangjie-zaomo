# Shader, lighting, and material compatibility gate

Read this before concepts for every model. A user may choose the vanilla baseline, but the decision itself is mandatory because lighting, emissive masks, transparency, PBR maps, render layers, texture painting, runtime adapters, and evidence cannot be repaired reliably after production.

## Plain-language intake

Ask these together with the other pre-concept questions, in Chinese when the user uses Chinese:

1. Must the model remain readable with shaders disabled? The required default is a **no-shader fallback**; exceptions are blocked because users may disable shaders or use an unsupported device.
2. Is the target vanilla/common-safe rendering, **Iris or OptiFine**, or another exact loader? For a named target, lock Minecraft version plus loader name and version.
3. Is there a required shader pack? Record the **exact shader-pack name and version**, official source, date checked, and relevant preset. “Popular shaders” or “all shaders” is unresolved.
4. Is PBR required? Lock the **PBR material standard and version** and its exact normal/specular or normal/roughness/metalness channel convention. Do not guess LabPBR or map channels.
5. Define **emissive behavior**: none, visual full-bright mask, optional/required bloom, and whether actual world light is implemented by runtime block light or dynamic-light integration. Emissive pixels alone do not prove that nearby blocks are illuminated.
6. Define transparency: opaque, cutout, translucent, or mixed; lock the **transparency/render layer**, sorting risk, overlapping-surface behavior, and fallback.
7. Lock performance expectations: gameplay distance, target hardware, texture/map count, atlas dimensions, number of translucent layers, and any custom-render passes.

Do not invoke imagegen until the user answers or explicitly accepts the recommended baseline. If the answer is unknown, choose `vanilla_baseline`, keep optional maps absent, and record named shader/PBR support as unresolved—not supported.

## Compatibility tiers

| Tier | Meaning | Permitted claim |
|---|---|---|
| `vanilla_baseline` | Base texture is readable without a shader pack | `baseline_only` |
| `common_shader_safe` | Neutral textures avoid common double-lighting and bloom problems; no named pack is proven | `baseline_only` |
| `specified_shader_pack` | Exact Minecraft, loader, loader version, shader pack, pack version, preset, and evidence are locked | `named_targets_only` |
| `pbr_targeted` | A named shader target plus an exact PBR material standard/version and map convention are locked | `named_targets_only` |

Never claim compatibility with all shader packs. Shader packs may interpret light, bloom, normals, specular channels, transparency, and custom renderers differently. Public claims are baseline only or named targets only.

## Pre-concept design rules

- Paint a neutral albedo/base texture. Do not bake strong light direction, cast shadows, bloom halos, or environment color into it.
- Avoid painted-in directional highlights and deep directional shadows; these cause double lighting when runtime illumination is added. Small material-defining edge accents and recess value separation are allowed when they remain neutral.
- Keep visual emissive data in a separate mask or exact target-standard channel. Retain a readable non-emissive base beneath it.
- Treat actual world light as runtime behavior with a named owner. A texture or Blockbench preview cannot implement or prove it.
- Choose opaque/cutout where possible. Translucent or mixed materials require a declared render layer, overlap/sorting test, and gameplay-distance inspection.
- Do not generate normal/specular/roughness/metalness maps until the target standard and version are locked. Map filenames and channels follow that exact standard.
- Concept sheets show buildable geometry and neutral textures. Any runtime lighting sheet is supplementary, named by target, and never replaces the neutral Blockbench-faithful sheet.

## `shader-contract.json`

After concept approval and before detailed texturing, save an identity-scoped contract beside `model-spec.json`, then run `scripts/validate_shader_contract.py`. Minimum structure:

```json
{
  "schema_version": 1,
  "project_id": "energy_defense",
  "asset_id": "crystal_tower",
  "asset_version": "1.2.0",
  "edition": "java",
  "compatibility_tier": "specified_shader_pack",
  "support_claim": "named_targets_only",
  "baseline_required": true,
  "target_stack": {
    "minecraft_version_status": "locked",
    "minecraft_version": "exact project version",
    "shader_loader_status": "locked",
    "shader_loader": "iris",
    "shader_loader_version": "exact installed version",
    "shader_packs": [
      {"name": "exact name", "version": "exact version", "status": "locked", "source_url": "official URL", "checked_at": "YYYY-MM-DD"}
    ],
    "material_standard": "none",
    "material_standard_version": null
  },
  "materials": {
    "base_texture": "textures/crystal_tower.png",
    "emissive_mask": "textures/crystal_tower_emissive.png",
    "normal_map": null,
    "specular_map": null,
    "roughness_map": null,
    "metalness_map": null,
    "translucency": "cutout",
    "render_layer": "cutout",
    "painted_lighting_policy": "neutral_only"
  },
  "emissive": {
    "visual_emissive": true,
    "world_light": "runtime_block_light",
    "world_light_runtime_owner": "authorized Mod block-entity light controller",
    "bloom_dependency": "optional"
  },
  "fallback": {
    "no_shader_supported": true,
    "missing_optional_maps": "base_texture_only",
    "fallback_verified": false
  },
  "test_matrix": [],
  "qualification_status": "unverified"
}
```

`qualification_status` starts as `unverified`. Static validation proves that the contract is complete; it does not prove the visual result.

## Stable runtime test matrix

Every contract contains required rows with `case_id`, `required`, `status`, and `evidence`. Preserve these IDs:

| `case_id` | When required | Check |
|---|---|---|
| `no_shader_daylight` | always | Vanilla/no-shader readability, material separation, no painted shadow conflict |
| `no_shader_dark` | always | Silhouette and identity anchors in dark/cave conditions |
| `side_lighting` | always | Front/side/back response, no double lighting, inverted faces, or light leaks |
| `target_shader_daylight` | named shader/PBR target | Exact loader/pack/version/preset in daylight |
| `target_shader_dark` | named shader/PBR target | Exact target at night/cave and high-contrast lighting |
| `emissive_dark` | visual emissive enabled | Mask alignment, readable base, no full-body fullbright accident |
| `bloom_stress` | bloom optional/required | Low/default/high bloom or nearest available presets; no clipping/halo takeover |
| `transparency_overlap` | translucent/mixed | Overlap ordering, halos, depth sorting, water/particles, front/back view |

Also inspect Nether/high-saturation light, close range, expected gameplay distance, moving animation frames, damage states, and project reload when applicable. Reject crushed blacks, blown emissive whites, double lighting, inverted normal response, noisy metallic/specular response, transparency halos or sorting errors, Z-fighting, culling, light leaks, or a model that visually detaches from the Minecraft world.

Each passed named-target row records exact Minecraft/loader/shader-pack versions and preset, GPU/render settings when relevant, model and texture hashes, timestamp, tester, steps, expected/actual result, and contained screenshots or video with SHA-256. Blockbench screenshots are useful design evidence, but runtime lighting is not proof until tested in the game.

## Release and change rules

- Any change to base texture, emissive/PBR map, UV, render layer, renderer, loader, shader pack, shader preset, or Minecraft version invalidates affected evidence.
- `compatible` means the contract and static checks pass while real-game rows remain incomplete. `verified` requires all applicable rows passed with evidence and the no-shader fallback verified.
- A named target may be advertised only at its proven version/preset. Unlisted packs remain unverified.
- If the user later supplies a Mod, reconcile the contract against the inspected project before copying assets. If the actual render path differs, stop and produce an impact report.

## Primary technical references

Verify current behavior against primary sources at execution time rather than freezing versions in this Skill:

- Iris shader format documentation: https://shaders.properties/current/reference/overview/
- Iris project compatibility boundary: https://github.com/IrisShaders/Iris
- OptiFine shader documentation: https://github.com/sp614x/optifine/blob/master/OptiFineDoc/doc/shaders.txt
- shaderLABS LabPBR material standard: https://shaderlabs.org/wiki/LabPBR_Material_Standard
- Fabric item-model lighting fields where applicable: https://docs.fabricmc.net/develop/items/item-models
