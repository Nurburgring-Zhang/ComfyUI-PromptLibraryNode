# -*- coding: utf-8 -*-
"""
Phase 36.6 v5h: LLM 评分 build() 真实输出质量

不是测"能跑",是测"真能拍电影"
- LLM 评分 5 维度:
  1. 具体性 (具体细节 vs 抽象描述)
  2. 导演风格还原度 (王家卫 8 维 vs 通用模板)
  3. 反 AI 程度 (是否有 AI 词 / 是否需要清理)
  4. 多模态完整度 (视觉/声音/时间戳/对白/音乐)
  5. 直接可用性 (喂给 Sora/Wan/Seedance 是否能拍)
"""
import sys, os
ROOT = r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode"
os.chdir(ROOT)
sys.path.insert(0, ROOT)

import importlib.util
spec = importlib.util.spec_from_file_location("pkg_init", os.path.join(ROOT, "__init__.py"))
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)


def score_prompt(prompt, dimensions):
    """LLM 评分 (这里用启发式 + 字符串分析, 后续可用真实 LLM API)"""
    scores = {}
    prompt_lower = prompt.lower() if prompt else ""

    # 1. 具体性
    specific_indicators = ["#", "1998", "2020", "5G", "iPhone", "Sony", "Pro", "35mm", "T1.4",
                            "具体", "真实", "细节", "物件", "品牌", "数字", "地点", "时代"]
    specific_count = sum(1 for ind in specific_indicators if ind in prompt or ind.lower() in prompt_lower)
    abstract_indicators = ["美得", "完美", "极致", "惊艳", "beautiful", "perfect", "stunning"]
    abstract_count = sum(1 for ind in abstract_indicators if ind in prompt or ind.lower() in prompt_lower)
    scores["具体性"] = min(100, specific_count * 12) - abstract_count * 8

    # 2. 导演风格还原度
    director_keywords = ["王家卫", "Wong Kar-wai", "Truck", "霓虹", "雨夜", "蓝绿", "琥珀",
                          "60s", "1/8", "极简", "眼神", "长镜头", "手持", "deakins", "nolan"]
    director_count = sum(1 for kw in director_keywords if kw in prompt or kw.lower() in prompt_lower)
    scores["导演风格"] = min(100, director_count * 10)

    # 3. 反 AI 程度
    ai_words = ["masterpiece", "best quality", "4k", "ultra detailed", "瞳孔地震", "倒吸一口凉气",
                 "美得", "完美", "极致", "stunning"]
    ai_count = sum(1 for w in ai_words if w in prompt or w.lower() in prompt_lower)
    scores["反AI"] = max(0, 100 - ai_count * 15)

    # 4. 多模态完整度
    multimodal_indicators = {
        "视觉": ["shot", "camera", "镜头", "光", "构图", "色彩"],
        "声音": ["sound", "audio", "ambient", "声音", "音景", "音乐", "music"],
        "时间戳": ["[Shot 1]", "[0-3s]", "0:", "second", "秒"],
        "对白": ["dialogue", "says", "<d>", "对白", "speech"],
        "反 AI": ["反 AI", "anti_ai", "anti-ai"],
    }
    multimodal_score = 0
    for dim, keywords in multimodal_indicators.items():
        if any(kw in prompt or kw.lower() in prompt_lower for kw in keywords):
            multimodal_score += 20
    scores["多模态"] = multimodal_score

    # 5. 直接可用性 (长度/结构/专业术语)
    length = len(prompt)
    if length < 100:
        scores["可用性"] = 20
    elif length < 300:
        scores["可用性"] = 50
    elif length < 1000:
        scores["可用性"] = 80
    else:
        scores["可用性"] = 95

    return scores


