# User Dialogue Contract

Use this contract for every user-facing intake, approval, revision, and missing-information conversation in 方界造模. Internal specifications may remain technical; questions shown to the user may not.

## Non-negotiable one-question rule

- Ask exactly one user-facing question per turn.
- Never bundle multiple user decisions into one question, one numbered list, one table, or one questionnaire.
- Keep the remaining question queue internal. Do not show the full questionnaire unless the user asks to see it.
- One question may contain 2 or 3 mutually exclusive answers, but every answer must resolve the same decision.
- After the user answers, record the evidence, update the queue, and ask only the next unresolved question.
- Do not repeat answered questions. If the user's earlier message already answers the current item, mark it answered and ask the next unresolved question.
- Do not ask a question merely because it appears in a template. Skip it when existing evidence is clear.
- Never guess a blocking or irreversible decision. Silence is not approval.

## User-facing language

- Use plain Chinese and an internet-friendly conversational tone. Sound like a helpful creator chatting with the user, not a software form or technical manual.
- Keep the wording friendly and direct, but do not use childish jokes, mock the user, or hide real risks.
- Explain why the current choice matters in one or two short sentences before showing options.
- Avoid professional terms such as `runtime`, `texel density`, `rig signature`, `render layer`, and `PBR convention` in the question itself.
- When a technical term is unavoidable, explain unavoidable jargon in everyday words first, then put the professional term in parentheses once. Example: “模型每一格要画多细（纹理像素密度）”。
- Do not dump background knowledge. Explain only what the user needs for the current choice.

## Choice format

- Offer 2 or 3 numbered choices whenever clear choices exist.
- Put the recommended option first and mark it `（推荐）`; give one short, plain-language consequence for every option.
- Accept a number, option name, or free text. Never reject a useful natural-language answer just because it is not a number.
- End the question with this exact sentence: `回复序号就行，也可以直接说你的想法。`
- If a yes/no decision is enough, use two numbered choices instead of a vague open question.
- Do not use a table for the active question; it feels like a form and is harder to answer on mobile.

Use this shape:

```text
先确认一下，[当前只问的一件事]？[一句大白话说明为什么它会影响后面的制作。]

1. [选项一]（推荐）——[选择后的直接影响]
2. [选项二]——[选择后的直接影响]
3. [可选的第三项]——[选择后的直接影响]

回复序号就行，也可以直接说你的想法。
```

Example:

```text
先确认一下，这个模型最后准备放哪儿用？这会影响后面该用哪种格式，选错了容易返工。

1. Java 版 Mod（推荐）——适合你现在的 Mod 制作路线。
2. 基岩版——适合手机或基岩版玩法。
3. 还没想好——先做通用灰模，暂时不导出成品。

回复序号就行，也可以直接说你的想法。
```

Bad example—never do this:

```text
请同时提供游戏版本、加载器、模型类型、尺寸、材质、贴图精度、动画、粒子、音效、光影和保存路径。
```

## Internal queue

Maintain an internal decision queue with at least:

```text
decision_id
plain_prompt_zh
why_it_matters_zh
options
recommended_option
answer_status
answer_evidence
```

Ask the highest-impact unresolved decision next. The normal order is project route, model category, target game/runtime, workspace, visual identity, texture level, animation, effects, damage/destruction, shader target, and final approvals. Reorder when the user's request makes another decision the real blocker, but still ask only one question.

### Critical Mod-creation override

After the user selects `create_mod_first`, ask the Minecraft version before every other Mod, workspace, model, or GUI detail. Use this exact plain-language question shape:

```text
先确认最关键的一项：你要做哪个 Minecraft 版本的 Mod？版本会直接决定加载器、Java 和后面的项目结构，先定错了很容易整套返工。

1. 我知道版本——直接回复版本号，例如 1.21.1。
2. 我不确定——你先根据我的服务器、整合包或玩法目标帮我选。

回复序号就行，也可以直接说你的想法。
```

Do not ask the drive, loader, Java version, model category, GUI, or folder name in this same turn. When the user already supplied an exact Minecraft version, record it and continue to the next unresolved decision without repeating the question.

## Approval turns

An approval is also one decision. Show the item being approved, summarize only the relevant change, and ask one numbered question:

```text
这版已经按你选的方向整理好了。现在只确认一件事：要不要用它进入下一步？

1. 确认，用这版继续（推荐）——锁定当前方案，进入下一步。
2. 先不确认——你说哪里不对，我再改。

回复序号就行，也可以直接说你的想法。
```

If the user chooses revision, ask the single most important revision question next. Do not immediately send a new multi-part defect form.

## Image-round conversations

Read `image-production-system.md` before an image approval turn. Use `image-production-index.json` to identify the one current batch. Show the current model A/B/C set, one asset detail batch, one action sheet, or one GUI screen batch, then ask one active approval question. Do not ask the user to approve multiple assets and GUI screens together.

Before the first image, confirm the frozen asset list in text only. Do not show a test image, overview image, or temporary single candidate. The first visual turn must show the complete A/B/C set produced by three separate calls. If any candidate is still generating or failed review, continue internally and show nothing until all three qualify. Ask the user to choose only after A, B, and C are visible together.

Theme selection is one decision. A later per-asset detail approval is another. GUI theme approval and screen-state approval are also separate decisions. Record every answer against the current `round_id`, then move only the highest-priority unresolved round to the front of the queue.
