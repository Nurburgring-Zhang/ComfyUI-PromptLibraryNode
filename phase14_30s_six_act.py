# -*- coding: utf-8 -*-
"""
Phase 14 - 30 秒场景单元 6 段式分镜 (Higgsfield 卡兹克 2.5 升级版)
================================================
Higgsfield Hell Grind + 卡兹克 2.5 升级版核心: 30 秒接近完整场景单元
6 段式分镜 (建置/引入/互动/冲突/高潮/钩子) - 卡兹克 2.5 升级

5 要素架构:
1. 数据         - 14 部真实短剧 + 4 类创作者实战 + 50 参考输入
2. 上下文缩略   - 类型/演员/情绪/导演 1 句话
3. Skill/Harness- 30s 6 段 + 11 维控制 + 11 H3 规则 + 13 镜头
4. 经验矩阵     - Hell Grind 卡兹克 2.5 升级 + 6 段式分镜
5. AI 深度处理  - 模型压住随手补戏的冲动 (卡兹克 2.5 核心)
"""

import os
import sys

try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES, clean_anti_ai_text, inject_anti_ai_rules,
    )
    from prompt_builder import (
        CAMERA_MOTION_13, STYLE_KEYWORDS, SCENE_MOTION_MAP,
        H3_RULES_11, SEEDANCE_25_QUOTES, DIRECTOR_CONTROL_11,
        build_30s_timeline, build_alignment_instruction, build_h3_three_fields,
        inject_director_control_11, inject_5_elements, inject_anti_ai_rules as inject_anti_ai_pb,
    )
    from phase14_six_documents import ASSET_REGISTRY
    from phase14_style_prefix import STYLE_PREFIX
    _HAS_DEPS = True
except Exception as e:
    _HAS_DEPS = False
    _DEPS_ERROR = str(e)


# ============================================================
# 30 秒场景单元 6 段定义 (Higgsfield + 卡兹克 2.5 升级)
# ============================================================
SIX_ACT_30S = [
    {
        "id": 1, "stage": "建置 (Establish)", "time": "0:00-0:03", "duration": 3,
        "purpose": "1 秒全景让 AI 认路: 谁在哪, 什么在哪, 光从哪来",
        "key_action": "Wide static shot, no motion, no dialogue, no complex action",
        "directive": "EXACT N CHARACTERS — NO DUPLICATES + GEO SPATIAL LAYOUT 一次性定位置",
        "ai_pitfall": "模型爱在第 1 秒就放人物动作, 删掉这一秒角色就开始换位",
        "key_skill": "小 hack: 这一秒里让谁蹦一个短词 (如 'hm'), Seedance 更容易把它当独立镜头处理",
    },
    {
        "id": 2, "stage": "引入 (Introduce)", "time": "0:03-0:08", "duration": 5,
        "purpose": "主角进入空间, 模型开始有动作发展",
        "key_action": "Character enters frame, makes initial contact with space/objects",
        "directive": "复杂动作从生成的第一帧直接开始 (不要 'walk to the door, raise arm' 先准备动作)",
        "ai_pitfall": "模型爱加 'uhm'/傻笑/整句台词, prompt 必须下硬性规定: 每个人只说引号里的那句",
        "key_skill": "光从 sky and windows only, 动作开始时眼睛先到, 头晚半拍",
    },
    {
        "id": 3, "stage": "互动 (Interact)", "time": "0:08-0:15", "duration": 7,
        "purpose": "核心情节开始, 主体动作/对话",
        "key_action": "Main interaction, dialogue, key actions",
        "directive": "听者半句就懂了, 脸已先答, 没台词的人必须保持安静",
        "ai_pitfall": "重要事件后立刻切, 模型不消化, 让尾巴进下一镜",
        "key_skill": "让手忙起来: 一边修东西/数东西/倒东西一边聊, 最强重音是突然停下手里的活",
    },
    {
        "id": 4, "stage": "冲突 (Conflict)", "time": "0:15-0:22", "duration": 7,
        "purpose": "矛盾开始, 戏剧张力",
        "key_action": "Conflict escalation, opposing forces visible",
        "directive": "30 秒这里应该有 1-2 个 180° axis 的微妙变化, 但绝不越线",
        "ai_pitfall": "模型爱 '漂移', 摄影机突然跑到轴线另一边, 180° 锁死",
        "key_skill": "冲突时, 角色必须保持张力, 绝不 'nobody moves' 静止 (会冻结画面)",
    },
    {
        "id": 5, "stage": "高潮 (Climax)", "time": "0:22-0:27", "duration": 5,
        "purpose": "镜头表达最连贯, 表演密度最高",
        "key_action": "Emotional peak, 1-2 个最关键动作/对白",
        "directive": "3-5 秒高潮内必有: 1 句台词 + 1 个关键动作 + 1 个面部表情",
        "ai_pitfall": "模型爱在高潮抢戏, 加新角色, 加新道具",
        "key_skill": "EXACTLY ONE 关键动作, NEVER add another. 分阶段眨眼 (lazy → DOUBLE → HARD reset)",
    },
    {
        "id": 6, "stage": "钩子 (Hook)", "time": "0:27-0:30", "duration": 3,
        "purpose": "末帧悬念, 引导下一镜",
        "key_action": "Last frame visual surprise or audio cue",
        "directive": "末帧应留下: 1 个未说完的台词 / 1 个未完成的动作 / 1 个出框的视线",
        "ai_pitfall": "模型爱 '圆满' 收尾, 加 'the end', 完美握手, 大合影",
        "key_skill": "30s 钩子: 把最有趣的元素放在最后一秒, 让观众想看下一秒",
    },
]


