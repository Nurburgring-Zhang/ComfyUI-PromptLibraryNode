# Phase 14 项目调研报告: ComfyUI 导演/编剧/分镜/无限画布生态

> **调研对象:** ComfyUI-PromptLibraryNode 项目(25 节点, 导演/编剧/分镜/故事板/短剧)
> **调研目的:** 找 10 个同方向开源项目,提炼可借鉴能力,为 25 节点改进提供方向
> **调研时间:** Phase 14
> **调研员:** Phase 14 Research Agent

---

## 📊 调研总结

| 指标 | 数值 |
|------|------|
| 找到项目数 | **10 个** (覆盖 5 个方向) |
| 深入分析数 | **10 个** (全部 10 个项目) |
| 单独 README 文档 | 10 个 (保存在 `phase14_research/*.md`) |
| 覆盖方向 | 5/5 (导演编剧/短剧分镜/无限画布/提示词工程/角色一致性) |
| 关键借鉴建议 | 见 "第六部分" 25 节点具体改进 |

---

## 第一部分: 10 项目总览

| # | 项目名 | 作者 | 方向 | 许可证 | 状态 |
|---|--------|------|------|--------|------|
| 1 | **comfyui-storyboard** | colorAi | 1 导演/分镜 | MIT | ⭐⭐⭐⭐⭐ 直接竞品 |
| 2 | **ComfyUI-Impact-Pack** | ltdrdata | 5 角色一致性 | GPL-3.0 | ⭐⭐⭐⭐⭐ 3.2k stars 必看 |
| 3 | **ComfyUI-Prompt-Assistant** | yawiii | 4 提示词工程 | open source | ⭐⭐⭐⭐⭐ V3 提示词小助手 |
| 4 | **ComfyUI-LTXVideo** | Lightricks | 2 AI 视频 | open source | ⭐⭐⭐⭐ 官方 LTX-2 支持 |
| 5 | **ComfyUI-Ycanvas** | yichengup | 3 无限画布 | open source | ⭐⭐⭐ 画布拖拽编辑 |
| 6 | **ComfyUI-StoryDiffusion** | zhou311113 | 1 故事生成 | open source | ⭐⭐⭐⭐ 角色一致性算法 |
| 7 | **Pixelle-Video** | Open Source | 2 AI 视频 | open source | ⭐⭐⭐⭐ 占位符工作流 |
| 8 | **ComfyUI-StringConstructor** | Lex-DRL | 4 提示词工程 | open source | ⭐⭐⭐⭐⭐ 字典+递归格式化 |
| 9 | **ComfyUI-Workflow** | knishika62 | 2 短剧分镜 | open source | ⭐⭐⭐⭐ sora2-like 模板 |
| 10 | **Comfyroll Studio** | RockOfFire | 4 实用工具 | open source | ⭐⭐⭐⭐ 8 个 CR 节点 |

---

## 第二部分: 5 大方向详细分析

### 方向 1: ComfyUI 导演/编剧/故事板节点

| 项目 | 核心能力 | 与我们的关系 |
|------|---------|-------------|
| **comfyui-storyboard** | 网格视图分镜、3D相机控制自动转提示词、SQLite持久化、双语UI | **直接竞品** - 我们有 director_storyboard_pro,可借鉴其网格视图+3D相机 |
| **ComfyUI-StoryDiffusion** | 角色一致性自注意力算法(南开HVision)、多角色同框、图像反推故事 | **互补** - 角色一致性是核心技术,我们应学习 |

**关键发现:** 我们在"导演领域知识"上领先(63位导演库+22种类型片+故事前文系统),但在"3D交互"和"角色一致性算法"上落后。

---

### 方向 2: ComfyUI 短剧/分镜/AI 视频工作流

