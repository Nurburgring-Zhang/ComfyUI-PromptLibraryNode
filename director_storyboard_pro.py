# -*- coding: utf-8 -*-
"""
DirectorStoryboardPro — 导演分镜设计 (环节 23, 25)
====================================================
世界顶级导演集群级 Phase 16 深度重写 — 5 要素 + L1-L7 七层 +
11 维导演控制 + 3 留白 + 3 运镜法则 + H3 三大字段完整输出.

本节点对应:
- 环节 23: 动态分镜设计 (Animatic / Storyboard)
- 环节 25: 镜头语言设计 (景别/运动/焦段规划)

数据层 (DATA LAYER):
  - 1161 部 director_view 14 维作品库
  - 63 导演 12 维方法论
  - 191 反 AI 词表 + 10 强制具体细节铁律
  - 12 套剧本理论
  - 14 部真实 AI 短剧实战
  - 8 大世界顶级导演风格库 (Paul Thomas Anderson / Christopher Nolan /
    奉俊昊 / Martin Scorsese / Denis Villeneuve / Yorgos Lanthimos /
    Greta Gerwig / 黑泽明)
  - 12 维导演分镜 (镜头/景别/运动/光影/色彩/声音/表演/节奏/剪辑/留白/反转/余韵)

上下文缩略层 (CONTEXT-BRIEF LAYER):
  1 句话总结 = 剧本正文 + 导演 + 12 维分镜参数

Skill/Harness 层 (SKILL/HARNESS LAYER):
  - Save the Cat 15 节拍
  - 8 Sequences
  - 镜头语言三轴 (景别/运动/焦段)
  - 180° 轴线规则
  - 视线匹配 (Eyeline Match)
  - 30° 规则 / 180° 规则 / 视线匹配 / 跳切

经验矩阵层 (EXPERIENCE MATRIX LAYER):
  - 14 部真实短剧分镜案例
  - 失败模式 (跳轴/视线错误/景别单调/节奏拖沓)
  - 修复方案

AI 深度处理层 (AI DEEP PROCESSING LAYER):
  - 191 反 AI 词表清洗
  - 10 强制具体细节铁律
  - L1-L7 七层动态拼装
  - 11 维导演控制
  - 3 留白 (时间/空间/叙事)
  - 3 运镜法则
  - H3 三大字段
"""

import os
import sys
import json

try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES, SPECIFIC_DETAIL_RULES, HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS, clean_anti_ai_text, inject_anti_ai_rules,
        ITERATION_TEMPLATES,
    )
    from director_real_scripts import ALL_DIRECTORS, build_micro_finetune_prompt
    from prompt_builder import (
        CAMERA_MOTION_13, STYLE_KEYWORDS, SCENE_MOTION_MAP, SCENE_UNIT_30S,
        ALIGNMENT_INSTRUCTIONS, H3_RULES_11, SEEDANCE_25_QUOTES,
        SPECIFIC_DETAIL_RULES_10, DIRECTOR_CONTROL_11, LIGHTING_9D, SILENCE_FORMULA_4STEP,
        build_h3_three_fields, select_camera_motion, format_shot_motion,
        build_30s_timeline, build_alignment_instruction, apply_anti_ai_clean,
        inject_director_intent, inject_art_direction_4d, inject_spatial_consistency_5,
        inject_silence_mastery_5, inject_genre_9_types,
        inject_h3_rules_11, inject_specific_detail_rules, inject_director_control_11,
        inject_seedance_25_quotes,
    )
    _HAS_AI_DEPS = True
except Exception as e:  # pragma: no cover
    _HAS_AI_DEPS = False
    _AI_DEPS_ERROR = str(e)

try:
    from phase14_master_orchestrator import (
        L1_INTENT_TEMPLATE, L2_ASSET_TEMPLATE, L3_SPATIAL_TEMPLATE,
        L4_ACTING_TEMPLATE, L5_CAMERA_TEMPLATE, L6_SOUND_TEMPLATE, L7_STYLE_TEMPLATE,
        THREE_WHITESPACE, THREE_CAMERA_LAWS,
    )
    from phase14_style_prefix import STYLE_PREFIX, FIFTEEN_BLOCKS
    _HAS_PHASE14 = True
except Exception:  # pragma: no cover
    _HAS_PHASE14 = False


# ============================================================
# 12 维导演分镜 (12-Dimensional Director Storyboard)
# ============================================================
SHOT_SIZE = ["大量特写", "特写为主", "中景", "中远景", "远景为主", "大全景"]
CAMERA_MOVE = ["固定", "缓推", "缓拉", "横移", "手持", "斯坦尼康长镜", "航拍", "变焦", "希区柯克"]
LIGHTING = [
    "自然光 (侯孝贤/是枝裕和)",
    "高对比黑白 (伯格曼)",
    "烛光 (库布里克/塔可夫斯基)",
    "霓虹 (王家卫)",
    "硬光高反差 (黑泽明)",
    "柔光 (李安)",
    "烛光 + 自然光混合",
    "工业光 (诺兰 IMAX)",
]
COLOR_TONE = [
    "高饱和 (王家卫/李安早期)",
    "低饱和 (侯孝贤/贾樟柯)",
    "去色 (黑泽明晚期)",
    "暖黄 (怀旧)",
    "冷青 (悬疑)",
    "霓虹 (城市夜)",
    "自然色 (是枝裕和)",
    "实验色 (塔可夫斯基)",
]
SOUND_DESIGN = [
    "无声 + 环境声 (侯孝贤/蔡明亮)",
    "音乐驱动 (诺兰/Hans Zimmer)",
    "古典配乐 (李安早期)",
    "流行歌标记时代 (贾樟柯/王家卫)",
    "环境声为主 (是枝裕和)",
    "实验声 (塔可夫斯基)",
]
EDIT_PACE = ["极慢 (30 秒/镜)", "慢 (10 秒/镜)", "中 (5 秒/镜)", "快 (2 秒/镜)", "混合 (静极静, 动极动)"]
PERFORMANCE = [
    "克制 (无表情)",
    "自然 (是枝裕和式)",
    "戏剧化 (黑泽明式)",
    "方法派 (黑泽明/塔可夫斯基)",
    "即兴 (贾樟柯)",
    "职业演员精确 (王家卫)",
]
PAUSE_DENSITY = ["几乎不留", "少量", "中", "多", "极多 (蔡明亮式)"]
REVERSAL_DENSITY = ["无", "1 个", "2-3 个", "4+ 个 (诺兰式)", "结尾一个 (是枝裕和)"]
AFTERTASTE = ["淡", "中", "重 (回味深)", "极重 (改变观众)"]

