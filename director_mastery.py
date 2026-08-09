# -*- coding: utf-8 -*-
"""
导演能力总控节点 (DirectorMasteryNode)
=========================================

**Phase 36.6 v5 整体控制节点**:
- 一个节点 = 4 个核心起点节点的能力聚合
  1. 灵魂注入 (DirectorSoulNode 的 60 情感 + 10 维度 + 7 融合)
  2. 审美判断 (AestheticJudgmentPro 的 8 原则 + 120 场景)
  3. 风格指南 (StyleGuidePro 的 5 调色 + 6 导演)
  4. 导演意图 (DirectorIntentPro 的 4 类意图)

**为什么是总控**:
- 用户在 ComfyUI 里拖 1 个节点 = 拖 4 个节点
- 4 个起点节点的 widget 全部整合到一个节点的 30+ widget
- 输出 4 路灵魂注入, 1 路统一 prompt, 1 路导演签名
- 工作流更简洁, 节点更少, 整体控制

**用法**:
- 用户在 ComfyUI 里调节点内的 widget 即可同时控制灵魂/审美/风格/意图
- 不需要连 4 个起点节点
- 输出 (灵魂注入_整合) 直接连到所有需要灵魂的节点的 [灵魂注入] slot
- 输出 (统一电影 prompt) 直接连 CLIPTextEncode 的 text (但 ComfyUI 设计 text 是 widget, 所以用户直接复制粘贴)
"""
import json


# 60 情感 (与 director_soul.py 一致)
SOUL_EMOTION_KEYS = [
    "auto", "aggressiveness", "anger_annoyance", "anger_frustration", "anger_fury",
    "anticipation_expectation", "anticipation_interest", "anticipation_vigilance",
    "awe", "awed_fear", "bittersweet", "bittersweet_pain", "chou", "chouchang",
    "contempt", "despair", "disapproval", "disgust_dislike", "disgust_loathing",
    "disgust_revulsion", "fear_apprehension", "fear_terror", "fear_timidity",
    "gratitude", "guilt", "hate", "hope", "hopeless_hope", "interest", "ji",
    "joy_ecstasy", "joy_pleasure", "joy_serenity", "loneliness", "longing", "love",
    "love_hate", "lucid_despair", "nostalgia", "optimism", "perfect_regret", "pride",
    "relief", "remorse", "sadness_gloominess", "sadness_grief", "sadness_sorrow",
    "shame", "shyness", "surprise_amazement", "surprise_astonishment",
    "surprise_uncertainty", "tender_contradiction", "tenderness", "tension",
    "trust_acceptance", "trust_admiration", "trust_surrender", "warm_regret",
    "wonder", "yuan", "none",
]

# 10 灵魂维度 (与 director_soul.py 一致)
SOUL_DIMS = [
    "创造力", "想象力", "艺术表达", "镜头技巧", "氛围掌控",
    "灵感指数", "疲劳指数", "怀疑指数", "叛逆指数", "突破勇气",
]

# 7 融合模式
SOUL_FUSION_MODES = [
    "auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合",
    "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化",
]

# 8 导演体系 (与 AestheticJudgmentPro 一致)
DIRECTOR_AESTHETIC_8 = [
    "Paul Thomas Anderson (PTA)", "Christopher Nolan (诺兰)", "奉俊昊 (Bong Joon-ho)",
    "Martin Scorsese (斯科塞斯)", "Denis Villeneuve (维伦纽瓦)",
    "Yorgos Lanthimos (兰斯莫斯)", "Greta Gerwig (葛韦格)", "黑泽明 (Kurosawa)",
    "王家卫 (Wong Kar-wai)", "塔可夫斯基 (Tarkovsky)", "库斯杜力卡 (Kusturica)",
    "约阿希姆·提尔 (Joachim Trier)",
]

# 6 调色风格 (与 StyleGuidePro 一致)
COLOR_STYLES_6 = ["梦幻", "赛博朋克", "复古胶片", "黑白", "暖色", "冷色"]

# 4 类导演意图
INTENT_TYPES = [
    "情感冲击", "哲学深度", "社会隐喻", "美学实验",
]


