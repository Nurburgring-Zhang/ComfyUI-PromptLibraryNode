# Project: comfyui-storyboard

**URL:** https://github.com/colorAi/comfyui-storyboard
**Author:** colorAi (jtydhr88 项目支持)
**License:** MIT License
**Last update:** 2026-01-10
**Stars:** (项目初期)
**类别:** ComfyUI 导演/编剧/分镜节点 (方向 1)

---

## 📋 Changelog

- **2026-01-10** Added camera parameter preset functionality. Users can now add custom angles and corresponding prompts.

---

## 项目简介

ComfyUI Storyboard 是一个功能强大的 ComfyUI 自定义节点和界面扩展,旨在实现高效的故事板创建、管理和执行。它引入了一个可视化的工作流,用于管理具有独立提示词和相机设置的多个"分镜"(场景),并无缝集成到您现有的 ComfyUI 工作流中。

---

## ✨ Features

- **Visual Storyboard Interface**: Manage multiple shots in a grid view.
- **3D Camera Control**: Interactive 3D viewer to set camera angles (Azimuth, Elevation, Zoom) which automatically generates descriptive prompts (e.g., "front view", "high angle").
- **Batch Execution**: Run individual shots or all shots in sequence.
- **Workflow Integration**: Dynamically injects prompts and camera settings into your existing ComfyUI graph.
- **Add to Workflow**: Converts your storyboard shots into actual nodes in the ComfyUI workspace for further editing.
- **Data Persistence**: Automatically saves your storyboard data (shots, settings) using a local SQLite database, ensuring you never lose your work.
- **Bilingual UI**: Fully supports English and Chinese interfaces.

---

## 📦 Installation

### Method 1: Via ComfyUI Manager
Search for `comfyui storyboard` in ComfyUI Manager and install.

### Method 2: Manual Installation
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/colorAi/comfyui-storyboard.git
# Restart ComfyUI
```

---

## 🚀 Usage

### 1. Opening the Interface
Click the "Storyboard" button in the ComfyUI menu bar to open the main interface.

### 2. Configuring Nodes
At the top of the Storyboard interface, you need to map the nodes from your current workflow:
- **Prompt Node**: Select the node where the text prompt should be injected (usually a CLIP Text Encode or similar).
- **Save Image Node**: Select the node that handles saving or previewing the image.
- **Ref Image Node (Optional)**: Select a Load Image node if you are doing img2img workflows.

### 3. Managing Shots
- **Add Shot**: Click "➕ Add Shot" to create a new storyboard panel.
- **Edit Prompt**: Type your prompt directly into the shot card.
- **Camera Settings**: Click the "Camera" button on a shot to open the 3D Camera tool. Adjust the angle and zoom, and the tool will generate a prompt description for you.

### 4. Running Generations
- **Run Shot**: Click the "▶" button on a specific shot to generate just that image.
- **Run All**: Click "▶ Run All" to generate all shots in sequence.

### 5. Add to Workflow
Click "📥 Add to Workflow" to output your generated storyboard shots as actual nodes into the main ComfyUI canvas. This is useful if you want to perform further complex processing on specific shots.

---

## 🔧 Requirements
- ComfyUI (latest version recommended)
- Python 3.x
- Modern Browser (Chrome/Firefox/Edge) for the 3D features.

---

## 📄 License
MIT License.

---

## 与我们项目的关系

**类别: 强竞争/可借鉴** (类似功能,我们有 director_storyboard_pro.py)

### 借鉴价值 (⭐⭐⭐⭐⭐)
1. **网格视图分镜管理** - 我们当前是表格+分镜文本,可考虑图形化卡片视图
2. **3D 相机控制 → 提示词自动生成** - 我们有 director_storyboard_pro 的景别/运镜,但没有 3D 交互
3. **SQLite 本地数据持久化** - 我们当前用 JSON,可能需考虑切换到 SQLite 应对大项目
4. **双语界面(中英文)** - 我们已支持中文,可借鉴其 UI 切换模式
5. **"Add to Workflow" 反向输出** - 我们是单节点,可借鉴把故事板展开成 ComfyUI 节点图

### 差异化机会
- 我们有 **63位导演风格库 + 22种类型片视觉语言**,这是其没有的领域知识
- 我们的**故事前文系统 + 张弛有度节奏系统** 更专业

