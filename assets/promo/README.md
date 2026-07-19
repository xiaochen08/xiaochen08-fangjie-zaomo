# 宣传图片上传指南

本目录由仓库所有者自行上传最终宣传图片。请使用下面的固定文件名，避免 README、平台文案和图片顺序失配。

## 文件清单

| 顺序 | 文件名 | 用途 | 推荐尺寸 |
|---:|---|---|---:|
| 00 | `P00-visual-anchor.png` | 内部视觉一致性基准，通常不公开展示 | 3840×2160 |
| 01 | `P01-official-hero.png` | GitHub README 与平台主封面 | 3840×2160 |
| 02 | `P02-approval-workflow.png` | 需求问诊与三案确认 | 3840×2160 |
| 03 | `P03-blockbench-demonstration.png` | Blockbench 直观建模演示 | 3840×2160 |
| 04 | `P04-animation-system.png` | 动画、冷却、归位与损毁系统 | 3840×2160 |
| 05 | `P05-full-system-integration.png` | 模型、粒子、音效与 Mod 联动 | 3840×2160 |
| 06 | `P06-asset-delivery.png` | 独立工作区与专业交付 | 3840×2160 |

## README 主视觉接入

上传 `P01-official-hero.png` 后，将根目录 `README.md` 中的主视觉占位文字替换为：

```markdown
![方界造模主视觉](assets/promo/P01-official-hero.png)
```

## 质量要求

- PNG、sRGB、16:9。
- 中文标题无错字、无多余字符。
- 六张正式图片使用同一座水晶塔。
- Blockbench 界面必须真实可信，禁止使用乱码软件界面冒充演示。
- 两块护盾保持同向公转、相隔 180°、不接触水晶且不穿模。
- 不包含 Minecraft、Blockbench 或其他品牌 Logo，除非拥有明确授权。
- 不包含生成平台水印、签名或来源不明素材。

## 上传后检查

1. 在 GitHub 文件页面确认图片可以打开。
2. 检查文件名大小写与本文完全一致。
3. 检查 README 相对路径。
4. 使用桌面端和手机端预览仓库首页。
5. 确认缩略图状态下标题和模型主体仍然清晰。