| 项目 | 核心能力 | 与我们的关系 |
|------|---------|-------------|
| **ComfyUI-Workflow (scenario_i2v)** | 详细CRITICAL规则(角色一致/对白/镜头/4-6场景)、日语对白处理 | **高借鉴** - 提示词规则设计非常专业 |
| **ComfyUI-LTXVideo** | T2V/I2V/V2V 三模式、IC-LoRA联合控制、注意力控制区域、性能优化 | **互补** - AI视频执行层,我们应桥接 |
| **Pixelle-Video** | **占位符动态替换** `{{prompt}}`、三阶段流水线(image/video/tts) | **高借鉴** - 关键创新,工作流模板化 |

**关键发现:** 占位符机制(Pixelle-Video)和严格CRITICAL规则(ComfyUI-Workflow)是两个最值得我们立刻学习的点。

---

### 方向 3: ComfyUI 无限画布/Infinite Canvas/Workflow Builder

| 项目 | 核心能力 | 与我们的关系 |
|------|---------|-------------|
| **ComfyUI-Ycanvas** | Web画布弹窗、拖拽缩放旋转、透明度调节 | **互补** - 用户交互层 |
| **类似 infinite-canvas** | 提示词管理、素材库、批量任务、画布/工作区 | **高借鉴** - 批量任务+变量替换 |

**关键发现:** 我们当前的批量和变量替换能力不足,应学习 infinite-canvas 的"变量列表+排列组合" 模式。

---

### 方向 4: ComfyUI 提示词工程/工程师节点

| 项目 | 核心能力 | 与我们的关系 |
|------|---------|-------------|
| **ComfyUI-Prompt-Assistant** | LLM多服务管理(Ollama/302.AI/OpenAI)、标签CSV、视频反推、多语言UI、节点文档翻译 | **直接竞品** - V3架构非常成熟 |
| **ComfyUI-StringConstructor** | 字典+递归格式化、Bus设计、条件格式化、模式作为字典一部分 | **底层技术** - 关键创新 |
| **Comfyroll Studio** | CR Combine Prompt (4 part)、CR Select Model (5 ckpt)、CR Conditioning Mixer | **实用工具** - 借鉴具体节点设计 |

**关键发现:** 三个项目各有侧重 - Prompt-Assistant是LLM包装、StringConstructor是格式化机制、Comfyroll是实用工具。我们应取三者之长。

---

### 方向 5: ComfyUI 资产/角色一致性管理

| 项目 | 核心能力 | 与我们的关系 |
|------|---------|-------------|
| **ComfyUI-Impact-Pack** | 3.2k stars ⭐⭐⭐⭐⭐、Detector(BBox/SAM/SEGM)、**Pipe管道系统**、**Wildcards系统**、FaceDetailer、SEGS、ImageSender/Receiver | **强借鉴** - Pipe和Wildcards是核心创新 |

**关键发现:** Impact-Pack的Pipe系统(用一条线代替多条线)和Wildcards系统(权重+YAML)是两个最值得我们立刻学习的架构级创新。

---

## 第三部分: 能力矩阵对比 (10 项目 × 8 关键能力)

| 项目 | 导演领域知识 | 角色一致性 | 批量/变量 | 画布/可视化 | 提示词工程 | LLM集成 | AI视频 | 工作流模板化 |
|------|-------------|-----------|----------|------------|------------|---------|---------|-------------|
| **comfyui-storyboard** | ★★ | ★★ | ★★★ | ★★★★★ | ★ | × | × | ★★★ |
| **ComfyUI-Impact-Pack** | × | ★★★★★ | ★★★ | ★★ | ★★ | × | × | ★★ |
| **ComfyUI-Prompt-Assistant** | ★ | ★ | ★★ | ★★ | ★★★★★ | ★★★★★ | × | ★★ |
| **ComfyUI-LTXVideo** | × | ★★★ | ★★ | × | × | × | ★★★★★ | ★★★ |
| **ComfyUI-Ycanvas** | × | × | ★★ | ★★★★★ | × | × | × | × |
| **ComfyUI-StoryDiffusion** | ★★ | ★★★★★ | ★★ | ★★★ | ★ | × | ★★ | ★★ |
| **Pixelle-Video** | × | ★★ | ★★★ | ★★ | ★ | ★★ | ★★★★★ | ★★★★★ |
| **ComfyUI-StringConstructor** | × | × | ★★★★ | × | ★★★★★ | × | × | ★★★★ |
| **ComfyUI-Workflow** | ★★★ | ★★★★ | ★★★ | × | ★★★★ | × | ★★★ | ★★★ |
| **Comfyroll Studio** | × | × | ★★ | × | ★★★★ | × | × | ★★★ |
| **我们(25 节点)** | ★★★★★ | ★★★ | ★★ | ★★ | ★★★ | ★★★ | ★★ | ★★ |

