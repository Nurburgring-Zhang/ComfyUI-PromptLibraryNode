# ============================================================
# PromptLibraryNode V20.5 — 全能创作节点（定制版）
# ============================================================
# V20.5 核心变更（2026-05-29）：
#   1. 故事板模式：铁律从九条→十二条，增加变化五维度明细、风格统一、对话框绑定角色
#   2. 绘本模式：输出维度从5个→7个，增加构图与景别说明；创作原则从十项→十五项
#   3. 短剧模式：铁律从九条→十二条，增加变化五维度、时空连续性、风格统一规则
#   4. 儿童视频格式一：变化标注从一句话→五维度逐项，增加对话框绑定+页面衔接
#   5. 儿童视频格式二：增加变化追踪、对话框绑定、通用约束
#   6. 儿童微动视频/GIF：增加变化标注字段、对话框绑定、通用约束
#   7. 儿童绘本格式：增加时空锚定、变化标注五维度、对话框绑定、页面衔接
#   8. 融入儿童绘本规则(1).txt中全部六类定制规则和通用约束体系

import os
import random
import re
import json
import hashlib
import math
import time as _time
import urllib.request
import threading
import io
import base64
from pathlib import Path
from datetime import datetime

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

OUTPUT_NAMES = ("提示词", "绘本提示词", "短剧提示词", "故事提示词", "负面提示词", "儿童提示词")
OUTPUT_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")

WEB_DIRECTORY = "./web"


