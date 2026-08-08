# -*- coding: utf-8 -*-
"""
Phase 17 - 导演灵魂节点 (Director Soul Node)
================================================
L5+ 顶级导演级 + AIGC 影视全流程解析 + 情感矩阵 + 灵魂维度

核心设计哲学:
- AI 不会有真正的"灵魂" (个人、欲望、创伤、叛逆)
- 但可以用情感矩阵 + 融合算法 + 灵魂维度来**极限模拟**顶级导演的"灵魂"
- 让所有其他节点能接收灵魂注入

核心组成:
1. EMOTION_MATRIX_60 - 60+ 种情感完整定义 (基于 Plutchik + Izard + Geneva + Barrett)
2. EMOTION_FUSION_7 - 7 大情感融合公式 (单情感 / 双情感 / 多情感 + 不同比例)
3. SOUL_DIMENSIONS_10 - 10 大灵魂维度 (创造力/想象力/艺术表达/镜头语言/氛围掌控/精神状态/灵感/叛逆/怀疑/突破)
4. SOUL_STATE - 当前灵魂状态 (灵感指数/疲劳指数/叛逆指数/怀疑指数)
5. SOUL_OUTPUT - 注入到所有其他节点的格式

参考理论:
- Plutchik's Wheel of Emotions (1980) - 8 基础情感 + 强度 + 二元组合
- Izard 10 基础情感 (1977)
- Geneva Emotion Wheel (GEW) - 4 维情感
- Barrett 建构情绪理论 (2006) - 情绪是大脑在情境和先验下建构的
- Lazarus 认知-评价理论
- Russell 环形模型 (Valence-Arousal 2D)
"""

import os
import sys
import json
import random
import math