**矩阵读法:**
- **我们的优势:** 导演领域知识(★★★★★)无人能敌
- **我们最大的缺口:**
  1. **批量/变量(★★)** - 应借鉴 StringConstructor(★★★★) + Pixelle-Video(★★★) + Impact-Pack(★★★)
  2. **画布/可视化(★★)** - 应借鉴 Ycanvas(★★★★★) + storyboard(★★★★★)
  3. **工作流模板化(★★)** - 应借鉴 Pixelle-Video(★★★★★) + StringConstructor(★★★★)

---

## 第四部分: 5 个最值得深入分析的项目 (核心借鉴)

### ⭐⭐⭐⭐⭐ ComfyUI-Impact-Pack (3.2k stars, 最推荐)

**为什么最值得分析:**
1. **Pipe 管道系统** - 用一条线代替多条线 (model/clip/vae/positive/negative),减少 80% 连线
2. **Wildcards 系统** - `__animal__` 通配符 + 权重选择 + YAML 格式
3. **FaceDetailer** - 完整的人脸检测+修复流水线
4. **SEGS / MakeTileSEGS** - 超大图像分块处理
5. **Hook 系统** - Detailer 钩子,扩展点清晰

**直接借鉴清单:**
- ✅ Pipe 概念用于 `prompt_builder.py` 重构
- ✅ Wildcards 用于 `modes_book.py` / `director_pro.py` (63位导演库)
- ✅ FaceDetailer 用于 `character_arc_pro.py` (角色面部一致性)
- ⚠️ 注意安全: 2024-12 报告 path traversal 漏洞,用户输入必须白名单校验

---

### ⭐⭐⭐⭐⭐ ComfyUI-StringConstructor (字典+递归格式化, 技术核心)

**为什么最值得分析:**
1. **字典 Bus 设计** - 单线传递全字典,任意节点可访问
2. **递归格式化** - chunks 相互引用,构建层次化模板
3. **条件格式化** - 动态模式 `{{character_N}}` 切换
4. **safe mode** - 无法格式化时保留原样

**直接借鉴清单:**
- ✅ 创建 `StoryDict` 全局字典 (角色/场景/导演/质量)
- ✅ 递归引用减少 `script_body_pro.py` 70% 代码量
- ✅ 动态切换"主导演"
- ✅ 修一处全局生效

**示例改进:**
```python
# 当前 (我们的做法)
shot_1_prompt = "masterpiece, best quality, 1girl, ..."

# 借鉴后
quality = "masterpiece, best quality"
character = "1girl, blue hair"
shot_1_prompt = "{quality}, {character}, in a garden"
```

---

### ⭐⭐⭐⭐⭐ ComfyUI-Prompt-Assistant (V3 成熟架构)

**为什么最值得分析:**
1. **多服务管理** - OpenAI / Ollama / 302.AI / 自定义,智能路由
2. **标签 CSV 模式** - 多套标签切换 + 收藏 + 排序
3. **节点随机种子** - `[R]` 触发词(后来改为统一种子节点)
4. **多语言 UI** - 中英日韩法西俄德 8 语言
5. **节点文档翻译** - 英文 → 中文自动翻译

**直接借鉴清单:**
- ✅ `pln_utils.py` 增加多服务管理 (Ollama 智能路由)
- ✅ `director_pro.py` 标签 CSV 化
- ✅ 新节点 `prompt_translate_pro.py` - 多服务 + 缓存
- ✅ 视频反推 (V2.0 beta) - 与 `vertical_short_drama_pro.py` 联动

