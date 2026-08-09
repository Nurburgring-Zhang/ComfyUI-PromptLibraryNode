# -*- coding: utf-8 -*-
"""
Phase 36.6 v5e: 修复 5 个 MEGA 工作流 (KSampler/CLIPTextEncode/UNETLoader/CLIPLoader/VAELoader/EmptyLatentImage/VAEDecode/PreviewImage)

修复内容:
1. Bug 3: KSampler widgets_values 7 个 (加 control_after_generate = 'random')
2. Bug 4: input slot name 用英文小写 (model/positive/negative/latent_image, text/clip, ckpt_name/unet_name/clip_name/vae_name, samples/images/vae)
3. 同时 widgets_values 中的字段名修正 (control_after_generate 等)

INPUT_TYPES 真实字段名 (来自 ComfyUI master):
  KSampler: required: model(MODEL), seed(INT), steps(INT), cfg(FLOAT), sampler_name(COMBO), scheduler(COMBO), positive(CONDITIONING), negative(CONDITIONING), latent_image(LATENT), denoise(FLOAT)
            widgets: [seed, control_after_generate, steps, cfg, sampler_name, scheduler, denoise]  (7 个)
            inputs: [model, positive, negative, latent_image]  (4 个)
  CLIPTextEncode: required: text(STRING), clip(CLIP)
                  widgets: [text]  (1 个)
                  inputs: [clip]  (1 个)
  UNETLoader: required: unet_name(COMBO), weight_dtype(COMBO)
              widgets: [unet_name, weight_dtype]  (2 个)
              inputs: []  (0 个)
  CLIPLoader: required: clip_name(COMBO), type(COMBO), device(COMBO)
              widgets: [clip_name, type, device]  (3 个)
              inputs: []  (0 个)
  VAELoader: required: vae_name(COMBO)
             widgets: [vae_name]  (1 个)
             inputs: []  (0 个)
  EmptyLatentImage: required: width(INT), height(INT), batch_size(INT)
                    widgets: [width, height, batch_size]  (3 个)
                    inputs: []  (0 个)
  VAEDecode: required: samples(LATENT), vae(VAE)
             widgets: []  (0 个)
             inputs: [samples, vae]  (2 个)
  PreviewImage: required: images(IMAGE)
                widgets: []  (0 个)
                inputs: [images]  (1 个)
"""
import json
from pathlib import Path

ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode\workflows")

# Phase 36.6 v5f: 中英对照表 (来自 AIGODLIKE 汉化插件 + ComfyUI 默认 i18n)
# 修复 "UNKNOWN" bug: ComfyUI 加载 LiteGraph 时用 label 字段显示中文 slot 名
# 缺失 label → fallback t(name) → fallback "UNKNOWN"
LABEL_ZH = {
    # KSampler
    "model": "模型", "positive": "正面条件", "negative": "负面条件",
    "latent_image": "潜空间图像",
    "seed": "随机种", "control_after_generate": "生成后控制",
    "steps": "步数", "cfg": "CFG", "sampler_name": "采样器名称",
    "scheduler": "调度器", "denoise": "降噪",
    # CLIPTextEncode
    "clip": "CLIP", "text": "文本",
    # UNETLoader
    "unet_name": "UNet 名称", "weight_dtype": "权重类型",
    # CLIPLoader
    "clip_name": "CLIP 名称", "type": "类型", "device": "设备",
    # VAELoader
    "vae_name": "VAE 名称",
    # EmptyLatentImage
    "width": "宽度", "height": "高度", "batch_size": "批量大小",
    # VAEDecode
    "samples": "潜空间", "vae": "VAE",
    # PreviewImage / SaveImage
    "images": "图像", "filename_prefix": "文件名前缀",
    # EmptySD3LatentImage (新)
    "image": "图像",
    # VideoCombine (VHS)
    "frame_rate": "帧率", "loop_count": "循环次数", "format": "格式",
    "pingpong": "乒乓", "save_output": "保存输出", "video": "视频",
    "audio": "音频", "movie": "视频", "duration": "时长",
    # 通用
    "mask": "遮罩", "noise_mask": "噪声遮罩",
    "strength": "强度", "weight": "权重",
    "batch_count": "批量数", "noise": "噪声",
    "start_at_step": "起始步", "end_at_step": "结束步",
    "return_with_left": "左对齐", "return_with_right": "右对齐",
    "start_percent": "起始百分比", "end_percent": "结束百分比",
    "lora_name": "LoRA 名称", "strength_model": "模型强度", "strength_clip": "CLIP 强度",
    "upscale_method": "放大方法", "scale_by": "缩放系数", "crop": "裁剪",
    "tile_size": "瓦片大小", "overlap": "重叠", "upscale_model": "放大模型",
    "image1": "图像 1", "image2": "图像 2",
}


