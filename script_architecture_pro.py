# -*- coding: utf-8 -*-
"""
ScriptArchitecturePro — 故事架构节点
=====================================
(节点 1/3 — 剧本输出拆分为 3 个节点)

功能:
- 接收用户故事/题材
- 输出: 世界观 + 主题 + 角色小传 + 结构 + 节奏曲线
- 内置反 AI 词表 + 真实导演剧本微调
- 强制具体细节铁律
- 多轮迭代机制
- **Phase 17.6 灵魂注入**: 真实调用 director_soul.soul_inject_simple,
  按 灵魂_主导情感 / 灵魂_场景权重 / 灵魂_次要情感 / 灵魂_融合模式
  四个灵魂输入动态驱动故事架构, 不同情感真的会输出不同的
  情感核 / 强度 / 极性 / 视觉表现 / 色彩 / 音乐 / 灵魂状态 / 10 维

输入 (20 个核心参数 + 4 个灵魂参数):
- 题材/题材描述
- 时长/规模
- 主题(可多选 12 类)
- 风格基调(63 导演之一)
- 时代背景
- 地域文化
- 结构(经典三幕/英雄之旅/多线/反结构)
- 主角数量
- 反派数量
- 核心冲突类型
- 情绪曲线(7 点)
- 节奏密度
- 留白比例
- 反转次数
- 多线并行
- 隐喻层数
- 哲学内核
- 受众
- 禁忌词(额外反 AI)
- 启用反 AI 规则

灵魂输入 (Phase 17.6):
- 灵魂_主导情感 (auto + 60 EMOTION keys)
- 灵魂_次要情感 (auto + 60 keys, 单选, 走 secondary 列表)
- 灵魂_场景权重 (FLOAT 0-1, 决定故事强度)
- 灵魂_融合模式 (auto + F1-F7 7 种融合模式)

输出 (3-tuple, 不破坏现有 API):
- story_architecture: 注入反 AI 规则 + 真实导演微调 + 灵魂注入 的完整 prompt
- anti_ai_rules:     反 AI 词表 (1000 字符)
- iteration_chain:   多轮迭代链
"""

import os
import sys
import json

# 反 AI + 真实导演微调
try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES,
        SPECIFIC_DETAIL_RULES,
        HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS,
        ITERATION_TEMPLATES,
        inject_anti_ai_rules,
    )
    from director_real_scripts import ALL_DIRECTORS, build_micro_finetune_prompt
    _HAS_ANTI_AI = True
except Exception as e:
    _HAS_ANTI_AI = False
    _ANTI_AI_ERROR = str(e)

# ============================================================
# 灵魂注入依赖 (Phase 17.6) — 真实接入 director_soul
# ============================================================
try:
    from director_soul import (
        soul_inject_simple,
        EMOTION_MATRIX_60,
        EMOTION_FUSION_7,
        SOUL_DIMENSIONS_10,
    )
    _HAS_SOUL = True
except Exception as _soul_err:  # pragma: no cover
    _HAS_SOUL = False
    _SOUL_ERROR = str(_soul_err)
    # 兜底常量, 保证 INPUT_TYPES 仍然能返回
    EMOTION_MATRIX_60 = {}
    EMOTION_FUSION_7 = {}


# 主题分类(12 大类,真实人类剧作主题)
THEMES = [
    "爱与失去",
    "家庭与代际",
    "身份与归属",
    "权力与反抗",
    "孤独与连接",
    "记忆与时间",
    "城市与异化",
    "战争与和平",
    "信仰与怀疑",
    "阶层与流动",
    "生与死",
    "自由与责任",
]

# 经典叙事结构
STRUCTURES = [
    "经典三幕剧",
    "英雄之旅 12 阶段",
    "多线平行收敛",
    "非线性时间",
    "回环结构",
    "反结构 / 反高潮",
    "群像叙事",
    "公路片",
    "成长小说 (Bildungsroman)",
    "社会派推理",
    "心理悬疑",
    "日常流 (大时间跨度)",
]