# ============================================================
# 6 段生成函数
# ============================================================
def build_six_act_30s(
    concept="一个失败的父亲在女儿婚礼上找回她所有生日",
    genre="电影",
    director="是枝裕和",
    characters="ROCO, JAX, REIN",
    scene="训练室, 雨夜 1998",
    mood="压抑中见希望",
    first_prop="一只破旧口琴",
    inner_monologue="我想你/我错了/再给我一次机会",
    task_type="T2VA",
):
    """6 段式 30 秒场景单元生成"""
    out = f"""════════════════════════════════════════
【30 秒场景单元 6 段式分镜 (Higgsfield + 卡兹克 2.5 升级)】
════════════════════════════════════════

【核心】30 秒接近完整场景单元, 6 段式分镜, 不再是碎片

概念: {concept}
类型: {genre}
导演: {director} - 镜头运动倾向按导演风格映射
场景: {scene}
情绪: {mood}
人物: {characters} (EXACT N CHARACTERS — NO DUPLICATES)
任务类型: {task_type}
关键道具: {first_prop}
内心独白 (INNER): {inner_monologue}

════════════════════════════════════════
6 段式分镜 (30 秒 = 6 × 5 秒)
════════════════════════════════════════

"""
    for i, act in enumerate(SIX_ACT_30S, 1):
        out += f"""--- 段 {i}/6: {act['stage']} ({act['time']}, {act['duration']}秒) ---

目的: {act['purpose']}

关键动作: {act['key_action']}

Prompt 指令: {act['directive']}

模型陷阱: {act['ai_pitfall']}

导演秘籍: {act['key_skill']}

[Shot {i}] 0:{act['time'].split(':')[1].split('-')[0]} - 0:{act['time'].split(':')[1].split('-')[1]}
[Time] {act['time']} (持续 {act['duration']} 秒)

════════════════════════════════════════
"""
    return out


def build_six_act_h3_prompts(
    concept="一个失败的父亲在女儿婚礼上找回她所有生日",
    genre="电影",
    director="是枝裕和",
    characters="ROCO, JAX, REIN",
    scene="训练室, 雨夜 1998",
    mood="压抑中见希望",
    first_prop="一只破旧口琴",
    task_type="T2VA",
    n_shots=6,
):
    """完整 H3 三大字段 × 6 段 = 30 秒场景"""
    if not _HAS_DEPS:
        return "H3 prompt builder unavailable"
    h3 = build_h3_three_fields(
        style="Cinematic, live-action, 35mm film grain",
        shot_1_content=f"Wide static. {scene}. {characters} at fixed position. {first_prop} catches light. Camera on door side. No motion. 1 second of pure space.",
        shots_content=[
            f"[Shot {i+1}] At 00:0{i*5}.000, the camera cuts to {act['key_action']} over {act['duration']}s. {act['directive']}"
            for i, act in enumerate(SIX_ACT_30S)
        ],
        soundscape="Steady rain taps against the kitchen window. The clock ticks. The old radio plays at low volume. Underwater silence in pauses.",
        music="Sparse piano notes at a slow tempo, joined by sustained low strings that gradually increase in volume before fading out at 0:28.",
        language="Chinese",
    )
    # 对齐指令
    alignment = build_alignment_instruction(task_type, n_shots=n_shots, duration_sec=30.0)
    if alignment:
        h3 = alignment + "\n\n" + h3
    return h3


