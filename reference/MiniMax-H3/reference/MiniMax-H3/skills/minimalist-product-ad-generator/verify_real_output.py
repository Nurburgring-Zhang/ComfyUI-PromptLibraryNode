# -*- coding: utf-8 -*-
"""
真实LLM输出验证harness — 闭合"输出从未用真实LLM验证"缺口

用法:
  python verify_real_output.py --api-url http://localhost:1234/v1/chat/completions \
                                --api-key YOUR_KEY --model gpt-4o \
                                --mode 电影分镜 --style 悬疑风 --shots 6 \
                                --topic "侦探追凶" --prompt-tier full

输出: 真实LLM生成的6镜分镜 + 知识库注入的system prompt(供对比) + 质量自评清单
用户配置真实API后即可验证输出质量是否达世界级(本脚本不模拟, 真实调用)
"""
import os, sys, json, argparse, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from director_engine import DirectorPromptBuilder
from engine_story_arc import ShotConstraints, PromptSegmenter, StoryArc
from pln_llm import call_ai


def run_real_verification(args):
    """真实LLM端到端验证(非模拟, 真实调用API)"""
    print("=" * 70)
    print("【真实LLM输出验证】— 知识库注入真实, AI调用真实")
    print(f"模式:{args.mode} 风格:{args.style} 镜数:{args.shots} tier:{args.prompt_tier}")
    print(f"导演:{args.directors} 叙事:{args.narrative or '自动'}")
    print(f"API:{args.api_url} 模型:{args.model}")
    print("=" * 70)

    # 构建导演引擎
    director_keys = args.directors.split(",") if args.directors else None
    is_vertical = "竖屏" in (args.camera or "")
    b = DirectorPromptBuilder(
        args.mode, args.style, args.color, args.topic, args.character, args.env,
        args.shots, camera_style=args.camera or "", is_vertical=is_vertical,
        director_keys=director_keys, narrative_structure=args.narrative or "",
        short_drama_type=args.drama_type or "", audience_archetype=args.audience or "",
    )
    b.prompt_mode = args.prompt_tier  # full / lean
    b.knowledge.set_directors(director_keys) if director_keys else None

    header = b.build_header()
    constraints = ShotConstraints()
    segments = []

    for i in range(args.shots):
        # 模拟beat(真实场景应从StoryArc解析, 此处用进度推断)
        beat = {
            "beat_name": ["开场","铺垫","转折","中点","高潮","余韵"][min(i,5)],
            "emotion_value": [0.5,0.4,0.6,0.7,0.9,0.3][min(i,5)],
            "intensity": [0.4,0.4,0.6,0.7,0.95,0.4][min(i,5)],
            "narrative_func": ["冷开场","铺垫","转折","中点反转","终极对决","余韵收束"][min(i,5)],
            "story_progress": (i+1)/args.shots,
            "recommended_shot_types": ["远景","中景","双人","过肩","全景","中近"][min(i,5)].split("/"),
        }
        sys_p = b.build_system_prompt(i, beat, constraints.get_constraints_text())
        user_p = (
            f"主题: {args.topic}\n角色: {args.character}\n环境: {args.env}\n"
            f"第{i+1}/{args.shots}镜。风格: {args.style}。\n请输出第{i+1}镜内容。\n"
        )
        # 真实LLM调用(非模拟)
        t0 = time.time()
        ai_result, err = call_ai(args.api_url, args.api_key, args.model,
                                   sys_p, user_p, args.temperature, args.max_tokens)
        dt = time.time() - t0
        if err:
            print(f"\n✗ 第{i+1}镜 AI调用失败: {err}")
            return
        print(f"\n--- 第{i+1}/{args.shots}镜 (tier={args.prompt_tier}, prompt={len(sys_p)}字符, 耗时{dt:.1f}s) ---")
        print(f"  [system prompt注入的导演决策]:")
        for key in ["运镜触发条件","布光触发","叙事结构指导","表演指导"]:
            if key in sys_p:
                # 取该章节首行
                idx = sys_p.find(key)
                line = sys_p[idx:sys_p.find("\n", idx)]
                print(f"    {line[:80]}")
        print(f"  [LLM真实输出]:")
        print(ai_result[:500] + ("..." if len(ai_result)>500 else ""))
        b.record_shot_result(i, ai_result, beat)
        segments.append(f"{header}\n【镜头{i+1}/{args.shots}】\n{ai_result}\n")

    output = PromptSegmenter.join_outputs(segments)
    # 保存完整输出
    out_file = f"verified_output_{int(time.time())}.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"=== 真实LLM验证输出 ===\n模式:{args.mode} 风格:{args.style} 镜数:{args.shots} tier:{args.prompt_tier}\n")
        f.write(f"API:{args.api_url} 模型:{args.model} 导演:{args.directors}\n")
        f.write(f"生成时间:{time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(output)
    print(f"\n{'='*70}")
    print(f"✓ 真实验证完成, 完整输出: {out_file}")
    print(f"✓ 提示词tier: {args.prompt_tier} ({'完整决策上下文' if args.prompt_tier=='full' else '精简'})")
    print(f"\n【质量自评清单(请人工评判是否达世界级)】")
    print("  □ 故事连续性: 各镜是否自然衔接前文(无跳跃)?")
    print("  □ 导演风格落地: 选定导演的视觉技法是否在画面中体现?")
    print("  □ 张弛有度: 强度曲线是否合理(无连续高潮脱敏)?")
    print("  □ 表演具体: 是否用微表情/肢体而非抽象情绪词?")
    print("  □ 镜头连续性: 角色/光线/道具跨镜一致?")
    print("  □ 时空锚定: 每镜开头有时间·空间前缀?")
    print("  □ 类型视觉: 类型片视觉语言(布光/构图/色彩)是否落地?")
    print("  □ 整体水准: 与IMDB顶级导演分镜对比, 是否达世界级?")
    print(f"\n若未达世界级, 调整: --prompt-tier lean/full对比, 或换更强模型, 或调temperature。")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="真实LLM输出验证harness")
    p.add_argument("--api-url", required=True, help="OpenAI兼容API地址")
    p.add_argument("--api-key", default="", help="API密钥")
    p.add_argument("--model", required=True, help="模型名(如gpt-4o)")
    p.add_argument("--mode", default="电影分镜", help="模式")
    p.add_argument("--style", default="悬疑风", help="画面风格")
    p.add_argument("--color", default="冷调", help="色彩基调")
    p.add_argument("--topic", default="侦探追凶", help="故事主题")
    p.add_argument("--character", default="侦探林寒, 目标周明", help="角色")
    p.add_argument("--env", default="雨夜都市", help="环境")
    p.add_argument("--shots", type=int, default=6, help="镜头数")
    p.add_argument("--camera", default="", help="运镜风格")
    p.add_argument("--directors", default="fincher,hitchcock", help="导演(逗号分隔)")
    p.add_argument("--narrative", default="", help="叙事结构(空=自动)")
    p.add_argument("--drama-type", default="", help="短剧类型")
    p.add_argument("--audience", default="", help="目标受众")
    p.add_argument("--prompt-tier", default="full", choices=["full","lean"], help="prompt层级")
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--max-tokens", type=int, default=10000)
    args = p.parse_args()
    run_real_verification(args)
