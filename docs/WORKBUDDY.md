# WorkBuddy 导入说明

[`fjzm-suite-v5.2.0.zip`](../dist/fjzm-suite-v5.2.0.zip) 是完整下载包，里面已经同时带上四个 WorkBuddy 导入文件：

1. `workbuddy/fjzm-workbuddy-v5.2.0.zip`
2. `workbuddy/fjzm-model-workbuddy-v5.2.0.zip`
3. `workbuddy/fjzm-texture-workbuddy-v5.2.0.zip`
4. `workbuddy/fjzm-animation-workbuddy-v5.2.0.zip`

请在 WorkBuddy 的“导入技能”窗口依次拖入这四个 ZIP。每个子 ZIP 的根目录都直接包含 `SKILL.md`，符合单技能导入结构。

为什么不是把外层套件 ZIP 直接拖进去？因为 WorkBuddy 当前导入窗口按“一个 ZIP 根目录对应一个 `SKILL.md`”识别。外层 ZIP 的作用是保证四个 Skill 一起下载；四个内层 ZIP 的作用是让 WorkBuddy 分别登记四个调用名。没有经过平台验证前，本项目不会声称外层多 Skill ZIP 可以一次自动注册四个入口。

导入后确认技能列表同时出现：

- 方界造模，调用名 `$fjzm`
- 方界造模·模型工坊，调用名 `$fjzm-model`
- 方界造模·纹理工坊，调用名 `$fjzm-texture`
- 方界造模·动画工坊，调用名 `$fjzm-animation`

如果缺少任意一个，补导入对应 ZIP。主 Skill 会在几何、纹理或动画任务中检查对应工坊是否可用，缺失时停止对应专业生产。