# ============================================================
# ComfyUI 节点
# ============================================================
class Phase14_30sSixAct:
    """Phase 14 - 30 秒场景单元 6 段式分镜 (Higgsfield + 卡兹克 2.5 升级)"""

    CATEGORY = "PromptLibrary/Phase14 6段"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("six_act_overview", "act_1_establish", "act_2_introduce", "act_3_interact", "act_4_conflict", "act_5_climax", "act_6_hook", "h3_three_fields_prompt")
    FUNCTION = "build"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "概念": ("STRING", {"default": "一个失败的父亲在女儿婚礼上找回她所有生日", "multiline": True}),
                "类型": (["电影", "电视剧", "AIGC 短剧", "短视频", "AIGC 短视频", "MV", "故事绘本", "互动剧", "AIGC 实时互动剧"], {"default": "电影"}),
                "导演": (["塔可夫斯基", "王家卫", "诺兰", "是枝裕和", "侯孝贤", "李沧东", "奉俊昊", "贾樟柯", "周星驰", "Vince Gilligan", "大衛·芬奇", "Papi酱", "诺兰_短剧版", "毕赣", "小津安二郎", "黑泽明", "库布里克", "伯格曼", "李安", "蔡明亮"], {"default": "是枝裕和"}),
                "人物": ("STRING", {"default": "ROCO, JAX, REIN", "multiline": False}),
                "场景": ("STRING", {"default": "训练室, 雨夜 1998", "multiline": True}),
                "情绪": ("STRING", {"default": "压抑中见希望", "multiline": False}),
                "关键道具": ("STRING", {"default": "一只破旧口琴", "multiline": False}),
                "内心独白": ("STRING", {"default": "我想你/我错了/再给我一次机会", "multiline": True}),
                "任务类型": (["T2VA", "I2VA", "FL2VA", "L2VA"], {"default": "T2VA"}),
                "启用反AI": ("BOOLEAN", {"default": True}),
            },
        }

    def build(self, 概念, 类型, 导演, 人物, 场景, 情绪, 关键道具, 内心独白, 任务类型, 启用反AI):
        # 6 段概览
        overview = build_six_act_30s(概念, 类型, 导演, 人物, 场景, 情绪, 关键道具, 内心独白, 任务类型)
        # 6 段分别
        act_1 = SIX_ACT_30S[0]
        act_2 = SIX_ACT_30S[1]
        act_3 = SIX_ACT_30S[2]
        act_4 = SIX_ACT_30S[3]
        act_5 = SIX_ACT_30S[4]
        act_6 = SIX_ACT_30S[5]
        # H3 prompt
        h3 = build_six_act_h3_prompts(概念, 类型, 导演, 人物, 场景, 情绪, 关键道具, 任务类型, n_shots=6)

        # 注入 11 维导演控制
        if _HAS_DEPS:
            try:
                control_block = inject_director_control_11()
                overview += "\n" + control_block
            except Exception:
                pass

        # 反 AI
        if 启用反AI and _HAS_DEPS:
            try:
                overview = inject_anti_ai_pb(overview)
                h3 = inject_anti_ai_pb(h3)
            except Exception:
                pass

        return (overview, act_1['purpose'] + " | " + act_1['key_skill'],
                act_2['purpose'] + " | " + act_2['key_skill'],
                act_3['purpose'] + " | " + act_3['key_skill'],
                act_4['purpose'] + " | " + act_4['key_skill'],
                act_5['purpose'] + " | " + act_5['key_skill'],
                act_6['purpose'] + " | " + act_6['key_skill'],
                h3)


# ============================================================
# 演示
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("Phase 14 - 30 秒场景单元 6 段式 (Higgsfield + 卡兹克 2.5 升级)")
    print("=" * 70)
    n = Phase14_30sSixAct()
    print(f"ComfyUI 节点: CATEGORY={n.CATEGORY}, RETURN_NAMES={n.RETURN_NAMES}")
    print()
    overview = build_six_act_30s()
    print(overview[:2500])
    print("...")
