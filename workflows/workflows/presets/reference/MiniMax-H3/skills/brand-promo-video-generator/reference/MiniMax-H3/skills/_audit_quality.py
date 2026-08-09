# -*- coding: utf-8 -*-
"""
深度审查 6: 输出质量真实性测试
- 用真实的导演级场景跑节点
- 检查输出长度, 关键词, 内容质量
- 不接受空字符串, 不接受 stub 字符串
"""
import sys, importlib.util
from pathlib import Path

ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("pkg_init", str(ROOT / "__init__.py"))
pkg_init = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg_init)
NODE_MAP = pkg_init.NODE_CLASS_MAPPINGS


def real_scenario(ntype):
    """给每种节点一个真实场景输入"""
    real = {}
    cls = NODE_MAP[ntype]
    it = cls.INPUT_TYPES()
    for kind in ("required",):
        for k, sch in it.get(kind, {}).items():
            t = sch[0] if isinstance(sch, tuple) else sch
            if isinstance(t, list):
                # 枚举: 选一个真实的
                if ntype in ("ConceptPitchPro", "WorldBuildingPro", "ThemePhilosophyPro", "SoundDesignPro",
                            "MusicScorePro", "PerformanceDirectionPro", "CostumePropSetPro", "VfxPro",
                            "MvPro", "PictureBookPro", "InteractiveDramaPro", "QualityAssurancePro",
                            "EditingPro", "ColorGradingPro", "IterationPostPro"):
                    real[k] = "剧情短片"
                elif ntype == "DirectorSoulNode":
                    if k == "主导情感": real[k] = "渴望"
                    elif k.startswith("次要情感"): real[k] = "孤独"
                    elif k == "融合模式": real[k] = "叠加"
                    elif k == "导演": real[k] = "王家卫"
                    else: real[k] = t[0]
                elif ntype == "AestheticJudgmentPro":
                    if k == "导演风格": real[k] = "王家卫"
                    elif k == "场景类型": real[k] = "URBAN_EXTERIOR"
                    else: real[k] = t[0]
                elif ntype == "StyleGuidePro":
                    if k == "调色风格": real[k] = "冷调忧郁"
                    elif k == "配色方案": real[k] = "蓝绿互补"
                    elif k == "导演体系": real[k] = "王家卫"
                    else: real[k] = t[0]
                elif ntype == "ShotSelectionPro":
                    if k == "目标情感": real[k] = "渴望"
                    else: real[k] = t[0]
                elif ntype == "MarketAudiencePro":
                    if k == "类型": real[k] = "剧情"
                    elif k == "档期": real[k] = "暑期档"
                    elif k == "市场定位": real[k] = "中端商业"
                    else: real[k] = t[0]
                else:
                    real[k] = t[0]
            else:
                s = str(t).upper()
                if "BOOL" in s: real[k] = True
                elif "INT" in s: real[k] = 5
                elif "FLOAT" in s: real[k] = 0.7
                else:
                    # STRING: 给真实场景描述
                    if k in ("场景描述", "故事架构_来自节点1", "剧本正文_来自节点2"):
                        real[k] = "现代都市, 雨夜咖啡馆, 男女主角因一杯拿铁再次相遇, 回忆杀+长镜头+克制冷调"
                    elif k in ("输入文本", "输入描述"):
                        real[k] = "都市夜景, 霓虹灯, 雨湿街道, 孤独的男人走在路上, 内心独白"
                    elif k == "类型":
                        real[k] = "剧情短片"
                    elif k == "项目名":
                        real[k] = "雨夜咖啡馆"
                    elif k == "内容1":
                        real[k] = "第一段内容: 概念立项"
                    elif k == "内容2":
                        real[k] = "第二段内容: 剧本架构"
                    elif k == "内容3":
                        real[k] = "第三段内容: 调色归档"
                    else:
                        real[k] = f"真实的{k}输入"
    return real


print("=== 41 节点真实场景输出质量审查 ===\n")
print(f"{'NODE':<30} {'OUT_LEN':<10} {'TOTAL_CHARS':<15} {'KEY_HIT':<20} {'PASS'}")
print("-" * 100)

total_pass = 0
quality_issues = []

for name in NODE_MAP:
    try:
        cls = NODE_MAP[name]
        inst = cls()
        kwargs = real_scenario(name)
        fn = getattr(inst, cls.FUNCTION)
        ret = fn(**kwargs)
        if not isinstance(ret, tuple):
            ret = (ret,)
        out_len = len(ret)
        total_chars = sum(len(str(x)) for x in ret if x)
        # 质量检查: 总字符数 > 50, 且至少 1 个含真实关键词
        keywords_hit = 0
        for x in ret:
            if not x: continue
            s = str(x)
            for kw in ("导演", "镜头", "情感", "光", "色", "音", "画面", "场景", "调色", "叙事",
                       "构图", "光影", "节奏", "表演", "剧本", "故事", "角色", "对白", "构图", "空间"):
                if kw in s:
                    keywords_hit += 1
                    break
        is_real = total_chars > 50 and keywords_hit >= 1
        if is_real:
            total_pass += 1
            status = "OK"
        else:
            status = "WEAK"
            quality_issues.append((name, total_chars, keywords_hit, [str(x)[:50] for x in ret]))
        print(f"{name:<30} {out_len:<10} {total_chars:<15} {keywords_hit:<20} {status}")
    except Exception as e:
        print(f"{name:<30} EXC    {str(e)[:60]}")
        quality_issues.append((name, 0, 0, [str(e)]))

print(f"\n=== 总结 ===")
print(f"通过 (有真实输出): {total_pass}/41")
if quality_issues:
    print(f"\n=== 输出偏弱的节点 ({len(quality_issues)}) ===")
    for name, chars, kw, sample in quality_issues:
        print(f"\n[{name}] 字符={chars} 关键词命中={kw}")
        for s in sample[:2]:
            print(f"  样例: {s[:80]}")
