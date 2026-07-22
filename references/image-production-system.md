# Persistent image production system

Use this system whenever concept approval needs more than one image, more than one asset, a GUI, damage states, or animation previews. Its core rule is: generate the right bounded batch, show it, record the decision, and resume from evidence instead of restarting or guessing.

## Production order

Finish a **text-only asset scope confirmation** before image generation. The confirmation names the primary asset, every approved companion, excluded suggestions, GUI scope, damage/destruction scope, relative scale, and required later sheets. Freeze it as a manifest and obtain the user's correction or confirmation in text. **Do not generate an asset-overview image.** Asset confirmation is not an image round and must not delay or replace the user's real visual choice.

The **first user-visible image batch** is the A/B/C choice batch. Invoke imagegen with **exactly three separate imagegen calls**:

1. `Variant A`: one complete, buildable direction based on the frozen scope.
2. `Variant B`: one equally complete, buildable direction based on the same scope.
3. `Variant C`: one equally complete, buildable direction based on the same scope.

Do not show a partial A/B/C batch. Never show Variant A early and describe it as a temporary preview, overview, test, or non-choice image. Finish all three calls, audit them, regenerate any failed candidate, and only then show A, B, and C together for one selection decision.

All three candidates use the **same quality floor**, same approved requirements, same texture tier, same feasibility rules, same camera/view contract, and comparable information density. **No sacrificial option** is allowed: do not make B or C intentionally ugly, incomplete, generic, lower resolution, lower effort, missing parts, or reduced detail merely to make another option win. A candidate must express a genuinely different silhouette, construction language, material arrangement, or theme logic—not merely a recolor. If one candidate fails, regenerate only the failed candidate before showing the batch; do not lower the other candidates to match it.

Use this order:

1. `asset_scope_confirmation`: text and manifest only; no generated preview image.
2. `concept_choice`: `round-001__concept-choice`, three separately generated A/B/C candidates shown together.
3. `theme_lock`: obtain explicit user selection or revision of one direction.
4. `asset_detail`: run per-asset detail rounds, one bounded asset or tightly coupled asset family at a time.
5. `model_views`: after shape and style stabilize, generate the complete build-reference view matrix.
6. `model_actions`: generate action/keyframe sheets for every approved animation or state transition.
7. `gui_theme`: independently generate GUI A/B/C theme previews; for a GUI-only job this is also the first image batch and follows the same three-call rule.
8. `gui_detail`: after GUI theme approval, run screen-specific GUI detail rounds and state sheets.
9. `final_visual_lock`: archive only explicitly approved outputs as production anchors.

Do not treat asset-scope confirmation, theme lock, model approval, GUI approval, texture approval, or action preview as approval for another gate. Theme lock establishes one shared art direction; it does not silently approve every asset.

## Complete model view contract

Every final model reference package must show:

- front;
- back;
- left side;
- right side;
- top;
- bottom;
- three-quarter;
- an action/keyframe sheet for every approved action, attack, transformation, damage stage, destruction route, or important transition.

Use orthographic projection for front, back, left side, right side, top, and bottom. Use a restrained fixed camera for three-quarter. Every view must depict the **exact same geometry, proportions, cube inventory, and texture**. Keep scale, ground line, part count, attachment state, material palette, and lighting consistent. Reject and regenerate any sheet with invented rear parts, changed limb length, mirrored asymmetry, missing attachments, hidden bottom geometry, or inconsistent texture markings.

An action/keyframe sheet is a visual animation plan, not proof that the clip runs in Blockbench or Minecraft. Runtime proof still requires the real model, rig, exported clip, and in-game evidence.

Do not combine model sheets and GUI screens in one image. A model view sheet, action sheet, GUI screen, GUI component/state sheet, effect sheet, and damage sheet each receive their own round entries and files. This preserves readable scale and prevents one image from hiding implementation gaps.

## One active decision per conversation turn

Keep the complete queue internal. Show only the current image batch and ask one active approval question. Examples:

