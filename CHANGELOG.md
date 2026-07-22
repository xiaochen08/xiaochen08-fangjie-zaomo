# 更新日志

本项目使用语义化版本号：

- 主版本：工作方式或兼容范围发生重大变化；
- 次版本：加入新的完整能力或生产门槛；
- 修订版本：修复错误、补充校验或改善文字。

## 5.2.0 - 2026-07-22

### 战斗导演与原创动作编排

- 动画工坊新增 `combat-behavior-system.json` 合同，把单条动作升级为可验证的战斗行为系统。
- 支持武器姿态、目标距离、相对高度、冷却和 Boss 阶段筛选，以及权重、防连续重复、命中/落空、硬直打断和退出清理。
- 主技能新增战斗运行时接入合同，明确服务端伤害判定、客户端表现、网络同步和状态所有权；动画文件本身不冒充游戏逻辑。
- 新增 `validate_combat_behavior.py`，阻止不存在的动作、循环攻击、无限硬直、无清理中断和不完整分支进入发布流程。
- 编排方法借鉴高观赏性 Minecraft 动画的一般规律，但禁止复制“烦人的村民”、Epic Fight、WOM 或其他第三方作品的动画资产、关键帧与专有内容。

### 原创标准 Boss 验证样例

- 新增 [`examples/standard-humanoid-boss-combat`](examples/standard-humanoid-boss-combat/README.md)，使用原创双手大剑人形 Boss `Iron Vanguard` 验证完整编排链路。
- 固定种子运行 2000 次决策模拟，覆盖近、中、远距离动作、两个 Boss 阶段、命中/落空、打断和冷却回退。
- 模拟报告明确标记 `runtime_verified: false`：它验证合同和状态逻辑，不代替 Blockbench、Blender、Epic Fight 或 Minecraft 游戏内实测。

### 发行与验证

- 套件版本统一提升至 v5.2.0，并发布四个独立 WorkBuddy 导入包。
- 仓库布局测试从旧版三技能假设升级为四技能原子安装检查。
- 主控 291 项、模型工坊 16 项、纹理工坊 25 项、动画工坊 48 项、仓库布局 4 项、Boss 样例 7 项，共 391 项自动化测试。

## 5.1.0 - 2026-07-22

### Blender 与 Epic Fight 动画后端

- 动画工坊内部新增 Blender 高表现路线和 Epic Fight 接入合同，不再把 Blockbench 作为所有动作的唯一生产工具。
- 增加骨架重定向、单位和坐标系、Root Motion、关键事件、导出边界和真实运行时验证要求。
- 用户仍只面对一个 `$fjzm-animation` 调用名；后端选择属于动画工坊内部路由，避免再安装一堆零散技能。

## 5.0.0 - 2026-07-22

### 模型工坊与 ContractFlow v1

- 新增独立 `$fjzm-model`，把灰盒、几何、基础骨架和八视图还原证据从主技能中剥离。
- 套件从三个 Skill 扩展为主控、模型、纹理、动画四个 Skill，并要求成套安装。
- 新增 ContractFlow v1：主控是唯一调度者，三个专业工坊只能接收主控合同并返回结果，不能互相越权调用。
- 每次交接锁定项目、资产、版本、模型哈希、骨架签名、批准范围、依赖和写入权限，降低串模型与覆盖文件风险。
- 增加自动修复上限、八视图叠图、差异阈值和真实 Blockbench 检查点，不能仅凭 JSON 声称高还原。

## 4.2.0 - 2026-07-20

### 连续生图项目制

- 多资产范围必须先创建全资产总览，明确主模型、相关资产、GUI、投射物、掉落物、损毁状态和比例关系。
- 之后按主模型 A/B/C、主题锁定、单资产细化、完整视图、动作关键帧、GUI A/B/C 和单屏状态逐轮审批。
- 完整模型参考必须包含正、背、左、右、顶、底和三分之四视图；每个批准动画拥有独立关键帧图。
- 模型图、GUI 图、动作图、损毁图和特效图不得混成一张低可读性图片。

### 跨对话留档

- 新增 `references/image-production-system.md`。
- 每轮保存提示词、负面提示词、清单、图片、审查、用户修改、批准证据和 SHA-256。
- 新增 `design/image-production-index.json` 状态机，支持跨对话继续最高优先级的未完成轮次。
- 旧图片只能标记 `superseded`，不能覆盖或删除。
- 新增 `scripts/validate_image_production_index.py` 与自动化测试。

