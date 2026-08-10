# -*- coding: utf-8 -*-
"""UniversalDirectorPromptNode 真实 build() 测试"""
import sys, os
ROOT = r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode"
os.chdir(ROOT)
sys.path.insert(0, ROOT)

import importlib.util
spec = importlib.util.spec_from_file_location("pkg_init", os.path.join(ROOT, "__init__.py"))
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)

udp = pkg.NODE_CLASS_MAPPINGS['UniversalDirectorPromptNode']
print("FUNCTION:", udp.FUNCTION)

# 真实测试 6 个模型路由
import inspect
sig = inspect.signature(udp.convert_universal)
print("convert_universal params:", list(sig.parameters.keys()))

for model in ["H3", "Seedance 2.5", "Wan 2.6", "Sora 2", "Veo 3.1", "短剧平台 (抖音/快手/小红书)"]:
    print(f"\n--- 路由模型: {model} ---")
    try:
        # 必填参数 + 一些常见 optional
        result = udp().convert_universal(
            user_intent="父女厨房戏",
            target_model=model,
            scene="雨夜香港厨房",
            visual_style="Cinematic",
            director="王家卫",
            duration=5,
            aspect_ratio="16:9",
        )
        print(f"  result {len(result)} 项, max {max(len(str(r)) for r in result if r)} chars")
        for i, r in enumerate(result):
            if r:
                rn = udp.RETURN_NAMES[i] if i < len(udp.RETURN_NAMES) else f"out_{i}"
                print(f"  [{rn}]: {str(r)[:120]}...")
    except Exception as e:
        print(f"  FAIL: {e}")