# 核心冲突类型
CONFLICTS = [
    "人与人",
    "人与自我",
    "人与社会",
    "人与自然",
    "人与命运",
    "人vs过去",
    "理想vs现实",
    "道德vs欲望",
]

# 灵魂可选情感 (auto + none + 60 矩阵 keys)
SOUL_EMOTION_KEYS = (
    ["auto", "none"] + list(EMOTION_MATRIX_60.keys())
    if _HAS_SOUL else ["auto", "none"]
)
SOUL_FUSION_MODES = [
    "auto",
    "F1_单情感主导",
    "F2_双情感主次融合",
    "F3_双情感对等融合",
    "F4_三情感递进融合",
    "F5_矛盾情感爆炸",
    "F6_复合情绪三角",
    "F7_情感转化",
]


# ============================================================
# 灵魂注入块 (Phase 17.6 标准化输出)
# ============================================================
def _build_soul_injection(
    soul_primary,
    soul_secondary,
    soul_scene_weight,
    soul_fusion_mode,
    director,
    scene_context,
    story_intensity=None,
    scene_progress=0.5,
):
    """
    真实调用 director_soul.soul_inject_simple 注入灵魂.
    返回 4 元组: (injection_str, fused_dict, soul_state, soul_dims)
    失败时回落到中性占位, 不抛异常.
    """
    if not _HAS_SOUL:
        return (
            "【灵魂注入 - 依赖未加载】\n请检查 director_soul.py 是否存在: " + _SOUL_ERROR,
            {"name": "Neutral 中性", "intensity": 0.0, "polarity": "neutral",
             "arousal": "medium", "emotions": [], "fusion_mode": "none",
             "visual_signs": "", "voice_signs": "", "facial_au": "",
             "inner_monologue": "", "color_palette": "", "music_tempo": ""},
            {"inspiration": 0.7, "fatigue": 0.3, "doubt": 0.5,
             "rebelliousness": 0.6, "mental_state": "neutral"},
            {"creativity": 0.8, "imagination": 0.8, "artistic_expression": 0.8,
             "camera_skill": 0.8, "atmosphere_control": 0.8,
             "mental_state": "neutral", "inspiration": 0.8,
             "rebelliousness": 0.7, "self_doubt": 0.5, "breakthrough_courage": 0.7},
        )

    # 1. 解析输入 — soul_inject_simple 内部已做 alias 解析
    primary = soul_primary if soul_primary not in (None, "", "none") else "auto"
    secondary = None
    if soul_secondary and soul_secondary not in (None, "", "none", "auto"):
        secondary = [soul_secondary]

    # 2. 真实调用统一 wrapper
    try:
        inj, fused, soul_state, soul_dims = soul_inject_simple(
            primary=primary,
            scene_weight=float(soul_scene_weight),
            director=director or "默认",
            secondary=secondary,
            fusion_mode=soul_fusion_mode or "auto",
            story_intensity=story_intensity,
            scene_progress=scene_progress,
            scene_context=scene_context or "",
        )
        if not fused:
            fused = {
                "name": "Neutral 中性", "intensity": 0.0, "polarity": "neutral",
                "arousal": "medium", "emotions": [], "fusion_mode": "none",
                "visual_signs": "", "voice_signs": "", "facial_au": "",
                "inner_monologue": "", "color_palette": "", "music_tempo": "",
            }
        if not soul_state:
            soul_state = {"inspiration": 0.7, "fatigue": 0.3, "doubt": 0.5,
                          "rebelliousness": 0.6, "mental_state": "neutral"}
        if not soul_dims:
            soul_dims = {"creativity": 0.8, "imagination": 0.8, "artistic_expression": 0.8,
                         "camera_skill": 0.8, "atmosphere_control": 0.8,
                         "mental_state": "neutral", "inspiration": 0.8,
                         "rebelliousness": 0.7, "self_doubt": 0.5, "breakthrough_courage": 0.7}
        return inj, fused, soul_state, soul_dims
    except Exception as _e:
        # 真出错了: 用最小占位返回, 不要让整个 build 崩
        return (
            "【灵魂注入 - 运行失败】\n" + str(_e),
            {"name": "Neutral 中性", "intensity": 0.0, "polarity": "neutral",
             "arousal": "medium", "emotions": [], "fusion_mode": "none",
             "visual_signs": "", "voice_signs": "", "facial_au": "",
             "inner_monologue": "", "color_palette": "", "music_tempo": ""},
            {"inspiration": 0.7, "fatigue": 0.3, "doubt": 0.5,
             "rebelliousness": 0.6, "mental_state": "neutral"},
            {"creativity": 0.8, "imagination": 0.8, "artistic_expression": 0.8,
             "camera_skill": 0.8, "atmosphere_control": 0.8,
             "mental_state": "neutral", "inspiration": 0.8,
             "rebelliousness": 0.7, "self_doubt": 0.5, "breakthrough_courage": 0.7},
        )