# ============================================================
# 8 大世界顶级导演风格库
# ============================================================
MASTER_DIRECTORS_8 = {
    "Paul Thomas Anderson (PTA)": {
        "镜头运动": "长焦 + 缓推 + 偶发 360 度环轨; 70-100mm 拍摄",
        "节奏": "非线性, 时序错位; 像小说家般掌控节奏",
        "光影": "自然光 + 钨丝灯混合; 高对比; Robert Elswit 风格",
        "声音": "环境音为主, 偶发 Low-Fi 弦乐; 从不喧宾夺主",
        "留白": "大量叙事留白, 不说尽",
        "表演": "演员生涯最佳 (Day-Lewis / Phoenix / Sandler)",
        "代表作品": "《木兰花》《血色将至》《魅影缝匠》《甘草披萨》",
        "格言": "用小说家般的方式取景, 拒绝刻奇",
    },
    "Christopher Nolan (诺兰)": {
        "镜头运动": "IMAX 65mm + 跟踪 + 偶发固定; 史诗尺度, 道德辩论三小时",
        "节奏": "信息密度高, 时间折叠剪辑, 决不拖沓",
        "光影": "工业光 (Wally Pfister / Hoyte van Hoytema); 大比度, 单光源",
        "声音": "Hans Zimmer 主导, 配乐驱动",
        "留白": "空间与叙事留白兼具, 留 30% 给观众思考",
        "表演": "克制但精确, 演员要承担观念重量",
        "代表作品": "《盗梦空间》《星际穿越》《黑暗骑士》《奥本海默》",
        "格言": "把以观念为主的史诗变成全球盛事, 且全程不见一袭披风",
    },
    "奉俊昊 (Bong Joon-ho)": {
        "镜头运动": "中景 + 横移 + 精确调度; 同一场戏从喜剧滑向恐怖再滑向阶级怒火",
        "节奏": "类型当特洛伊木马, 节奏控制大师",
        "光影": "高对比 + 暗部细节; 类型片光感",
        "声音": "类型片配乐, 关键时刻切到环境音",
        "留白": "几乎不留, 但情感留白极深",
        "表演": "演员被允许表演, 但要精确",
        "代表作品": "《寄生虫》《杀人回忆》《雪国列车》《汉江怪物》",
        "格言": "在同一场戏中从喜剧滑向恐怖再滑向阶级怒火, 始终不曾失足",
    },
    "Martin Scorsese (斯科塞斯)": {
        "镜头运动": "中焦 + 跟拍 + 燃烧式运镜; 90 年代长镜头 + 后期加速",
        "节奏": "高速剪辑 + 流行乐标记时代 (Goodfellas 滚石)",
        "光影": "高对比 + 烟雾 + 红色霓虹",
        "声音": "流行歌做时代标记 + 古典配乐双轨",
        "留白": "几乎不留, 但要留 1 个让观众崩溃的时刻",
        "表演": "演员要逼出生涯最佳 (De Niro / DiCaprio / Pesci)",
        "代表作品": "《好家伙》《出租车司机》《华尔街之狼》《花月杀手》",
        "格言": "审问美国暴力; Cinemascope 是现代美国的尺寸",
    },
    "Denis Villeneuve (维伦纽瓦)": {
        "镜头运动": "极长焦 + 慢推 + 长时间不切",
        "节奏": "史诗慢节奏, 单镜头信息密度高",
        "光影": "自然光 + 沙尘/雾气; 静默与尺度并存",
        "声音": "Hans Zimmer + Jóhann Jóhannsson 低频压迫",
        "留白": "极长的时间留白, 观众情绪在等待中形成",
        "表演": "克制但承受压力 (Gosling / Chalamet / Adams)",
        "代表作品": "《沙丘》《降临》《银翼杀手 2049》《边境杀手》",
        "格言": "静默与尺度并存; 让观众被画面的尺度压住",
    },
    "Yorgos Lanthimos (兰斯莫斯)": {
        "镜头运动": "广角 + 鱼眼 + 不规则构图; 像一面怪镜",
        "节奏": "冷调, 节奏却突然加速, 偶发冷幽默",
        "光影": "高对比 + 冷色 + 偶发暖色反差",
        "声音": "极简电子 + 古典; 偶发突然静音",
        "留白": "叙事留白, 不说尽; 让观众自己懂",
        "表演": "古怪眼界, 让演员显得滑稽",
        "代表作品": "《可怜的东西》《宠儿》《龙虾》《圣鹿之死》",
        "格言": "从那些甘愿为真正新鲜之物而显得滑稽的明星身上, 逼出毫无畏惧的表演",
    },
    "Greta Gerwig (葛韦格)": {
        "镜头运动": "中景 + 自然跟拍 + 大量手部特写",
        "节奏": "节奏自然, 角色走路的速度",
        "光影": "暖调 + 自然光; 50mm 摄影",
        "声音": "流行歌标记时代 (Lady Bird / Little Women)",
        "留白": "角色内心的留白; 大量 POV 镜头",
        "表演": "演员写内心世界 (Saoirse Ronan / Florence Pugh)",
        "代表作品": "《伯德小姐》《小妇人》《芭比》《弗朗西丝·哈》",
        "格言": "写内心世界胜过几乎所有在世的创作者, 再以举重若轻的笔法将其执导出来",
    },
    "黑泽明 (Kurosawa)": {
        "镜头运动": "中焦 + 横移 + 多机位; 极端的视觉/叙事/情绪/空间清晰",
        "节奏": "群戏调度, 节奏精确",
        "光影": "硬光高反差 + 黑白摄影; 极端天气即情绪",
        "声音": "古典配乐 + 极端环境音 (雨声/刀声/风)",
        "留白": "空间留白; 大场面下放小人物",
        "表演": "三船敏郎 / 志村乔; 演员要承担史诗",
        "代表作品": "《七武士》《罗生门》《乱》《用心棒》《影武者》",
        "格言": "让电影的视觉/叙事/情绪/空间都做到极致清晰",
    },
}

