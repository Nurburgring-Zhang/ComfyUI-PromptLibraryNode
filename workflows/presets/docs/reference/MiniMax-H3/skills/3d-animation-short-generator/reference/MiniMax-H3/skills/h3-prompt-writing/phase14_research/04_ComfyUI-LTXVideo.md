# Project: ComfyUI-LTXVideo

**URL:** https://gitcode.com/GitHub_Trending/co/ComfyUI-LTXVideo
**Author:** Lightricks 团队官方
**License:** open source (具体许可证参考官方仓库)
**类别:** ComfyUI 短剧/分镜/AI视频工作流 (方向 2)

---

## 项目简介

ComfyUI-LTXVideo 是一个强大的 AI 视频生成工具包,专门为 LTX-2 视频生成模型提供 ComfyUI 支持。这个开源项目让用户能够在 ComfyUI 中轻松创建高质量的 AI 视频内容,从文本描述、静态图像到现有视频的增强处理,都能通过直观的节点工作流实现。无论你是 AI 视频生成的新手还是经验丰富的创作者,LTXVideo 都能提供专业级的视频生成体验。

---

## 核心能力

### 1. 三种生成模式

| 模式 | 最佳用途 | 关键优势 | 推荐模型 |
|------|---------|---------|---------|
| **文本到视频 (T2V)** | 创意内容创作 | 从零开始生成视频 | LTX-2.3 蒸馏模型 |
| **图像到视频 (I2V)** | 动态图像增强 | 保持原图风格 | LTX-2.3 完整模型 |
| **视频到视频 (V2V)** | 视频质量提升 | 分辨率/帧率提升 | 联合 IC-LoRA 模型 |

### 2. 注意力机制控制

通过注意力控制节点,你可以精确指导模型关注视频中的特定区域:
- focus_regions - 多焦点区域定义
- focus_strength - 关注强度 (1.2)
- blur_radius - 过渡平滑度
- keyframes - 关键帧时间点

### 3. IC-LoRA 联合控制 (杀手锏!)

联合 IC-LoRA 是 LTXVideo 的核心创新,允许同时使用多种控制条件:
- depth_map - 深度图控制
- edge_map - 边缘图控制
- pose_map - 姿态图控制
- control_weights - 控制权重数组
- downsample_factor - 下采样因子

### 4. 多模态生成引擎

---

## 快速上手

### 硬件要求
- GPU: NVIDIA RTX 3090 或更高(24GB+ 显存)
- 内存: 32GB RAM
- 存储: 100GB+ 可用空间

### 模型下载清单
```
ComfyUI/models/
├── checkpoints/
│   ├── ltx-2.3-22b-distilled-1.1.safetensors
│   └── ltx-2.3-22b-dev.safetensors
├── latent_upscale_models/
│   ├── ltx-2.3-spatial-upscaler-x2-1.1.safetensors
│   └── ltx-2.3-temporal-upscaler-x2-1.0.safetensors
├── loras/
│   ├── ltx-2.3-22b-distilled-lora-384-1.1.safetensors
│   └── ltx-2.3-22b-ic-lora-union-control-ref0.5.safetensors
└── text_encoders/
    └── gemma-3-12b-it-qat-q4_0-unquantized/
```

### 最简单的入门方式
打开 ComfyUI 界面 → 点击"Load" → 导航到:
`custom_nodes/ComfyUI-LTXVideo/example_workflows/2.3/`
→ 选择 `LTX-2.3_T2V_I2V_Single_Stage_Distilled_Full.json`

---

## 应用场景

### 1. 社交媒体短视频
- 分辨率: 1080x1920 (竖屏)
- 时长: 10 秒
- 风格: cinematic

### 2. 教育内容动态演示
- 概念可视化 (clarity 0.9)
- 步骤动画
- 文本叠加 + 语音同步

### 3. 商业产品展示
- 360度旋转
- 特写细节
- 品牌色系强化
- Logo位置控制

---

## 性能优化

### 显存优化技巧
- **load_strategy="sequential"** - 顺序加载策略
- **unload_after_use=["text_encoder"]** - 使用后卸载
- **memory_threshold=0.8** - 显存使用阈值

### 速度配置对比

| 模式 | Steps | 分辨率 | 模型 | 时间 |
|------|------|--------|------|------|
| 快速预览 | 20 | 512x288 | 蒸馏 | 快 |
| 高质量 | 50 | 1920x1080 | 完整 | 慢 |

---

## 关键工作流模式

### T2V 基础配置
```python
prompt = "A beautiful sunset over the ocean with gentle waves"
negative_prompt = "blurry, distorted, low quality"
num_frames = 24  # 视频帧数
fps = 8
width = 1024
height = 576
guidance_scale = 7.5
```

### I2V 高级配置
```python
i2v_node = LTXImageToVideoNode(
    image_path="input_image.jpg",
    prompt="Add subtle camera movement and atmospheric effects",
    motion_strength=0.3,    # 运动强度控制
    temporal_consistency=0.8,  # 时间一致性
    style_preservation=0.9    # 风格保持度
)
```

### 自定义节点示例
```python
from .nodes_registry import comfy_node

@comfy_node
class CustomVideoEnhancerNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO",),
                "enhancement_type": (["sharpness", "contrast", "color"],),
                "strength": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0})
            }
        }
    RETURN_TYPES = ("VIDEO",)
    FUNCTION = "enhance_video"
```

---

## 与我们项目的关系

**类别: 互补 (AI 视频执行层) + 高借鉴 (工作流自动化)**

### ⭐⭐⭐⭐⭐ 工作流模板化 (核心借鉴!)

我们当前的分镜输出是文本,需要用户手动复制到 ComfyUI:
- 我们应借鉴其**example_workflows/ 模式** - 每个导演风格一个工作流 JSON
- 把我们的 `director_storyboard_pro.py` 输出**直接注入** 到 LTXVideo 的工作流

### ⭐⭐⭐⭐ 联合控制权重 (高借鉴!)

其 IC-LoRA 的 control_weights 数组设计很优雅:
- 我们可借鉴用于 `director_intent_pro.py` 的"多意图权重分配"
- 比如: "复仇" 0.4 + "救赎" 0.6 = 复合主题镜头

### ⭐⭐⭐⭐ 性能监控 (中借鉴)

其 PerformanceMonitor 类 (elapsed_time, frame_count, fps, gpu_usage, gpu_memory) 可集成到:
- 我们的 `production_pipeline_v3.py`
- 让用户看到 LLM 推理分镜的时间分布

### ⭐⭐⭐ 注意力控制 (低借鉴)

`focus_regions` 概念可借鉴到:
- 我们的 `costume_prop_set_pro.py` 中"特写镜头聚焦核心道具"

### 互补关系
- LTXVideo 是 **AI 视频生成引擎** (T2V/I2V/V2V)
- 我们是 **导演/编剧领域知识** (故事/分镜/导演意图)
- **未来集成路径**: 我们的 `script_body_pro.py` 输出的 25 段分镜 → 解析成 LTX-Video 工作流参数 → 调用 LTX 节点 → 输出视频

### 直接给我们的改进方向
1. **新节点 `video_ltx_bridge_pro.py`** - 桥接我们的文本分镜到 LTX-Video 工作流
2. **director_storyboard_pro.py** - 增加"输出 ComfyUI 工作流 JSON" 按钮,一键注入到 LTX-Video
3. **production_pipeline_v3.py** - 增加显存监控仪表板

