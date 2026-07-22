# Iron Vanguard：标准人形 Boss 战斗编排实测

这是 FJZM v5.2.0 的原创技术样例，用来验证动画工坊与主技能之间的战斗合同，不是第三方动画复刻，也不是已完成的 Minecraft 游戏内 Boss。

## 动作设计

测试角色使用双手大剑人形姿态，动作思路强调“脚底发力 → 重心移动 → 髋部带动躯干 → 肩膀与武器延迟跟随 → 命中后顺势收招”：

- `close_combo_a`：左斩起手、右斩续压、下劈收尾；命中可以继续，打空进入恢复。
- `close_spin_finisher`：二阶段近距离回旋终结，用更长冷却换取范围压制。
- `mid_gap_close`：中距离踏步追击，不允许隔着远距离直接播放近战动作。
- `far_leap`：二阶段远距离跃击，带落地事件和明确恢复。
- `guard`：目标无效、超出高度、视线丢失或招式冷却时的安全回退。

所有动作 ID、连招顺序、速度、权重和节奏均为本样例原创。只借鉴公开项目里“武器动作池、条件筛选、加权连段、可打断和事件协同”的通用工程思想。

## 已验证内容

- 合同、动作库、事件表的模型身份与骨架签名一致。
- 两个 Boss 阶段完整覆盖 0–100% 血量。
- 近、中、远距离和相对高度会筛掉不合适的招式。
- 无视线时回退到防御动作。
- 同一实体和战斗轮次会得到可复现的加权选择。
- 最近使用的连段会受到重复惩罚。
- 所有步骤同时具备命中和落空分支。
- 受击、眩晕、击倒、丢失目标、阶段变化、死亡和卸载均有清理事件。
- 2000 次决策模拟覆盖全部四组连段，没有连续重复攻击系列。

模拟中有 1718 次进入防御回退，这是因为样例把每个循环都当作一次决策，而攻击仍处于 18–48 tick 的冷却。它证明系统不会为了“看起来一直在打”而绕过冷却；真实 Mod 通常只在攻击准备完成时请求下一次攻击决策。

## 尚未验证内容

当前状态是 `contract_simulated`，不是 `runtime_verified`：

- 没有生成或播放 `.blend` / `.bbmodel` 动作曲线；
- 没有进入 Blender、Blockbench 或 Minecraft；
- 没有验证 Epic Fight 动作注册、真实碰撞箱、伤害、粒子、音效、多人同步和存档重载；
- 因此不能把本例宣传成“游戏内 Boss 已完成”。

等目标 Minecraft、加载器和 Epic Fight 版本确定后，才能继续生成对应动作并做真实游戏验证。

## 运行

先验证合同：

```powershell
python -X utf8 ..\..\skills\fjzm-animation\scripts\validate_combat_behavior.py `
  .\contracts\combat-behavior-system.json `
  --action-library .\contracts\action-library.json `
  --events .\contracts\animation-events.json
```

运行单元测试：

```powershell
python -X utf8 -m unittest discover -s .\tests -p "test_*.py" -v
```

重新生成一份不覆盖旧证据的报告时，请换一个新文件名：

```powershell
python -X utf8 .\scripts\simulate_combat_director.py `
  .\contracts\combat-behavior-system.json `
  --cycles 2000 `
  --output .\evidence\simulation-report-v2.json
```

正式证据见 [simulation-report.json](evidence/simulation-report.json)。