# ============================================================
# 1. EMOTION_MATRIX_60 - 60+ 种情感完整定义
# ============================================================
# 基于 Plutchik 8 基础情感 + 3 强度级别 + 复合二元 + Izard 10 基础 + 复杂情感
EMOTION_MATRIX_60 = {
    # ===== 8 基础情感 (Plutchik) × 3 强度 = 24 种 =====
    # 1. Joy (喜悦) - 极性正
    "joy_serenity": {
        "name": "Serenity 安宁",
        "category": "Joy",
        "intensity": 0.3,
        "polarity": "positive",
        "arousal": "low",
        "description": "内心平静, 波澜不惊, 微笑而不动声色",
        "visual_signs": "微微上扬嘴角, 呼吸平稳, 眼神温和不闪烁",
        "voice_signs": "语速中速, 音调中等, 没有起伏",
        "facial_au": "AU12 (轻微嘴角上扬)",
        "inner_monologue": "这一刻, 我选择不打扰这份安宁",
        "color_palette": "淡蓝, 浅米, 雾白",
        "music_tempo": "60-70 BPM, 钢琴单音",
        "director_examples": "是枝裕和《步履不停》 - 全家聚餐, 安宁的午后",
    },
    "joy_pleasure": {
        "name": "Pleasure 愉悦",
        "category": "Joy",
        "intensity": 0.6,
        "polarity": "positive",
        "arousal": "medium",
        "description": "发自内心的满足和快乐",
        "visual_signs": "明显笑容, 眼睛眯起, 身体微微前倾",
        "voice_signs": "语速略快, 音调高, 有自然停顿的笑声",
        "facial_au": "AU6+AU12 (杜兴式微笑)",
        "inner_monologue": "这一刻值得被记住",
        "color_palette": "暖黄, 浅粉, 蜜桃",
        "music_tempo": "80-100 BPM, 弦乐轻快",
        "director_examples": "宫崎骏《龙猫》 - 姐妹俩在田野奔跑",
    },
    "joy_ecstasy": {
        "name": "Ecstasy 狂喜",
        "category": "Joy",
        "intensity": 1.0,
        "polarity": "positive",
        "arousal": "high",
        "description": "极致的高潮, 失去自我控制",
        "visual_signs": "大笑, 身体完全放松, 手臂张开",
        "voice_signs": "语速极快, 音调极高, 笑声不断",
        "facial_au": "AU6+AU12+AU25+AU26 (全开笑)",
        "inner_monologue": "这一刻我是完整的",
        "color_palette": "金黄, 朱红, 鲜橙",
        "music_tempo": "120-150 BPM, 鼓点密集",
        "director_examples": "PTA《不羁夜》 - 色情业黄金时代的派对高潮",
    },
    # 2. Trust (信任) - 极性正
    "trust_acceptance": {
        "name": "Acceptance 接纳",
        "category": "Trust",
        "intensity": 0.3,
        "polarity": "positive",
        "arousal": "low",
        "description": "接受现状, 没有防备",
        "visual_signs": "身体放松, 双手自然垂放, 没有紧张动作",
        "voice_signs": "语速慢, 音调平, 没有抑扬",
        "facial_au": "AU1+AU2 (眉毛自然)",
        "inner_monologue": "我不需要解释, 你也不需要",
        "color_palette": "米白, 浅灰绿, 燕麦",
        "music_tempo": "50-60 BPM, 大提琴",
        "director_examples": "王家卫《花样年华》 - 走廊里的擦肩而过",
    },
    "trust_admiration": {
        "name": "Admiration 仰慕",
        "category": "Trust",
        "intensity": 0.7,
        "polarity": "positive",
        "arousal": "medium",
        "description": "对他人由衷的尊重和欣赏",
        "visual_signs": "眼睛注视对方, 微微点头, 嘴角上扬",
        "voice_signs": "音调略高, 语速正常, 偶尔停顿表示尊重",
        "facial_au": "AU1+AU2+AU12",
        "inner_monologue": "这个人值得我学习",
        "color_palette": "暖金, 灰蓝, 米色",
        "music_tempo": "70-80 BPM, 小提琴独奏",
        "director_examples": "斯皮尔伯格《林肯》 - 林肯看麦克白",
    },
    "trust_surrender": {
        "name": "Surrender 臣服",
        "category": "Trust",
        "intensity": 1.0,
        "polarity": "positive",
        "arousal": "high",
        "description": "完全交出控制权, 极致信任",
        "visual_signs": "身体完全放松, 闭眼, 双手打开",
        "voice_signs": "语速极慢, 音调低, 完全柔软",
        "facial_au": "AU43 (闭眼) + AU1+AU2 (无防备)",
        "inner_monologue": "我把自己完全交给你",
        "color_palette": "柔白, 浅金, 淡粉",
        "music_tempo": "40-50 BPM, 风铃",
        "director_examples": "塔可夫斯基《飞向太空》 - 宇宙中的彻底静谧",
    },
    # 3. Fear (恐惧) - 极性负
    "fear_timidity": {
        "name": "Timidity 胆怯",
        "category": "Fear",
        "intensity": 0.3,
        "polarity": "negative",
        "arousal": "low",
        "description": "隐约的不安, 怕被注意",
        "visual_signs": "肩膀微缩, 视线躲避, 身体语言收缩",
        "voice_signs": "音量小, 语速慢, 经常停顿",
        "facial_au": "AU4 (眉间皱)",
        "inner_monologue": "也许没人注意到我",
        "color_palette": "灰紫, 暗蓝, 苍白",
        "music_tempo": "50-60 BPM, 弦乐低吟",
        "director_examples": "伯格曼《假面》 - 伊丽莎白在派对角落",
    },
    "fear_apprehension": {
        "name": "Apprehension 忧虑",
        "category": "Fear",
        "intensity": 0.6,
        "polarity": "negative",
        "arousal": "medium",
        "description": "对未来的明确担忧",
        "visual_signs": "咬唇, 手指搓动, 眼神不定",
        "voice_signs": "语速不规律, 经常重复, 音调颤抖",
        "facial_au": "AU4+AU5+AU7+AU20 (焦虑组合)",
        "inner_monologue": "接下来会发生什么",
        "color_palette": "深绿, 冷蓝, 铁灰",
        "music_tempo": "70-80 BPM, 渐强弦乐",
        "director_examples": "希区柯克《后窗》 - 杰夫发现真相",
    },
    "fear_terror": {
        "name": "Terror 恐惧",
        "category": "Fear",
        "intensity": 1.0,
        "polarity": "negative",
        "arousal": "high",
        "description": "极致的惊恐, 完全失去理性",
        "visual_signs": "瞳孔放大, 嘴张, 全身僵硬, 脸色苍白",
        "voice_signs": "尖叫, 语速失控, 音调极高",
        "facial_au": "AU1+AU2+AU5+AU20+AU26 (恐惧全开)",
        "inner_monologue": "完了完了完了",
        "color_palette": "血红, 漆黑, 惨白",
        "music_tempo": "150+ BPM, 失谐弦乐",
        "director_examples": "波兰斯基《罗斯玛丽的婴儿》 - 罗斯玛丽看到孩子",
    },
    # 4. Surprise (惊讶) - 极性中性
    "surprise_uncertainty": {
        "name": "Uncertainty 困惑",
        "category": "Surprise",
        "intensity": 0.3,
        "polarity": "neutral",
        "arousal": "low",
        "description": "不确定发生了什么的瞬间",
        "visual_signs": "眉毛微抬, 头微倾, 眼睛微眯",
        "voice_signs": "音调上扬, 语速变慢, 经常\"嗯?\"",
        "facial_au": "AU1+AU2 (轻微扬眉)",
        "inner_monologue": "等等, 这是什么",
        "color_palette": "雾灰, 浅紫, 米白",
        "music_tempo": "50-60 BPM, 不和谐音",
        "director_examples": "林奇《穆赫兰道》 - Betty 醒来",
    },
    "surprise_astonishment": {
        "name": "Astonishment 惊讶",
        "category": "Surprise",
        "intensity": 0.7,
        "polarity": "neutral",
        "arousal": "high",
        "description": "明确感到出乎意料",
        "visual_signs": "眼睛睁大, 嘴微张, 身体后仰",
        "voice_signs": "音量增大, 语速变快, 经常\"啊!\"",
        "facial_au": "AU1+AU2+AU5B+AU26 (惊讶全开)",
        "inner_monologue": "这不可能!",
        "color_palette": "亮白, 鲜红, 鲜蓝",
        "music_tempo": "突然的强音",
        "director_examples": "诺兰《记忆碎片》 - Lenny 找到照片",
    },
    "surprise_amazement": {
        "name": "Amazement 惊异",
        "category": "Surprise",
        "intensity": 1.0,
        "polarity": "positive/neutral",
        "arousal": "high",
        "description": "面对伟大或神秘的敬畏",
        "visual_signs": "眼睛极亮, 嘴张, 双手举起, 后退半步",
        "voice_signs": "语速极慢, 经常无言, 偶发\"哇\"",
        "facial_au": "AU1+AU2+AU5B+AU26 (震撼全开)",
        "inner_monologue": "这是真的存在吗",
        "color_palette": "金色, 极光色, 紫红",
        "music_tempo": "全乐队爆发",
        "director_examples": "维伦纽瓦《降临》 - 第一次看到外星人文字",
    },
    # 5. Sadness (悲伤) - 极性负
    "sadness_gloominess": {
        "name": "Gloominess 阴郁",
        "category": "Sadness",
        "intensity": 0.3,
        "polarity": "negative",
        "arousal": "low",
        "description": "淡淡的忧伤, 没有原因的失落",
        "visual_signs": "眉下垂, 嘴角下垂, 视线下移",
        "voice_signs": "音调低, 语速慢, 经常停顿",
        "facial_au": "AU1+AU4+AU15 (悲伤三件套)",
        "inner_monologue": "不知道为什么, 有点难过",
        "color_palette": "灰蓝, 暗紫, 阴沉",
        "music_tempo": "40-50 BPM, 钢琴低音",
        "director_examples": "王家卫《重庆森林》 - 何志武在电话亭旁",
    },
    "sadness_sorrow": {
        "name": "Sorrow 悲痛",
        "category": "Sadness",
        "intensity": 0.7,
        "polarity": "negative",
        "arousal": "medium",
        "description": "明确的失去带来的痛苦",
        "visual_signs": "眼眶湿润, 嘴唇紧抿, 身体蜷缩",
        "voice_signs": "音调颤抖, 经常哽咽, 句子碎裂",
        "facial_au": "AU1+AU4+AU7+AU15+AU17 (悲痛全开)",
        "inner_monologue": "为什么是他 / 为什么是她",
        "color_palette": "深蓝灰, 阴雨色, 苍白",
        "music_tempo": "30-40 BPM, 大提琴低吟",
        "director_examples": "是枝裕和《步履不停》 - 黄昏散步, 想起长子",
    },
    "sadness_grief": {
        "name": "Grief 悲恸",
        "category": "Sadness",
        "intensity": 1.0,
        "polarity": "negative",
        "arousal": "high",
        "description": "极致的失去, 不可承受的痛",
        "visual_signs": "哭, 全身颤抖, 身体折叠, 失语",
        "voice_signs": "无声, 哭到失声, 反复抽泣",
        "facial_au": "AU1+AU4+AU7+AU15+AU17+AU43 (全开)",
        "inner_monologue": "再也回不来了",
        "color_palette": "漆黑, 极暗蓝, 阴影",
        "music_tempo": "停止, 只有呼吸声",
        "director_examples": "PTA《魅影缝匠》 - Reynolds 在餐厅崩溃",
    },
    # 6. Disgust (厌恶) - 极性负
    "disgust_dislike": {
        "name": "Dislike 反感",
        "category": "Disgust",
        "intensity": 0.3,
        "polarity": "negative",
        "arousal": "low",
        "description": "轻微的不喜欢, 距离感",
        "visual_signs": "嘴角微撇, 鼻翼微皱, 视线偏移",
        "voice_signs": "音调平, 经常叹气",
        "facial_au": "AU9 (轻微上唇提)",
        "inner_monologue": "我不太想接近",
        "color_palette": "灰绿, 暗黄, 浊色",
        "music_tempo": "60-70 BPM, 慢板",
        "director_examples": "伯格曼《沉默》 - 姐妹俩的疏离",
    },
    "disgust_revulsion": {
        "name": "Revulsion 反感",
        "category": "Disgust",
        "intensity": 0.7,
        "polarity": "negative",
        "arousal": "high",
        "description": "明确的排斥和不适",
        "visual_signs": "后仰, 遮脸, 身体退缩",
        "voice_signs": "呕吐反射, 音调升高",
        "facial_au": "AU9+AU15+AU17 (厌恶组合)",
        "inner_monologue": "这太恶心了",
        "color_palette": "恶心的黄绿, 浊紫",
        "music_tempo": "不和谐音",
        "director_examples": "PTA《血色将至》 - Daniel 第一次看到矿井",
    },
    "disgust_loathing": {
        "name": "Loathing 憎恶",
        "category": "Disgust",
        "intensity": 1.0,
        "polarity": "negative",
        "arousal": "high",
        "description": "极致的厌恶, 道德层面的强烈排斥",
        "visual_signs": "嘴歪, 眼寒, 全身紧绷, 准备攻击",
        "voice_signs": "音量极高, 音调尖锐, 颤抖",
        "facial_au": "AU9+AU15+AU16+AU17+AU26 (全开)",
        "inner_monologue": "我要让这个人付出代价",
        "color_palette": "毒绿, 焦黑, 病态黄",
        "music_tempo": "失谐重音",
        "director_examples": "奉俊昊《寄生虫》 - 金基泽看朴社长",
    },
    # 7. Anger (愤怒) - 极性负
    "anger_annoyance": {
        "name": "Annoyance 烦恼",
        "category": "Anger",
        "intensity": 0.3,
        "polarity": "negative",
        "arousal": "low",
        "description": "轻度的不耐烦, 没有爆发",
        "visual_signs": "眉头微皱, 嘴角下撇, 视线躲避",
        "voice_signs": "音调略高, 经常叹气",
        "facial_au": "AU4+AU17 (皱眉 + 嘴角下)",
        "inner_monologue": "我不想被打扰",
        "color_palette": "暗橙, 浊黄",
        "music_tempo": "70 BPM, 烦躁弦乐",
        "director_examples": "王家卫《阿飞正传》 - 旭仔被拒绝后",
    },
    "anger_frustration": {
        "name": "Frustration 挫败",
        "category": "Anger",
        "intensity": 0.7,
        "polarity": "negative",
        "arousal": "high",
        "description": "明确感到挫败, 但未完全爆发",
        "visual_signs": "咬牙, 拳握, 鼻翼张, 视线锁定",
        "voice_signs": "语速快, 音调高, 经常咬字",
        "facial_au": "AU4+AU5+AU7+AU17+AU23 (愤怒组合)",
        "inner_monologue": "我一定要做到",
        "color_palette": "红橙, 暗红",
        "music_tempo": "100 BPM, 鼓点重",
        "director_examples": "诺兰《黑暗骑士》 - 蝙蝠侠追小丑",
    },
    "anger_fury": {
        "name": "Fury 暴怒",
        "category": "Anger",
        "intensity": 1.0,
        "polarity": "negative",
        "arousal": "high",
        "description": "极致的愤怒, 失去理性",
        "visual_signs": "吼, 摔物, 攻击, 全身通红",
        "voice_signs": "咆哮, 音调极高, 完全失控",
        "facial_au": "AU4+AU5+AU7+AU17+AU23+AU26+AU27 (全开)",
        "inner_monologue": "我要毁了一切",
        "color_palette": "血红, 漆黑, 火焰色",
        "music_tempo": "失谐重击",
        "director_examples": "芬奇《七宗罪》 - Pitt 看到冰箱里",
    },
    # 8. Anticipation (期待) - 极性正
    "anticipation_interest": {
        "name": "Interest 兴趣",
        "category": "Anticipation",
        "intensity": 0.3,
        "polarity": "positive",
        "arousal": "low",
        "description": "对某事的轻微好奇",
        "visual_signs": "眉毛微抬, 头微前倾, 眼神专注",
        "voice_signs": "音调略高, 语速略快",
        "facial_au": "AU1+AU2 (抬眉)",
        "inner_monologue": "我有点想知道",
        "color_palette": "浅黄, 暖白",
        "music_tempo": "70 BPM, 轻快",
        "director_examples": "诺兰《盗梦空间》 - Cobb 看陀螺",
    },
    "anticipation_expectation": {
        "name": "Expectation 期待",
        "category": "Anticipation",
        "intensity": 0.7,
        "polarity": "positive",
        "arousal": "medium",
        "description": "明确的期待感, 关注未来",
        "visual_signs": "身体前倾, 眼睛睁大, 嘴角微扬",
        "voice_signs": "语速加快, 音调升高, 经常追问",
        "facial_au": "AU1+AU2+AU5+AU12 (期待组合)",
        "inner_monologue": "快了, 快了",
        "color_palette": "暖橙, 鲜黄, 浅红",
        "music_tempo": "90 BPM, 渐强",
        "director_examples": "诺兰《信条》 - 主角理解时间逆转",
    },
    "anticipation_vigilance": {
        "name": "Vigilance 警觉",
        "category": "Anticipation",
        "intensity": 1.0,
        "polarity": "neutral",
        "arousal": "high",
        "description": "极度警觉, 准备应对威胁",
        "visual_signs": "眼睛扫描环境, 全身紧绷, 准备行动",
        "voice_signs": "语速极快, 音调高, 简短的命令式",
        "facial_au": "AU1+AU2+AU4+AU5+AU7 (警觉全开)",
        "inner_monologue": "准备行动",
        "color_palette": "冷蓝, 银白, 警戒橙",
        "music_tempo": "120 BPM, 紧张鼓点",
        "director_examples": "诺兰《敦刻尔克》 - 飞行员在驾驶舱",
    },
    # ===== Izard 10 基础情感 (扩展 Plutchik) =====
    "interest": {
        "name": "Interest 兴趣",
        "category": "Izard",
        "intensity": 0.5,
        "polarity": "positive",
        "arousal": "medium",
        "description": "主动的探索欲, 注意力集中",
        "visual_signs": "眉毛微抬, 眼睛明亮, 头前倾",
        "voice_signs": "音调升高, 语速加快",
        "facial_au": "AU1+AU2+AU7 (兴趣组合)",
        "inner_monologue": "我想了解更多",
        "color_palette": "亮黄, 浅绿",
        "music_tempo": "80 BPM, 好奇弦乐",
        "director_examples": "塔可夫斯基《镜子》 - 探索童年",
    },
    "shyness": {
        "name": "Shyness 羞怯",
        "category": "Izard",
        "intensity": 0.5,
        "polarity": "negative",
        "arousal": "medium",
        "description": "被注意时的不自在",
        "visual_signs": "视线下移, 身体微缩, 脸红",
        "voice_signs": "音量小, 语速慢, 经常中断",
        "facial_au": "AU1+AU2+AU20 (羞怯组合)",
        "inner_monologue": "我宁愿不被看到",
        "color_palette": "淡粉, 苍白",
        "music_tempo": "60 BPM, 轻柔",
        "director_examples": "伯格曼《芬妮与亚历山大》 - 孩子们",
    },
    "guilt": {
        "name": "Guilt 愧疚",
        "category": "Izard",
        "intensity": 0.7,
        "polarity": "negative",
        "arousal": "low",
        "description": "对做过的事的内疚",
        "visual_signs": "视线下移, 身体蜷缩, 不敢看人",
        "voice_signs": "音量小, 经常道歉, 句子断",
        "facial_au": "AU1+AU4+AU15 (内疚组合)",
        "inner_monologue": "我不该那样做",
        "color_palette": "暗灰, 阴绿",
        "music_tempo": "40 BPM, 钢琴单音",
        "director_examples": "约阿希姆·提尔《情感价值》 - 父亲独白",
    },
    "contempt": {
        "name": "Contempt 轻蔑",
        "category": "Izard",
        "intensity": 0.6,
        "polarity": "negative",
        "arousal": "low",
        "description": "从道德/智识层面的优越感俯视",
        "visual_signs": "单侧嘴角上扬, 视线俯视",
        "voice_signs": "音调平, 经常用\"哼\"开头",
        "facial_au": "AU12R (单侧嘴角上扬) + AU14",
        "inner_monologue": "你不配",
        "color_palette": "暗金, 浊紫",
        "music_tempo": "50 BPM, 单音",
        "director_examples": "斯科塞斯《华尔街之狼》 - Belfort 看客户",
    },
    "shame": {
        "name": "Shame 羞耻",
        "category": "Izard",
        "intensity": 0.8,
        "polarity": "negative",
        "arousal": "high",
        "description": "暴露后的强烈自我否定",
        "visual_signs": "头低垂, 想消失, 脸通红",
        "voice_signs": "完全失语, 或者极小声",
        "facial_au": "AU1+AU4+AU20+AU52 (羞耻组合)",
        "inner_monologue": "我应该消失",
        "color_palette": "血红色 (脸部) + 灰色 (背景)",
        "music_tempo": "30 BPM, 完全安静",
        "director_examples": "布努埃尔《泯灭天使》 - 上流社会的崩溃",
    },
    "pride": {
        "name": "Pride 骄傲",
        "category": "Izard",
        "intensity": 0.7,
        "polarity": "positive",
        "arousal": "medium",
        "description": "对自己的成就感",
        "visual_signs": "胸挺, 头高, 视线平视",
        "voice_signs": "音调高, 语速正常, 坚定",
        "facial_au": "AU12+AU53+AU58 (骄傲组合)",
        "inner_monologue": "我做到了",
        "color_palette": "金, 深红, 皇家蓝",
        "music_tempo": "100 BPM, 雄壮弦乐",
        "director_examples": "PTA《不羁夜》 - Dirk 完成电影",
    },
    # ===== 5 大复杂情感 (复合) =====
    "love": {
        "name": "Love 爱",
        "category": "Complex",
        "intensity": 0.85,
        "polarity": "positive",
        "arousal": "medium",
        "description": "Joy + Trust 二元组合, 深层依恋",
        "visual_signs": "注视对方时瞳孔扩张, 嘴角自然上扬, 身体微微前倾",
        "voice_signs": "音调柔和, 语速放慢, 经常停顿",
        "facial_au": "AU6+AU12+AU1+AU2 (爱的微表情)",
        "inner_monologue": "我愿意为你做任何事",
        "color_palette": "暖金 + 浅粉, 玫瑰金",
        "music_tempo": "60-80 BPM, 弦乐 + 钢琴",
        "director_examples": "王家卫《花样年华》 - 周慕云与苏丽珍",
        "fusion": "Joy + Trust",
    },
    "hate": {
        "name": "Hate 恨",
        "category": "Complex",
        "intensity": 0.95,
        "polarity": "negative",
        "arousal": "high",
        "description": "Anger + Fear 二元组合, 极致敌意",
        "visual_signs": "眼睛冰冷, 嘴紧, 全身僵硬",
        "voice_signs": "完全冰冷, 经常沉默",
        "facial_au": "AU4+AU5+AU7+AU17+AU24 (恨的组合)",
        "inner_monologue": "我要让你付出代价",
        "color_palette": "漆黑, 血红, 死灰",
        "music_tempo": "50 BPM, 不和谐音",
        "director_examples": "PTA《血色将至》 - Plainview 杀 Eli",
        "fusion": "Anger + Fear",
    },
    "awe": {
        "name": "Awe 敬畏",
        "category": "Complex",
        "intensity": 0.9,
        "polarity": "positive",
        "arousal": "high",
        "description": "Fear + Surprise 二元组合, 面对伟大的震撼",
        "visual_signs": "眼睛极大, 嘴张, 后退半步, 双手举起",
        "voice_signs": "语速极慢, 经常无言, 偶发\"哇\"",
        "facial_au": "AU1+AU2+AU5B+AU26+AU27 (敬畏全开)",
        "inner_monologue": "这超越了语言",
        "color_palette": "金色, 极光色, 紫红, 圣光",
        "music_tempo": "全乐队 + 和声",
        "director_examples": "维伦纽瓦《降临》 - Louise 看外星文字",
        "fusion": "Fear + Surprise",
    },
    "aggressiveness": {
        "name": "Aggressiveness 攻击性",
        "category": "Complex",
        "intensity": 0.85,
        "polarity": "negative",
        "arousal": "high",
        "description": "Anger + Anticipation 二元组合, 准备攻击",
        "visual_signs": "身体前倾, 拳紧, 鼻翼张, 视线锁定",
        "voice_signs": "音调高, 攻击性语速, 经常咆哮",
        "facial_au": "AU4+AU5+AU7+AU17+AU23+AU26 (攻击组合)",
        "inner_monologue": "先发制人",
        "color_palette": "血红, 黑, 攻击橙",
        "music_tempo": "120 BPM, 失谐鼓点",
        "director_examples": "希区柯克《精神病患者》 - Norman 戴母亲面具",
        "fusion": "Anger + Anticipation",
    },
    "optimism": {
        "name": "Optimism 乐观",
        "category": "Complex",
        "intensity": 0.7,
        "polarity": "positive",
        "arousal": "low",
        "description": "Anticipation + Joy 二元组合, 期待好事",
        "visual_signs": "眼睛明亮, 嘴角自然上扬, 身体放松",
        "voice_signs": "语速略快, 音调高, 经常用未来时",
        "facial_au": "AU6+AU12+AU1+AU2+AU5 (乐观组合)",
        "inner_monologue": "明天会更好",
        "color_palette": "浅金, 暖白, 浅蓝",
        "music_tempo": "80 BPM, 轻快弦乐",
        "director_examples": "宫崎骏《哈尔的移动城堡》 - 苏菲变年轻后",
        "fusion": "Anticipation + Joy",
    },
    "disapproval": {
        "name": "Disapproval 反对",
        "category": "Complex",
        "intensity": 0.6,
        "polarity": "negative",
        "arousal": "medium",
        "description": "Surprise + Sadness 二元组合, 失望",
        "visual_signs": "嘴角下撇, 摇头, 视线回避",
        "voice_signs": "音调低, 经常用\"但是\"",
        "facial_au": "AU1+AU4+AU15 (反对组合)",
        "inner_monologue": "我不认同",
        "color_palette": "灰蓝, 暗紫",
        "music_tempo": "60 BPM, 低音",
        "director_examples": "斯科塞斯《基督最后的诱惑》 - 宗教审判",
        "fusion": "Surprise + Sadness",
    },
    "remorse": {
        "name": "Remorse 悔恨",
        "category": "Complex",
        "intensity": 0.85,
        "polarity": "negative",
        "arousal": "low",
        "description": "Sadness + Disgust 二元组合, 对自己行为的痛",
        "visual_signs": "眼眶湿润, 全身蜷缩, 头低",
        "voice_signs": "经常说\"我错了\"",
        "facial_au": "AU1+AU4+AU15+AU17 (悔恨组合)",
        "inner_monologue": "我多希望时光倒流",
        "color_palette": "深蓝, 灰紫, 苍白",
        "music_tempo": "30 BPM, 大提琴低吟",
        "director_examples": "约阿希姆·提尔《情感价值》 - 父亲的独白",
        "fusion": "Sadness + Disgust",
    },
    # ===== 10 种状态情感 (Plutchik 之外的更复杂组合) =====
    "loneliness": {
        "name": "Loneliness 孤独",
        "category": "State",
        "intensity": 0.7,
        "polarity": "negative",
        "arousal": "low",
        "description": "渴望连接但无连接的状态",
        "visual_signs": "身体蜷缩, 视线远眺, 经常独自一人",
        "voice_signs": "经常沉默, 偶发自言自语",
        "facial_au": "AU1+AU4+AU15+AU43 (孤独组合)",
        "inner_monologue": "有谁在听吗",
        "color_palette": "冷蓝, 苍白, 灰",
        "music_tempo": "40 BPM, 单音钢琴",
        "director_examples": "塔可夫斯基《镜子》 - 独居的母亲",
    },
    "longing": {
        "name": "Longing 思念",
        "category": "State",
        "intensity": 0.7,
        "polarity": "mixed",
        "arousal": "medium",
        "description": "对远方的人/物的深刻思念",
        "visual_signs": "凝视远方, 手抚旧物, 眼有泪光",
        "voice_signs": "音调柔, 经常说远方的人名",
        "facial_au": "AU1+AU2+AU4+AU15+AU43 (思念组合)",
        "inner_monologue": "如果他在就好了",
        "color_palette": "暖黄, 雾蓝, 金光",
        "music_tempo": "50-60 BPM, 大提琴 + 钢琴",
        "director_examples": "王家卫《春光乍泄》 - 黎耀辉在瀑布前",
    },
    "bittersweet": {
        "name": "Bittersweet 苦乐参半",
        "category": "State",
        "intensity": 0.6,
        "polarity": "mixed",
        "arousal": "low",
        "description": "Joy + Sadness 同时存在",
        "visual_signs": "微笑时眼角有泪, 笑声变轻",
        "voice_signs": "经常停顿, 句子在结尾时变轻",
        "facial_au": "AU6+AU12+AU1+AU4+AU15 (矛盾组合)",
        "inner_monologue": "如果我快乐的时候你在就好了",
        "color_palette": "金 + 蓝, 暖白 + 冷灰",
        "music_tempo": "60 BPM, 大调小调交替",
        "director_examples": "是枝裕和《步履不停》 - 母亲去世后父亲做天妇罗",
        "fusion": "Joy + Sadness",
    },
    "nostalgia": {
        "name": "Nostalgia 怀旧",
        "category": "State",
        "intensity": 0.6,
        "polarity": "mixed",
        "arousal": "low",
        "description": "对过去的温暖回忆, 略带忧伤",
        "visual_signs": "抚摸旧物, 看老照片, 微笑而眼神遥远",
        "voice_signs": "经常说\"那时候...\"",
        "facial_au": "AU1+AU2+AU6+AU12+AU15 (怀旧组合)",
        "inner_monologue": "那时候一切都简单",
        "color_palette": "褪色暖色, 暖黄, 复古蓝",
        "music_tempo": "60 BPM, 复古钢琴",
        "director_examples": "王家卫《花样年华》 - 60 年代的香港",
    },
    "tension": {
        "name": "Tension 紧张",
        "category": "State",
        "intensity": 0.7,
        "polarity": "negative",
        "arousal": "high",
        "description": "Anticipation + Fear 同时存在, 等待坏事",
        "visual_signs": "咬指甲, 全身紧绷, 视线锁定",
        "voice_signs": "音调不稳, 语速快, 经常屏气",
        "facial_au": "AU4+AU5+AU7+AU20+AU23 (紧张组合)",
        "inner_monologue": "希望不要发生",
        "color_palette": "冷蓝, 紧张红, 阴影",
        "music_tempo": "100 BPM, 紧张弦乐渐强",
        "director_examples": "希区柯克《惊魂记》 - 浴室场景",
        "fusion": "Anticipation + Fear",
    },
    "tenderness": {
        "name": "Tenderness 温柔",
        "category": "State",
        "intensity": 0.6,
        "polarity": "positive",
        "arousal": "low",
        "description": "对脆弱的事物的保护性温柔",
        "visual_signs": "动作轻柔, 声音放低, 眼神温柔",
        "voice_signs": "音调极低极柔, 经常用昵称",
        "facial_au": "AU1+AU2+AU12+AU41 (温柔组合)",
        "inner_monologue": "我来保护你",
        "color_palette": "暖粉, 浅金, 柔白",
        "music_tempo": "50 BPM, 钢琴 + 弦乐轻奏",
        "director_examples": "是枝裕和《奇迹》 - 父母对孩子的温柔",
    },
    "relief": {
        "name": "Relief 如释重负",
        "category": "State",
        "intensity": 0.7,
        "polarity": "positive",
        "arousal": "low",
        "description": "长期压力后的突然释放",
        "visual_signs": "全身放松, 长呼气, 微笑浮现",
        "voice_signs": "语速变慢, 音量降低, 经常\"啊...\"",
        "facial_au": "AU1+AU2+AU12+AU24 (释然组合)",
        "inner_monologue": "终于过去了",
        "color_palette": "暖白, 浅蓝, 柔和",
        "music_tempo": "60 BPM, 渐慢",
        "director_examples": "诺兰《盗梦空间》 - Cobb 见到孩子",
    },
    "despair": {
        "name": "Despair 绝望",
        "category": "State",
        "intensity": 1.0,
        "polarity": "negative",
        "arousal": "low",
        "description": "完全失去希望, 比悲伤更深",
        "visual_signs": "眼神失焦, 全身瘫软, 不愿动",
        "voice_signs": "完全失语, 或者极小声",
        "facial_au": "AU1+AU4+AU15+AU17+AU43 (绝望组合)",
        "inner_monologue": "已经没有任何意义了",
        "color_palette": "深灰, 死蓝, 苍白",
        "music_tempo": "20 BPM, 只有呼吸声",
        "director_examples": "塔可夫斯基《牺牲》 - 主人公的献祭",
    },
    "hope": {
        "name": "Hope 希望",
        "category": "State",
        "intensity": 0.7,
        "polarity": "positive",
        "arousal": "medium",
        "description": "在黑暗中看到光明的状态",
        "visual_signs": "眼睛亮, 嘴角自然上扬, 身体微微挺",
        "voice_signs": "音调升高, 经常用未来时",
        "facial_au": "AU1+AU2+AU5+AU12 (希望组合)",
        "inner_monologue": "总会有办法的",
        "color_palette": "暖金, 浅黄, 晨曦",
        "music_tempo": "70 BPM, 渐强轻快",
        "director_examples": "宫崎骏《千与千寻》 - 千寻找到工作",
    },
    "gratitude": {
        "name": "Gratitude 感恩",
        "category": "State",
        "intensity": 0.7,
        "polarity": "positive",
        "arousal": "low",
        "description": "对他人善意的深刻感谢",
        "visual_signs": "双手交握, 微微鞠躬, 眼神真诚",
        "voice_signs": "音调柔, 经常说\"谢谢\"",
        "facial_au": "AU1+AU2+AU6+AU12 (感恩组合)",
        "inner_monologue": "我真的很幸运",
        "color_palette": "暖金, 米白, 淡蓝",
        "music_tempo": "50 BPM, 大提琴 + 钢琴",
        "director_examples": "是枝裕和《比海更深》 - 母子重逢",
    },
    "wonder": {
        "name": "Wonder 惊奇",
        "category": "State",
        "intensity": 0.8,
        "polarity": "positive",
        "arousal": "medium",
        "description": "对世界/生命奥秘的惊叹",
        "visual_signs": "凝视, 身体前倾, 表情混合惊讶+喜悦",
        "voice_signs": "语速慢, 经常\"哇\"",
        "facial_au": "AU1+AU2+AU5B+AU12 (惊奇组合)",
        "inner_monologue": "这真神奇",
        "color_palette": "金, 紫, 极光色",
        "music_tempo": "70 BPM, 渐强",
        "director_examples": "宫崎骏《天空之城》 - 看到飞行石",
    },
    # ===== 12 种复杂情感 (Phase 17.3 补充) =====
    # 东方特有情感 (中式美学)
    "yuan": {
        "name": "Yuan 怨 (中式幽怨)",
        "category": "Complex Eastern",
        "intensity": 0.75,
        "polarity": "negative",
        "arousal": "low",
        "description": "中式特有的幽怨, 委屈但不说, 久久不散",
        "visual_signs": "眉下垂, 嘴角下撇但克制, 眼神幽怨, 经常独自一人",
        "voice_signs": "音调低, 语速慢, 经常停顿, 经常说\"没什么\"",
        "facial_au": "AU1+AU4+AU15+AU17 (幽怨组合)",
        "inner_monologue": "我又能说什么呢",
        "color_palette": "暗蓝灰, 黛色, 烟雨色",
        "music_tempo": "40 BPM, 古琴/二胡",
        "director_examples": "王家卫《花样年华》 - 苏丽珍的旗袍背影",
    },
    "chouchang": {
        "name": "Chouchang 惆怅 (中式惆怅)",
        "category": "Complex Eastern",
        "intensity": 0.6,
        "polarity": "mixed",
        "arousal": "low",
        "description": "对失去/不可追的淡淡惆怅",
        "visual_signs": "远眺, 轻叹, 偶尔摇头",
        "voice_signs": "经常长叹, 语速极慢",
        "facial_au": "AU1+AU4+AU15+AU43 (惆怅组合)",
        "inner_monologue": "时光不等人",
        "color_palette": "暮色, 远山蓝, 暖灰",
        "music_tempo": "30 BPM, 笛子",
        "director_examples": "侯孝贤《悲情城市》 - 远望山景",
    },
    "ji": {
        "name": "Ji 寂 (中式寂静)",
        "category": "Complex Eastern",
        "intensity": 0.5,
        "polarity": "mixed",
        "arousal": "low",
        "description": "不只是孤独, 是宇宙性的寂静, 与天地合一",
        "visual_signs": "完全静坐, 呼吸极慢, 眼神深远",
        "voice_signs": "完全失语, 偶发极轻叹息",
        "facial_au": "AU1+AU2+AU43+AU47 (寂的组合)",
        "inner_monologue": "无",
        "color_palette": "水墨, 留白, 单色",
        "music_tempo": "10 BPM, 只有风声",
        "director_examples": "侯孝贤《刺客聂隐娘》 - 山中静坐",
    },
    "chou": {
        "name": "Chou 愁 (中式愁绪)",
        "category": "Complex Eastern",
        "intensity": 0.7,
        "polarity": "negative",
        "arousal": "low",
        "description": "对家国/时事的深沉忧愁",
        "visual_signs": "眉头紧锁, 远眺, 经常抚摸旧物",
        "voice_signs": "音调低沉, 经常长叹",
        "facial_au": "AU1+AU4+AU15 (愁绪组合)",
        "inner_monologue": "国将何如",
        "color_palette": "铁灰, 暮色, 衰草色",
        "music_tempo": "20 BPM, 古琴",
        "director_examples": "侯孝贤《悲情城市》 - 林家客厅",
    },
    # 复杂矛盾情感
    "bittersweet_pain": {
        "name": "Bittersweet Pain 甜蜜的痛苦",
        "category": "Complex Paradox",
        "intensity": 0.8,
        "polarity": "mixed",
        "arousal": "low",
        "description": "Joy + Sadness 矛盾融合, 快乐与痛苦并存",
        "visual_signs": "微笑时眼角有泪, 笑声变轻, 身体微微颤抖",
        "voice_signs": "句子结尾变轻, 经常欲言又止",
        "facial_au": "AU6+AU12+AU1+AU4+AU15+AU43 (矛盾组合)",
        "inner_monologue": "如果这一刻能停止就好了",
        "color_palette": "金 + 蓝, 暖光 + 冷阴影",
        "music_tempo": "50 BPM, 大调小调交替",
        "director_examples": "是枝裕和《步履不停》 - 母亲去世后父亲做天妇罗",
        "fusion": "Joy + Sadness",
    },
    "warm_regret": {
        "name": "Warm Regret 温暖的遗憾",
        "category": "Complex Paradox",
        "intensity": 0.7,
        "polarity": "mixed",
        "arousal": "low",
        "description": "Trust + Sadness 矛盾, 遗憾中带温暖",
        "visual_signs": "抚摸旧物, 微笑回忆, 偶尔眼角湿",
        "voice_signs": "经常说\"那时候...\"",
        "facial_au": "AU6+AU12+AU1+AU4+AU15+AU43 (温暖遗憾)",
        "inner_monologue": "如果当时能多陪你一会儿",
        "color_palette": "暖金, 复古蓝, 旧照片色",
        "music_tempo": "60 BPM, 复古钢琴",
        "director_examples": "王家卫《一代宗师》 - 叶问看宫二照片",
        "fusion": "Trust + Sadness",
    },
    "hopeless_hope": {
        "name": "Hopeless Hope 绝望的希望",
        "category": "Complex Paradox",
        "intensity": 0.85,
        "polarity": "mixed",
        "arousal": "low",
        "description": "Sadness + Anticipation 矛盾, 绝望中还有期待",
        "visual_signs": "眼神混合绝望和希望, 嘴角在笑和不笑之间",
        "voice_signs": "句子破碎, 经常说\"也许...\"",
        "facial_au": "AU1+AU4+AU15+AU17+AU5 (绝望希望)",
        "inner_monologue": "也许...不会的",
        "color_palette": "暗金, 蓝灰, 黎明前",
        "music_tempo": "60 BPM, 渐强渐弱",
        "director_examples": "诺兰《星际穿越》 - 库珀看墨菲",
        "fusion": "Sadness + Anticipation",
    },
    "love_hate": {
        "name": "Love-Hate 爱到深处的恨",
        "category": "Complex Paradox",
        "intensity": 0.95,
        "polarity": "mixed",
        "arousal": "high",
        "description": "Love + Hate 极矛盾, 极致爱恨交织",
        "visual_signs": "看对方时眼睛混合柔情和凶光, 手握紧又松开",
        "voice_signs": "温柔和咆哮交替, 经常突然沉默",
        "facial_au": "AU6+AU12+AU4+AU17+AU26 (爱恨交织)",
        "inner_monologue": "我恨你, 但我离不开你",
        "color_palette": "血红 + 玫红, 黑金",
        "music_tempo": "50-100 BPM 剧烈变化, 不和谐音",
        "director_examples": "PTA《魅影缝匠》 - Reynolds 看 Alma",
        "fusion": "Love + Hate",
    },
    # 哲学性情感
    "lucid_despair": {
        "name": "Lucid Despair 清醒的绝望",
        "category": "Complex Philosophical",
        "intensity": 0.95,
        "polarity": "negative",
        "arousal": "low",
        "description": "完全清醒地意识到绝望, 没有自我欺骗",
        "visual_signs": "眼神完全清醒但失焦, 嘴角极轻微苦笑",
        "voice_signs": "音调完全平, 没有起伏, 经常说\"我知道\"",
        "facial_au": "AU1+AU4+AU15+AU17+AU53 (清醒绝望)",
        "inner_monologue": "我看得很清楚, 这就是结局",
        "color_palette": "无色, 苍白, 灰",
        "music_tempo": "20 BPM, 单音大提琴",
        "director_examples": "塔可夫斯基《牺牲》 - 主人公献祭前",
    },
    "awed_fear": {
        "name": "Awed Fear 敬畏的恐惧",
        "category": "Complex Philosophical",
        "intensity": 0.85,
        "polarity": "mixed",
        "arousal": "high",
        "description": "Fear + Awe 矛盾, 面对伟大的恐惧和敬畏并存",
        "visual_signs": "后退半步但眼睛无法离开, 身体颤抖但不跑",
        "voice_signs": "语速极慢, 经常沉默, 偶发极轻的声音",
        "facial_au": "AU1+AU2+AU5+AU20+AU26+AU27 (敬畏恐惧)",
        "inner_monologue": "这太伟大了, 让我害怕",
        "color_palette": "极光, 神光, 深紫, 银",
        "music_tempo": "全乐队 + 和声 + 低音",
        "director_examples": "维伦纽瓦《降临》 - Louise 第一次看到外星人",
        "fusion": "Fear + Awe",
    },
    "tender_contradiction": {
        "name": "Tender Contradiction 矛盾的温柔",
        "category": "Complex Paradox",
        "intensity": 0.7,
        "polarity": "positive",
        "arousal": "low",
        "description": "Joy + Sadness + Trust 三元, 温柔中带忧伤",
        "visual_signs": "轻轻抚摸, 眼神温柔但含泪",
        "voice_signs": "音调极柔, 句子经常未完成",
        "facial_au": "AU1+AU2+AU6+AU12+AU15 (矛盾温柔)",
        "inner_monologue": "我多希望这一刻能永远",
        "color_palette": "暖白, 浅金, 暮色",
        "music_tempo": "50 BPM, 钢琴 + 弦乐",
        "director_examples": "是枝裕和《步履不停》 - 母亲最后的散步",
        "fusion": "Joy + Sadness + Trust",
    },
    "perfect_regret": {
        "name": "Perfect Regret 完美的遗憾",
        "category": "Complex Philosophical",
        "intensity": 0.9,
        "polarity": "negative",
        "arousal": "low",
        "description": "Joy + Sadness 极致融合, 已经做到最好但还是失去",
        "visual_signs": "已经完成, 但眼神中无光",
        "voice_signs": "完全平静, 经常用过去时",
        "facial_au": "AU1+AU2+AU4+AU12+AU15+AU17+AU53 (完美遗憾)",
        "inner_monologue": "我已经做了所有能做的",
        "color_palette": "极淡蓝, 苍白金, 暮雪",
        "music_tempo": "30 BPM, 大提琴 + 钢琴",
        "director_examples": "约阿希姆·提尔《情感价值》 - 父亲的独白",
        "fusion": "Joy + Sadness",
    },
}


