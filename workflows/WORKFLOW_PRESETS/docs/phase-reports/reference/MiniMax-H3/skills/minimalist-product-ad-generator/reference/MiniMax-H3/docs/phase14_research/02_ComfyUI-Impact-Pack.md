# Project: ComfyUI-Impact-Pack

**URL:** https://github.com/ltdrdata/ComfyUI-Impact-Pack
**Author:** Dr.Lt.Data (ltdrdata)
**License:** GPL-3.0
**Stars:** 3.2k ⭐ | **Forks:** 391
**类别:** ComfyUI 资产/角色一致性管理 (方向 5, 同时跨方向 4/5)

---

## 项目简介

Custom nodes pack for ComfyUI. This custom node helps to conveniently enhance images through Detector, Detailer, Upscaler, Pipe, and more.

---

## 核心节点分类

### 1. Detector 检测器
- **BBOX (Bounding Box)** - 用 `bbox/face_yolov8m.pt` 等检测面部矩形区域
- **SAM (Segment Anything)** - 用 SAM 模型生成轮廓蒙版,结合 BBOX 精细化
- **SEGM (Segmentation)** - 用 `segm/person_yolov8n-seg.pt` 获得人体形状轮廓
- 模型路径: `ComfyUI/models/ultralytics/`
- SAM 模型: `sam_vit_h/l/b` (4b/1.16g/357M)

### 2. Detailer 细节增强器
- **FaceDetailer** - 自动检测面部,高分辨率修复面部细节
  - 输入: image, model, clip, vae, positive, negative, bbox_detector, sam_model_opt
  - 输出: image, cropped_refined, cropped_enhanced_alpha, mask, detailer_pipe, cent_images
  - 关键参数: guide_size, max_size, seed, steps, cfg, sampler_name, scheduler, denoise, feather, noise_mask, force_inpaint, bbox_threshold, bbox_dilation, bbox_crop_factor, sam_detection_hint, sam_dilation, sam_threshold, drop_size
- **MaskDetailer** - 基于掩码的局部精细处理
- **SEGSDetailer** - 区域分割处理

### 3. SEGS (Segmentation) 语义分割
- **MakeTileSEGS** - 分块处理超高分辨率图像
- **5-prompt-per-tile** - 图像不同分块应用不同提示词

### 4. Pipe 管道系统 (核心创新!)
- **ToBasicPipe / FromBasicPipe / FromBasicPipe_V2** - 整合 model/clip/vae/positive/negative 成一个 pipe
- **ToDetailerPipe / ToDetailerPipeSDXL** - Detailer 管道
- **BasicPipe->DetailerPipe** - 管道转换
- **Edit BasicPipe / Edit DetailerPipe** - 管道编辑

### 5. Wildcards 通配符
- 支持简单列表、权重选择、YAML 格式
- 路径: `wildcards/` 或 `custom_wildcards/`
- 例: prompt 写 `__animal__`,自动从 `animal.txt` 随机选

### 6. Image Sender/Receiver
- 跨工作流传输图片,无需直接连线
- `save_to_workflow` 选项将图片嵌入工作流 JSON

### 7. Hook 系统
- **PreviewDetailerHookProvider** - 细节处理钩子
- 间歇性噪声、迭代细化

### 8. DetailerForEach / Iterative Upscale
- PK_HOOK 高级迭代放大
- TwoSamplersForMask 高级迭代放大

---

## Interactive SAM Detector (Clipspace) - 创新功能

- 右键 "Open in SAM Detector" 打开 SAM 交互界面
- 左键添加蓝色正点(包含区域)
- 右键添加红色负点(排除区域)
- 通过 Detect 按钮生成 mask
- 调整 fidelity 滑块控制置信区域

---

## 版本与依赖

### 兼容性表
| Impact-Pack 版本 | 最低 ComfyUI 版本 | ultralytics 版本 |
|----------------|-----------------|------------------|
| v8.24+         | 0.3.63+         | >=8.0.200        |
| v8.0-v8.23     | 0.3.0+          | >=8.0.150        |
| v7.0-v7.6      | 2024.04.08+     | >=8.0.0          |
| v6.0 及以下     | 2023.10.08+     | >=7.0.0          |

### 架构演进
- V1-V3: 单体集成架构
- V4-V6: 插件化架构
- V7-V8: 微内核架构 + 延迟加载 + LRU 智能缓存

### 性能数据 (vs v7.2 vs v8.0)
| 场景 | V7.2 内存峰值 | V8.0 内存峰值 | 降低 |
|------|--------------|--------------|------|
| 基础检测 | 4.2GB | 1.8GB | 57.1% |
| 语义分割 | 6.5GB | 2.3GB | 64.6% |
| Wildcard 加载 | 3.1GB | 0.9GB | 71.0% |
| 多任务并发 | 8.7GB | 3.2GB | 63.2% |

---

## 与我们项目的关系

**类别: 强借鉴 (关键技术参考) + 互补**

### ⭐⭐⭐⭐⭐ Pipe 系统 (核心借鉴!)

Impact-Pack 的 **Pipe 系统** 是其最大创新:用一条线代替多条线(model/clip/vae/positive/negative),大幅减少工作流复杂度。

**我们的借鉴方向:**
- 我们的 25 个节点每个都重复要求 model/clip/vae 输入,可考虑封装成 **PromptPipe / StoryboardPipe**
- 减少用户连线负担,提升工作流可读性

### ⭐⭐⭐⭐⭐ Wildcards 系统 (高借鉴!)

**我们的借鉴方向:**
- 我们当前有 `modes_book.py` 等多个数据文件,可参考 Impact-Pack 的 YAML 格式 + 权重选择
- 在故事板中实现"角色库"、"场景库"、"导演风格库"的随机/权重调用
- 故事分镜中可使用 `__shot_type__` 通配符批量生成

### ⭐⭐⭐⭐ FaceDetailer (中借鉴)

- 我们没有"面部修复"功能
- 但在 **character_arc_pro.py / director_real_scripts.py** 中可考虑加入"角色面部一致性"输出

### ⭐⭐⭐ DetailerForEach / Iterative Upscale (中借鉴)

- 我们的 `script_body_pro.py` 输出的多镜头,可考虑"逐镜头增强"工作流
- 与 director_intent_pro 配合,每个意图一个独立 Detailer

### 互补关系
- Impact-Pack 是**通用基础设施** (检测/修复)
- 我们是**导演/编剧领域知识** (故事/分镜/导演风格)
- **可叠加使用**: 用户先在 ComfyUI 加 Impact-Pack,再加载我们的 director_storyboard_pro 节点

### 安全提示
- ⚠️ 2024-12 发现 path traversal 漏洞 (CVE 相关),固定字段验证缺失可导致 RCE
- 影响模块: `modules/impact/impact_server.py`
- 我们的代码要注意: **用户输入路径必须做白名单校验**

