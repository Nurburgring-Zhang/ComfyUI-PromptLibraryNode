# -*- coding: utf-8 -*-
"""
Phase 14 - 表演层 (Higgsfield ACTING Skill 复刻)
================================================
Higgsfield Hell Grind 的 ACTING skill 5 支柱:
- WHAT (目标)
- OBSTACLE (障碍)
- COST (失败代价)
- STRATEGY (当前策略)
- TURN (新信息让策略改变)

永远不写情绪, 写可观察行为:
- "下颌绷紧" 不是 "愤怒"
- "视线先到门口, 头晚半拍" 不是 "惊讶"
- "鼻血流到上唇但不擦" 不是 "受伤"

5 要素架构 (5 Elements):
1. 数据         - 真实短剧表演 + 4 类创作者实战 + 14 真实短剧
2. 上下文缩略   - 场景 + 角色 + 时刻 1 句话
3. Skill/Harness- 5 支柱 + 11 维导演控制 + 9 维光照 + 13 镜头运动
4. 经验矩阵     - Hell Grind ACTING skill + 5 支柱案例库
5. AI 深度处理  - 不写情绪写动作 + INNER 内心独白 + 微事件 1-2s
"""

import os
import sys

try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES, SPECIFIC_DETAIL_RULES, HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS, clean_anti_ai_text, inject_anti_ai_rules,
    )
    from production_pipeline_v3 import (
        DIRECTOR_INTENT_5D, ART_DIRECTION_4D, SPATIAL_CONSISTENCY_5, SILENCE_MASTERY_5,
    )
    from phase14_six_documents import ASSET_REGISTRY, ACTING_STATE
    _HAS_DEPS = True
except Exception as e:
    _HAS_DEPS = False
    _DEPS_ERROR = str(e)


# ============================================================
# 5 支柱 (5 PILLARS) — 来自 Higgsfield ACTING skill
# ============================================================
FIVE_PILLARS = {
    "WHAT": "角色想从对方那里得到什么 (The Goal — what he wants from the other person)",
    "OBSTACLE": "什么在挡着他 (What's In The Way — internal/external block)",
    "COST": "失败会怎样 (What He Stands To Lose — stakes)",
    "STRATEGY": "他正在用什么方法 (His Current Approach — how he's playing it)",
    "TURN": "什么让他改变策略 (What Will Make Him Change — the pivot)",
}


# ============================================================
# 7 条活人感规则 (LIVING HUMAN RULES) — 来自 Higgsfield
# ============================================================
LIVING_HUMAN_RULES = {
    "BLINK_PATTERN": "分阶段眨眼: one lazy blink → a quick DOUBLE-BLINK → one HARD reset-blink",
    "EYE_LEADS_HEAD": "眼神方向写死, 或写眼珠乱转. 视线先于头: 眼睛先到门口, 头晚半拍",
    "MICRO_LIFE": "微生命规则: 每 1-2 秒一个可见的微事件: 胸口呼吸/鼻翼动/眉头紧松",
    "TENSION_NOT_STILL": "静止写成'保持的张力', 绝不写'nobody moves'. 'nobody moves' 会冻结画面",
    "REACTION_BEFORE_LINE": "反应先于台词结束: 听话的人半句就懂了, 脸已经先答了",
    "DIGESTION_PAUSE": "重要事件后, 给角色半秒消化再开口",
    "HANDS_BUSY": "让手忙起来: 他不'聊天', 他一边修东西/数东西/倒东西一边聊. 一场戏最强的重音, 是他因为听到的话突然停下手里的活",
}


# ============================================================
# 情绪→动作翻译表 (EMOTION_TO_ACTION_MAP) — 不写情绪写动作
# ============================================================
EMOTION_TO_ACTION = {
    "sad": "下颌松, 视线掉到地面, 呼吸变浅变慢, 手指无意识抓衣摆, 喉结滚一下",
    "angry": "下颌咬紧, 鼻翼张, 瞳孔缩, 肩膀抬, 拳头握, 不眨眼",
    "scared": "瞳孔放大, 呼吸快而浅, 身体缩, 视线快速扫视, 重心后移",
    "tired": "眼皮下垂, 肩膀塌, 步幅小, 胸起伏变浅, 反应慢半拍",
    "nervous": "吞咽, 清嗓子, 视线飘忽, 手反复握松, 脚尖点地",
    "determined": "下颌收, 视线锁定, 肩膀正, 重心前移, 呼吸深长",
    "guilty": "视线闪躲, 反复吞咽, 手指交叉, 肩膀内扣, 说话时停顿多",
    "loving": "视线柔, 嘴角微提, 身体倾向对方, 呼吸同步, 手指轻触",
    "betrayed": "瞳孔缩, 嘴唇抿, 视线定在对方但焦距散, 呼吸停一拍, 后退半步",
    "relieved": "肩膀塌, 呼长气, 视线软, 嘴角松, 手指张",
    "jealous": "下颌咬, 视线锁定对方和目标, 呼吸浅, 手指攥紧",
    "hopeful": "视线抬, 呼吸变深, 身体前倾, 嘴角微提但不一定笑",
}


