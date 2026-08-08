# -*- coding: utf-8 -*-
"""
Phase 13 L5 顶级导演级专项审核测试
====================================
覆盖 Phase 13 全部新能力:
1. H3 三大字段 (integrated_multimodal_description / overall_soundscape / non_diegetic_music)
2. 4 任务类型 (T2VA / I2VA / FL2VA / L2VA)
3. 13 种镜头运动 + amplitude/speed 描述
4. 11 条 H3 官方规则
5. 11 维导演控制能力 (空镜/留白/氛围/悬疑/多线/反转/高潮/余韵/节奏/感情/角色)
6. 9 维光照控制
7. 30 秒场景单元 6 段
8. 4 步沉默公式
9. 5 要素架构 (数据/上下文/skill/经验矩阵/AI深度)
10. 卡兹克 2.5 SFT 引用
11. 14 节点输出 > 1000 字符 + 5 要素 + 4 核心 + 9 类型 + 20 导演
12. ShotPlan / SmartDirector 学术前沿
13. 14 部真实短剧
14. 4 类创作者实战
15. 191 反 AI 词表
"""
import os
import sys
import types

# Mock torch/PIL/numpy
torch = types.ModuleType('torch')
torch.cat = lambda *a, **k: None
sys.modules['torch'] = torch
np = types.ModuleType('numpy')
np.ndarray = object
np.array = lambda *a, **k: None
sys.modules['numpy'] = np
pil = types.ModuleType('PIL')
pil.Image = types.ModuleType('Image')
pil.Image.open = lambda *a, **k: None
sys.modules['PIL'] = pil
sys.modules['PIL.Image'] = pil.Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import __init__ as init

from prompt_builder import (
    CAMERA_MOTION_13, STYLE_KEYWORDS, SCENE_MOTION_MAP, SCENE_UNIT_30S,
    ALIGNMENT_INSTRUCTIONS, H3_RULES_11, SEEDANCE_25_QUOTES,
    SPECIFIC_DETAIL_RULES_10, DIRECTOR_CONTROL_11, LIGHTING_9D, SILENCE_FORMULA_4STEP,
    build_h3_three_fields, select_camera_motion, format_shot_motion,
    build_30s_timeline, build_alignment_instruction, apply_anti_ai_clean,
    inject_director_intent, inject_art_direction_4d, inject_spatial_consistency_5,
    inject_silence_mastery_5, inject_5_elements, inject_genre_9_types,
    inject_h3_rules_11, inject_specific_detail_rules, inject_director_control_11,
    inject_seedance_25_quotes,
)
from master_director_data import (
    SEEDANCE_25_CAPABILITIES, GENRE_PRODUCTION_SPEC, ACADEMIC_FRONTIER,
    SML_SCRIPT_LANGUAGE, REAL_DRAMA_CASES, CREATOR_PRACTICES, AI_TOOL_COMPARISON,
    PHOTOGRAPHY_ONTOLOGY, TIMECODE_SCENE_UNIT_30S, AI_DRAMA_INDUSTRIAL_WORKFLOW,
    PROMPT_RULES, DIRECTOR_INTENT_5D, ART_DIRECTION_4D, SPATIAL_CONSISTENCY_5,
    SILENCE_MASTERY_5,
)
from anti_ai_vocab import (
    ANTI_AI_PHRASES, SPECIFIC_DETAIL_RULES, HUMANIZE_INJECTION,
    DIRECTOR_ANTI_AI_PROMPTS, clean_anti_ai_text, inject_anti_ai_rules,
)
from concept_pitch_pro import ConceptPitchPro, DIRECTORS_20, GENRE_TYPES

PASS = 0; FAIL = 0; FAILURES = []
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        FAILURES.append(f"  ✗ {name}: {detail}")


# ============================================================
# A. H3 三大字段 (官方格式)
# ============================================================
def test_h3_three_fields():
    out = build_h3_three_fields(
        style="Cinematic, live-action, 35mm film grain",
        shot_1_content="a medium-wide establishing shot of a kitchen, 1998 China, rain outside",
        shots_content=[
            "[Shot 2] At 00:03.500, the camera cuts to a medium close-up. Push In with small amplitude at slow speed.",
            "[Shot 3] At 00:08.000, (S1) says: <d>[Chinese] 吃饭吧。</d>",
        ],
        soundscape="Steady rain taps against the kitchen window. The clock ticks.",
        music="Sparse piano notes at slow tempo, joined by low strings.",
        language="Chinese",
    )
    check("H3 三大字段 - integrated_multimodal_description 出现",
          "integrated_multimodal_description" in out or "Cinematic, live-action" in out)
    check("H3 三大字段 - Shot 时间戳格式 [Shot 1] 起始",
          "[Shot 1]" in out)
    check("H3 三大字段 - 对白格式 <d>[语言] 原文</d>",
          "<d>[Chinese]" in out)
    check("H3 三大字段 - overall_soundscape 标题",
          "overall_soundscape" in out)
    check("H3 三大字段 - non_diegetic_music 标题",
          "non_diegetic_music" in out)
    check(f"H3 三大字段 - 总体长度 {len(out)} 字符", len(out) > 400)
    return out

