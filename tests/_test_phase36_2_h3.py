"""
Phase 36.2 MiniMax-H3 整合验证脚本

测试覆盖:
T1. H3 框架知识库加载
T2. H3ContextIRNode 5 模式选择
T3. H3ContextIRNode 8 字段输出
T4. DirectorSoulNode H3 段真实施
T5. 14+1 段 (14 原有 + H3 新增) 全部存在
T6. H3 camera 3D 维度 (motion + amplitude + speed)
T7. H3 reference labels 4 选
T8. H3 dialogue <d>[Language] 格式
T9. H3 retention markers (visible + audio)
T10. 5 维具体化 (era/location/brand/numbers/objects) 保留
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# === 全局计数器 ===
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


# === 1. 加载 H3 框架 ===
print("=" * 60)
print("T1. H3 框架知识库加载")
print("=" * 60)
try:
    from knowledge_base.h3_prompt_framework import (
        H3_MODES, H3_REF2VA_SECTIONS, CAMERA_MOTION_TYPES,
        RETENTION_MARKERS_VISIBLE, RETENTION_MARKERS_AUDIO,
        H3_REFERENCE_LABELS, H3_OFFICIAL_SKILLS_SUMMARY,
        select_h3_mode, render_camera_motion, render_h3_style_opening,
        render_h3_soundscape, render_h3_nondiegetic_music, render_h3_dialogue,
    )
    test("H3 框架知识库加载", True)
except Exception as e:
    test("H3 框架知识库加载", False, str(e))
    print("ABORT: H3 知识库加载失败, 后续测试跳过")
    sys.exit(1)


# === 2. H3 5 模式选择 ===
print()
print("=" * 60)
print("T2. H3ContextIRNode 5 模式选择")
print("=" * 60)
test("select_h3_mode() 默认 = T2VA", select_h3_mode() == "T2VA", f"实际 {select_h3_mode()}")
test("select_h3_mode(has_first_frame) = I2VA", select_h3_mode(has_first_frame=True) == "I2VA", f"实际 {select_h3_mode(has_first_frame=True)}")
test("select_h3_mode(first+last) = FL2VA", select_h3_mode(has_first_frame=True, has_last_frame=True) == "FL2VA", f"实际 {select_h3_mode(has_first_frame=True, has_last_frame=True)}")
test("select_h3_mode(last only) = L2VA", select_h3_mode(has_last_frame=True) == "L2VA", f"实际 {select_h3_mode(has_last_frame=True)}")
test("select_h3_mode(refs) = Ref2VA", select_h3_mode(has_refs=True) == "Ref2VA", f"实际 {select_h3_mode(has_refs=True)}")


# === 3. H3ContextIRNode 8 字段输出 ===
print()
print("=" * 60)
print("T3. H3ContextIRNode 8 字段输出")
print("=" * 60)
from h3_context_ir_node import H3ContextIRNode
node = H3ContextIRNode()
result = node.convert_to_h3(
    user_intent="一个雨夜香港巷子, 男女主角擦肩而过",
    has_first_frame=False, has_last_frame=False, has_refs=False,
    director="王家卫",
    scene="雨夜香港旺角巷子, 霓虹灯光在雨水中反射",
    duration=8, visual_style="Cinematic", aspect_ratio="16:9",
    target_language="English",
    dialogue="I thought I would never see you again.",
    non_diegetic_music="",
    emotion="孤独", intent="营造孤寂浪漫氛围",
)
labels = ["h3_mode", "instruction", "multimodal", "soundscape", "music", "full_prompt", "validation", "summary"]
test(f"8 字段输出数量 = 8", len(result) == 8, f"实际 {len(result)}")
# T2VA 模式下 instruction 应该是空字符串 (H3 标准, T2VA 无 Part One)
for label, val in zip(labels[1:], result[1:]):
    if label == "instruction":
        # T2VA 模式 instruction 允许为空
        test(f"  {label} 存在 (T2VA 允许空)", val is not None, f"长度 {len(str(val)) if val else 0}")
    else:
        test(f"  {label} 非空", val is not None and len(str(val)) > 0, f"长度 {len(str(val)) if val else 0}")

# I2VA 模式下 instruction 必须非空
result_i2va = node.convert_to_h3(
    user_intent="从首帧图展开, 雨夜香港巷子",
    has_first_frame=True, has_last_frame=False, has_refs=False,
    director="王家卫", scene="雨夜香港",
    duration=8, visual_style="Cinematic", aspect_ratio="16:9",
    target_language="English", dialogue="", non_diegetic_music="",
    emotion="孤独", intent="首帧延展",
)
test("I2VA mode selected", result_i2va[0] == "I2VA", f"实际 {result_i2va[0]}")
test("I2VA instruction 非空", len(str(result_i2va[1])) > 0, f"长度 {len(str(result_i2va[1]))}")
test("I2VA instruction 含 'fully referenced'", "fully referenced" in str(result_i2va[1]), f"实际 {str(result_i2va[1])[:100]}")

# Ref2VA 模式
result_ref2va = node.convert_to_h3(
    user_intent="完整 reference 视频, 包含 4 张角色图 + 1 段参考视频 + 1 段参考音频",
    has_first_frame=True, has_last_frame=False, has_refs=True,
    director="黑泽明", scene="山间雾中",
    duration=10, visual_style="Cinematic", aspect_ratio="16:9",
    target_language="English", dialogue="", non_diegetic_music="",
    emotion="史诗", intent="群像剧",
)
test("Ref2VA mode selected", result_ref2va[0] == "Ref2VA", f"实际 {result_ref2va[0]}")
test("Ref2VA full_prompt 含 subject_definitions", "subject_definitions" in str(result_ref2va[5]), f"实际 {str(result_ref2va[5])[:200]}")
test("Ref2VA full_prompt 含 retention_analysis", "retention_analysis" in str(result_ref2va[5]), f"实际 {str(result_ref2va[5])[:200]}")


# === 4. DirectorSoulNode H3 段真实施 ===
print()
print("=" * 60)
print("T4. DirectorSoulNode H3 段真实施")
print("=" * 60)
from director_soul import _build_soul_addons, _H3_FRAMEWORK_LOADED
test("H3 framework loaded (director_soul)", _H3_FRAMEWORK_LOADED, f"{_H3_FRAMEWORK_LOADED}")

fused = {
    "name": "孤独", "intensity": 0.75, "polarity": "negative", "arousal": "low",
    "visual_signs": "雨夜、霓虹、慢镜头、面部特写",
    "voice_signs": "低语、沉默、留白",
    "inner_monologue": "我以为再也不会见到你",
    "color_palette": "蓝绿、暗红、琥珀、过曝",
    "music_tempo": "慢板",
    "facial_au": "AU1+AU4+AU15",
    "description": "雨夜香港, 男女主角擦肩而过",
    "director_examples": "王家卫 《花样年华》《重庆森林》",
}
soul_dims = {"creativity": 0.92, "imagination": 0.88, "artistic_expression": 0.90, "camera_skill": 0.95, "atmosphere_control": 0.93}
soul_state = {"inspiration": 0.88, "fatigue": 0.25, "doubt": 0.40, "rebelliousness": 0.78}

result = _build_soul_addons(
    fused=fused, director="王家卫", director_sig="TungWongKar-Style-NeonRain",
    soul_dims=soul_dims, soul_state=soul_state,
    scene="雨夜香港旺角", story_intensity=0.70, scene_progress=0.50,
)
test("H3_ADDON 段存在", "===H3_ADDON===" in result, "")
test("H3_END_ADDON 段存在", "===END_H3_ADDON===" in result, "")


# === 5. 14+1 段 (14 原有 + H3 新增) 全部存在 ===
print()
print("=" * 60)
print("T5. 14+1 段全部存在")
print("=" * 60)

addon_pairs = [
    ("EDITING", "===EDITING_ADDON===", "===END_EDITING_ADDON==="),
    ("PERFORMANCE", "===PERFORMANCE_ADDON===", "===END_PERFORMANCE_ADDON==="),
    ("SILENCE", "===SILENCE_ADDON===", "===END_SILENCE_ADDON==="),
    ("COLOR", "===COLOR_ADDON===", "===END_COLOR_ADDON==="),
    ("WORLDBUILDING", "===WORLDBUILDING_ADDON===", "===END_WORLDBUILDING_ADDON==="),
    ("THEME", "===THEME_ADDON===", "===END_THEME_ADDON==="),
    ("ART", "===ART_ADDON===", "===END_ART_ADDON==="),
    ("SPATIAL", "===SPATIAL_ADDON===", "===END_SPATIAL_ADDON==="),
    ("SOUND", "===SOUND_ADDON===", "===END_SOUND_ADDON==="),
    ("MUSIC", "===MUSIC_ADDON===", "===END_MUSIC_ADDON==="),
    ("INTENT", "===INTENT_ADDON===", "===END_INTENT_ADDON==="),
    ("STORYBOARD", "===STORYBOARD_ADDON===", "===END_STORYBOARD_ADDON==="),
    ("CHARACTER", "===CHARACTER_ADDON===", "===END_CHARACTER_ADDON==="),
    ("QA", "===QA_ADDON===", "===END_QA_ADDON==="),
    ("H3", "===H3_ADDON===", "===END_H3_ADDON==="),
]

for name, start, end in addon_pairs:
    test(f"{name}_ADDON 段存在", start in result and end in result, f"start={start in result}, end={end in result}")


# === 6. H3 camera 3D 维度 ===
print()
print("=" * 60)
print("T6. H3 camera 3D 维度 (motion + amplitude + speed)")
print("=" * 60)

# 从 H3 段提取
h3_block = result.split("===H3_ADDON===")[1].split("===END_H3_ADDON===")[0]

# 检查 H3 motion types
motion_found = sum(1 for m in CAMERA_MOTION_TYPES if m in h3_block)
test(f"H3 camera motion types 覆盖 ({len(CAMERA_MOTION_TYPES)} types)", motion_found >= 1, f"实际找到 {motion_found}")

# 检查 H3 amplitude
test("H3 amplitude 'with small/large amplitude' 存在", "with small amplitude" in h3_block or "with large amplitude" in h3_block, "")

# 检查 H3 speed
test("H3 speed 'at slow/fast speed' 存在", "at slow speed" in h3_block or "at fast speed" in h3_block, "")

# 检查 6 导演 camera motion
expected_phrases = [
    "Truck right",   # 王家卫
    "Push in",       # 李安
    "Long static",   # 侯孝贤
]
phrase_found = sum(1 for p in expected_phrases if p in h3_block or any(p in render_camera_motion(d) for d in ["王家卫", "李安", "侯孝贤"]))
test(f"6 导演 camera motion 映射 ({len(expected_phrases)} 关键)", phrase_found >= 2, f"实际 {phrase_found}")


# === 7. H3 reference labels 4 选 ===
print()
print("=" * 60)
print("T7. H3 reference labels 4 选")
print("=" * 60)
ref_labels = ["<Subject N>", "<Picture N>", "<Video N>", "<Audio N>"]
for label in ref_labels:
    test(f"  H3 label '{label}' 在 h3_block", label in h3_block, "")


# === 8. H3 dialogue <d>[Language] 格式 ===
print()
print("=" * 60)
print("T8. H3 dialogue <d>[Language] 格式")
print("=" * 60)
test("H3 dialogue 格式 <d>[Language] 在 H3 段", "<d>[Language]" in h3_block or "<d>[" in h3_block, "")
test("H3 voiceover 规则 'off-screen voiceover'", "off-screen voiceover" in h3_block, "")
test("H3 cross-cut 标记 <scenetrans>", "<scenetrans>" in h3_block, "")
test("H3 truncated 标记 <cutoff>", "<cutoff>" in h3_block, "")


# === 9. H3 retention markers (visible + audio) ===
print()
print("=" * 60)
print("T9. H3 retention markers (visible + audio)")
print("=" * 60)
visible_markers = ["fully_preserved", "partially_preserved", "attribute_transfer", "weak_reference"]
audio_markers = ["fully_copy", "partially_copy", "reference", "weak_reference"]

visible_found = sum(1 for m in visible_markers if m in h3_block)
test(f"H3 visible retention markers ({len(visible_markers)})", visible_found >= 2, f"实际 {visible_found}")

audio_found = sum(1 for m in audio_markers if m in h3_block)
test(f"H3 audio retention markers ({len(audio_markers)})", audio_found >= 2, f"实际 {audio_found}")

# H3 Ref2VA 6 段
ref2va_sections = ["subject_definitions", "summary", "retention_analysis", "detailed_description", "overall_soundscape", "non_diegetic_music"]
ref2va_found = sum(1 for s in ref2va_sections if s in h3_block)
test(f"H3 Ref2VA 6 段 ({len(ref2va_sections)})", ref2va_found >= 4, f"实际 {ref2va_found}")


# === 10. 5 维具体化 (era/location/brand/numbers/objects) 保留 ===
print()
print("=" * 60)
print("T10. 5 维具体化 保留 (Phase 35.6 兼容)")
print("=" * 60)
from director_soul import _extract_5d_specifics
specs = _extract_5d_specifics("1998 年香港, 哈尔滨道里区, 雪花啤酒 5 元, 11 月 7 日, 钢笔", "王家卫")
test("5 维具体化 era", "era" in specs, str(specs.get("era")))
test("5 维具体化 location", "location" in specs, str(specs.get("location")))
test("5 维具体化 brand", "brand" in specs, str(specs.get("brand")))
test("5 维具体化 numbers", "numbers" in specs, str(specs.get("numbers")))
test("5 维具体化 objects", "objects" in specs, str(specs.get("objects")))


# === 总结 ===
print()
print("=" * 60)
print(f"Phase 36.2 H3 整合验证汇总")
print("=" * 60)
print(f"通过 {passed} / 总计 {total}")

if fails:
    print(f"\n失败项:")
    for name, detail in fails:
        print(f"  - {name}: {detail}")
    sys.exit(1)
else:
    print(f"\n[PASS] Phase 36.2 H3 整合全部通过 {passed}/{total}")
    sys.exit(0)