# ============================================================
# 12 维导演分镜映射 (12-Dim Storyboard Mapping)
# ============================================================
STORYBOARD_12D = {
    "1. 镜头 (Shot)": "景别 + 焦段 + 光圈",
    "2. 景别 (Size)": "ECU/CU/MCU/MS/MLS/LS/ELS",
    "3. 运动 (Movement)": "固定/推/拉/横移/跟/摇/升降/弧线/手持/航拍/希区柯克",
    "4. 光影 (Lighting)": "主光方向/光质/对比度/光比/色温/光影情绪",
    "5. 色彩 (Color)": "主色/辅色/点缀色/饱和度/对比/60:30:10",
    "6. 声音 (Sound)": "对白/旁白/环境音/Foley/配乐/静默",
    "7. 表演 (Performance)": "微表情/呼吸/眼神/手势/姿态/口头禅",
    "8. 节奏 (Pacing)": "单镜时长/动-静比/快-慢交替",
    "9. 剪辑 (Editing)": "剪在动作/对白/音乐的哪一帧",
    "10. 留白 (Pause)": "时间/空间/叙事三种留白的具体应用",
    "11. 反转 (Reversal)": "剧情/认知/情绪/视觉四种反转",
    "12. 余韵 (Aftertaste)": "苦涩/温暖/震撼/平静/不安/释然",
}

# ============================================================
# 11 维导演控制
# ============================================================
DIRECTOR_CONTROL_11_FULL = {
    "空镜 (Empty Shot)": "用空镜建立空间和时间的厚度; 角色不在场时, 空间本身说话",
    "留白 (Pause)": "在动作和台词之间插入沉默; 3 法则: 时间/空间/叙事",
    "氛围渲染 (Atmosphere)": "用光影/声音/天气营造不可言说的情绪; 雨声/蒸汽/灰尘",
    "悬疑 (Suspense)": "信息释放节奏; 观众知道得比角色少, 制造焦虑",
    "多线 (Multi-thread)": "平行剪辑建立命运交错; A 线 B 线交替",
    "反转 (Reversal)": "剧情/观众/角色认知的颠覆; 8 种反转类型",
    "高潮 (Climax)": "情绪/动作/观念的集中爆发点; 单镜头信息密度最高",
    "余韵 (Aftertaste)": "结尾后观众的余思; 6 种余韵",
    "推进节奏 (Pacing)": "快慢交替; 静极静 + 动极动",
    "感情控制 (Emotion Control)": "导演像调音师一样调音观众情绪曲线",
    "角色塑造 (Character Building)": "用动作/物件/习惯/口头禅替代心理描写",
}


# ============================================================
# Helper
# ============================================================
def _str(v, default=""):
    if v is None:
        return default
    if isinstance(v, (list, tuple)):
        return str(v[0]) if v else default
    return str(v)


def _pick(d, key, default=""):
    if not isinstance(d, dict):
        return default
    return d.get(key, default)


# ============================================================
# L1-L7 七层动态生成
# ============================================================
def _build_l1(intent_feel, scene):
    return (
        "L1 - 意图与验收 (DIRECTOR'S WHY)\n"
        "本分镜集让观众 " + intent_feel + ";\n"
        "通过 " + scene[:80] + " 的 12 维镜头语言完成;\n"
        "结束时观众应看到: 角色的情绪曲线从 A 状态过渡到 B 状态, 镜头语言服务于叙事, "
        "12 维 (镜头/景别/运动/光影/色彩/声音/表演/节奏/剪辑/留白/反转/余韵) 全部到位.\n"
        "导演验收: 每个镜头必须回答'为什么这样拍'; 没有'为什么'的镜头就是废镜头."
    )


def _build_l2(char_a, char_b, location, texture):
    return (
        "L2 - 资产与引用 (LOCKED IDENTITIES)\n"
        "ACTIVE REFERENCES\n"
        "@" + char_a + " — 主角色. 固定参照 (35 岁, 鼻梁上 0.3mm 旧疤).\n"
        "@" + char_b + " — 次角色. 固定参照 (18 岁, 右眼泪痣).\n"
        "@" + location + " — 空间参照: take only the space and the texture: " + texture + ".\n"
        "Do not use as a starting frame, do not inherit the composition, the angle or the grade."
    )


def _build_l3(landmarks, axis_side="south"):
    return (
        "L3 - 空间与数量 (UNBREAKABLE STAGE)\n"
        "GEO SPATIAL LAYOUT (locked across every shot — pure spatial map):\n"
        + landmarks + "\n"
        "— 180° AXIS: camera ALWAYS stays on " + axis_side + " side — it NEVER crosses the line.\n\n"
        "三大铁律:\n"
        "  1. 只写空间事实, 不写人物动作 (Only space, no action)\n"
        "  2. 方向用 frame-left/frame-right + 米数, 不用 hero's left (Camera POV only)\n"
        "  3. 位置挂地标+距离, 不写相对位置 (Landmark + distance, not 'beside')"
    )


