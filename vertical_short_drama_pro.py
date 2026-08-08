# -*- coding: utf-8 -*-
"""
VerticalShortDramaPro — 垂直短剧专业节点
=========================================
(节点 4/7 — 剧本输出专业节点)

基于 ReelShort / DramaBox / 抖音短剧实战经验

核心功能:
- 1-2 分钟单集结构生成
- 3 秒钩子 + 30 秒爽点 + 结尾钩子
- 6 大套路应用
- 8 大爆款公式
- 付费卡点设计
- 短剧对白 / 节奏 / 镜头的全套

输入 (20 个核心参数):
- 套路 (11 种抖音爆款)
- 集数 (单集 1-2 分钟)
- 总集数 (60-100 集)
- 付费卡点位置
- 钩子强度
- 节奏密度
- 爽虐甜比例
- 受众 (性别/年龄/地域)
- 等
"""

import os
import sys
import json

try:
    from director_mastery_v2 import (
        SHORT_DRAMA_RULES,
        DOUYIN_TROPES,
        DOUYIN_HIT_FORMULA,
        SHORT_DRAMA_PAYWALL,
        PACING_PATTERNS,
        REVERSAL_TYPES,
        AFTERTASTE_LEVELS,
        CHARACTER_ARCS,
        MULTI_THREAD_RULES,
        inject_all_theories,
    )
    from anti_ai_vocab import (
        ANTI_AI_PHRASES,
        SPECIFIC_DETAIL_RULES,
        HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS,
        clean_anti_ai_text,
        inject_anti_ai_rules,
    )
    _HAS_MASTERY = True
except Exception as e:
    _HAS_MASTERY = False
    _MASTERY_ERROR = str(e)


# 11 大套路
TROPES = list(DOUYIN_TROPES.keys()) if _HAS_MASTERY else ["穿越", "重生", "真假千金"]

# 8 大爆款节奏
PACINGS = list(PACING_PATTERNS.keys()) if _HAS_MASTERY else ["pulse", "plateau_cliff", "zigzag"]

# 8 大反转类型
REVERSALS = list(REVERSAL_TYPES.keys()) if _HAS_MASTERY else ["identity_reveal", "value_reversal"]

# 7 大角色弧
ARCS = list(CHARACTER_ARCS.keys()) if _HAS_MASTERY else ["positive_arc"]

# 6 级余韵
AFTERTASTES = list(AFTERTASTE_LEVELS.keys()) if _HAS_MASTERY else ["level_3_medium"]


