# 更新日志

本项目使用语义化版本号：

- 主版本：工作方式或兼容范围发生重大变化；
- 次版本：加入新的完整能力或生产门槛；
- 修订版本：修复错误、补充校验或改善文字。

## 2.0.0 - 2026-07-20

### 正式命名

- 正式中文名修改为“方界造模”。
- 品牌缩写统一为大写 `FJZM`。
- Skill 机器调用名由 `$create-blockbench-minecraft-models` 修改为 `$fjzm`。
- `agents/openai.yaml` 的界面显示名修改为“方界造模 FJZM”。
- `SKILL.md` 的正式标题修改为“方界造模（FJZM）”。

### 为什么调用名是小写

Skill 的内部名称只允许小写字母、数字和连字符，因此品牌可以写 `FJZM`，但对话调用必须写 `$fjzm`。直接把 YAML 名称写成大写 `FJZM` 会违反 Skill 格式规范，可能导致无法安装或无法识别。

### 升级影响

这是一次破坏性调用名变更，所以版本升级为 2.0.0。模型、动画、粒子、音效、光影兼容和 Mod 接入能力没有删除，但旧调用方式不再是正式入口。

重新安装：

```powershell
python -X utf8 "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo xiaochen08/MC-FJZM --path . --name fjzm
```

重启 Codex 后使用：

```text
$fjzm
```

## 1.2.0 - 2026-07-20

### 核心变化

- 新增完整的光影、照明、发光、PBR 与透明材质兼容系统。
- 把光影目标提前到生图之前，不再等模型和贴图完成后才问用户是否需要光影。
- 所有项目都必须保留无光影保底；目标未知时，只允许声明原版基础兼容。
- 禁止“支持全部光影包”这种无法验证的宣传，只允许 `baseline_only` 或经过证据验证的 `named_targets_only`。

### 前期问诊门槛

- 必须确认 Minecraft 版本、Iris/OptiFine 或其他加载器及其版本。
- 指定光影兼容必须锁定光影包准确名称、版本、官方来源、检查日期和预设。
- PBR 必须锁定材质标准及版本，不能猜测 LabPBR 或贴图通道。
- 分开确认视觉发光、Bloom 依赖和真正照亮周围环境的运行时实现。
- 透明/半透明材质必须确定渲染层、排序风险和保底方案。
- 同时记录目标硬件、观察距离、贴图与材质图数量、透明层和自定义渲染成本。

### 生图与材质规则

- `concept-prompt.md` 新增中性基础色约束。
- 禁止把固定方向的强高光、投影、环境色和泛光画进基础贴图，避免开启光影后出现“双重打光”。
- 发光遮罩与基础贴图分离；没有指定 PBR 标准前，不生成法线/高光/粗糙度/金属度图。
- 运行时光影效果只能作为补充展示，不能替代可在 Blockbench 还原的中性模型方案图。

### 新增合同与自动验证

- 新增 `references/shader-compatibility.md`。
- 新增身份隔离的 `shader-contract.json` 规范。
- 新增 `scripts/validate_shader_contract.py`，验证保底、目标版本、材质图、发光归属、透明层、测试矩阵和证据状态。
- `validate_asset_bundle.py` 会在模型声明需要光影合同后强制检查合同及其引用的贴图资源。
- 新增光影合同自动化测试，并把光影门槛纳入 Skill 行为测试。

### 游戏内测试矩阵

- 固定无光影白天、无光影暗处和侧光测试。
- 指定光影目标增加白天、暗处与版本/预设检查。
- 视觉发光增加暗处遮罩检查；Bloom 增加压力测试；半透明材质增加重叠与排序测试。
- 重点拦截死黑、过曝、双重打光、法线反向、PBR 噪点、透明光边、排序错误、Z-fighting、剔面和漏光。
- Blockbench 截图、概念图和静态脚本通过都不能单独证明游戏内光影兼容。

### 兼容性说明

这是一次新的生产门槛。旧模型可以继续使用，但只有补齐并验证 `shader-contract.json` 后，才能获得 v1.2.0 的光影兼容声明。已验证结果只适用于合同中写明的 Minecraft、加载器、光影包、版本和预设。

## 1.1.0 - 2026-07-20

### 核心变化

- 新增“模型优先运行时可落地门槛”，防止没有 Mod 时直接生产无法接入游戏的成品模型。
- 不再把“先模型”理解为无条件完成全部几何、骨骼、动画和平台导出。
- 按低、中、高三个等级判断运行时风险。
- 对 Boss、复杂动画实体、动态方块实体、炮塔、投射物、攻击/伤害、粒子音效、自定义渲染、损毁和多人同步资产，默认推荐 `create_mod_first`。
- 不对静态装饰、简单物品等低风险资产强制创建 Mod。

### 模型优先保护机制

- 用户选择 `model_first` 后，必须先说明资产在游戏里的身份和运行功能。
- 中高风险资产若拒绝先创建 Mod，必须记录用户的明确拒绝和风险接受证据。
- 新增四级生产上限：`concept_only`、`graybox_only`、`runtime_neutral_source`、`platform_export`。
- 关键渲染路径或动画运行时未确定时，最多只能做到概念或灰盒。
- `runtime_deferred` 状态禁止平台专用导出、已验证声明和“游戏可用”宣传。

### 新增合同与接入流程

- 新增 `references/model-first-runtime-gate.md`。
- 新增 `runtime-contract.json` 规范。
- 新增稳定接口：`rig_signature`、`animation_ids`、`event_ids`、`locator_ids`、纹理 ID 和 `projectile_spawn`。
- 后续接入真实 Mod 时必须创建 `integration-map.json`，逐项映射模型资源、渲染器、实体/方块实体/投射物注册、动画状态、服务端事件、客户端粒子音效、网络同步、碰撞和存档行为。
- 实际项目版本与暂定目标不一致时，必须先生成迁移影响说明，不能偷偷重命名骨骼或重做动画。

### 自动验证

- 新增 `scripts/validate_runtime_contract.py`。
- `validate_mod_project_brief.py` 会阻止缺少运行时合同、风险确认或生产上限的模型优先任务。
- `validate_asset_bundle.py` 会要求模型优先资产包包含有效的 `runtime-contract.json`。
- 自动化测试由 172 项增加到 186 项。

### 行为变化

这是一次有意的安全收紧：旧版允许模型优先路线直接完成全部 Blockbench 生产；v1.1.0 改为只能做到经过验证的生产上限。这样会多一次前期确认，但能显著减少后期无法接入 Mod 的废弃资产。

### 升级方法

重新安装仓库中的 Skill，然后重启 Codex：

```powershell
python -X utf8 "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo xiaochen08/MC-FJZM --path . --name fjzm
```

## 1.0.0 - 2026-07-19

- 首次公开发布完整 Skill 本体。
- 提供需求问诊、三方案确认、Blockbench 建模、纹理精度、动画、粒子、音效、资产隔离、Java Mod 路线和发布验证流程。
- 发布 `SKILL.md`、代理配置、参考规范、验证脚本和自动化测试。
