# ============================================================
# PromptLibraryNode Pro V20.5 — 全能创作节点
# ============================================================
# 架构：
#   __init__.py         → 节点注册 + 主类（混入模式）
#   story_sense_data.py → 25个故事感总纲（内联常量）
#   llm_client.py       → AI API 调用封装（指数退避重试）
#   utils.py            → 工具函数（文件扫描/过滤/图片加载/负面词）
#   random_content.py   → 随机主题/角色/环境生成
#   modes_storyboard.py → 故事板模式（9种）
#   modes_book.py       → 绘本模式
#   modes_drama.py      → 短剧模式
#   modes_child.py      → 儿童内容模式（4种）
#   modes_design.py     → 专业设计模式（8种）
#   director_pro.py     → DirectorPromptPro 批次输出引擎
#   format_templates.py → 共享格式模板（消除跨模块重复）
#   engine_story_arc.py → StoryArc引擎 + ShotConstraints + PromptSegmenter
#   web/PromptLibraryNode.js → 参考图上传UI
# ============================================================
import os
import sys

# ComfyUI不自动把节点目录加入模块搜索路径，需要手动添加
_node_dir = os.path.dirname(os.path.abspath(__file__))
if _node_dir not in sys.path:
    sys.path.insert(0, _node_dir)

import random
import re
import json
import hashlib
import math
import time as _time
import threading
from datetime import datetime

import torch

# ---- 子模块导入 ----
from story_sense_data import STORY_SENSE_LIBRARY
from pln_llm import call_ai, translate_prompt
from pln_utils import (
    parse_keywords, parse_tags, scan_files, file_has_tag,
    load_lines, smart_filter, filter_by_subject,
    pick_n_lines, history_dedup,
    parse_ref_image_list, load_ref_image_tensors,
    generate_negative_prompt,
    append_history_log, make_output_id, _next_batch_seq,
)
from pln_random import random_topic, random_character, random_env
from modes_storyboard import (
    _process_storyboard_mode as _process_storyboard_mode_impl,
)
from modes_book import process_picture_book_mode as _process_picture_book_mode_impl
from modes_drama import process_short_drama as _process_short_drama_mode_impl
from modes_child import (
    build_child_system_prompt as _build_child_system_prompt_impl,
)

# [P0修复] modes_design 模块可能不存在，用 try/except 守卫避免整个插件加载崩溃
try:
    from modes_design import (
        _build_design_system_prompt,
        _build_design_user_prompt,
        _build_design_global_context,
    )
    _HAS_DESIGN_MODE = True
except ImportError:
    _HAS_DESIGN_MODE = False

from engine_story_arc import StoryArc, ShotConstraints, PromptSegmenter

# ============================================================
# 模式定义
# ============================================================
ALL_MODES = [
    "关闭",
    "电影分镜", "广告故事板", "动画故事板", "漫画分镜", "MV故事板",
    "教程步骤", "短视频分镜", "品牌故事板", "剧情分镜",
    "绘本模式", "短剧模式",
    "儿童视频格式一", "儿童视频格式二", "儿童微动视频/GIF", "儿童绘本格式",
    "电商套图", "海报设计", "品牌设计", "PPT设计",
    "逻辑关系图设计", "三视图设计", "爆炸拆解图设计", "流水线图设计",
]

MODE_CATEGORIES_STORYBOARD = {"电影分镜", "广告故事板", "动画故事板", "漫画分镜",
                               "MV故事板", "教程步骤", "短视频分镜", "品牌故事板", "剧情分镜"}
MODE_CATEGORIES_CHILD = {"儿童视频格式一", "儿童视频格式二", "儿童微动视频/GIF", "儿童绘本格式"}
MODE_CATEGORIES_DESIGN = {"电商套图", "海报设计", "品牌设计", "PPT设计",
                           "逻辑关系图设计", "三视图设计", "爆炸拆解图设计", "流水线图设计"}

# [P0修复] 移除原模块级 OUTPUT_NAMES（6项）和 OUTPUT_TYPES（6项）——
# 它们是从旧版遗留的死代码，与类级 RETURN_TYPES/RETURN_NAMES（5项）长度不一致，
# 容易引起维护混乱。ComfyUI 只读取类属性，此处无需保留。

WEB_DIRECTORY = "web"