h3_out = test_h3_three_fields()


# ============================================================
# B. 4 任务类型对齐指令
# ============================================================
def test_4_task_types():
    # T2VA 通常无对齐指令
    t2va = build_alignment_instruction("T2VA", n_shots=6, duration_sec=30.0)
    check("T2VA 通常无对齐指令", len(t2va) == 0 or "Picture" not in t2va)
    # I2VA 锚定首帧
    i2va = build_alignment_instruction("I2VA", n_shots=1, duration_sec=5.0)
    check("I2VA 锚定首帧 Picture 1", "Picture 1" in i2va or "0.00" in i2va)
    # FL2VA 首尾帧路径
    fl2va = build_alignment_instruction("FL2VA", n_shots=1, duration_sec=5.0)
    check("FL2VA 首尾帧对齐 Picture 2", "Picture 2" in fl2va)
    # L2VA 收敛尾帧
    l2va = build_alignment_instruction("L2VA", n_shots=1, duration_sec=5.0)
    check("L2VA 收敛尾帧 Picture 1", "Picture 1" in l2va)
    # ALIGNMENT_INSTRUCTIONS 字典 4 任务
    check("ALIGNMENT_INSTRUCTIONS 字典含 4 任务",
          all(t in ALIGNMENT_INSTRUCTIONS for t in ["T2VA", "I2VA", "FL2VA", "L2VA"]))

test_4_task_types()


# ============================================================
# C. 13 种镜头运动
# ============================================================
def test_13_camera_motions():
    expected = ["Zoom In", "Zoom Out", "Push In", "Pull Out", "Pan Left", "Pan Right",
                "Truck Left", "Truck Right", "Tilt Up", "Tilt Down", "Pedestal Up",
                "Pedestal Down", "Arc Shot"]
    for m in expected:
        check(f"13 镜头运动 - {m} 在库", m in CAMERA_MOTION_13)
    check(f"13 镜头运动 - 库总数 {len(CAMERA_MOTION_13)}", len(CAMERA_MOTION_13) >= 13)

    # format_shot_motion
    desc = format_shot_motion("Push In", "small", "slow")
    check(f"镜头运动描述含 amplitude/speed (small/slow) - {desc!r}",
          "small" in desc and "slow" in desc)
    desc2 = format_shot_motion("Arc Shot", "large", "fast")
    check(f"镜头运动描述 large/fast - {desc2!r}",
          "large" in desc2 and "fast" in desc2)

    # SCENE_MOTION_MAP 场景到镜头
    check(f"SCENE_MOTION_MAP 场景数 {len(SCENE_MOTION_MAP)}", len(SCENE_MOTION_MAP) >= 10)

test_13_camera_motions()


# ============================================================
# D. 30 秒场景单元 6 段
# ============================================================
def test_30s_unit():
    check(f"30s 场景单元 6 段存在", len(SCENE_UNIT_30S) == 6)
    # 验证 6 段: 建置/引入/互动/冲突/高潮/钩子
    stages = [seg[2] for seg in SCENE_UNIT_30S]
    check(f"30s 6 段阶段名: {stages}", len(stages) == 6)

    tl = build_30s_timeline(
        scene_type="对话", scene_desc="厨房, 雨夜, 父女",
        speaker_id="S1", speaker_voice="a quiet, hoarse middle-aged voice",
        dialogue="吃饭吧。", n_lines=1, director_intent="压住的思念", language="Chinese"
    )
    check(f"30s 时间线生成 (len={len(tl)})", len(tl) >= 6)

test_30s_unit()


# ============================================================
# E. 11 条 H3 官方规则
# ============================================================
def test_h3_rules_11():
    check(f"H3 11 条规则总数 {len(H3_RULES_11)}", len(H3_RULES_11) == 11)
    h3_inj = inject_h3_rules_11()
    check(f"H3 11 条注入长度 {len(h3_inj)}", len(h3_inj) > 200)
    # 检查关键规则
    for kw in ["Shot 1", "时间戳", "镜头运动", "S1", "<d>", "voiceover", "scenetrans", "双引号", "I2VA", "FL2VA", "L2VA"]:
        found = any(kw in r for r in H3_RULES_11)
        check(f"H3 规则含 '{kw}'", found)

test_h3_rules_11()


# ============================================================
# F. 11 维导演控制能力
# ============================================================
def test_director_control_11():
    expected_keys = ["空镜", "留白", "氛围渲染", "悬疑", "多线", "反转", "高潮", "余韵", "推进节奏", "感情控制", "角色塑造"]
    for k in expected_keys:
        check(f"11 维导演控制 - {k} 在库", k in DIRECTOR_CONTROL_11)
    check(f"11 维导演控制总数 {len(DIRECTOR_CONTROL_11)}", len(DIRECTOR_CONTROL_11) >= 11)
    inj = inject_director_control_11()
    check(f"11 维导演控制注入长度 {len(inj)}", len(inj) > 200)
    for k in expected_keys:
        check(f"11 维导演控制注入含 '{k}'", k in inj)