- choose A, B, or C for the primary model;
- approve or revise the current asset;
- approve or revise the current GUI theme;
- choose the most important detail to change.

Do not ask the user to approve several assets and several GUI screens in one turn. If the user lists many changes at once, record all of them, apply them to the queue, and ask only the highest-impact unresolved decision next.

## Persistent project archive

Create this structure inside the approved unified project root:

```text
design/
  image-production-index.json
  asset-scope-confirmation.json
  image-rounds/
    round-001__concept-choice/
      prompt.md
      negative-prompt.md
      manifest.json
      variant-a/
        prompt.md
        images/
      variant-b/
        prompt.md
        images/
      variant-c/
        prompt.md
        images/
      images/
      review.json
      approval-evidence.txt
    round-002__asset__<asset_id>/
    round-003__gui__<screen_id>/
  approved-previews/
    approval-index.json
```

Every generated image, input reference, prompt, negative prompt, manifest, critique, user revision, approval evidence, and superseded result stays inside its numbered round. Calculate and record SHA-256 for every prompt, manifest, and image. Never overwrite, rename in place, delete, or reuse an earlier round file. A revision creates a new round or a new versioned file with a new hash. `superseded` means retained but no longer authoritative.

Use only these round states:

```text
queued | generated | shown | revision_requested | approved | superseded
```

`image-production-index.json` is the cross-conversation source of truth. Each entry records:

```json
{
  "round_id": "round-001",
  "round_type": "concept_choice",
  "project_id": "energy_defense",
  "asset_id": "crystal_tower",
  "screen_id": null,
  "status": "shown",
  "depends_on": [],
  "prompt_path": "design/image-rounds/round-001__concept-choice/prompt.md",
  "negative_prompt_path": "design/image-rounds/round-001__concept-choice/negative-prompt.md",
  "manifest_path": "design/image-rounds/round-001__concept-choice/manifest.json",
  "generation_mode": "separate_calls",
  "variant_calls": [
    {"variant": "A", "call_id": "call-a", "quality_status": "passed", "image_sha256": "..."},
    {"variant": "B", "call_id": "call-b", "quality_status": "passed", "image_sha256": "..."},
    {"variant": "C", "call_id": "call-c", "quality_status": "passed", "image_sha256": "..."}
  ],
  "image_sha256": ["...", "...", "..."],
  "approval_evidence": null,
  "next_round": "round-004"
}
```

At the start of a future conversation, read `image-production-index.json`, verify referenced files and hashes, restate the current project/asset header, and continue only the highest-priority unresolved round. Do not regenerate an approved or superseded round unless the user explicitly reopens it. If the index and files disagree, stop image production and repair traceability before continuing.

Run `scripts/validate_image_production_index.py` before resuming a later conversation, before copying an approved anchor, and before final delivery. A failing index blocks further generation because asset identity or approval history may be ambiguous.

## Prompt and review discipline

Compile `concept-prompt.md` for model rounds and `gui-design.md` for GUI rounds. Keep the approved theme token, palette, material language, texture tier, view contract, and asset identity in every later prompt. Never rely on the image model to remember a previous round; inject the approved image hashes and frozen manifest into the next prompt.

Before showing the first choice batch:

1. verify every requested asset or screen is present and no unapproved asset was invented;
2. verify the batch contains exactly A, B, and C from three separate calls;
3. verify the three candidates share the same quality floor and none is a recolor, reduced-detail filler, or deliberately weak option;
4. verify model cross-view consistency and Blockbench feasibility;
5. verify GUI scale, text-safe regions, states, and Minecraft style when applicable;
6. record visible defects and per-candidate quality status in `review.json`;
7. regenerate only the failed candidate before showing the batch when a blocking defect is obvious;
8. show A, B, and C in their recorded order, then ask one approval question.

Copy approved anchors to `design/approved-previews/` without removing their original round copies. The approval index points to both locations, hashes, manifest, exact user evidence, and superseded versions.