# ============================================================
# 2. EMOTION_FUSION_7 - 7 大情感融合公式
# ============================================================
EMOTION_FUSION_7 = {
    "F1_单情感主导": {
        "name": "Single Emotion Dominant",
        "description": "整场戏只有一种情感, 这是最常见的 70% 场景",
        "weight_distribution": "100% single",
        "scenarios": "大多数普通场景, 单一明确情绪",
        "director_examples": "王家卫《重庆森林》- 何志武独白 (loneliness 100%)",
    },
    "F2_双情感主次融合": {
        "name": "Dual Emotion Primary-Secondary",
        "description": "两种情感, 一种主导 (70%) + 一种次要 (30%)",
        "weight_distribution": "70% primary + 30% secondary",
        "scenarios": "角色有表层和内层, 表面平静内心激动, 这是 25% 场景",
        "director_examples": "《情感价值》- 父亲表面平静 (acceptance 70%) 内里悔恨 (remorse 30%)",
    },
    "F3_双情感对等融合": {
        "name": "Dual Emotion Equal",
        "description": "两种情感对等 (50/50), 矛盾并存",
        "weight_distribution": "50% + 50%",
        "scenarios": "角色内心矛盾, 这是 20% 场景",
        "director_examples": "《花样年华》- 压抑欲望 (tenderness 50% + repression 50%)",
    },
    "F4_三情感递进融合": {
        "name": "Triple Emotion Progressive",
        "description": "三种情感, 随场景递进",
        "weight_distribution": "20% + 30% + 50% (随时间变化)",
        "scenarios": "角色经历情感变化, 这是 10% 场景",
        "director_examples": "《步履不停》- 兴趣→关切→悔恨",
    },
    "F5_矛盾情感爆炸": {
        "name": "Contradictory Explosion",
        "description": "两种极端矛盾情感同时达到峰值",
        "weight_distribution": "50% + 50% (intensity 1.0 + 1.0)",
        "scenarios": "角色在极端压力下情感崩溃, 5% 场景",
        "director_examples": "奉俊昊《寄生虫》- 朴社长在地下室的绝望 (disgust 100% + fear 100% 矛盾)",
    },
    "F6_复合情绪三角": {
        "name": "Compound Emotion Triangle",
        "description": "三种情感形成稳定复合体",
        "weight_distribution": "33% + 33% + 33%",
        "scenarios": "复杂心理状态, 2% 场景",
        "director_examples": "PTA《魅影缝匠》- Reynolds 复杂情感 (love 33% + obsession 33% + control 33%)",
    },
    "F7_情感转化": {
        "name": "Emotional Transformation",
        "description": "情感在场景内发生根本性转化",
        "weight_distribution": "100% emotion_A → 100% emotion_B",
        "scenarios": "情感转折点, 1% 场景, 但最重要",
        "director_examples": "《泰坦尼克号》- Jack 死时 Rose 从 love 100% → grief 100%",
    },
}