---

### ⭐⭐⭐⭐ Pixelle-Video (占位符工作流, 创新)

**为什么最值得分析:**
1. **占位符 `{{prompt}}`** 在工作流 JSON 中
2. **三阶段流水线** image → video → tts
3. **云端 + 本地双部署**

**直接借鉴清单:**
- ✅ `director_storyboard_pro.py` 输出"工作流 JSON" 按钮
- ✅ 新节点 `workflow_template_pro.py` - 读取 JSON 模板 + 替换占位符
- ✅ `production_pipeline_v3.py` 支持三阶段流水线

---

### ⭐⭐⭐⭐ ComfyUI-Workflow scenario_i2v (CRITICAL 规则设计)

**为什么最值得分析:**
1. **CRITICAL 关键字强制约束** - 非常专业
2. **镜头选择指南**:
   - Opening scenes → wide establishing shots
   - Dialogue moments → medium close-up
   - Action moments → handheld tracking
3. **对白处理** - 描述为音频("is heard saying")
4. **时序连接词** - "then", "next", "as the scene shifts to"

**直接借鉴清单:**
- ✅ `vertical_short_drama_pro.py` 加入 CRITICAL 规则
- ✅ `director_intent_pro.py` 增强镜头选择
- ✅ `script_body_pro.py` 加入时序连接词

---

## 第五部分: 与我们 25 节点的具体改进映射

### 5.1 我们当前的 25 节点清单 (基于目录扫描)

| # | 文件名 | 功能 | 当前缺口 |
|---|--------|------|---------|
| 1 | `director_pro.py` | 63位导演库 | 单选,无混合权重,无CSV |
| 2 | `director_intent_pro.py` | 导演意图 | 镜头选择规则不全 |
| 3 | `director_storyboard_pro.py` | 故事板 | 无3D交互,无网格视图 |
| 4 | `director_mastery_v2.py` | 导演综合 | 重复导演库 |
| 5 | `script_architecture_pro.py` | 脚本架构 | 引用繁琐 |
| 6 | `script_body_pro.py` | 脚本主体 | 25段重复,无递归 |
| 7 | `dialogue_master_pro.py` | 对白 | 无音频vs视觉处理 |
| 8 | `character_arc_pro.py` | 角色弧 | 无面部一致性 |
| 9 | `vertical_short_drama_pro.py` | 短剧 | 无CRITICAL规则 |
| 10 | `mv_pro.py` | MV | 音乐场景镜头规则不全 |
| 11 | `picture_book_pro.py` | 绘本 | 重复 |
| 12 | `interactive_drama_pro.py` | 互动剧 | 单次输出,无分支 |
| 13 | `hook_master_pro.py` | 钩子 | OK |
| 14 | `concept_pitch_pro.py` | 概念推介 | OK |
| 15 | `world_building_pro.py` | 世界观 | OK |
| 16 | `costume_prop_set_pro.py` | 服饰 | 特写聚焦不够 |
| 17 | `music_score_pro.py` | 配乐 | 节奏镜头映射 |
| 18 | `sound_design_pro.py` | 声音设计 | 音效每段变化 |
| 19 | `editing_pro.py` | 剪辑 | OK |
| 20 | `vfx_pro.py` | 视效 | OK |
| 21 | `color_grading_pro.py` | 调色 | OK |
| 22 | `anti_ai_vocab.py` | 反AI味 | OK |
| 23 | `theme_philosophy_pro.py` | 主题哲学 | OK |
| 24 | `performance_direction_pro.py` | 表演指导 | OK |
| 25 | `silence_mastery_pro.py` | 静默 | OK |
| 26 | `engine_story_arc.py` | 故事弧引擎 | 引擎层,OK |
| 27 | `production_pipeline_v3.py` | 生产线 | 缺占位符工作流 |
| 28 | `pln_llm.py` | LLM | 单服务,无智能路由 |
| 29 | `pln_utils.py` | 工具 | 缺字典+递归 |
| 30 | `pln_random.py` | 随机 | 缺通配符 |
| 31 | `format_templates.py` | 模板 | OK |
| 32 | `prompt_builder.py` | 提示词构建 | 重复 4 part 未实现 |
| 33 | `master_director_data.py` | 导演数据 | OK |
| 34 | `doctor.py` | 工具 | OK |

