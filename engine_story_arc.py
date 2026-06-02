# ============================================================
# 故事结构引擎 — 将25个故事感总纲变为可计算的结构化数据
# ============================================================
# 核心能力：
#   1. 解析故事感总纲为结构化的节拍序列
#   2. 对给定镜头序号，精确计算其所属节拍和情绪状态
#   3. 生成镜头间的连续性约束
# ============================================================
import random
import re
import math
import os
import sys

# 确保模块搜索路径包含本目录（ComfyUI不自动添加）
_node_dir = os.path.dirname(os.path.abspath(__file__))
if _node_dir not in sys.path:
    sys.path.insert(0, _node_dir)

from story_sense_data import STORY_SENSE_LIBRARY


# ============================================================
# 情绪映射字典 — 将中文情绪词映射为数值(0.0恐惧-1.0高涨)
# ============================================================
EMOTION_MAP = {
    # 积极情绪
    "高兴": 0.85, "快乐": 0.85, "开心": 0.82, "兴奋": 0.88, "激动": 0.90,
    "温暖": 0.75, "感动": 0.70, "幸福": 0.85, "满足": 0.72, "释然": 0.65,
    "希望": 0.70, "期待": 0.68, "惊喜": 0.80, "欢乐": 0.85,
    # 中性
    "平稳": 0.50, "安稳": 0.48, "平静": 0.45, "日常": 0.50, "普通": 0.50,
    "好奇": 0.55, "新鲜": 0.55, "平淡": 0.45, "仪式感": 0.52,
    # 消极
    "悲伤": 0.20, "难过": 0.22, "失落": 0.25, "绝望": 0.05, "恐惧": 0.10,
    "紧张": 0.30, "焦虑": 0.28, "挫败": 0.18, "愤怒": 0.25, "挣扎": 0.22,
    "孤独": 0.20, "无助": 0.12, "心痛": 0.18, "压抑": 0.15, "灰暗": 0.12,
    "消沉": 0.18, "低落": 0.20, "脆弱": 0.22, "害怕": 0.15, "不安": 0.30,
    "怀疑": 0.25, "崩溃": 0.08, "泪水": 0.20, "苦涩": 0.22,
    # 过渡情绪
    "坚持": 0.45, "倔强": 0.48, "努力": 0.55, "尝试": 0.50,
    "突破": 0.72, "起飞": 0.78, "爆发": 0.80,
    "微光": 0.38, "重新": 0.45, "缓冲": 0.42,
    # 复合情绪 — 取第一个主要情绪
    "犹豫": 0.35, "思念": 0.30, "怀念": 0.35, "感动": 0.70, "共鸣": 0.65,
}

# ============================================================
# 中文情绪词 → 英文标签映射
# ============================================================
EMOTION_EN_MAP = {
    "暖": "warm", "温暖": "warm", "感动": "touched", "美好": "beautiful",
    "释然": "relieved", "开阔": "open", "温柔": "gentle", "淡然": "peaceful",
    "继续": "continuing", "传递": "passing_on", "前行": "moving_on",
    "暖": "warm", "笑": "laughing", "希望在": "hopeful",
    "悲伤": "sad", "难过": "sad", "绝望": "desperate", "恐惧": "terrified",
    "紧张": "tense", "愤怒": "angry", "孤独": "lonely", "压抑": "oppressed",
    "心痛": "heartbroken", "失落": "lost",
}

# ============================================================
# 景别数值 — 用于交替检测
# ============================================================
SHOT_TYPE_PRIORITY = {
    "极远景": 1, "远景": 2, "全景": 3, "中景": 4,
    "近景": 5, "特写": 6, "极特写": 7,
}

SHOT_TYPE_NAMES = [
    "极远景", "远景", "全景", "中景", "近景", "特写", "极特写",
]