# ============================================================
# 3. SOUL_DIMENSIONS_10 - 10 大灵魂维度
# ============================================================
SOUL_DIMENSIONS_10 = {
    "D1_创造力": {
        "name": "Creativity 创造力",
        "description": "突破常规的联想能力, 把不相关的事物组合成新的意义",
        "low": "完全照搬已有模式, 产出'安全'但平庸的作品",
        "high": "能在寻常中看到不寻常, 产出'反预期'但'本该如此'的作品",
        "expression": "新隐喻 / 跨类比 / 反转预期 / 解构经典",
        "director_examples": "PTA 用石油和牛奶做权力隐喻 / 奉俊昊用楼梯做阶层隐喻",
    },
    "D2_想象力": {
        "name": "Imagination 想象力",
        "description": "在头脑中构建尚未存在的事物的能力",
        "low": "只能处理已经存在的素材",
        "high": "能在头脑中构建完整的虚构世界 (角色/空间/历史/物理规则)",
        "expression": "世界观构建 / 角色前史 / 平行宇宙 / 时间旅行 / 梦境",
        "director_examples": "维伦纽瓦构建 Arrakis 沙丘世界 / 林奇构建 Twin Peaks",
    },
    "D3_艺术表达力": {
        "name": "Artistic Expression 艺术表达力",
        "description": "用具体的艺术形式承载抽象情感的能力",
        "low": "用形容词表达 (美/丑/好/坏)",
        "high": "用具体的视觉/声音/动作表达抽象情感 (用一根头发表达爱情)",
        "expression": "物件代替心理 / 微动作代替情绪 / 视觉象征 / 声音隐喻",
        "director_examples": "王家卫用凤梨罐头代替时间 / 库斯杜力卡用沉默代替悲伤",
    },
    "D4_镜头语言技巧": {
        "name": "Camera Language Skill 镜头语言技巧",
        "description": "用摄影机运动/焦段/构图控制观众的眼睛和情感",
        "low": "所有镜头都中景 + 平稳",
        "high": "每个镜头都有独特的镜头语言服务于叙事和情感",
        "expression": "焦段变化 / 运动设计 / 构图引导 / 视角选择 / 镜头长度",
        "director_examples": "Roger Deakins 用景深构图 / Lubezki 用长镜头 + 自然光",
    },
    "D5_画面氛围掌控": {
        "name": "Visual Atmosphere Control 画面氛围掌控",
        "description": "用光线/色彩/质感营造情绪的能力",
        "low": "所有场景光线都一样",
        "high": "每个场景都有独特的光影氛围服务于情感",
        "expression": "60:30:10 色彩 / 9 维光影 / 质感选择 / 天气影响",
        "director_examples": "泰伦斯·马力克《天堂之日》 - 黄金时刻光 / 格雷厄姆《灯塔》 - 黑白高压",
    },
    "D6_精神状态": {
        "name": "Mental State 精神状态",
        "description": "导演创作时当下的精神状态, 影响所有决策",
        "states": ["清醒 (lucid)", "梦幻 (dreamy)", "焦虑 (anxious)", "平静 (serene)", "狂热 (manic)", "疲惫 (exhausted)", "激进 (radical)", "保守 (conservative)"],
        "impact": "不同精神状态导致完全不同的镜头选择",
        "director_examples": "PTA 《不羁夜》 - 70 年代迷幻精神状态 / 塔可夫斯基《镜子》 - 梦游精神状态",
    },
    "D7_灵感时刻": {
        "name": "Inspiration Moment 灵感时刻",
        "description": "在创作中突然涌现的『突然知道怎么拍』的瞬间",
        "manifestations": [
            "突然改变镜头角度",
            "突然改变色调",
            "突然加一个不相关的细节",
            "突然改变剪辑节奏",
            "突然改变演员调度",
        ],
        "frequency": "伟大导演每部片有 5-20 个真正的灵感时刻",
        "director_examples": "诺兰《盗梦空间》火车冲入街道 / 奉俊昊《寄生虫》暴雨倒流楼梯",
    },
    "D8_叛逆度": {
        "name": "Rebelliousness 叛逆度",
        "description": "打破规则的勇气和意愿",
        "low": "严格遵守行业规则",
        "high": "在关键时刻敢于打破一切规则",
        "manifestations": [
            "拒绝传统三幕剧结构",
            "拒绝给观众明确答案",
            "拒绝商业大团圆",
            "拒绝美化主角",
            "拒绝 happy ending",
        ],
        "director_examples": "林奇《穆赫兰道》 - 完全无解释 / 安哲罗普洛斯《永恒与一日》 - 完全非线性",
    },
    "D9_自我怀疑": {
        "name": "Self-Doubt 自我怀疑",
        "description": "对自己作品的不安, 推动反复修改",
        "low": "拍完就发布",
        "high": "反复重拍, 反复质疑自己的选择, 直到最后一刻",
        "manifestations": [
            "反复重写剧本",
            "反复重拍同一场景",
            "反复重剪",
            "发布前仍在修改",
        ],
        "director_examples": "泰伦斯·马力克 反复重剪 / 库布里克 反复重拍",
    },
    "D10_突破勇气": {
        "name": "Breakthrough Courage 突破勇气",
        "description": "在压力下做出真正创新的选择",
        "low": "选择安全的方案",
        "high": "选择真正创新但风险巨大的方案",
        "manifestations": [
            "选择非专业演员",
            "选择实验性叙事结构",
            "选择困难的主题",
            "选择不商业的结尾",
        ],
        "director_examples": "诺兰用 IMAX 拍《黑暗骑士》/ 奉俊昊《寄生虫》全非线性",
    },
}


