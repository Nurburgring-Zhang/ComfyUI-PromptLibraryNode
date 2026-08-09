# -*- coding: utf-8 -*-
"""
Step 1: 自我质疑 - 主动质疑当前节点输出中的潜在问题
诚实审视,不回避
"""
import sys, importlib.util
from pathlib import Path
ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("pkg_init", str(ROOT / "__init__.py"))
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)


def sample(ntype, kwargs, method):
    inst = pkg.NODE_CLASS_MAPPINGS[ntype]()
    return getattr(inst, method)(**kwargs)


# 王家卫 + 2046 雨夜酒店
WKW = {
    "ConceptPitchPro": ({
        "任务类型": "single_scene", "类型": "剧情短片",
        "场景描述": "2046 - 雨夜, 酒店走廊, 男人写小说, 孤独时空",
        "导演风格": "王家卫", "情绪基调": "孤独", "潜文本_情感": "等待与失去",
        "导演意图_观众应感到": "时空交错的怅惘",
        "关键道具": "钢笔, 烟, 打字机", "关键参考片": "2046, 花样年华",
        "启用反AI规则": True, "灵魂融合情感": "tender", "灵魂融合权重": "0.6",
        "灵魂融合模式": "auto", "灵魂维度JSON": "{}", "灵魂状态JSON": "{}",
        "灵魂导演": "王家卫",
    }, "build_concept"),
    "EditingPro": ({
        "任务类型": "single_scene", "类型": "剧情短片",
        "场景描述": "2046 - 雨夜, 酒店走廊", "导演风格": "王家卫",
        "情绪节奏": "低", "切点策略": "动作中切", "长镜占比": 0.6,
        "跳切场景": "敲门", "蒙太奇": "是", "静音切": "是", "镜头类型": "中景",
        "启用反AI规则": True,
    }, "build_edit"),
    "PerformanceDirectionPro": ({
        "任务类型": "single_scene", "类型": "剧情短片",
        "场景描述": "2046 - 雨夜", "导演风格": "王家卫",
        "情绪基调": "孤独", "潜文本_情感": "等待与失去",
        "导演意图_观众应感到": "怅惘",
        "关键道具": "钢笔, 烟", "关键参考片": "2046", "启用反AI规则": True,
    }, "build_performance"),
    "SilenceMasteryPro": ({
        "场景类型": "intimate", "场景描述": "2046 - 雨夜, 酒店",
        "实际对白数": 4, "沉默总时长秒": 18, "每句对白前停顿秒": 0.6,
        "对白前停顿占比": 0.4, "对白间沉默占比": 0.3, "动作后停顿占比": 0.2,
        "眼神对视占比": 0.4, "空镜留白占比": 0.2, "导演风格": "王家卫",
        "启用反AI规则": True,
    }, "build_silence"),
}

# 自我质疑: 我作为审计者, 找每个节点输出中的"问题"
print("=" * 80)
print("自我质疑 - 主动找潜在问题 (Mavis 自审)")
print("=" * 80)

self_issues = []

