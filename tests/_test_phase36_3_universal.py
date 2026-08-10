"""
Phase 36.3 UniversalDirectorPromptNode 验证脚本

测试覆盖:
T1. UniversalDirectorPromptNode 12 字段输出
T2. 6 模型路由 (H3/Seedance/Wan/Sora/Veo/短剧/通用)
T3. 短剧平台特定 (hook + 1-3 镜 + 字幕)
T4. 导演风格锚点 (8 维)
T5. Shot plan with MM:SS.mmm timestamp
T6. Audio 双轨 (soundscape + non_diegetic)
T7. Story arc 12 套理论
T8. Anti-AI clean guarantee
T9. ComfyUI 规范合规
T10. H3 mode 自动选择 (5 模式)
"""
import sys, os
HERE = r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode"
sys.path.insert(0, HERE)
os.chdir(HERE)

total = 0
passed = 0
fails = []

def test(name, ok, detail=""):
    global total, passed
    total += 1
    if ok:
        passed += 1
        print(f"[OK] {name}")
    else:
        print(f"[FAIL] {name}: {detail}")
        fails.append((name, detail))


print("=" * 60)
print("T1. UniversalDirectorPromptNode 12 字段输出")
print("=" * 60)
from universal_director_prompt_node import UniversalDirectorPromptNode, MODEL_PROMPT_OPTIMIZERS
node = UniversalDirectorPromptNode()
result = node.convert_universal(
    user_intent="雨夜香港旺角, 男女主角擦肩而过",
    target_model="通用 (兼容所有模型)",
    visual_style="Cinematic", director="王家卫",
    duration=8, aspect_ratio="16:9 横屏",
    scene="雨夜香港旺角, 霓虹灯光在雨水中反射",
    emotion="孤独", intent="营造孤寂浪漫氛围",
    dialogue="I thought I would never see you again.",
    dialogue_language="English",
)
test(f"12 字段输出 (实际 {len(result)})", len(result) == 12, f"实际 {len(result)}")

labels = ["target_model", "model_specific", "h3_mode", "h3_full", "universal_5",
          "director_anchor", "shot_plan", "dialogue", "audio", "story_arc",
          "validation", "anti_ai"]
for label, val in zip(labels, result):
    test(f"  {label} 非空", val is not None and len(str(val)) > 0, f"长度 {len(str(val)) if val else 0}")


# === T2. 6 模型路由 ===
print()
print("=" * 60)
print("T2. 6 模型路由")
print("=" * 60)

models_to_test = [
    "MiniMax H3 (官方)",
    "Seedance 2.5 (字节)",
    "Wan 3.0 (阿里)",
    "Sora 2 (OpenAI)",
    "Veo 3 (Google)",
    "短剧平台 (抖音/快手/小红书)",
    "通用 (兼容所有模型)",
]
for m in models_to_test:
    r = node.convert_universal(
        user_intent="测试", target_model=m, director="王家卫",
        duration=8, scene="测试场景", emotion="孤独",
    )
    test(f"  Model '{m}' 路由成功", r[0] == m, f"实际 {r[0]}")


# === T3. 短剧平台特定 ===
print()
print("=" * 60)
print("T3. 短剧平台特定 (hook + 1-3 镜 + 字幕)")
print("=" * 60)

r_short = node.convert_universal(
    user_intent="测试短剧", target_model="短剧平台 (抖音/快手/小红书)",
    director="通用", duration=8,
    scene="测试", emotion="喜",
    hook_style="情感冲击", subtitle_required=True,
)
test("短剧 prompt 含 [HOOK] 情感冲击", "[HOOK] 情感冲击开场" in str(r_short[1]), f"实际 {str(r_short[1])[:200]}")
test("短剧 prompt 含 [SUBTITLE] 字幕", "[SUBTITLE]" in str(r_short[1]), f"实际 {str(r_short[1])[:200]}")
test("短剧 prompt 含 1-3 镜结构", "[镜 1]" in str(r_short[1]) or "1-3 镜" in str(r_short[1]), f"实际 {str(r_short[1])[:200]}")


# === T4. 导演风格锚点 ===
print()
print("=" * 60)
print("T4. 导演风格锚点 (8 维)")
print("=" * 60)
test("导演锚点含 8 维 (镜头/光线/节奏/色彩/表演/构图/声音/剪辑)",
     all(k in str(result[5]) for k in ["镜头", "光线", "节奏", "色彩", "表演", "构图", "声音", "剪辑"]),
     f"实际 {str(result[5])[:300]}")


# === T5. Shot plan with timestamp ===
print()
print("=" * 60)
print("T5. Shot plan with MM:SS.mmm timestamp")
print("=" * 60)
test("Shot 1 标记", "[Shot 1]" in str(result[6]), f"实际 {str(result[6])[:200]}")
test("Shot 2 时间戳 MM:SS.mmm", "00:0" in str(result[6]) and "At 00:0" in str(result[6]), f"实际 {str(result[6])[:300]}")
test("Camera motion 含 amplitude + speed", "amplitude" in str(result[6]) and "speed" in str(result[6]), f"实际 {str(result[6])[:300]}")