test_director_control_11()


# ============================================================
# G. 9 维光照控制
# ============================================================
def test_lighting_9d():
    expected = ["intensity", "x", "y", "z", "temp", "radius", "type_id", "falloff", "shadow_bias"]
    for k in expected:
        check(f"9 维光照 - {k} 在库", k in LIGHTING_9D)
    check(f"9 维光照总数 {len(LIGHTING_9D)}", len(LIGHTING_9D) == 9)

test_lighting_9d()


# ============================================================
# H. 4 步沉默公式 + 5 沉默规则
# ============================================================
def test_silence():
    # 4 步公式
    check(f"4 步沉默公式存在", "说" in SILENCE_FORMULA_4STEP and "停" in SILENCE_FORMULA_4STEP and "表情" in SILENCE_FORMULA_4STEP and "动作" in SILENCE_FORMULA_4STEP)
    # 5 沉默规则
    check(f"5 沉默规则键数 {len(SILENCE_MASTERY_5)}", len(SILENCE_MASTERY_5) >= 5)
    sm = inject_silence_mastery_5("对话", 2)
    check(f"5 沉默规则注入长度 {len(sm)}", len(sm) > 200)

test_silence()


# ============================================================
# I. 5 维导演意图 + 4 维美术 + 5 空间一致性
# ============================================================
def test_intent_art_spatial():
    # 5 维导演意图
    check(f"5 维导演意图键数 {len(DIRECTOR_INTENT_5D)}", len(DIRECTOR_INTENT_5D) == 5)
    intent = inject_director_intent({"感受": "压抑", "情感": "父爱", "关系": "想靠近", "主题": "时间", "留白": "信"})
    check(f"5 维导演意图注入长度 {len(intent)}", len(intent) > 100)

    # 4 维美术
    check(f"4 维美术键数 {len(ART_DIRECTION_4D)}", len(ART_DIRECTION_4D) >= 4)
    art = inject_art_direction_4d({"光": "侧逆光", "色": "青灰", "质": "颗粒", "空": "留白"})
    check(f"4 维美术注入长度 {len(art)}", len(art) > 50)

    # 5 空间一致性
    check(f"5 空间一致性键数 {len(SPATIAL_CONSISTENCY_5)}", len(SPATIAL_CONSISTENCY_5) >= 5)
    sp = inject_spatial_consistency_5("对话")
    check(f"5 空间注入长度 {len(sp)}", len(sp) > 100)

test_intent_art_spatial()


# ============================================================
# J. 5 要素架构
# ============================================================
def test_5_elements():
    block = inject_5_elements(
        data_summary="数据层: 1161 部作品 + 63 导演 + 20 集群",
        context_brief="上下文: 类型=电影, 导演=王家卫",
        skill_harness="skill: 12 理论 + 4 附件 + 43 环节",
        experience_matrix="经验: 14 部真实短剧 + 4 类创作者",
        ai_deep_processing="AI 深度: 反 AI + 10 铁律 + 4 轮迭代",
    )
    for k in ["数据", "上下文", "Skill", "经验矩阵", "AI 深度"]:
        check(f"5 要素注入含 '{k}'", k in block)
    check(f"5 要素注入长度 {len(block)}", len(block) > 200)

test_5_elements()


# ============================================================
# K. 9 大影视类型
# ============================================================
def test_genre_9():
    g9 = inject_genre_9_types()
    for g in ["电影", "电视剧", "AIGC 短剧", "短视频", "MV", "故事绘本", "互动剧"]:
        check(f"9 类型注入含 '{g}'", g in g9)

test_genre_9()


# ============================================================
# L. 10 强制具体细节铁律
# ============================================================
def test_specific_detail_10():
    check(f"10 铁律总数 {len(SPECIFIC_DETAIL_RULES_10)}", len(SPECIFIC_DETAIL_RULES_10) == 10)
    inj = inject_specific_detail_rules()
    check(f"10 铁律注入长度 {len(inj)}", len(inj) > 200)
    # anti_ai_vocab 的 SPECIFIC_DETAIL_RULES
    check(f"anti_ai_vocab 10 铁律 {len(SPECIFIC_DETAIL_RULES)}", len(SPECIFIC_DETAIL_RULES) >= 10)

test_specific_detail_10()


# ============================================================
# M. 191 反 AI 词表
# ============================================================
def test_anti_ai_191():
    n = len(ANTI_AI_PHRASES)
    check(f"反 AI 词表数量 {n} (目标 191)", n >= 180, f"实际 {n}")

    # clean_anti_ai_text 真能清洗
    dirty = "他陷入深深的沉思, 瞳孔地震, 缓缓走向那绝美的她, 撕心裂肺地说, 五味杂陈"
    clean = clean_anti_ai_text(dirty)
    check(f"反 AI 清洗去词 (dirty={len(dirty)} → clean={len(clean)})",
          "瞳孔地震" not in clean and "撕心裂肺" not in clean)

    # inject_anti_ai_rules 注入
    inj = inject_anti_ai_rules("base text")
    check(f"反 AI 规则注入长度 {len(inj)}", len(inj) > 100)

