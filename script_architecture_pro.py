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

输入 (20 个核心参数):
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

输出:
- story_architecture: dict (含 worldview/theme/characters/structure/pacing/metaphysics)
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


class ScriptArchitecturePro:
    """
    故事架构节点 — 拆节点 1/3
    输出: 世界观 + 主题 + 角色 + 结构 + 节奏曲线
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
            },
            "optional": {
                # === 7. 额外反 AI 配置 ===
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

    def build_architecture(self, **kwargs):
        """构建故事架构"""
        # 注入反 AI 规则
        director = kwargs.get("导演风格_63选1", "王家卫")
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
                anti_ai_text,  # story_architecture(反 AI 后的完整 prompt)
                json.dumps({k: v for k, v in ANTI_AI_PHRASES.items() if k}, ensure_ascii=False)[:1000] if _HAS_ANTI_AI else "未加载",
                iter_text,
            )
        else:
            # 没有反 AI 词表时, 简单 prompt
            return (
                f"题材: {kwargs.get('题材','')}\n输出: 故事架构 JSON",
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
