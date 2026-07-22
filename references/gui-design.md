# Minecraft GUI concept and approval system

Use this when the Mod includes a screen, menu, HUD, inventory, machine panel, Boss bar, configuration screen, dialogue, quest page, spell book, or other player-facing interface.

## Approval gate

Do not implement GUI textures or code from a text description alone. Complete the one-question-at-a-time intake, then **REQUIRED SUB-SKILL: use imagegen** to create three distinct Minecraft-faithful GUI theme previews. Obtain explicit GUI approval independently from model approval. Silence or model approval is not GUI approval.

Follow `image-production-system.md`. Confirm which GUI screens belong to the Mod in the text-only asset-scope manifest; do not generate a GUI overview image. Generate GUI A/B/C as independent, separately called candidates after the shared visual theme is known. For a GUI-only job, its first image batch must directly be three separately generated GUI choices shown together. After the user selects a GUI theme, continue screen-specific detail and state rounds one screen at a time; preserve every round and resume from `design/image-production-index.json` in later conversations.

The three directions must be meaningfully different while supporting the same functions:

- `Theme A`: the safest readable direction, usually closest to the approved Mod and vanilla Minecraft visual language;
- `Theme B`: a richer material/theme interpretation with distinct frames, icons, states, and decorative hierarchy;
- `Theme C`: a bolder alternative with a different palette, silhouette, information hierarchy, or fantasy/technology language.

Do not produce three recolors of one layout.

## Intake and manifest

Ask one plain-language question per turn. Lock the screen purpose, target Minecraft/loader, target GUI scale, input methods, screen states, slot grid, buttons, tooltips, localization expansion, accessibility, and performance. Build a `screen-to-texture manifest` that maps every visible panel, slot, icon, label area, button state, progress bar, and tooltip to an implementable texture region or runtime widget.

When a screen displays a Mod asset, read `asset-presentation.md` and show the approved display name, gray italic Mod line, colored usage line, and flavor-text treatment in the GUI preview. Treat these as runtime text regions, not baked texture pixels. Validate every referenced `asset-presentation.json` before final GUI approval.

## Visual standard

Every preview must use Minecraft pixel-art language and remain implementable at the declared texture resolution. Use crisp nearest-neighbor pixels, a coherent themed palette, readable value hierarchy, restrained texture noise, real slot and button states, and a professional rich composition that matches the Mod theme.

Respect the target GUI scale, safe margins, slot grid, Minecraft font/localization behavior, mouse/keyboard/controller focus, and nine-slice or tiled panel strategy. Show normal, hover/focus, pressed, disabled, selected, progress, warning, and error states when applicable.

Use no web-dashboard styling, modern SaaS cards, browser navigation, glossy mobile-app gradients, photographic materials, arbitrary rounded rectangles, unreadably tiny text, or details impossible at the target atlas size.

## Image generation package

Generate each theme separately with exactly three imagegen calls at the same screen size, information content, and quality floor. Do not use a recolor, reduced-detail layout, or sacrificial option as filler. Audit all three and show them together. Each package includes:

1. full screen at the target aspect and GUI scale;
2. component/state sheet for panels, buttons, slots, icons, meters, tabs, and tooltips;
3. optional flow sheet when multiple screens or transitions are approved;
4. the manifest, atlas estimate, implementation risks, and what is runtime text rather than baked pixels.

After theme selection, generate later screen-specific GUI detail rounds for normal, hover/focus, pressed, disabled, selected, progress, warning, error, and tooltip states that apply. Do not combine these GUI sheets with model front/side/back/top/bottom sheets.

Label Theme A, Theme B, and Theme C outside the images. Audit every visible element against the manifest before showing it. Regenerate invented, inconsistent, unreadable, or non-Minecraft elements.

## Approval and archive

After the user selects or revises a theme, copy the approved GUI preview and approved model preview into the same unified project folder:

```text
design/approved-previews/
  model__<asset_id>__<variant>__v<version>.png
  gui__<screen_id>__<theme>__v<version>.png
  approval-index.json
```

`approval-index.json` records file hashes, project/asset/screen IDs, approval evidence, timestamp, manifest paths, and superseded versions. The shared folder does not merge model identity with GUI identity; prefixes and the index keep them traceable.

## Implementation evidence

Implement only the approved theme and manifest. Compare the finished runtime screen against the approved image at the same GUI scale. Capture an actual in-game screenshot for normal and interactive states; code compilation or an image alone is not runtime proof. Any layout, palette, icon, atlas, or state change that materially diverges from approval reopens the GUI gate.