# ============================================================
# 主节点类
# ============================================================
class PromptLibraryNodePro:
    """提示词库节点 V20.5 — 全能创作节点"""
    _instance_lock = threading.Lock()
    # 故事感总纲缓存（类级，只加载一次）
    _story_sense_cache = None

    @classmethod
    def _ensure_story_sense(cls):
        """确保故事感总纲已加载（类级缓存，线程安全）"""
        # [P2修复] 使用 _instance_lock 保护类级缓存的初始化，
        # 防止 ComfyUI 多工作流线程并发场景下的竞态条件
        if cls._story_sense_cache is None:
            with cls._instance_lock:
                # 双重检查锁定（Double-Checked Locking）
                if cls._story_sense_cache is None:
                    cls._story_sense_cache = STORY_SENSE_LIBRARY[:]

    def _pick_story_sense(self):
        """从故事感总纲常量中随机抽取一个（缓存版本，避免重复读文件）"""
        self._ensure_story_sense()
        if self._story_sense_cache:
            return random.choice(self._story_sense_cache)
        return ""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文件夹路径": ("STRING", {"default": "", "multiline": False}),
                "读取模式": (
                    ["随机抽取", "顺序循环", "洗牌遍历", "权重随机",
                     "等权随机", "短文优先", "长文优先", "文件均衡"],
                    {"default": "随机抽取"},
                ),
                "循环模式": (
                    ["无限循环", "读完停止", "历史不重复(1000条)",
                     "批次内不重复", "重置循环位置"],
                    {"default": "无限循环"},
                ),
                "输出数量": ("INT", {"default": 1, "min": 1, "max": 50, "step": 1}),
                "输出分隔符": (
                    ["换行", "双换行", "逗号", "分号", "段落分隔(===)", "无分隔"],
                    {"default": "换行"},
                ),
                "启用历史落盘": ("BOOLEAN", {"default": True}),
                "固定种子_0为真随机": ("INT", {"default": 0}),
                "关键词筛选": ("STRING", {"default": "", "multiline": False}),
                "标签筛选": ("STRING", {"default": "", "multiline": False}),
                "开启AI润色": ("BOOLEAN", {"default": False}),
                "AI润色系统提示词": ("STRING", {"default": "你是一个专业prompt润色师。将用户输入的prompt润色为细节丰富的中文prompt。保持原意，增加光影、材质、构图、氛围等细节。直接输出润色后的prompt，不要解释。", "multiline": True}),
                "开启AI生成": ("BOOLEAN", {"default": False}),
                "AI生成系统提示词": ("STRING", {"default": "你是一个专业AI绘画prompt生成器。请生成一条完整的中文prompt，包含：艺术风格+主体+场景+光线+构图+细节+色彩+质量词。直接输出prompt，不要解释。", "multiline": True}),
                "批量AI生成数": ("INT", {"default": 1, "min": 1, "max": 20, "step": 1}),
                "启用主体过滤": ("BOOLEAN", {"default": True}),
                "启用负面词生成": ("BOOLEAN", {"default": False}),
                "负面词自定义": ("STRING", {"default": "", "multiline": False}),
                "开启翻译": ("BOOLEAN", {"default": False}),
                "翻译方向": (["中译英", "英译中", "日译中"], {"default": "中译英"}),
                "API地址": ("STRING", {"default": "http://localhost:1234/v1/chat/completions", "multiline": False}),
                "API密钥": ("STRING", {"default": "", "multiline": False}),
                "AI模型名": ("STRING", {"default": "", "multiline": False}),
                "AI推理温度": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 2.0, "step": 0.1}),
                "AI最大Token数": ("INT", {"default": 10000, "min": 256, "max": 100000, "step": 256}),
                "参考图列表": ("STRING", {"default": "[]", "multiline": True}),
                "模式选择": (ALL_MODES, {"default": "关闭"}),
                "故事剧本": ("STRING", {"default": "", "multiline": True}),
                "角色描述": ("STRING", {"default": "", "multiline": True}),
                "环境背景描述": ("STRING", {"default": "", "multiline": True}),
                "总页数/总片段数": ("INT", {"default": 8, "min": 1, "max": 60, "step": 1}),
                "画面风格": (
                    ["电影感", "古装风", "喜剧风", "言情风", "悬疑风", "科幻风",
                     "奇幻风", "武侠风", "宫廷风", "都市风", "民国风", "田园风",
                     "赛博风", "蒸汽朋克风", "末日废土风", "校园风", "职场风",
                     "家庭温情风", "史诗正剧风", "文艺叙事风", "黑色幽默风",
                     "实验先锋风", "纪录写实风", "神话史诗风"],
                    {"default": "电影感"},
                ),
                "色彩基调": (
                    ["自动", "暖色调", "冷色调", "高对比", "低饱和", "复古",
                     "赛博朋克", "日系清新", "黑白",
                     "温暖明亮", "清新淡雅", "梦幻柔和", "浓郁鲜艳"],
                    {"default": "自动"},
                ),
                "景别偏好": (
                    ["自动-多种交替", "以远景为主", "以中景为主", "以近景/特写为主", "全特写"],
                    {"default": "自动-多种交替"},
                ),
                "运镜风格": (
                    ["自动", "稳重固定镜头", "流畅运动", "手持纪实", "炫酷动感",
                     "竖屏固定机位为主", "竖屏流畅运动"],
                    {"default": "自动"},
                ),
            },
            "optional": {
                "绘本文字量": (["自动", "少字（每页10字以内）", "中等（每页20-40字）", "多字（每页50字以上）"], {"default": "自动"}),
                "绘本年龄段": (["0-3岁低幼", "3-6岁幼儿", "6-9岁学龄", "9-12岁少年"], {"default": "3-6岁幼儿"}),
                "短剧节奏强度": (["自动", "舒缓铺垫", "紧凑推进", "高能密集"], {"default": "自动"}),
                "儿童年龄段": (["0-3岁低幼", "3-6岁幼儿", "6-9岁学龄"], {"default": "3-6岁幼儿"}),
                "儿童画风": (["水彩插画", "卡通动画", "彩铅手绘", "黏土定格", "扁平矢量"], {"default": "卡通动画"}),
                "产品材质": ("STRING", {"default": "", "multiline": False}),
                "产品颜色": ("STRING", {"default": "", "multiline": False}),
                "拍摄角度": (["自动", "正面平视", "45度俯视", "顶部俯拍", "侧面特写",
                              "微距细节", "场景环绕", "多角度组图"], {"default": "自动"}),
                "布光方案": (["自动", "柔光箱主光+补光", "侧光+轮廓光", "逆光+正面补光",
                              "顶光+漫反射", "三点布光", "自然光", "硬光戏剧效果"], {"default": "自动"}),
                "背景类型": (["自动", "纯色背景", "渐变色背景", "纹理背景", "场景实景",
                              "悬浮展示", "模特穿戴", "创意道具"], {"default": "自动"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "IMAGE",)
    RETURN_NAMES = ("文件夹提示词", "剧本模式输出", "负面提示词", "元数据JSON", "回调图片",)
    FUNCTION = "get_prompt"
    CATEGORY = "提示词工具"
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # [修复] 智能变更检测：
        # - 文件夹模式 + seed=0(随机) → 每次强制重算（用户期望新结果）
        # - 文件夹模式 + 顺序/洗牌循环 → 每次强制重算（需推进idx）
        # - 固定种子 > 0 且无文件夹 → 用参数哈希缓存（确定性输出）
        seed = kwargs.get("固定种子_0为真随机", 0)
        folder = kwargs.get("文件夹路径", "")
        mode = kwargs.get("读取模式", "随机抽取")
        模式选择 = kwargs.get("模式选择", "关闭")

        # 文件夹路径有值 → 几乎所有模式都需要重新执行
        if folder:
            if seed and seed > 0 and mode == "随机抽取":
                # 唯一可缓存的情况：固定种子 + 纯随机（确定性复现）
                # 但顺序/洗牌/文件均衡等有状态的模式不能缓存
                pass
            else:
                return _time.time()

        # 剧本模式 / AI生成 → 需要重新执行（LLM 输出不确定）
        if 模式选择 != "关闭":
            return _time.time()
        if kwargs.get("开启AI生成", False) or kwargs.get("开启AI润色", False):
            return _time.time()

        # 种子=0 时即使无文件夹也强制重算（未来可能有随机因素）
        if not seed or seed <= 0:
            return _time.time()

        # 固定种子 + 无文件夹 + 无AI → 确定性，用参数哈希缓存
        try:
            hash_parts = []
            for k, v in sorted(kwargs.items()):
                try:
                    hash_parts.append(f"{k}={v}")
                except Exception:
                    pass
            hash_str = "|".join(hash_parts)
            return hashlib.md5(hash_str.encode("utf-8")).hexdigest()
        except Exception:
            return _time.time()

    def __init__(self):
        self._cache_lock = threading.Lock()
        self._cache = {}
        self._last_ai_error = ""
        self._last_folder_meta = ""
        self._ensure_story_sense()

    # ============================================================
    # 主入口
    # ============================================================
    def get_prompt(self, **kwargs):
        """主处理入口 - 按模式分派"""
        start_time = datetime.now()

        模式选择 = kwargs.get("模式选择", "关闭")
        主题 = kwargs.get("故事剧本", "")
        角色描述 = kwargs.get("角色描述", "")
        环境背景描述 = kwargs.get("环境背景描述", "")
        总页数 = kwargs.get("总页数/总片段数", 8)
        画面风格 = kwargs.get("画面风格", "电影感")
        色彩基调 = kwargs.get("色彩基调", "自动")
        景别偏好 = kwargs.get("景别偏好", "自动-多种交替")
        运镜风格 = kwargs.get("运镜风格", "自动")
        API地址 = kwargs.get("API地址", "")
        API密钥 = kwargs.get("API密钥", "")
        AI模型名 = kwargs.get("AI模型名", "")
        AI推理温度 = kwargs.get("AI推理温度", 0.8)
        AI最大Token数 = kwargs.get("AI最大Token数", 10000)

        # 参考图
        ref_image_files = parse_ref_image_list(kwargs.get("参考图列表", "[]"))
        ref_image_tensors = load_ref_image_tensors(ref_image_files)

        # 种子
        固定种子_0为真随机 = kwargs.get("固定种子_0为真随机", 0)
        if 固定种子_0为真随机 and 固定种子_0为真随机 > 0:
            random.seed(固定种子_0为真随机)

        # 初始化输出
        final_prompt = ""
        mode_output = ""
        negative_prompt = ""
        meta_json = {}

        # 构建 call_ai 闭包（绑定参数）
        # [P1修复-合约说明] 此闭包返回 str（仅结果文本），将错误存储在 self._last_ai_error。
        # 注意：director_pro.py 中的批处理函数直接调用 pln_llm.call_ai()，
        # 返回 (result_str, error_str) 元组。两套接口的差异是有意设计：
        # - 本闭包供传统模式和单次模式使用，调用者只需判断返回值是否为空
        # - director_pro 的批处理需要独立的错误处理逻辑，因此直接使用底层 API
        def _call_ai(system_prompt, user_message):
            result, self._last_ai_error = call_ai(
                API地址, API密钥, AI模型名,
                system_prompt, user_message,
                AI推理温度, AI最大Token数
            )
            return result

        # ====== 按模式分派 ======
        if 模式选择 == "关闭":
            self._last_folder_meta = ""
            final_prompt, mode_output = self._process_traditional_mode(kwargs, _call_ai)
            meta_json = {"mode": "关闭"}
            # [深度优化] 文件夹模式抽取元数据合并入 meta_json
            if self._last_folder_meta:
                try:
                    meta_json["folder_pick"] = json.loads(self._last_folder_meta)
                except Exception:
                    pass
        elif 模式选择 in MODE_CATEGORIES_STORYBOARD:
            # 计算故事弧
            story_arc = None
            try:
                sense_text = self._pick_story_sense()
                if sense_text:
                    story_arc = StoryArc(sense_text)
            except Exception:
                pass
            
            mode_output = _process_storyboard_mode_impl(
                模式选择, 主题, 角色描述, 环境背景描述,
                总页数, 画面风格, 色彩基调, 景别偏好, 运镜风格,
                API地址, API密钥, AI模型名, AI推理温度, AI最大Token数,
                ref_image_tensors,
                random_topic_fn=random_topic,
                random_character_fn=random_character,
                random_env_fn=random_env,
                call_ai_fn=_call_ai,
                pick_story_sense_fn=self._pick_story_sense,
                story_arc=story_arc,
            )
            meta_json = {"mode": 模式选择, "type": "故事板", "shots": 总页数}
        elif 模式选择 == "绘本模式":
            mode_output = _process_picture_book_mode_impl(
                主题, 角色描述, 环境背景描述, 总页数,
                画面风格, 色彩基调, kwargs.get("绘本文字量", "自动"), kwargs.get("绘本年龄段", "3-6岁幼儿"),
                API地址, API密钥, AI模型名, AI推理温度, AI最大Token数,
                ref_image_tensors,
                random_topic_fn=random_topic,
                random_character_fn=random_character,
                random_env_fn=random_env,
                call_ai_fn=_call_ai,
                pick_story_sense_fn=self._pick_story_sense,
            )
            meta_json = {"mode": "绘本模式", "type": "绘本", "pages": 总页数}
        elif 模式选择 == "短剧模式":
            mode_output = _process_short_drama_mode_impl(
                主题, 角色描述, 环境背景描述, 总页数,
                画面风格, kwargs.get("短剧节奏强度", "自动"), 运镜风格, 色彩基调,
                API地址, API密钥, AI模型名, AI推理温度, AI最大Token数,
                ref_image_tensors,
                random_topic,
                random_character,
                random_env,
                _call_ai,
                pick_story_sense_fn=self._pick_story_sense,
            )
            meta_json = {"mode": "短剧模式", "type": "短剧", "shots": 总页数}
        elif 模式选择 in MODE_CATEGORIES_CHILD:
            mode_output = self._process_child_mode(
                模式选择, 主题, 角色描述, 环境背景描述, 总页数,
                kwargs.get("儿童年龄段", "3-6岁幼儿"), kwargs.get("儿童画风", "卡通动画"),
                API地址, API密钥, AI模型名, AI推理温度, AI最大Token数,
                ref_image_tensors, _call_ai)
            meta_json = {"mode": 模式选择, "type": "儿童内容"}
        elif 模式选择 in MODE_CATEGORIES_DESIGN:
            if _HAS_DESIGN_MODE:
                mode_output = self._process_design_mode(
                    模式选择, 主题, 角色描述, 环境背景描述, 总页数, 画面风格, 色彩基调,
                    kwargs.get("产品材质", ""), kwargs.get("产品颜色", ""),
                    kwargs.get("拍摄角度", "自动"), kwargs.get("布光方案", "自动"), kwargs.get("背景类型", "自动"),
                    API地址, API密钥, AI模型名, AI推理温度, AI最大Token数,
                    ref_image_tensors, _call_ai)
                meta_json = {"mode": 模式选择, "type": "专业设计"}
            else:
                mode_output = f"[提示] 设计模式「{模式选择}」需要安装 modes_design 模块才能使用。"
                meta_json = {"mode": 模式选择, "type": "设计(模块缺失)"}

        # 负面词
        启用负面词生成 = kwargs.get("启用负面词生成", False)
        负面词自定义 = kwargs.get("负面词自定义", "")
        if 启用负面词生成:
            main_content = final_prompt or mode_output or ""
            negative_prompt = generate_negative_prompt(负面词自定义, main_content)

        # 回调图片
        callback_image = None
        if ref_image_tensors:
            try:
                callback_image = torch.cat(ref_image_tensors, dim=0)
            except Exception:
                callback_image = None

        result_tuple = (final_prompt, mode_output, negative_prompt,
                        json.dumps(meta_json, ensure_ascii=False),
                        callback_image)
        return result_tuple

    # ============================================================
    # 传统模式（提示词库/AI生成/润色/翻译）
    # ============================================================
    def _process_traditional_mode(self, kwargs, _call_ai):
        final_prompt = ""
        开启AI生成 = kwargs.get("开启AI生成", False)
        开启AI润色 = kwargs.get("开启AI润色", False)
        开启翻译 = kwargs.get("开启翻译", False)
        启用主体过滤 = kwargs.get("启用主体过滤", True)
        批量AI生成数 = kwargs.get("批量AI生成数", 1)
        固定种子_0为真随机 = kwargs.get("固定种子_0为真随机", 0)
        API地址 = kwargs.get("API地址", "")
        AI推理温度 = kwargs.get("AI推理温度", 0.8)
        AI最大Token数 = kwargs.get("AI最大Token数", 10000)

        if 开启AI生成:
            keywords = parse_keywords(kwargs.get("关键词筛选", ""))
            sys_p = kwargs.get("AI生成系统提示词", "") or "你是一个专业AI绘画prompt生成器。生成一条完整英文prompt，直接输出。"
            user_msg = "请生成一条高质量AI绘画prompt"
            if keywords:
                user_msg = f"请根据以下关键词生成一条高质量AI绘画prompt：{', '.join(keywords)}"
            ai_result = _call_ai(sys_p, user_msg)
            if ai_result:
                final_prompt = ai_result

        文件夹路径 = kwargs.get("文件夹路径", "")
        if 文件夹路径:
            folder_path = os.path.abspath(文件夹路径)
            if not os.path.isdir(folder_path):
                return ("", "")
            关键词筛选 = kwargs.get("关键词筛选", "")
            标签筛选 = kwargs.get("标签筛选", "")
            读取模式 = kwargs.get("读取模式", "随机抽取")
            循环模式 = kwargs.get("循环模式", "无限循环")
            输出数量 = kwargs.get("输出数量", 1)
            输出分隔符 = kwargs.get("输出分隔符", "换行")
            keywords = parse_keywords(关键词筛选)
            wanted_tags = parse_tags(标签筛选)
            files = scan_files(folder_path)
            if not files:
                return ("", "")
            if wanted_tags:
                matched_files = [f for f in files if file_has_tag(f, wanted_tags)]
                if not matched_files:
                    return ("", "")
                files = matched_files
            all_lines = load_lines(files, keywords)
            if not all_lines:
                return ("", "")
            smart_filtered = smart_filter(all_lines)
            if smart_filtered is not None:
                all_lines = smart_filtered
                if not all_lines:
                    return ("", "")
            if 启用主体过滤:
                subject_filtered = filter_by_subject(all_lines)
                if not subject_filtered:
                    return ("", "")
                all_lines = subject_filtered
            # [深度优化] 传递种子，pick_n_lines 使用独立 RNG
            chosen, self._cache = pick_n_lines(
                all_lines, 读取模式, 循环模式, 输出数量,
                folder_path, self._cache, seed=固定种子_0为真随机,
            )
            if not chosen:
                return ("", "")
            if "不重复" in 循环模式 and 循环模式 == "历史不重复(1000条)":
                chosen = history_dedup(
                    chosen, folder_path, self._cache,
                    all_lines=all_lines, seed=固定种子_0为真随机,
                )
                if not chosen:
                    chosen = [random.choice(all_lines)]
            result_texts = [l["text"] for l in chosen]
            # [深度优化] 拼接全部 chosen（不再丢弃多条），按用户分隔符
            sep_map = {
                "换行": "\n",
                "双换行": "\n\n",
                "逗号": ", ",
                "分号": "; ",
                "段落分隔(===)": "\n===SEGMENT_BREAK===\n",
                "无分隔": " ",
            }
            sep = sep_map.get(输出分隔符, "\n")
            final_prompt = sep.join(result_texts) if result_texts else ""
            # [深度优化] 写入当天历史日志 + 生成 output_id 反查索引
            启用历史落盘 = kwargs.get("启用历史落盘", True)
            output_ids = []
            if 启用历史落盘 and chosen:
                from datetime import datetime as _dt
                from pln_utils import _today_str
                _ts_now = _dt.now()
                _date_str = _ts_now.strftime("%Y-%m-%d")
                _batch_seq = _next_batch_seq(_date_str)
                _records = []
                for _i, _e in enumerate(chosen, start=1):
                    _oid = make_output_id(
                        固定种子_0为真随机, _batch_seq, _i, ts=_ts_now)
                    output_ids.append(_oid)
                    _records.append({
                        "ts": _ts_now.strftime("%Y-%m-%d %H:%M:%S"),
                        "date": _date_str,
                        "output_id": _oid,
                        "batch_seq": _batch_seq,
                        "folder": folder_path,
                        "mode": 读取模式,
                        "loop": 循环模式,
                        "seed": int(固定种子_0为真随机) if 固定种子_0为真随机 else 0,
                        "index": _i,
                        "text": _e["text"],
                        "source_file": os.path.basename(_e.get("source", "")),
                    })
                append_history_log(_records)
            # [深度优化] 元数据：抽取来源/数量/模式 + output_ids 反查索引
            try:
                meta = {
                    "folder": folder_path,
                    "mode": 读取模式,
                    "loop": 循环模式,
                    "requested": 输出数量,
                    "delivered": len(result_texts),
                    "pool_size": len(all_lines),
                    "sources": list({os.path.basename(l.get("source", "")) for l in chosen}),
                    "seed": 固定种子_0为真随机,
                    "output_ids": output_ids,
                    "history_logged": bool(启用历史落盘 and output_ids),
                }
                self._last_folder_meta = json.dumps(meta, ensure_ascii=False)
            except Exception:
                self._last_folder_meta = ""

        if 开启AI润色 and final_prompt:
            sys_p = kwargs.get("AI润色系统提示词", "") or "将用户输入的prompt润色为高质量英文prompt。直接输出结果。"
            ai_result = _call_ai(sys_p, final_prompt)
            if ai_result:
                final_prompt = ai_result

        if 开启AI生成 and final_prompt and 批量AI生成数 > 1:
            batch_results = [final_prompt]
            for b in range(批量AI生成数 - 1):
                b_seed = (固定种子_0为真随机 if 固定种子_0为真随机 > 0 else int(_time.time())) + b + 1
                random.seed(b_seed)
                kw = parse_keywords(kwargs.get("关键词筛选", ""))
                user_msg = "请生成一条高质量AI绘画prompt"
                if kw:
                    user_msg = f"请根据以下关键词生成一条高质量AI绘画prompt：{', '.join(kw)}"
                b_ret = _call_ai(
                    kwargs.get("AI生成系统提示词", "") or "你是一个专业AI绘画prompt生成器",
                    user_msg)
                if b_ret:
                    batch_results.append(b_ret)
            # [P1修复] 拼接所有批量生成结果，而非只取 batch_results[0]
            # 原来只返回第一条，丢弃了用户请求的多条AI生成结果
            final_prompt = "\n\n---\n\n".join(batch_results) if batch_results else ""

        if 开启翻译 and final_prompt and API地址:
            translated = translate_prompt(
                final_prompt, kwargs.get("翻译方向", "中译英"),
                API地址, kwargs.get("API密钥", ""), kwargs.get("AI模型名", ""),
                AI推理温度, AI最大Token数)
            if translated:
                final_prompt = translated

        return final_prompt, ""

    # ============================================================
    # 儿童内容模式处理
    # ============================================================
    def _process_child_mode(self, mode, topic, character_desc, env_desc, count,
                             age_group, art_style,
                             api_url, api_key, model_name, temperature, max_tokens,
                             ref_images, _call_ai):
        if not api_url:
            return ""

        if not topic:
            topic = random_topic(mode)
        if not character_desc:
            character_desc = random_character(mode, topic)
        if not env_desc:
            env_desc = random_env(mode, topic)

        kid_sys = _build_child_system_prompt_impl(
            mode, topic, character_desc, env_desc,
            count, age_group, art_style, ref_images,
            pick_story_sense_fn=self._pick_story_sense)
        kid_user = f"故事主题：{topic or '小动物的冒险'}\n"
        if character_desc:
            kid_user += f"角色描述：{character_desc}\n"
        kid_user += f"片段数/页数：{count}\n"
        if age_group:
            kid_user += f"年龄段：{age_group}\n"

        ai_result = _call_ai(kid_sys, kid_user) or ""

        if ai_result:
            header = (
                f"{mode}总纲\n"
                f"整体视觉风格：\n"
                f"画风采用{art_style}，适合{age_group}年龄段的孩子。色彩鲜明活泼，符合儿童的视觉偏好。\n"
                f"角色物品设定：\n"
                f"{(character_desc or '待定角色').replace(chr(10), ' ').rstrip()}\n"
                f"道具或武器：\n"
                f"待补充。\n"
                f"场景设定：\n"
                f"{env_desc or '待定场景'}\n"
                f"氛围与画质标准：\n"
                f"用孩子的语言讲故事，不说教。画面活泼有趣，色彩鲜明。角色的表情和动作夸张可爱，让小朋友看了想跟着学。\n"
                f"声音设定：\n"
                f"旁白和对话使用短句、拟声词、重复句式，适合儿童模仿跟读。\n"
                f"核心叙事设定：\n"
                f"共{count}个片段/页。用孩子能理解的节奏推进——先引起好奇，中间有小小的波折，最后开心收尾。每段只讲一个核心动作或情节，不复杂。\n"
            )
            return f"{header}\n\n{ai_result}"
        return ""

    # ============================================================
    # 专业设计模式处理
    # ============================================================
    def _process_design_mode(self, mode, topic, character_desc, env_desc, count,
                              style, color_tone, product_material, product_color,
                              shoot_angle, lighting_scheme, bg_type,
                              api_url, api_key, model_name, temperature, max_tokens,
                              ref_images, _call_ai):
        if not api_url:
            return ""

        if not topic:
            topic = random_topic(mode)
        if not character_desc:
            character_desc = random_character(mode, topic)
        if not env_desc:
            env_desc = random_env(mode, topic)

        design_sys = _build_design_system_prompt(
            mode, topic, character_desc, env_desc, count,
            style, color_tone, product_material, product_color,
            shoot_angle, lighting_scheme, bg_type, ref_images)
        design_global_ctx = _build_design_global_context(
            "专业设计", mode, topic, character_desc, env_desc, style, color_tone)
        design_user = _build_design_user_prompt(
            mode, topic, character_desc, env_desc, count,
            style, color_tone, product_material, product_color,
            shoot_angle, lighting_scheme, bg_type)

        ai_result = _call_ai(design_sys + design_global_ctx, design_user) or ""
        return ai_result


# ============================================================
# ComfyUI 节点注册 — V20.5
# ============================================================

class DirectorPromptPro:
    """导演级分镜批次输出节点 — 每次输出总纲+一个分镜，按镜头数批次输出"""
    
    @classmethod
    def INPUT_TYPES(cls):
        required = {
            "模式选择": (ALL_MODES, {"default": "关闭"}),
            "故事剧本": ("STRING", {"default": "", "multiline": True}),
            "角色描述": ("STRING", {"default": "", "multiline": True}),
            "环境背景描述": ("STRING", {"default": "", "multiline": True}),
            "输出数量": ("INT", {"default": 8, "min": 1, "max": 60, "step": 1}),
            "画面风格": (
                ["电影感", "古装风", "喜剧风", "言情风", "悬疑风", "科幻风",
                 "奇幻风", "武侠风", "宫廷风", "都市风", "民国风", "田园风",
                 "赛博风", "蒸汽朋克风", "末日废土风", "校园风", "职场风",
                 "家庭温情风", "史诗正剧风", "文艺叙事风", "黑色幽默风",
                 "实验先锋风", "纪录写实风", "神话史诗风"],
                {"default": "电影感"},
            ),
            "色彩基调": (
                ["自动", "暖色调", "冷色调", "高对比", "低饱和", "复古",
                 "赛博朋克", "日系清新", "黑白",
                 "温暖明亮", "清新淡雅", "梦幻柔和", "浓郁鲜艳"],
                {"default": "自动"},
            ),
            "API地址": ("STRING", {"default": "", "multiline": False}),
            "API密钥": ("STRING", {"default": "", "multiline": False}),
            "AI模型名": ("STRING", {"default": "", "multiline": False}),
            "AI推理温度": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 2.0, "step": 0.1}),
            "AI最大Token数": ("INT", {"default": 10000, "min": 256, "max": 100000, "step": 256}),
        }
        optional = {
            "景别偏好": (["自动-多种交替", "以远景为主", "以中景为主", "以近景/特写为主", "全特写"], {"default": "自动-多种交替"}),
            "运镜风格": (["自动", "稳重固定镜头", "流畅运动", "手持纪实", "炫酷动感",
                          "竖屏固定机位为主", "竖屏流畅运动"], {"default": "自动"}),
            # 绘本
            "绘本文字量": (["自动", "少字（每页10字以内）", "中等（每页20-40字）", "多字（每页50字以上）"], {"default": "自动"}),
            "绘本年龄段": (["0-3岁低幼", "3-6岁幼儿", "6-9岁学龄", "9-12岁少年"], {"default": "3-6岁幼儿"}),
            # 短剧
            "短剧节奏强度": (["自动", "舒缓铺垫", "紧凑推进", "高能密集"], {"default": "自动"}),
            # 儿童
            "儿童年龄段": (["0-3岁低幼", "3-6岁幼儿", "6-9岁学龄"], {"default": "3-6岁幼儿"}),
            "儿童画风": (["水彩插画", "卡通动画", "彩铅手绘", "黏土定格", "扁平矢量"], {"default": "卡通动画"}),
            # 设计
            "产品材质": ("STRING", {"default": "", "multiline": False}),
            "产品颜色": ("STRING", {"default": "", "multiline": False}),
            "拍摄角度": (["自动", "正面平视", "45度俯视", "顶部俯拍", "侧面特写",
                          "微距细节", "场景环绕", "多角度组图"], {"default": "自动"}),
            "布光方案": (["自动", "柔光箱主光+补光", "侧光+轮廓光", "逆光+正面补光",
                          "顶光+漫反射", "三点布光", "自然光", "硬光戏剧效果"], {"default": "自动"}),
            "背景类型": (["自动", "纯色背景", "渐变色背景", "纹理背景", "场景实景",
                          "悬浮展示", "模特穿戴", "创意道具"], {"default": "自动"}),
        }
        return {"required": required, "optional": optional}
    
    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("剧本模式批次分镜输出", "元数据JSON",)
    FUNCTION = "process"
    CATEGORY = "提示词工具"
    OUTPUT_NODE = True
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # [修复] 导演分镜节点每次执行都应产出新结果（调用LLM + 随机性）
        return _time.time()
    
    def __init__(self):
        self._cache_lock = threading.Lock()
        self._cache = {}
    
    def _pick_story_sense(self):
        PromptLibraryNodePro._ensure_story_sense()
        if PromptLibraryNodePro._story_sense_cache:
            return random.choice(PromptLibraryNodePro._story_sense_cache)
        return ""
    
    def process(self, **kwargs):
        """主处理入口"""
        模式选择 = kwargs.get("模式选择", "关闭")
        主题 = kwargs.get("故事剧本", "")
        角色描述 = kwargs.get("角色描述", "")
        环境背景描述 = kwargs.get("环境背景描述", "")
        输出数量 = kwargs.get("输出数量", 8)
        画面风格 = kwargs.get("画面风格", "电影感")
        色彩基调 = kwargs.get("色彩基调", "自动")
        景别偏好 = kwargs.get("景别偏好", "自动-多种交替")
        运镜风格 = kwargs.get("运镜风格", "自动")
        API地址 = kwargs.get("API地址", "")
        API密钥 = kwargs.get("API密钥", "")
        AI模型名 = kwargs.get("AI模型名", "")
        AI推理温度 = kwargs.get("AI推理温度", 0.8)
        AI最大Token数 = kwargs.get("AI最大Token数", 10000)
        
        if not API地址:
            return ("请先配置API地址", json.dumps({"error": "API未配置"}, ensure_ascii=False))
        
        batch_output = ""
        meta = {"mode": 模式选择, "shots": 输出数量}
        
        from director_pro import (
            process_storyboard_batched,
            process_picture_book_batched,
            process_short_drama_batched,
            process_child_batched,
            process_design_batched,
        )
        
        if 模式选择 in MODE_CATEGORIES_STORYBOARD:
            batch_output = process_storyboard_batched(
                模式选择, 主题, 角色描述, 环境背景描述,
                输出数量, 画面风格, 色彩基调, 景别偏好, 运镜风格,
                API地址, API密钥, AI模型名, AI推理温度, AI最大Token数,
                [], pick_story_sense_fn=self._pick_story_sense,
            )
            meta["type"] = "故事板批次"
        elif 模式选择 == "绘本模式":
            batch_output = process_picture_book_batched(
                主题, 角色描述, 环境背景描述, 输出数量,
                画面风格, 色彩基调, kwargs.get("绘本文字量", "自动"), kwargs.get("绘本年龄段", "3-6岁幼儿"),
                API地址, API密钥, AI模型名, AI推理温度, AI最大Token数,
                [], pick_story_sense_fn=self._pick_story_sense,
            )
            meta["type"] = "绘本批次"
        elif 模式选择 == "短剧模式":
            batch_output = process_short_drama_batched(
                主题, 角色描述, 环境背景描述, 输出数量,
                画面风格, kwargs.get("短剧节奏强度", "自动"), 运镜风格, 色彩基调,
                API地址, API密钥, AI模型名, AI推理温度, AI最大Token数,
                [], pick_story_sense_fn=self._pick_story_sense,
            )
            meta["type"] = "短剧批次"
        elif 模式选择 in MODE_CATEGORIES_CHILD:
            batch_output = process_child_batched(
                模式选择, 主题, 角色描述, 环境背景描述, 输出数量,
                kwargs.get("儿童年龄段", "3-6岁幼儿"), kwargs.get("儿童画风", "卡通动画"),
                API地址, API密钥, AI模型名, AI推理温度, AI最大Token数,
                [], pick_story_sense_fn=self._pick_story_sense,
            )
            meta["type"] = "儿童批次"
        elif 模式选择 in MODE_CATEGORIES_DESIGN:
            if _HAS_DESIGN_MODE:
                batch_output = process_design_batched(
                    模式选择, 主题, 角色描述, 环境背景描述, 输出数量, 画面风格, 色彩基调,
                    kwargs.get("产品材质", ""), kwargs.get("产品颜色", ""),
                    kwargs.get("拍摄角度", "自动"), kwargs.get("布光方案", "自动"), kwargs.get("背景类型", "自动"),
                    API地址, API密钥, AI模型名, AI推理温度, AI最大Token数,
                    [], pick_story_sense_fn=self._pick_story_sense,
                )
                meta["type"] = "设计批次"
            else:
                batch_output = f"[提示] 设计模式「{模式选择}」需要安装 modes_design 模块才能使用。"
                meta["type"] = "设计(模块缺失)"
        else:
            batch_output = f"DirectorPromptPro暂不支持{模式选择}模式"
            meta["type"] = "不支持"
        
        return (batch_output or "", json.dumps(meta, ensure_ascii=False))


NODE_CLASS_MAPPINGS = {
    "PromptLibraryNodePro": PromptLibraryNodePro,
    "DirectorPromptPro": DirectorPromptPro,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptLibraryNodePro": "提示词库节点 Pro V20.5",
    "DirectorPromptPro": "导演分镜批次输出 V1.0",
}