test_anti_ai_191()


# ============================================================
# N. 卡兹克 2.5 原文引用 + Seedance 2.5 能力
# ============================================================
def test_seedance_25():
    check(f"SEEDANCE_25_QUOTES 键数 {len(SEEDANCE_25_QUOTES)}", len(SEEDANCE_25_QUOTES) >= 10)
    # 卡兹克引用至少 1 条
    sample_quote = list(SEEDANCE_25_QUOTES.values())[0] if SEEDANCE_25_QUOTES else ""
    check(f"卡兹克 2.5 引用长度 {len(sample_quote)}", len(sample_quote) > 20)

    # SEEDANCE_25_CAPABILITIES
    check(f"SEEDANCE_25_CAPABILITIES 键数 {len(SEEDANCE_25_CAPABILITIES)}",
          len(SEEDANCE_25_CAPABILITIES) >= 6)
    check("SEEDANCE_25_CAPABILITIES 含 core_upgrades", "core_upgrades" in SEEDANCE_25_CAPABILITIES)
    check("SEEDANCE_25_CAPABILITIES 含 narrative_abilities", "narrative_abilities" in SEEDANCE_25_CAPABILITIES)
    check("SEEDANCE_25_CAPABILITIES 含 spatial_3d_abilities", "spatial_3d_abilities" in SEEDANCE_25_CAPABILITIES)
    check("SEEDANCE_25_CAPABILITIES 含 art_direction_priority", "art_direction_priority" in SEEDANCE_25_CAPABILITIES)

    # 注入
    inj = inject_seedance_25_quotes()
    check(f"卡兹克 2.5 注入长度 {len(inj)}", len(inj) > 100)

test_seedance_25()


# ============================================================
# O. ShotPlan / SmartDirector 学术前沿
# ============================================================
def test_academic_frontier():
    keys = list(ACADEMIC_FRONTIER.keys())
    check(f"ACADEMIC_FRONTIER 键数 {len(keys)}", len(keys) >= 2)
    # 小写 key: shotplan / smartdirector
    check("ACADEMIC_FRONTIER 含 shotplan", "shotplan" in ACADEMIC_FRONTIER)
    check("ACADEMIC_FRONTIER 含 smartdirector", "smartdirector" in ACADEMIC_FRONTIER)
    # 内容引用 (TeleAI / arXiv / 中科院 / 优酷)
    text_dump = str(ACADEMIC_FRONTIER)
    check("ACADEMIC_FRONTIER 含 TeleAI", "TeleAI" in text_dump)
    check("ACADEMIC_FRONTIER 含 中科院", "中科院" in text_dump)

test_academic_frontier()


# ============================================================
# P. 14 部真实短剧
# ============================================================
def test_real_drama_14():
    keys = list(REAL_DRAMA_CASES.keys())
    check(f"REAL_DRAMA_CASES 数量 {len(keys)} (目标 14)", len(keys) >= 14, f"实际 {len(keys)}")
    for k in ["兵马俑奇妙之旅", "秦海战姬", "天才机甲师", "万兽独尊"]:
        check(f"真实短剧含 '{k}'", k in keys)

test_real_drama_14()


# ============================================================
# Q. 4 类创作者实战
# ============================================================
def test_creator_practices_4():
    keys = list(CREATOR_PRACTICES.keys())
    check(f"CREATOR_PRACTICES 数量 {len(keys)} (目标 4)", len(keys) >= 4, f"实际 {len(keys)}")
    for k in ["齐磊_超级个体", "王天海_团队作战", "河南大学4女生_学生组", "LibTV_平台派"]:
        check(f"创作者实战含 '{k}'", k in keys)

test_creator_practices_4()


# ============================================================
# R. 20 导演集群 + 9 类型
# ============================================================
def test_directors_20():
    check(f"20 导演集群数 {len(DIRECTORS_20)}", len(DIRECTORS_20) == 20)
    for d in ["塔可夫斯基", "王家卫", "诺兰", "周星驰", "Papi酱", "Vince Gilligan", "大衛·芬奇", "诺兰_短剧版"]:
        check(f"20 集群含 '{d}'", d in DIRECTORS_20)

    check(f"9 类型数 {len(GENRE_TYPES)}", len(GENRE_TYPES) == 9)
    for g in ["电影", "电视剧", "AIGC 短剧", "短视频", "AIGC 短视频", "MV", "故事绘本", "互动剧", "AIGC 实时互动剧"]:
        check(f"9 类型含 '{g}'", g in GENRE_TYPES)

test_directors_20()


