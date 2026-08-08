# -*- coding: utf-8 -*-
"""
SpatialConsistencyPro — 空间一致性节点 (附件核心)
==================================================
(节点 - 导演级)

附件强调: 2.5 对空间的理解明显变强以后, 创作者不需要再用那么多切镜去藏拙了。
- 一个角色可以在同一空间里连续运动
- 摄影机换一个角度, 模型依然大致知道人物、道具和场景之间是什么关系
- 这会给叙事带来非常直接的变化
- 只有空间稳定, 演员才有地方表演
- 只有镜头愿意停下来, 观众才有时间看见表情
- 只有人物在空间里的位置可信, 走近、远离、回头、躲避这些动作才会产生意义

5 大规则:
1. 连续运动 - 一个角色可以在同一空间里连续运动
2. 角度变化 - 摄影机换一个角度, 关系不变
3. 空间稳定 - 演员才有地方表演
4. 镜头停留 - 观众才有时间看见表情
5. 位置可信 - 走近/远离/回头/躲避产生意义
"""

import os
import sys
import json

try:
    from anti_ai_vocab import (
        ANTI_AI_PHRASES, SPECIFIC_DETAIL_RULES, HUMANIZE_INJECTION,
        DIRECTOR_ANTI_AI_PROMPTS, clean_anti_ai_text, inject_anti_ai_rules,
    )
    from production_pipeline_v3 import SPATIAL_CONSISTENCY_5
    _HAS_ANTI_AI = True
except Exception as e:
    _HAS_ANTI_AI = False
    _ANTI_AI_ERROR = str(e)


# 空间布局 8 种
SPACE_LAYOUTS = {
    "1_厨房_8平米": "8 平米, 冰箱+炉灶+餐桌, 4 人容量, 紧",
    "2_客厅_20平米": "20 平米, 沙发+电视+茶几, 8 人容量, 开阔",
    "3_卧室_12平米": "12 平米, 床+衣柜+梳妆台, 私密",
    "4_办公室_30平米": "30 平米, 办公桌+会议桌, 权力感",
    "5_餐厅_50平米": "50 平米, 多桌, 社交",
    "6_走廊_3米": "3 米长, 单向, 紧张感",
    "7_楼梯": "垂直, 上下权力对比",
    "8_街头": "开放, 路人, 时代感",
}


class SpatialConsistencyPro:
    """
    空间一致性节点 - 拆节点
    核心: 空间稳定, 演员才有地方表演; 镜头愿意停, 观众才有时间看表情
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # === 1. 空间 ===
                "空间类型": (list(SPACE_LAYOUTS.keys()), {"default": "1_厨房_8平米"}),
                "空间细节": ("STRING", {
                    "default": "8 平米厨房, 冰箱在左, 炉灶在右, 餐桌在中, 老式吊灯",
                    "multiline": False,
                }),
                "空间尺寸": ("STRING", {
                    "default": "8 平米, 4x2 米",
                    "multiline": False,
                }),

                # === 2. 角色与道具 ===
                "角色数量": ("INT", {"default": 2, "min": 1, "max": 10}),
                "角色1_位置": ("STRING", {
                    "default": "在炉灶前, 背对镜头",
                    "multiline": False,
                }),
                "角色2_位置": ("STRING", {
                    "default": "在餐桌边, 面对镜头",
                    "multiline": False,
                }),
                "关键道具": ("STRING", {
                    "default": "餐桌/炉灶/冰箱/吊灯",
                    "multiline": False,
                }),

                # === 3. 镜头参数 ===
                "镜头停留秒数": ("INT", {"default": 30, "min": 5, "max": 600}),
                "连续运动": ("BOOLEAN", {"default": True}),
                "换角度次数": ("INT", {"default": 1, "min": 0, "max": 10}),

                # === 4. 5 大规则应用强度 ===
                "连续运动强度_1_10": ("INT", {"default": 9, "min": 1, "max": 10}),
                "空间稳定强度_1_10": ("INT", {"default": 10, "min": 1, "max": 10}),
                "镜头停留强度_1_10": ("INT", {"default": 9, "min": 1, "max": 10}),
                "位置可信强度_1_10": ("INT", {"default": 10, "min": 1, "max": 10}),

                # === 5. 反 AI ===
                "启用反AI规则": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("spatial_design", "5_rules_application", "director_samples")
    FUNCTION = "build_spatial"
    CATEGORY = "PromptLibrary/导演级"

    def build_spatial(self, **kwargs):
        if not _HAS_ANTI_AI:
            return ("未加载: " + _ANTI_AI_ERROR, "", "")

        space_type = kwargs.get("空间类型", "1_厨房_8平米")
        space_detail = kwargs.get("空间细节", "")
        space_size = kwargs.get("空间尺寸", "")
        n_chars = kwargs.get("角色数量", 2)
        c1_pos = kwargs.get("角色1_位置", "")
        c2_pos = kwargs.get("角色2_位置", "")
        props = kwargs.get("关键道具", "")
        cam_stay = kwargs.get("镜头停留秒数", 30)
        continuous = kwargs.get("连续运动", True)
        angle_changes = kwargs.get("换角度次数", 1)
        s1 = kwargs.get("连续运动强度_1_10", 9)
        s2 = kwargs.get("空间稳定强度_1_10", 10)
        s3 = kwargs.get("镜头停留强度_1_10", 9)
        s4 = kwargs.get("位置可信强度_1_10", 10)

        # 1. 空间设计
        design = f"""【空间设计 Bible】

