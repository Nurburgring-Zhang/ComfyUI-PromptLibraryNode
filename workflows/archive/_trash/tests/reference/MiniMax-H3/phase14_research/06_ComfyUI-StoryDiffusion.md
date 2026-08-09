# Project: ComfyUI-StoryDiffusion

**URL:** https://github.com/zhou311113/ComfyUI-StoryDiffusion
**Author:** zhou311113 (移植自 HVision-NKU 原始论文)
**上游:** HVision-NKU/StoryDiffusion (南开大学 HVision 团队)
**License:** open source (具体查看 requirements.txt: spaces, peft, diffusers)
**类别:** ComfyUI 导演/编剧/故事生成 (方向 1)

---

## 项目简介

ComfyUI_StoryDiffusion 项目融合了 StoryDiffusion、MS-Diffusion、StoryMaker、Consistory、Kolor、Pulid、Flux、PhotoMaker、IP-Adapter 以及 InfiniteYou 等多个先进技术,旨在为用户提供一个强大的故事生成和编辑环境。

---

## 集成技术

| 技术 | 作用 |
|------|------|
| **StoryDiffusion** | 用于长距离图像和视频生成的自注意力机制 |
| **MS-Diffusion** | 基于控制图像生成的方法,可以实现两个角色在同一图像中的同框效果 |
| **StoryMaker** | 图像到故事生成的工具,可以自动生成与输入图像相关的故事 |
| **Kolor** | 基于深度学习的图像着色技术 |
| **Pulid-Flux** | 基于优化的图像生成方法 |
| **InfiniteYou** | 通过控制网络生成无限变化图像的技术 |
| **IP-Adapter** | 图像提示词适配器 |
| **PhotoMaker** | 风格化人像生成 |
| **Consistory** | 一致性故事生成 |
| **Flux** | 新的扩散模型架构 |

---

## 核心技术:StoryDiffusion 一致性自注意力算法

南开大学 HVision 团队研发,核心创新:

> 通过采用创新的一致性自注意力算法,StoryDiffusion 革命性地实现了在无需额外训练流程下,连续生成主题紧密相连、角色形象统一的高质量图像序列。

### 关键能力
- 连续生成多张图片,角色身份保持一致
- 适用于漫画创作、故事板生成、长视频关键帧
- 在多幅漫画页面或是长视频片段中,角色外观与环境设定维持高度一致

---

## 依赖 (requirements.txt)

```
spaces
peft
diffusers
```

极简依赖,主要靠 HuggingFace Spaces 生态。

---

## 项目特点

- **模块化设计**:支持多种不同的生成模式 (StoryDiffusion, MS-Diffusion, StoryMaker)
- **易于使用**:通过提供 example.json 文件,用户可以轻松配置和使用
- **灵活性和扩展性**:支持多种不同的模型和库
- **性能优化**:不断更新和优化

---

## 故事生成 - 应用场景

1. **故事创作** - 帮助创作者快速生成和编辑故事
2. **游戏开发** - 生成具有连贯性故事背景
3. **动画制作** - 自动生成具有故事性的连续图像
4. **教育和培训** - 帮助学生理解故事生成的技术和方法

---

## 我们的对应节点

我们项目中的相关节点:
- `script_body_pro.py` - 脚本主体生成 (类似 StoryMaker 思路)
- `character_arc_pro.py` - 角色弧线 (类似角色一致性)
- `director_storyboard_pro.py` - 故事板生成 (类似故事板)
- `character_arc_pro.py` - 角色弧
- `vertical_short_drama_pro.py` - 短剧分镜

---

## 与我们项目的关系

**类别: 强竞争 + 高度互补 (角色一致性是这个项目的核心)**

### ⭐⭐⭐⭐⭐ 角色一致性算法 (核心借鉴!)

**StoryDiffusion 一致性自注意力算法** 是核心技术,我们应学习:
- 我们当前的角色弧在脚本生成后,**没有强制每个分镜保持角色一致性**
- 应增加 **角色身份嵌入向量 (Identity Embedding)** 到每个分镜生成
- 借鉴 `Consistory` 项目的"条件解耦"思路:
  - 身份特征 vs 姿势/服装/背景 独立控制

### ⭐⭐⭐⭐⭐ 多角色同框 (高借鉴!)

**MS-Diffusion** 的双角色同框:
- 我们当前的 `script_body_pro.py` 单次输出,角色之间无交互生成
- 应学习:输入两个角色参考图 + 关系词 → 输出同框图
- 这对短剧/双人戏特别有用

### ⭐⭐⭐⭐ StoryMaker: 图像到故事 (高借鉴!)

**借鉴方向:**
- 我们当前是 "文本 → 故事"
- 应增加 "图像 → 故事" 反向能力
- 例: 用户上传一张林黛玉图,自动生成"葬花" 故事

### ⭐⭐⭐⭐ Kolor 着色 + Flux 增强 (中借鉴)

- Flux 风格在我们的 `director_pro.py` 63位导演库中应有
- 上色功能可作为新节点 `image_colorize_pro.py`

### ⭐⭐⭐ InfiniteYou: 无限变化 (中借鉴)

- 我们 `concept_pitch_pro.py` 中"概念变化" 可借鉴
- 同一角色在多个世界观中的变化

### 直接给我们的改进方向

1. **新节点 `character_consistency_pro.py`** - 角色身份嵌入向量,保证 25 段分镜中角色一致
2. **script_body_pro.py** - 增加"参考角色图像"输入端口
3. **director_storyboard_pro.py** - 增加"多角色同框"输出
4. **新节点 `image_to_story_pro.py`** - 图像反推故事
5. **pln_llm.py** - 借鉴 Spaces 生态的轻量化部署

### 互补关系
- StoryDiffusion = **角色一致性技术**
- 我们 = **导演/编剧领域知识 + 故事前文系统**
- 完美组合: 我们的导演风格 → StoryDiffusion 一致性算法 → 25 张同角色分镜

