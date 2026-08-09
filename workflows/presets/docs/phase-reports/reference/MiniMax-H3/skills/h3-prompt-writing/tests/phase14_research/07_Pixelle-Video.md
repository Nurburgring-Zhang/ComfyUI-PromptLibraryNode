# Project: Pixelle-Video

**URL:** https://gitcode.com/gh_mirrors/pi/Pixelle-Video
**Author:** Open Source Contributors
**License:** open source
**类别:** ComfyUI 短剧/分镜/AI视频工作流 (方向 2)

---

## 项目简介

Pixelle-Video 是一款 AI 全自动短视频引擎,基于 ComfyUI 架构实现了原子能力的灵活组合,让用户可以轻松定制从图像生成到视频合成的完整流程。

---

## 核心架构优势

基于 ComfyUI 架构的灵活扩展性,通过自定义工作流,你可以:

1. **替换生图模型** - 为 FLUX、SD3.5 等最新模型
2. **整合第三方服务** - 整合 ChatTTS 等第三方语音合成服务
3. **实现特定风格** - 视频生成效果优化
4. **优化生成效率和资源占用**

---

## 自定义工作流前准备

### 环境要求
- 本地安装并运行 ComfyUI(推荐 NVIDIA 显卡 6GB+ 显存)
- Pixelle-Video 项目已正确配置 ComfyUI 连接
- 基础的 JSON 文件编辑能力

### 必要文件准备
- 从 ComfyUI 官方仓库克隆并安装 ComfyUI
- 下载所需的模型文件并放置在 ComfyUI 的 models 目录下
- 确保 Pixelle-Video 配置文件中已正确设置 ComfyUI 地址:
  ```yaml
  comfyui_url: "http://127.0.0.1:8188"
  ```

---

## 工作流文件结构

工作流文件存储在 `workflows/` 目录下,分为两个子目录:

| 目录 | 用途 |
|------|------|
| `runninghub/` | 适用于云端运行的工作流 |
| `selfhost/` | 适用于本地部署的工作流 |

### 工作流文件命名示例
- `image_flux.json` - 使用 FLUX 模型生成图像
- `tts_edge.json` - 使用 Edge TTS 服务的语音合成
- `video_wan2.2.json` - 基于 Wan2.2 模型的视频生成

---

## 自定义工作流基本步骤

### 1. 设计工作流
在本地 ComfyUI 编辑器中设计你的工作流:
- 添加所需节点(加载模型、图像生成、视频合成等)
- 连接节点形成完整的处理流程
- 调整参数并测试运行效果
- 导出工作流为 JSON 文件

### 2. 工作流文件规范
自定义工作流需遵循以下规范:
- 确保工作流在本地 ComfyUI 中能正常运行
- 使用**相对路径引用资源文件**
- 关键参数使用**占位符**以便 Pixelle-Video 动态替换
- 文件名建议使用功能前缀(如 `image_`、`tts_`、`video_`)

### 3. 集成到 Pixelle-Video
将自定义的工作流 JSON 文件复制到 `workflows/` 目录下,然后在配置文件中指定:
```yaml
workflow:
  image: "workflows/selfhost/your_custom_image_workflow.json"
  video: "workflows/selfhost/your_custom_video_workflow.json"
```

---

## 高级自定义技巧

### 参数动态调整 - 关键创新!

通过在工作流 JSON 中使用特殊占位符,实现参数的动态调整:

```json
"inputs": {
  "prompt": "{{prompt}}",
  "width": "{{width}}",
  "height": "{{height}}"
}
```

这些占位符会在运行时被 Pixelle-Video 传递的实际参数替换。

### 工作流组合使用
- 使用 `image_flux.json` 生成高质量图像
- 使用 `video_wan2.2.json` 将图像合成为视频
- 使用 `tts_edge.json` 为视频添加语音解说

### 性能优化
- 本地部署:优先使用 `selfhost/` 目录下的工作流
- 调整模型精度和分辨率平衡生成质量和速度
- 合理设置缓存参数减少重复计算

---

## 常见问题解决

### ComfyUI 连接失败
- 确认 ComfyUI 服务正在运行
- 检查配置文件中的 `comfyui_url` 是否正确
- 在浏览器中访问 ComfyUI 地址测试连接

### 工作流运行出错
- 检查所需模型是否已正确下载
- 在 ComfyUI 中手动测试工作流定位问题
- 查看 Pixelle-Video 日志获取详细错误信息

---

## 核心借鉴点

### ⭐⭐⭐⭐⭐ 占位符动态替换 (核心创新!)

这是 Pixelle-Video 最重要的设计:
- 工作流 JSON 中使用 `{{prompt}}`, `{{width}}`, `{{height}}` 占位符
- 运行时由系统替换为实际值

**借鉴意义:**
- 我们当前 `director_storyboard_pro.py` 输出的分镜提示词需要用户**手动复制到 ComfyUI 工作流**
- 应学习这种**占位符注入** 模式:
  - 我们生成 `{"shot1_prompt": "...", "shot1_seed": 42, "shot1_size": "1920x1080"}` JSON
  - 工作流 JSON 模板中 `{{shot1_prompt}}` 自动填充
  - 一键生成 25 段分镜工作流

### ⭐⭐⭐⭐ 原子能力组合

- "image" + "video" + "tts" 三个工作流可组合
- 我们可借鉴: `director_storyboard_pro` + `vertical_short_drama_pro` + `mv_pro` 组合

### ⭐⭐⭐ 云端 + 本地双部署

- `runninghub/` (云端) + `selfhost/` (本地) 分离
- 我们未来如果做云端,可参考

---

## 与我们项目的关系

**类别: 强借鉴 (占位符机制) + 互补 (AI 视频执行层)**

### 直接给我们的改进方向

1. **`director_storyboard_pro.py` 重大改造**:
   - 增加"导出 ComfyUI 工作流 JSON" 按钮
   - 使用 `{{shot_N_prompt}}` 占位符模式
   - 用户可一键注入到 ComfyUI 节点图

2. **新节点 `workflow_template_pro.py`**:
   - 读取 Pixelle-Video 风格的工作流 JSON
   - 替换占位符为实际值
   - 输出最终可执行的工作流文件

3. **`production_pipeline_v3.py` 增强**:
   - 支持 "image → video → tts" 三阶段流水线
   - 对应我们的 `costume_prop_set_pro.py` → `vertical_short_drama_pro.py` → `mv_pro.py`