### Mod 资产展示系统

- 新增 `references/asset-presentation.md`。
- 每个玩家可见资产必须提供资产名、灰色斜体 Mod 名、使用说明和主题彩蛋文本。
- 支持 `themed serious`、`light chuunibyou`、`full chuunibyou` 三档文案风格。
- 每个资产维护 4–8 条已批准文案，并使用稳定随机规则，禁止每帧或每次刷新跳字。
- 所有正式文本使用本地化键和运行时渲染，禁止把最终中文硬编码到模型或 GUI 贴图。
- 新增 `scripts/validate_asset_presentation.py` 与自动化测试。

### 验证与发行

- 主技能 265 项、动画技能 18 项、纹理技能 21 项，共 304 项测试通过。
- 发布三个 Skill、Windows 安装器、插件清单和 WorkBuddy 内层包组成的 `fjzm-suite-v4.2.0.zip`。

## 4.1.0 - 2026-07-20

- 创建 Mod 路线把 Minecraft 版本提升为第一问题。
- Java 使用最低门槛加高版本验证策略，不强制卸载或降级已安装的新 JDK。
- 新增 Windows UTF-8 主机和项目双重红色门禁，避免后期中文乱码返工。
- 用户只需提供盘符，系统自动创建 `X:\FJZM-Projects\<project_id>` 统一工程目录。
- GUI 必须先生成三套 Minecraft 风格主题并单独审批。
- 所有 Mod、模型、GUI、贴图、动画、音效、粒子、合同和证据统一归档。

## 4.0.0 - 2026-07-20

- 新增独立纹理专修 Skill `$fjzm-texture`，套件从两个 Skill 扩展为三个。
- UV、像素贴图、材质层次、眼睛和参考图还原由纹理工坊单独负责。
- 使用 `texture-handoff.json` 与 `texture-result.json` 锁定模型、几何、UV、参考图和光影合同，防止贴图返修误改骨骼或模型。

## 3.0.0 - 2026-07-20

### 新增动画专修 Skill

- 新增 `fjzm-animation`，正式调用名为 `$fjzm-animation`。
- 主 Skill `$fjzm` 继续负责需求、概念审批、模型身份、材质、光影、粒子、音效、Mod 接入和最终发布。
- 动画工坊负责骨骼绑定、动画生产、实际 Blockbench 预览、问题诊断和动画返修。
- 支持 `delegated production`、`standalone revision` 和经过主流程批准的 `delegated_rig_and_animation` 三种工作模式。

### 防串模型与防误改合同

- 新增 `animation-handoff.json`，强制锁定 `project_id`、`asset_id`、`asset_version`、`model_sha256`、`model_spec_sha256` 和 `rig_signature`。
- 新增 `validate_animation_handoff.py`，自动检查路径越界、哈希不一致、目标模型错误、未授权改动、写入者冲突和审批缺失。
- 原始 `.bbmodel` 只读；每次动画修改都输出新版本，禁止覆盖源模型。
- 同一版本只能有一个动画写入者，避免主 Skill、子 Skill 或多个 Blockbench 会话互相覆盖。
- standalone 返修禁止修改几何、UV、纹理、骨骼名称、层级、定位器和骨骼拓扑。

### 主从交接与事件顺序

- 动画工坊必须返回 `animation-result.json`，记录输入/输出哈希、骨骼签名变化、修改过的动画和事件、验证证据及重绑要求。
- 返回结果前，主 Skill 禁止把变化后的骨骼绑定到粒子、音效、碰撞、能量弹或 Mod 控制器。
- 如果需要几何或骨骼拓扑变化，必须回到 `$fjzm` 重新取得用户批准并重建交接合同。

### 成套发行

- 新增 `.codex-plugin/plugin.json`，插件一次发现 `$fjzm` 和 `$fjzm-animation`。
- GitHub 正式源位于 `skills/fjzm` 与 `skills/fjzm-animation`。
- 新增 `Install-FJZMSuite.ps1`，Windows 下同时安装或同时更新两个 Skill；检测到半套安装会拒绝继续。
- 新增单一离线发行包 `fjzm-suite-v3.0.0.zip`，其中包含两个 Skill、插件清单、安装器和分别可导入的 WorkBuddy 子 ZIP。

### 升级影响

这是工作流架构变化，因此升级主版本到 3.0.0。旧 `$fjzm` 仍可识别，但正式动画生产必须同时安装 `$fjzm-animation`。

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