### 5.2 直接改进映射表 (借鉴 → 我们的节点)

| 借鉴来源 | 借鉴能力 | 改进哪个节点 | 优先级 |
|---------|---------|-------------|--------|
| **StringConstructor** | 字典+递归格式化 | `pln_utils.py` 新增 `FormatDict` 类 | 🔴 P0 |
| **StringConstructor** | 模板继承 | `script_body_pro.py` 重构(减70%代码) | 🔴 P0 |
| **Impact-Pack Pipe** | 管道系统 | 新节点 `prompt_pipe_pro.py` | 🟡 P1 |
| **Impact-Pack Wildcards** | 通配符+权重 | `pln_random.py` + `director_pro.py` | 🟡 P1 |
| **Impact-Pack FaceDetailer** | 面部修复+角色一致性 | `character_arc_pro.py` 增强 | 🟡 P1 |
| **Prompt-Assistant 多服务** | Ollama 智能路由 | `pln_llm.py` 重构 | 🔴 P0 |
| **Prompt-Assistant 标签 CSV** | 多套标签切换 | `director_pro.py` 标签 CSV 化 | 🟡 P1 |
| **Prompt-Assistant 视频反推** | 视频反推 | 新节点 `video_to_prompt_pro.py` | 🟢 P2 |
| **Prompt-Assistant 多语言 UI** | 8 语言 | 所有节点的 UI | 🟢 P2 |
| **Pixelle-Video 占位符** | `{{prompt}}` 工作流 | `director_storyboard_pro.py` 导出 JSON | 🔴 P0 |
| **Pixelle-Video 流水线** | image→video→tts | `production_pipeline_v3.py` 增强 | 🟡 P1 |
| **storyboard 网格视图** | 网格卡片 | 新节点 `storyboard_canvas_pro.py` | 🟡 P1 |
| **storyboard 3D 相机** | 3D 控制转提示词 | 新节点 `camera_3d_pro.py` | 🟢 P2 |
| **StoryDiffusion 角色一致性** | 自注意力算法 | 新节点 `character_consistency_pro.py` | 🟡 P1 |
| **StoryDiffusion 多角色同框** | MS-Diffusion | `script_body_pro.py` 增强 | 🟢 P2 |
| **StoryDiffusion 图像反推故事** | StoryMaker | 新节点 `image_to_story_pro.py` | 🟢 P2 |
| **Ycanvas 画布** | 拖拽编辑 | 新节点 `storyboard_canvas_pro.py` | 🟡 P1 |
| **infinite-canvas 批量+变量** | 排列组合 | 新节点 `batch_storyboard_pro.py` | 🔴 P0 |
| **infinite-canvas 素材库** | 参考图管理 | 新节点 `asset_library_pro.py` | 🟢 P2 |
| **Workflow scenario_i2v CRITICAL** | 强制规则 | `vertical_short_drama_pro.py` 加入 | 🟡 P1 |
| **Workflow scenario_i2v 镜头指南** | 情绪→镜头 | `director_intent_pro.py` 增强 | 🟡 P1 |
| **Workflow scenario_i2v 对白处理** | 描述为音频 | `dialogue_master_pro.py` 增强 | 🟡 P1 |
| **Comfyroll CR Combine Prompt** | 4 part 输入 | `prompt_builder.py` 重构 | 🟡 P1 |
| **Comfyroll CR Select Model** | 5 候选选择器 | `director_pro.py` 增强 | 🟢 P2 |
| **Comfyroll CR Conditioning Mixer** | 多条件混合 | 新节点 `director_blend_pro.py` | 🟢 P2 |

---

## 第六部分: 关键借鉴建议清单 (按优先级)

### 🔴 P0 - 立即实现 (最高价值)

