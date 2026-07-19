# 使用环境与专业注意事项

## 推荐环境

| 项目 | 最低建议 | 推荐 |
|---|---:|---:|
| 操作系统 | Windows 10 64 位 | Windows 11 64 位 |
| CPU | 4 核 | 6 核或以上 |
| 内存 | 8 GB | 16–32 GB |
| 显卡 | 支持 WebGL | 4 GB 以上独立显卡 |
| 可用空间 | 10 GB | 30 GB 以上 |
| 分辨率 | 1366×768 | 1920×1080 或更高 |

数值是工作流建议，不是 Blockbench 官方硬性要求。同时运行 Codex、Blockbench、Minecraft、IDE 和 Gradle 时建议至少 16 GB 内存。

## 必需软件

### Codex 桌面端

安装 `create-blockbench-minecraft-models` Skill，使用技术调用名启动。品牌显示名“方界造模”不替代技术调用名。

### Blockbench 桌面稳定版

正式生产优先使用桌面版。Web 版受浏览器权限影响，固定路径读取、写入、导出和纹理加载可能需要额外步骤。

- 项目中途不随意升级 Blockbench。
- 记录 Blockbench 和插件版本。
- 升级前备份 `.bbmodel`。
- 插件必须确认模型格式、平台和最低版本。

### Python

验证脚本建议使用 Python 3.11 或 3.12：

```powershell
python --version
```

中文文档和配置统一使用 UTF-8。

## Mod 开发环境

只制作模型时可以不安装 Java 和 IDE。需要接入 Java 版 Mod 时再准备：

- 与目标 Minecraft 和加载器匹配的 64 位 JDK
- Fabric、Forge、NeoForge、MCreator 或已确认的其他工具链
- IntelliJ IDEA、Eclipse 或配置完整的 VS Code
- 项目自带 Gradle Wrapper
- 可选 Git

不要使用一个“最新 JDK”构建所有 Minecraft 版本。先锁定 Minecraft、加载器和构建插件，再确认 JDK。

检查：

```powershell
java -version
```

构建：

```powershell
.\gradlew.bat build
```

优先使用项目自带 Wrapper，不擅自更换包管理器或全局 Gradle。

## 路径规范

模型资产根目录可以独立于 Mod 工程：

```text
D:\Minecraft-Blockbench-Models\energy_defense\crystal_tower__v1
```

Mod 工程建议使用英文、无空格、本地磁盘路径：

```text
D:\MinecraftProjects\crystal_tower_mod
```

避免：

- OneDrive 或其他同步目录
- `Program Files` 和系统保护目录
- 桌面、下载目录和移动盘临时目录
- 空格、Emoji 和复杂特殊字符的 Mod 工程路径
- “最终版”“最终版2”“真的最终版”等不可追踪名称

模型显示名可以使用中文；`asset_id`、`mod_id`、动画、粒子、音效事件、Java 包名和资源文件名建议使用英文小写命名空间。

## Blockbench 格式

开始前必须确认 Java Block/Item、Java Entity、Bedrock Entity、Generic、GeckoLib、OptiFine CEM 或自定义格式。格式会影响几何限制、UV、骨骼、动画、旋转和导出，不能制作完成后再决定。

## 概念图边界

概念图用于批准结构和视觉方向，不是 `.bbmodel` 完成证据。为了缩小差距：

- 只展示可实现的方块几何和简单旋转。
- 多视图保持部件数量、比例与位置一致。
- 不用景深、烟雾和强阴影隐藏结构。
- 区分模型纹理发光和运行时粒子光效。
- 不用电影级材质暗示游戏内必然实现相同光照。

## 纹理

高分辨率不等于高质量。需要同时控制纹素密度、UV 利用率、观看距离、同屏数量、发光遮罩和显存开销。

禁止简单放大低清纹理、相邻部件纹素密度不一致、用纯黑抹去黑铁层次，或把方向性阴影完全烘焙死。

## 动画与穿模

旋转部件必须记录父级、原点、轴、方向、半径、朝向、安全距离和是否自转。公转不是自转。

至少检查：

1. 开始帧
2. 加速阶段
3. 最大展开
4. 完整旋转周期
5. 攻击帧
6. 冷却等待
7. 减速归位
8. 最终待机

插值区间同样可能穿模，不能只检查关键帧。

## 粒子、音效与游戏逻辑

普通模型几何不负责真实伤害、目标选择、攻击冷却、碰撞、服务端判定、粒子和声音播放。这些通常需要资源包、动画控制器或 Mod 代码。

AI 音频建议保留生成平台、日期、提示词、许可证、原文件和哈希。关键攻击音效同时提供视觉预警，避免可访问性问题。

## 数据安全与版权

上传第三方图片、模型、纹理、音频、字体、Logo 或代码前，确认拥有使用权。参考风格不等于允许复制具体角色或游戏资产。

发布前检查：

- 模型和纹理权利
- 音频商业许可
- AI 平台输出条款
- 字体与 Logo 许可
- 插件和开源代码许可证
- 非官方项目声明

## 版本与备份

推荐阶段版本：

```text
v1_concept_approved
v2_geometry_complete
v3_texture_complete
v4_animation_complete
v5_runtime_tested
```

保留参考资料、批准记录、原始模型、纹理、音频、规格、导出物和验证报告。高风险修改前先建立备份或 Git 检查点。

## 环境记录模板

```text
操作系统：
Codex 版本：
方界造模版本：
Blockbench 版本：
模型格式：
Minecraft 版本：
Mod 加载器与版本：
JDK 版本：
Python 版本：
动画运行库：
Mod 项目路径：
模型资产根目录：
纹理分辨率：
目标发布平台：
```

## 责任边界

- 概念图生成成功不等于模型完成。
- 文件生成成功不等于 Blockbench 可以重新打开。
- 构建成功不等于游戏逻辑正确。
- 动画预览正常不等于整个插值过程无穿模。
- 没有实际游戏测试时不能宣称“完全兼容”或“已验证”。