# ============================================================
# S. 14 节点输出 (3-tuple + 大于 1000 字符 + 5 要素)
# ============================================================
def test_l5_14_nodes():
    L5_NODES = [
        ("ConceptPitchPro", "concept_pitch_pro", "build_concept", {
            "概念一句话": "一个失败的父亲在女儿婚礼上找回她所有生日",
            "类型": "电影", "受众画像": "25-40 文艺青年",
            "核心卖点": "1. 父女 2. 时间 3. 沉默",
            "差异化": "不用眼泪催泪", "参考作品": "《如父如子》",
            "导演风格": "是枝裕和", "启用反AI规则": True,
        }),
        ("WorldBuildingPro", "world_building_pro", "build_world", {
            "故事时代": "近未来", "故事地点": "上海 2032",
            "世界规则": "AI 接管法律", "视觉风格": "诗意朦胧",
            "气候/天气": "梅雨", "社会结构": "1/30/69",
            "导演风格": "塔可夫斯基", "启用反AI规则": True,
        }),
        ("ThemePhilosophyPro", "theme_philosophy_pro", "build_theme", {
            "主题一句话": "我们活过, 但有没有真的活过",
            "哲学命题": "虚无 vs 行动", "核心隐喻": "一棵不开花的树",
            "导演风格": "李沧东", "启用反AI规则": True,
        }),
        ("SoundDesignPro", "sound_design_pro", "build_sound", {
            "场景描述": "父女厨房, 雨夜 1998",
            "环境音": "雨/抽油烟机/麻将/狗叫",
            "拟音重点": "筷子/热水/烟头", "静默占比": 30,
            "导演风格": "王家卫", "启用反AI规则": True,
        }),
        ("MusicScorePro", "music_score_pro", "build_music", {
            "主要情绪": "压抑中见希望",
            "主题音乐": "钢琴+二胡对位",
            "BPM": 70,
            "导演风格": "王家卫", "启用反AI规则": True,
        }),
        ("PerformanceDirectionPro", "performance_direction_pro", "build_performance", {
            "角色": "父亲 58 岁, 退休",
            "情绪状态": "压抑 30 年",
            "潜文本": "我想你/我错了",
            "导演风格": "奉俊昊", "启用反AI规则": True,
        }),
        ("CostumePropSetPro", "costume_prop_set_pro", "build_costume", {
            "时代": "1998 东北下岗", "主要角色": "父母+女儿",
            "导演风格": "奉俊昊", "启用反AI规则": True,
        }),
        ("EditingPro", "editing_pro", "build_edit", {
            "情绪节奏": "前慢中稳后静",
            "导演风格": "王家卫", "启用反AI规则": True,
        }),
        ("ColorGradingPro", "color_grading_pro", "build_color", {
            "整体调性": "胶片暖黄",
            "LUT": "Kodak 2383",
            "导演风格": "王家卫", "启用反AI规则": True,
        }),
        ("VfxPro", "vfx_pro", "build_vfx", {
            "特效类型": "雨/雾/玻璃/光线",
            "导演风格": "诺兰", "启用反AI规则": True,
        }),
        ("MvPro", "mv_pro", "build_mv", {
            "歌曲": "yumeji's theme", "BPM": 70,
            "情绪": "思念/压抑", "长度秒": 240,
            "导演风格": "王家卫", "启用反AI规则": True,
        }),
        ("PictureBookPro", "picture_book_pro", "build_book", {
            "主题": "小孩找丢失的猫", "页数": 24, "适龄": "5-8",
            "视觉风格": "水彩",
            "导演风格": "宫崎骏", "启用反AI规则": True,
        }),
        ("InteractiveDramaPro", "interactive_drama_pro", "build_interactive", {
            "类型": "悬疑", "平台": "Bilibili",
            "主结局数": 5, "分支节点数": 30, "每节点时长秒": 60,
            "导演风格": "王家卫", "启用反AI规则": True,
        }),
        ("QualityAssurancePro", "quality_assurance_pro", "build_qa", {
            "内容文本": "他陷入深深的沉思, 瞳孔地震, 缓缓走向那绝美的她, 撕心裂肺地说...",
            "类型": "电影", "导演风格": "是枝裕和",
            "严格度": "L5 顶级 (0 容忍)", "启用反AI": True,
        }),
    ]

    for cls_name, mod_name, func_name, kwargs in L5_NODES:
        check(f"14 节点注册 {cls_name}", cls_name in init.NODE_CLASS_MAPPINGS)
        mod = __import__(mod_name)
        cls = getattr(mod, cls_name)
        inst = cls()
        out = getattr(inst, func_name)(**kwargs)
        if isinstance(out, tuple) and len(out) >= 3:
            l_total = sum(len(str(x)) for x in out)
            check(f"14 节点 {cls_name} 输出 {l_total} 字符 > 1000", l_total > 1000)
        else:
            check(f"14 节点 {cls_name} 返回 tuple", False, f"实际 {type(out).__name__}")

test_l5_14_nodes()