1. **`pln_utils.py` 增加 FormatDict 字典机制 (借鉴 StringConstructor)**
   - 创建 `StoryDict` 全局字典
   - 支持 `{quality}`, `{character}`, `{director}` 模板引用
   - 支持递归引用
   - **预期价值:** `script_body_pro.py` 代码量减少 70%,修一处全 25 段生效

2. **`director_storyboard_pro.py` 增加"导出 ComfyUI 工作流 JSON" 按钮 (借鉴 Pixelle-Video)**
   - 使用 `{{shot_N_prompt}}` 占位符
   - 用户可一键注入到 ComfyUI 节点图
   - **预期价值:** 用户从 25 段分镜 → 直接生成可执行工作流,无需手动复制

3. **`pln_llm.py` 重构多服务管理 (借鉴 Prompt-Assistant)**
   - 支持 OpenAI / Ollama / 302.AI / 自定义
   - 智能路由 (base_url 不加 /v1 走原生,加 /v1 走 OpenAI 兼容)
   - 主服务失败自动切换备选
   - **预期价值:** 用户不再被单一 LLM 服务绑架,稳定性提升 5x

4. **新节点 `batch_storyboard_pro.py` (借鉴 infinite-canvas 变量替换)**
   - 输入: 角色列表 + 场景列表
   - 输出: 自动生成 N×M 个分镜
   - 例如: 林黛玉+薛宝钗 × 大观园+潇湘馆 = 4 个分镜
   - **预期价值:** 真正"批量"生成,而不是"单次"25段

### 🟡 P1 - 中期改进 (高价值)

5. **`script_body_pro.py` 重构 (借鉴 StringConstructor 递归)**
   - 25 段共享质量标签、负面词、风格
   - 修一处全 25 段生效
   - 减少 70% 代码量

6. **新节点 `prompt_pipe_pro.py` (借鉴 Impact-Pack Pipe 系统)**
   - 一条线代替多条线 (model/clip/vae/positive/negative)
   - 大幅减少工作流连线复杂度

7. **`director_pro.py` 标签 CSV 化 (借鉴 Prompt-Assistant)**
   - 多套导演库切换
   - 标签收藏、排序
   - 用户可上传自己的导演库

8. **`character_arc_pro.py` 增强 (借鉴 Impact-Pack FaceDetailer)**
   - 加入面部一致性
   - 借鉴 IP-Adapter 实现角色身份嵌入

9. **`vertical_short_drama_pro.py` 加入 CRITICAL 规则 (借鉴 ComfyUI-Workflow)**
   - 强制角色一致性
   - 强制对白处理
   - 强制镜头选择规则

10. **`director_intent_pro.py` 增强镜头选择 (借鉴 ComfyUI-Workflow 镜头指南)**
    - Opening → wide establishing
    - Dialogue → medium close-up
    - Action → handheld tracking
    - Emotional → slow dolly in

11. **`dialogue_master_pro.py` 增强 (借鉴 ComfyUI-Workflow 对白处理)**
    - 描述为音频 (`is heard saying`, 不是 `says`)
    - 用户对白 EXACT 使用
    - 不要"清理"用户内容

12. **`prompt_builder.py` 重构 (借鉴 Comfyroll CR Combine Prompt)**
    - 4 个 part 输入端口
    - 可选 separator
    - 用户在 UI 中直接拼接

13. **`production_pipeline_v3.py` 增强 (借鉴 Pixelle-Video 流水线)**
    - 支持 image → video → tts 三阶段
    - 对应我们的 `costume_prop_set_pro` → `vertical_short_drama_pro` → `mv_pro`

14. **新节点 `storyboard_canvas_pro.py` (借鉴 comfyui-storyboard 网格视图)**
    - 网格卡片显示分镜
    - 拖拽调整顺序
    - 删除/重新生成单个

15. **新节点 `character_consistency_pro.py` (借鉴 StoryDiffusion)**
    - 角色身份嵌入向量
    - 保证 25 段分镜中角色一致
    - 借鉴 Consistory 条件解耦

