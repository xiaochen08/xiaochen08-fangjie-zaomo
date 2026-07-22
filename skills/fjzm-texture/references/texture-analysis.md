# Reference decomposition and handoff

## Step 1: reference decomposition

Analyze the approved reference before generating pixels.

### Material library

For each material record:

- named model parts and UV regions;
- material type and visual scale;
- base color family;
- highlight and shadow families;
- a 3-5 color ramp with deliberate hue shift;
- intrinsic surface cues such as weave, grain, oxidation, fur clustering, skin warmth, or sharp metal response;
- allowed wear, noise, edge accents, local contact AO, emissive/PBR maps, and gameplay-distance priority.

Do not sample one bright and one dark pixel and call it a material. A ramp must describe how value and hue move through the material.

### Lighting separation

Record reference scene lighting direction, softness, exposure, cast shadows, rim light, environment tint, bloom, and ambient fill only to understand the picture. Separate these from intrinsic material cues.

Neutral albedo may contain local recess values, material-defining clusters, restrained non-directional wear, and local contact AO. Never bake directional scene light, cast shadows, studio floor bounce, bloom halos, or environment color into the base texture. These belong to Blockbench preview, Minecraft lighting, shader maps, or runtime effects; painting them twice creates double lighting.

### Feature anchors

Create an anchor table with:

```json
{
  "anchor_id": "eye_left_iris",
  "reference_region": "approved-cat.png#left-eye",
  "model_part": "head",
  "model_face": "north",
  "uv_region": [32, 16, 4, 4],
  "geometry_dependency": "satisfied | blocked",
  "requirements": ["blue iris", "dark pupil", "one-pixel catchlight"],
  "priority": "identity_critical"
}
```

If an eye, ear, muzzle, armor plate, buckle, bag, weapon, or silhouette feature has the wrong shape or location, mark `geometry_dependency: blocked` and return to `$fjzm`. Do not fake protrusions, depth, or missing parts with painted perspective.

## Handoff identity

`texture-handoff.json` uses ContractFlow v1 and routes only from `$fjzm`. It locks `project_id`, `asset_id`, `asset_version`, `model_sha256`, `model_spec_sha256`, `geometry_signature`, `rig_signature`, `uv_signature`, approved reference hashes, and `shader-contract.json` hash. The source is read-only and `$fjzm-texture` is the single writer for one versioned output. Geometry, base bones, origins, and locators are immutable; only `delegated_uv_and_texture` may replace the final UV contract.

The handoff also records allowed and protected mutations, both approvals, atlas, density, material library, UV plan, eye system, output paths, and return-contract path.