class StoryBeat:
    """一个叙事节拍 — 包含情绪值、节奏、视觉强度、叙事功能"""
    
    def __init__(self, name, emotion_value, pace, intensity, narrative_func):
        self.name = name
        self.emotion_value = emotion_value  # 0.0-1.0
        self.pace = pace                    # "slow" / "medium" / "fast"
        self.intensity = intensity          # 0.0-1.0 视觉冲击力
        self.narrative_func = narrative_func  # 文本描述
    
    def to_dict(self):
        return {
            "name": self.name,
            "emotion": self.emotion_value,
            "pace": self.pace,
            "intensity": self.intensity,
            "narrative_func": self.narrative_func,
        }


class StoryArc:
    """故事弧 — 解析总纲并计算每个镜头的节拍位置"""
    
    def __init__(self, sense_text):
        """
        从故事感总纲文本中解析出结构化的故事弧
        
        sense_text: 一条完整的【故事感总纲N：XXX】文本
        """
        self.sense_text = sense_text
        self.beats = self._parse_beats()
        self.emotion_curve = [b.emotion_value for b in self.beats]
    
    def _parse_beats(self):
        """解析总纲文本为结构化的节拍序列"""
        text = self.sense_text
        
        # 提取标题
        title_match = re.search(r'【故事感总纲\d+：([^】]+)】', text)
        self.title = title_match.group(1) if title_match else "未知"
        
        # 提取一句话核心
        core_match = re.search(r'一句话核心：([^\n]+)', text)
        self.core = core_match.group(1).strip() if core_match else ""
        
        # 提取情感节奏行
        rhythm_match = re.search(r'情感节奏：([^\n]+)', text)
        rhythm_text = rhythm_match.group(1).strip() if rhythm_match else ""
        
        # 解析情感节奏
        beats = []
        if rhythm_text:
            parts = rhythm_text.split("→")
            for i, part in enumerate(parts):
                part = part.strip()
                # 格式如 "开场-平稳" 或 "开场-压抑微痛"
                segments = part.split("-", 1)
                beat_name = segments[0].strip() if len(segments) > 0 else f"节拍{i+1}"
                emotion_words = segments[1].strip() if len(segments) > 1 else "中性"
                
                # 计算情绪值
                emotion_val = self._emotion_to_value(emotion_words)
                
                # 根据位置确定节奏和强度
                total = len(parts)
                progress = i / max(total - 1, 1)
                
                if progress < 0.15:
                    pace = "medium"
                    intensity = 0.3 + emotion_val * 0.4
                elif progress < 0.35:
                    pace = "medium"
                    intensity = 0.4 + emotion_val * 0.3
                elif progress < 0.55:
                    pace = "slow" if emotion_val < 0.3 else "medium"
                    intensity = 0.3 + emotion_val * 0.3
                elif progress < 0.7:
                    pace = "slow"
                    intensity = 0.2 + emotion_val * 0.2
                elif progress < 0.85:
                    pace = "fast"
                    intensity = 0.6 + emotion_val * 0.4
                else:
                    pace = "slow"
                    intensity = 0.4 + emotion_val * 0.4
                
                beat = StoryBeat(
                    name=beat_name,
                    emotion_value=emotion_val,
                    pace=pace,
                    intensity=min(intensity, 1.0),
                    narrative_func=emotion_words,
                )
                beats.append(beat)
        
        # 提取情节结构步骤
        self.story_steps = self._extract_story_steps()
        
        return beats
    
    def _extract_story_steps(self):
        """提取情节结构的步骤描述"""
        steps = []
        for line in self.sense_text.split('\n'):
            line = line.strip()
            match = re.match(r'\d+\.\s*(.+?)(?::|$)', line)
            if match:
                steps.append(match.group(1).strip())
        return steps
    
    def _emotion_to_value(self, word_text):
        """将中文情绪描述转为数值"""
        words = word_text.split("/")
        values = []
        for w in words:
            w = w.strip()
            if w in EMOTION_MAP:
                values.append(EMOTION_MAP[w])
            else:
                # 拆字匹配
                for key, val in EMOTION_MAP.items():
                    if key in w:
                        values.append(val)
                        break
                else:
                    values.append(0.5)  # 默认中性
        if values:
            return sum(values) / len(values)
        return 0.5
    
    def get_beat_for_shot(self, shot_index, total_shots):
        """
        计算第N个镜头所属的节拍
        
        返回:
            dict: {name, emotion, pace, intensity, narrative_func, beat_progress}
        """
        if not self.beats or total_shots <= 0:
            return self._default_beat()
        
        progress = shot_index / max(total_shots, 1)
        beat_idx = min(int(progress * len(self.beats)), len(self.beats) - 1)
        beat = self.beats[beat_idx]
        
        # 节拍内的进度（用于微调）
        beat_start = beat_idx / len(self.beats)
        beat_end = (beat_idx + 1) / len(self.beats)
        if beat_end - beat_start > 0:
            beat_progress = (progress - beat_start) / (beat_end - beat_start)
        else:
            beat_progress = 0.5
        
        # 如果是倒数几个beat，标记为"结尾阶段"
        is_final = (beat_idx >= len(self.beats) - 2)
        
        # 推荐的景别（根据情绪和强度）
        recommended_shot_types = self._recommend_shot_type(beat, beat_idx, shot_index)
        
        # 情绪描述（中文转英文标签）
        emotion_tags = self._emotion_tags(beat.narrative_func)
        
        return {
            "beat_name": beat.name,
            "beat_index": beat_idx,
            "total_beats": len(self.beats),
            "beat_progress": beat_progress,
            "story_progress": progress,
            "emotion_value": beat.emotion_value,
            "emotion_tags": emotion_tags,
            "pace": beat.pace,
            "intensity": beat.intensity,
            "narrative_func": beat.narrative_func,
            "is_final": is_final,
            "recommended_shot_types": recommended_shot_types,
            "constraints": {
                "no_abstract_words": True,
                "use_visible_description": True,
                "emotion_target": beat.emotion_value,
            }
        }
    
    def _recommend_shot_type(self, beat, beat_idx, shot_index):
        """根据节拍推荐合适的景别"""
        intensity = beat.intensity
        
        if intensity < 0.25:
            return ["远景", "全景"]  # 低强度用远景表现孤独/渺小
        elif intensity < 0.45:
            return ["全景", "中景"]  # 中低强度
        elif intensity < 0.65:
            return ["中景", "近景"]  # 中等强度
        elif intensity < 0.85:
            return ["近景", "特写"]  # 高强度用近景/特写
        else:
            return ["特写", "极特写"]  # 极致情绪
    
    def _emotion_tags(self, func_text):
        """将情绪描述转为英文标签"""
        tags = []
        for cn, en in EMOTION_EN_MAP.items():
            if cn in func_text:
                tags.append(en)
        if not tags:
            tags.append("neutral")
        return tags
    
    def _default_beat(self):
        return {
            "beat_name": "开场",
            "beat_index": 0,
            "total_beats": 1,
            "beat_progress": 0.5,
            "story_progress": 0.0,
            "emotion_value": 0.5,
            "emotion_tags": ["neutral"],
            "pace": "medium",
            "intensity": 0.5,
            "narrative_func": "开场建立情境",
            "is_final": False,
            "recommended_shot_types": ["全景", "中景"],
            "constraints": {"no_abstract_words": True, "use_visible_description": True, "emotion_target": 0.5},
        }
    
    def to_text(self, shot_index=None, total_shots=None):
        """生成用于prompt的总纲文本"""
        text_parts = [self.sense_text]
        
        if shot_index is not None and total_shots is not None:
            beat = self.get_beat_for_shot(shot_index, total_shots)
            text_parts.append(
                f"\n【当前镜头叙事信息】\n"
                f"这是第{shot_index+1}/{total_shots}个镜头\n"
                f"当前故事节拍：{beat['beat_name']}（第{beat['beat_index']+1}/{beat['total_beats']}段）\n"
                f"情绪目标：{beat['emotion_value']:.2f}（{', '.join(beat['emotion_tags'])}）\n"
                f"节奏：{beat['pace']} | 视觉强度：{beat['intensity']:.2f}\n"
                f"叙事功能：{beat['narrative_func']}\n"
                f"推荐景别：{'/'.join(beat['recommended_shot_types'])}\n"
            )
            if beat['is_final']:
                text_parts.append("【注意】这是结尾阶段的镜头，画面应具有收束感和余韵。\n")
        
        return "\n".join(text_parts)