# ============================================================
# 核心函数
# ============================================================
def build_5_pillars(what, obstacle, cost, strategy, turn):
    """构建 5 支柱"""
    out = f"""════════════════════════════════════════
【5 PILLARS (Higgsfield ACTING)】
════════════════════════════════════════

WHAT (目标): {what}
OBSTACLE (障碍): {obstacle}
COST (失败代价): {cost}
STRATEGY (当前策略): {strategy}
TURN (让他改变的事): {turn}

NOTE: 5 支柱是角色的"内在驱动", 用身体行为表达出来.
不写 'sad' / 'angry' / 'shocked' — 这些词一出模型就开始即兴发挥, 出来的东西很浅.
"""
    return out


def translate_emotion_to_action(emotion, body_anchor=""):
    """把情绪翻译成身体动作 (Hell Grind 核心反直觉)"""
    action = EMOTION_TO_ACTION.get(emotion.lower(), f"未识别的情绪 '{emotion}', 请直接写动作")
    out = f"""════════════════════════════════════════
【EMOTION → ACTION 翻译】
════════════════════════════════════════

情绪: {emotion}
身体动作: {action}
{f'额外锚点: {body_anchor}' if body_anchor else ''}

RULE: 永远不写情绪, 写可观察行为. 情绪从肌肉和时间线长出来.
"""
    return out


def build_action_timing(beats):
    """动作时间线 - 每节拍最多 3 句话, 一节拍超载模型直接糊"""
    out_lines = ["════════════════════════════════════════", "【ACTION TIMING (逐秒拆, 每节拍 ≤3 句)】", "════════════════════════════════════════", ""]
    for start, end, action in beats:
        out_lines.append(f"{start}-{end}s — {action}")
    out_lines.append("")
    out_lines.append("RULE: 复杂动作从生成的第一帧直接开始 (不要 'walk to the door, raise arm' 先准备动作).")
    out_lines.append("RULE: 模型爱加 'uhm'/傻笑/整句台词, prompt 必须下硬性规定: 每个人只说引号里的那句.")
    return "\n".join(out_lines)


def build_blink_sequence(pattern="default"):
    """分阶段眨眼序列"""
    if pattern == "default":
        out = "one lazy blink → a quick DOUBLE-BLINK → one HARD reset-blink"
    elif pattern == "anxiety":
        out = "rapid three-blink cluster → one hard reset-blink → eye darts"
    elif pattern == "thinking":
        out = "single slow blink → pause 2s → one hard reset-blink"
    else:
        out = pattern
    return f"分阶段眨眼: {out}"


def build_eye_lead(eye_target, head_target, eye_first=True):
    """视线先于头 (Hell Grind 核心)"""
    direction = "EYES then HEAD" if eye_first else "head and eyes together"
    return f"视线先于头: 眼睛先 {eye_target}, {direction} 转到 {head_target}"


def build_micro_life(interval_sec=1.5, count=5):
    """微生命事件 - 每 1-2 秒一个微事件 (胸呼吸/鼻翼动/眉头紧松)"""
    events = [
        "chest rises and falls with breath",
        "a nostril flares once",
        "the brow tightens then releases",
        "a finger taps the table",
        "the jaw sets and releases",
        "eyes blink in slow rhythm",
        "a hand brushes the collar",
        "weight shifts from one foot to the other",
        "a swallow in the throat",
        "the corner of the mouth twitches",
    ]
    selected = events[:count]
    out = f"每 {interval_sec} 秒一个微生命事件:\n"
    for i, e in enumerate(selected):
        time = round(i * interval_sec, 1)
        out += f"  t={time}s: {e}\n"
    return out.strip()