空间类型: {space_type}
空间细节: {space_detail}
空间尺寸: {space_size}

════════════════════════════════════════
5 大规则 (附件核心)
════════════════════════════════════════

【规则 1: 连续运动 - 强度 {s1}/10】
{('一个角色可以在同一空间里连续运动。' if continuous else '切镜较多, 隐藏空间不一致。')}

【规则 2: 角度变化 - {angle_changes} 次换角度】
摄影机换一个角度, 模型依然知道人物/道具/场景之间是什么关系。
{('角色1 位置: ' + c1_pos) if c1_pos else ''}
{('角色2 位置: ' + c2_pos) if c2_pos else ''}
关键道具: {props}

【规则 3: 空间稳定 - 强度 {s2}/10】
只有空间稳定, 演员才有地方表演。
空间稳定 = 角色始终在合理位置, 道具始终在固定位置, 空间始终有物理规则。
- 灯光从窗户来 = 角色背光的一面应该有影子
- 餐桌有 4 把椅子 = 角色坐 1 把, 不能凭空多出椅子
- 冰箱在左 = 角色开冰箱时, 永远从左侧开

【规则 4: 镜头停留 - 强度 {s3}/10, 停留 {cam_stay} 秒】
只有镜头愿意停下来, 观众才有时间看见表情。
{('每个镜头停留 {cam_stay} 秒以上, 不用快速切镜藏拙。' if cam_stay >= 20 else '镜头停留太短, 观众看不到表情。')}
30 秒开始接近一个完整的场景单元。
几分钟的停顿, 看起来什么都没发生, 实际是情感的酝酿。

【规则 5: 位置可信 - 强度 {s4}/10】
只有人物在空间里的位置可信, 走近/远离/回头/躲避这些动作才会产生意义。
- 走近 = 距离缩短, 关系靠近
- 远离 = 距离变远, 关系疏远
- 回头 = 转身, 关系重启
- 躲避 = 离开, 关系破裂

════════════════════════════════════════
{space_type} 空间参考
════════════════════════════════════════

{SPACE_LAYOUTS.get(space_type, '')}

════════════════════════════════════════
5 要素处理
════════════════════════════════════════

【数据】1161 部作品 director_view 14 维 + 63 导演 12 维档案

【上下文缩略】
- 空间: {space_type}, {space_size}
- 角色: {n_chars} 个
- 道具: {props}
- 镜头: 停留 {cam_stay} 秒

【Skill/Harness】
- 5 大空间规则 (附件)
- 8 种空间布局
- 5 大空间一致性检查点
- 4 维空间设计 (大小/布局/灯光/声音)

【经验矩阵】15 导演真实空间风格
- 王家卫: 拥挤城市, 镜中空间
- 塔可夫斯基: 单一空间长镜头
- 侯孝贤: 长镜头自然空间
- 是枝裕和: 家庭日常空间
- 诺兰: 旋转走廊 (盗梦空间)
- 库布里克: 对称走廊
- 奉俊昊: 楼梯垂直空间

【AI 深度处理】
- 反 AI 词表: 191 条禁用
- 空间一致性: 4 检查点
  1. 角色位置始终合理
  2. 道具位置始终固定
  3. 灯光阴影物理正确
  4. 镜头换角度关系不变
"""

        # 2. 5 规则应用
        rules_app = "5 大规则应用强度:\n"
        for k, v in SPATIAL_CONSISTENCY_5.items():
            rules_app += f"\n  {k}:\n    {v}"

        # 3. 导演样本
        director_samples = "15 导演真实空间风格:\n"
        for d, art in [
            ("王家卫", "拥挤城市, 镜中空间"),
            ("塔可夫斯基", "单一空间长镜头"),
            ("侯孝贤", "长镜头自然空间"),
            ("是枝裕和", "家庭日常空间"),
            ("诺兰", "旋转走廊 (盗梦空间)"),
            ("库布里克", "对称走廊"),
            ("奉俊昊", "楼梯垂直空间"),
        ]:
            director_samples += f"  - {d}: {art}\n"

        if kwargs.get("启用反AI规则", True):
            design = inject_anti_ai_rules(design)

        return (design, rules_app, director_samples)


NODE_CLASS_MAPPINGS = {
    "SpatialConsistencyPro": SpatialConsistencyPro,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SpatialConsistencyPro": "📐 空间一致性 (附件核心)",
}