class ShotConstraints:
    """镜头连续性约束 — 在逐镜头生成时维护状态"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.shot_count = 0
        self.last_shot_type = None
        self.shot_type_history = []
        self.last_duration = None
        self.last_camera = None
        self.last_transition = None
        self.last_characters = ""
        self.last_scene = ""
    
    def record_shot(self, shot_data):
        """记录一个已生成的镜头数据"""
        self.shot_count += 1
        if isinstance(shot_data, dict):
            st = shot_data.get("shot_type")
            if st:
                self.shot_type_history.append(st)
                self.last_shot_type = st
            
            dur = shot_data.get("duration")
            if dur:
                self.last_duration = dur
            
            cam = shot_data.get("camera")
            if cam:
                self.last_camera = cam
            
            trans = shot_data.get("transition")
            if trans:
                self.last_transition = trans
            
            chars = shot_data.get("characters")
            if chars:
                self.last_characters = chars
            
            scene = shot_data.get("scene")
            if scene:
                self.last_scene = scene
    
    def get_constraints_text(self):
        """生成对下一镜头的约束文本"""
        parts = []
        
        # 景别交替约束
        recent = self.shot_type_history[-3:]
        if len(recent) >= 3 and len(set(recent)) == 1:
            parts.append(f"【⚠️景别警告】最近3个镜头都是{recent[0]}，下一个镜头必须更换为不同的景别。")
        elif len(recent) >= 2 and len(set(recent)) == 1:
            parts.append(f"【提示】最近2个镜头都是{recent[0]}，建议下一个镜头切换景别。")
        
        # 时长交替
        if self.last_duration:
            parts.append(f"【参考】上一个镜头时长为{self.last_duration}秒。")
        
        # 运镜交替
        if self.last_camera:
            parts.append(f'【参考】上一个镜头运镜方式为"{self.last_camera}"。')
        
        # 转场
        if self.last_transition:
            parts.append(f'【参考】上一个镜头转场为"{self.last_transition}"。')
        
        # 角色一致性
        if self.last_characters:
            parts.append(f"【角色一致性】上一个镜头的角色描述：{self.last_characters[:100]}。本镜头需保持角色外貌、服装、状态一致，除非有明确的变化交代。")
        
        # 场景连续性
        if self.last_scene:
            parts.append(f"【场景连续性】上一个镜头的场景：{self.last_scene[:100]}。场景变化时请明确标注。")
        
        return "\n".join(parts)
    
    def get_shot_index_display(self):
        return f"第{self.shot_count+1}个镜头"


class PromptSegmenter:
    """输出分割器 — 将一批镜头的输出切分为独立的段"""
    
    SEGMENT_SEPARATOR = "===SEGMENT_BREAK==="
    SHOT_SEPARATOR = "===SHOT_SEPARATOR==="
    
    @classmethod
    def join_outputs(cls, segments):
        """将多个独立输出拼接为一个批次"""
        return cls.SEGMENT_SEPARATOR.join(segments)
    
    @classmethod
    def split_output(cls, combined_text):
        """将批次输出拆分为独立段"""
        if not combined_text:
            return []
        parts = combined_text.split(cls.SEGMENT_SEPARATOR)
        return [p.strip() for p in parts if p.strip()]
