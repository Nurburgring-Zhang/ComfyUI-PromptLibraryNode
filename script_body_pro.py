# -*- coding: utf-8 -*-
"""
ScriptBodyPro — 剧本正文节点
=============================
(节点 2/3 — 剧本输出拆分为 3 个节点)

功能:
- 接收 节点 1/3 输出的 story_architecture
- 输出: 场次/场景描写/对白/动作
- 强反 AI 词表 + 真实导演微调 + 多轮迭代
- 强制对白 8-15 字以内
- 90% 场景用具象动作

输入 (18 个核心参数):
- 故事架构 (字符串, 来自节点 1/3)
- 导演风格
- 对白密度
- 静默场景比例
- 食物/物件出现
- 时代具体年份
- 地点具体地址
- 镜头偏好
- 等

输出:
- script_body: 含场次/对白/动作的完整剧本
- cleaned_anti_ai_preview: 清洗后样本
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
        clean_anti_ai_text,
    )
    from director_real_scripts import ALL_DIRECTORS, build_micro_finetune_prompt
    _HAS_ANTI_AI = True
except Exception as e:
    _HAS_ANTI_AI = False
    _ANTI_AI_ERROR = str(e)


# 对白密度
DIALOGUE_DENSITY = ["极少 (10%以下)", "少 (30%)", "中 (50%)", "高 (70%)", "对话为主 (90%+)"]

# 静默场景比例(王家卫/蔡明亮式)
SILENCE_RATIO = ["几乎不 (5%)", "少 (15%)", "中 (30%)", "多 (50%)", "极多 (70%+)"]

# 食物出现频率(李安/是枝裕和式)
FOOD_FREQ = ["无", "偶尔", "常出现", "核心场景"]

# 物件密度(王家卫/塔可夫斯基式)
OBJECT_DENSITY = ["少", "中", "多", "极多 (每场 3+ 物件)"]

# 时代具体度
TIME_SPECIFICITY = ["模糊 (一天)", "粗 (某个时期)", "中 (某年)", "精 (年月日)"]

# 地点具体度
PLACE_SPECIFICITY = ["模糊", "粗 (城市)", "中 (区/街道)", "精 (门牌号)"]


class ScriptBodyPro:
    """
    剧本正文节点 — 拆节点 2/3
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # === 1. 接收节点 1/3 输出 ===
                "故事架构_来自节点1": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),

                # === 2. 导演风格 ===
                "导演风格_63选1": ("STRING", {
                    "default": "王家卫",
                    "multiline": False,
                }),

                # === 3. 风格细节 ===
                "对白密度": (DIALOGUE_DENSITY, {"default": "中 (50%)"}),
                "静默场景比例": (SILENCE_RATIO, {"default": "中 (30%)"}),
                "食物出现频率": (FOOD_FREQ, {"default": "偶尔"}),
                "物件密度": (OBJECT_DENSITY, {"default": "中"}),

                # === 4. 时代与地点 ===
                "时代具体度": (TIME_SPECIFICITY, {"default": "精 (年月日)"}),
                "地点具体度": (PLACE_SPECIFICITY, {"default": "精 (门牌号)"}),

                # === 5. 角色具体度 ===
                "对白最大字数": ("INT", {"default": 15, "min": 5, "max": 50}),
                "主角身体习惯": ("STRING", {
                    "default": "左眼眨眼多 / 走路外八 / 摸下巴",
                    "multiline": False,
                }),
                "主角口头禅": ("STRING", {
                    "default": "嘛 / 反正 / 嗯",
                    "multiline": False,
                }),

                # === 6. 节奏 ===
                "场次数量": ("INT", {"default": 20, "min": 3, "max": 200}),
                "最长场次时长秒": ("INT", {"default": 120, "min": 10, "max": 1800}),

                # === 7. 反 AI 强度 ===
                "反AI强度": (["关", "轻 (词表)", "中 (词表+铁律)", "重 (词表+铁律+微调)"], {"default": "重 (词表+铁律+微调)"}),
            },
            "optional": {
                "额外禁用词": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                "生成样例小段": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("script_body", "anti_ai_sample", "iteration_chain")
    FUNCTION = "build_script_body"
    CATEGORY = "PromptLibrary/剧本输出"

    def build_script_body(self, **kwargs):
        director = kwargs.get("导演风格_63选1", "王家卫")
        architecture = kwargs.get("故事架构_来自节点1", "")

        # 用户 prompt
        user_prompt = f"""【任务: 基于以下架构写出剧本正文(场次+对白+动作)】

【故事架构】
{architecture}

【导演风格】
{director}

【风格细节】
- 对白密度: {kwargs.get('对白密度', '中 (50%)')}
- 静默场景比例: {kwargs.get('静默场景比例', '中 (30%)')}
- 食物出现频率: {kwargs.get('食物出现频率', '偶尔')}
- 物件密度: {kwargs.get('物件密度', '中')}

【具体度要求】
- 时代: {kwargs.get('时代具体度', '精 (年月日)')}
- 地点: {kwargs.get('地点具体度', '精 (门牌号)')}
- 对白最大字数: {kwargs.get('对白最大字数', 15)}
- 主角身体习惯: {kwargs.get('主角身体习惯', '')}
- 主角口头禅: {kwargs.get('主角口头禅', '')}

【场次】
- 总场次: {kwargs.get('场次数量', 20)}
- 最长场次: {kwargs.get('最长场次时长秒', 120)} 秒

【输出格式】
场次 1: [场次标题, 具体时间, 具体地点]
场景描写: (具体物件 + 真实光影, 不写情绪形容词)
(动作 1): [具体动作, 不用"试图/缓缓/静静"]
人物 A: (对白, 8-15 字内)
人物 B: (对白)
(沉默 / 动作 / 物件特写)
场次 2: ...

【强制要求】
1. 对白不超过 {kwargs.get('对白最大字数', 15)} 字
2. 90% 场景用具象动作(物件/数字/品牌/地址)
3. 不写情绪形容词, 用动作呈现
4. 静默场景 = 镜头不切 + 不说话 + 物件特写
5. 时代/地点必须可考据
"""

        if _HAS_ANTI_AI:
            # 注入反 AI
            strength = kwargs.get("反AI强度", "重 (词表+铁律+微调)")
            if strength != "关":
                user_prompt = inject_anti_ai_rules(user_prompt, director if director in DIRECTOR_ANTI_AI_PROMPTS else "")
            if "重" in strength and director in ALL_DIRECTORS:
                user_prompt += "\n\n" + build_micro_finetune_prompt(director, "剧本正文")

            # 额外禁用词
            extra_ban = kwargs.get("额外禁用词", "")
            if extra_ban:
                user_prompt += f"\n\n【额外禁用词(必须严格遵守)】\n{extra_ban}"

            # 多轮迭代链
            iter_chain = [
                ITERATION_TEMPLATES["round_1_draft"].format(
                    theme=kwargs.get("故事架构_来自节点1", "")[:100],
                    characters=f"主角: {kwargs.get('主角身体习惯','')} 口头禅: {kwargs.get('主角口头禅','')}",
                    structure=f"{kwargs.get('场次数量', 20)} 场次",
                    pacing=f"静默 {kwargs.get('静默场景比例','')}",
                ),
                ITERATION_TEMPLATES["round_2_anti_ai"],
                ITERATION_TEMPLATES["round_3_humanize"],
                ITERATION_TEMPLATES["round_4_director_polish"].format(
                    director=director,
                    camera_style="按" + director + "的镜头习惯",
                    pacing_style=kwargs.get("静默场景比例", "中"),
                    theme_focus="见故事架构",
                    visual_signature="按" + director + "的视觉签名",
                ),
            ]
            iter_text = "\n\n=========\n\n".join(iter_chain)

            # 反 AI 清洗样本(如果开了样例)
            if kwargs.get("生成样例小段", True):
                sample = "他陷入深深的沉思, 瞳孔地震, 心中暗道, 缓缓地站起身来, 看着她绝美的脸庞, 撕心裂肺地喊了一声。"
                cleaned = clean_anti_ai_text(sample)
            else:
                cleaned = ""
        else:
            iter_text = "反 AI 词表未加载"
            cleaned = ""

        return (user_prompt, cleaned, iter_text)


NODE_CLASS_MAPPINGS = {
    "ScriptBodyPro": ScriptBodyPro,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ScriptBodyPro": "📜 剧本正文 (2/3)",
}