def build_inner_monologue(thought, label="INNER"):
    """内心独白 — 每一段动作配一行未说出口的内心"""
    return f"[{label}] {thought}  # 不会说出来, 但会改变呼吸/眼神/动作节奏"


def build_reaction_chain(listener_beat, reaction_type="half_beat", what_changed="face responds before speaker finishes"):
    """反应先于台词结束 — 听话的人半句就懂了, 脸已经先答了"""
    out = f"反应链 ({reaction_type}):\n"
    out += f"  0.0s: 听者 {listener_beat}\n"
    out += f"  0.5s: {what_changed}\n"
    out += f"  1.0s: 听者身体也跟上, 但嘴还没动\n"
    out += f"  1.5s: 听者开口\n"
    return out


def act_no_motion_but_tension(tension="heavy silence"):
    """静止但保持张力 — 绝不写 'nobody moves'"""
    return f"静止但保持张力 ({tension}): 人物用力维持静止, 呼吸仍然没有恢复, 眼睛没离开, 肩膀还端着. 绝不用 'nobody moves' (会冻结画面)"


def render_acting_prompt(actor, scene_context, goal, obstacle, cost, strategy, turn, action_beats=None, eye_lead=None, micro_life=None, inner=None):
    """完整表演 prompt"""
    out = f"""════════════════════════════════════════
【CHARACTER ACTING — {actor}】
════════════════════════════════════════

Scene: {scene_context}

5 PILLARS:
- WHAT: {goal}
- OBSTACLE: {obstacle}
- COST: {cost}
- STRATEGY: {strategy}
- TURN: {turn}

CHARACTER DESCRIPTION (locked across every shot):
{actor} — emotional state: visible body state, NOT a word. What he wants: {goal}. What he is hiding: see OBSTACLE. Dominant body rhythm: see STRATEGY. Visible habits in this beat: see INNER.

{build_action_timing(action_beats) if action_beats else ''}

{build_eye_lead(*eye_lead) if eye_lead else ''}

{build_micro_life() if micro_life else ''}

{build_inner_monologue(inner) if inner else ''}

LIVING HUMAN RULES (Higgsfield):
1. 分阶段眨眼: one lazy blink → a quick DOUBLE-BLINK → one HARD reset-blink
2. 视线先于头: 眼睛先到门口, 头晚半拍
3. 微生命规则: 每 1-2 秒一个微事件
4. 静止保持张力: 不用 'nobody moves', 用 '用力维持静止, 呼吸仍未恢复'
5. 反应先于台词: 听话的人半句就懂了, 脸已先答
6. 重要事件后半秒消化再开口
7. 让手忙起来: 一边修东西一边聊, 最强重音是突然停下手里的活
"""
    return out


