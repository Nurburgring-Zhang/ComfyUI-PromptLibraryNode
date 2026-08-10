# -*- coding: utf-8 -*-
"""Phase 36.6 v5h: 数据完整性 + 反 AI 词表真实效果测试"""
import sys, os
ROOT = r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode"
os.chdir(ROOT)
sys.path.insert(0, ROOT)

import importlib.util
spec = importlib.util.spec_from_file_location("pkg_init", os.path.join(ROOT, "__init__.py"))
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)

# 1. prompt_builder 数据完整性
print("=" * 80)
print("1. prompt_builder 数据完整性")
print("=" * 80)
import prompt_builder
for name in dir(prompt_builder):
    if name.isupper() and not name.startswith('_'):
        obj = getattr(prompt_builder, name)
        if isinstance(obj, (list, tuple, set)):
            print(f"  {name}: {len(obj)} 项 ({type(obj).__name__})")
        elif isinstance(obj, dict):
            print(f"  {name}: {len(obj)} keys ({type(obj).__name__})")
        elif isinstance(obj, str):
            print(f"  {name}: {len(obj)} chars (str)")

# 2. asset_registry_data 数据完整性
print()
print("=" * 80)
print("2. asset_registry_data 数据完整性")
print("=" * 80)
import asset_registry_data as ard
for name in dir(ard):
    if name.isupper() and not name.startswith('_'):
        obj = getattr(ard, name)
        if isinstance(obj, (list, tuple, set)):
            print(f"  {name}: {len(obj)} 项")
        elif isinstance(obj, dict):
            print(f"  {name}: {len(obj)} keys")
        elif isinstance(obj, str):
            print(f"  {name}: {len(obj)} chars")

# 3. 反 AI 词表真实效果
print()
print("=" * 80)
print("3. 反 AI 词表真实效果测试")
print("=" * 80)
import anti_ai_vocab
test_prompts = [
    "他在那里, 瞳孔地震, 突然倒吸一口凉气",
    "美得让人窒息, 完美无瑕, 极致惊艳",
    "a beautiful girl with perfect skin, stunning, masterpiece, best quality, 4k, ultra detailed",
    "主角站在那里, 身上有 5G 信号灯, 手上握着一部 iPhone 15 Pro Max",
]

for prompt in test_prompts:
    print(f"\n原始: {prompt}")
    try:
        cleaned = anti_ai_vocab.clean_anti_ai_text(prompt)
        print(f"清理: {cleaned}")
    except Exception as e:
        print(f"FAIL: {e}")

# 4. 真实多模态: H3 输出能否被 Wan/Seedance/Sora 等模型接受
print()
print("=" * 80)
print("4. H3 多模态模式选择 (5 模式)")
print("=" * 80)
node = pkg.NODE_CLASS_MAPPINGS['H3ContextIRNode']
for mode_inputs in [
    {"has_first_frame": False, "has_last_frame": False, "has_refs": False},  # T2VA
    {"has_first_frame": True, "has_last_frame": False, "has_refs": False},   # I2VA
    {"has_first_frame": True, "has_last_frame": True, "has_refs": False},    # FL2VA
    {"has_first_frame": False, "has_last_frame": True, "has_refs": False},   # L2VA
    {"has_first_frame": False, "has_last_frame": False, "has_refs": True},   # Ref2VA
]:
    result = node().convert_to_h3(
        user_intent="测试", director="王家卫", scene="测试场景",
        duration=5, visual_style="Cinematic", aspect_ratio="16:9",
        target_language="English", dialogue="", non_diegetic_music="",
        emotion="情感冲击", intent="营造情感",
        **mode_inputs
    )
    print(f"  {mode_inputs} -> mode: {result[0]}")

# 5. UniversalDirectorPromptNode 12 个 output
print()
print("=" * 80)
print("5. UniversalDirectorPromptNode 6 模型路由")
print("=" * 80)
udp = pkg.NODE_CLASS_MAPPINGS['UniversalDirectorPromptNode']
print(f"  RETURN_TYPES: {udp.RETURN_TYPES}")
print(f"  RETURN_NAMES: {udp.RETURN_NAMES}")
result = udp().build(
    目标模型="H3",
    场景描述="测试场景",
    导演风格="王家卫",
    时长=5,
    分辨率="16:9",
    模型偏好="电影感",
    关键道具="霓虹灯",
    服装描述="皮夹克",
    角色名="主角",
    节奏="慢",
    情感="怀旧",
    动作="走",
    音景="夜雨",
)
print(f"  build() 输出 {len(result)} 项, 最长 {max(len(str(r)) for r in result if r)} chars")
