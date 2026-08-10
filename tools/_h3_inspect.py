# -*- coding: utf-8 -*-
import sys, os
ROOT = r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode"
os.chdir(ROOT)
sys.path.insert(0, ROOT)
# 用文件名 import 而不是 __init__
import importlib.util
spec = importlib.util.spec_from_file_location("pkg_init", os.path.join(ROOT, "__init__.py"))
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)
NODE_MAP = pkg.NODE_CLASS_MAPPINGS
H3NODE = NODE_MAP['H3ContextIRNode']
print("NODE_MAP type:", type(H3NODE))
print("is class:", isinstance(H3NODE, type))
print("is callable:", callable(H3NODE))
print("has convert_to_h3:", hasattr(H3NODE, 'convert_to_h3'))

# 真实测试 build
result = H3NODE().convert_to_h3(
    user_intent="T2VA 父女厨房戏",
    has_first_frame=False, has_last_frame=False, has_refs=False,
    reference_assets="霓虹灯厨房", director="王家卫", scene="父女厨房戏",
    duration=5, visual_style="Cinematic", aspect_ratio="16:9",
    target_language="English", dialogue="", non_diegetic_music="",
    emotion="情感冲击", intent="营造情感"
)
print("result 数:", len(result))
for i, r in enumerate(result):
    if r:
        print(f"[output {i}] ({type(r).__name__}, {len(str(r))} chars): {str(r)[:100]}")

