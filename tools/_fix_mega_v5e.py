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
    # 修复 inputs: 强制按 spec 顺序, name 用英文小写
    new_inputs = []
    for i, slot_spec in enumerate(spec["input_slots"]):
        if i < len(old_inputs):
            old = old_inputs[i]
            new_inputs.append({
                "name": slot_spec["name"],
                "type": slot_spec["type"],
                "link": old.get("link"),  # 保留 link 关系
            })
        else:
            new_inputs.append({
                "name": slot_spec["name"],
                "type": slot_spec["type"],
                "link": None,
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
    # 如果 KSampler 漏了 control_after_generate, 强制插入
    if ntype == "KSampler" and len(old_wvs) < 7:
        # 假设老顺序是 [seed, steps, cfg, sampler_name, scheduler, denoise] (6 个)
        # 调整为 [seed, control_after_generate, steps, cfg, sampler_name, scheduler, denoise]
        if len(old_wvs) == 6:
            new_wvs = [old_wvs[0], "random", old_wvs[1], old_wvs[2],
                       old_wvs[3], old_wvs[4], old_wvs[5]]
        else:
            new_wvs = list(spec["widget_defaults"])
    node["widgets_values"] = new_wvs


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