# ============================================================
# 3.5 EMOTION_ALIASES - 情感别名映射 (兼容用户直觉输入)
# ============================================================
# 用户/节点的合理输入可能是基础情感 (fear) 或裸子词 (apprehension) 或复合 (loneliness)
# 我们把所有合理别名映射到 EMOTION_MATRIX_60 中的具体 key
# 中等强度子词作为默认 (apprehension/sorrow/pleasure 等)
EMOTION_ALIASES = {
    # ===== Plutchik 8 基础情感 → 中等强度子词 =====
    "fear":         "fear_apprehension",
    "joy":          "joy_pleasure",
    "trust":        "trust_admiration",
    "surprise":     "surprise_astonishment",
    "sadness":      "sadness_sorrow",
    "disgust":      "disgust_revulsion",
    "anger":        "anger_frustration",
    "anticipation": "anticipation_expectation",
    # ===== 24 子词裸名 → 完整 key (中等强度优先) =====
    "timidity":     "fear_timidity",
    "apprehension": "fear_apprehension",
    "terror":       "fear_terror",
    "serenity":     "joy_serenity",
    "pleasure":     "joy_pleasure",
    "ecstasy":      "joy_ecstasy",
    "acceptance":   "trust_acceptance",
    "admiration":   "trust_admiration",
    "surrender":    "trust_surrender",
    "uncertainty":  "surprise_uncertainty",
    "astonishment": "surprise_astonishment",
    "amazement":    "surprise_amazement",
    "gloominess":   "sadness_gloominess",
    "sorrow":       "sadness_sorrow",
    "grief":        "sadness_grief",
    "dislike":      "disgust_dislike",
    "revulsion":    "disgust_revulsion",
    "loathing":     "disgust_loathing",
    "annoyance":    "anger_annoyance",
    "frustration":  "anger_frustration",
    "fury":         "anger_fury",
    "interest_emotion": "anticipation_interest",
    "interest_emo": "anticipation_interest",
    "expectation":  "anticipation_expectation",
    "vigilance":    "anticipation_vigilance",
    # ===== Izard 6 扩展 - 已直接是 key, 但兼容 snake/camel =====
    "guilt":        "guilt",
    "shame":        "shame",
    "pride":        "pride",
    "contempt":     "contempt",
    "shyness":      "shyness",
    "interest":     "interest",
    # ===== 常见中文情感到英文 key =====
    "孤独":         "loneliness",
    "寂寞":         "loneliness",
    "思念":         "longing",
    "渴望":         "longing",
    "焦虑":         "tension",
    "紧张":         "tension",
    "温柔":         "tenderness",
    "柔情":         "tenderness",
    "怀旧":         "nostalgia",
    "惆怅":         "chouchang",
    "寂":           "ji",
    "愁":           "chou",
    "怨":           "yuan",
    "恐惧":         "fear_apprehension",
    "害怕":         "fear_timidity",
    "喜悦":         "joy_pleasure",
    "快乐":         "joy_pleasure",
    "高兴":         "joy_pleasure",
    "悲伤":         "sadness_sorrow",
    "痛苦":         "sadness_grief",
    "愤怒":         "anger_frustration",
    "憎恨":         "hate",
    "爱":           "love",
    "信任":         "trust_admiration",
    "希望":         "hope",
    "绝望":         "despair",
    "感激":         "gratitude",
    "惊奇":         "surprise_astonishment",
    "震惊":         "surprise_amazement",
    "厌恶":         "disgust_revulsion",
    "反感":         "disgust_dislike",
    "期待":         "anticipation_expectation",
    "警觉":         "anticipation_vigilance",
    "内疚":         "guilt",
    "羞耻":         "shame",
    "骄傲":         "pride",
    "轻蔑":         "contempt",
    "害羞":         "shyness",
    "兴味":         "interest",
    "释然":         "relief",
    "宽慰":         "relief",
    "温暖遗憾":     "warm_regret",
    "清醒绝望":     "lucid_despair",
    "敬畏恐惧":     "awed_fear",
    "矛盾温柔":     "tender_contradiction",
    "完美遗憾":     "perfect_regret",
    "甜蜜痛苦":     "bittersweet_pain",
    "绝望希望":     "hopeless_hope",
    "爱恨交织":     "love_hate",
}


