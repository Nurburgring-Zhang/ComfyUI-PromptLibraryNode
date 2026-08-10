# -*- coding: utf-8 -*-
"""H3ContextIRNode 真实测试"""
import sys
sys.path.insert(0, r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
from h3_context_ir_node import H3ContextIRNode

cls = H3ContextIRNode()
it = cls.INPUT_TYPES()
print("INPUT_TYPES required:", len(it.get("required", {})))
print("INPUT_TYPES optional:", len(it.get("optional", {})))
rt = cls.RETURN_TYPES
rn = cls.RETURN_NAMES
print("RETURN_TYPES:", rt)
print("RETURN_NAMES:", rn)

# 真实测试 build()
test_inputs = {
    "user_intent": "T2VA 父女厨房戏",
    "has_first_frame": False,
    "has_last_frame": False,
    "has_refs": False,
    "reference_assets": "霓虹灯厨房",
    "director": "王家卫",
    "scene": "父女厨房戏",
    "duration": 5,
    "visual_style": "Cinematic",
    "aspect_ratio": "16:9",
    "target_language": "English",
    "dialogue": "",
    "non_diegetic_music": "",
    "emotion": "情感冲击",
    "intent": "营造情感",
}
print()
print("=== 真实 build() 输出 ===")
try:
    func_name = cls.FUNCTION
    print("FUNCTION:", func_name)
    instance = cls()
    print("instance type:", type(instance).__name__)
    print("hasattr convert_to_h3:", hasattr(instance, 'convert_to_h3'))
    print("convert_to_h3 type:", type(getattr(instance, 'convert_to_h3', None)))
    result = instance.convert_to_h3(**test_inputs)
    print("result 数:", len(result) if isinstance(result, tuple) else 1)
    for i, r in enumerate(result):
        if r:
            print(f"\n[output {i}] ({type(r).__name__}, {len(str(r))} chars):")
            print(str(r)[:300])
except Exception as e:
    import traceback
    print(f"FAIL: {e}")
    traceback.print_exc()