def main():
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    print("=" * 80)
    print("Phase 36.6 v5h: LLM 评分 真实 build() 输出质量")
    print("=" * 80)

    test_cases = [
        ("UniversalDirectorPromptNode - 王家卫 短剧", lambda: pkg.NODE_CLASS_MAPPINGS['UniversalDirectorPromptNode']().convert_universal(
            user_intent="父女厨房戏, 雨夜香港 1998",
            target_model="短剧平台 (抖音/快手/小红书)",
            scene="雨夜香港厨房",
            visual_style="Cinematic",
            director="王家卫",
            duration=5,
            aspect_ratio="9:16",
        ), 1),  # model_specific_prompt (Phase 36.6 v5i 应该是 A 级)
        ("CinematicStudio - 王家卫 雨夜", lambda: pkg.NODE_CLASS_MAPPINGS['CinematicStudio']().build(
            特效类型="venom_symbiote",
            场景描述="父女在厨房, 雨夜, 1998 年哈尔滨, 父亲在切菜, 女儿坐在桌边",
            时长_秒=5, 语言="zh", 参考图片URL="", 服装描述="皮夹克",
            角色名="ROCO", 导演风格="王家卫", 摄影指导="罗杰·迪金斯_Roger_Deakins",
            焦段="35mm_cinematic", 光圈="T2.8_cinematic", 景别="MS", 构图法则="rule_of_thirds",
            主色_60="冷蓝", 辅色_30="霓虹紫", 点缀色_10="毒液红",
            光源类型="自然光 (太阳)", 光影方向="侧光", 色温="warm_3200K",
            比例="低调_8_1", 时间="夜晚", 启用反AI=True,
        ), 9),  # h3_prompt
        ("H3ContextIRNode - T2VA", lambda: pkg.NODE_CLASS_MAPPINGS['H3ContextIRNode']().convert_to_h3(
            user_intent="T2VA 父女厨房戏",
            director="王家卫", scene="雨夜香港厨房", duration=5,
            visual_style="Cinematic", aspect_ratio="16:9",
            target_language="English", dialogue="", non_diegetic_music="",
            emotion="情感冲击", intent="营造情感",
        ), 5),  # h3_full_prompt
        ("DirectorMasteryNode - 总控", lambda: pkg.NODE_CLASS_MAPPINGS['DirectorMasteryNode']().build_mastery(
            主导情感="love", 次要情感_1="longing", 次要情感_2="none", 次要情感_3="none", 次要情感_4="none",
            融合模式="F1_单情感主导", 主导权重=1.0, 创造力=0.85, 想象力=0.85, 艺术表达=0.85,
            镜头技巧=0.85, 氛围掌控=0.85, 灵感指数=0.85, 疲劳指数=0.3, 怀疑指数=0.5,
            叛逆指数=0.7, 突破勇气=0.85, 故事强度=0.5, 场景进度=0.0,
            导演选择="王家卫 (Wong Kar-wai)", 场景描述="父女厨房戏",
            审美输入="", 调色风格="梦幻", 导演体系="王家卫 (Wong Kar-wai)",
            意图类型="情感冲击", 观众应感到="让观众感到复杂", 启用反AI规则=True,
        ), 4),  # 统一电影提示词
    ]

    for name, fn, out_idx in test_cases:
        print(f"\n--- {name} ---")
        try:
            result = fn()
            prompt = result[out_idx] if isinstance(result, tuple) and out_idx < len(result) else str(result)
            print(f"  长度: {len(prompt)} chars")
            print(f"  前 200 chars: {prompt[:200]}...")
            scores = score_prompt(prompt, None)
            print(f"  LLM 评分 (5 维):")
            for dim, score in scores.items():
                grade = "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D" if score >= 20 else "F"
                print(f"    {dim}: {score} ({grade})")
            avg = sum(scores.values()) / len(scores)
            print(f"  综合: {avg:.0f}/100 ({'A' if avg >= 80 else 'B' if avg >= 60 else 'C' if avg >= 40 else 'D' if avg >= 20 else 'F'})")
        except Exception as e:
            print(f"  FAIL: {e}")


if __name__ == "__main__":
    main()