def _resolve_emotion_aliases(emotion_keys: list) -> list:
    """解析情感别名 - 基础情感/裸子词/中文 → EMOTION_MATRIX_60 key"""
    resolved = []
    for k in emotion_keys:
        if k in EMOTION_MATRIX_60:
            resolved.append(k)
        elif k in EMOTION_ALIASES:
            target = EMOTION_ALIASES[k]
            # 防止别名指向不存在的 key
            if target in EMOTION_MATRIX_60:
                resolved.append(target)
            else:
                # 别名指向无效 key, 跳过
                pass
        # 都不在 - 跳过 (不要让单个错误拖垮整个融合)
    return resolved


# ============================================================
# 4. SOUL_FUSION_ENGINE - 情感融合引擎
# ============================================================
def fuse_emotions(emotion_keys: list, weights: list = None, mode: str = "auto"):
    """
    情感融合引擎 - 核心算法
    input: 情感 key 列表 + 权重 (可选) + 模式 (F1-F7)
    output: 融合后的完整情感档案

    Phase 17.1 增强: 自动解析情感别名 (fear→fear_apprehension, 恐惧→fear_apprehension, etc.)
    """
    if not emotion_keys:
        return None
    if not _HAS_EMOTION_DATA and False:
        return None

    # Phase 17.1: 别名解析 - 让用户/节点能用直觉输入 (fear, 恐惧, etc.)
    emotion_keys = _resolve_emotion_aliases(emotion_keys)

    # 验证情感存在
    valid_emotions = [k for k in emotion_keys if k in EMOTION_MATRIX_60]
    if not valid_emotions:
        return None

    # 自动推断模式
    n = len(valid_emotions)
    if mode == "auto":
        if n == 1:
            mode = "F1_单情感主导"
        elif n == 2 and weights is None:
            mode = "F3_双情感对等融合"  # 50/50 默认
        elif n == 2 and weights is not None:
            mode = "F2_双情感主次融合"
        elif n == 3:
            mode = "F4_三情感递进融合"
        elif n >= 4:
            mode = "F6_复合情绪三角"
        else:
            mode = "F1_单情感主导"

    # 默认权重
    if weights is None:
        if mode == "F1_单情感主导":
            weights = [1.0]
        elif mode == "F2_双情感主次融合":
            weights = [0.7, 0.3]
        elif mode == "F3_双情感对等融合":
            weights = [0.5, 0.5]
        elif mode == "F4_三情感递进融合":
            weights = [0.2, 0.3, 0.5]
        elif mode == "F5_矛盾情感爆炸":
            weights = [0.5, 0.5]
        elif mode == "F6_复合情绪三角":
            weights = [1/3] * min(3, n)
            valid_emotions = valid_emotions[:3]
        elif mode == "F7_情感转化":
            weights = [1.0, 1.0]
    # 归一化权重
    total = sum(weights)
    if total > 0:
        weights = [w / total for w in weights]

    # 融合每个字段
    fused = {
        "fusion_mode": mode,
        "emotions": valid_emotions,
        "weights": weights,
        "name": "",
        "category": "Fused",
        "intensity": 0.0,
        "polarity": "neutral",
        "arousal": "medium",
        "description": "",
        "visual_signs": "",
        "voice_signs": "",
        "facial_au": "",
        "inner_monologue": "",
        "color_palette": "",
        "music_tempo": "",
        "director_examples": "",
    }

    for i, ekey in enumerate(valid_emotions):
        emo = EMOTION_MATRIX_60[ekey]
        w = weights[i] if i < len(weights) else 1.0 / len(valid_emotions)

        if not fused["name"]:
            fused["name"] = emo["name"]
        else:
            fused["name"] += f" + {emo['name']}"

        # 加权平均数值
        fused["intensity"] += emo["intensity"] * w

        # 极性: 加权投票
        p = emo["polarity"]
        if p not in ["positive", "negative", "neutral", "mixed"]:
            p = "neutral"
        # 简单累积 (后续可以更复杂)

        # 文本字段: 加权拼接
        if emo.get("description"):
            fused["description"] += f"[{w*100:.0f}%] {emo['description']} "
        if emo.get("visual_signs"):
            fused["visual_signs"] += f"[{w*100:.0f}%] {emo['visual_signs']} "
        if emo.get("voice_signs"):
            fused["voice_signs"] += f"[{w*100:.0f}%] {emo['voice_signs']} "
        if emo.get("facial_au"):
            fused["facial_au"] += f"[{w*100:.0f}%] {emo['facial_au']} "
        if emo.get("inner_monologue"):
            fused["inner_monologue"] += f"[{w*100:.0f}%] {emo['inner_monologue']} "
        if emo.get("color_palette"):
            fused["color_palette"] += f"[{w*100:.0f}%] {emo['color_palette']} "
        if emo.get("music_tempo"):
            fused["music_tempo"] += f"[{w*100:.0f}%] {emo['music_tempo']} "
        if emo.get("director_examples"):
            fused["director_examples"] += f"[{w*100:.0f}%] {emo['director_examples']} "

    # 极性综合判断
    pos_w = sum(w for k, w in zip(valid_emotions, weights) if EMOTION_MATRIX_60[k]["polarity"] == "positive")
    neg_w = sum(w for k, w in zip(valid_emotions, weights) if EMOTION_MATRIX_60[k]["polarity"] == "negative")
    mixed_w = sum(w for k, w in zip(valid_emotions, weights) if EMOTION_MATRIX_60[k]["polarity"] in ["mixed", "neutral"])
    if pos_w > neg_w + mixed_w:
        fused["polarity"] = "positive"
    elif neg_w > pos_w + mixed_w:
        fused["polarity"] = "negative"
    elif mixed_w > 0.3:
        fused["polarity"] = "mixed (矛盾情感)"
    else:
        fused["polarity"] = "neutral"

    # arousal 综合
    high_w = sum(w for k, w in zip(valid_emotions, weights) if EMOTION_MATRIX_60[k]["arousal"] == "high")
    low_w = sum(w for k, w in zip(valid_emotions, weights) if EMOTION_MATRIX_60[k]["arousal"] == "low")
    if high_w > low_w:
        fused["arousal"] = "high"
    elif low_w > high_w:
        fused["arousal"] = "low"
    else:
        fused["arousal"] = "medium"

    return fused


