# Project: ComfyUI-Prompt-Assistant

**URL:** https://github.com/yawiii/ComfyUI-Prompt-Assistant
**Author:** yawiii
**License:** open source (具体许可证未在 README 中声明)
**类别:** ComfyUI 提示词工程/工程师节点 (方向 4)

---

## 核心简介

支持调用云端大模型 API、本地 Ollama 大模型。实现提示词、Markdown 节点、节点文档翻译;提示词优化、图像反推和视频反推;常用标签收藏、历史记录等功能。是一个全能 all in one 的提示词插件!

适配 ComfyUI node2.0!

---

## 主要功能模块

### 1. 💡 提示词优化 + 翻译
- 支持预设多套提示词优化规则(扩写、qwen-edit指令优化、kontext指令优化并翻译等)
- 无语设置目标语言,自动中英互译
- 自带翻译缓存功能,避免重复翻译导致原文偏差

### 2. 🖼 图像反推
- 在图像节点上快速实现将图片反推成提示词
- 支持(中/英)
- 支持多种反推风格(自然语言、Tag风格...)

### 3. 🔖 标签、短语预设与收藏
- 可将常用标签、短语、Lora 触发词收集,快速插入
- 标签可收藏、自定义、排序
- 支持多套标签切换

### 4. 🕐 历史、撤销、重做
- 按句为单位记录(输入框失焦触发记录)
- 撤销和重做提示词
- 支持跨节点查看提示词历史记录

### 5. 📜 Markdown 和节点文档翻译
- 支持翻译 note 节点和 Markdown 节点,并保持格式
- 支持翻译英文节点文档

### 6. 📒 视频反推 (V2.0 新增)
- 视频反推成提示词 (beta)

### 7. 🏷️ V2 标签管理 (CSV 模式)
- 全新标签机制
- 加载 csv 模式,支持多到 csv 随时切换
- 支持标签收藏

### 8. 🔌 API 服务管理
- 支持自定义服务、支持添加多个模型作为备选
- 扩写、翻译、反推可独立选择服务和模型
- Ollama 支持智能路由(base_url 不加 /v1 走原生 API,加 /v1 走OpenAI 兼容 API)

### 9. 🌐 多语言 UI (V2.0.5)
- 支持:中、英、日、韩、法、西、俄、德等

### 10. 🌱 节点随机种子
- 为所有节点添加了统一的随机种子实现节点重复执行
- 移除通过触发词"[R]"机制实现可重复执行的机制

---

## 节点清单

### ✨ Prompt Assistant 分类
- **翻译节点** - `✨Prompt Assistant → 提示词翻译`
- **提示词优化节点** - `✨Prompt Assistant → 提示词优化`
- **图像反推节点** - `✨Prompt Assistant → 图像反推提示词`
  - 可以反推图像
  - 结合视觉模型优化图像编辑指令
- **视频反推节点** - `✨Prompt Assistant → 视频反推提示词`

---

## 安装方法

### ⚠️ 旧版本迁移注意事项
如果您安装过提示词小助手 2.0 之前的版本,请注意备份原插件目录下的 `config` 目录。避免 api 配置、自定义规则、自定义标签数据丢失!

### 从 ComfyUI Manager 中安装
在 Manager 中输入 `Prompt Assistant` 或 `提示词小助手`,点击 Install,选择最新版本安装。

### 克隆代码仓库
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/yawiii/ComfyUI-Prompt-Assistant.git
# 重启 ComfyUI
# 建议将插件目录名称修改为:prompt-assistant
```

### 数据自动迁移
新版本能自动将用户的 api 配置、自定义规则、自定义标签进行升级和迁移。配置文件存储在:
`ComfyUI/user/default/prompt-assistant`

---

## 关键版本演进

| 版本 | 重要更新 |
|------|---------|
| V3 (最新) | 适配 ComfyUI V3 API 标准;修复 Ollama 路由;子图挂载优化;视频反推 bug 修复 |
| V2.0.5 | 节点随机种子;多语言 UI;修复 node2.0 节点宽度被锁死;baseUrl 输入框置灰 |
| V2.0.0 | 全重构小助手;UI 优化 (支持 node2.0);标签机制重做 (CSV 模式);视频反推节点 (beta) |
| V1.2.x | Ollama 原生接口支持 qwen3vl;新增 http api 保底 |
| V1.1.x | 自动避开滚动条;节点重构;支持所有兼容 OpenAI SDK API |
| V1.0.x | 标签面板可调整大小;UI 资源加载优化;修复汉化插件冲突 |

---

## 与我们项目的关系

**类别: 强竞争/高度互补** (我们已有 prompt_builder.py 等)

### ⭐⭐⭐⭐⭐ API 服务管理 (核心借鉴!)

我们当前的 `prompt_builder.py` 用单 API 配置,应学习其:
- **多服务并行管理** (OpenAI / 302.AI / Ollama / 自定义)
- **扩写/翻译/反推可独立选择服务**
- **模型备选链**(主服务失败自动切换)

### ⭐⭐⭐⭐⭐ 标签 CSV 模式 (高借鉴!)

我们的 `modes_book.py` 等是 Python dict,应学习:
- **加载 csv 模式,支持多套标签切换** - 用户可加载自己的标签库
- **标签收藏、排序、跨工程** - 个人 vs 项目级标签
- 这对 `director_pro.py` 的"63位导演"、"22种类型片"管理特别有用

### ⭐⭐⭐⭐ 多语言支持 (高借鉴!)

我们当前节点仅支持中文,应学习:
- 多语言 UI 切换(中英日韩法西俄德)
- 节点文档自动翻译(英文 → 中文)

### ⭐⭐⭐⭐ 视频反推 (新功能!)

- V2.0 新增,beta
- 我们项目当前没有视频反推能力
- 未来可加入: 输入短视频 → 反推成 Sora 风格提示词
- 与 `vertical_short_drama_pro.py` / `mv_pro.py` 联动

### ⭐⭐⭐ 历史/撤销机制 (中借鉴)

我们当前节点无"按句撤销"
- 我们的 `script_body_pro.py` 输出 25 段,撤销可以做到段级

### 互补关系
- Prompt-Assistant 是**通用 LLM 包装器**
- 我们是**导演/编剧领域知识** (导演风格库、故事弧、节拍)
- 我们的 prompt_builder 可以**调用他们的服务** 作为底层 API

### 给我们 25 节点的直接改进方向

1. **pln_utils.py / prompt_builder.py** - 增加多服务管理 (类似 Ollama 智能路由)
2. **director_pro.py** - 标签 CSV 化,支持多套导演/类型片库切换
3. **script_body_pro.py** - 加入"按句历史/撤销"
4. **新节点 `prompt_translate_pro.py`** - 直接借鉴其翻译节点 (多服务 + 缓存)

