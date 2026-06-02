# ============================================================
# 工具函数 — 文件扫描/过滤/解析/缓存/图片加载
# ============================================================
import os
import re
import random
import json
import threading

import torch
import numpy as np
from PIL import Image


# 预编译正则表达式
_RE_SD_PARENS = re.compile(r'\(\([^)]*\)\)')
_RE_SD_BRACKETS = re.compile(r'\[\[[^\]]*\]\]')
_RE_SD_CURLY = re.compile(r'\{[^}]*\}')
_RE_CJK = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')
_RE_ASCII_ONLY = re.compile(r'[^\x00-\x7F]')
_RE_MULTISPACE = re.compile(r'\s+')

# 无生命关键词（用于智能过滤）
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

# 白名单词（用于主体过滤）
WHITELIST_WORDS = [
    "人", "人物", "人像", "肖像", "女孩", "男孩", "女人", "男人",
    "美女", "帅哥", "少女", "仙女", "精灵", "天使",
    "公主", "王子", "女王", "国王", "骑士", "战士", "法师",
    "猫", "狗", "兔子", "鸟", "龙", "狮子", "老虎",
    "风景", "日落", "日出", "山脉", "海滩", "森林", "星空",
    "portrait", "woman", "man", "girl", "boy",
    "cat", "dog", "dragon", "lion", "tiger",
]

# 强主体信号（用于主体过滤器）
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


def parse_keywords(kw_str):
    """解析关键词字符串"""
    if not kw_str or not kw_str.strip():
        return []
    return [k.strip() for k in kw_str.split(",") if k.strip()]


def parse_tags(tag_str):
    """解析标签字符串"""
    if not tag_str or not tag_str.strip():
        return []
    return [t.strip() for t in tag_str.split(",") if t.strip()]


def scan_files(folder_path):
    """扫描文件夹中的提示词文件"""
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


def file_has_tag(filepath, wanted_tags):
    """检查文件名是否包含标签"""
    fname = os.path.basename(filepath).lower()
    return any(tag.lower() in fname for tag in wanted_tags)


def load_lines(files, keywords, max_lines=0):
    """加载提示词文件中的所有行"""
    all_lines = []
    total_bytes = 0
    MB = 50 * 1024 * 1024
    for fp in files:
        if total_bytes >= MB:
            break
        try:
            fsize = os.path.getsize(fp)
            if fsize > MB:
                lines = _stream_load(fp, max_lines or 5000)
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


def _stream_load(fp, limit):
    """流式读取大文件前N行"""
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


def smart_filter(lines):
    """智能过滤：保留有主体/非纯静物的行"""
    if not lines:
        return None
    filtered = []
    for entry in lines:
        text = entry["text"]
        has_subject = any(s in text for s in STRONG_SUBJECT_SIGNALS)
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
        if not any(kw in text for kw in LIFELESS_KEYWORDS):
            filtered.append(entry)
    if len(filtered) == len(lines):
        return None
    return filtered


def filter_by_subject(lines):
    """纯主体过滤"""
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


def pick_n_lines(lines, mode, loop_mode, count, folder_path, cache):
    """从lines中选择N条（随机/顺序/洗牌/权重）"""
    if not lines:
        return [], cache

    cache_key = f"idx_{folder_path}"
    cache_lock = threading.Lock()

    with cache_lock:
        state = cache.get(cache_key, {})
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
        with cache_lock:
            cache[cache_key] = {"idx": idx}
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
        with cache_lock:
            cache[cache_key] = {"idx": idx, "shuffled": shuffled}
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
    return chosen, cache


def history_dedup(chosen, folder_path, cache):
    """历史去重（50条缓存）"""
    cache_key = f"hist_{folder_path}"
    cache_lock = threading.Lock()
    with cache_lock:
        hist = cache.get(cache_key, [])
    deduped = []
    for e in chosen:
        if e["text"] not in hist:
            deduped.append(e)
            hist.append(e["text"])
        if len(deduped) >= len(chosen):
            break
    if len(hist) > 50:
        hist = hist[-50:]
    with cache_lock:
        cache[cache_key] = hist
    return deduped


def parse_ref_image_list(ref_list_str):
    """解析参考图列表JSON字符串"""
    if not ref_list_str or ref_list_str.strip() in ("", "[]"):
        return []
    try:
        items = json.loads(ref_list_str)
        if not isinstance(items, list):
            return []
        valid = []
        for item in items:
            if isinstance(item, dict) and "filename" in item:
                valid.append(item)
                if len(valid) >= 9:
                    break
        return valid
    except (json.JSONDecodeError, TypeError):
        return []


def load_ref_image_tensors(file_items):
    """从文件信息列表加载图片为IMAGE tensor，过滤>4096的"""
    if not file_items:
        return []
    tensors = []
    try:
        import folder_paths
        for item in file_items:
            try:
                filename = item.get("filename", "")
                subfolder = item.get("subfolder", "")
                img_type = item.get("type", "input")
                img_path = folder_paths.get_annotated_filepath(f"{filename} [input]")
                if not os.path.isfile(img_path):
                    input_dir = folder_paths.get_input_directory()
                    img_path = os.path.join(input_dir, filename)
                    if not os.path.isfile(img_path):
                        continue

                pil_img = Image.open(img_path).convert("RGB")
                w, h = pil_img.size
                if w > 4096 or h > 4096:
                    continue

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


def generate_negative_prompt(custom_negative, main_content):
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
