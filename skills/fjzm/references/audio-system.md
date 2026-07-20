# Audio intake and model-linking system

## Contents

- Runtime boundary and independent approvals
- Conversation attachment intake and mapping
- Inspection, quality, conversion, and naming
- Trigger ownership, loops, accessibility, provenance, and budgets
- Manifest, validation, re-approval, and delivery

## Runtime boundary

Blockbench keyframes schedule sound events; they do not register or play mod audio by themselves. The selected Minecraft runtime registers resources, owns state, starts/stops loops, and synchronizes gameplay.

Use this system whenever sound effects, music, voice, generated audio, or audio files are attached or implied. Read `audio-runtime-adapters.md` before implementation.

## Independent approvals

Model concept approval and audio mapping approval are independent gates. Changing audio alone does not revoke model approval. Changing geometry alone does not approve audio. Audio-file replacement, event meaning, timing, rig, or event ownership changes require audio re-approval; harmless metadata corrections do not.

Do not delay concept previews merely because optional audio is unassigned. Do not process or bind attachments until their audio mapping is approved.

Before intake, apply `asset-identity.md`: show the target model header and lock `project_id`, `asset_id`, `asset_version`, model specification hash, and rig signature. Every mapping repeats that `asset_id`; never transfer mappings through the active Blockbench tab or most recent model.

## Primary intake: conversation attachments

Tell the user to drag audio files into the conversation attachment area. Accept WAV, MP3, or OGG source files. Do not require English filenames.

Accept:

- Chinese filenames such as `炮塔启动.wav` or `能量弹命中.wav`;
- number-only filenames such as `01.wav`, `2.mp3`, or `003.ogg`;
- mixed names such as `01_蓄能.wav`;
- the user's Chinese description or numbered list assigning meanings.

Do not ask the user to translate or rename files. Convert the meaning into a stable English event ID yourself. Preserve the Chinese label and original filename in the manifest. If an attachment cannot be inspected, request reattachment; never invent its content.

## Bulk intake states

Inventory every attachment before asking for assignments. Show concise statuses:

| State | Display | Action |
|---|---|---|
| Assigned | `01.wav -> 炮塔启动` | Propose English ID |
| missing number | `02 -> 未收到文件` | Ask only if referenced by the user |
| duplicate filename | `01.wav (attachment 1/2)` | Disambiguate by attachment order and hash |
| unassigned | `03.wav -> 未确定` | Preview/inspect; request meaning |
| random variants | `04A/04B -> 发射音效 variants` | Map to one event with multiple resources |

For ambiguous numbers, preview or inspect each file. Do not guess numbered-file meanings. When the user edits an approved table, confirm only the changed rows unless the change alters shared timing, ownership, or variants. Never infer meaning from sequence alone.

## Attachment inventory

Record for every file:

- original source file, attachment order, size, format, duration, channels, sample rate, `source_sha256`;
- Chinese label, English event ID, variant group, role, critical-cue flag;
- animation/state, trigger time or condition, one playback owner;
- locator, volume, pitch, attenuation, start/stop, interruption, retrigger, and distance behavior;
- target edition, Minecraft version, loader, animation runtime, asset type, and output format;
- provenance, license, subtitle, visual telegraph, and performance budget.

Use `scripts/audio_pipeline.py inspect` for deterministic inspection. WAV receives waveform metrics without external dependencies. MP3/OGG metadata requires existing FFprobe. Never install dependencies automatically.

## Mapping approval gate

Present the target model identity header, then this table before processing:

| Source file | Chinese meaning | English event ID | Animation/state | Trigger/owner |
|---|---|---|---|---|
| `01.wav` | 炮塔启动 | `mymod:crystal_tower.activate` | `startup` | 0.00 s / animation |
| `蓄能.wav` | 水晶蓄能 | `mymod:crystal_tower.charge` | `attack` | 0.35 s / animation |
| `命中.wav` | 能量弹命中 | `mymod:crystal_tower.projectile_impact` | projectile | collision |

Wait for explicit user approval of the mapping. Never rename, overwrite, convert, copy, or bind the original attachment before approval. Corrections update the table and follow the independent re-approval rules.

## English identifier rules

- Use lowercase ASCII `namespace:asset.action` identifiers.
- Allow `a-z`, `0-9`, `_`, `-`, `.`, plus one namespace separator.
- Name by function: `crystal_tower.fire`, not `audio_01`.
- Map random variants such as `fire_01.ogg` and `fire_02.ogg` to one event.
- Preserve source name, attachment order, and hash for traceability.

## Processing and quality gates

Run conversion only after approval:

```powershell
python -X utf8 scripts/audio_pipeline.py inspect '.\炮塔启动.wav' --json-out '.\audio-inspection.json'
python -X utf8 scripts/audio_pipeline.py process-wav '.\炮塔启动.wav' '.\work\crystal_tower\activate_processed.wav' --approved --trim-threshold-dbfs -60 --fade-ms 5 --target-peak-dbfs -1
python -X utf8 scripts/audio_pipeline.py loop-seam '.\work\crystal_tower\idle_loop_processed.wav' --window-ms 10
python -X utf8 scripts/audio_pipeline.py convert '.\work\crystal_tower\activate_processed.wav' '.\sounds\crystal_tower\activate.ogg' --approved
```

The deterministic DSP command supports 16-bit PCM WAV, refuses existing destinations, trims/fades/normalizes only an approved copy, and verifies the source hash. Conversion uses argument lists rather than shell command strings. Positional effects default to mono OGG; music/UI audio may remain stereo when justified.