class VerticalShortDramaPro:
    """
    垂直短剧专业节点 — 拆节点 4/7
    ReelShort / DramaBox / 抖音短剧实战级
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # === 1. 套路选择 ===
                "套路_11选1": (TROPES, {"default": "穿越"}),
                "爆款公式_8选1": (PACINGS, {"default": "plateau_cliff"}),
                "反转类型": (REVERSALS, {"default": "identity_reveal"}),
                "角色弧_7选1": (ARCS, {"default": "positive_arc"}),
                "余韵强度": (AFTERTASTES, {"default": "level_3_medium"}),

                # === 2. 规模 ===
                "总集数": ("INT", {"default": 80, "min": 20, "max": 300}),
                "单集时长秒": ("INT", {"default": 90, "min": 30, "max": 300}),
                "付费卡点位置_第几集": ("INT", {"default": 8, "min": 3, "max": 30}),

                # === 3. 节奏 ===
                "爽虐甜比例_532": ("STRING", {
                    "default": "5 爽 / 3 虐 / 2 甜",
                    "multiline": False,
                }),
                "钩子强度_1_10": ("INT", {"default": 9, "min": 1, "max": 10}),
                "前3秒冲突类型": (["暴力", "身份揭秘", "情感爆发", "性张力", "金钱冲突", "权谋", "威胁生命"], {"default": "身份揭秘"}),

                # === 4. 风格 ===
                "对白最大字数": ("INT", {"default": 12, "min": 5, "max": 25}),
                "主角性别": (["男", "女", "双男主", "双女主", "群像"], {"default": "女"}),
                "画风": (["现代都市", "古装言情", "年代剧", "仙侠", "校园", "都市悬疑", "豪门宅斗"], {"default": "现代都市"}),
                "受众": (["女频", "男频", "泛人群"], {"default": "女频"}),

                # === 5. 平台 ===
                "目标平台": (["ReelShort", "DramaBox", "抖音", "快手", "TikTok", "通用"], {"default": "ReelShort"}),
                "字幕语言": (["中文", "英文", "双语", "多语言"], {"default": "双语"}),

                # === 6. 反 AI ===
                "启用反AI规则": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "额外禁用词": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("short_drama_system", "single_episode_template", "paywall_design")
    FUNCTION = "build_short_drama"
    CATEGORY = "PromptLibrary/剧本输出"

    def build_short_drama(self, **kwargs):
        if not _HAS_MASTERY:
            return ("未加载 director_mastery_v2: " + _MASTERY_ERROR, "", "")

        # 用户要求
        trope = kwargs.get("套路_11选1", "穿越")
        pacing = kwargs.get("爆款公式_8选1", "plateau_cliff")
        reversal = kwargs.get("反转类型", "identity_reveal")
        arc = kwargs.get("角色弧_7选1", "positive_arc")
        aftertaste = kwargs.get("余韵强度", "level_3_medium")
        total_eps = kwargs.get("总集数", 80)
        ep_duration = kwargs.get("单集时长秒", 90)
        paywall_ep = kwargs.get("付费卡点位置_第几集", 8)
        hook_type = kwargs.get("前3秒冲突类型", "身份揭秘")
        hook_strength = kwargs.get("钩子强度_1_10", 9)
        dialogue_max = kwargs.get("对白最大字数", 12)
        gender = kwargs.get("主角性别", "女")
        style = kwargs.get("画风", "现代都市")
        audience = kwargs.get("受众", "女频")
        platform = kwargs.get("目标平台", "ReelShort")
        lang = kwargs.get("字幕语言", "双语")
        ratio = kwargs.get("爽虐甜比例_532", "5 爽 / 3 虐 / 2 甜")

        # ===== 1. 系统级 prompt (导演/编剧) =====
        system_prompt = f"""【任务: 写出 {total_eps} 集 {platform} 风格短剧剧本】

【套路: {trope}】
{DOUYIN_TROPES.get(trope, "")}

【爆款公式: {pacing}】
{PACING_PATTERNS.get(pacing, "")}

【反转类型: {reversal}】
{REVERSAL_TYPES.get(reversal, "")}

【角色弧: {arc}】
{CHARACTER_ARCS.get(arc, "")}

【余韵强度: {aftertaste}】
{AFTERTASTE_LEVELS.get(aftertaste, "")}

【基础设定】
- 总集数: {total_eps} 集
- 单集: {ep_duration} 秒
- 主角性别: {gender}
- 画风: {style}
- 受众: {audience}
- 平台: {platform}
- 语言: {lang}
- 爽虐甜比例: {ratio}
- 对白最大字数: {dialogue_max} 字
- 钩子强度: {hook_strength}/10
- 付费卡点: 第 {paywall_ep} 集

【爆款公式核心 (8 条)】
1. 前 3 秒钩子, 7 秒冲突, 15 秒反转, 30 秒第一个爽点, 60 秒第二个爽点
2. 扁平化人物 (好/坏清楚, 反派脸谱化)
3. 3 集一个小反转, 10 集一个大反转, 全剧不超过 100 集
4. 对白 < {dialogue_max} 字/句, 平均 7 字
5. 3 大情绪: 爽/虐/甜 不断切换 {ratio} 循环
6. 每 5-8 集设付费卡点, 关键时刻卡点
7. 竖屏 9:16, 字幕必须, 镜头快切 1-2 秒/镜
8. 低成本高节奏, 一天拍 3-5 集