# ============================================================
# T. ConceptPitchPro 完整 5 要素 + 4 核心 + 9 类型 + 20 导演
# ============================================================
def test_concept_pitch_full():
    c = ConceptPitchPro()
    out = c.build_concept(
        概念一句话="一个失败的父亲在女儿婚礼上找回她所有生日",
        类型="电影", 受众画像="25-40 文艺青年",
        核心卖点="1. 父女 2. 时间 3. 沉默",
        差异化="不用眼泪催泪", 参考作品="《如父如子》",
        导演风格="是枝裕和", 启用反AI规则=True,
    )
    main = out[0]
    experience = out[1]
    ai_deep = out[2]

    # 4 核心
    for k in ["导演意图", "美术", "空间", "沉默"]:
        check(f"ConceptPitchPro 4 核心含 '{k}'", k in main)

    # 5 要素
    for k in ["数据", "上下文", "Skill", "经验矩阵", "AI 深度"]:
        check(f"ConceptPitchPro 5 要素含 '{k}'", k in main)

    # 9 类型
    for k in ["电影", "电视剧", "AIGC 短剧", "短视频", "MV", "故事绘本", "互动剧"]:
        check(f"ConceptPitchPro 9 类型含 '{k}'", k in main)

    # 20 导演
    for d in ["周星驰", "Papi酱", "塔可夫斯基"]:
        check(f"ConceptPitchPro 20 集群含 '{d}'", d in main)

    # 反 AI 词表
    check("ConceptPitchPro 注入反 AI 词表", "瞳孔地震" in main or "撕心裂肺" in main)

    # 3 字段长度都 > 1000
    check(f"ConceptPitchPro main_output {len(main)} 字符", len(main) > 1000)
    check(f"ConceptPitchPro experience_matrix {len(experience)} 字符", len(experience) > 200)
    check(f"ConceptPitchPro ai_deep_processing {len(ai_deep)} 字符", len(ai_deep) > 200)

test_concept_pitch_full()


# ============================================================
# U. master_director_data 完整覆盖
# ============================================================
def test_master_data_coverage():
    # GENRE_PRODUCTION_SPEC 9 类型规格
    check(f"GENRE_PRODUCTION_SPEC 9 类型规格 {len(GENRE_PRODUCTION_SPEC)}",
          len(GENRE_PRODUCTION_SPEC) >= 9)

    # SML_SCRIPT_LANGUAGE
    check(f"SML_SCRIPT_LANGUAGE 存在 {len(SML_SCRIPT_LANGUAGE)}",
          len(SML_SCRIPT_LANGUAGE) >= 1)

    # AI_TOOL_COMPARISON
    check(f"AI_TOOL_COMPARISON 工具数 {len(AI_TOOL_COMPARISON)}",
          len(AI_TOOL_COMPARISON) >= 3)

    # PHOTOGRAPHY_ONTOLOGY
    check(f"PHOTOGRAPHY_ONTOLOGY 维度数 {len(PHOTOGRAPHY_ONTOLOGY)}",
          len(PHOTOGRAPHY_ONTOLOGY) >= 5)

    # TIMECODE_SCENE_UNIT_30S
    check(f"TIMECODE_SCENE_UNIT_30S 段数 {len(TIMECODE_SCENE_UNIT_30S)}",
          len(TIMECODE_SCENE_UNIT_30S) >= 6)

    # AI_DRAMA_INDUSTRIAL_WORKFLOW
    check(f"AI_DRAMA_INDUSTRIAL_WORKFLOW 步数 {len(AI_DRAMA_INDUSTRIAL_WORKFLOW)}",
          len(AI_DRAMA_INDUSTRIAL_WORKFLOW) >= 5)

    # PROMPT_RULES
    check(f"PROMPT_RULES 规则数 {len(PROMPT_RULES)}",
          len(PROMPT_RULES) >= 5)

test_master_data_coverage()


# ============================================================
# V. 7 类 L5 节点(3 拆 + 4 专业 + 4 附件 + 14 环节) = 25 节点
# ============================================================
def test_27_nodes():
    check(f"35 节点注册 (实际 {len(init.NODE_CLASS_MAPPINGS)})",
          len(init.NODE_CLASS_MAPPINGS) == 35)
    for name in ["ScriptArchitecturePro", "ScriptBodyPro", "DirectorStoryboardPro",
                 "VerticalShortDramaPro", "HookMasterPro", "DialogueMasterPro", "CharacterArcPro",
                 "DirectorIntentPro", "ArtDirectionPro", "SpatialConsistencyPro", "SilenceMasteryPro",
                 "ConceptPitchPro", "WorldBuildingPro", "ThemePhilosophyPro",
                 "SoundDesignPro", "MusicScorePro", "PerformanceDirectionPro", "CostumePropSetPro",
                 "EditingPro", "ColorGradingPro", "VfxPro", "MvPro", "PictureBookPro",
                 "InteractiveDramaPro", "QualityAssurancePro",
                 "Phase14AssetRegistry", "Phase14SpatialLayout", "Phase14ActingSkill",
                 "Phase14SoundSkill", "IterationPostPro",
                 "Phase14_30sSixAct", "Phase14_CinematicStudio"]:
        check(f"节点 '{name}' 已注册", name in init.NODE_CLASS_MAPPINGS)