for ntype, (kwargs, method) in WKW.items():
    print(f"\n{'='*80}")
    print(f"节点: {ntype}")
    print(f"{'='*80}")
    ret = sample(ntype, kwargs, method)
    if not isinstance(ret, tuple):
        ret = (ret,)
    text = str(ret[0])

    # === 我主动质疑的问题 ===
    issues = []

    # 1. 词汇重复
    import re
    from collections import Counter
    # 提取中文 2+ 字词
    words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
    counter = Counter(words)
    top_repeats = [(w, c) for w, c in counter.most_common(10) if c >= 5]
    if top_repeats:
        issues.append(f"高频重复词 (出现 5+ 次): {top_repeats[:3]}")

    # 2. 模板感 (同样的句子结构重复 3+ 次)
    sentences = re.split(r'[。\n]', text)
    sentence_starts = [s.strip()[:15] for s in sentences if len(s.strip()) > 15]
    start_counter = Counter(sentence_starts)
    template_starts = [(s, c) for s, c in start_counter.most_common(5) if c >= 3]
    if template_starts:
        issues.append(f"模板句式 (3+ 次): {template_starts[:2]}")

    # 3. 句号/换行密度 - 太密像 list, 太稀像散文
    n_sentences = len([s for s in sentences if s.strip()])
    n_chars = len(text)
    if n_chars > 0:
        density = n_sentences / n_chars
        if density > 0.05:  # 一句 20 字内
            issues.append(f"句式过密 ({n_sentences} 句 / {n_chars} 字, 密度 {density:.3f})")
        if density < 0.005:  # 200 字一句
            issues.append(f"句式过疏 ({n_sentences} 句 / {n_chars} 字, 密度 {density:.3f})")

    # 4. 信息密度 - 标点符号分布
    n_punct = sum(1 for c in text if c in '【】()（）:：')
    if n_punct > 0 and n_chars > 0:
        punct_ratio = n_punct / n_chars
        if punct_ratio > 0.15:
            issues.append(f"标点过多 ({n_punct} 标点 / {n_chars} 字, 比例 {punct_ratio:.3f}) - 像目录不像内容")

    # 5. 数字/英文 vs 中文 - 数据感 vs 文学感
    n_english = sum(1 for c in text if c.isascii() and c.isalpha())
    n_chinese = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    if n_chinese > 0:
        en_ratio = n_english / n_chinese
        if en_ratio > 0.5:
            issues.append(f"英文/中文比例过高 ({n_english}/{n_chinese} = {en_ratio:.2f}) - 数据感过强")

    # 6. 关键概念覆盖度
    must_have = {
        "ConceptPitchPro": ["导演", "情绪", "场景", "节奏", "灵魂"],
        "EditingPro": ["镜头", "切", "节奏", "静默", "对白"],
        "PerformanceDirectionPro": ["动作", "表情", "沉默", "身体", "情感"],
        "SilenceMasteryPro": ["沉默", "停顿", "空镜", "余韵", "对白"],
    }
    if ntype in must_have:
        missing = [w for w in must_have[ntype] if w not in text]
        if missing:
            issues.append(f"关键概念缺失: {missing}")

    # 7. 段落结构
    sections = text.split('【')
    n_sections = len(sections) - 1
    if n_sections > 20:
        issues.append(f"段落过多 ({n_sections} 段) - 看起来像目录")

    # 8. 反 AI 检测 - 是不是真的没有 AI 味
    ai_words = ["绝美", "视觉盛宴", "精致", "震撼", "史诗", "叹为观止",
                "巧夺天工", "独具匠心", "完美", "极致", "惊艳", "无与伦比"]
    ai_hits = [w for w in ai_words if w in text]
    if ai_hits:
        issues.append(f"AI 味残留: {ai_hits}")

    # 9. 自我解释 - 节点设计是否服务于"导演实战"目标
    if "ConceptPitchPro" in ntype:
        # 这是 prompt 模板节点, 不是 narrative 输出
        if n_punct / n_chars < 0.05:
            issues.append("ConceptPitchPro 应该是模板节点, 但格式不够清晰 (标点过少)")
    if "PerformanceDirectionPro" in ntype:
        # 应该含具体微动作
        micro_actions = ["手", "眼", "头", "肩", "背", "呼吸", "眉", "指", "握"]
        missing_micro = [w for w in micro_actions if w not in text]
        if len(missing_micro) > 5:
            issues.append(f"PerformanceDirectionPro 缺具体微动作: {missing_micro}")

    print(f"\n输出长度: {len(text)} 字符")
    print(f"自我质疑发现的问题 ({len(issues)} 个):")
    for iss in issues:
        print(f"  ❌ {iss}")
    self_issues.append({"node": ntype, "issues": issues, "len": len(text)})

# 总结
total = sum(len(r["issues"]) for r in self_issues)
print(f"\n{'='*80}")
print(f"自我质疑总问题: {total}")
print(f"按节点:")
for r in self_issues:
    print(f"  {r['node']}: {len(r['issues'])} 个问题")