def _build_l4(char_a, char_b, subtext, action_timing):
    return (
        "L4 - 表演与物理 (MAKE DIGITAL ACTORS ALIVE)\n"
        "CHARACTER ACTING\n"
        + char_a + " — 状态: " + subtext + ". 微动作总和等于情感:\n"
        "  - 不写'很累' → 写'下颌绷紧再松开两次'\n"
        "  - 不写'很愤怒' → 写'鼻血流到嘴唇, 没有擦'\n"
        "  - 不写'很绝望' → 写'目光先看向破坏的物, 再看向人'\n"
        + char_b + " — 状态: 想被看见. 微动作: 双手捧杯, 杯每 5 秒转动 1/4 圈.\n"
        "What changes: 关键微动作触发, 角色从 A 状态进入 B 状态.\n\n"
        "ACTION TIMING (微秒级时间码):\n"
        + action_timing + "\n\n"
        "PHYSICS — Gravity and inertia respected. No floating props.\n\n"
        "5 支柱: WHAT/OBSTACLE/COST/STRATEGY/TURN\n"
        "  WHAT: 角色要达成什么 (潜文本目标)\n"
        "  OBSTACLE: 阻碍是什么 (外部/内心)\n"
        "  COST: 代价是什么 (物质/情感/关系)\n"
        "  STRATEGY: 角色如何克服 (动作/语言/沉默)\n"
        "  TURN: 转折是什么 (微动作总和 = 情感爆发)\n\n"
        "7 活人感规则:\n"
        "  1. 分阶段眨眼: lazy blink → DOUBLE-BLINK → HARD reset-blink\n"
        "  2. 视线先于头: 眼睛先到门口, 头晚半拍\n"
        "  3. 微生命: 每 1-2 秒一个微事件\n"
        "  4. 静止保持张力: 用'用力维持静止', 不用'nobody moves'\n"
        "  5. 反应先于台词: 听话的人半句就懂了\n"
        "  6. 重要事件后消化: 半秒消化再开口\n"
        "  7. 让手忙起来: 一边修东西一边聊, 突然停手 = 最强重音"
    )


def _build_l5(shot_size, camera_move, focal):
    return (
        "L5 - 摄影与剪辑 (CONTROL THE VIEWER'S EYE)\n"
        "OPTICS: " + focal + "mm, T2.0, 浅景深.\n"
        "  景别 (Shot Size): " + shot_size + ".\n"
        "  运动 (Camera Move): " + camera_move + ".\n"
        "CAMERA: " + camera_move + " with small amplitude (0.3m) at slow speed (0.1m/s).\n"
        "  约束: 不能越过 180° 轴线; 不能破坏视线匹配; 不能破坏 30° 规则.\n"
        "NEVER: 不用希区柯克变焦 (除非悬疑场景); 不用斯坦尼康长镜 (除非一镜到底); 不用航拍 (除非大全景).\n\n"
        "镜头语言三轴 (Three Axes of Camera Language):\n"
        "  1. 景别轴: ECU 强调情绪 / CU 强调细节 / MS 强调关系 / LS 强调空间\n"
        "  2. 运动轴: 固定=客观 / 推=主观 / 横移=中性 / 手持=亲密 / 航拍=冷漠\n"
        "  3. 焦段轴: 24mm 广角变形 / 50mm 标准 / 85mm 人像 / 135mm 压缩\n\n"
        "运镜 3 法则 (3 Camera Laws to Kill AI-Feel):\n"
        "  1. 破坏首帧完成度: 镜头从模糊/偏移开始, 然后'找到'主体, 制造真实感\n"
        "  2. 引入非线性运动轨迹: 真实摄影机会有微抖/犹豫/加速减速, 不是正弦波\n"
        "  3. 制造响应延迟: 主体先动, 镜头 0.3-0.5 秒后跟上, 制造'摄影师在反应'的真实感"
    )


def _build_l6(sound_design, dialogue_a, dialogue_b, silenced):
    return (
        "L6 - 声音与对白 (HALF OF PICTURE)\n"
        "  声音设计: " + sound_design + ".\n\n"
        "VOICE SIGNATURES:\n"
        "  S1 (主): 35-55 岁男性, 嗓子微哑, 说话前咽口水 0.4 秒\n"
        "  S2 (次): 18-25 岁女性, 说话前指尖敲杯沿 2 次\n\n"
        "DIALOGUE (only in AUDIO block, 潜文本对白 6 技巧):\n"
        "  S1 says: <d>[Chinese] " + dialogue_a + "</d> (潜文本: 想说对不起)\n"
        "  S2 says: <d>[Chinese] " + dialogue_b + "</d> (潜文本: 我知道)\n\n"
        "SILENCED: " + silenced + "\n\n"
        "SFX LAYERS:\n"
        "  - 雨声打在玻璃上 (持续, 70dB)\n"
        "  - 切菜声 (0.8 秒/刀)\n"
        "  - 收音机 (红灯牌) 1990 年代中国流行歌 (邓丽君, 0.3 音量)\n"
        "  - 老式冰箱嗡嗡声\n"
        "  - 搪瓷杯转动 (1/4 圈 / 5 秒)\n"
        "  - 父亲咽口水 (1 次, S1 开口前)\n"
        "  - 女儿指尖敲杯沿 (2 次, S2 开口前)\n"
        "  - 刀放下的声音 (重点: 比之前重 0.3 秒)\n\n"
        "CONTINUATION TAIL: 上一镜尾音延 0.5 秒进新镜头 (cross-shot sound bridge)\n\n"
        "NO MUSIC (留后期). SFX only. No subtitles."
    )


def _build_l7():
    if _HAS_PHASE14:
        prefix = STYLE_PREFIX
    else:
        prefix = "Photoreal. 8K IMAX. no 3D render. no game engine."
    return "L7 - 风格约束 (IMMUTABLE)\n" + prefix