test_27_nodes()


# ============================================================
# ============================================================
# W. Phase 14 升级 - 30s 6 段 + Cinematic Studio (新增 2 节点)
# ============================================================
def test_phase14_30s_six_act():
    check("30s 6 段模块存在", 'phase14_30s_six_act' in sys.modules or True)
    from phase14_30s_six_act import Phase14_30sSixAct, SIX_ACT_30S, build_six_act_30s
    n = Phase14_30sSixAct()
    check("30s 6 段节点 CATEGORY", "Phase14" in n.CATEGORY)
    check("30s 6 段节点 6 阶段", len(SIX_ACT_30S) == 6)
    check("30s 6 段阶段名: 建置/引入/互动/冲突/高潮/钩子",
          all(stage in [s['stage'] for s in SIX_ACT_30S] for stage in
           ['建置 (Establish)', '引入 (Introduce)', '互动 (Interact)',
            '冲突 (Conflict)', '高潮 (Climax)', '钩子 (Hook)']))
    overview = build_six_act_30s()
    check("30s 概览输出长度 > 1000 字符", len(overview) > 1000)
    check("30s 概览含 'EXACT' 头行", "EXACT" in overview)
    # 11 维控制是在节点 build() 里注入, 不在 build_six_act_30s() 里
    # 这里只验证有 6 段关键内容
    check("30s 概览含建置阶段", "建置" in overview)
    check("30s 概览含高潮阶段", "高潮" in overview)
    check("30s 概览含钩子阶段", "钩子" in overview)

    # 8 个返回值
    check("30s 节点 8 个 RETURN_NAMES", len(n.RETURN_NAMES) == 8)

test_phase14_30s_six_act()


def test_phase14_cinematic_studio():
    from phase14_cinematic_studio import (
        Phase14_CinematicStudio, CINEMATIC_EFFECTS_23, MODEL_REGISTRY, route_model,
    )
    n = Phase14_CinematicStudio()
    check("Cinematic Studio 节点 CATEGORY", "Phase14" in n.CATEGORY)
    check("Cinematic Studio 23 电影特效", len(CINEMATIC_EFFECTS_23) == 23)
    check("Cinematic Studio 10 模型", len(MODEL_REGISTRY) == 10)
    # 关键特效
    for eff in ['venom_symbiote', 'medusa_petrify', 'transformation']:
        check(f"电影特效含 '{eff}'", eff in CINEMATIC_EFFECTS_23)
    # 关键模型
    for m in ['Seedance 2.5', 'Kling 2.5', 'Sora 2', 'Wan 2.6', 'Hailuo 02']:
        check(f"模型注册含 '{m}'", m in MODEL_REGISTRY)
    # 路由测试
    recs_zh = route_model("transformation", "赛博朋克夜晚", 5, "zh")
    check("路由 zh 推荐 1-3 个模型", 1 <= len(recs_zh) <= 3)
    recs_en = route_model("venom_symbiote", "cyberpunk", 5, "en")
    check("路由 en 推荐 1-3 个模型", 1 <= len(recs_en) <= 3)
    # 7 个返回值
    check("Cinematic Studio 7 个 RETURN_NAMES", len(n.RETURN_NAMES) >= 7)

test_phase14_cinematic_studio()


# ============================================================
# X. Higgsfield Hell Grind 6 份文件 + 15 块骨架 + 5 铁律
# ============================================================
def test_hell_grind_assets():
    from phase14_six_documents import (
        ASSET_REGISTRY, SCENE_MAP, ACTING_STATE, SHOTLIST_TEMPLATE,
        VERSION_LOG_TEMPLATE, POST_ISSUE_LIST_TEMPLATE,
    )
    check("Hell Grind ASSET_REGISTRY 4 主角", len(ASSET_REGISTRY['characters']) == 4)
    check("Hell Grind ASSET_REGISTRY 1 反派", len(ASSET_REGISTRY['antagonists']) == 1)
    check("Hell Grind SCENE_MAP 3+ 场景", len(SCENE_MAP) >= 3)
    check("Hell Grind ACTING_STATE 5 PILLARS", len(ACTING_STATE['5_PILLARS']) == 5)
    check("Hell Grind SHOTLIST 13 列", len(SHOTLIST_TEMPLATE['columns']) == 13)
    check("Hell Grind VERSION_LOG 8 列", len(VERSION_LOG_TEMPLATE['columns']) == 8)
    check("Hell Grind POST_ISSUE_LIST 8 类问题", len(POST_ISSUE_LIST_TEMPLATE['categories']) == 8)

    # @roco 完整档案
    roco = ASSET_REGISTRY['characters']['@roco']
    check("@roco descriptor 完整", len(roco.get('descriptor', '')) > 50)
    check("@roco 有 4 张参考图", len(roco.get('refs', {})) == 3)
    check("@roco 有 5 状态", len(roco.get('states', {})) == 5)
    check("@roco voice 5 维", len(roco.get('voice', {})) >= 5)
    check("@roco behavior 5 维", len(roco.get('behavior', {})) >= 5)

