# Per-model Windows workspace

## Core invariant

Use one independent folder per model. Treat each independent `.bbmodel` as one asset even when it is a projectile, companion, variant, or replacement wreck model. Give every such asset its own `asset_id`, model specification, approvals, and sibling folder. Geometry, damage groups, and clips stored inside the same `.bbmodel` remain in that model's folder.

Never mix two asset_id values in one asset folder. Project-level indexes and explicitly approved shared libraries live above or beside asset folders, never inside one model's workspace.

## Drive and destination intake

Ask which Windows drive and parent folder to use before concepts. Do not choose a drive for the user. Accept a drive such as `D:` or an absolute root such as `D:\Minecraft-Blockbench-Models`; if only a drive is supplied, propose a clearly named root and wait.

Build and show the absolute proposed asset folder, for example:

```text
D:\Minecraft-Blockbench-Models\energy_defense\crystal_tower__v1
```

State the drive, approved root, project folder, asset folder, and whether the destination already exists. Wait for explicit path approval. A model-category choice, Mod-project destination, concept approval, delegated choice, or silence is not path approval.

## Safe creation

Create the dedicated folder after explicit path approval. Creating it only establishes storage; folder creation is not model-generation approval. Immediately before writing:

1. Resolve the approved root and destination; verify the resolved destination remains inside the approved root.
2. Require an unused destination. If it exists, do not overwrite, merge, or silently reuse it; propose a versioned sibling path and obtain approval again.
3. Use PowerShell 7 with literal paths and create only the approved directory:

```powershell
New-Item -ItemType Directory -LiteralPath 'D:\Minecraft-Blockbench-Models\energy_defense\crystal_tower__v1'
```

Do not scan or create across other drives. Do not use wildcard paths. Record the created absolute path and path approval evidence.

## Folder layout

Create these subfolders only inside the approved asset folder:

```text
consultation/  requirements, decisions, approval evidence
concepts/      A/B/C prompts, manifests, and generated previews
specs/         model-spec, animation, particle, and audio contracts
source/        editable .bbmodel after concept approval
textures/      texture atlases and emissive masks
animations/    exported animation/controller files
audio/         identity-scoped sources, processed files, and manifests
particles/     particle contracts and runtime files
previews/      Blockbench screenshots, GIFs, and keyframes
exports/       runtime model exports
evidence/      validator reports, hashes, and runtime evidence
```

Before concept approval, store only consultation and concept materials. Do not create `.bbmodel`, final textures, rigs, or animations before concept approval. After approval, keep every produced file within the declared asset folder except authorized Mod-project integration copies, which must retain source hashes and identity mappings.

## Multi-model rule

Create every approved related model in a sibling folder under the same approved project root. A separate projectile `.bbmodel`, summon, dropped item, trophy, or replacement wreck is a separate model folder. Never put one model's texture, audio, animation, export, or evidence into another model's folder. Validate the collection through `project-index.json` after each asset bundle passes independently.