【前 3 秒铁律】
{hook_type} 类型钩子, 强度 {hook_strength}/10。前 3 秒必抛强冲突/强悬念/颠覆认知画面, 杜绝铺垫/慢镜头/空镜, 第一秒锁住观众视线。
"""

        # ===== 2. 单集模板 =====
        episode_template = f"""【单集 {ep_duration} 秒标准结构】

0-3s: 黄金开篇 (钩子)
   - {hook_type} 冲突画面 + 直击悬念
   - 拒绝铺垫, 直接进入核心冲突
   - 例: 主角被当场揭穿/被推下楼梯/接到神秘电话/撞见背叛

3-7s: 升级冲突
   - 让冲突更激烈
   - 例: 反派嘲讽/打脸/威胁

7-15s: 第一次反转铺垫
   - 暗示有什么不对
   - 例: 主角发现证据/发现线索/接到来电

15-30s: 第一个爽点 (或虐点)
   - 小高潮, 锁定观众
   - 例: 主角反击/复仇得手/身份曝光

30-60s: 中段剧情 (拉扯)
   - 矛盾升级/误会加深/伏笔预埋/正反对峙
   - 镜头快切, 1-2 秒/镜

60-{ep_duration-3}s: 第二个爽点 (或虐点)
   - 大高潮, 推动剧情

{ep_duration-3}s-{ep_duration}s: 结尾钩子 (锁粉)
   - 突发反转/身份曝光/致命危机/惊天秘密
   - 留白收尾, 悬念拉满
   - 倒逼看下一集

【单集对白铁律】
- 单句对白不超过 {dialogue_max} 字
- 平均对白长度 7 字
- 用短句制造速度感
- 不用书面化/生硬台词
- 贴合 {gender} {audience} 视角
- 不要"瞳孔地震"等 AI 套路

【画面要求】
- 竖屏 9:16
- 1-2 秒/镜 镜头快切
- 所有情节标注镜头景别/动作/细节
- 字幕必加, 居中下方
- 重要对白加 emoji 表情
"""

        # ===== 3. 付费卡点设计 =====
        paywall_design = f"""【{total_eps} 集付费卡点设计 (每 5-8 集)】

{SHORT_DRAMA_PAYWALL.get('paywall_1_reveal', '')}  → 建议第 {paywall_ep} 集
{SHORT_DRAMA_PAYWALL.get('paywall_2_revenge', '')}  → 建议第 {paywall_ep + 5} 集
{SHORT_DRAMA_PAYWALL.get('paywall_3_romance', '')}  → 建议第 {paywall_ep + 10} 集
{SHORT_DRAMA_PAYWALL.get('paywall_4_climax', '')}  → 建议第 {paywall_ep + 15} 集

{SHORT_DRAMA_PAYWALL.get('interval_rule', '')}

【付费卡点时刻的设计原则】
1. 揭秘/反转/复仇/告白/对决 - 关键时刻
2. 每 5-8 集一个, 不可太密集 (用户疲劳)
3. 卡点前 30 秒必须有强烈铺垫
4. 卡点后第一句台词必须是"什么?"
5. 卡点不能解决主冲突, 只暴露信息
"""

        # ===== 4. 注入反 AI 规则 =====
        if kwargs.get("启用反AI规则", True):
            system_prompt = inject_anti_ai_rules(system_prompt)
            episode_template = inject_anti_ai_rules(episode_template)
            paywall_design = inject_anti_ai_rules(paywall_design)

        # 5. 额外禁用词
        extra_ban = kwargs.get("额外禁用词", "")
        if extra_ban:
            system_prompt += f"\n\n【额外禁用词】\n{extra_ban}"

        return (system_prompt, episode_template, paywall_design)


NODE_CLASS_MAPPINGS = {
    "VerticalShortDramaPro": VerticalShortDramaPro,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VerticalShortDramaPro": "📱 垂直短剧 (4/7)",
}
