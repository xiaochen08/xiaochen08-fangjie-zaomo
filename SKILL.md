---
name: fjzm
description: "Use when users ask for 方界造模 or FJZM, or when creating, revising, texturing, animating, sonifying, exporting, or validating Minecraft Blockbench .bbmodel assets: entities, weapons, items, machines, furniture, structures, vehicles, or environments."
---

# 方界造模（FJZM）

## Category routing

Read [asset-identity.md](references/asset-identity.md); lock the target asset before creating or binding files. Ask whether an authorized Minecraft project exists. If absent/unknown, Read [mod-project-bootstrap.md](references/mod-project-bootstrap.md). Require an explicit project route choice before the model category: `create_mod_first` or `model_first`. Do not auto-resolve this choice. Read [model-categories.md](references/model-categories.md). Start by asking which top-level model category. Show only the compact top-level menu; accept a number, name, or free-text description, then expand only the selected branch. If `model_first`, Read [model-first-runtime-gate.md](references/model-first-runtime-gate.md); classify runtime risk and lock the provisional production ceiling before images. Read [asset-workspace.md](references/asset-workspace.md) before concepts; ask drive/root and create one approved folder per model. Read [asset-ecosystem.md](references/asset-ecosystem.md); lock scope. Read [shader-compatibility.md](references/shader-compatibility.md) before concepts; lock the no-shader fallback and any named loader, shader-pack, PBR, emissive, transparency, and performance targets before image generation.

## Approval gate

For a new model without an approved anchor:

1. Ask use, runtime, scale, shape, materials, signature parts, motion, references, texture resolution and texel density in at most three grouped questions. Explain what low resolution loses and what high resolution costs. Assess whether high resolution is necessary. Recommendations state atlas dimensions, texels per Blockbench unit, tradeoffs, necessity rationale, and quality commitment. Use exactly: 64x64 minimum/1 texel per unit; 128x128 standard/1; 256x256 detailed/2; 512x512 ultra/4. Do not recommend below 64x64. Lock the shader-compatibility tier, no-shader fallback, exact named targets, PBR convention, emissive/world-light behavior, render layer, and evidence burden. If animation is requested or implied, Read [animation-system.md](references/animation-system.md) before concepts. If particles or runtime effects are requested or implied, Read [particle-design.md](references/particle-design.md). If sound is requested/implied or audio files are attached, Read [audio-system.md](references/audio-system.md); inventory and obtain mapping approval before processing/binding. Do not invoke imagegen until related-asset scope and damage/destruction scope are explicitly answered. Shader/lighting scope must also be explicitly answered.
2. Read [concept-prompt.md](references/concept-prompt.md) before invoking imagegen; compile its manifest. **REQUIRED SUB-SKILL:** use imagegen for three distinct Blockbench-feasible concept previews. Generate separately; label A/B/C outside images. Pause if unavailable.
3. Explain differences; invite revision.
4. Wait for explicit user approval naming the concept and authorizing model generation. Silence is not approval. Never auto-resolve this gate.
5. Do not open or control Blockbench before approval. Do not create a `.bbmodel`, final texture, rig, geometry, or animation before approval.

“Do it now”/“surprise me,” urgency, and references are not approval.

Bypass only for an already-approved design anchor plus explicit generation permission; redesigns require approval.

## Production workflow

1. Read [model-brief.md](references/model-brief.md); save an identity-scoped `model-spec.json`. Create `shader-contract.json`, run `scripts/validate_shader_contract.py`, and stop before detailed texturing when it is invalid. For `model_first`, create `runtime-contract.json`, run `scripts/validate_runtime_contract.py`, and obey its validated stage ceiling before detailed work.
2. Never reinterpret the approved concept.
3. Pass manifest-matched graybox → motion → detail → export.
4. Apply animation, particle, and approved audio contracts through the central event table.
5. Build clean groups, stable UUIDs, native textures, and correct origins.
6. Use [quality-gates.md](references/quality-gates.md), `scripts/validate_bbmodel.py`, and interpolated-frame tests; execute the applicable no-shader, named-shader, PBR, emissive, bloom, and transparency rows from `shader-contract.json` in the actual runtime.
7. For audio use `scripts/audio_pipeline.py`, `scripts/migrate_audio_manifest.py`, Read [audio-runtime-adapters.md](references/audio-runtime-adapters.md), then run `scripts/validate_audio_manifest.py`.
8. Run `scripts/validate_asset_bundle.py`; for multiple models Read [project-integration.md](references/project-integration.md) and run `scripts/validate_project_index.py`.
9. Use `scripts/inspect_runtime_project.py`; Read [runtime-delivery.md](references/runtime-delivery.md), run `scripts/scaffold_runtime_delivery.py` and `scripts/validate_release_evidence.py`, then Read [release-qualification.md](references/release-qualification.md).

## Quick reference

| State | Allowed action |
|---|---|
| Brief incomplete | Ask; create nothing |
| Brief complete, concept unapproved | Generate/iterate A/B/C images only |
| Audio mapping unapproved | Inventory and propose mappings only |
| Shader/lighting scope unresolved | Ask; concept generation is blocked |
| Concept approved, runtime contract missing/invalid | Stop before detailed production |
| Shader contract missing/invalid | Stop before detailed texturing and any compatibility claim |
| Model-first critical runtime fields unresolved | Concept or graybox only |
| Concept and runtime gate approved | Build only through the validated production ceiling |