# 节点规范
NATIVE_SPEC = {
    "KSampler": {
        "input_slots": [
            {"name": "model", "type": "MODEL"},
            {"name": "positive", "type": "CONDITIONING"},
            {"name": "negative", "type": "CONDITIONING"},
            {"name": "latent_image", "type": "LATENT"},
        ],
        "widgets": ["seed", "control_after_generate", "steps", "cfg",
                    "sampler_name", "scheduler", "denoise"],
        "widget_defaults": [42, "random", 20, 7.5, "euler", "simple", 1.0],
    },
    "CLIPTextEncode": {
        "input_slots": [{"name": "clip", "type": "CLIP"}],
        "widgets": ["text"],
        "widget_defaults": [""],
    },
    "UNETLoader": {
        "input_slots": [],
        "widgets": ["unet_name", "weight_dtype"],
        "widget_defaults": ["", "default"],
    },
    "CLIPLoader": {
        "input_slots": [],
        "widgets": ["clip_name", "type", "device"],
        "widget_defaults": ["", "stable_diffusion", "default"],
    },
    "VAELoader": {
        "input_slots": [],
        "widgets": ["vae_name"],
        "widget_defaults": [""],
    },
    "EmptyLatentImage": {
        "input_slots": [],
        "widgets": ["width", "height", "batch_size"],
        "widget_defaults": [512, 512, 1],
    },
    "VAEDecode": {
        "input_slots": [
            {"name": "samples", "type": "LATENT"},
            {"name": "vae", "type": "VAE"},
        ],
        "widgets": [],
        "widget_defaults": [],
    },
    "PreviewImage": {
        "input_slots": [{"name": "images", "type": "IMAGE"}],
        "widgets": [],
        "widget_defaults": [],
    },
}


def fix_node(node):
    """修复单个节点: 修正 inputs name, widgets_values 数量和顺序"""
    ntype = node.get("type")
    if ntype not in NATIVE_SPEC:
        return  # 自定义节点不处理

    spec = NATIVE_SPEC[ntype]
    n_inputs = len(spec["input_slots"])
    n_widgets = len(spec["widgets"])

    # 保留 node 的现有 inputs links (target_id+slot 关系)
    old_inputs = node.get("inputs", [])
    # 修复 inputs: 强制按 spec 顺序, name 用英文小写, label 用中文
    new_inputs = []
    for i, slot_spec in enumerate(spec["input_slots"]):
        zh_label = LABEL_ZH.get(slot_spec["name"], slot_spec["name"])
        if i < len(old_inputs):
            old = old_inputs[i]
            new_inputs.append({
                "name": slot_spec["name"],
                "type": slot_spec["type"],
                "link": old.get("link"),
                "label": zh_label,  # ComfyUI 用 label 显示中文
                "slot_index": i,
            })
        else:
            new_inputs.append({
                "name": slot_spec["name"],
                "type": slot_spec["type"],
                "link": None,
                "label": zh_label,
                "slot_index": i,
            })
    node["inputs"] = new_inputs

    # 修复 widgets_values: 补齐到 n_widgets 个, 保留已有值
    old_wvs = node.get("widgets_values", [])
    new_wvs = []
    for i, default in enumerate(spec["widget_defaults"]):
        if i < len(old_wvs):
            new_wvs.append(old_wvs[i])
        else:
            new_wvs.append(default)
    if ntype == "KSampler" and len(old_wvs) < 7:
        if len(old_wvs) == 6:
            new_wvs = [old_wvs[0], "random", old_wvs[1], old_wvs[2],
                       old_wvs[3], old_wvs[4], old_wvs[5]]
        else:
            new_wvs = list(spec["widget_defaults"])
    node["widgets_values"] = new_wvs

    # 修复 outputs: 加中文 label 字段
    for i, out in enumerate(node.get("outputs", [])):
        if "name" in out:
            out["label"] = LABEL_ZH.get(out["name"], out["name"])
            if "slot_index" not in out:
                out["slot_index"] = i


def fix_workflow(path):
    with open(path, "r", encoding="utf-8") as f:
        wf = json.load(f)
    fixed = 0
    for node in wf.get("nodes", []):
        if node.get("type") in NATIVE_SPEC:
            fix_node(node)
            fixed += 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)
    return fixed


def main():
    print("=" * 70)
    print("Phase 36.6 v5e: 修复 5 个 MEGA 工作流 (内置节点规范)")
    print("=" * 70)
    total = 0
    for wf_path in sorted(ROOT.glob("MEGA_*.json")):
        n = fix_workflow(wf_path)
        total += n
        print("  {}: 修复 {} 个内置节点".format(wf_path.name, n))
    print()
    print("=" * 70)
    print("修复完成: 共 {} 个内置节点".format(total))
    print("=" * 70)


if __name__ == "__main__":
    main()