# ============================================================
# 主节点类
# ============================================================
class PromptLibraryNodePro:
    """提示词库节点 V19.0 — 全能创作节点（定制版）"""
    _instance_lock = threading.Lock()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # ======== 最上方：传统提示词库 ========
                "文件夹路径": ("STRING", {"default": "", "multiline": False}),
                "读取模式": (["随机抽取", "顺序循环", "洗牌遍历", "权重随机"], {"default": "随机抽取"}),
                "循环模式": (["无限循环", "读完停止", "历史不重复(50条)"], {"default": "无限循环"}),
                "输出数量": ("INT", {"default": 1, "min": 1, "max": 50, "step": 1}),
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
                # ======== AI设置（翻译功能下方） ========
                "API地址": ("STRING", {"default": "http://localhost:1234/v1/chat/completions", "multiline": False}),
                "API密钥": ("STRING", {"default": "", "multiline": False}),
                "AI模型名": ("STRING", {"default": "", "multiline": False}),
                "AI推理温度": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 2.0, "step": 0.1}),
                "AI最大Token数": ("INT", {"default": 10000, "min": 256, "max": 100000, "step": 256}),
                # ======== 载入参考图（AI下方） ========
                "参考图列表": ("STRING", {"default": "[]", "multiline": True}),
                # ======== 基础设定区（参考图下方） ========
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
                # ======== 模式专属参数 ========
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
    RETURN_NAMES = ("提示词", "模式输出", "负面提示词", "元数据JSON", "回调图片",)
    FUNCTION = "get_prompt"
    CATEGORY = "提示词工具"
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return _time.time()

    def __init__(self):
        self._cache_lock = threading.Lock()
        self._cache = {}
        self._last_ai_error = ""

    # ============================================================
    # 故事感总纲随机抽取
    # ============================================================
    def _pick_story_sense(self):
        """从故事感总纲文库中随机抽取一个"""
        import random as _random
        library_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "story_sense_library_complete.md")
        try:
            with open(library_path, "r", encoding="utf-8") as f:
                content = f.read()
            items = content.split("【故事感总纲")
            items = [item for item in items if item.strip() and not item.startswith("#") and "文库" not in item[:20]]
            if items:
                chosen = _random.choice(items)
                return "【故事感总纲" + chosen.strip()
            return ""
        except Exception:
            return ""

    # ============================================================
    # 主入口
    # ============================================================
    def get_prompt(self, **kwargs):
        """主处理入口 - 从kwargs解包参数，按模式分派"""
        start_time = datetime.now()

        # 直接提取参数
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

        # 参考图（从"参考图列表"字符串中解析文件路径，加载图片）
        ref_image_files = self._parse_ref_image_list(kwargs.get("参考图列表", "[]"))
        ref_image_tensors = self._load_ref_image_tensors(ref_image_files)

        # 种子
        固定种子_0为真随机 = kwargs.get("固定种子_0为真随机", 0)
        if 固定种子_0为真随机 and 固定种子_0为真随机 > 0:
            random.seed(固定种子_0为真随机)

        # 初始化输出
        final_prompt = ""      # 主输出：提示词/AI生成/设计模式
        mode_output = ""       # 模式输出：所有模式详细内容
        negative_prompt = ""   # 负面提示词
        meta_json = {}         # 元数据

        # ====== 按模式分派 ======
        if 模式选择 == "关闭":
            final_prompt, negative_prompt = self._process_traditional_mode(kwargs)
            meta_json = {"mode": "关闭"}
        elif 模式选择 in MODE_CATEGORIES_STORYBOARD:
            mode_output = self._process_storyboard_mode(
                模式选择, 主题, 角色描述, 环境背景描述,
                总页数, 画面风格, 色彩基调, 景别偏好, 运镜风格,
                API地址, API密钥, AI模型名, AI推理温度, AI最大Token数, ref_image_tensors)
            meta_json = {"mode": 模式选择, "type": "故事板", "shots": 总页数}
        elif 模式选择 == "绘本模式":
            mode_output = self._process_picture_book_mode(
                主题, 角色描述, 环境背景描述, 总页数,
                画面风格, 色彩基调, kwargs.get("绘本文字量", "自动"), kwargs.get("绘本年龄段", "3-6岁幼儿"),
                API地址, API密钥, AI模型名, AI推理温度, AI最大Token数, ref_image_tensors)
            meta_json = {"mode": "绘本模式", "type": "绘本", "pages": 总页数}
        elif 模式选择 == "短剧模式":
            mode_output = self._process_short_drama_mode(
                主题, 角色描述, 环境背景描述, 总页数,
                画面风格, kwargs.get("短剧节奏强度", "自动"), 运镜风格, 色彩基调,
                API地址, API密钥, AI模型名, AI推理温度, AI最大Token数, ref_image_tensors)
            meta_json = {"mode": "短剧模式", "type": "短剧", "shots": 总页数}
        elif 模式选择 in MODE_CATEGORIES_CHILD:
            mode_output = self._process_child_mode(
                模式选择, 主题, 角色描述, 环境背景描述, 总页数,
                kwargs.get("儿童年龄段", "3-6岁幼儿"), kwargs.get("儿童画风", "卡通动画"),
                API地址, API密钥, AI模型名, AI推理温度, AI最大Token数, ref_image_tensors)
            meta_json = {"mode": 模式选择, "type": "儿童内容"}
        elif 模式选择 in MODE_CATEGORIES_DESIGN:
            mode_output = self._process_design_mode(
                模式选择, 主题, 角色描述, 环境背景描述, 总页数, 画面风格, 色彩基调,
                kwargs.get("产品材质", ""), kwargs.get("产品颜色", ""),
                kwargs.get("拍摄角度", "自动"), kwargs.get("布光方案", "自动"), kwargs.get("背景类型", "自动"),
                API地址, API密钥, AI模型名, AI推理温度, AI最大Token数, ref_image_tensors)
            meta_json = {"mode": 模式选择, "type": "专业设计"}

        # 负面词
        启用负面词生成 = kwargs.get("启用负面词生成", False)
        负面词自定义 = kwargs.get("负面词自定义", "")
        if 启用负面词生成:
            main_content = final_prompt or mode_output or ""
            negative_prompt = self._generate_negative_prompt(负面词自定义, main_content)

        # 回调图片（输出所有参考图，按1~9顺序打包成batch tensor）
        callback_image = None
        if ref_image_tensors:
            callback_image = torch.cat(ref_image_tensors, dim=0)  # (N, H, W, C)

        # 构建返回结果
        result_tuple = (final_prompt, mode_output, negative_prompt, json.dumps(meta_json, ensure_ascii=False), callback_image)
        return result_tuple

    # ============================================================
    # 参考图：从"参考图列表"JSON解析文件路径并加载为tensor
    # JS上传后存储文件信息到"参考图列表"widget
    # ============================================================
    def _parse_ref_image_list(self, ref_list_str):
        """解析参考图列表JSON字符串，返回文件信息列表"""
        if not ref_list_str or ref_list_str.strip() in ("", "[]"):
            return []
        try:
            items = json.loads(ref_list_str)
            if not isinstance(items, list):
                return []
            # 验证每个条目
            valid = []
            for item in items:
                if isinstance(item, dict) and "filename" in item:
                    valid.append(item)
                    if len(valid) >= 9:
                        break
            return valid
        except (json.JSONDecodeError, TypeError):
            return []

    def _load_ref_image_tensors(self, file_items):
        """从文件信息列表加载图片为IMAGE tensor，并过滤>4096的"""
        if not file_items:
            return []
        tensors = []
        try:
            import folder_paths
            import numpy as np
            from PIL import Image

            for item in file_items:
                try:
                    filename = item.get("filename", "")
                    subfolder = item.get("subfolder", "")
                    img_type = item.get("type", "input")
                    # 查找文件路径
                    img_path = folder_paths.get_annotated_filepath(f"{filename} [input]")
                    if not os.path.isfile(img_path):
                        # 尝试在input目录查找
                        input_dir = folder_paths.get_input_directory()
                        img_path = os.path.join(input_dir, filename)
                        if not os.path.isfile(img_path):
                            continue

                    pil_img = Image.open(img_path).convert("RGB")
                    w, h = pil_img.size
                    if w > 4096 or h > 4096:
                        continue  # 过滤超尺寸

                    img_np = np.array(pil_img).astype(np.float32) / 255.0
                    img_tensor = torch.from_numpy(img_np)[None,]  # (1, H, W, C)
                    tensors.append(img_tensor)
                    if len(tensors) >= 9:
                        break
                except Exception:
                    continue
        except Exception:
            pass
        return tensors

    # ============================================================
    # 传统模式（提示词库/AI生成/润色/翻译）
    # ============================================================
    def _process_traditional_mode(self, kwargs):
        final_prompt = ""
        开启AI生成 = kwargs.get("开启AI生成", False)
        开启AI润色 = kwargs.get("开启AI润色", False)
        开启翻译 = kwargs.get("开启翻译", False)
        启用主体过滤 = kwargs.get("启用主体过滤", True)
        批量AI生成数 = kwargs.get("批量AI生成数", 1)
        固定种子_0为真随机 = kwargs.get("固定种子_0为真随机", 0)
        API地址 = kwargs.get("API地址", "")
        API密钥 = kwargs.get("API密钥", "")
        AI模型名 = kwargs.get("AI模型名", "")
        AI推理温度 = kwargs.get("AI推理温度", 0.8)
        AI最大Token数 = kwargs.get("AI最大Token数", 10000)

        if 开启AI生成:
            keywords = self._parse_keywords(kwargs.get("关键词筛选", ""))
            sys_p = kwargs.get("AI生成系统提示词", "") or "你是一个专业AI绘画prompt生成器。生成一条完整英文prompt，直接输出。"
            user_msg = "请生成一条高质量AI绘画prompt"
            if keywords:
                user_msg = f"请根据以下关键词生成一条高质量AI绘画prompt：{', '.join(keywords)}"
            ai_result = self._call_ai(API地址, API密钥, AI模型名, sys_p, user_msg, AI推理温度, AI最大Token数)
            if ai_result:
                final_prompt = ai_result

        文件夹路径 = kwargs.get("文件夹路径", "")
        if 文件夹路径:
            folder_path = os.path.abspath(文件夹路径)
            if not os.path.isdir(folder_path):
                return ("", "")  # 返回空字符串，不是嵌套元组
            关键词筛选 = kwargs.get("关键词筛选", "")
            标签筛选 = kwargs.get("标签筛选", "")
            读取模式 = kwargs.get("读取模式", "随机抽取")
            循环模式 = kwargs.get("循环模式", "无限循环")
            输出数量 = kwargs.get("输出数量", 1)
            keywords = self._parse_keywords(关键词筛选)
            wanted_tags = self._parse_tags(标签筛选)
            files = self._scan_files(folder_path)
            if not files:
                return ("", "")
            if wanted_tags:
                matched_files = [f for f in files if self._file_has_tag(f, wanted_tags)]
                if not matched_files:
                    return ("", "")
                files = matched_files
            all_lines = self._load_lines(files, keywords)
            if not all_lines:
                return ("", "")
            smart_filtered = self._smart_filter(all_lines)
            if smart_filtered is not None:
                all_lines = smart_filtered
                if not all_lines:
                    return ("", "")
            if 启用主体过滤:
                subject_filtered = self._filter_by_subject(all_lines)
                if not subject_filtered:
                    return ("", "")
                all_lines = subject_filtered
            chosen = self._pick_n_lines(all_lines, 读取模式, 循环模式, 输出数量, folder_path)
            if not chosen:
                return ("", "")
            if "不重复" in 循环模式:
                chosen = self._history_dedup(chosen, folder_path)
                if not chosen:
                    chosen = [random.choice(all_lines)]
            result_texts = [l["text"] for l in chosen]
            final_prompt = result_texts[0] if result_texts else ""

        if 开启AI润色 and final_prompt:
            sys_p = kwargs.get("AI润色系统提示词", "") or "将用户输入的prompt润色为高质量英文prompt。直接输出结果。"
            ai_result = self._call_ai(API地址, API密钥, AI模型名, sys_p, final_prompt, AI推理温度, AI最大Token数)
            if ai_result:
                final_prompt = ai_result

        if 开启AI生成 and final_prompt and 批量AI生成数 > 1:
            batch_results = [final_prompt]
            for b in range(批量AI生成数 - 1):
                b_seed = (固定种子_0为真随机 if 固定种子_0为真随机 > 0 else int(_time.time())) + b + 1
                random.seed(b_seed)
                kw = self._parse_keywords(kwargs.get("关键词筛选", ""))
                user_msg = "请生成一条高质量AI绘画prompt"
                if kw:
                    user_msg = f"请根据以下关键词生成一条高质量AI绘画prompt：{', '.join(kw)}"
                b_ret = self._call_ai(API地址, API密钥, AI模型名,
                    kwargs.get("AI生成系统提示词", "") or "你是一个专业AI绘画prompt生成器",
                    user_msg, AI推理温度, AI最大Token数)
                if b_ret:
                    batch_results.append(b_ret)
            final_prompt = batch_results[0] if batch_results else ""

        if 开启翻译 and final_prompt and API地址:
            translated = self._translate_prompt(final_prompt, kwargs.get("翻译方向", "中译英"),
                API地址, API密钥, AI模型名, AI推理温度, AI最大Token数)
            if translated:
                final_prompt = translated

        return final_prompt, ""

    # ============================================================
    # 随机内容生成 — 当用户没填写时，根据模板类型自动生成匹配的信息
    # ============================================================
    def _random_topic(self, mode):
        """根据模板类型随机生成主题"""
        pools = {
            "电影分镜": ["末日前最后一班地铁", "雨夜的便利店抢劫", "废弃游乐园里的老人", "天台上的谈判", "深夜食堂的最后一位客人"],
            "广告故事板": ["一款重新定义饮水的杯子", "可以穿100年的帆布鞋", "会呼吸的床垫", "能折叠进钱包的雨衣", "改变睡眠方式的光疗灯"],
            "动画故事板": ["会飞的小猪找云朵", "一只想当厨师的长颈鹿", "月亮掉进池塘里", "会说话的路灯", "迷路的星星找家"],
            "漫画分镜": ["转学生是个忍者", "学校天台上的秘密基地", "会说话的猫咪侦探", "时间停止的图书馆", "影子被偷走的那天"],
            "MV故事板": ["失恋后的第一场雪", "夏日海边的告别", "凌晨三点的便利店", "末班车的相遇", "一个人的毕业旅行"],
            "教程步骤": ["如何用手机拍出专业级美食照片", "三分钟学会系蝴蝶结领带", "新手也能做的手冲咖啡", "手机剪辑入门：剪出电影感", "十分钟整理出极简书桌"],
            "短视频分镜": ["一百元在城市里活三天", "和陌生人交换礼物", "挑战24小时不说一句话", "给十年前自己打个电话", "在办公室偷偷做了一顿饭"],
            "品牌故事板": ["一个坚持用手工造纸的文具品牌", "传承四代的酱油酿造坊", "用回收渔网做运动鞋的品牌", "开在雪山脚下的书店", "只卖一本书的移动书店"],
            "剧情分镜": ["父亲的第二次婚礼", "多年后重逢的初恋", "辞职去旅行的决定", "给失忆母亲念日记", "最后一个离开故乡的人"],
            "绘本模式": ["迷路的小云朵找妈妈", "不肯睡觉的小熊", "会变颜色的蜗牛", "森林里的声音晚会", "一颗种子的旅行"],
            "短剧模式": ["被分手后我嫁给了千亿总裁", "重生之我在古代当厨神", "穿越回八十年代当富婆", "一不小心捡到了上司的手机", "前夫跪求我复婚"],
            "儿童视频格式一": ["小猫咪学游泳", "会飞的气球找朋友", "彩虹桥的另一边", "森林里的捉迷藏", "小刺猬的苹果"],
            "儿童视频格式二": ["小兔子借尾巴", "不爱刷牙的小老虎", "小鸭子找妈妈", "爱发脾气的小云朵", "想变大的小蚂蚁"],
            "儿童微动视频/GIF": ["摇摆的小企鹅", "打哈欠的小猫", "转圈圈的落叶", "跳出水面的小鱼", "眨眼睛的星星"],
            "儿童绘本格式": ["小蝌蚪找妈妈", "好饿的毛毛虫", "小种子长大了", "月亮是什么味道", "谁的脚印"],
            "室内设计": ["极简主义客厅改造", "日式原木风卧室设计", "轻奢风小户型公寓", "工业风 loft 办公空间", "北欧风儿童房"],
            "产品摄影": ["一款全手工制作的陶瓷茶杯", "极简设计的无线耳机", "复古皮革背包", "冷锻不锈钢厨刀", "手工真皮钱包"],
            "UI界面设计": ["健康管理类App主页", "在线教育平台课程详情页", "音乐播放器播放界面", "智能家居控制面板", "旅游预订App首页"],
            "LOGO/IP形象设计": ["一家手工咖啡店的品牌LOGO", "宠物用品品牌的吉祥物", "环保科技公司的图标", "儿童教育品牌的IP形象", "户外运动品牌标识"],
            "海报设计": ["独立书店的周年庆海报", "环保主题公益海报", "新中式茶饮品牌主视觉", "独立音乐人巡演海报", "设计展览开幕海报"],
            "AI生成摄影": ["城市雨夜街拍", "极简主义静物摄影", "情绪人像摄影", "美食杂志风格摄影", "旅行纪实风格"],
            "电商/包装设计": ["有机茶饮系列包装", "护肤品极简包装", "精酿啤酒标签设计", "手工巧克力礼盒", "香薰蜡烛包装"],
        }
        pool = pools.get(mode, ["一次意外的相遇", "一个重要的决定", "一场特别的旅行", "一次难忘的对话", "一个改变命运的瞬间"])
        return random.choice(pool)

    def _random_character(self, mode, topic=""):
        """根据模板类型随机生成角色描述"""
        pools = {
            "电影分镜": ["中年警探，灰白鬓角，旧风衣，眼神疲惫但锐利", "年轻女画家，素色长裙，手指沾满颜料，神情专注",
                         "退休教师，花白头发，老花镜挂在胸前，说话慢条斯理", "外卖骑手，晒黑的肤色，旧电瓶车，头盔下藏着故事",
                         "独自旅行的大学生，背包旧了，眼神里有好奇也有戒备"],
            "广告故事板": ["都市白领女性，30岁左右，干练短发，追求生活品质", "年轻创业者，25岁，T恤牛仔裤，充满干劲",
                         "家庭主妇，40岁，温柔细致，注重家人健康", "户外运动爱好者，35岁，小麦色皮肤，热爱自然"],
            "动画故事板": ["一只橙色小猫，戴着蓝色小围巾，眼睛圆溜溜的", "一头紫色小象，耳朵特别大，走路总被绊倒",
                         "一颗会发光的小星星，胆子很小，躲在云后面", "一只蓝色小企鹅，围巾是妈妈织的，想去南方看看"],
            "漫画分镜": ["高中生，校服领带总是歪的，书包挂着奇怪挂件", "神秘转校生，黑色制服，总戴耳机不说话",
                         "咖啡店老板，30岁，爱讲冷笑话，有一只会说话的鹦鹉"],
            "MV故事板": ["失恋的吉他手，在房间里对着窗户弹琴", "即将离开城市的女孩，在屋顶看日落",
                         "在深夜便利店值夜班的男孩，有一双会说话的眼睛"],
            "短视频分镜": ["搞笑博主，表情丰富，肢体夸张", "美食达人，手很巧，嘴很挑",
                         "旅行者，背着一台旧相机，走哪拍哪"],
            "品牌故事板": ["手工匠人，六十岁，布满老茧的双手，专注的眼神", "年轻设计师，海归，想把传统工艺现代化",
                         "第四代传人，三十岁，接手家族老店，想做些改变"],
            "剧情分镜": ["单亲爸爸，四十岁，开一间小面馆，女儿刚上大学", "从大城市回乡的青年，不适应慢节奏的生活",
                         "退休护士，七十岁，每天去医院做义工"],
            "绘本模式": ["一只毛茸茸的小熊，总是揉着眼睛说睡不着", "一朵软绵绵的小云朵，胆子很小，总跟着妈妈",
                         "一只彩色的小蜗牛，背着彩虹壳，走路慢悠悠", "一颗小种子，躺在泥土里，好奇外面的世界"],
            "短剧模式": ["被分手后决心逆袭的普通女孩，25岁，素颜也好看", "重生到古代的现代女厨师，会做各种现代美食",
                         "穿越回八十年代的女强人，靠摆摊发家致富", "职场小白，25岁，不小心捡到冷酷总裁的手机"],
            "儿童视频格式一": ["橙色小猫咪，戴着小水帽，想学游泳又怕水", "红色气球，系着小绳子，想去天上看看",
                         "绿色小刺猬，背着一颗红苹果，走路摇摇晃晃"],
            "儿童视频格式二": ["短尾巴的小兔子，想借一条长尾巴", "不爱刷牙的小老虎，牙齿黄黄的",
                         "毛茸茸的小鸭子，跟在妈妈后面一摇一摆"],
            "儿童微动视频/GIF": ["胖乎乎的小企鹅，走路左摇右摆", "圆滚滚的小猫，蜷成一团打哈欠",
                         "金色的小鱼，时不时跃出水面"],
            "儿童绘本格式": ["圆圆的月亮挂在夜空，散发着温柔的银光", "绿色的小叶子，从树枝上探出头来看世界",
                         "长长的梯子架在树上，一个小男孩正往上爬"],
            "室内设计": ["追求极简生活方式的年轻夫妇，30岁出头，热爱干净利落的线条", "喜欢日式美学的程序员，35岁，家里原木和白色为主",
                         "创业中的独立女性，28岁，希望家也能体现品味", "艺术策展人，40岁，偏爱工业风的粗犷质感"],
            "产品摄影": ["手工陶瓷匠人，专注器形的曲线和质感", "独立设计师品牌创始人，对材质和细节极其严苛",
                         "复古爱好者，收藏各种皮具和五金件"],
            "UI界面设计": ["活跃的健身爱好者，25岁，想用App记录每天的变化", "在线教育平台的设计师，关注学习体验",
                         "音乐发烧友，对播放器界面有独到见解"],
            "LOGO/IP形象设计": ["独立咖啡店主理人，想让小店有独特的品牌气质", "宠物用品品牌创始人，家里养了三只猫一条狗",
                         "环保科技公司CEO，希望LOGO传递绿色和未来感"],
            "海报设计": ["独立书店店主，爱读书也爱设计", "NGO组织的项目负责人，想用视觉传递环保理念",
                         "新中式茶饮品牌主理人，想做出有东方美学的视觉"],
            "AI生成摄影": ["深夜在街头晃悠的摄影师，喜欢雨天的倒影", "静物摄影师，享受在自然光下捕捉质感",
                         "情绪人像摄影师，善于捕捉不经意的瞬间"],
            "电商/包装设计": ["有機茶饮品牌的创办人，想让包装也传递自然的味道", "独立护肤品牌创始人，极简主义爱好者",
                         "手工巧克力师，靠颜值和味道双打动人"],
        }
        pool = pools.get(mode, ["一位有故事的普通人，外表平凡但眼神里有不平凡的经历"])
        return random.choice(pool)

    def _random_env(self, mode, topic=""):
        """根据模板类型随机生成环境背景"""
        pools = {
            "电影分镜": ["深夜的城市，霓虹灯在雨天的路面上倒映成碎片", "废弃的工厂车间，铁锈味混着灰尘的气息",
                         "老旧小区的天台，晾晒的床单在风中飘动", "凌晨的便利店，荧光灯嗡嗡作响，只有收银员和一个客人",
                         "雨后的公园长椅，湿漉漉的，落叶铺了一地"],
            "广告故事板": ["极简风格的起居室，落地窗外是城市天际线", "阳光充足的开放式厨房，原木色的台面上摆着新鲜食材",
                         "户外露营地，星空下燃着篝火", "早晨的浴室，热水蒸汽弥漫在镜面上"],
            "动画故事板": ["彩虹色的森林，蘑菇会发光，小溪流淌着星光", "云朵上的小镇，房子是用棉花糖做的",
                         "海底的游乐园，水母当灯光，珊瑚做滑梯", "星星之间的游乐园，月亮是个大秋千"],
            "漫画分镜": ["普通高中的天台上，画满了涂鸦", "老街拐角的旧书店，书架高到天花板",
                         "午后的教室，阳光透过窗帘洒在课桌上，粉笔灰在光线里飘"],
            "MV故事板": ["黄昏的海边，退潮后的沙滩上留下贝壳和脚印", "空无一人的画廊，只有一幅画还亮着灯",
                         "初雪的城市街头，路灯把雪花照得像星星"],
            "短视频分镜": ["家里的厨房，灯光温暖，锅铲碰撞的声音很治愈", "城市街角，人来人往中找到一个安静的拍摄位",
                         "路边摊，烟火气十足，老板和熟客在聊天"],
            "品牌故事板": ["古镇里的老作坊，木头和纸张的气味混合在一起", "城市角落里的手工作坊，窗外是高楼大厦",
                         "雪山脚下的木屋，壁炉里火烧得正旺"],
            "剧情分镜": ["小城市的旧街道，梧桐树遮住了大半个天空", "医院走廊里，长椅上坐着各种各样的人",
                         "火车站候车室，每个人都有自己的目的地"],
            "绘本模式": ["晚上的森林里，萤火虫飞来飞去，月光洒在树叶上", "软软的云朵上面，有一座小房子",
                         "春天的花园里，花朵刚刚开放，蜜蜂嗡嗡地飞", "安静的泥土下面，小种子在黑暗中等待"],
            "短剧模式": ["繁华都市的高档写字楼，落地窗外霓虹闪烁", "古色古香的古代庭院，假山流水，雕花窗棂",
                         "八十年代的小城街头，自行车铃声此起彼伏", "现代都市的咖啡馆，暖黄的灯光，舒缓的音乐"],
            "儿童视频格式一": ["阳光明媚的小池塘边，水面上开着荷花", "蓝蓝的天空上，飘着几朵白云，小鸟在飞",
                         "绿油油的草地上，开满了五颜六色的小花"],
            "儿童视频格式二": ["大森林里，阳光透过树叶洒下斑驳的光影", "小河边，河水哗啦啦地流，小鱼在水里游",
                         "春天的草地上，蝴蝶在花丛中飞来飞去"],
            "儿童微动视频/GIF": ["南极的冰面上，白茫茫一片，远处有冰山", "温暖的小窝里，阳光洒进来，暖洋洋的",
                         "清澈的小池塘里，水面上泛起一圈圈涟漪"],
            "儿童绘本格式": ["深蓝色的夜空中，星星一闪一闪，月亮弯弯的", "春天的树枝上，嫩绿的新芽刚刚冒出来",
                         "一棵大树下，阳光透过树叶的缝隙洒下来"],
            "室内设计": ["高层公寓的客厅，落地窗外是城市天际线", "老小区改造中的毛坯房，阳光从南面洒进来",
                         "坐落在创意园区的loft空间，水泥柱子和红砖墙", "精装交付的样板间，白色墙面和木地板"],
            "产品摄影": ["极简摄影棚，柔光灯箱打出的干净背景", "阳光充足的木质桌面上，铺着手工亚麻布",
                         "暗色调的摄影棚，只有一束锥形光从上方打下"],
            "UI界面设计": ["健康管理App的界面设计稿，展示着今日运动数据", "在线教育平台的课程详情页，展示着高互动性的学习体验",
                         "音乐播放器的深色模式界面，封面图占视觉主导"],
            "LOGO/IP形象设计": ["手工咖啡店的门头设计草图，旁边摆着咖啡杯", "宠物品牌设计工作室，墙上贴满了动物形象草图",
                         "环保科技公司的白色会议室，白板上画着品牌方案"],
            "海报设计": ["独立书店的复古木门和橱窗，玻璃上反射着树叶的影子", "环保主题展览的白色展厅，墙面等待被填满",
                         "新中式茶饮店的门店装修，原木和青砖的质感"],
            "AI生成摄影": ["雨夜的斑马线，红绿灯倒影在水面上", "大理石台面上摆着一个白色陶瓷盘，侧光打下柔和的阴影",
                         "咖啡馆靠窗的位置，阳光透过百叶窗留下条纹光影"],
            "电商/包装设计": ["有機茶饮的包装打样室，各种材质的样品排列在桌上", "极简风格的设计工作室，墙面上展示着在做的包装方案",
                         "巧克力工坊的包装台，旁边摆着刚做好的样品"],
        }
        pool = pools.get(mode, ["一个有故事的地方，时光在这里留下了痕迹"])
        return random.choice(pool)
    def _error_result(self, msg, err_code="", count=0):
        return (msg, "", "", "", None)

    # ============================================================
    # 故事板模式处理（9种）
    # ============================================================
    def _process_storyboard_mode(self, mode, topic, character_desc, env_desc,
                                  shot_count, style, color_tone, preferred_shot, camera_style,
                                  api_url, api_key, model_name, temperature, max_tokens, ref_images):
        """处理故事板模式 - 9种子模式"""
        if not api_url:
            return ""

        # 用户没填信息时随机生成，确保所有信息相互匹配
        if not topic:
            topic = self._random_topic(mode)
        if not character_desc:
            character_desc = self._random_character(mode, topic)
        if not env_desc:
            env_desc = self._random_env(mode, topic)

        sys_p = self._build_storyboard_system_prompt(mode, style, topic, character_desc, env_desc, ref_images)
        user_prompt = self._build_storyboard_user_prompt(
            mode, topic, character_desc, shot_count, style,
            color_tone, preferred_shot, camera_style, env_desc
        )

        # 故事板专属总纲：五维设定展开
        storyboard_header = (
            f"{mode}总纲\n"
            f"整体视觉风格：\n"
            f"整体风格为{style}，色彩基调偏向{color_tone}。\n"
            f"角色物品设定：\n"
            f"{(character_desc or '待定角色').replace(chr(10), chr(10)).rstrip()}\n"
            f"道具或武器：\n"
            f"待补充。\n"
            f"场景设定：\n"
            f"{(env_desc or '待定场景').rstrip()}\n"
            f"氛围与画质标准：\n"
            f"{mode}风格叙事，景别以{preferred_shot}为主，运镜采用{camera_style}的方式。镜头语言注重叙事节奏和情绪表达，禁止使用抽象情绪词，用具体可见的画面传递情感。\n"
            f"声音设定：\n"
            f"根据场景氛围搭配环境音效和配乐。\n"
            f"核心叙事设定：\n"
            f"共{shot_count}个镜头，围绕主题展开，镜头之间要有因果推进关系，节奏上注意松紧交替。每个镜头用饱满的画面描写，让读者能清晰想象出画面。\n"
        )

        ai_result = self._call_ai(api_url, api_key, model_name, sys_p, user_prompt, temperature, max_tokens)
        if not ai_result:
            return ""

        return f"{storyboard_header}\n\n{ai_result}"

    # ============================================================
    # 绘本模式处理
    # ============================================================
    def _process_picture_book_mode(self, topic, character_desc, env_desc, pages,
                                    style, color_tone, text_amount, age_group,
                                    api_url, api_key, model_name, temperature, max_tokens, ref_images):
        if not api_url:
            return ""

        if not topic:
            topic = self._random_topic("绘本模式")
        if not character_desc:
            character_desc = self._random_character("绘本模式", topic)
        if not env_desc:
            env_desc = self._random_env("绘本模式", topic)

        book_sys = self._build_picture_book_system_prompt(topic, character_desc, env_desc, pages,
                                                           style, color_tone, text_amount, age_group, ref_images)
        book_user = self._build_picture_book_user_prompt(topic, pages, style, color_tone, text_amount, age_group)

        ai_result = self._call_ai(api_url, api_key, model_name, book_sys, book_user, temperature, max_tokens) or ""

        if ai_result:
            header = (
                f"绘本总纲\n"
                f"整体视觉风格：\n"
                f"风格偏向{style}，整体色调为{color_tone}，适合{age_group}年龄段。\n"
                f"角色物品设定：\n"
                f"{(character_desc or '待定角色').replace(chr(10), chr(10)).rstrip()}\n"
                f"道具或武器：\n"
                f"待补充。\n"
                f"场景设定：\n"
                f"{env_desc or '待定场景'}\n"
                f"氛围与画质标准：\n"
                f"用孩子的视角看世界。不说教，让故事自己说话。角色形象和场景风格在全书中保持一致。画面叙事和文字叙事交替推进，视觉上要有变化。\n"
                f"声音设定：\n"
                f"适合亲子朗读的节奏和韵律。文案需要朗朗上口，让孩子愿意跟读。\n"
                f"核心叙事设定：\n"
                f"共{pages}页，文字量{text_amount}。故事结构完整——开端引入角色和场景，中间有小小的波折和解决，结尾温暖收束。每页的视觉重心要清晰，画面主体突出。\n"
            )
            return f"{header}\n\n{ai_result}"
        return ""

    # ============================================================
    # 短剧模式处理
    # ============================================================
    def _process_short_drama_mode(self, topic, character_desc, env_desc, shot_count,
                                   style, rhythm, camera_style, color_tone,
                                   api_url, api_key, model_name, temperature, max_tokens, ref_images):
        if not api_url:
            return ""

        if not topic:
            topic = self._random_topic("短剧模式")
        if not character_desc:
            character_desc = self._random_character("短剧模式", topic)
        if not env_desc:
            env_desc = self._random_env("短剧模式", topic)

        drama_sys = self._build_short_drama_system_prompt(topic, character_desc, env_desc, shot_count,
                                                           style, rhythm, camera_style, color_tone, ref_images)
        drama_user = self._build_short_drama_user_prompt(topic, shot_count, style, rhythm, camera_style)

        ai_result = self._call_ai(api_url, api_key, model_name, drama_sys, drama_user, temperature, max_tokens) or ""

        if ai_result:
            header = (
                f"短剧总纲\n"
                f"整体视觉风格：\n"
                f"风格为{style}，节奏{rhythm}，色彩调性偏向{color_tone}。竖屏9:16垂直构图。\n"
                f"角色物品设定：\n"
                f"{(character_desc or '待定角色').replace(chr(10), chr(10)).rstrip()}\n"
                f"道具或武器：\n"
                f"待补充。\n"
                f"场景设定：\n"
                f"{env_desc or '待定场景'}\n"
                f"氛围与画质标准：\n"
                f"竖屏短剧特有的叙事节奏。运镜以{camera_style}为主。开场快抓注意力，中间情绪反转，结尾留钩子。每个镜头要有画面感，禁止抽象词，用可见的动作和场景推进剧情。\n"
                f"声音设定：\n"
                f"根据剧情类型搭配配乐和音效。情绪转折点用音效强化冲击力。\n"
                f"核心叙事设定：\n"
                f"共{shot_count}个镜头。故事围绕{topic or '穿越时空的爱恋'}展开，遵循短剧创作规律——前几秒制造钩子，中间推进矛盾，结尾留下悬念或反转。\n"
            )
            return f"{header}\n\n{ai_result}"
        return ""

    # ============================================================
    # 儿童内容模式处理（4种）
    # ============================================================
    def _process_child_mode(self, mode, topic, character_desc, env_desc, count,
                             age_group, art_style,
                             api_url, api_key, model_name, temperature, max_tokens, ref_images):
        if not api_url:
            return ""

        if not topic:
            topic = self._random_topic(mode)
        if not character_desc:
            character_desc = self._random_character(mode, topic)
        if not env_desc:
            env_desc = self._random_env(mode, topic)

        kid_sys = self._build_child_system_prompt(mode, topic, character_desc, env_desc,
                                                   count, age_group, art_style, ref_images)
        kid_user = f"故事主题：{topic or '小动物的冒险'}\n"
        if character_desc:
            kid_user += f"角色描述：{character_desc}\n"
        kid_user += f"片段数/页数：{count}\n"
        if age_group:
            kid_user += f"年龄段：{age_group}\n"

        ai_result = self._call_ai(api_url, api_key, model_name, kid_sys, kid_user, temperature, max_tokens) or ""

        if ai_result:
            header = (
                f"{mode}总纲\n"
                f"整体视觉风格：\n"
                f"画风采用{art_style}，适合{age_group}年龄段的孩子。色彩鲜明活泼，符合儿童的视觉偏好。\n"
                f"角色物品设定：\n"
                f"{(character_desc or '待定角色').replace(chr(10), chr(10)).rstrip()}\n"
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
    # 专业设计模式处理（7种）
    # ============================================================
    def _process_design_mode(self, mode, topic, character_desc, env_desc, count,
                              style, color_tone, product_material, product_color,
                              shoot_angle, lighting_scheme, bg_type,
                              api_url, api_key, model_name, temperature, max_tokens, ref_images):
        if not api_url:
            return ""

        if not topic:
            topic = self._random_topic(mode)
        if not character_desc:
            character_desc = self._random_character(mode, topic)
        if not env_desc:
            env_desc = self._random_env(mode, topic)

        design_sys = self._build_design_system_prompt(mode, topic, character_desc, env_desc, count,
                                                       style, color_tone, product_material, product_color,
                                                       shoot_angle, lighting_scheme, bg_type, ref_images)
        design_global_ctx = self._build_design_global_context("专业设计", mode, topic, character_desc, env_desc, style, color_tone)
        design_user = self._build_design_user_prompt(mode, topic, character_desc, env_desc, count,
                                                      style, color_tone, product_material, product_color,
                                                      shoot_angle, lighting_scheme, bg_type)

        ai_result = self._call_ai(api_url, api_key, model_name, design_sys + design_global_ctx, design_user, temperature, max_tokens) or ""
        return ai_result

    # ============================================================
    # 7种专业设计模式 — 世界级专家系统提示词
    # ============================================================
    def _build_design_system_prompt(self, mode, topic, character_desc, env_desc, count,
                                     style, color_tone, product_material, product_color,
                                     shoot_angle, lighting_scheme, bg_type, ref_images):
        """根据模式构建世界级设计系统提示词"""
        builders = {
            "电商套图": self._build_ecommerce_prompt,
            "海报设计": self._build_poster_prompt,
            "品牌设计": self._build_brand_prompt,
            "PPT设计": self._build_ppt_prompt,
            "逻辑关系图设计": self._build_logic_diagram_prompt,
            "三视图设计": self._build_three_view_prompt,
            "爆炸拆解图设计": self._build_exploded_view_prompt,
            "流水线图设计": self._build_pipeline_diagram_prompt,
        }
        builder = builders.get(mode)
        if not builder:
            return ""
        return builder(topic, character_desc, env_desc, count, style, color_tone,
                       product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images)

    def _build_design_user_prompt(self, mode, topic, character_desc, env_desc, count,
                                   style, color_tone, product_material, product_color,
                                   shoot_angle, lighting_scheme, bg_type):
        parts = [f"设计主题：{topic or '未指定'}"]
        if character_desc: parts.append(f"角色/主体描述：{character_desc}")
        if env_desc: parts.append(f"环境/场景：{env_desc}")
        if style and style != "电影感": parts.append(f"设计风格：{style}")
        if product_material: parts.append(f"产品材质：{product_material}")
        if product_color: parts.append(f"产品颜色：{product_color}")
        if shoot_angle and shoot_angle != "自动": parts.append(f"拍摄/展示角度：{shoot_angle}")
        if lighting_scheme and lighting_scheme != "自动": parts.append(f"布光方案：{lighting_scheme}")
        if bg_type and bg_type != "自动": parts.append(f"背景类型：{bg_type}")
        parts.append(f"输出数量：{count}张/组")
        return "\n".join(parts)

    # ------ 电商套图（世界顶级电商摄影导演） ------
    def _build_ecommerce_prompt(self, topic, character_desc, env_desc, count, style, color_tone,
                                 product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images):
        ref_section = f"\n# 参考图信息\n用户提供了 {len(ref_images)} 张参考图，产品的材质质感、光影方向、构图方式需与参考图保持一致的调性。\n" if ref_images else ""
        return (
            "角色设定\n"
            "你是世界顶级的电商视觉导演——曾主导苹果、戴森、三宅一生等品牌的产品视觉企划。"
            "你的作品兼具「商业转化力」与「艺术品质感」，精通产品造型美学、材质光效渲染、场景化陈列与情绪化视觉营销。"
            "你的每一次布光都像在雕刻产品灵魂，每一帧画面都具备「让人想下单」的心理暗示力。\n\n"
            "# 核心设计哲学\n"
            "- 光即触感：产品的价值感靠光来「翻译」。丝绸光感、磨砂质感、金属冷感、皮革温感——光源的方向、面积、色温决定了用户是否能「感受到」材质\n"
            "- 构图减法：电商图的终极目标是「3秒传达核心卖点」。画面中只能保留1个视觉重心+1个辅助信息+1个情绪信号，多余元素全部切除\n"
            "- 色彩心理锚：红=冲动/黄=温暖/蓝=信任/黑=奢华/白=纯净。主色调占画面70%，辅助色25%，点缀色5%。不能违背色彩心理学规律\n"
            "- 视觉层级法则：眼球停留路径 = 产品(60%) → 材质细节(25%) → 情绪氛围(15%)。每一张图的光影引导必须遵循这个注意力分配\n\n"
            "# 输出要求\n"
            "请为以下产品生成 高质量AI电商套图提示词，每张图输出一段完整的AI提示词（可直接输入SD/Flux/DALL-E等工具），"
            "包含：产品主体描述+材质细节+光源方案+构图说明+色彩方案+氛围质感+画质标准。\n"
            "每张图的主题角度不同：第一张全景展示、第二张材质特写、第三张场景化使用、第四张创意陈列等。\n"
            "画面需达到电商级品质：超写实/8K/商业级渲染/无畸变/色彩精准/无AI常见伪影。\n"
            f"{ref_section}"
            "输出格式\n每张图以 【图N】标题 开头，输出完整AI提示词。变化规则：产品形态变化时增加场景描述。\n"
            "请直接输出，不要额外解释。"
        )

    # ------ 海报设计（世界级海报设计大师） ------
    def _build_poster_prompt(self, topic, character_desc, env_desc, count, style, color_tone,
                              product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images):
        ref_section = f"\n# 参考图信息\n用户提供了 {len(ref_images)} 张参考图，海报的版式结构、色彩系统、字体风格需与参考图调性保持一致。\n" if ref_images else ""
        return (
            "角色设定\n"
            "你是融合了福田繁雄的视错觉悖论、杉浦康平的信息编排法、保罗·兰德的设计减法与David Carson的解构主义的世界级海报设计师。"
            "你的海报设计兼具「信息传达的精准度」与「视觉冲击的艺术性」，精通负空间运用、字体排印层级、色彩对比法则和视觉动力学。\n\n"
            "# 核心设计哲学\n"
            "- 信息层级三原则：第一眼抓住注意力的是「标题」→第二眼读取的是「主视觉」→第三眼消化的是「详细信息」。三者的面积比例约为1:3:6\n"
            "- 负空间的力量：留白不是空白，而是呼吸。海报的视觉冲击力来自于「元素」与「空白」的对抗张力，不是信息堆砌\n"
            "- 字体即声音：衬线体=权威/经典/高端，无衬线体=现代/简洁/可亲，手写体=情感/个性/温度。字距、行距、对比大小构成视觉节奏\n"
            "- 色彩对比法则：面积色+点缀色的黄金比例=70%主色+25%辅助色+5%强调色。高对比不是颜色多，而是冷与暖、明与暗、纯与灰的精准对抗\n\n"
            "# 输出要求\n"
            "请生成 海报设计AI提示词，用于AI文生图工具生成高质量海报画面。每张提示词需包含：\n"
            "1) 主视觉描述：画面的核心图像内容、构图方式、视觉元素布局\n"
            "2) 色彩方案：主色调+辅助色+强调色的具体色值和比例\n"
            "3) 字体排印说明：标题/副标题/正文的字体风格、大小层级和位置\n"
            "4) 氛围质感：纸质/光面/纹理/印刷工艺（烫金/UV/击凸等）效果\n"
            "注意：提示词要能产出可直接使用的海报画面，画面构图需预留文字排版空间（通常在画面1/3区域）。\n"
            "画质标准：300DPI/印刷级/CMYK色域/超高清细节。\n"
            f"{ref_section}"
            "输出格式\n每张海报以 【海报N】标题 开头，输出完整AI提示词。变化规则：场景变化时增加场景描述。"
        )

    # ------ 品牌设计（世界级品牌设计总监） ------
    def _build_brand_prompt(self, topic, character_desc, env_desc, count, style, color_tone,
                             product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images):
        ref_section = f"\n# 参考图信息\n用户提供了 {len(ref_images)} 张参考图，品牌的视觉调性、色彩系统和设计语言需与参考图保持一致。\n" if ref_images else ""
        return (
            "角色设定\n"
            "你是世界500强品牌的设计总监——曾为Apple、MUJI、Patagonia、Aesop塑造品牌视觉系统。"
            "你精通品牌基因解码、视觉语言系统构建、品牌触点全链路设计。"
            "你的设计信条是「品牌不是一个LOGO，而是一种完整的世界观」——每个颜色、每种材质、每个图形都在讲同一个故事。\n\n"
            "# 核心设计哲学\n"
            "- 品牌元语言：品牌的视觉系统需要从品牌的核心价值观中推导出3个视觉关键词（例如：自然/精准/温暖），所有设计决策必须同时通过这3个关键词的检验\n"
            "- 延展统一性：一个强大的品牌视觉系统，LOGO只是冰山一角。字体系统、色彩系统、图形语言、图像风格、材质触感——五者必须是一个有机整体\n"
            "- 极简中的丰富：限制即创意。给定2种颜色、1个字体家族、1种图形语言，在这套限制中创造出无限的变化——才是真正的品牌设计\n"
            "- 情感锚点设计：品牌视觉的终极目标是创造「无条件偏爱」。每个视觉元素都要回答「这个元素为什么让人想拥有/信任/追随」\n\n"
            "# 输出要求\n"
            "请生成 品牌设计AI提示词，用于AI工具生成品牌视觉方案。每张提示词需包含：\n"
            "1) 品牌LOGO/徽标的核心视觉描述\n"
            "2) 品牌色彩系统的色值、比例和用法\n"
            "3) 品牌字体/排印的风格和层级\n"
            "4) 品牌图形语言和视觉元素\n"
            "5) 品牌应用场景（名片/包装/网页/空间等）的呈现方式\n"
            f"{ref_section}"
            "输出格式\n每张品牌设计以 【品牌设计N】标题 开头。变化规则：应用场景变化时增加场景描述。"
        )

    # ------ PPT设计（全球顶级PPT设计专家） ------
    def _build_ppt_prompt(self, topic, character_desc, env_desc, count, style, color_tone,
                           product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images):
        ref_section = f"\n# 参考图信息\n用户提供了 {len(ref_images)} 张参考图，PPT的版式风格和信息设计语言需与参考图调性一致。\n" if ref_images else ""
        return (
            "角色设定\n"
            "你是全球顶尖的演示设计专家——曾为TEDx、世界经济论坛、苹果发布会、Google I/O制作关键幻灯片。"
            "你精通信息可视化、数据叙事、演示节奏设计和观众注意力管理。"
            "你的核心理念是「一页只讲一个观点」，每一页幻灯片都是一次「认知的闪电」。\n\n"
            "# 核心设计哲学\n"
            "- 三秒法则：观众在3秒内必须理解这页在讲什么。做不到=设计失败。清晰>创意，速度>美感\n"
            "- 数据叙事弧：数据不是用来展示的，是用来讲故事的。高潮在第二页提出「问题和痛感」，第三页「数据揭示真相」，第四页「解决方案可视化」\n"
            "- 视觉锚点：每页只能有1个视觉锚点（大数字/图表峰值/对比图/关键引语）。其他元素围绕这个锚点服务\n"
            "- 节奏呼吸感：信息密集页和留白清爽页交替出现。两个密集页之间必须插入一页视觉缓冲（全幅图片/引语/过渡页）\n\n"
            "# 输出要求\n"
            "请生成 PPT设计AI提示词，每张提示词对应一页幻灯片。需包含：\n"
            "1) 页面类型（封面/目录/数据页/案例页/结尾页）\n"
            "2) 版式结构（左文右图/上下分区/满版/网格等）\n"
            "3) 视觉主元素（图表/图片/插图/大数字/引语）\n"
            "4) 色彩方案（主色+强调色+背景色+文字色）\n"
            "5) 信息层级（标题大小/副标题/正文/标注）\n"
            "6) 氛围质感（商务专业/科技感/温暖人文/极简高级）\n"
            f"{ref_section}"
            "输出格式\n每页以 【第N页】页面类型 开头。变化规则：演示环境变化时增加场景描述。"
        )

    # ------ 逻辑关系图设计（信息图表大师/瑞士设计风格） ------
    def _build_logic_diagram_prompt(self, topic, character_desc, env_desc, count, style, color_tone,
                                      product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images):
        ref_section = f"\n# 参考图信息\n用户提供了 {len(ref_images)} 张参考图，信息图表的视觉语言和逻辑结构需与参考图一致。\n" if ref_images else ""
        return (
            "角色设定\n"
            "你是信息图表与逻辑可视化领域的世界级大师——融合了Edward Tufte的数据墨水比理论、"
            "瑞士国际主义风格的网格系统、以及Richard Saul Wurman的信息架构方法。"
            "你擅长将复杂的系统逻辑、数据关系和抽象概念转化为一目了然的视觉图表。"
            "你的信条是「好的图表不需要解释」——读者看3秒就能理解整个逻辑关系。\n\n"
            "# 核心设计哲学\n"
            "- 数据墨水比最大化：去除所有非数据墨水（装饰性网格线、3D伪效果、多余的颜色、无意义的图标）。每一像素都要传达信息\n"
            "- 逻辑视觉化六类型：选择最合适的图表类型来表达逻辑关系——\n"
            "  ① 层级关系→树状图/金字塔图  ② 流程关系→流程图/时间线  ③ 对比关系→矩阵/对比栏  ④ 因果关系统→鱼骨图/影响图  ⑤ 循环关系→圆形图/反馈环  ⑥ 网络关系→力导向图/辐射图\n"
            "- 视觉层次三平面：第一平面=核心关系（最大最突出）→第二平面=子关系（中等尺寸）→第三平面=支持数据/标注（最小最轻）。三者通过大小/颜色饱和度/透明度区分\n"
            "- 颜色编码规则：同一逻辑层级使用同一色系（色相相同，明度变化）。不同逻辑层级使用不同色系（色相不同）。避免使用超过5种色相\n\n"
            "# 输出要求\n"
            "请生成 逻辑关系图AI提示词，用于AI工具生成清晰美观的逻辑关系图。需包含：\n"
            "1) 图表类型和逻辑结构描述\n"
            "2) 各节点/模块的内容和层级关系\n"
            "3) 连接线的类型（实线/虚线/箭头方向）和含义\n"
            "4) 色彩方案（同一层级同一色系，不同层级不同色系）\n"
            "5) 版式布局和网格对齐方式\n"
            "6) 文字说明的字体大小层级\n"
            f"{ref_section}"
            "输出格式\n每张图以 【图N】逻辑关系名称 开头。变化规则：逻辑层级变化时增加场景描述。"
        )

    # ------ 三视图设计（工业设计工程制图专家） ------
    def _build_three_view_prompt(self, topic, character_desc, env_desc, count, style, color_tone,
                                   product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images):
        ref_section = f"\n# 参考图信息\n用户提供了 {len(ref_images)} 张参考图，产品的造型比例、细节特征、材质表现需与参考图一致。\n" if ref_images else ""
        return (
            "角色设定\n"
            "你是世界顶级的工业设计师兼产品渲染专家——曾为保时捷、Bang & Olufsen、Muji设计产品。"
            "你精通产品三视图（正视图/侧视图/俯视图或仰视图）的工程美学表达。"
            "你的风格融合了Dieter Rams的「少而精」设计哲学和苹果工业设计团队的「极致细节」追求。\n\n"
            "# 核心设计哲学\n"
            "- 正交投影精确性：三视图必须遵循严格的正交投影规则——正视图确定宽高比，侧视图确定深度，俯视图确定顶部轮廓。三个视图的尺寸比例必须完全对应\n"
            "- 轮廓线的语言：外轮廓线（最粗）→分型线/结构线（中等）→细节线/装饰线（最细）。线的粗细变化本身就在传达「这是什么材质」「这里有多厚」\n"
            "- 光影结构提示：在工程图中加入精准的结构光影暗示——高光线表示曲率最高点，阴影线表示凹陷/转折。让观者仅通过线条就能「感受」到产品的三维形态\n"
            "- 材质与表面处理标注：不同材质用不同的渲染方式——金属=高光锐利/环境反射清晰、磨砂=漫反射柔和/边缘高光弥散、透明=折射率+厚度渐变\n\n"
            "# 输出要求\n"
            "请生成 产品三视图AI提示词，用于AI工具生成产品三视图渲染图。每组需包含：\n"
            "1) 正视图（Front View）：正面造型、屏幕/按键布局、比例标注\n"
            "2) 侧视图（Side/Right View）：侧面轮廓、厚度、接口位置、曲线形态\n"
            "3) 俯视图或仰视图（Top/Bottom View）：顶部/底部造型、功能区域分布\n"
            "4) 可选：45度三维透视展示（作为补充参考）\n"
            "画面风格：工业设计渲染/中性灰背景/干净柔光/无环境色干扰/清晰轮廓线。\n"
            f"{ref_section}"
            "输出格式\n每张图以 【图N】视图名称 开头。变化规则：视图环境变化时增加场景描述。"
        )

    # ------ 爆炸拆解图设计（世界顶级工业产品拆解插画师） ------
    def _build_exploded_view_prompt(self, topic, character_desc, env_desc, count, style, color_tone,
                                     product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images):
        ref_section = f"\n# 参考图信息\n用户提供了 {len(ref_images)} 张参考图，产品的拆解逻辑和零部件表现方式需与参考图一致。\n" if ref_images else ""
        return (
            "角色设定\n"
            "你是世界顶级的工业产品拆解视觉专家——你的作品风格融合了任天堂Labo的趣味拆解、"
            "IKEA说明书的图示化逻辑和《万物运转的秘密》的科普可视化。"
            "你擅长用爆炸拆解图（Exploded View）将复杂产品的内部结构、组装逻辑和零部件关系变得一目了然。\n\n"
            "# 核心设计哲学\n"
            "- 爆炸轴法则：选择一个主爆炸轴（通常是垂直Z轴或水平X轴），所有零部件沿该轴线性展开。爆炸距离=装配关系紧密度的视觉化——距离越近关系越近\n"
            "- 分层拆解逻辑：产品拆解按「外壳→内部框架→核心组件→电子元件→细微零件」的层级顺序展开。每个层级一种视觉密度，从外到内逐步加密\n"
            "- 编号+引线系统：每个零部件必须有唯一的编号，引线从零件指向编号，不能交叉。引线使用45度或90度折线，线径0.5pt，末端小圆点\n"
            "- 材质视觉编码：不同材质用不同的视觉处理——金属=灰色+高光反射、塑料=有色+柔光漫反射、电路板=绿色+铜色线条、玻璃/透明件=浅蓝+半透明\n\n"
            "# 输出要求\n"
            "请生成 产品爆炸拆解图AI提示词，用于AI工具生成产品的拆解图。需包含：\n"
            "1) 产品整体外观（组装状态）\n"
            "2) 沿爆炸轴展开的各个零部件（按从外到内的顺序排列）\n"
            "3) 每个零部件的材质和颜色标注\n"
            "4) 编号系统（从1开始，顺序=拆解顺序）\n"
            "5) 可选的装配方向箭头指示\n"
            "画面风格：工业技术插图/矢量风格/干净白色背景/精确正交投影/柔和均匀照明。\n"
            f"{ref_section}"
            "输出格式\n每张图以 【图N】产品名称 开头。变化规则：拆解环境变化时增加场景描述。"
        )

    # ------ 流水线图设计（流程图/信息设计专家） ------
    def _build_pipeline_diagram_prompt(self, topic, character_desc, env_desc, count, style, color_tone,
                                        product_material, product_color, shoot_angle, lighting_scheme, bg_type, ref_images):
        ref_section = f"\n# 参考图信息\n用户提供了 {len(ref_images)} 张参考图，流程图的视觉语言和结构布局需与参考图保持一致。\n" if ref_images else ""
        return (
            "角色设定\n"
            "你是世界顶级的流程可视化与系统设计专家——融合了丰田生产系统（TPS）的价值流图方法论、"
            "BPMN 2.0的业务流程建模标准和Google Material Design的信息层级设计。"
            "你擅长将复杂的生产流程、业务管线或系统架构转化为清晰、美观、可执行的流程图。\n\n"
            "# 核心设计哲学\n"
            "- 从左到右+从上到下的阅读流：主流程必须从左到右（或从上到下），分支流程可以垂直展开。读者不需要停下来思考「下一步该看哪」\n"
            "- 泳道（Swimlane）分区：不同角色/部门/系统的职责范围用泳道区分。每个泳道一种底色（低饱和度），同一泳道内的所有流程图元使用同色系\n"
            "- 图元标准化：圆角矩形=开始/结束 → 矩形=处理/操作 → 菱形=判断/分支 → 平行四边形=输入/输出 → 文档形=文档/记录。严禁随意使用图形形状\n"
            "- 信息密度的节奏：复杂步骤和简单步骤交替排列。连续3个以上复杂步骤之间必须插入1个判断节点或注释节点作为视觉缓冲\n\n"
            "# 输出要求\n"
            "请生成 流水线/流程图AI提示词，用于AI工具生成清晰的流程图。需包含：\n"
            "1) 流程图标题和整体布局说明（水平/垂直/混合流向）\n"
            "2) 每个步骤/节点的内容和图元类型\n"
            "3) 泳道分区（不同部门/角色用不同色带区分）\n"
            "4) 箭头方向和判定分支说明\n"
            "5) 色彩方案（每个泳道一种色系，判断节点用特殊色）\n"
            "6) 文字说明的字体大小和排版规范\n"
            f"{ref_section}"
            "输出格式\n每张图以 【图N】流程图名称 开头。变化规则：流程环境变化时增加场景描述。"
        )

    # ============================================================
    # 负面提示词生成（保留V18完整逻辑）
    # ============================================================
    def _generate_negative_prompt(self, custom_negative, main_content):
        """生成负面提示词"""
        neg_base = [
            "ugly", "deformed", "blurry", "bad anatomy", "bad proportions",
            "extra limbs", "cloned face", "disfigured", "gross proportions",
            "malformed limbs", "missing arms", "missing legs", "extra arms",
            "extra legs", "fused fingers", "too many fingers", "long neck",
            "bad quality", "normal quality", "worst quality", "low quality",
            "lowres", "monochrome", "grayscale", "bad composition",
            "cropped", "watermark", "text", "signature", "logo", "nsfw",
        ]
        pos_text = (main_content or "").lower()
        if "hand" in pos_text or "手指" in pos_text or "手" in pos_text:
            neg_base.append("bad hands")
        if "face" in pos_text or "脸" in pos_text or "面部" in pos_text:
            neg_base.append("bad face")
        if "eye" in pos_text or "眼睛" in pos_text:
            neg_base.append("bad eyes")

        if custom_negative:
            custom = [c.strip() for c in custom_negative.split(",") if c.strip()]
            neg_base.extend(custom)

        seen = set()
        unique = []
        for n in neg_base:
            if n not in seen:
                seen.add(n)
                unique.append(n)
        return ", ".join(unique)
    def _build_design_global_context(self, category, mode, topic, character_desc, env_desc, style, color_tone):
        ctx = (
            f"\n\n# 全局产品设计参考\n"
            f"设计类别：{mode}\n"
            f"主题：{topic or '未指定'}\n"
            f"风格参考：{style}\n"
            f"色彩基调：{color_tone or '自动'}\n"
            f"角色/主体：{character_desc or '未指定'}\n"
            f"场景环境：{env_desc or '未指定'}\n"
        )
        return ctx

    # ============================================================
    # 故事板系统提示词构建
    # ============================================================
    def _build_storyboard_system_prompt(self, mode, style, topic, character_desc, env_desc, ref_images):
        mode_name = self._get_mode_name(mode)
        mode_style = self._get_mode_style(mode)
        layout_desc = self._get_layout_desc(mode)

        ref_section = ""
        if ref_images:
            ref_section = (
                f"\n# 参考图信息\n"
                f"用户提供了 {len(ref_images)} 张参考图。这些图片的角色外貌、服装风格、场景环境、色彩氛围应作为本故事板的核心视觉参考。\n"
                f"在所有镜头中，角色外貌、服装样式、色彩基调需与参考图保持一致。在画面描述中参考参考图的构图、光影和氛围。\n"
            )

        env_section = ""
        if env_desc:
            env_section = f"环境背景：{env_desc}\n"

        # ===== 9种模式 ===== 各自独立的输出格式 =====
        # 每个模式定义自己的 format_template
        format_templates = {
            "电影分镜": (
                "输出格式（电影分镜专用）\n"
                "每个镜头严格按以下格式输出：\n\n"
                "【Shot N】\n"
                "景别：极远景/全景/中景/近景/特写/极特写（始终输出）\n"
                "分镜场景：有场景变化时输出完整场景描述（地点、时间、光线、环境氛围，2-4句）。无变化时不出现\n"
                "角色特征：仅在角色外貌/服装/状态有实质性变化时输出（换装/变脏/受伤/新增饰品等可见变化）。禁止写角色在做什么（那是画面维度的事）。无变化时此行整行不出现。\n"
                "画面：围绕这三层展开——①角色在做什么（具体动作）②场景里发生了什么能推动剧情的事③光线和色彩在说什么情绪。3-6句，像给小说写段落，让读者眼睛里有画面。\n"
                "运镜：固定/推/拉/摇/移/跟/升降/手持 + 速度 + 角度\n"
                "转场：硬切/叠化/淡入淡出/划像/匹配剪辑\n"
                "时长：X秒\n"
                "叙事功能：必要时才输出。\n"
            "\n"
                "电影分镜创作原则\n"
                "- 节奏变化：交替使用远景/中景/近景/特写，避免连续3个同景别\n"
                "- 180度法则：保持角色视线的方向连续性\n"
                "- 情绪弧线：每个情节节拍对应视觉色温变化（暖=安全/冷=危机）\n"
            ),
            "广告故事板": (
                "输出格式（广告故事板专用）\n"
                "每个镜头按以下格式输出：\n\n"
                "【Shot N】\n"
                "分镜场景：有场景变化时输出完整场景描述（地点、时间、光线、环境氛围，2-4句）。无变化时不出现\n"
                "角色特征：仅在角色外貌/服装/状态有实质性变化时输出（换装/变脏/受伤/新增饰品等可见变化）。禁止写角色在做什么（那是画面维度的事）。无变化时此行整行不出现。\n"
                "画面：产品在场景里是怎样的存在——它在被使用、被注视还是被环境烘托？周围的人和物跟它是什么关系？光线是突出它的质感还是它的情绪？2-4句。\n"
                "卖点传达：这个镜头在传递什么信息——是功能卖点、情感诉求还是品牌态度\n"
                "拍摄方式：产品机位+镜头焦距+运动方式\n"
                "品牌元素：LOGO在哪出现、品牌色怎么用、Slogan什么时候出现\n"
                "时长：X秒 | 节奏提示：快切还是留白\n\n"
                "广告故事板创作原则\n"
                "- 每个镜头必须服务于品牌信息的传递，不能游离于核心卖点之外\n"
                "- 前3秒抓住注意力，中间展示卖点，最后3秒强化品牌记忆\n"
                "- 产品在画面中的比例：开场全景(20%)→中景展示(40%)→特写质感(60%)\n"
            ),
            "动画故事板": (
                "输出格式（动画故事板专用）\n"
                "每个镜头按以下格式输出：\n\n"
                "【Shot N】\n"
                "分镜场景：有场景变化时输出完整场景描述（地点、时间、光线、环境氛围，2-4句）。无变化时不出现\n"
                "角色特征：仅在角色外貌/服装/状态有实质性变化时输出（换装/变脏/受伤/新增饰品等可见变化）。禁止写角色在做什么（那是画面维度的事）。无变化时此行整行不出现。\n"
                "画面描述：角色在做什么、表情是什么样、场景里发生了什么——但要记住这是动画，动作幅度比现实大，表情比现实夸张，物体可以有违反物理规律的变形。3-5句。\n"
                "关键帧：动作起/中/止三帧的关键姿态描述\n"
                "表情/动作：该镜头角色需要表现的核心情绪和肢体语言\n"
                "特效提示：粒子/烟雾/魔法/变形等动画特效的时机和方式\n"
                "时长：X秒（动画通常12-24帧/秒）\n\n"
                "动画故事板创作原则\n"
                "- 动作幅度比实拍电影大1.5-2倍，表情更夸张\n"
                "- 关键帧之间必须包含中间帧的动作提示（物理解算/变形路线）\n"
                "- 色彩和形状跟随情绪变化（快乐=鲜亮暖色/悲伤=冷暗模糊）\n"
            ),
            "漫画分镜": (
                "输出格式（漫画分镜专用）\n"
                "按页面布局输出，每个页面包含3-4格：\n\n"
                "【第X页】\n"
                "页面布局: [2×2格/3×1横条/1大格+3小格等]\n"
                "---\n"
                "格1\n"
                "分镜场景：有场景变化时输出完整场景描述（地点、时间、光线、环境氛围，2-4句）。无变化时不出现\n"
                "角色特征：仅在角色外貌/服装/状态有实质性变化时输出（换装/变脏/受伤/新增饰品等可见变化）。禁止写角色在做什么（那是画面维度的事）。无变化时此行整行不出现。\n"
                "画面描述：位置、角色在做什么、透视角度、这格在整个页面里扮演什么角色（定场/推进/高潮/收尾）\n"
                "对话框位置：左上/右中/下方——注意阅读顺序，不要让对话框挡住重要画面\n"
                "文本内容：要有对话的节奏感，短句为主\n"
                "拟声词提示：什么声音、多大、什么字体风格\n"
                "格2\n"
                "...\n\n"
                "漫画分镜创作原则\n"
                "- 阅读顺序：从左到右+从上到下（日式从右到左需标注）\n"
                "- 大格用于情绪高潮/场景全景/关键动作，小格用于对话/细节\n"
                "- 拟声词要用文字写出来（如'砰！''哗啦—'）并标注字体大小\n"
            ),
            "MV故事板": (
                "输出格式（MV故事板专用）\n"
                "每个镜头按以下格式输出：\n\n"
                "【Shot N】\n"
                "歌词段落：对应的歌词文本\n"
                "画面：歌词说了一件事，但画面可以讲另一层故事——或者画面对位歌词、或者反差、或者延展歌词的意境。2-4句。\n"
                "音乐配合：这镜头卡在哪个音乐节点上——前奏、主歌进鼓、副歌爆发、桥段转调？乐器/节奏变化怎么跟画面切换咬合。\n"
                "色彩调性：这镜头的主色调，以及它跟前一个镜头的色彩怎么过渡（硬切/渐变色/补色跳转）\n"
                "剪辑点：XX秒对应歌曲XX歌词/旋律节点\n\n"
                "MV故事板创作原则\n"
                "- 主歌部分：以叙事/角色状态为主，镜头节奏舒缓\n"
                "- 副歌/高潮部分：画面冲击力最大化，快速剪辑+特效\n"
                "- 歌词可视化：避免字面翻译歌词，而是将歌曲的情绪视觉化\n"
            ),
            "教程步骤": (
                "输出格式（教程步骤专用）\n"
                "按步骤编号顺序输出：\n\n"
                "【步骤X】\n"
                "标题：本步骤的核心操作名称\n"
                "画面：动手之前是什么状态，动手之后变成什么样。手部动作+界面变化+工具使用，2-3句。重点在'操作前vs操作后'的对比。\n"
                "操作说明：具体干什么——点击哪里、输入什么、拖拽到什么位置。越具体越好。\n"
                "重点提示：这里容易错在什么地方，搞错了怎么补救。\n"
                "完成状态：这步做完后应该看到什么效果\n\n"
                "教程步骤创作原则\n"
                "- 每步只教一个操作，步骤之间逻辑递进\n"
                "- 画面用箭头/标注/放大镜效果指示操作位置\n"
                "- 总步骤数不超过10步，超过则分组（第1部分/第2部分）\n"
            ),
            "短视频分镜": (
                "输出格式（短视频分镜专用）\n"
                "竖屏9:16，每个镜头1-3秒。每个镜头输出：\n\n"
                "【镜头N】\n"
                "画面：角色在做什么、画面里有什么吸引眼球的东西、这个镜头在1-3秒内怎么抓住人不让划走。1-2句。\n"
                "字幕/文本：画面叠加的文字——不超过8个字，要一眼看完\n"
                "音效/配乐：用BGM情绪带动画面——节奏点、音效、人声什么时候进\n"
                "转场：滑入/缩放/闪切/无缝转场\n"
                "心理时间：这个镜头在观众感觉里是快还是慢——快=激动/兴奋，慢=沉浸/情绪\n\n"
                "短视频分镜创作原则\n"
                "- 前3秒必须制造钩子（反直觉画面/问题提问/视觉冲击）\n"
                "- 每5-7秒一个信息点，每15秒一个转折/悬念\n"
                "- 竖屏构图：主体占据画面中上60%，底部留字幕空间\n"
                "- 画面文字：不超过10字/屏，大字号+高对比色\n"
            ),
            "品牌故事板": (
                "输出格式（品牌故事板专用）\n"
                "每个镜头按以下格式输出：\n\n"
                "【Shot N】\n"
                "画面：场景+角色+品牌元素怎么自然融入画面——不是生硬摆LOGO，而是让品牌成为场景的一部分。2-4句。\n"
                "品牌VI体现：这镜头里品牌色出现在哪里？LOGO以什么方式被看到？\n"
                "情感调性：这个镜头想让观众感受到什么——信任/活力/优雅/创新/安心\n"
                "文案参考：配合这个镜头的旁白或字幕大概写什么方向\n"
                "时长：X秒 | 节奏：舒缓还是紧凑\n\n"
                "品牌故事板创作原则\n"
                "- 品牌色占画面比例：主色60%+辅色30%+强调色10%\n"
                "- LOGO只在品牌记忆点出现（开场定调/高潮情感/结尾收束）\n"
                "- 品牌人格化：镜头语言本身反映品牌调性（高端=稳重镜头/活力=运动镜头）\n"
            ),
            "剧情分镜": (
                "输出格式（剧情分镜专用）\n"
                "以剧本式格式输出，每个镜头包含：\n\n"
                "【场景N】\n"
                "内/外景-地点-时间\n"
                "画面描述：角色在做什么、周围的环境是什么样的、空气中是什么氛围——3-6句，像在跟读者讲'你站在这场景里会看到什么、感觉到什么'。\n"
                "角色情绪：这镜头里角色处在什么状态——紧张/松弛/期待/疲惫，不写'他很难过'，写'他盯着窗外不说话，手指在桌沿反复摩挲'\n"
                "戏剧冲突：这镜头里矛盾在哪——两个人目标不同？信息不对称？情绪错位？还是外部压力在逼近？\n"
                "镜头语言：景别+机位+运动方式——镜头本身也在讲故事\n"
                "对白/独白：写出对话，每句话要么推进剧情要么揭示性格\n\n"
                "剧情分镜创作原则\n"
                "- 三幕结构：第一幕建立角色关系，第二幕冲突升级，第三幕高潮解决\n"
                "- 冲突密度递增：前30%大冲突间隔5分钟，后30%间隔1分钟\n"
                "- 每个镜头揭示一条新信息或推动情节发展，不能有冗余镜头\n"
                "- 对白精简：每句话要么推进剧情，要么揭示角色性格\n"
            ),
        }

        format_section = format_templates.get(mode,
            "输出格式（标准故事板）\n每个镜头包含：景别+画面描述+运镜+转场+备注\n"
        )

        story_sense = self._pick_story_sense()

        return (
            f"{story_sense}\n"
            f"上述故事感总纲是本片的故事结构设计核心。你必须用该总纲的情感曲线来设计整体情节的起伏——开场建立好奇，前段有小挫折，中段有真正的困境和最低点，之后出现转折，高潮解决问题，结尾温暖闭环。不要在每个分镜硬塞表情，而是让故事本身的走向有波折、有悬念、有反转。想象观众看到每个转折点时的反应：好奇→担心→心疼→松一口气→感动。\n\n"
            f"角色设定\n"
            f"你是一位世界顶级的{mode_name}导演兼分镜师，拥有20年好莱坞/影视行业经验。"
            f"你精通镜头语言、视觉叙事和节奏控制。"
            f"现在请你根据用户提供的主题、角色描述和镜头数量，创作一个完整的{style}风格{mode_name}故事板。\n"
            f"分镜具体内容\n\n"
            f"画面铁律（十二条红线）\n"
            f"1. 禁止抽象词：禁止「悲伤」「紧张」等情绪词，只用可见的描述来传递情绪。\n"
            f"2. 饱满叙事：每格3-6句话，充分描写场景氛围和角色动态，让画面生动丰满。\n"
            f"3. 镜头连续性：相邻镜头之间的角色位置、光线、道具必须一致。\n"
            f"4. 禁止参数：不能写焦距mm、色温K、分辨率dpi等数值参数。\n"
            f"5. 变化标注规则：仅在场景或角色有大的变化时，输出分镜场景或角色特征行。分镜场景：完整场景描述（地点、时间、光线、环境氛围，2-4句）。角色特征：仅在外貌/服装/状态有实质性变化时输出（换装/变脏/受伤/新增饰品等可见变化），描述变化了什么，2-3句。禁止写角色动作叙事（那是画面维度的事）。两者都变化时各一行。无变化时这两行不出现。其他字段正常输出。\n"
            f"6. 叙事功能仅在需要说明镜头作用时才输出，不是每个镜头都必须有。\n"
            f"7. 时空锚定：每页/每格开头固定用「时间·空间」前缀（如「清晨·森林小屋厨房」「傍晚·湖边小码头」）。当时间或空间发生变化时，在先导句中明确标注「时间推进到…」或「场景切换到…」。\n"
            f"8. 180度不越轴：相邻镜头保持角色视线和站位方向一致（左侧机位/右侧机位锁定），禁止突然镜像翻转。\n"
            f"9. 单格凝固动作：每格/每页只描述一个凝固的瞬间动作，禁止连续动作（如「跑向…然后跳起来」会导致画面鬼影）。\n"
            f"10. 场景切换时在首镜内增加场景描述和角色特征变化描述（换装/变脏等可见变化，无变化不写）。\n"
            f"11. 风格统一：所有镜头中角色外貌、服装、色彩基调必须保持严格一致（除非场景转换有明确交代）。每格开头重复主风格词。\n"
            f"12. 对话框绑定角色：多角色场景下，每个对话框必须明确指向该角色（如「指向[角色名]的对话框」「[角色名]头顶的气泡对话框」），禁止模糊的「有对话框」。旁白不加对话框。\n\n"
            f"{format_section}\n"
            f"# {mode_name}风格参考\n"
            f"{layout_desc}\n"
            f"{mode_style}\n"
            f"{ref_section}"
            f"{env_section}"
            f"请直接输出故事板内容，不要额外解释。\n"
            f"重要：输出中不要包含任何** - 等符号标记，不要用星号或横线装饰文字标题。直接输出纯文字。"
        )

    def _build_storyboard_user_prompt(self, mode, topic, character_desc, shot_count, style,
                                       color_tone, preferred_shot, camera_style, env_desc):
        parts = []
        if topic:
            parts.append(f"【主题】\n{topic}")
        if character_desc:
            parts.append(f"【角色描述】\n{character_desc}")
        if env_desc:
            parts.append(f"【环境背景】\n{env_desc}")
        parts.append(f"【镜头数量】\n{shot_count}个镜头")
        parts.append(f"【风格】\n{style}")

        tone_map = {
            "暖色调": "整体色调采用暖色调风格，以橙红、金黄、琥珀色为主",
            "冷色调": "整体色调采用冷色调风格，以蓝灰、青蓝、冷白为主",
            "高对比": "整体采用高对比风格，明暗反差强烈，光影分明",
            "低饱和": "整体采用低饱和风格，色彩淡雅克制，氛围沉静",
            "复古": "整体采用复古色调风格，暖黄+褪色感，仿胶片质感",
            "赛博朋克": "整体采用赛博朋克风格，霓虹紫蓝+暗黑对比",
            "日系清新": "整体采用日系清新风格，高明度低饱和，干净通透",
            "黑白": "整体采用黑白风格，以灰度层次表现光影",
        }
        if color_tone and color_tone != "自动":
            desc = tone_map.get(color_tone, f"整体色调采用{color_tone}风格")
            parts.append(f"【色彩基调要求】\n{desc}。请在所有镜头的画面描述中统一体现。")
        if preferred_shot and preferred_shot != "自动-多种交替":
            parts.append(f"【景别要求】\n以{preferred_shot}为主，占比60%以上。")
        if camera_style and camera_style != "自动":
            cam_map = {
                "稳重固定镜头": "大部分镜头使用固定机位，强调画面构图和内部运动",
                "流畅运动": "大量使用轨道推拉、稳定器跟拍等流畅运动镜头",
                "手持纪实": "使用手持摄影风格，轻微晃动感，增强真实感",
                "炫酷动感": "使用环绕、快速推拉、航拍等动感镜头",
            }
            desc = cam_map.get(camera_style, camera_style)
            parts.append(f"【运镜风格要求】\n{desc}")

        return "\n\n".join(parts)

    def _get_mode_name(self, mode):
        names = {
            "电影分镜": "电影分镜", "广告故事板": "广告故事板", "动画故事板": "动画故事板",
            "漫画分镜": "漫画分镜", "MV故事板": "MV故事板", "教程步骤": "教程步骤",
            "短视频分镜": "短视频分镜", "品牌故事板": "品牌故事板", "剧情分镜": "剧情分镜",
        }
        return names.get(mode, "故事板")

    def _get_mode_style(self, mode):
        styles = {
            "电影分镜": "🎬 电影分镜风格：强调镜头语言，包含景别标注，描述光影氛围，标注镜头时长",
            "广告故事板": "📺 广告故事板风格：每个镜头突出产品卖点/品牌信息，包含视觉焦点，节奏明快",
            "动画故事板": "🎨 动画故事板风格：注意角色动作夸张表现，描述关键帧，适合2D/3D制作",
            "漫画分镜": "📖 漫画分镜风格：标注页面布局，描述对话框位置，注意阅读顺序，包含拟声词提示",
            "MV故事板": "🎵 MV故事板风格：标注对应歌词段落，描述画面节奏与音乐配合",
            "教程步骤": "📚 教程步骤风格：每步清晰序号和标题，描述具体操作，步骤逻辑连贯",
            "短视频分镜": "📱 短视频分镜风格：单镜头1-3秒，竖屏9:16，描述画面切换和转场",
            "品牌故事板": "🏢 品牌故事板风格：突出品牌VI元素，描述调性和情感氛围，标注LOGO位置",
            "剧情分镜": "🎭 剧情分镜风格：强调角色情感表达和表演，描述戏剧冲突和节奏",
        }
        return styles.get(mode, "标准故事板格式")

    def _get_layout_desc(self, mode):
        layouts = {
            "电影分镜": "推荐16:9宽屏比例，注重纵深构图",
            "广告故事板": "每个镜头中心突出产品或品牌",
            "动画故事板": "注意角色表情和动作的夸张表达，16:9",
            "漫画分镜": "页面布局推荐3x3或2x4格",
            "MV故事板": "画面比例2.35:1电影宽银幕",
            "教程步骤": "画面比例4:3或1:1方形，标注编号",
            "短视频分镜": "画面比例9:16竖屏，垂直构图",
            "品牌故事板": "统一品牌色系，16:9比例",
            "剧情分镜": "推荐2.35:1宽银幕比例",
        }
        return layouts.get(mode, "标准16:9比例")

    # ============================================================
    # 绘本系统提示词构建（参考V18）
    # ============================================================
    def _build_picture_book_system_prompt(self, topic, character_desc, env_desc, pages,
                                          style, color_tone, text_amount, age_group, ref_images):
        age_guide = {
            "0-3岁低幼": "适合0-3岁婴儿/幼儿的绘本：每页画面简单，主体突出，色彩鲜明对比强，线条简洁圆润。文字极短（每页5-15字），句式重复，节奏感强。主题为日常生活认知。",
            "3-6岁幼儿": "适合3-6岁幼儿园儿童：画面丰富但有清晰视觉焦点，色彩温暖明亮。文字每页20-40字，故事有简单情节结构。角色形象可爱，表情丰富。",
            "6-9岁学龄": "适合6-9岁小学生：画面细节丰富，有多层景深和复杂构图。文字每页30-60字，故事有完整起承转合。主题涉及勇气/成长/科学/历史等。",
            "9-12岁少年": "适合9-12岁少年的插画书/图像小说：画面更写实或更具艺术风格，文字每页50-100字，故事可以有多条线索和深层寓意。",
        }
        word_count_guide = {
            "自动": "根据年龄段自动匹配文字量",
            "少字（每页10字以内）": "每页画面主体突出，文字极简（5-10字），以图叙事为主",
            "中等（每页20-40字）": "每页20-40字，图文并重，文字描述画面情节但留有想象空间",
            "多字（每页50字以上）": "每页50-100字，文字内容丰富，可以包含对话和细节描写",
        }
        ref_section = ""
        if ref_images:
            ref_section = f"\n# 参考图信息\n用户提供了 {len(ref_images)} 张参考图，角色设计、场景风格、色彩调性需与参考图保持一致。\n"
        env_section = f"环境背景设定：{env_desc}\n" if env_desc else ""

        sense = self._pick_story_sense()
        return (
            f"{sense}\n"
            f"上述故事感总纲是本绘本的故事结构设计核心。用总纲的情感曲线来设计整体的情节起伏——开场好奇，前段小挫折，中段真正的困境和最低点，转折，高潮，温暖闭环。让故事本身的走向有波折有悬念，不要在每个页面硬塞表情。\n\n"
            f"角色设定\n你是一位世界顶级的儿童绘本作家兼插画师，作品被全球数百万儿童阅读。"
            "你精通儿童心理认知发展、视觉叙事节奏和图文配合艺术。"
            f"现在请你根据用户提供的主题、页数、风格和年龄段，创作一本完整的儿童绘本。\n"
            "绘本各页的具体内容\n\n"
            "输出格式（严格遵循）\n以'【第N页】'开头，每页包含以下7个维度：\n\n"
            "1. 页码：第N页 / 共M页\n"
            "2. 时间·空间锚定：每页开头固定用「时间·空间」前缀（如「清晨·森林小屋厨房」「傍晚·湖边小码头」「午后·花园小径」）。当时间或空间发生变化时，在先导句中明确标注「时间推进到…」或「场景切换到…」。\n"
            "3. 画面描述：用孩子的眼睛看世界——角色在做什么、场景是什么样、光线给人的感觉是温暖还是神秘。可以写颜色和形状给人的感受，不需要写细节标注。2-4句。需要包含：角色表情/动作的明确描述、场景中关键道具的出现/位置、光线的来源和色温感受。注意：单页只写一个凝固瞬间动作，禁止连续动作。\n"
            "4. 分镜场景：有场景变化时输出完整场景描述（地点、时间、光线、环境氛围，2-4句）。无变化时不出现\n"
            "5. 角色特征：仅在角色外貌/服装/状态有实质性变化时输出（换装/变脏/受伤/新增饰品等可见变化）。禁止写角色在做什么（那是画面维度的事）。无变化时此行整行不出现。\n"
            "6. 文案：该页的绘本正文文字，适合亲子朗读，注意节奏感和韵律美。字数根据年龄段和文字量设置决定。\n"
            "7. 视觉连续性提示：该页与上一页/下一页的视觉关联说明（角色位置延续/色彩过渡/场景转换方式）\n"
            "8. 构图与景别说明：明确该页的构图方式（居中/三分法/对角线/框架构图等）和景别（远景/中景/近景/特写），确保每2-3页的景别交替变化。\n\n"
            "创作原则（十五项）\n"
            "- 叙事结构的「四个箱子」法则：每个故事元素必须同时满足：角色外部目标（可观测的、能画出来的动作）+ 角色内部需求（通过物理行动暗示）+ 场景的视觉趣味（颜色/形状/动感的峰值）+ 对话的潜在含义\n"
            "- 五感锚定法：每介绍一个新概念，必须通过至少2个感官通道的具象描述来呈现。不能直接解释原理，而是让儿童通过角色身体的物理体验来「感受」\n"
            "- 好奇心驱动的20-7-3节奏：前20%篇幅展示反直觉的视觉现象→第7%-12%角色提出开放式问题→最后3%必须有动手验证的视觉演示\n"
            "- 不说教公式：不直接陈述结论。结构为：角色A的错误假设→产生可观测的混乱→角色B用更巧妙的方式解决→儿童自己悟出「原来应该这样」\n"
            "- 🔴 角色一致性锚定：主角的外貌、服饰、颜色在所有页面中保持统一，除非场景变化有明确的服装更换交代。每页开头重复主风格词+核心角色特征描述\n"
            "- 变化必须可见：任何场景切换、角色增减、服装更换必须在分镜场景或角色特征字段中写清楚。角色特征仅写可见的外貌/服装变化，不写角色动作。无变化时字段不出现。\n"
            "- 视觉节奏：全景/中景/特写交替使用。每2-3页设置一个视觉高潮。禁止连续3页同景别\n"
            "- 负空间构图：背景色块尽量大一些、不复杂，给文字排版留出空间。画面顶部天空或底部路面留出纯净的水彩渐变区域用于排版\n"
            "- 八大红线：①不越轴（角色视线方向一致）②不跳时间（明确时间推进）③不连续动作（每页只一个凝固瞬间）④透视正确（全景比例自然）⑤风格统一（主风格词每页重复）⑥不抽象词（只用可见描述）⑦旁白/对话框绑定特定角色⑧时空前缀每页固定\n"
            "- 情绪始终正向：禁止恐怖/黑暗/危险/成人暗示/负面情绪。色彩基调必须温暖明亮、梦幻柔和或清新淡雅\n"
            "- 角色Prompt结构参考（用于前期设定）：根据参考图，总结参考图的整体风格（保留风格不要保留角色特征），生成同样风格的角色形象。画面左侧1/3为全身展示，右侧2/3为6个不同姿势和表情，背影纯白色。无文字符号分割线。\n"
            "- 场景Prompt结构参考：根据参考图生成同样风格场景。可全景展示或左侧全景+右侧细节拆分。无文字符号分割线。\n"
            "- 对话绑定规则：多角色场景下，对话框必须指向特定角色（「[角色名]头顶的气泡对话框」「指向[角色名]的对话框」）。旁白不加对话框。文字气泡搭配绘本风格样式。\n"
            "- 页面衔接规则：翻页后角色位置、视线方向和细节保持一致。上下页不能出现越轴。如需场景时间跳转，在变化页首句明确「时间推进到...」「场景切换到...」\n"
            "- 通用约束参考：风格词+角色描述(年龄/外貌/服装/表情)+场景描述(地点/关键道具)+光线色彩+情绪氛围+构图方式。禁止广角畸变、极端仰视。禁止恐怖/黑暗/危险/成人暗示。\n\n"
            f"# 年龄段创作指南\n{age_guide.get(age_group, age_guide['3-6岁幼儿'])}\n\n"
            f"# 文字量参考\n{word_count_guide.get(text_amount, word_count_guide['自动'])}\n\n"
            f"{ref_section}{env_section}\n重要：输出中不要包含任何** - 等符号标记，不要用星号或横线装饰文字。直接输出纯文字。"
        )

    def _build_picture_book_user_prompt(self, topic, pages, style, color_tone, text_amount, age_group):
        color_map = {
            "温暖明亮": "整体色调温暖明亮，以橙色、黄色、粉色为主色", "清新淡雅": "整体色调清新淡雅，以浅蓝、浅绿、淡紫为主色",
            "梦幻柔和": "整体色调梦幻柔和，以粉彩、薰衣草色为主色", "浓郁鲜艳": "整体色调浓郁鲜艳，以大红、宝蓝、翠绿等高饱和度颜色为主色",
            "黑白素描": "整体采用黑白素描风格，以线条和灰度层次表现",
            "暖色调": "整体色调以暖色为主", "冷色调": "整体色调以冷色为主",
            "高对比": "明暗反差强烈", "低饱和": "色彩淡雅克制", "复古": "暖黄+褪色感，仿胶片质感",
            "赛博朋克": "霓虹紫蓝+暗黑对比", "日系清新": "高明度低饱和，干净通透", "黑白": "以灰度层次表现光影",
        }
        parts = [f"主题：{topic or '童话森林探险'}", f"页数：{pages}页", f"风格：{style}"]
        if age_group: parts.append(f"年龄段：{age_group}")
        cd = color_map.get(color_tone, "")
        if cd: parts.append(f"色调要求：{cd}")
        if text_amount and text_amount != "自动": parts.append(f"文字量要求：{text_amount}")
        return "\n".join(parts)

    # ============================================================
    # 短剧系统提示词构建（参考V18）
    # ============================================================
    def _build_short_drama_system_prompt(self, topic, character_desc, env_desc, shot_count,
                                         style, rhythm, camera_style, color_tone, ref_images):
        rhythm_map = {
            "自动": "根据短剧类型自动匹配节奏", "舒缓铺垫": "节奏舒缓，前1/3建立角色关系，每个镜头3-5秒，以淡入淡出和叠化为主",
            "紧凑推进": "开场10秒内抛出冲突，每15-20秒一个小反转，镜头2-3秒/个", "高能密集": "开场3秒内用视觉冲击抓住注意力，每10-15秒一个爆点，镜头1-2秒/个",
        }
        ref_section = f"\n# 参考图信息\n用户提供了 {len(ref_images)} 张参考图，角色外貌、场景氛围、色彩调性需保持一致。\n" if ref_images else ""
        env_section = f"环境背景设定：{env_desc}\n" if env_desc else ""

        camera_desc = ""
        if camera_style not in ("自动", "稳重固定镜头", "流畅运动", "手持纪实", "炫酷动感"):
            cam_map = {"竖屏固定机位为主": "以竖屏固定机位为主，9:16垂直构图", "竖屏流畅运动": "竖屏中使用流畅的运动镜头，纵向升降、前后推拉"}
            camera_desc = cam_map.get(camera_style, "")

        sense = self._pick_story_sense()
        return (
            f"{sense}\n"
            f"上述故事感总纲是本短剧的故事结构设计核心。用总纲的情感曲线来设计整体的情节起伏——开场钩子，前段小冲突，中段真正的困境和最低点，转折，高潮，闭环。让剧情本身有波折有反转，不要在每个镜头硬塞表情。\n\n"
            f"角色设定\n你是一位世界顶级的AI短剧导演兼分镜编剧，你的作品在抖音、快手、Reels等平台拥有数千万播放量。"
            "你精通竖屏叙事语言、微短剧节奏控制、情绪引爆点设计和场景氛围营造。"
            f"现在请你根据用户提供的主题、镜头数和风格，创作一部完整的AI短剧分镜头剧本。\n\n"
            "核心世界观与通用设定\n## 角色设定\n- 每个角色必须有明确的外貌描述：性别、年龄、身高、体型、发型、面部特征、服装（款式+颜色+材质）、标志性道具\n"
            "- 所有镜头中角色外貌、服装、道具必须保持严格一致\n"
            "- 变化标注规则：仅在场景或角色有大的变化时，输出分镜场景或角色特征行。分镜场景：完整场景描述（地点、时间、光线、环境氛围，2-4句）。角色特征：仅在外貌/服装/状态有实质性变化时输出（换装/变脏/受伤/新增饰品等可见变化），描述变化了什么，2-3句。禁止写角色动作叙事（那是画面维度的事）。两者都变化时各一行。无变化时这两行不出现。其他字段正常输出。\n"
            "- 🔴 对话框绑定规则：多角色场景下，每个对话框必须明确指向该角色（「指向[角色名]的对话框」「[角色名]头顶的气泡对话框」）。旁白不加对话框。每句对话前标注角色名：角色名+冒号+对话内容。\n"
            "## 场景设定\n- 每个镜头需明确场景位置（室内/室外、具体空间名称），包含环境氛围提示：时间、光线、天气\n"
            "- 时空连续性：同一场景连续镜头必须沿用相同时空标签（如「白天·总裁办公室」「夜晚·天台上」）。时间变化时在镜头首句标注「时间推进到…」\n"
            "## 氛围与画质标准\n- 画面需达到电影级超写实质感，杜绝游戏CG感。色彩基调与短剧类型匹配\n\n"
            "输出格式\n以镜头N：标题开头。\n画面铁律（十二条红线）\n"
            "1. 禁止抽象词：只用可见描述\n"
            "2. 有画面：角色在做什么、环境什么样、有什么情绪暗示——3-5句，不是干巴巴的'他走了过去'，是'他穿过人群时肩膀擦过每个人的肩，却好像谁也没碰到'\n"
            "3. 竖屏视觉：9:16比例\n"
            "4. 变化标注规则：仅在场景或角色有大的变化时，输出分镜场景或角色特征行。分镜场景：完整场景描述（地点、时间、光线、环境氛围，2-4句）。角色特征：仅在外貌/服装/状态有实质性变化时输出（换装/变脏/受伤/新增饰品等可见变化），描述变化了什么，2-3句。禁止写角色动作叙事（那是画面维度的事）。两者都变化时各一行。无变化时这两行不出现。其他字段正常输出。\n"
            "5. 叙事功能仅在必要时输出。\n"
            "6. 时空锚定：每镜开头固定时间·空间前缀\n"
            "7. 180度不越轴：相邻镜头角色视线方向一致。场景切换时增加分镜场景描述。\n"
            "8. 单镜凝固动作：每镜只一个凝固瞬间，禁止连续动作\n"
            "9. 透视正确：全景比例自然，禁止广角畸变\n"
            "10. 禁止参数：不写焦距mm/色温K等数值\n"
            "11. 风格统一：角色外貌、服装、色彩基调所有镜头严格一致。每镜开头重复主风格词\n"
            "12. 对话框绑定角色：每句对白标注角色名，旁白不加对话框\n\n"
            "脚本正文后输出：景别、台词、运镜、备注\n\n"
            "创作原则\n"
            "- 镜头连续性：相邻镜头需有明确的视觉或动作逻辑衔接\n"
            "- 黄金3秒三联序列：开场反物理冲击→可理解动作→开放式悬念\n"
            "- 15秒反转节奏：每15秒一个反转\n- 竖屏构图：9:16比例\n"
            "- 情绪断崖法则：同一情绪状态持续不超过3秒\n- 对白精简：每句不超过15字\n- 结尾悬念\n\n"
            "# 色彩与视觉调性\n- 古风言情：暖杏色+黛蓝色\n- 现代都市：冷白色+霓虹色\n- 悬疑惊悚：冷灰色+暗青色\n- 奇幻仙侠：紫色+金色\n- 喜剧轻松：暖黄色+亮粉色\n\n"
            f"# 节奏风格\n{rhythm_map.get(rhythm, rhythm_map['自动'])}\n\n"
            f"{ref_section}{env_section}"
            f"{('# 运镜要求' + chr(10) + camera_desc + chr(10) + chr(10)) if camera_desc else ''}"
        )

    def _build_short_drama_user_prompt(self, topic, shot_count, style, rhythm, camera_style):
        parts = [f"主题：{topic or '穿越时空的爱恋'}", f"镜头数：{shot_count}个", f"风格：{style}"]
        if rhythm and rhythm != "自动": parts.append(f"节奏要求：{rhythm}")
        return "\n".join(parts)

    # ============================================================
    # 儿童内容提示词（4种子模式，参考V18）
    # ============================================================
    def _build_child_system_prompt(self, mode, topic, character_desc, env_desc, count, age_group, art_style, ref_images):
        age_desc = {
            "0-3岁低幼": "画面简单主体突出，色彩鲜明对比强，线条简洁圆润。文字极短（每页5-15字），句式重复有节奏感。",
            "3-6岁幼儿": "画面丰富有清晰视觉焦点，色彩温暖明亮。文字每段10-30字，故事有简单情节。角色形象可爱。",
            "6-9岁学龄": "画面细节丰富，文字每段20-50字，故事有完整起承转合。可涉及勇气/成长/科学等主题。",
        }
        style_map = {
            "水彩插画": "水彩晕染风格，色彩柔和通透，边缘自然过渡", "卡通动画": "明亮卡通风格，粗轮廓线，纯色填充，表情夸张可爱",
            "彩铅手绘": "彩色铅笔手绘质感，线条有铅笔纹理", "黏土定格": "黏土定格动画风格，立体感强", "扁平矢量": "扁平矢量插画风格，简洁几何形状",
        }
        age_text = age_desc.get(age_group, age_desc["3-6岁幼儿"])
        style_text = style_map.get(art_style, style_map["卡通动画"])
        ref_section = f"\n参考图信息：用户提供了 {len(ref_images)} 张参考图，角色设计、色彩风格需与参考图保持一致。\n" if ref_images else ""
        env_section = f"环境背景：{env_desc}\n" if env_desc else ""

        if mode == "儿童视频格式一":
            return self._build_child_v1(style_text, age_text, ref_section, env_section)
        elif mode == "儿童视频格式二":
            return self._build_child_v2(style_text, age_text, ref_section, env_section)
        elif mode == "儿童微动视频/GIF":
            return self._build_child_gif(style_text, age_text, ref_section, env_section)
        elif mode == "儿童绘本格式":
            return self._build_child_book(style_text, age_text, ref_section, env_section)
        return ""

    def _build_child_v1(self, style_text, age_text, ref_section, env_section):
        sense = self._pick_story_sense()
        return (
            f"{sense}\n"
            f"上述故事感总纲是本故事的结构设计核心。严格按照总纲的情节结构来设计故事的起承转合。让故事本身有波折有悬念，不要平铺直叙。情感表达在恰当的情节节点出现，配合故事推动。\n\n"
            f'角色设定\n你是一位世界顶级的儿童动画编剧兼分镜师。\n'
            f'输出格式\n按叙事进程分为第一部分、第二部分，每部分下分【片段1】、【片段2】。\n'
            f'每个片段按以下顺序输出：\n'
            '  1.时间·空间锚定：每片段固定「清晨·池塘边」「午后·树荫下」前缀，变化时标注推进\n'
            '  2.场景描述：用孩子的语言描述画面，2-3句。单片段只写一个凝固瞬间动作\n'
            '  3.动态描述【动态】：标注该片段的动效和运动方式\n'
            '  4.分镜场景：有大的场景变化时输出完整场景描述（地点、时间、光线、环境氛围，2-4句）。无变化时此行不出现\n'
            '  5.角色特征：仅在角色外貌/服装/状态有实质性变化时输出（换装/变脏/受伤/新增饰品等可见变化）。禁止写角色动作叙事（那是画面维度的事）。无变化时此行不出现\n'
            '  6.旁白/对话：多角色时标注角色名\n'
            '  7.特效/TIPS：可选\n\n'
            '创作原则\n'
            '- 皮克斯四个箱子法则\n'
            '- 五感锚定法\n'
            '- 不说教公式\n'
            '- 短句、拟声词\n'
            '- 变化必须可见：场景切换、角色增减、服装更换必须在分镜场景或角色特征字段中写清楚。角色特征仅写可见的外貌/服装变化，不写角色动作叙事。无变化时字段不出现。\n'
            '- 八大红线：不越轴、不跳时间、不连续动作、透视正确、风格统一、不抽象词、绑定对话框、时空锚定\n'
            '- 情绪节奏：平静到小问题到努力解决到快乐结局\n'
            '- 对话框绑定规则：多角色场景下，对话框必须指向特定角色。旁白不加对话框\n'
            '- 页面衔接规则：翻页后角色位置、视线方向保持一致，上下页不能越轴\n'
            '- 通用约束参考：风格词+角色描述+场景描述+光线色彩+情绪氛围。禁止广角畸变、极端仰视、恐怖元素\n\n'
            f'年龄段适配\n{age_text}\n画面风格\n{style_text}\n{ref_section}{env_section}\n重要：输出中不要包含任何** - 等符号标记，不要用星号或横线装饰文字。直接输出纯文字。'
        )

    def _build_child_v2(self, style_text, age_text, ref_section, env_section):
        sense = self._pick_story_sense()
        return (
            f"{sense}\n"
            f"上述故事感总纲是本故事的结构设计核心。严格按照总纲的情节结构来设计故事的起承转合。让故事本身有波折有悬念，不要平铺直叙。情感表达在恰当的情节节点出现。\n\n"
            "角色设定\n你是一位世界顶级的儿童动画编剧兼分镜师。\n"
            "输出结构\n严格按四幕叙事结构输出：第一幕起 / 第二幕承 / 第三幕转 / 第四幕合。每幕下包含多个片段。\n"
            "每个片段按以下维度输出（维度顺序固定，但只输出有内容的维度）：\n"
            "【场景】地点·天气·时间·内外（如「森林·晴·日·外」「大树洞·雨·日·内」）。始终输出。\n"
            "画面描述：场景氛围、光线、色彩情绪、关键视觉元素，2-3句。用孩子的语言描述，每片段只写一个凝固瞬间动作。\n"
            "旁白：叙事旁白文字，用短句和拟声词，适合儿童跟读。\n"
            "对话：角色名（表情动作标注）：对话内容。多角色时每句标注角色名。表情动作标注用简洁的中文状态词如开心扭身体、慌张缩起身体、耷拉着小脑袋。\n"
            "TIPS：该片段的叙事功能或关键提示，可选输出。\n"
            "（以下两个维度仅在有大变化时输出：分镜场景——地点/时间/光线/环境氛围变化，2-3句。角色特征——外貌/服装/状态变化，2-3句。无变化时不出现在输出中。）\n"
            "动态描述【动态】：标注该片段的动效和运动方式（如「雨滴从天空缓缓落下，地面水花溅起」）。可选输出，有动效变化时必出。\n\n"
            "输出示例（仅供参考格式，实际内容按故事需要填充）：\n"
            "第一幕起\n"
            "【场景】森林·晴·日·外\n"
            "画面描述：晴朗的夏天，大森林里暖洋洋的。小蛇溜溜正蜷在软软的草地上晒太阳，晃着细细的小尾巴。\n"
            "旁白：太阳暖暖照下来，溜溜今天好开心。\n"
            "对话：小蛇溜溜（开心扭身体）：太阳暖暖真舒服，溜溜今天好开心！\n\n"
            "创作原则\n"
            "皮克斯四箱子法则\n五感锚定法\n不说教公式\n"
            "冲突不超过全篇30%\n结局有正向教育意义\n"
            "变化必须可见：场景切换、角色增减、服装更换才输出分镜场景或角色特征字段\n"
            "八大红线：不越轴、不跳时间、不连续动作、透视正确、风格统一、不抽象词、绑定对话框、时空锚定\n"
            "对话框绑定规则：多角色场景下，对话框必须指向特定角色，旁白不加对话框\n"
            "页面衔接规则：上下页角色位置、视线方向保持一致，不能越轴\n"
            "通用约束：风格词+角色描述+场景+光线+情绪。禁止广角畸变、极端仰视、恐怖元素\n\n"
            f"年龄段适配\n{age_text}\n画面风格\n{style_text}\n{ref_section}{env_section}\n"
            "输出约束：严禁使用任何符号标记——禁止#、禁止**、禁止-开头、禁止→、禁止1. 2. 3.编号、禁止---分隔线。直接用纯文字叙述。各维度之间用换行分隔，不要用符号装饰维度名称。")

    def _build_child_gif(self, style_text, age_text, ref_section, env_section):
        sense = self._pick_story_sense()
        return (
            f"{sense}\n"
            f"上述故事感总纲是本故事的结构设计核心。严格按照总纲的情节结构来设计故事的起承转合。让故事本身有波折有悬念，不要平铺直叙。情感表达在恰当的情节节点出现。\n\n"
            "角色设定\n你是一位世界顶级的儿童动画编剧兼分镜师，专攻微动视频/GIF格式。\n"
            "输出格式\n按故事叙事顺序编号【第N页】。每页严格按以下维度输出：\n"
            "核心动作：该页的核心情节节点/动作，一句话概括（带情绪关键词）。\n"
            "画面：场景氛围、角色位置、关键视觉元素、光线色彩情绪，2-3句。用孩子的语言描述。每页只写一个凝固瞬间动作。\n"
            "动效：标注该页的动效和循环方式（如「兔子踮脚—放下—踮脚循环」「萝卜弹起—滚落（弧线运动）」）。首帧等于末帧。\n"
            "（分镜场景和角色特征仅在有大变化时输出。分镜场景：地点/时间/光线/环境氛围变化，2-3句。角色特征：外貌/服装/状态变化，2-3句。不写角色动作叙事。无变化时不出现在输出中。）\n\n"
            "创作原则\n"
            "- 每页只表达1个核心动作，画面简洁\n"
            "- 动效标注循环方式，GIF首帧等于末帧形成无缝循环\n"
            "- 变化必须可见：场景切换、角色增减、服装更换才输出分镜场景或角色特征字段\n"
            "- 八大红线：不越轴、不跳时间、不连续动作、透视正确、风格统一、不抽象词、绑定对话框、时空锚定\n"
            "- 对话框绑定规则：多角色对话框指向特定角色，旁白不加对话框\n"
            "- 页面衔接规则：翻页后角色位置、视线方向保持一致，上下页不能越轴\n"
            "- 通用约束：风格词+角色描述+场景+光线+情绪。禁止广角畸变、极端仰视、恐怖元素\n\n"
            f"年龄段适配\n{age_text}\n画面风格\n{style_text}\n{ref_section}{env_section}\n"
            "输出约束：严禁使用任何符号标记——禁止#、禁止**、禁止-开头、禁止→、禁止1. 2. 3.、禁止---分隔线、禁止任何形式的装饰符号。直接用纯文字叙述。每页维度用换行分隔，不要编号前缀。"
        )

    def _build_child_book(self, style_text, age_text, ref_section, env_section):
        sense = self._pick_story_sense()
        return (
            f"{sense}\n"
            f"上述故事感总纲是本故事的结构设计核心。严格按照总纲的情节结构来设计故事的起承转合。让故事本身有波折有悬念，不要平铺直叙。情感表达在恰当的情节节点出现。\n\n"
            "角色设定\n你是一位世界顶级的儿童绘本编剧兼插画师。\n"
            "输出格式\n按故事顺序编号【第N页】。每页严格按以下维度输出：\n"
            "画面：场景氛围、角色位置和表情动作、关键视觉元素、光线色彩情绪，2-4句。用孩子的语言描述。每页只写一个凝固瞬间动作。页面负空间留出文字排版区域。\n"
            "文案：绘本正文文字，适合亲子朗读，注意节奏感和韵律美。字数根据年龄段和文字量设置决定。\n"
            "旁白/对话：多角色时标注角色名。对话框自然融入画面描述。\n"
            "视觉连续性提示：该页与上一页/下一页的视觉关联说明（角色位置延续/色彩过渡/场景转换方式），可选输出。\n"
            "构图与景别：明确该页的构图方式（居中/三分法/对角线/框架构图等）和景别（远景/中景/近景/特写），确保每2-3页的景别交替变化。\n"
            "（分镜场景和角色特征仅在有大变化时输出。分镜场景：地点/时间/光线/环境氛围变化，2-3句。角色特征：外貌/服装/状态变化，2-3句。不写角色动作叙事。无变化时不出现在输出中。）\n\n"
            "创作原则\n"
            "不说教公式：不直接陈述结论。角色A的错误假设产生可观测的混乱，角色B用更巧妙的方式解决，儿童自己悟出原来应该这样\n"
            "角色一致性锚定：主角的外貌、服饰、颜色在所有页面中保持统一，除非场景变化有明确的服装更换交代。每页开头重复主风格词\n"
            "变化必须可见：场景切换、角色增减、服装更换才输出分镜场景或角色特征字段\n"
            "视觉节奏：全景/中景/特写交替使用，每2-3页设置一个视觉高潮，禁止连续3页同景别\n"
            "八大红线：不越轴、不跳时间、不连续动作、透视正确、风格统一、不抽象词、绑定对话框、时空锚定\n"
            "负空间构图：背景色块尽量大一些、不复杂，给文字排版留出空间。画面顶部天空或底部路面留出纯净区域用于排版\n"
            "情绪始终正向：禁止恐怖/黑暗/危险/成人暗示/负面情绪。色彩基调温暖明亮、梦幻柔和或清新淡雅\n"
            "对话框绑定规则：多角色场景下，对话框必须指向特定角色，旁白不加对话框\n"
            "页面衔接规则：翻页后角色位置、视线方向保持一致，上下页不能越轴\n"
            "通用约束：风格词+角色描述+场景+光线+情绪。禁止广角畸变、极端仰视、恐怖元素\n\n"
            f"年龄段适配\n{age_text}\n画面风格\n{style_text}\n{ref_section}{env_section}\n"
            "输出约束：严禁使用任何符号标记——禁止#、禁止**、禁止-开头、禁止→、禁止1. 2. 3.编号、禁止---分隔线。直接用纯文字叙述。各维度之间用换行分隔，不要用符号装饰维度名称。")

    # ============================================================
    # V18 辅助方法 — 文件扫描/过滤/AI调用/翻译/解析
    # ============================================================

    # 预编译正则表达式
    _RE_SD_PARENS = re.compile(r'\(\([^)]*\)\)')
    _RE_SD_BRACKETS = re.compile(r'\[\[[^\]]*\]\]')
    _RE_SD_CURLY = re.compile(r'\{[^}]*\}')
    _RE_CJK = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')
    _RE_ASCII_ONLY = re.compile(r'[^\x00-\x7F]')
    _RE_MULTISPACE = re.compile(r'\s+')

    LIFELESS_KEYWORDS = [
        "产品", "商品", "静物", "物件", "物品", "陈列品",
        "食物", "菜肴", "菜品", "中餐", "西餐",
        "珠宝", "首饰", "戒指", "项链", "耳环",
        "家具", "沙发", "桌子", "椅子", "床", "柜子",
        "手机", "电脑", "显示器", "键盘", "鼠标",
        "汽车", "轿车", "鞋", "衣服", "服装",
        "花瓶", "杯子", "餐具",
        "化妆品", "护肤品", "口红", "香水",
        "product photo", "still life", "food photography",
    ]

    WHITELIST_WORDS = [
        "人", "人物", "人像", "肖像", "女孩", "男孩", "女人", "男人",
        "美女", "帅哥", "少女", "仙女", "精灵", "天使",
        "公主", "王子", "女王", "国王", "骑士", "战士", "法师",
        "猫", "狗", "兔子", "鸟", "龙", "狮子", "老虎",
        "风景", "日落", "日出", "山脉", "海滩", "森林", "星空",
        "portrait", "woman", "man", "girl", "boy",
        "cat", "dog", "dragon", "lion", "tiger",
    ]

    STRONG_SUBJECT_SIGNALS = {
        "少女", "少年", "女孩", "男孩", "女性", "男性", "女子", "男子",
        "女人", "男人", "模特", "人物", "人像", "肖像", "角色", "主角",
        "美女", "帅哥", "精灵", "天使", "公主", "王子", "女王", "国王",
        "新娘", "新郎", "婴儿", "孩童", "舞者", "歌手",
        "猫咪", "狗狗", "鸟儿", "兔子", "狐狸", "蝴蝶", "金鱼",
        "风景", "山水", "日落", "日出", "海滩", "森林", "山脉",
        "woman", "man", "girl", "boy", "portrait", "character",
        "cat", "dog", "bird", "dragon", "landscape", "sunset",
    }

    def _parse_keywords(self, kw_str):
        if not kw_str or not kw_str.strip():
            return []
        return [k.strip() for k in kw_str.split(",") if k.strip()]

    def _parse_tags(self, tag_str):
        if not tag_str or not tag_str.strip():
            return []
        return [t.strip() for t in tag_str.split(",") if t.strip()]

    def _scan_files(self, folder_path):
        exts = (".txt", ".csv", ".md", ".jsonl")
        files = []
        try:
            for entry in os.scandir(folder_path):
                if entry.is_file() and entry.name.lower().endswith(exts):
                    files.append(entry.path)
        except (PermissionError, OSError):
            return []
        files.sort()
        return files

    def _file_has_tag(self, filepath, wanted_tags):
        fname = os.path.basename(filepath).lower()
        for tag in wanted_tags:
            if tag.lower() in fname:
                return True
        return False

    def _load_lines(self, files, keywords, max_lines=0):
        all_lines = []
        total_bytes = 0
        MB = 50 * 1024 * 1024
        for fp in files:
            if total_bytes >= MB:
                break
            try:
                fsize = os.path.getsize(fp)
                if fsize > MB:
                    lines = self._stream_load(fp, max_lines or 5000)
                else:
                    with open(fp, "r", encoding="utf-8", errors="replace") as f:
                        if max_lines > 0:
                            lines = [f.readline() for _ in range(max_lines)]
                            lines = [l for l in lines if l]
                        else:
                            lines = f.readlines()
                    total_bytes += fsize
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith(("#", "//", "--")) or len(line) < 3:
                        continue
                    if keywords and not any(kw.lower() in line.lower() for kw in keywords):
                        continue
                    all_lines.append({"text": line, "source": fp})
                    if max_lines > 0 and len(all_lines) >= max_lines:
                        break
                if max_lines > 0 and len(all_lines) >= max_lines:
                    break
            except (OSError, UnicodeDecodeError):
                continue
        return all_lines

    def _stream_load(self, fp, limit):
        lines = []
        try:
            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                for _ in range(limit):
                    line = f.readline()
                    if not line:
                        break
                    lines.append(line)
        except (OSError, UnicodeDecodeError):
            pass
        return lines

    def _smart_filter(self, lines):
        if not lines:
            return None
        filtered = []
        for entry in lines:
            text = entry["text"]
            has_subject = any(s in text for s in self.STRONG_SUBJECT_SIGNALS)
            if not has_subject:
                for body in ["长发", "短发", "手臂", "腿部", "站立", "行走",
                              "抚摸", "微笑", "凝视", "猫咪", "小狗"]:
                    if body in text:
                        has_subject = True
                        break
                if not has_subject and "猫" in text and "猫粮" not in text:
                    has_subject = True
            if has_subject:
                filtered.append(entry)
                continue
            if not any(kw in text for kw in self.LIFELESS_KEYWORDS):
                filtered.append(entry)
        if len(filtered) == len(lines):
            return None
        return filtered

    def _filter_by_subject(self, lines):
        if not lines:
            return []
        patterns = [
            r"女性", r"男性", r"女人", r"男人", r"女孩", r"男孩",
            r"模特", r"人物", r"人像", r"肖像", r"角色", r"主角",
            r"美女", r"帅哥", r"精灵", r"天使", r"公主", r"王子",
            r"风景", r"日落", r"日出", r"山脉", r"海滩", r"森林",
            r"woman", r"man", r"girl", r"boy", r"portrait",
            r"cat", r"dog", r"dragon", r"landscape", r"sunset",
        ]
        filtered = [e for e in lines if any(re.search(p, e["text"], re.I) for p in patterns)]
        return filtered

    def _pick_n_lines(self, lines, mode, loop_mode, count, folder_path):
        if not lines:
            return []
        cache_key = f"idx_{folder_path}"
        with self._cache_lock:
            state = self._cache.get(cache_key, {})
        idx = state.get("idx", 0)
        shuffled = state.get("shuffled", None)
        chosen = []
        avail = list(lines)

        if mode == "随机抽取":
            for _ in range(count):
                if not avail:
                    break
                e = random.choice(avail)
                chosen.append(e)
                if loop_mode == "读完停止":
                    avail.remove(e)
        elif mode == "顺序循环":
            for _ in range(count):
                if not avail:
                    break
                chosen.append(avail[idx % len(avail)])
                idx += 1
                if loop_mode == "读完停止" and idx >= len(avail):
                    break
            with self._cache_lock:
                self._cache[cache_key] = {"idx": idx}
        elif mode == "洗牌遍历":
            if shuffled is None:
                shuffled = list(avail)
                random.shuffle(shuffled)
            for _ in range(count):
                if not shuffled:
                    if loop_mode == "读完停止":
                        break
                    shuffled = list(avail)
                    random.shuffle(shuffled)
                chosen.append(shuffled.pop(0))
            with self._cache_lock:
                self._cache[cache_key] = {"idx": idx, "shuffled": shuffled}
        elif mode == "权重随机":
            weights = [max(len(e["text"]), 1) for e in avail]
            if sum(weights) <= 0:
                weights = [1] * len(avail)
            for _ in range(count):
                if not avail:
                    break
                e = random.choices(avail, weights=weights, k=1)[0]
                chosen.append(e)
                if loop_mode == "读完停止":
                    i = avail.index(e)
                    avail.pop(i)
                    weights.pop(i)
        return chosen

    def _history_dedup(self, chosen, folder_path):
        key = f"hist_{folder_path}"
        with self._cache_lock:
            hist = self._cache.get(key, [])
        deduped = []
        for e in chosen:
            if e["text"] not in hist:
                deduped.append(e)
                hist.append(e["text"])
            if len(deduped) >= len(chosen):
                break
        if len(hist) > 50:
            hist = hist[-50:]
        with self._cache_lock:
            self._cache[key] = hist
        return deduped

    def _call_ai(self, api_url, api_key, model_name, system_prompt, user_message, temperature, max_tokens):
        if not api_url:
            self._last_ai_error = "API地址为空"
            return ""
        for attempt in range(3):
            try:
                headers = {"Content-Type": "application/json"}
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": user_message})
                payload = {
                    "model": model_name or "default",
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=300) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                if "choices" in result and len(result["choices"]) > 0:
                    c = result["choices"][0]
                    content = c.get("message", {}).get("content", "") or c.get("text", "")
                    return content.strip()
                elif "response" in result:
                    return result["response"].strip()
                self._last_ai_error = f"API格式异常: {str(result)[:200]}"
                return ""
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="replace")[:300]
                if e.code in (429, 502, 503, 504) and attempt < 2:
                    _time.sleep(2 * (attempt + 1))
                    continue
                self._last_ai_error = f"HTTP {e.code}: {body}"
                return ""
            except urllib.error.URLError as e:
                self._last_ai_error = f"连接失败: {str(e.reason)[:100]}"
                if attempt < 2:
                    _time.sleep(2 * (attempt + 1))
                    continue
                return ""
            except Exception as e:
                self._last_ai_error = f"错误: {str(e)[:100]}"
                if attempt < 2:
                    continue
                return ""
        return ""

    def _translate_prompt(self, text, direction, api_url, api_key, model_name, temperature, max_tokens):
        if not text or not api_url:
            return ""
        prefixes = {"中译英": "将以下中文翻译成英文", "英译中": "将以下英文翻译成中文", "日译中": "将以下日文翻译成中文"}
        prefix = prefixes.get(direction, prefixes["中译英"])
        sys_p = "You are a professional translator. Output only the translated text."
        user_msg = f"{prefix}，只输出翻译结果：\n\n{text}"
        return self._call_ai(api_url, api_key, model_name, sys_p, user_msg, temperature, max_tokens)

# ============================================================
# ComfyUI节点注册 — V19.0
# ============================================================
NODE_CLASS_MAPPINGS = {
    "PromptLibraryNodePro": PromptLibraryNodePro,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptLibraryNodePro": "提示词库节点 Pro V19",
}