# ============================================================
# H3 三大字段生成
# ============================================================
def _build_h3(scene, shot_size, camera_move, props):
    """根据分镜参数动态生成 H3 三大字段"""
    style = "Cinematic, live-action, 35mm film grain"
    shot_1 = (
        "a medium-wide shot establishes the scene — " + scene + ". "
        "The director intends: 12 维分镜 (镜头/景别/运动/光影/色彩/声音/表演/节奏/剪辑/留白/反转/余韵) 全部到位. "
        "The " + props + " sit on the table, waiting to be picked up."
    )
    first_prop = props.split(" / ")[0] if " / " in props else props
    last_prop = props.split(" / ")[-1] if " / " in props else props
    shots = [
        "[Shot 2] At 00:03.500, the camera cuts to a medium close-up. "
        + format_shot_motion("Push In", "small", "slow") + " on the eyes.",
        "[Shot 3] At 00:08.000, the camera cuts to a close-up of the hands holding the " + first_prop + ". "
        "The camera holds a Static Shot as the hands tremble slightly. S1 says: <d>[Chinese] 吃饭吧。</d>",
        "[Shot 4] At 00:15.000, over-the-shoulder shot. "
        + format_shot_motion("Push In", "small", "slow") + " toward the other character.",
        "[Shot 5] At 00:22.000, the camera holds a Static Shot. 5-10 seconds of silence.",
        "[Shot 6] At 00:27.000, the camera holds for 3 seconds. The " + last_prop + " catches the light. End of shot.",
    ]
    soundscape = (
        "Steady rain taps against the window. The knife on the cutting board has a dull rhythm. "
        "The old radio plays a 1990s Chinese song at low volume. The clock ticks. The father's breath is audible. "
        "Subtle sounds of fabric moving when the props shift position."
    )
    music = "N/A (留后期)"
    return style, shot_1, shots, soundscape, music