def _format_soul_block(inj, fused, soul_state, soul_dims, director, scene_context):
    """
    把灵魂注入结果拼成清晰的文本块, 拼到 anti_ai_text 之后.
    这一块包含 fused['name'] (如 'Loneliness 孤独' / 'Apprehension 恐惧' / 'Warm Regret 温暖遗憾'),
    不同情感真的会输出不同文本.
    """
    lines = []
    lines.append("")
    lines.append("════════════════════════════════════════")
    lines.append("【Phase 17.6 灵魂注入 (Director Soul)】")
    lines.append("════════════════════════════════════════")
    # 1. 情感核心 (含 fused['name'])
    lines.append("")
    lines.append("【1. 情感核心 (Emotion Core)】")
    lines.append(f"主导情感 (fused name): {fused.get('name', 'Neutral 中性')}")
    lines.append(f"融合模式: {fused.get('fusion_mode', 'F1_单情感主导')}")
    emos = fused.get("emotions", []) or []
    lines.append(f"融合来源: {' + '.join(emos) if emos else '(无)'}")
    lines.append(f"强度: {float(fused.get('intensity', 0.0)):.2f}")
    lines.append(f"极性: {fused.get('polarity', 'neutral')}")
    lines.append(f"唤醒度: {fused.get('arousal', 'medium')}")

    # 2. 情感表达
    lines.append("")
    lines.append("【2. 情感表达 (Emotion Manifestation)】")
    vs = str(fused.get("visual_signs", "") or "").strip()
    if vs:
        lines.append(f"- 视觉表现: {vs[:500]}")
    vos = str(fused.get("voice_signs", "") or "").strip()
    if vos:
        lines.append(f"- 声音表现: {vos[:300]}")
    fau = str(fused.get("facial_au", "") or "").strip()
    if fau:
        lines.append(f"- 面部肌肉: {fau[:300]}")
    im = str(fused.get("inner_monologue", "") or "").strip()
    if im:
        lines.append(f"- 内心独白: {im[:300]}")

    # 3. 艺术氛围
    lines.append("")
    lines.append("【3. 艺术氛围 (Atmosphere)】")
    cp = str(fused.get("color_palette", "") or "").strip()
    if cp:
        lines.append(f"- 色彩: {cp[:300]}")
    mt = str(fused.get("music_tempo", "") or "").strip()
    if mt:
        lines.append(f"- 音乐: {mt[:300]}")

    # 4. 灵魂状态
    lines.append("")
    lines.append("【4. 灵魂状态 (Soul State)】")
    lines.append(f"灵感指数: {soul_state.get('inspiration', 0.0):.2f}")
    lines.append(f"疲劳指数: {soul_state.get('fatigue', 0.0):.2f}")
    lines.append(f"怀疑指数: {soul_state.get('doubt', 0.0):.2f}")
    lines.append(f"叛逆指数: {soul_state.get('rebelliousness', 0.0):.2f}")
    lines.append(f"精神状态: {soul_state.get('mental_state', 'neutral')}")

    # 5. 灵魂维度 (10 维度)
    lines.append("")
    lines.append("【5. 灵魂维度 (Soul Dimensions)】")
    lines.append(f"创造力: {soul_dims.get('creativity', 0.0):.2f}")
    lines.append(f"想象力: {soul_dims.get('imagination', 0.0):.2f}")
    lines.append(f"艺术表达: {soul_dims.get('artistic_expression', 0.0):.2f}")
    lines.append(f"镜头技巧: {soul_dims.get('camera_skill', 0.0):.2f}")
    lines.append(f"氛围掌控: {soul_dims.get('atmosphere_control', 0.0):.2f}")
    lines.append(f"精神状态: {soul_dims.get('mental_state', 'neutral')}")
    lines.append(f"灵感时刻: {soul_dims.get('inspiration', 0.0):.2f}")
    lines.append(f"叛逆度: {soul_dims.get('rebelliousness', 0.0):.2f}")
    lines.append(f"自我怀疑: {soul_dims.get('self_doubt', 0.0):.2f}")
    lines.append(f"突破勇气: {soul_dims.get('breakthrough_courage', 0.0):.2f}")

    # 6. 导演视角
    lines.append("")
    lines.append("【6. 导演视角 (Director Lens)】")
    lines.append(f"导演: {director or '默认'}")
    if scene_context:
        lines.append(f"场景: {scene_context[:100]}")
    lines.append("注入模式: SOUL_INJECTION_V1 (Phase 17.6 wrapper)")
    lines.append("════════════════════════════════════════")

    # 7. 原始 injection 字符串 (来自 director_soul.build_soul_injection, 完整版)
    if inj and isinstance(inj, str) and "导演灵魂注入" in inj:
        lines.append("")
        lines.append("【附: director_soul 原始注入 (build_soul_injection)】")
        lines.append(inj)
        lines.append("════════════════════════════════════════")

    return "\n".join(lines)


