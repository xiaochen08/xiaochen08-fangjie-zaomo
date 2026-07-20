# 更新日志

本项目使用语义化版本号：

- 主版本：工作方式或兼容范围发生重大变化；
- 次版本：加入新的完整能力或生产门槛；
- 修订版本：修复错误、补充校验或改善文字。

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
python -X utf8 "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo xiaochen08/MC-FJZM --path . --name create-blockbench-minecraft-models
```

## 1.0.0 - 2026-07-19

- 首次公开发布完整 Skill 本体。
- 提供需求问诊、三方案确认、Blockbench 建模、纹理精度、动画、粒子、音效、资产隔离、Java Mod 路线和发布验证流程。
- 发布 `SKILL.md`、代理配置、参考规范、验证脚本和自动化测试。