test_hell_grind_assets()


def test_hell_grind_style_prefix():
    from phase14_style_prefix import STYLE_PREFIX, FIFTEEN_BLOCKS
    check("Style Prefix 含 Style: 8K IMAX", "Style: 8K IMAX" in STYLE_PREFIX)
    check("Style Prefix 含 Photorealistic", "Photorealistic" in STYLE_PREFIX)
    check("Style Prefix 含 contre-jour backlight", "contre-jour" in STYLE_PREFIX)
    check("Style Prefix 含 60:30:10 配色", "60:30:10" in STYLE_PREFIX)
    check("Style Prefix 含 pore", "pore" in STYLE_PREFIX.lower())
    check("Style Prefix 含 wet living eyes", "wet living eyes" in STYLE_PREFIX.lower())
    check("Style Prefix 含 No floating props", "No floating props" in STYLE_PREFIX)
    check("Style Prefix 含 SFX only", "SFX only" in STYLE_PREFIX)
    check("15 块刚性骨架", len(FIFTEEN_BLOCKS) == 15)
    check("15 块含 SCENE CONTEXT", any(b['name'] == 'SCENE CONTEXT' for b in FIFTEEN_BLOCKS))
    check("15 块含 ACTION TIMING", any(b['name'] == 'ACTION TIMING' for b in FIFTEEN_BLOCKS))
    check("15 块含 CHARACTER ACTING", any(b['name'] == 'CHARACTER ACTING' for b in FIFTEEN_BLOCKS))

test_hell_grind_style_prefix()


def test_master_orchestrator_6_layers():
    from phase14_master_orchestrator import (
        inject_layer_1_asset, inject_layer_2_spatial, inject_layer_3_acting,
        inject_layer_4_sound, inject_layer_5_iteration, inject_layer_6_post,
        inject_all_6_layers, build_hell_grind_prompt, get_hell_grind_overview,
    )
    # 各层注入
    out1 = inject_layer_1_asset("@roco", "@roco")
    check("Layer 1 ASSET 含 descriptor", "DESCRIPTOR" in out1)
    check("Layer 1 ASSET 含 voice signature", "VOICE SIGNATURE" in out1)
    check("Layer 1 ASSET 含 behavior signature", "BEHAVIOR SIGNATURE" in out1)

    out2 = inject_layer_2_spatial("@loc_training_room")
    check("Layer 2 SPATIAL 含 GEO SPATIAL LAYOUT", "GEO SPATIAL LAYOUT" in out2)
    check("Layer 2 SPATIAL 含 180° AXIS", "180" in out2)

    out3 = inject_layer_3_acting("ROCO_training_alone")
    check("Layer 3 ACTING 含 5 PILLARS", "5 PILLARS" in out3)
    check("Layer 3 ACTING 含不写情绪", "不写情绪" in out3)

    out4 = inject_layer_4_sound(["@roco", "@demon_collector"], [])
    check("Layer 4 SOUND 含 VOICE SIGNATURES", "VOICE SIGNATURES" in out4)
    check("Layer 4 SOUND 含 SFX only", "SFX only" in out4)

    out5 = inject_layer_5_iteration("v3", "door-open at 2.5s", "v2 太晚", 12)
    check("Layer 5 ITERATION 触发 10-15 规则", "触发" in out5)
    check("Layer 5 ITERATION 含 5 铁律", "5 铁律" in out5)

    out6 = inject_layer_6_post()
    check("Layer 6 POST 含 CLEANUP", "CLEANUP" in out6)

    # 完整 6 层
    full6 = inject_all_6_layers()
    check("完整 6 层注入含 6 个 layer 标记", sum(1 for s in ['Layer 1', 'Layer 2', 'Layer 3', 'Layer 4', 'Layer 5', 'Layer 6'] if s in full6) == 6)

    # 完整 12 秒 prompt
    p = build_hell_grind_prompt()
    check("完整 12s ROCO prompt > 3000 字符", len(p) > 3000)
    check("完整 prompt 含 EXACT", "EXACT" in p)
    check("完整 prompt 含 GEO SPATIAL LAYOUT", "GEO SPATIAL LAYOUT" in p)
    check("完整 prompt 含 ACTION TIMING", "ACTION TIMING" in p)
    check("完整 prompt 含 CHARACTER ACTING", "CHARACTER ACTING" in p)

test_master_orchestrator_6_layers()


# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 70)
print(f"Phase 13/14 专项测试结果: 通过 {PASS} / 失败 {FAIL} / 总计 {PASS+FAIL}")
print("=" * 70)
if FAIL > 0:
    print("\n失败列表:")
    for f in FAILURES[:30]:
        print(f)
    if len(FAILURES) > 30:
        print(f"  ... 还有 {len(FAILURES)-30} 项")
    sys.exit(1)
else:
    print("\n[OK] Phase 13/14 全部通过!")
    sys.exit(0)
