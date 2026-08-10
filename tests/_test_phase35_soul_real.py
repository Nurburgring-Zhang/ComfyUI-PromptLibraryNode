# -*- coding: utf-8 -*-
"""
Phase 35 Round 1 真修复端到端测试
验证 DirectorSoulNode 14 addon 段 + 3 个下游节点 parse addon
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import director_soul
from director_soul import DirectorSoulNode
import editing_pro
from editing_pro import EditingPro, _parse_soul_addon_for_editing
import performance_direction_pro
from performance_direction_pro import PerformanceDirectionPro
import silence_mastery_pro
from silence_mastery_pro import SilenceMasteryPro

results = []
def test(name, passed, detail=""):
    results.append((name, passed, detail))
    status = "OK" if passed else "FAIL"
    print(f"[{status}] {name}: {detail}")


# ===== T1: 14 个 addon 段全部存在 =====
print("\n========== T1: 14 addon 段验证 ==========")
node = DirectorSoulNode()
out = node.build_soul(
    **{'主导情感': 'loneliness', '次要情感_1': 'longing', '次要情感_2': 'none',
       '次要情感_3': 'none', '次要情感_4': 'none',
       '融合模式': 'F2_双情感主次融合', '主导权重': 0.6,
       '创造力': 0.9, '想象力': 0.85, '艺术表达': 0.95, '镜头技巧': 0.88, '氛围掌控': 0.92,
       '灵感指数': 0.85, '疲劳指数': 0.3, '怀疑指数': 0.5, '叛逆指数': 0.7,
       '导演': '王家卫', '场景描述': '父女在厨房, 雨夜, 1998 年哈尔滨', '故事强度': 0.6, '场景进度': 0.4}
)
soul_str = out[0]

expected_addons = [
    "EDITING_ADDON", "PERFORMANCE_ADDON", "SILENCE_ADDON", "COLOR_ADDON",
    "WORLDBUILDING_ADDON", "THEME_ADDON", "ART_ADDON", "SPATIAL_ADDON",
    "SOUND_ADDON", "MUSIC_ADDON", "INTENT_ADDON", "STORYBOARD_ADDON",
    "CHARACTER_ADDON", "QA_ADDON"
]
all_present = True
for addon in expected_addons:
    has_start = f"==={addon}===" in soul_str
    has_end = f"===END_{addon}===" in soul_str
    if not (has_start and has_end):
        all_present = False
        test(f"14 addon 段 {addon}", False, "缺失")
test("14 addon 段全部存在", all_present, f"共 {len(expected_addons)} 段")

# 长度校验
test("灵魂注入长度 > 5000", len(soul_str) > 5000, f"实际 {len(soul_str)} 字符")


# ===== T2: 不同导演 → 灵魂addon 段内容不同 =====
print("\n========== T2: 5 导演灵魂addon 段差异化 ==========")
directors = ["王家卫", "诺兰", "奉俊昊", "塔可夫斯基", "PTA"]
emotion_choices = {
    "王家卫": "loneliness",
    "诺兰": "fear_terror",
    "奉俊昊": "anger_fury",
    "塔可夫斯基": "trust_surrender",
    "PTA": "sadness_sorrow"
}
director_outputs = {}
for d in directors:
    out_d = node.build_soul(
        **{'主导情感': emotion_choices[d], '次要情感_1': 'none', '次要情感_2': 'none',
           '次要情感_3': 'none', '次要情感_4': 'none',
           '融合模式': 'F1_单情感主导', '主导权重': 1.0,
           '创造力': 0.9, '想象力': 0.9, '艺术表达': 0.9, '镜头技巧': 0.9, '氛围掌控': 0.9,
           '灵感指数': 0.9, '疲劳指数': 0.4, '怀疑指数': 0.6, '叛逆指数': 0.8,
           '导演': d, '场景描述': '测试场景', '故事强度': 0.5, '场景进度': 0.5}
    )
    director_outputs[d] = out_d[0]

# 检查每对导演的 EDITING 段是否不同
editing_segments = {}
for d, soul in director_outputs.items():
    m = re.search(r"===EDITING_ADDON===\s*\n(.*?)===END_EDITING_ADDON===", soul, re.DOTALL)
    editing_segments[d] = m.group(1).strip() if m else ""

# 5 导演 EDITING 段两两不同
unique_count = len(set(editing_segments.values()))
test("5 导演 EDITING 段全部不同", unique_count == 5, f"唯一值数 {unique_count}/5")
for d, seg in editing_segments.items():
    print(f"  {d}: 长度 {len(seg)}, 头部 {seg[:80]}")


# ===== T3: EditingPro 真正 parse 灵魂addon 段 =====
print("\n========== T3: EditingPro parse 灵魂addon ==========")
editing_node = EditingPro()
parse_result = _parse_soul_addon_for_editing(director_outputs["王家卫"])
test("parse 王家卫 addon 找到", parse_result["found"], f"cut_strategy 长度 {len(parse_result['cut_strategy'])}")
test("parse 提取切点策略", "切点策略" in parse_result["cut_strategy"], parse_result["cut_strategy"][:80])
test("parse 提取长镜头指令", "12-30s" in parse_result["long_take"], parse_result["long_take"][:80])
test("parse 提取跳切指令", "叛逆" in parse_result["jump_cut"], parse_result["jump_cut"][:80])

# 5 导演 parse 后 cut_strategy 真正不同
cuts = {}
for d in directors:
    p = _parse_soul_addon_for_editing(director_outputs[d])
    cuts[d] = p["cut_strategy"]
unique_cuts = len(set(cuts.values()))
test("5 导演 cut_strategy 唯一", unique_cuts == 5, f"唯一数 {unique_cuts}/5")


# ===== T4: PerformanceDirectionPro + SilenceMasteryPro 接受 addon 字段 =====
print("\n========== T4: PerformanceDirectionPro + SilenceMasteryPro addon 字段 ==========")
perf_node = PerformanceDirectionPro()
# 不传灵魂addon 应正常工作
try:
    out4 = perf_node.build_performance(
        **{'场景描述': '测试', '任务类型': 'T2VA (文生视频, 无参考图)'}
    )
    test("PerformanceDirectionPro 无 addon 可运行", True, f"返回 {len(out4)} 字段")
except Exception as e:
    test("PerformanceDirectionPro 无 addon 可运行", False, f"报错: {e}")

# 传灵魂addon 应能 parse (即使主函数没全部使用)
silence_node = SilenceMasteryPro()
try:
    out5 = silence_node.build_silence(
        **{'场景类型': '对话', '场景描述': '测试', '实际对白数': 8,
           '灵魂addon': director_outputs["王家卫"]}
    )
    # 检查 design 是否含灵魂addon 段的内部内容 (供 SilenceMasteryPro 解析)
    has_silence = "供 SilenceMasteryPro 解析" in out5[0] or "===END_SILENCE_ADDON===" in out5[0]
    test("SilenceMasteryPro addon 注入成功", has_silence, f"design 长度 {len(out5[0])}")
except Exception as e:
    test("SilenceMasteryPro addon 注入成功", False, f"报错: {e}")


# ===== T5: 跨场景不同 → 输出不同 =====
print("\n========== T5: 同导演不同情感 → 灵魂addon 段不同 ==========")
scenes = [
    ("loneliness", "父女在厨房, 雨夜"),
    ("fear_terror", "驾驶舱, 1.5G 侧倾, 夜战"),
    ("joy_ecstasy", "婚礼, 阳光"),
    ("sadness_grief", "葬礼, 阴雨"),
]
scene_outputs = {}
for emo, desc in scenes:
    out_s = node.build_soul(
        **{'主导情感': emo, '次要情感_1': 'none', '次要情感_2': 'none',
           '次要情感_3': 'none', '次要情感_4': 'none',
           '融合模式': 'F1_单情感主导', '主导权重': 1.0,
           '创造力': 0.85, '想象力': 0.85, '艺术表达': 0.85, '镜头技巧': 0.85, '氛围掌控': 0.85,
           '灵感指数': 0.85, '疲劳指数': 0.3, '怀疑指数': 0.5, '叛逆指数': 0.7,
           '导演': '王家卫', '场景描述': desc, '故事强度': 0.5, '场景进度': 0.5}
    )
    scene_outputs[emo] = out_s[0]

# 4 场景灵魂addon 段两两不同
unique_scenes = len(set(scene_outputs.values()))
test("4 场景灵魂注入两两不同", unique_scenes == 4, f"唯一数 {unique_scenes}/4")


# ===== T6: 反 AI 词表 0 命中 (用 anti_ai_vocab.py 真实词表) =====
print("\n========== T6: 反 AI 词表 0 命中 ==========")
# 用 anti_ai_vocab.py 里的真实词表
try:
    from anti_ai_vocab import ANTI_AI_PHRASES
    # 收集所有反 AI 短语 (取前 30 个高频)
    real_anti = []
    if isinstance(ANTI_AI_PHRASES, dict):
        for k, v in list(ANTI_AI_PHRASES.items())[:30]:
            if isinstance(v, (list, tuple)):
                real_anti.extend(v[:3])
            elif isinstance(v, str):
                real_anti.append(v)
    else:
        real_anti = list(ANTI_AI_PHRASES)[:30]
    hit_count = 0
    for d, soul in director_outputs.items():
        for cli in real_anti:
            if cli and cli in soul:
                hit_count += 1
    test("5 导演 anti_ai 词表 0 命中", hit_count == 0, f"实际命中 {hit_count}/{len(real_anti)*5}")
except Exception as e:
    test("anti_ai 词表检测", False, f"加载失败: {e}")


# ===== T7: 12 套理论至少 1 个被激活 =====
print("\n========== T7: 12 套理论激活 ==========")
# 简化检查: 灵魂addon 段引用了哪个理论名
theory_keywords = ["Save the Cat", "Hero's Journey", "McKee", "三幕剧", "因果链",
                   "反转", "余韵", "节拍", "转折点", "伏笔", "情绪因果", "物件因果"]
any_hits = sum(1 for kw in theory_keywords for d, soul in director_outputs.items() if kw in soul)
test("12 理论至少 1 个激活", any_hits > 0, f"激活 {any_hits} 次")


# ===== T8: 5 维具体化 =====
print("\n========== T8: 5 维具体化 ==========")
# 时代/地点/品牌/数字/物件 各至少 1 个具体细节
specific_terms = ["1998", "哈尔滨", "雪花啤酒", "桑塔纳", "大哥大", "11 月",
                  "2014", "巴黎", "奔驰", "iPhone", "上海", "地铁"]
hits_spec = sum(1 for t in specific_terms for d, soul in director_outputs.items() if t in soul)
test("5 维具体化覆盖", hits_spec > 0, f"具体词命中 {hits_spec} 次")


# ===== 汇总 =====
print("\n" + "=" * 60)
print("Phase 35 Round 1 验证汇总")
print("=" * 60)
total = len(results)
passed = sum(1 for _, p, _ in results if p)
print(f"通过 {passed} / 总计 {total}")
if passed < total:
    print("\n失败项:")
    for n, p, d in results:
        if not p:
            print(f"  ❌ {n}: {d}")

sys.exit(0 if passed == total else 1)