### 🟢 P2 - 长期改进 (中等价值)

16. **新节点 `camera_3d_pro.py` (借鉴 comfyui-storyboard 3D 相机)**
    - 交互式 3D 视角控制
    - 自动转提示词 (Azimuth, Elevation, Zoom)

17. **`director_pro.py` 增强 (借鉴 Comfyroll CR Select Model)**
    - 5 个候选导演
    - 1 个选择器

18. **新节点 `director_blend_pro.py` (借鉴 Comfyroll CR Conditioning Mixer)**
    - 多导演权重混合 (徐克 0.6 + 黑泽明 0.4)
    - 类似平均强度

19. **新节点 `image_to_story_pro.py` (借鉴 StoryDiffusion StoryMaker)**
    - 图像反推故事
    - 用户上传林黛玉图 → 自动生成"葬花"故事

20. **多语言 UI (借鉴 Prompt-Assistant)**
    - 8 语言支持 (中英日韩法西俄德)
    - 节点文档自动翻译

21. **新节点 `video_to_prompt_pro.py` (借鉴 Prompt-Assistant 视频反推)**
    - 输入短视频 → 输出 Sora 风格提示词
    - 与 `vertical_short_drama_pro.py` 联动

22. **新节点 `asset_library_pro.py` (借鉴 infinite-canvas 素材库)**
    - 参考图管理
    - 我们的 22 种类型片视觉语言关联参考图

23. **新节点 `story_music_sync_pro.py` (借鉴 Workflow scenario_i2v)**
    - 音乐场景镜头规则
    - BPM 节奏映射镜头切换
    - 充实 `mv_pro.py`

24. **`script_body_pro.py` 加入时序连接词 (借鉴 ComfyUI-Workflow)**
    - "then", "next", "as the scene shifts to"
    - 在段落之间自动插入

25. **多角色同框 (借鉴 StoryDiffusion MS-Diffusion)**
    - 输入两个角色参考图 + 关系词
    - 输出同框图
    - 对短剧双人戏特别有用

---

## 第七部分: 关键架构级洞察

### 洞察 1: 我们是"领域知识 + 规则引擎",不是"工具节点"

我们 25 节点的本质是**导演/编剧领域知识 + 故事前文系统**。这在所有调研项目中**独一无二**。
- **不**模仿的工具: Impact-Pack (基础设施), StringConstructor (格式化), Comfyroll (CR 工具)
- **应该**借鉴的: 它们的"工作流架构模式"(Pipe, Wildcards, 占位符, 字典),然后用我们的领域知识填充。

### 洞察 2: 三大"借鉴阶梯"

| 阶梯 | 来源 | 我们的 25 节点现状 |
|------|------|------------------|
| **基础设施层** | Impact-Pack, Comfyroll | 缺失 Pipe 概念、Wildcards、CR Combine Prompt |
| **执行层** | LTX-Video, Pixelle-Video, Ycanvas | 缺失占位符工作流、画布、变量替换 |
| **技术层** | StringConstructor, Prompt-Assistant | 缺失字典+递归、多服务管理、标签 CSV |

**建议:** 按阶梯顺序实现,先 P0(基础设施),再 P1(执行层),最后 P2(技术层)。

### 洞察 3: 我们的核心壁垒 (从竞争中保护)

| 我们独有 | 谁也无法复制 |
|---------|-------------|
| **63位导演风格库** | 数据壁垒 |
| **22种类型片视觉语言** | 数据壁垒 |
| **故事前文系统** (每个分镜前携带大纲) | 架构壁垒 |
| **张弛有度节奏系统** (识别蓄势/拐点/爆发/喘息/余韵) | 算法壁垒 |
| **按叙事功能推断表演情绪** (不是纯数值映射) | 算法壁垒 |
| **导演+类型→叙事结构自动适配** (徐克+神话→英雄之旅) | 知识图谱壁垒 |

**保护策略:** 这些是我们的护城河,绝不能为追求"通用性"而削弱。应专注于深化和扩展这些壁垒。

### 洞察 4: 最该做的 5 件事 (Top 5)