# ============================================================
# 5. SOUL_OUTPUT - 灵魂注入格式 (供其他节点使用)
# ============================================================
def build_soul_injection(
    story_emotion_keys: list = None,
    story_weights: list = None,
    fusion_mode: str = "auto",
    director: str = "王家卫",
    scene_context: str = "",
):
    """
    构建导演灵魂注入 - 供所有其他节点使用
    """
    # 1. 情感融合
    fused_emotion = fuse_emotions(story_emotion_keys or ["loneliness"], story_weights, fusion_mode)

    # 2. 灵魂状态 (基于故事情感 + 导演风格)
    soul_state = {
        "current_inspiration_index": round(random.uniform(0.6, 0.95), 2),
        "current_fatigue_index": round(random.uniform(0.2, 0.6), 2),
        "current_doubt_index": round(random.uniform(0.4, 0.8), 2),
        "current_rebelliousness_index": round(random.uniform(0.5, 0.9), 2),
        "current_mental_state": "lucid-dreamy",  # 清醒-梦幻
    }

    # 3. 灵魂维度 (基于导演)
    soul_dimensions = {
        "creativity": 0.92,
        "imagination": 0.90,
        "artistic_expression": 0.95,
        "camera_skill": 0.88,
        "atmosphere_control": 0.93,
        "mental_state": "lucid-dreamy",
        "inspiration": 0.85,
        "rebelliousness": 0.80,
        "self_doubt": 0.70,
        "breakthrough_courage": 0.88,
    }

    # 4. 灵魂输出
    injection = f"""════════════════════════════════════════
【导演灵魂注入 (Director Soul Injection)】
════════════════════════════════════════

【1. 情感核心】
主导情感: {fused_emotion['name']}
融合模式: {fused_emotion['fusion_mode']}
融合情感: {' + '.join(fused_emotion['emotions'])}
权重: {[f'{w:.2f}' for w in fused_emotion['weights']]}
强度: {fused_emotion['intensity']:.2f}
极性: {fused_emotion['polarity']}
唤醒度: {fused_emotion['arousal']}

【2. 情感表达】
- 视觉表现: {fused_emotion['visual_signs'][:500]}
- 声音表现: {fused_emotion['voice_signs'][:300]}
- 面部肌肉: {fused_emotion['facial_au'][:300]}
- 内心独白: {fused_emotion['inner_monologue'][:300]}

【3. 艺术氛围】
- 色彩: {fused_emotion['color_palette'][:300]}
- 音乐: {fused_emotion['music_tempo'][:300]}

【4. 灵魂状态 (Soul State)】
灵感指数: {soul_state['current_inspiration_index']}
疲劳指数: {soul_state['current_fatigue_index']}
怀疑指数: {soul_state['current_doubt_index']}
叛逆指数: {soul_state['current_rebelliousness_index']}
精神状态: {soul_state['current_mental_state']}

【5. 灵魂维度 (10 Dimensions)】
创造力: {soul_dimensions['creativity']}
想象力: {soul_dimensions['imagination']}
艺术表达: {soul_dimensions['artistic_expression']}
镜头技巧: {soul_dimensions['camera_skill']}
氛围掌控: {soul_dimensions['atmosphere_control']}
精神状态: {soul_dimensions['mental_state']}
灵感时刻: {soul_dimensions['inspiration']}
叛逆度: {soul_dimensions['rebelliousness']}
自我怀疑: {soul_dimensions['self_doubt']}
突破勇气: {soul_dimensions['breakthrough_courage']}

【6. 导演视角】
{director} 的灵魂签名:
- 不写情绪, 写可观察行为 (PTA)
- 让沉默比台词更有力 (库斯杜力卡)
- 用空间叙事 (诺兰)
- 用物件代替心理 (王家卫)
- 用微动作总和等于情感 (L4 表演层)
- 3 留白 + 3 运镜法则 (AIGC 文档)

════════════════════════════════════════
导演: {director}
场景: {scene_context[:100]}
注入模式: SOUL_INJECTION_V1
════════════════════════════════════════
"""
    return injection


# ============================================================
# 6. SOUL_STATE - 当前灵魂状态 (动态变化)
# ============================================================
def compute_soul_state(story_intensity: float = 0.5, scene_progress: float = 0.0):
    """
    计算当前灵魂状态 (基于故事强度和场景进度)
    scene_progress: 0.0 (开场) → 1.0 (结尾)
    """
    # 灵感指数: 开头低, 中间高, 结尾中等
    inspiration = 0.3 + 0.7 * math.exp(-((scene_progress - 0.4) ** 2) / 0.1)

    # 疲劳指数: 随时间累积
    fatigue = min(0.95, 0.1 + scene_progress * 0.85)

    # 怀疑指数: 故事强度越大, 怀疑越低
    doubt = max(0.2, 0.8 - story_intensity * 0.6)

    # 叛逆指数: 故事强度越大, 越可能打破规则
    rebelliousness = min(0.95, 0.4 + story_intensity * 0.5)

    return {
        "inspiration": round(inspiration, 2),
        "fatigue": round(fatigue, 2),
        "doubt": round(doubt, 2),
        "rebelliousness": round(rebelliousness, 2),
        "mental_state": "lucid" if doubt < 0.5 else "anxious-dreamy",
    }


# ============================================================
# 7. SCENE_WEIGHT_INFERENCE - 场景自动权重推断
# ============================================================
SCENE_TYPE_PATTERNS = {
    "key_climax": {
        "patterns": ["高潮", "climax", "决战", "对质", "真相", "爆发", "死亡", "分离"],
        "emotion_count": 2,
        "weight_dist": "50/50",
        "fusion_mode": "F5_矛盾情感爆炸",
        "intensity_boost": 1.3,
        "rationale": "关键场景需要矛盾情感的极致张力",
    },
    "transitional": {
        "patterns": ["过渡", "走路", "等待", "日常", "工作", "吃饭"],
        "emotion_count": 1,
        "weight_dist": "100%",
        "fusion_mode": "F1_单情感主导",
        "intensity_boost": 0.8,
        "rationale": "过渡场景用单情感保持节奏",
    },
    "inner_monologue": {
        "patterns": ["独白", "独处", "回忆", "想象", "内心", "梦境", "monologue", "dream"],
        "emotion_count": 2,
        "weight_dist": "70/30",
        "fusion_mode": "F2_双情感主次融合",
        "intensity_boost": 0.9,
        "rationale": "内心场景是表层 + 内层的双情感",
    },
    "ensemble": {
        "patterns": ["群戏", "聚餐", "会议", "派对", "战争", "ensemble", "group"],
        "emotion_count": 3,
        "weight_dist": "33/33/33",
        "fusion_mode": "F6_复合情绪三角",
        "intensity_boost": 1.1,
        "rationale": "群戏需要多个角色情感的复合",
    },
    "transition_moment": {
        "patterns": ["转折", "转变", "觉醒", "领悟", "决定", "turning", "moment"],
        "emotion_count": 2,
        "weight_dist": "100%→100%",
        "fusion_mode": "F7_情感转化",
        "intensity_boost": 1.5,
        "rationale": "转折点是情感转化的关键时刻",
    },
}


def infer_scene_weights(scene_description: str, scene_progress: float = 0.0, story_intensity: float = 0.5):
    """
    场景自动权重推断 - 根据场景描述自动选择融合公式和情感数量
    """
    if not scene_description:
        return {
            "scene_type": "transitional",
            "emotion_count": 1,
            "fusion_mode": "F1_单情感主导",
            "default_emotion": "loneliness",
            "default_weight": 1.0,
            "intensity_boost": 0.8,
        }

    desc_lower = scene_description.lower()

    # 匹配场景类型
    matched_type = "transitional"
    matched_score = 0
    for scene_type, config in SCENE_TYPE_PATTERNS.items():
        for pattern in config["patterns"]:
            if pattern.lower() in desc_lower:
                if len(pattern) > matched_score:
                    matched_type = scene_type
                    matched_score = len(pattern)
                break

    config = SCENE_TYPE_PATTERNS[matched_type]

    # 根据场景进度调整
    progress_boost = 1.0
    if scene_progress > 0.7:
        progress_boost = 1.2  # 结尾加强
    elif scene_progress < 0.2:
        progress_boost = 0.8  # 开场稍弱

    # 根据故事强度调整
    intensity_boost = config["intensity_boost"] * story_intensity * progress_boost

    # 根据融合模式决定默认权重
    if config["weight_dist"] == "100%":
        default_weight = 1.0
        default_emotion = "loneliness"
    elif config["weight_dist"] == "70/30":
        default_weight = 0.7
        default_emotion = "loneliness"
    elif config["weight_dist"] == "50/50":
        default_weight = 0.5
        default_emotion = "tension"
    elif config["weight_dist"] == "33/33/33":
        default_weight = 0.33
        default_emotion = "tension"
    elif config["weight_dist"] == "100%→100%":
        default_weight = 1.0
        default_emotion = "despair"
    else:
        default_weight = 1.0
        default_emotion = "loneliness"

    return {
        "scene_type": matched_type,
        "emotion_count": config["emotion_count"],
        "fusion_mode": config["fusion_mode"],
        "default_emotion": default_emotion,
        "default_weight": default_weight,
        "intensity_boost": round(intensity_boost, 2),
        "rationale": config["rationale"],
    }


# ============================================================
# 8. INSPIRATION_MOMENT - 灵感时刻注入器
# ============================================================
INSPIRATION_MOMENTS = {
    "camera": [
        "突然切换焦段: 35mm 切 85mm, 压缩空间",
        "突然切换视角: 从正面切到俯视, 强调渺小",
        "突然切到主观镜头: 视角从角色切换到角色",
        "突然推近到极特写: 整个画面被眼睛占满",
    ],
    "color": [
        "突然切换色温: 暖色 5600K 切冷色 3200K",
        "突然去饱和: 整个画面瞬间变成黑白",
        "突然加红: 全部色调偏向血红",
        "突然加青: 全部色调偏向青绿, 像监视器",
    ],
    "composition": [
        "突然切对称构图: 之前松散现在绝对居中",
        "突然打破三分法: 主体偏离到画面边缘",
        "突然框中框: 用窗户/门/镜子制造框架",
        "突然消失构图: 留白占满 80%",
    ],
    "rhythm": [
        "突然静止: 之前 3 秒一切换, 突然 15 秒静止",
        "突然跳切: 不连续的两镜直接硬切",
        "突然倒放: 关键瞬间倒放一遍",
        "突然加速: 升格 60fps 切到正常 24fps",
    ],
    "detail": [
        "突然插入不相关细节: 桌上突然多一支烟, 没人点燃",
        "突然特写某个东西: 一滴水 / 一只蚂蚁 / 一根头发",
        "突然声音: 没有画面的环境音先出现 2 秒",
        "突然消失: 角色突然走出画面, 留 5 秒空镜",
    ],
}


