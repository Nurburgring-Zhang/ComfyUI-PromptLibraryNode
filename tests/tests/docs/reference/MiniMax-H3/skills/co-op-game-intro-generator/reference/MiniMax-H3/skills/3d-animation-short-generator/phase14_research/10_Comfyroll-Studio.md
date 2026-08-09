# Project: Comfyroll Studio

**URL:** https://civitai.com/models/87609/comfyroll-custom-nodes-for-comfyui
**Author:** RockOfFire (Comfyroll)
**License:** open source
**类别:** ComfyUI 提示词工程/工程师节点 (方向 4)

---

## 项目简介

Comfyroll Studio 是一款功能强大的自定义节点集合,专为 ComfyUI 用户打造,旨在提供更加丰富和专业的图像生成与编辑工具。借助这些节点,用户可以在静态图像的精细调整和动态动画的复杂构建方面进行深入探索。

---

## 8 个优质节点详解

### 1. CR Latent Batch Size 节点
- **作用**: 设置潜在空间批处理大小
- **输入**: Latent (编码后的图像特征)
- **参数**: batch_size (一次处理生成的图像数量)
- **输出**: LATENT
- **使用场景**:
  - 批量生成图像(显存允许时增大批大小加速)
  - 实验调优(批量生成对比)

### 2. CR Image Output 节点
- **作用**: 管理/输出生成的图像
- **输入**: images
- **参数**: output_type, file format
- **使用场景**:
  - 批量生成保存
  - 图像预处理和后处理
  - 格式转换与优化

### 3. CR Conditioning Mixer 节点
- **作用**: 混合多个条件输入
- **输入**: conditioning_1, conditioning_2
- **参数**: mix_method (三种), average_strength
- **使用场景**:
  - 文本与图像混合
  - 多文本描述合并
  - 风格迁移

### 4. CR Seed 节点
- **作用**: 管理/控制随机种子
- **参数**: seed, control_after_generate
- **使用场景**:
  - 可重复性实验(固定种子对比)
  - 多样性生成(不同种子)
  - 批量生成(种子序列)

### 5. CR Select Model 节点
- **作用**: 选择和加载生成模型
- **参数**: ckpt_name1~5, select_model
- **输出**: MODEL, CLIP, VAE, ckpt_name
- **使用场景**:
  - 模型对比(快速切换)
  - 多任务处理
  - 模型调优

### 6. CR Combine Prompt 节点
- **作用**: 合并多个文本提示
- **参数**: part1, part2, part3, part4, separator
- **输出**: prompt
- **使用场景**:
  - 详细描述生成
  - 风格混合
  - 创意探索

### 7. CR Prompt Text 节点
- **作用**: 输入/管理文本提示
- **参数**: prompt
- **使用场景**:
  - 图像描述
  - 风格指引
  - 特定主题生成

### 8. CR VAE Decode 节点
- **作用**: 解码 VAE 潜空间表示
- **输入**: samples, vae
- **参数**: tiled, circular
- **使用场景**:
  - 图像生成
  - 图像重建
  - 风格迁移
  - 图像编辑

---

## 安装方法

### 方法一: ComfyUI Manager
1. 打开 ComfyUI 界面 → Manager 管理器
2. 点击 Custom Nodes Manager
3. 搜索"Comfyroll",点击 Install
4. 重启 ComfyUI

### 方法二: Git 克隆
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Suzie1/ComfyUI-Comfyroll-CustomNodes
```

### 方法三: Civitai 下载
https://civitai.com/models/87609/comfyroll-custom-nodes-for-comfyui

---

## 我们的对应节点

我们项目中的相关节点:
- `pln_random.py` (对应 CR Seed 的随机种子管理)
- `prompt_builder.py` (对应 CR Combine Prompt / CR Prompt Text)
- `format_templates.py` (对应 CR Combine Prompt 的模板)

---

## 与我们项目的关系

**类别: 互补 (实用工具节点) + 中借鉴**

### ⭐⭐⭐⭐ CR Combine Prompt (高借鉴)

**借鉴方向:**
- 我们当前的 `prompt_builder.py` 是用 Python dict 实现
- 应学习 Comfyroll 的 `part1, part2, part3, part4, separator` 模式
- 直接作为 ComfyUI 节点的输入端口,而不是 Python 代码

### ⭐⭐⭐⭐ CR Select Model (高借鉴)

**借鉴方向:**
- 我们当前节点没有"模型快速切换" 能力
- 用户要切换模型必须改代码或 hardcode
- 应增加类似 `director_pro.py` 中"5个候选导演"的选择器

### ⭐⭐⭐⭐ CR Conditioning Mixer (中借鉴)

**借鉴方向:**
- 我们当前的 `director_pro.py` 是"选择一个导演",不是"混合多个"
- 应增加"导演风格混合"输入:
  - `徐克 0.6 + 黑泽明 0.4 = 复合风格`
  - 类似 CR Conditioning Mixer 的 average_strength

### ⭐⭐⭐ CR Image Output (中借鉴)

**借鉴方向:**
- 我们没有图像输出管理节点
- 输出只是单一 IMAGE 端口
- 应增加"自动保存到指定目录 + 自定义命名规则"

### 直接给我们的改进方向

1. **`prompt_builder.py` 大改**:
   - 4 个 part 输入端口 (参考 CR Combine Prompt)
   - 可选 separator
   - 用户在 ComfyUI 节点 UI 中直接拼接

2. **新节点 `director_blend_pro.py`**:
   - 借鉴 CR Conditioning Mixer
   - 输入两个导演风格 + 权重
   - 输出混合后的导演风格

3. **新节点 `model_select_pro.py`**:
   - 借鉴 CR Select Model
   - 5 个 ckpt 候选
   - 1 个选择器

4. **新节点 `image_output_pro.py`**:
   - 借鉴 CR Image Output
   - 支持批量保存 + 命名规则
   - 支持文件格式转换 (PNG/JPEG/WebP)

### 互补关系
- Comfyroll Studio = **实用工具节点** (CR* 通用工具)
- 我们 = **导演/编剧领域知识** (director/script 等)
- 完美组合: 我们的导演节点 + Comfyroll 的 CR 工具 = 完整工作流