# ============================================================
# 节点类 (Phase 17.6 灵魂接入)
# ============================================================
class ScriptArchitecturePro:
    """
    故事架构节点 — 拆节点 1/3
    输出: 世界观 + 主题 + 角色 + 结构 + 节奏曲线 (+ Phase 17.6 灵魂注入)
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # === 1. 题材/输入 ===
                "题材": ("STRING", {
                    "default": "一段关于父女的故事, 在 1998 年哈尔滨",
                    "multiline": True,
                }),
                "片长分钟": ("INT", {"default": 120, "min": 1, "max": 600}),
                "集数": ("INT", {"default": 1, "min": 1, "max": 100}),

                # === 2. 主题与冲突 ===
                "主题_可多选": ("STRING", {
                    "default": "家庭与代际,记忆与时间,孤独与连接",
                    "multiline": False,
                }),
                "核心冲突": (CONFLICTS, {"default": "人与人"}),
                "哲学内核": ("STRING", {
                    "default": "失去的不可逆, 但记忆可以重建",
                    "multiline": True,
                }),

                # === 3. 风格与导演 ===
                "导演风格_63选1": ("STRING", {
                    "default": "王家卫",
                    "multiline": False,
                }),
                "时代背景": ("STRING", {
                    "default": "1990 年代",
                    "multiline": False,
                }),
                "地域文化": ("STRING", {
                    "default": "东北 / 香港 / 东京",
                    "multiline": False,
                }),

                # === 4. 结构 ===
                "叙事结构": (STRUCTURES, {"default": "经典三幕剧"}),
                "反转次数": ("INT", {"default": 1, "min": 0, "max": 5}),
                "多线并行": (["无", "双线", "三线", "四线+"], {"default": "无"}),
                "隐喻层数": ("INT", {"default": 1, "min": 0, "max": 4}),

                # === 5. 角色与受众 ===
                "主角数量": ("INT", {"default": 1, "min": 1, "max": 10}),
                "反派数量": ("INT", {"default": 1, "min": 0, "max": 5}),
                "目标受众": (["大众", "成人/艺术", "智性", "女性向", "男性向", "青少年"], {"default": "大众"}),

                # === 6. 节奏 ===
                "节奏密度": (["疏 (留白多)", "中", "密 (高信息)"], {"default": "中"}),
                "留白比例": (["10%以下", "30%", "50%", "70%", "90%以上"], {"default": "30%"}),
                "余韵强度": (["淡", "中", "重 (反转后留白)"], {"default": "中"}),

                # === 7. 灵魂注入 (Phase 17.6) — 真实驱动, 与 editing_pro.py 命名一致 ===
                "灵魂_主导情感": (SOUL_EMOTION_KEYS, {"default": "auto"}),
                "灵魂_次要情感": (SOUL_EMOTION_KEYS, {"default": "none"}),
                "灵魂_场景权重": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵魂_融合模式": (SOUL_FUSION_MODES, {"default": "auto"}),
            },
            "optional": {
                # === 8. 额外反 AI 配置 ===
                "额外禁用词": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                "启用反AI规则": ("BOOLEAN", {"default": True}),
                "多轮迭代": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("story_architecture", "anti_ai_rules", "iteration_chain")
    FUNCTION = "build_architecture"
    CATEGORY = "PromptLibrary/剧本输出"

    # ------------------------------------------------------------------
    # build_architecture — 真实灵魂驱动 (Phase 17.6)
    # ------------------------------------------------------------------
    def build_architecture(self, **kwargs):
        """构建故事架构 (含灵魂注入)"""
        # 0. 灵魂输入 (Phase 17.6) — 必须在最前面, 反 AI 块也要看灵魂色彩
        director = kwargs.get("导演风格_63选1", "王家卫")
        soul_primary = kwargs.get("灵魂_主导情感", "auto")
        soul_secondary = kwargs.get("灵魂_次要情感", "none")
        soul_scene_weight = kwargs.get("灵魂_场景权重", 0.5)
        soul_fusion_mode = kwargs.get("灵魂_融合模式", "auto")

        # 真实调用 director_soul.soul_inject_simple (统一 wrapper)
        inj, fused, soul_state, soul_dims = _build_soul_injection(
            soul_primary=soul_primary,
            soul_secondary=soul_secondary,
            soul_scene_weight=soul_scene_weight,
            soul_fusion_mode=soul_fusion_mode,
            director=director,
            scene_context=kwargs.get("题材", "") or kwargs.get("哲学内核", ""),
            story_intensity=soul_scene_weight,  # 故事强度 = 场景权重
            scene_progress=0.5,                 # 故事架构节点: 进度 0.5
        )

        # 注入反 AI 规则
        if _HAS_ANTI_AI:
            user_prompt = f"""【任务: 为以下故事生成完整架构】