def generate_inspiration_moment(seed: int = None, current_progress: float = 0.0):
    """
    生成灵感时刻 - 在场景中突然改变镜头/色彩/构图/节奏
    """
    if seed is not None:
        random.seed(seed)

    # 灵感时刻的触发概率: 5-20% (基于场景进度)
    trigger_prob = 0.05 + 0.15 * math.sin(current_progress * math.pi)

    if random.random() > trigger_prob:
        return None

    # 随机选择灵感时刻类型
    moment_type = random.choice(list(INSPIRATION_MOMENTS.keys()))
    moment_content = random.choice(INSPIRATION_MOMENTS[moment_type])

    return {
        "type": moment_type,
        "content": moment_content,
        "trigger_prob": round(trigger_prob, 2),
        "context": f"在 scene_progress={current_progress:.2f} 时触发",
    }


# 兼容引用
_HAS_EMOTION_DATA = True


# ============================================================
# 7. DirectorSoulNode - ComfyUI 节点
# ============================================================
class DirectorSoulNode:
    """导演灵魂节点 - 单独节点, 注入到所有其他节点"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # === 情感选择 (单情感/双情感/多情感) ===
                "主导情感": (["auto"] + list(EMOTION_MATRIX_60.keys()), {"default": "loneliness"}),
                "次要情感_1": (["none"] + list(EMOTION_MATRIX_60.keys()), {"default": "none"}),
                "次要情感_2": (["none"] + list(EMOTION_MATRIX_60.keys()), {"default": "none"}),
                "次要情感_3": (["none"] + list(EMOTION_MATRIX_60.keys()), {"default": "none"}),
                "次要情感_4": (["none"] + list(EMOTION_MATRIX_60.keys()), {"default": "none"}),

                # === 融合模式 ===
                "融合模式": (["auto", "F1_单情感主导", "F2_双情感主次融合", "F3_双情感对等融合", "F4_三情感递进融合", "F5_矛盾情感爆炸", "F6_复合情绪三角", "F7_情感转化"], {"default": "auto"}),

                # === 主导情感权重 ===
                "主导权重": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05}),

                # === 灵魂维度 ===
                "创造力": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "想象力": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "艺术表达": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "镜头技巧": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "氛围掌控": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),

                # === 灵魂状态 ===
                "灵感指数": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "疲劳指数": ("FLOAT", {"default": 0.30, "min": 0.0, "max": 1.0, "step": 0.05}),
                "怀疑指数": ("FLOAT", {"default": 0.50, "min": 0.0, "max": 1.0, "step": 0.05}),
                "叛逆指数": ("FLOAT", {"default": 0.70, "min": 0.0, "max": 1.0, "step": 0.05}),

                # === 导演视角 ===
                "导演": (["王家卫", "诺兰", "PTA", "奉俊昊", "黑泽明", "库斯杜力卡", "塔可夫斯基", "伯格曼", "王家卫_1980", "约阿希姆·提尔", "李安", "王家卫+侯孝贤"], {"default": "王家卫"}),

                # === 场景上下文 ===
                "场景描述": ("STRING", {"default": "父女在厨房, 雨夜, 1998 年哈尔滨", "multiline": True}),

                # === 故事强度 (影响灵魂状态) ===
                "故事强度": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),

                # === 场景进度 ===
                "场景进度": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "soul_injection",           # 完整灵魂注入字符串 (供其他节点使用)
        "fused_emotion",            # 融合情感档案
        "emotion_dimensions",       # 情感强度 + 极性 + 唤醒度
        "soul_dimensions",          # 10 灵魂维度
        "soul_state",               # 当前灵魂状态
        "director_signature",       # 导演签名
        "scene_prompt_addon",       # 场景 prompt 增强
        "h3_alignment_addon",       # H3 三大字段增强
    )

    FUNCTION = "build_soul"
    CATEGORY = "PromptLibrary/Phase17 灵魂"

    def build_soul(self, **kwargs):
        # 1. 收集情感
        emotion_keys = []
        if kwargs.get("主导情感") and kwargs["主导情感"] != "auto":
            emotion_keys.append(kwargs["主导情感"])
        for i in range(1, 5):
            key = f"次要情感_{i}"
            val = kwargs.get(key, "none")
            if val and val != "none":
                emotion_keys.append(val)

        # 2. 收集权重
        weights = [kwargs.get("主导权重", 1.0)]
        # 剩余权重按平均分配
        if len(emotion_keys) > 1:
            remaining = 1.0 - weights[0]
            n_remaining = len(emotion_keys) - 1
            for _ in range(n_remaining):
                weights.append(remaining / n_remaining)

        # 3. 融合情感
        fused = fuse_emotions(
            emotion_keys,
            weights,
            kwargs.get("融合模式", "auto"),
        )
        if not fused:
            fused = fuse_emotions(["loneliness"], [1.0], "F1_单情感主导")

        # 4. 灵魂维度
        soul_dims = {
            "creativity": kwargs.get("创造力", 0.85),
            "imagination": kwargs.get("想象力", 0.85),
            "artistic_expression": kwargs.get("艺术表达", 0.85),
            "camera_skill": kwargs.get("镜头技巧", 0.85),
            "atmosphere_control": kwargs.get("氛围掌控", 0.85),
        }

        # 5. 灵魂状态
        soul_state = {
            "inspiration": kwargs.get("灵感指数", 0.85),
            "fatigue": kwargs.get("疲劳指数", 0.30),
            "doubt": kwargs.get("怀疑指数", 0.50),
            "rebelliousness": kwargs.get("叛逆指数", 0.70),
        }

        # 6. 导演签名
        director = kwargs.get("导演", "王家卫")
        director_signatures = {
            "王家卫": "用物件代替心理, 时间戳, 60s 慢节奏",
            "诺兰": "时间结构即主题, 史诗感, IMAX 客观",
            "PTA": "用可观察行为代替情绪, 70s 迷幻, 慢推长焦",
            "奉俊昊": "用空间做阶层隐喻, 类型当特洛伊木马, 同场多情绪",
            "黑泽明": "天气即角色, 极致清晰, 群戏调度",
            "库斯杜力卡": "少说话, 沉默即情感, 塞尔维亚乡愁",
            "塔可夫斯基": "时间即主角, 长镜头, 诗意朦胧",
            "伯格曼": "脸特写, 沉默, 心理剧",
            "王家卫_1980": "王家卫早期, 短片, 实验性",
            "约阿希姆·提尔": "从房子视角叙事, 家庭代际, 北欧光",
            "李安": "饭桌戏, 东西方文化张力, 父亲",
            "王家卫+侯孝贤": "长镜头+少台词+物件, 东方美学",
        }
        director_sig = director_signatures.get(director, "")

        # 7. 完整灵魂注入
        soul_injection = build_soul_injection(
            emotion_keys,
            weights,
            kwargs.get("融合模式", "auto"),
            director,
            kwargs.get("场景描述", ""),
        )

        # 8. 场景 prompt 增强 (供 concept_pitch / director_intent 等使用)
        scene_prompt_addon = f"""
[灵魂融合层注入]
主导情感: {fused['name']} (强度 {fused['intensity']:.2f}, 极性 {fused['polarity']})
视觉锚点: {fused['visual_signs'][:200]}
声音锚点: {fused['voice_signs'][:200]}
内心独白: {fused['inner_monologue'][:200]}
色彩倾向: {fused['color_palette'][:150]}
音乐倾向: {fused['music_tempo'][:150]}
导演签名: {director_sig}
导演灵魂: 创造 {soul_dims['creativity']:.2f} | 想象 {soul_dims['imagination']:.2f} | 艺术 {soul_dims['artistic_expression']:.2f}
灵感: {soul_state['inspiration']:.2f} | 怀疑: {soul_state['doubt']:.2f} | 叛逆: {soul_state['rebelliousness']:.2f}
[灵魂融合层结束]
"""

        # 9. H3 三大字段增强
        h3_addon = f"""
INTEGRATED_MULTIMODAL_DESCRIPTION 灵魂增强:
[Emotion Anchor] {fused['name']} ({fused['polarity']}, intensity {fused['intensity']:.2f})
[Visual] {fused['visual_signs'][:150]}
[Voice] {fused['voice_signs'][:100]}
[Color] {fused['color_palette'][:100]}

OVERALL_SOUNDSCAPE 灵魂增强:
{', '.join([fused['voice_signs'][:80], fused['music_tempo'][:80]])}

NON_DIEGETIC_MUSIC 灵魂增强:
[Music Style: {fused['music_tempo'][:120]}]
"""

        # 输出
        soul_inj_str = soul_injection
        fused_str = json.dumps(fused, ensure_ascii=False, indent=2)
        emotion_dims_str = f"intensity={fused['intensity']:.2f} | polarity={fused['polarity']} | arousal={fused['arousal']}"
        soul_dims_str = " | ".join([f"{k}={v:.2f}" for k, v in soul_dims.items()])
        soul_state_str = " | ".join([f"{k}={v:.2f}" for k, v in soul_state.items()])
        director_sig_str = f"导演: {director} | 签名: {director_sig}"

        return (
            soul_inj_str,
            fused_str,
            emotion_dims_str,
            soul_dims_str,
            soul_state_str,
            director_sig_str,
            scene_prompt_addon,
            h3_addon,
        )


NODE_CLASS_MAPPINGS = {
    "DirectorSoulNode": DirectorSoulNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DirectorSoulNode": "🎭 导演灵魂节点 (Phase 17 灵魂)",
}


if __name__ == "__main__":
    # 测试情感融合
    print("=" * 60)
    print("情感矩阵测试 (60 种情感)")
    print("=" * 60)
    print(f"  情感总数: {len(EMOTION_MATRIX_60)}")
    for i, (k, v) in enumerate(EMOTION_MATRIX_60.items()):
        if i < 3:
            print(f"  - {k}: {v['name']} ({v['category']}, intensity {v['intensity']}, {v['polarity']})")

    print("\n" + "=" * 60)
    print("情感融合测试 (F1-F7)")
    print("=" * 60)
    for i, (k, v) in enumerate(EMOTION_FUSION_7.items()):
        print(f"  {k}: {v['name']} - {v['scenarios']}")

    # 测试 F3 双情感对等融合
    fused = fuse_emotions(["loneliness", "longing"], [0.5, 0.5], "F3_双情感对等融合")
    if fused:
        print(f"\n  融合结果: {fused['name']}")
        print(f"  intensity: {fused['intensity']:.2f}, polarity: {fused['polarity']}")
        print(f"  description: {fused['description'][:200]}")

    # 测试灵魂注入
    print("\n" + "=" * 60)
    print("导演灵魂注入测试")
    print("=" * 60)
    inj = build_soul_injection(
        ["loneliness", "longing"],
        [0.5, 0.5],
        "F3_双情感对等融合",
        "王家卫",
        "父女在厨房, 雨夜"
    )
    print(inj[:2000])
    print(f"\n总长度: {len(inj)} 字符")