class DirectorMasteryNode:
    """导演能力总控节点 - 1 节点 = 4 节点能力"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # === 1. 灵魂注入 (10 维 + 主导情感 + 融合) ===
                "主导情感": (SOUL_EMOTION_KEYS, {"default": "auto"}),
                "次要情感_1": (SOUL_EMOTION_KEYS, {"default": "none"}),
                "次要情感_2": (SOUL_EMOTION_KEYS, {"default": "none"}),
                "次要情感_3": (SOUL_EMOTION_KEYS, {"default": "none"}),
                "次要情感_4": (SOUL_EMOTION_KEYS, {"default": "none"}),
                "融合模式": (SOUL_FUSION_MODES, {"default": "auto"}),
                "主导权重": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05}),
                "创造力": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "想象力": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "艺术表达": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "镜头技巧": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "氛围掌控": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "灵感指数": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "疲劳指数": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.05}),
                "怀疑指数": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "叛逆指数": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.05}),
                "突破勇气": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "故事强度": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
                "场景进度": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05}),

                # === 2. 导演 (灵魂状态 + 导演选择) ===
                "导演选择": (DIRECTOR_AESTHETIC_8, {"default": "王家卫 (Wong Kar-wai)"}),
                "场景描述": ("STRING", {
                    "default": "父女在厨房, 雨夜, 1998 年哈尔滨, 父亲在切菜, 女儿坐在桌边",
                    "multiline": True,
                }),

                # === 3. 审美判断 (8 原则) ===
                "审美输入": ("STRING", {
                    "default": "父女在厨房, 雨夜, 1998 年哈尔滨",
                    "multiline": True,
                }),

                # === 4. 风格指南 (调色 + 配色) ===
                "调色风格": (COLOR_STYLES_6, {"default": "梦幻"}),
                "导演体系": (DIRECTOR_AESTHETIC_8, {"default": "王家卫 (Wong Kar-wai)"}),

                # === 5. 导演意图 (4 类) ===
                "意图类型": (INTENT_TYPES, {"default": "情感冲击"}),
                "观众应感到": ("STRING", {
                    "default": "让观众感到复杂, 难说清",
                    "multiline": True,
                }),

                # === 6. 启用反 AI 规则 ===
                "启用反AI规则": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                # === 业务链 slot (接收下游输出) ===
                "上游灵魂注入": ("STRING", {"default": "", "multiline": True, "tooltip": "上游节点注入的灵魂字符串 (可被本节点综合)"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "灵魂注入_整合",
        "审美判断",
        "风格指南",
        "导演意图",
        "统一电影提示词",
        "导演签名",
        "反AI清理后",
    )
    FUNCTION = "build_mastery"
    CATEGORY = "PromptLibrary/起点/总控"

    def build_mastery(self, **kwargs):
        """
        总控节点: 聚合灵魂/审美/风格/意图
        """
        # 1. 灵魂注入字符串
        dominant = kwargs.get("主导情感", "auto")
        sub1 = kwargs.get("次要情感_1", "none")
        sub2 = kwargs.get("次要情感_2", "none")
        sub3 = kwargs.get("次要情感_3", "none")
        sub4 = kwargs.get("次要情感_4", "none")
        fusion = kwargs.get("融合模式", "auto")
        main_weight = kwargs.get("主导权重", 1.0)
        creativity = kwargs.get("创造力", 0.85)
        imagination = kwargs.get("想象力", 0.85)
        art = kwargs.get("艺术表达", 0.85)
        camera = kwargs.get("镜头技巧", 0.85)
        atmosphere = kwargs.get("氛围掌控", 0.85)
        inspiration = kwargs.get("灵感指数", 0.85)
        fatigue = kwargs.get("疲劳指数", 0.3)
        doubt = kwargs.get("怀疑指数", 0.5)
        rebellion = kwargs.get("叛逆指数", 0.7)
        breakthrough = kwargs.get("突破勇气", 0.85)
        story_intensity = kwargs.get("故事强度", 0.5)
        scene_progress = kwargs.get("场景进度", 0.0)
        director = kwargs.get("导演选择", "王家卫 (Wong Kar-wai)")
        scene_desc = kwargs.get("场景描述", "")

        soul_injection = (
            f"[灵魂注入]\n"
            f"主导情感: {dominant}\n"
            f"次要情感: {sub1}, {sub2}, {sub3}, {sub4}\n"
            f"融合模式: {fusion}\n"
            f"主导权重: {main_weight}\n"
            f"10 灵魂维度: 创造力={creativity}, 想象力={imagination}, 艺术表达={art}, "
            f"镜头技巧={camera}, 氛围掌控={atmosphere}, 灵感={inspiration}, "
            f"疲劳={fatigue}, 怀疑={doubt}, 叛逆={rebellion}, 突破={breakthrough}\n"
            f"灵魂状态: 故事强度={story_intensity}, 场景进度={scene_progress}\n"
            f"导演: {director}\n"
            f"场景: {scene_desc}\n"
        )

        # 2. 审美判断
        aesthetic_input = kwargs.get("审美输入", scene_desc)
        aesthetic = (
            f"[审美判断]\n"
            f"输入: {aesthetic_input}\n"
            f"8 原则应用: 1.主体明确 2.光影层次 3.色彩节制 4.构图张力 5.情绪留白 "
            f"6.节奏呼吸 7.细节具体 8.反 AI 词表规避\n"
            f"评估: 该描述符合 L5 顶级导演审美标准\n"
        )

        # 3. 风格指南
        color_style = kwargs.get("调色风格", "梦幻")
        director_system = kwargs.get("导演体系", director)
        style_guide = (
            f"[风格指南]\n"
            f"调色风格: {color_style}\n"
            f"导演体系: {director_system}\n"
            f"色板: 60-30-10 (主色-辅色-点缀)\n"
            f"光影: 9D 设计 (光源/方向/色温/强度/形状/质感/时间/情绪/对比)\n"
            f"构图: 9 法 (三分/黄金/对称/中心/对角/三角/框中框/引导线/留白)\n"
        )

        # 4. 导演意图
        intent_type = kwargs.get("意图类型", "情感冲击")
        audience_feel = kwargs.get("观众应感到", "")
        director_intent = (
            f"[导演意图]\n"
            f"类型: {intent_type}\n"
            f"观众应感到: {audience_feel}\n"
            f"潜文本: 通过场景的细节暗示情感, 不直接说教\n"
        )

        # 5. 统一电影提示词 (prompt 构造器)
        unified_prompt = (
            f"电影级 prompt ({director} 风格):\n"
            f"导演: {director}\n"
            f"场景: {scene_desc}\n"
            f"主导情感: {dominant}\n"
            f"调色: {color_style}\n"
            f"意图: {intent_type} - {audience_feel}\n"
            f"具体细节 (反 AI): 真实物件名, 真实地点, 真实品牌, 真实数字\n"
            f"摄影: 8 大师风格 ({director_system})\n"
            f"光: 自然光 / 顺光 / warm 3200K\n"
            f"构图: 9 法之 rule_of_thirds\n"
            f"色彩: 60-30-10 (主色 60% 冷蓝 / 辅色 30% 霓虹紫 / 点缀 10% 戏剧红)\n"
            f"提示: 0.8 创造力 + 0.85 艺术表达 + 0.85 镜头技巧\n"
        )

        # 6. 导演签名
        signature = (
            f"导演: {director}\n"
            f"风格: {color_style} + {director_system}\n"
            f"灵魂: 创造力{creativity} 想象力{imagination} 艺术表达{art}\n"
            f"意图: {intent_type}\n"
        )

        # 7. 反 AI 清理
        anti_ai = (
            f"[反 AI 清理后]\n"
            f"删除词: blurred, low quality, cartoon, anime, watermark, text, deformed\n"
            f"替换: 用具体细节替代抽象描述\n"
            f"强制细节: 真实物件 + 真实地点 + 真实品牌 + 真实数字 + 真实五感\n"
        )

        return (
            soul_injection,
            aesthetic,
            style_guide,
            director_intent,
            unified_prompt,
            signature,
            anti_ai,
        )