题材: {kwargs.get('题材', '')}
片长: {kwargs.get('片长分钟', '')} 分钟
集数: {kwargs.get('集数', '')}
主题: {kwargs.get('主题_可多选', '')}
核心冲突: {kwargs.get('核心冲突', '')}
哲学内核: {kwargs.get('哲学内核', '')}
导演风格: {director}
时代背景: {kwargs.get('时代背景', '')}
地域文化: {kwargs.get('地域文化', '')}
叙事结构: {kwargs.get('叙事结构', '')}
反转次数: {kwargs.get('反转次数', '')}
多线并行: {kwargs.get('多线并行', '')}
隐喻层数: {kwargs.get('隐喻层数', '')}
主角数量: {kwargs.get('主角数量', '')}
反派数量: {kwargs.get('反派数量', '')}
目标受众: {kwargs.get('目标受众', '')}
节奏密度: {kwargs.get('节奏密度', '')}
留白比例: {kwargs.get('留白比例', '')}
余韵强度: {kwargs.get('余韵强度', '')}

【输出格式 JSON】
{{
  "worldview": "世界观的 3-5 句话具象描述",
  "theme": "主题的具象呈现(不用'关于'XXX 直接说XXX)",
  "characters": [
    {{"name": "姓名", "age": 年龄, "body": "身体特征", "habit": "身体习惯", "object": "标志性物件", "arc": "人物弧光"}}
  ],
  "structure": "分幕/分集结构, 每幕用一句话+一个关键场景",
  "pacing_curve": [0.0-1.0, 0.0-1.0, 0.0-1.0, 0.0-1.0, 0.0-1.0, 0.0-1.0, 0.0-1.0],
  "metaphysics": "哲学内核的具象呈现",
  "direct_signature": "{director}的标志性手法怎么用在本题材"
}}
"""
            # 注入反 AI 规则
            if kwargs.get("启用反AI规则", True):
                anti_ai_text = inject_anti_ai_rules(user_prompt, director if director in DIRECTOR_ANTI_AI_PROMPTS else "")
            else:
                anti_ai_text = user_prompt

            # 注入真实导演微调
            if director in ALL_DIRECTORS:
                micro_tune = build_micro_finetune_prompt(director, "故事架构")
                anti_ai_text = f"{anti_ai_text}\n\n{micro_tune}"

            # 注入额外禁用词
            extra_ban = kwargs.get("额外禁用词", "")
            if extra_ban:
                anti_ai_text += f"\n\n【额外禁用词(必须严格遵守)】\n{extra_ban}"

            # ============================================================
            # Phase 17.6 灵魂块: 拼到 anti_ai_text 后面
            # 真实数据来源: director_soul.soul_inject_simple 的返回
            # 不同 灵魂_主导情感 → fused['name'] 不同 → 整段灵魂块不同
            # ============================================================
            soul_block = _format_soul_block(
                inj, fused, soul_state, soul_dims,
                director=director,
                scene_context=kwargs.get("题材", "") or "",
            )
            anti_ai_text = f"{anti_ai_text}\n\n{soul_block}"

            # 多轮迭代链
            if kwargs.get("多轮迭代", True):
                iter_chain = [
                    ITERATION_TEMPLATES["round_1_draft"].format(
                        theme=kwargs.get("主题_可多选", ""),
                        characters=f"{kwargs.get('主角数量', 1)} 主角 + {kwargs.get('反派数量', 1)} 反派",
                        structure=kwargs.get("叙事结构", ""),
                        pacing=kwargs.get("节奏密度", ""),
                    ),
                    ITERATION_TEMPLATES["round_2_anti_ai"],
                    ITERATION_TEMPLATES["round_3_humanize"],
                    ITERATION_TEMPLATES["round_4_director_polish"].format(
                        director=director,
                        camera_style="按" + director + "的镜头习惯",
                        pacing_style=kwargs.get("节奏密度", "中"),
                        theme_focus=kwargs.get("主题_可多选", ""),
                        visual_signature="按" + director + "的视觉签名",
                    ),
                ]
                iter_text = "\n\n=========\n\n".join(iter_chain)
            else:
                iter_text = "未启用多轮迭代"

            return (
                anti_ai_text,  # story_architecture(反 AI + 真实导演微调 + Phase 17.6 灵魂注入)
                json.dumps({k: v for k, v in ANTI_AI_PHRASES.items() if k}, ensure_ascii=False)[:1000] if _HAS_ANTI_AI else "未加载",
                iter_text,
            )
        else:
            # 没有反 AI 词表时, 简单 prompt + 灵魂注入 (灵魂注入是独立的, 不依赖 anti_ai)
            soul_block = _format_soul_block(
                inj, fused, soul_state, soul_dims,
                director=director,
                scene_context=kwargs.get("题材", "") or "",
            )
            return (
                f"题材: {kwargs.get('题材','')}\n输出: 故事架构 JSON\n\n{soul_block}",
                "反 AI 词表未加载: " + _ANTI_AI_ERROR if not _HAS_ANTI_AI else "",
                "未启用多轮迭代",
            )


# 节点注册映射
NODE_CLASS_MAPPINGS = {
    "ScriptArchitecturePro": ScriptArchitecturePro,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ScriptArchitecturePro": "📖 剧本架构 (1/3)",
}