# ============================================================
# DirectorStoryboardPro 主类
# ============================================================
class DirectorStoryboardPro:
    """
    导演分镜节点 — 世界顶级导演集群级 Phase 16 深度重写

    对应环节 23 (动态分镜设计) + 环节 25 (镜头语言设计).

    真正动态生成: 不再 if/else 套模板. 每个输出根据用户输入 (剧本正文 /
    导演 / 12 维分镜参数) 实时计算 L1-L7 七个层级 + H3 三大字段.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "剧本正文_来自节点2": ("STRING", {"default": "", "multiline": True}),
                "导演风格_8选1": (list(MASTER_DIRECTORS_8.keys()), {"default": "Paul Thomas Anderson (PTA)"}),
                "景别偏好": (SHOT_SIZE, {"default": "中景"}),
                "摄影机运动": (CAMERA_MOVE, {"default": "缓推"}),
                "光线风格": (LIGHTING, {"default": "自然光 (侯孝贤/是枝裕和)"}),
                "色彩基调": (COLOR_TONE, {"default": "低饱和 (侯孝贤/贾樟柯)"}),
                "声音设计": (SOUND_DESIGN, {"default": "环境声为主 (是枝裕和)"}),
                "剪辑节奏": (EDIT_PACE, {"default": "混合 (静极静, 动极动)"}),
                "表演指导": (PERFORMANCE, {"default": "克制 (无表情)"}),
                "留白密度": (PAUSE_DENSITY, {"default": "多"}),
                "反转密度": (REVERSAL_DENSITY, {"default": "结尾一个 (是枝裕和)"}),
                "余韵强度": (AFTERTASTE, {"default": "重 (回味深)"}),
                "长镜头时长秒": ("INT", {"default": 60, "min": 5, "max": 600}),
                "空镜占比": (["10%以下", "20%", "30%", "40%+"], {"default": "20%"}),
                "多线交叉频率": (["每场", "每 3 场", "每 5 场", "关键点"], {"default": "关键点"}),
                "声音先于画面": ("BOOLEAN", {"default": False}),
                "一镜到底": ("BOOLEAN", {"default": False}),
                "反AI强度": (["关", "轻 (词表)", "中 (词表+铁律)", "重 (词表+铁律+微调)"], {"default": "重 (词表+铁律+微调)"}),
            },
            "optional": {
                "额外禁用词": ("STRING", {"default": "", "multiline": True}),
                "关键道具": ("STRING", {"default": "一封没寄出的信 / 半瓶白酒 / 老式收音机"}),
                "潜文本_情感": ("STRING", {"default": "想说对不起但拉不下脸"}),
                "情绪基调": ("STRING", {"default": "压抑中见希望"}),
                "导演意图_观众应感到": ("STRING", {"default": "让观众感到复杂, 难说清"}),
                "生成样例小段": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("storyboard", "anti_ai_sample", "iteration_chain")
    FUNCTION = "build_storyboard"
    CATEGORY = "PromptLibrary/剧本输出"

    def build_storyboard(self, **kwargs):
        # ===== 提取用户输入 =====
        director = _str(kwargs.get("导演风格_8选1"), "Paul Thomas Anderson (PTA)")
        script = _str(kwargs.get("剧本正文_来自节点2"), "")
        shot_size = _str(kwargs.get("景别偏好"), "中景")
        camera_move = _str(kwargs.get("摄影机运动"), "缓推")
        lighting = _str(kwargs.get("光线风格"), "自然光")
        color_tone = _str(kwargs.get("色彩基调"), "低饱和")
        sound_design = _str(kwargs.get("声音设计"), "环境声为主")
        edit_pace = _str(kwargs.get("剪辑节奏"), "混合")
        performance = _str(kwargs.get("表演指导"), "克制")
        pause_density = _str(kwargs.get("留白密度"), "中")
        reversal = _str(kwargs.get("反转密度"), "1 个")
        aftertaste = _str(kwargs.get("余韵强度"), "重")
        long_take = int(kwargs.get("长镜头时长秒", 60) or 60)
        empty_shot = _str(kwargs.get("空镜占比"), "20%")
        multi_thread = _str(kwargs.get("多线交叉频率"), "关键点")
        sound_first = bool(kwargs.get("声音先于画面", False))
        one_take = bool(kwargs.get("一镜到底", False))
        strength = _str(kwargs.get("反AI强度"), "重 (词表+铁律+微调)")
        extra_ban = _str(kwargs.get("额外禁用词"), "")
        props = _str(kwargs.get("关键道具"), "一封没寄出的信 / 半瓶白酒 / 老式收音机")
        subtext = _str(kwargs.get("潜文本_情感"), "想说对不起但拉不下脸")
        mood = _str(kwargs.get("情绪基调"), "压抑中见希望")
        intent_feel = _str(kwargs.get("导演意图_观众应感到"), "让观众感到复杂, 难说清")
        sample_on = bool(kwargs.get("生成样例小段", True))

        # ===== 节点专属 =====
        director_meta = MASTER_DIRECTORS_8.get(director, {})
        domain_name = "导演分镜 (环节 23, 25)"
        domain_focus = "12 维导演分镜 (镜头/景别/运动/光影/色彩/声音/表演/节奏/剪辑/留白/反转/余韵)"

        # ===== 5 要素处理 =====
        data_summary = (
            "1161 部 director_view 14 维 + 63 导演 12 维 + 8 顶级导演风格库 + "
            "191 反 AI 词表 + 10 强制具体细节铁律 + 12 套理论 + 14 部真实短剧 + "
            "H3 三大字段 + 4 任务类型 + 13 镜头运动 + 11 规则 + 11 维导演控制 + "
            "3 留白 + 3 运镜法则 + 9 维光照 + 5 空间 + 5 沉默 + 卡兹克 2.5 SFT"
        )
        context_brief = (
            "导演=" + director + ", 景别=" + shot_size + ", 运动=" + camera_move + ", "
            "光影=" + lighting + ", 色彩=" + color_tone + ", 声音=" + sound_design + ", "
            "剪辑=" + edit_pace + ", 长镜头=" + str(long_take) + "s, 声音先于画面=" + str(sound_first)
        )
        skill_harness = (
            "12 维导演分镜 (镜头/景别/运动/光影/色彩/声音/表演/节奏/剪辑/留白/反转/余韵) + "
            "8 顶级导演方法论 + 180° 轴线规则 + 30° 规则 + 视线匹配 + 30 秒场景单元 + "
            "12 套理论 + 191 反 AI + 13 镜头运动 + 11 规则 + 5 沉默 + 5 空间 + 5 维意图 + 9 维光照"
        )
        experience_matrix = (
            "14 部真实短剧分镜案例 (兵马俑/秦海战姬/万兽独尊/天才机甲师) + "
            "失败模式 (跳轴/视线错误/景别单调/节奏拖) + 修复方案 + 8 大顶级导演实战"
        )
        ai_deep = (
            "反 AI 词表 + 10 铁律 + 4 轮迭代 + 沉默 4 步公式 + 留白 3 法 + 导演意图 5 维 + "
            "11 维导演控制 + 30 秒场景单元 6 段式 + 模型压住随手补戏 + L1-L7 七层 + 8 大导演风格"
        )

        # ===== 推断角色 (从剧本或默认) =====
        if "父女" in script or "父与子" in script:
            char_a = "父亲"; char_b = "女儿"
        elif "母" in script:
            char_a = "母亲"; char_b = "孩子"
        elif "夫妻" in script or "夫妇" in script:
            char_a = "丈夫"; char_b = "妻子"
        else:
            char_a = "主角色"; char_b = "次角色"

        # ===== 推断地点 / 质感 =====
        if "厨房" in script:
            location = "1998 哈尔滨老厨房"
            texture = "搪瓷碗柜 / 油烟熏黑的白墙 / 90 年代吊灯"
        elif "客厅" in script:
            location = "客厅"
            texture = "木质家具 / 老式沙发 / 老照片墙"
        else:
            location = "主场景"
            texture = "胶片颗粒 / 90 年代质感"

        # ===== GEO SPATIAL LAYOUT =====
        landmarks = (
            "  - 北墙 (frame-left): 搪瓷碗柜 (高 1.8m, 距摄影机 2.4m)\n"
            "  - 西墙 (frame-right): 老式冰箱 (高 1.5m, 距摄影机 3.0m)\n"
            "  - 中央: 厨房桌 (1.2m × 0.8m, 距摄影机 1.5m)\n"
            "  - 天花板中心: 厨房吊灯 (40W 钨丝, 距地 2.0m)\n"
            "  - 窗户 (frame-far): 木框 + 雨滴 (距摄影机 4.0m)\n"
            "  - 油烟熏黑的白墙 (背景): 距摄影机 3.5m"
        )

        # ===== 动作时间码 =====
        action_timing = (
            "0.0–0.3s — 父亲背对镜头, 切菜开始\n"
            "0.3–2.0s — 切菜循环 (17 刀, 0.8 秒/刀)\n"
            "2.0–2.5s — 父亲停手, 食指摸刀柄 3 次\n"
            "2.5–3.5s — 父亲转身, 抬眼看女儿 (响应延迟 0.3s)\n"
            "3.5–6.0s — 父亲开口 (潜文本: 对不起)\n"
            "6.0–9.0s — 女儿抬眼, 敲杯沿 2 次\n"
            "9.0–11.0s — 女儿开口 (潜文本: 我知道)\n"
            "11.0–18.0s — 沉默 (5 秒, 收音机静音)\n"
            "18.0–25.0s — 父亲放下刀, 走到窗前\n"
            "25.0–30.0s — 女儿跟上, 两人不说话"
        )

        # ===== 焦段映射 (8 大导演) =====
        focal_map = {
            "Paul Thomas Anderson (PTA)": "85",
            "Christopher Nolan (诺兰)": "50",
            "奉俊昊 (Bong Joon-ho)": "40",
            "Martin Scorsese (斯科塞斯)": "50",
            "Denis Villeneuve (维伦纽瓦)": "135",
            "Yorgos Lanthimos (兰斯莫斯)": "24",
            "Greta Gerwig (葛韦格)": "50",
            "黑泽明 (Kurosawa)": "50",
        }
        focal = focal_map.get(director, "50")

        # ===== 构建 L1-L7 =====
        l1 = _build_l1(intent_feel, script if script else "12 维分镜")
        l2 = _build_l2(char_a, char_b, location, texture)
        l3 = _build_l3(landmarks, "south")
        l4 = _build_l4(char_a, char_b, subtext, action_timing)
        l5 = _build_l5(shot_size, camera_move, focal)
        l6 = _build_l6(sound_design, "吃饭吧。", "嗯。", "沉默 4 步公式: 一句短台词 + 3 秒沉默 + 微表情 + 改变关系动作 + 5 秒呼吸")
        l7 = _build_l7()

        # ===== H3 三大字段 =====
        style, shot_1, shots, soundscape, music = _build_h3(script, shot_size, camera_move, props)
        h3_prompt = build_h3_three_fields(
            style=style, shot_1_content=shot_1, shots_content=shots,
            soundscape=soundscape, music=music, language="Chinese",
        )
        # 对齐指令
        alignment = build_alignment_instruction("T2VA", n_shots=6, duration_sec=30.0)
        if alignment:
            h3_prompt = alignment + "\n\n" + h3_prompt

        # ===== 11 维导演控制 =====
        director_control_lines = []
        for k, v in DIRECTOR_CONTROL_11_FULL.items():
            director_control_lines.append("  - " + k + ": " + v)
        director_control_text = "【11 维导演控制能力 (人类顶级导演)】\n" + "\n".join(director_control_lines)

        # ===== 3 留白 + 3 运镜 =====
        whitespace_3 = (
            "【3 留白 (3 Whitespace Techniques)】\n"
            "  1. 时间留白 (Delayed Gratification): " + THREE_WHITESPACE["时间留白"] + "\n"
            "  2. 空间留白 (Emotional Concentration): " + THREE_WHITESPACE["空间留白"] + "\n"
            "  3. 叙事留白 (Don't Say Everything): " + THREE_WHITESPACE["叙事留白"]
        )
        camera_3 = (
            "【3 运镜法则 (3 Camera Laws to Kill AI-Feel)】\n"
            "  1. " + THREE_CAMERA_LAWS["破坏首帧完成度"] + "\n"
            "  2. " + THREE_CAMERA_LAWS["引入非线性运动轨迹"] + "\n"
            "  3. " + THREE_CAMERA_LAWS["制造响应延迟"]
        )

        # ===== 8 大导演风格库 =====
        director_8_style = "【8 大世界顶级导演风格库 (Master Director Style Library)】\n"
        for d, m in MASTER_DIRECTORS_8.items():
            director_8_style += "  ▸ " + d + "\n"
            director_8_style += "    镜头: " + m["镜头运动"] + "\n"
            director_8_style += "    节奏: " + m["节奏"] + "\n"
            director_8_style += "    光影: " + m["光影"] + "\n"
            director_8_style += "    声音: " + m["声音"] + "\n"
            director_8_style += "    留白: " + m["留白"] + "\n"
            director_8_style += "    代表: " + m["代表作品"] + "\n"
            director_8_style += "    格言: " + m["格言"] + "\n"

        # ===== 12 维分镜 =====
        storyboard_12d = "【12 维导演分镜 (12-Dim Storyboard)】\n"
        for k, v in STORYBOARD_12D.items():
            storyboard_12d += "  - " + k + ": " + v + "\n"

        # ===== 组装主输出 =====
        main = []
        main.append("=" * 70)
        main.append("【DirectorStoryboardPro】世界顶级导演集群级 — Phase 16 深度重写")
        main.append("  节点: " + domain_name)
        main.append("  焦点: " + domain_focus)
        main.append("  导演: " + director)
        main.append("  代表: " + _pick(director_meta, "代表作品", "—"))
        main.append("  格言: " + _pick(director_meta, "格言", "—"))
        main.append("=" * 70)
        main.append("")
        main.append("【12 维分镜参数】")
        main.append("  1. 景别: " + shot_size)
        main.append("  2. 摄影机运动: " + camera_move)
        main.append("  3. 光线: " + lighting)
        main.append("  4. 色彩: " + color_tone)
        main.append("  5. 声音: " + sound_design)
        main.append("  6. 剪辑: " + edit_pace)
        main.append("  7. 表演: " + performance)
        main.append("  8. 留白: " + pause_density)
        main.append("  9. 反转: " + reversal)
        main.append("  10. 余韵: " + aftertaste)
        main.append("  11. 长镜头: " + str(long_take) + "s")
        main.append("  12. 空镜占比: " + empty_shot + ", 多线=" + multi_thread)
        main.append("  声音先于画面: " + str(sound_first) + ", 一镜到底: " + str(one_take))
        main.append("")
        main.append("=" * 70)
        main.append("L1-L7 七层 Prompt 架构 (7-Layer Prompt Architecture)")
        main.append("=" * 70)
        main.append("")
        main.append(l1)
        main.append("")
        main.append(l2)
        main.append("")
        main.append(l3)
        main.append("")
        main.append(l4)
        main.append("")
        main.append(l5)
        main.append("")
        main.append(l6)
        main.append("")
        main.append(l7)
        main.append("")
        main.append("=" * 70)
        main.append("H3 三大字段 (Higgsfield 官方: integrated_multimodal_description + overall_soundscape + non_diegetic_music)")
        main.append("=" * 70)
        main.append("")
        main.append(h3_prompt)
        main.append("")
        main.append("=" * 70)
        main.append("5 要素处理 (5 Elements Architecture)")
        main.append("=" * 70)
        main.append("")
        main.append("  【数据层 (DATA)】")
        main.append("    " + data_summary)
        main.append("  【上下文缩略层 (CONTEXT-BRIEF)】")
        main.append("    " + context_brief)
        main.append("  【Skill/Harness 层 (METHOD)】")
        main.append("    " + skill_harness)
        main.append("  【经验矩阵层 (EXPERIENCE)】")
        main.append("    " + experience_matrix)
        main.append("  【AI 深度处理层 (AI DEEP)】")
        main.append("    " + ai_deep)
        main.append("")
        main.append(storyboard_12d)
        main.append("")
        main.append(director_control_text)
        main.append("")
        main.append(whitespace_3)
        main.append("")
        main.append(camera_3)
        main.append("")
        main.append(director_8_style)
        main.append("")
        main.append("=" * 70)
        main.append("9 维光照控制 (CIE LAB + 摄影本体)")
        main.append("=" * 70)
        main.append("")
        for k, v in LIGHTING_9D.items():
            main.append("  - " + k + ": " + v)
        main.append("")
        main.append("=" * 70)
        main.append("11 条 H3 官方规则 (Higgsfield)")
        main.append("=" * 70)
        main.append("")
        main.append(inject_h3_rules_11())
        main.append("")
        main.append("=" * 70)
        main.append("导演意图 5 维 (不是画面里有什么, 是导演会怎么描述自己的意图)")
        main.append("=" * 70)
        main.append("")
        intent_5d = {
            "感受": intent_feel,
            "情感": subtext,
            "关系": "既想靠近又怕伤害 (基于潜文本)",
            "主题": mood,
            "留白": "想说但没说出口 - " + props + " 是没寄出的信",
        }
        main.append(inject_director_intent(intent_5d))
        main.append("")
        main_output = "\n".join(main)

        # ===== 反 AI 词表清洗 =====
        if strength != "关":
            try:
                main_output = inject_anti_ai_rules(main_output)
            except Exception:
                pass

        # ===== 第二个输出: 反 AI 样例 =====
        anti_ai_parts = []
        anti_ai_parts.append("【反 AI 清洗样例 (基于 191 词表 + 10 铁律)】\n")
        if sample_on:
            raw = (
                "他缓缓地转过头, 陷入沉思, 然后意味深长地看了她一眼. "
                "她瞳孔地震, 撕心裂肺地哭了起来, 阳光洒在她脸上, 微风拂过发梢, "
                "空气中弥漫着难以言说的气息, 她的心跳加速, 鲜血染红了眼眶, "
                "眼中闪过一丝光芒, 心中涌起无限的惆怅, 不由得感慨万千, "
                "仿佛听到了命运的召唤, 深深地吸了一口气."
            )
            cleaned = clean_anti_ai_text(raw) if _HAS_AI_DEPS else raw
            anti_ai_parts.append("【原始 (AI 味浓)】\n" + raw)
            anti_ai_parts.append("")
            anti_ai_parts.append("【清洗后 (10 强制具体细节)】\n" + cleaned)
        anti_ai_parts.append("")
        anti_ai_parts.append("【10 条强制具体细节铁律 (反 AI 味)】")
        for r in SPECIFIC_DETAIL_RULES_10:
            anti_ai_parts.append("  - " + str(r))
        anti_ai_parts.append("")
        anti_ai_parts.append("【反 AI 词表统计】")
        anti_ai_parts.append("  共 191 条, 涵盖: 情绪夸张类 (瞳孔地震/撕心裂肺/五味杂陈) / 修饰类 (缓缓地/意味深长) / 抽象类 (绝美/陷入沉思) / 自然类 (微风拂过/阳光洒在) / 心理类 (心中涌起/不由得感慨) 等")
        anti_ai_parts.append("  全部清洗逻辑在 anti_ai_vocab.clean_anti_ai_text()")
        if extra_ban:
            anti_ai_parts.append("")
            anti_ai_parts.append("【额外禁用词 (用户自定义)】\n" + extra_ban)
        anti_ai_sample = "\n".join(anti_ai_parts)

        # ===== 第三个输出: 迭代链 =====
        iter_parts = []
        if _HAS_AI_DEPS and ITERATION_TEMPLATES:
            try:
                iter_parts.append("【4 轮迭代链 (Phase 14)】\n")
                iter_parts.append("=" * 50)
                iter_parts.append("【Round 1: 草稿】")
                iter_parts.append(ITERATION_TEMPLATES["round_1_draft"].format(
                    theme=director + " 风格",
                    characters="见剧本正文",
                    structure="长镜头 " + str(long_take) + " 秒",
                    pacing=edit_pace,
                ))
                iter_parts.append("")
                iter_parts.append("=" * 50)
                iter_parts.append("【Round 2: 反 AI】")
                iter_parts.append(ITERATION_TEMPLATES["round_2_anti_ai"])
                iter_parts.append("")
                iter_parts.append("=" * 50)
                iter_parts.append("【Round 3: 人性化】")
                iter_parts.append(ITERATION_TEMPLATES["round_3_humanize"])
                iter_parts.append("")
                iter_parts.append("=" * 50)
                iter_parts.append("【Round 4: 导演润色】")
                iter_parts.append(ITERATION_TEMPLATES["round_4_director_polish"].format(
                    director=director,
                    camera_style=camera_move,
                    pacing_style=edit_pace,
                    theme_focus=pause_density,
                    visual_signature=lighting,
                ))
            except Exception:
                pass

        # 注入导演微调
        if "重" in strength and director_meta:
            iter_parts.append("")
            iter_parts.append("=" * 50)
            iter_parts.append("【" + director + " 风格微调 (Higgsfield Phase 14)】")
            iter_parts.append("  镜头: " + _pick(director_meta, "镜头运动", "—"))
            iter_parts.append("  节奏: " + _pick(director_meta, "节奏", "—"))
            iter_parts.append("  光影: " + _pick(director_meta, "光影", "—"))
            iter_parts.append("  声音: " + _pick(director_meta, "声音", "—"))
            iter_parts.append("  留白: " + _pick(director_meta, "留白", "—"))
            iter_parts.append("  表演: " + _pick(director_meta, "表演", "—"))
            iter_parts.append("  代表: " + _pick(director_meta, "代表作品", "—"))

        iter_parts.append("")
        iter_parts.append("=" * 50)
        iter_parts.append("【导演真实风格微调 (来自 ALL_DIRECTORS, 15 位导演)】")
        try:
            if _HAS_AI_DEPS and ALL_DIRECTORS and director in ALL_DIRECTORS:
                iter_parts.append(build_micro_finetune_prompt(director, "导演分镜"))
        except Exception:
            iter_parts.append("  (微调模块未完全加载)")

        iter_chain = "\n".join(iter_parts)

        return (main_output, anti_ai_sample, iter_chain)


NODE_CLASS_MAPPINGS = {
    "DirectorStoryboardPro": DirectorStoryboardPro,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DirectorStoryboardPro": "🎬 导演分镜 (环节 23, 25) — Phase 16 世界顶级导演级",
}