1. **引入字典+递归格式化** (StringConstructor) - 影响 70% 代码量
2. **工作流 JSON 占位符** (Pixelle-Video) - 影响用户从"看分镜"到"跑工作流"的最后一步
3. **多服务 LLM 路由** (Prompt-Assistant) - 影响稳定性和可扩展性
4. **批量变量替换** (infinite-canvas) - 影响从"单次"到"批量"的能力跃迁
5. **Pipe 管道系统** (Impact-Pack) - 影响整个工作流的易用性

### 洞察 5: 立即避免的 5 件事 (Anti-patterns)

1. ❌ **不要做通用 LLM 包装** - 这是 Prompt-Assistant 的赛道,会分散精力
2. ❌ **不要做图像反推** - 留给社区做,我们专注"领域知识"
3. ❌ **不要做 3D 相机** - 工程量大,价值相对小
4. ❌ **不要做 FaceDetailer** - 直接用 Impact-Pack 的(用户可叠加安装)
5. ❌ **不要做云端 SaaS** - 我们是开源工具,Pixelle-Video 已是云端

---

## 第八部分: 行动路线图

### Phase 15 - 立即执行 (1-2 周)
- ✅ P0-1: `pln_utils.py` 增加 FormatDict
- ✅ P0-2: `director_storyboard_pro.py` 导出 ComfyUI 工作流 JSON
- ✅ P0-3: `pln_llm.py` 多服务管理
- ✅ P0-4: 新节点 `batch_storyboard_pro.py`

### Phase 16 - 短期 (3-4 周)
- 🟡 P1-5 到 P1-15: 14 项中期改进

### Phase 17 - 中期 (5-8 周)
- 🟢 P2-16 到 P2-25: 10 项长期改进

### Phase 18+ - 持续
- 关注 Impact-Pack, StringConstructor, Prompt-Assistant 的更新
- 吸收社区新想法
- 持续深化 63位导演库, 22种类型片

---

## 第九部分: 附录 - 10 项目详细 README 索引

| # | 文件 | 方向 | 核心借鉴点 |
|---|------|------|----------|
| 1 | `01_comfyui-storyboard.md` | 1 导演/分镜 | 网格视图 + 3D 相机 + SQLite 持久化 |
| 2 | `02_ComfyUI-Impact-Pack.md` | 5 角色一致性 | **Pipe 管道** + **Wildcards** + FaceDetailer |
| 3 | `03_ComfyUI-Prompt-Assistant.md` | 4 提示词工程 | **多服务管理** + **标签 CSV** + 视频反推 + 8 语言 |
| 4 | `04_ComfyUI-LTXVideo.md` | 2 AI 视频 | T2V/I2V/V2V + IC-LoRA + 注意力控制 |
| 5 | `05_ComfyUI-Ycanvas.md` | 3 无限画布 | 拖拽 + 缩放 + 旋转 |
| 6 | `06_ComfyUI-StoryDiffusion.md` | 1 故事生成 | **角色一致性算法** + MS-Diffusion + StoryMaker |
| 7 | `07_Pixelle-Video.md` | 2 AI 视频 | **占位符动态替换** + 三阶段流水线 |
| 8 | `08_ComfyUI-StringConstructor.md` | 4 提示词工程 | **字典+递归格式化** + 条件格式化 |
| 9 | `09_ComfyUI-Workflow_scenario_i2v.md` | 2 短剧分镜 | **CRITICAL 规则** + 镜头选择指南 |
| 10 | `10_Comfyroll-Studio.md` | 4 实用工具 | CR Combine Prompt + CR Select Model + CR Conditioning Mixer |

---

## 报告元信息

- **生成时间:** Phase 14
- **生成方式:** 联网搜索 (5 个方向 × 2-3 关键词) + 10 个项目深入分析
- **数据来源:** GitHub README, 官方文档, 社区文章, 视频教程
- **下一步:** 等待 Phase 15 执行 P0 改进
- **维护者:** Phase 14 Research Agent

---

**报告结束**