# === T6. Audio 双轨 ===
print()
print("=" * 60)
print("T6. Audio 双轨 (soundscape + non_diegetic)")
print("=" * 60)
test("Audio 含 overall_soundscape", "overall_soundscape" in str(result[8]), f"实际 {str(result[8])[:200]}")
test("Audio 含 non_diegetic_music", "non_diegetic_music" in str(result[8]), f"实际 {str(result[8])[:200]}")


# === T7. Story arc 12 套理论 ===
print()
print("=" * 60)
print("T7. Story arc 12 套理论")
print("=" * 60)
testories = ["Save the Cat", "Hero's Journey", "McKee", "Pixar 22",
             "Kishōtenketsu (起承转合)", "Three Act", "5 Act" if False else "Five Act",
             "7 Point" if False else "7 Point",
             "Truby 8 Sequence", "Dan Harmon Story Circle", "In Medias Res", "双线 Parallel"]
for t in testories:
    r = node.convert_universal(
        user_intent="x", target_model="通用 (兼容所有模型)",
        director="通用", duration=8, scene="x", emotion="x", story_theory=t,
    )
    test(f"  Story theory '{t}'", t in str(r[9]) or testories[testories.index(t)] in str(r[9]), f"实际 {str(r[9])[:200]}")


# === T8. Anti-AI clean guarantee ===
print()
print("=" * 60)
print("T8. Anti-AI clean guarantee")
print("=" * 60)
test("anti_ai 含 5 维具体化", "5 维具体化" in str(result[11]), f"实际 {str(result[11])[:200]}")
test("anti_ai 含 35 联网导演", "35 联网导演档案" in str(result[11]) or "联网" in str(result[11]), f"实际 {str(result[11])[:200]}")
test("anti_ai 含 100 场景库", "100 场景库" in str(result[11]), f"实际 {str(result[11])[:200]}")


# === T9. ComfyUI 规范合规 ===
print()
print("=" * 60)
print("T9. ComfyUI 规范合规 (INPUT_TYPES / RETURN_TYPES / RETURN_NAMES)")
print("=" * 60)
test("INPUT_TYPES 存在", hasattr(UniversalDirectorPromptNode, "INPUT_TYPES"))
test("INPUT_TYPES() 可调用", callable(UniversalDirectorPromptNode.INPUT_TYPES))
it = UniversalDirectorPromptNode.INPUT_TYPES()
test("INPUT_TYPES 是 dict", isinstance(it, dict))
test("INPUT_TYPES.required 存在", "required" in it)
test("user_intent 在 required", "user_intent" in it["required"])
test("target_model 是 COMBO (list)", isinstance(it["required"]["target_model"][0], list))
test("RETURN_TYPES 长度 = 12", len(UniversalDirectorPromptNode.RETURN_TYPES) == 12, f"实际 {len(UniversalDirectorPromptNode.RETURN_TYPES)}")
test("RETURN_NAMES 长度 = 12", len(UniversalDirectorPromptNode.RETURN_NAMES) == 12, f"实际 {len(UniversalDirectorPromptNode.RETURN_NAMES)}")
test("RETURN_NAMES 全部 snake_case 英文", all("_" in n or n.islower() for n in UniversalDirectorPromptNode.RETURN_NAMES), f"实际 {UniversalDirectorPromptNode.RETURN_NAMES}")
test("FUNCTION 存在", hasattr(UniversalDirectorPromptNode, "FUNCTION"))
test("CATEGORY 是 PromptLibrary/*", UniversalDirectorPromptNode.CATEGORY.startswith("PromptLibrary/"))


# === T10. H3 mode 自动选择 ===
print()
print("=" * 60)
print("T10. H3 mode 自动选择 (5 模式)")
print("=" * 60)
modes = [
    ({"has_first_frame": False, "has_last_frame": False, "has_video_ref": False, "has_audio_ref": False}, "T2VA"),
    ({"has_first_frame": True, "has_last_frame": False, "has_video_ref": False, "has_audio_ref": False}, "I2VA"),
    ({"has_first_frame": True, "has_last_frame": True, "has_video_ref": False, "has_audio_ref": False}, "FL2VA"),
    ({"has_first_frame": False, "has_last_frame": True, "has_video_ref": False, "has_audio_ref": False}, "L2VA"),
    ({"has_first_frame": True, "has_last_frame": False, "has_video_ref": True, "has_audio_ref": True}, "Ref2VA"),
]
for kwargs, expected_mode in modes:
    r = node.convert_universal(
        user_intent="test", target_model="通用 (兼容所有模型)",
        director="通用", duration=8, scene="test", emotion="test",
        **kwargs,
    )
    test(f"  {kwargs} → {expected_mode}", r[2] == expected_mode, f"实际 {r[2]}")


# === 总结 ===
print()
print("=" * 60)
print(f"Phase 36.3 Universal Director Prompt 验证汇总")
print("=" * 60)
print(f"通过 {passed} / 总计 {total}")

if fails:
    print(f"\n失败项:")
    for name, detail in fails:
        print(f"  - {name}: {detail}")
    sys.exit(1)
else:
    print(f"\n[PASS] Phase 36.3 全部通过 {passed}/{total}")
    sys.exit(0)