Use these quantitative review defaults: peak at or below -1 dBFS after approved processing; attack/release leading silence under 20 ms unless anticipation is intentional; related variants should remain within 3 dB perceived level; no clipped samples or accidental DC/clicks; a loop seam must be inaudible at normal volume and survive ten repetitions. These are starting gates, not platform mandates. Compare short SFX by family and gameplay context rather than relying only on integrated LUFS.

Never normalize, trim, fade, denoise, pitch-shift, or loop-edit an original attachment. Work on a versioned copy and document every operation.

## Trigger ownership and lifecycle

Assign one playback owner:

- `animation_keyframe`: footsteps, mechanical contacts, startup accents, release, recoil;
- `state_lifecycle`: idle/active/cooldown loops with entry, exit, unload, death, range, and interruption cleanup;
- `gameplay_event`: target acquisition, damage, death, interaction, server-authoritative actions;
- `projectile_collision`: impact at the actual collision position, not a fixed animation timestamp.

Launch may coincide with an attack keyframe. A projectile impact belongs to the collision event, not a fixed animation timestamp. Damage and projectile creation remain server-authoritative. Do not also play the same event from a network callback and keyframe. A loop requires `stop_event`, `interruption_rule`, maximum instances, and unload/destruction cleanup. Test chunk reload, rapid retrigger, target loss, stun, death, and multiplayer.

## Accessibility and readable combat

Every critical cue requires a localized `subtitle_key` and a non-audio `visual_telegraph`. Never make attack timing, danger, puzzle state, or interaction success audio-only. Verify subtitles name the source/action clearly and that visual timing matches the sound event.

## Provenance and licensing

For AI-generated audio record provider, `generation_model`, prompt, generation date, `license_status`, commercial-use decision, attribution requirement, and source URL/reference when available. For recorded or purchased audio, record creator/store, license, receipt/reference, and modification permission. Always record `source_sha256`. Mark unknown licensing as blocking for public or commercial release; do not imitate a named copyrighted game sound as an exact target.

## Performance budget

Record per asset or event family:

- `max_simultaneous_instances` and duplicate suppression window;
- `attenuation_distance`, category, priority, and low-LOD fallback;
- `streaming_policy`: short SFX in memory, long ambience/music streamed when the runtime supports it;
- loop count, variant count, file size, channel count, and maximum audible emitters.

Stress-test many nearby towers/entities. Reduce inaudible loops and far emitters before reducing critical attack cues.

## Required manifest

Save `audio-manifest.json`:

```json
{
  "schema_version": 1,
  "project_id": "energy_defense",
  "asset_id": "crystal_tower",
  "asset_version": "1.0.0",
  "model_binding": {
    "model_spec_path": "model-spec.json",
    "model_spec_sha256": "64 lowercase hex characters",
    "rig_signature": "rig-crystal-tower-v1"
  },
  "workflow": {
    "completed_steps": [
      "asset_identity_locked",
      "attachments_inventoried",
      "sources_inspected",
      "mapping_proposed",
      "mapping_approved",
      "copies_converted",
      "events_registered",
      "animation_bound"
    ]
  },
  "target": {
    "edition": "java",
    "loader": "fabric",
    "minecraft_version": "1.21.1",
    "animation_runtime": "geckolib5"
  },
  "model_approval_id": "concept-B",
  "audio_mapping_approval": {"status": "approved", "evidence": "verbatim user message"},
  "budgets": {
    "max_simultaneous_instances": 4,
    "attenuation_distance": 32,
    "streaming_policy": "memory"
  },
  "mappings": [{
    "asset_id": "crystal_tower",
    "source_file": "炮塔启动.wav",
    "source_sha256": "64 lowercase hex characters",
    "user_label_zh": "炮塔启动",
    "event_id": "mymod:crystal_tower.activate",
    "output_file": "sounds/crystal_tower/activate.ogg",
    "role": "one_shot",
    "owner": "animation_keyframe",
    "animation_id": "animation.crystal_tower.startup",
    "time_seconds": 0.0,
    "locator": "tower_core",
    "approved": true,
    "critical_cue": true,
    "subtitle_key": "subtitles.mymod.crystal_tower.activate",
    "visual_telegraph": "core lights cyan",
    "origin": "ai_generated",
    "provenance": {
      "provider": "provider",
      "generation_model": "model-version",
      "prompt": "saved prompt",
      "generated_at": "YYYY-MM-DD",
      "license_status": "commercial_use_verified",
      "attribution": "none"
    }
  }]
}
```

Run `scripts/validate_audio_manifest.py` with the project root and, when available, runtime sound registry, central animation event table, localization tables, visual-event table, and shared-library manifest:

```powershell
python -X utf8 scripts/validate_audio_manifest.py '.\audio-manifest.json' --project-root '.\' --sounds-json '.\sounds.json' --event-table '.\animation-events.json' --model-spec '.\model-spec.json' --localizations '.\localizations.json' --visual-events '.\visual-events.json' --shared-library '.\shared-audio-library.json'
```

The validator requires random variants in one group to share one event and remain within 3 dB RMS, checks critical cues in both `zh_cn` and `en_us`, confirms their visual events, and verifies shared-library consumer/event authorization. Fix all errors before claiming integration.

For a legacy manifest, dry-run `scripts/migrate_audio_manifest.py` first. Writing requires explicit `--write-dir` and always allocates a versioned filename; migration never fabricates conversion, registration, binding, or runtime evidence.

## Delivery

Deliver approved mapping evidence, untouched sources or references, inspection/DSP/loop reports, versioned OGG outputs, `audio-manifest.json`, registry/subtitle/controller files, event bindings, runtime adapter notes, and actual in-game evidence. Run `validate_asset_bundle.py` across the complete model bundle. If no mod/resource-pack project is authorized, deliver only the manifest and implementation plan; do not claim playback.