# ============================================================
# ComfyUI 节点
# ============================================================
class Phase14ActingSkill:
    """Phase 14 — 表演层节点 (Higgsfield ACTING skill 复刻)"""

    CATEGORY = "PromptLibrary/Phase14 表演"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("five_pillars", "action_timing", "emotion_to_action", "living_human_rules", "inner_monologue", "full_acting_prompt")
    FUNCTION = "build_acting"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "角色": ("STRING", {"default": "ROCO", "multiline": False}),
                "场景": ("STRING", {"default": "训练室, 雨夜, 12 秒", "multiline": True}),
                "目标_WHAT": ("STRING", {"default": "在 JAX/REIN 进来前, 再完成一次 clean hit", "multiline": True}),
                "障碍_OBSTACLE": ("STRING", {"default": "右臂失控, 每次重击都会加剧", "multiline": True}),
                "代价_COST": ("STRING", {"default": "如果被发现失控, 就不能继续当组长", "multiline": True}),
                "策略_STRATEGY": ("STRING", {"default": "用左臂苦肉计压住右臂", "multiline": True}),
                "转折_TURN": ("STRING", {"default": "门被推开的那一秒, 他必须收起疲惫", "multiline": True}),
                "情绪词": ("STRING", {"default": "burnt out", "multiline": False}),
                "内心独白_INNER": ("STRING", {"default": "我想你 / 我错了 / 再给我一次机会", "multiline": True}),
                "导演风格": (["塔可夫斯基", "王家卫", "诺兰", "是枝裕和", "侯孝贤", "李沧东", "奉俊昊", "贾樟柯", "周星驰", "Vince Gilligan", "大衛·芬奇", "Papi酱", "诺兰_短剧版", "毕赣", "小津安二郎", "黑泽明", "库布里克", "伯格曼", "李安", "蔡明亮"], {"default": "是枝裕和"}),
                "启用反AI规则": ("BOOLEAN", {"default": True}),
            },
        }

    def build_acting(self, 角色, 场景, 目标_WHAT, 障碍_OBSTACLE, 代价_COST, 策略_STRATEGY, 转折_TURN, 情绪词, 内心独白_INNER, 导演风格, 启用反AI规则):
        # 5 支柱
        pillars = build_5_pillars(目标_WHAT, 障碍_OBSTACLE, 代价_COST, 策略_STRATEGY, 转折_TURN)
        # 情绪→动作
        emotion_action = translate_emotion_to_action(情绪词)
        # 活人感规则
        living = "════════════════════════════════════════\n【LIVING HUMAN RULES (Higgsfield 7 条)】\n════════════════════════════════════════\n\n"
        for k, v in LIVING_HUMAN_RULES.items():
            living += f"  - {k}: {v}\n"
        # 内心独白
        inner = build_inner_monologue(内心独白_INNER)
        # 微生命
        micro = build_micro_life(1.5, 5)
        # 动作时间线 (默认 ROCO 12s)
        beats = [
            ("0.0", "2.0", f"{角色} holds the center of the mat, feet planted wide, chest pumping in short shallow pulls"),
            ("2.0", "4.5", f"the jaw sets and releases twice; a thread of blood runs from his nose to his upper lip and he lets it run; one lazy blink, a quick DOUBLE-BLINK, one HARD reset-blink"),
            ("4.5", "6.0", f"the gaze drops to the smashed mannequins at frame-right, holds one beat, then lifts to the door as it opens — the eyes reach the door before the head turns"),
            ("6.0", "9.0", f"the second the door opens, {角色} re-arms his face — the exhaustion folds back behind a dry half-smile before he says a word"),
            ("9.0", "12.0", f"{角色} begins to speak, but the listener has already understood — her face responds before he finishes the first half"),
        ]
        timing = build_action_timing(beats)
        # 视线先于头
        eye = build_eye_lead("reach the door", "the head turns", eye_first=True)
        # 反应链
        reaction = build_reaction_chain("JAX's face: the smile fades half a beat late", "half_beat_late", "REIN's thumb stops on tablet first, then her head turns")

        full = f"""════════════════════════════════════════
【PHASE 14 ACTING PROMPT — {角色}】
════════════════════════════════════════

【导演风格】{导演风格}
【场景】{场景}
【Higgsfield ACTING skill 5 支柱 + 7 活人感规则 + 微事件 + 内心独白】

{pillars}

{timing}

{emotion_action}

{living}

{inner}

{micro}

{eye}

{reaction}

{act_no_motion_but_tension('heavy silence after the door opens — they all hold position, breathing uneven, eyes not leaving each other')}

════════════════════════════════════════
【5 要素架构 (5 Elements)】
════════════════════════════════════════

1. 数据: 14 部真实短剧表演实战 + 4 类创作者实战 + 15 导演表演档案
2. 上下文: {场景} + 角色 {角色} + 导演 {导演风格}
3. Skill: 5 支柱 + 7 活人感规则 + 11 维导演控制 + 9 维光照 + 13 镜头运动
4. 经验: Hell Grind ACTING skill + ROCO 训练室实战 + 情绪→动作翻译表
5. AI 深度: 不写情绪写动作 + INNER 内心独白 + 微事件 1-2s + 11 维导演控制
"""
        if 启用反AI规则 and _HAS_DEPS:
            full = inject_anti_ai_rules(full)

        return (pillars, timing, emotion_action, living, inner, full)


# ============================================================
# 演示
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("Phase 14 Acting Skill — Higgsfield ACTING 5 支柱 + 7 活人感规则")
    print("=" * 70)

    # 演示
    p = build_5_pillars(
        "再完成一次 clean hit",
        "右臂失控, 每次重击加剧",
        "如果被发现就不能当组长",
        "用左臂苦肉计压住右臂",
        "门被推开那一秒必须收起疲惫",
    )
    print(p)

    print(build_action_timing([
        ("0.0", "2.0", "ROCO holds center of mat, feet planted wide"),
        ("2.0", "4.5", "jaw sets twice; blood runs from nose to lip, one lazy blink"),
    ]))

    # 节点实例化
    n = Phase14ActingSkill()
    print(f"\nComfyUI 节点: CATEGORY={n.CATEGORY}, RETURN_NAMES={n.RETURN_NAMES}")
