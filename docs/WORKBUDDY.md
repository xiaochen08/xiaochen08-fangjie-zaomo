# WorkBuddy 导入说明

`fjzm-suite-v3.0.0.zip` 是一个完整下载包，里面已经同时带上两个 WorkBuddy 导入文件：

1. `workbuddy/fjzm-workbuddy-v3.0.0.zip`
2. `workbuddy/fjzm-animation-workbuddy-v3.0.0.zip`

请在 WorkBuddy 的“导入技能”窗口依次拖入这两个 ZIP。每个子 ZIP 的根目录都直接包含 `SKILL.md`，符合单技能导入结构。

为什么不是把外层套件 ZIP 直接拖进去？因为 WorkBuddy 当前导入窗口按“一个 ZIP 根目录对应一个 `SKILL.md`”识别。外层 ZIP 的作用是保证两个 Skill 一起下载；两个内层 ZIP 的作用是让 WorkBuddy 分别登记两个调用名。没有经过平台验证前，本项目不会声称外层多 Skill ZIP 可以一次自动注册两个入口。

导入后确认技能列表同时出现：

- 方界造模，调用名 `$fjzm`
- 方界造模·动画工坊，调用名 `$fjzm-animation`

如果只出现一个，不要开始动画生产；补导入另一个。主 Skill 会在动画任务中检查子 Skill 是否可用，缺失时停止动画部分。
