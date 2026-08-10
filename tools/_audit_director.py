# -*- coding: utf-8 -*-
"""
内容质量全量审计 - 顶级导演标准
- 6 个世界级导演,6 个真实场景
- 抽样关键节点,看输出
- 评估: 机械控制/AI味/叙事/故事线/氛围/留白/微表情
"""
import sys, importlib.util, json
from pathlib import Path

ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("pkg_init", str(ROOT / "__init__.py"))
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)
NODE_MAP = pkg.NODE_CLASS_MAPPINGS

# 6 个世界级导演 + 6 个真实场景
DIRECTORS = [
    ("王家卫", "2046", "雨夜, 酒店走廊, 男人写小说, 孤独时空"),
    ("塔可夫斯基", "镜子", "俄罗斯乡村, 母亲独居, 木屋, 风, 童年回忆"),
    ("黑泽明", "七武士", "战国日本, 农民找武士, 山村, 战乱前夕"),
    ("侯孝贤", "刺客聂隐娘", "唐代, 山雾, 女人内心, 朝廷暗杀, 克制"),
    ("诺兰", "盗梦空间", "酒店走廊, 重力翻转, 潜意识迷宫, 时间压力"),
    ("小津安二郎", "东京物语", "战后日本, 老人探望子女, 茶室, 海边, 失落"),
]


def real_scenario(ntype, director, film, scene):
    """给节点真实导演场景"""
    cls = NODE_MAP[ntype]
    it = cls.INPUT_TYPES()
    kwargs = {}
    for kind in ("required",):
        for k, sch in it.get(kind, {}).items():
            t = sch[0] if isinstance(sch, tuple) else sch
            if isinstance(t, list):
                # 枚举: 选择最相关的
                if ntype == "ConceptPitchPro":
                    if k == "任务类型": kwargs[k] = "single_scene"
                    elif k == "类型": kwargs[k] = "剧情短片"
                    elif k == "导演风格": kwargs[k] = director
                    elif k == "灵魂融合模式": kwargs[k] = "auto"
                    elif k == "灵魂导演": kwargs[k] = director
                    else: kwargs[k] = t[0] if t else ""
                elif ntype == "DirectorStoryboardPro":
                    if k == "导演风格_8选1": kwargs[k] = director
                    elif k == "景别偏好": kwargs[k] = "中景"
                    elif k == "摄影机运动": kwargs[k] = "固定"
                    elif k == "光线风格": kwargs[k] = "自然光"
                    elif k == "色彩基调": kwargs[k] = "低饱和"
                    elif k == "剪辑节奏": kwargs[k] = "长镜头"
                    elif k == "声音设计": kwargs[k] = "环境音"
                    else: kwargs[k] = t[0] if t else ""
                elif ntype == "ColorGradingPro":
                    if k == "任务类型": kwargs[k] = "single_scene"
                    elif k == "类型": kwargs[k] = "剧情短片"
                    elif k == "导演风格": kwargs[k] = director
                    elif k == "色彩风格": kwargs[k] = "低饱和度"
                    elif k == "焦段": kwargs[k] = "50mm"
                    elif k == "光圈": kwargs[k] = "f2.8"
                    elif k == "景别": kwargs[k] = "中景"
                    elif k == "构图法则": kwargs[k] = "三分法"
                    elif k == "主色_60": kwargs[k] = "冷蓝灰"
                    elif k == "辅色_30": kwargs[k] = "暖橘"
                    elif k == "点缀色_10": kwargs[k] = "深红"
                    elif k == "一级调色": kwargs[k] = "normal"
                    elif k == "二级调色": kwargs[k] = "normal"
                    elif k == "创意调色": kwargs[k] = "normal"
                    elif k == "光源类型": kwargs[k] = "自然光"
                    elif k == "光影方向": kwargs[k] = "侧光"
                    elif k == "色温": kwargs[k] = "5600K"
                    elif k == "比例": kwargs[k] = "16:9"
                    elif k == "时间": kwargs[k] = "黄昏"
                    else: kwargs[k] = t[0] if t else ""
                elif ntype == "PerformanceDirectionPro":
                    if k == "任务类型": kwargs[k] = "single_scene"
                    elif k == "类型": kwargs[k] = "剧情短片"
                    elif k == "导演风格": kwargs[k] = director
                    else: kwargs[k] = t[0] if t else ""
                elif ntype == "SilenceMasteryPro":
                    if k == "场景类型": kwargs[k] = "intimate"
                    elif k == "导演风格": kwargs[k] = director
                    else: kwargs[k] = t[0] if t else ""
                else:
                    kwargs[k] = t[0] if t else ""
            else:
                s = str(t).upper()
                if "BOOL" in s: kwargs[k] = True
                elif "INT" in s: kwargs[k] = 1
                elif "FLOAT" in s: kwargs[k] = 0.7
                else:
                    if k in ("场景描述", "输入描述", "输入文本"):
                        kwargs[k] = f"{film} - {scene}"
                    else:
                        kwargs[k] = f"{film} - {scene}"
    return kwargs


# 关键节点
KEY_NODES = [
    "ConceptPitchPro", "ScriptArchitecturePro", "ScriptBodyPro",
    "DirectorStoryboardPro", "PerformanceDirectionPro", "ColorGradingPro",
    "SilenceMasteryPro", "EditingPro", "SoundDesignPro", "MusicScorePro",
    "ArtDirectionPro", "DirectorIntentPro", "SpatialConsistencyPro",
    "WorldBuildingPro", "ThemePhilosophyPro", "DirectorSoulNode",
    "ShotSelectionPro", "AestheticJudgmentPro",
]

# 评估标准
def evaluate_output(text):
    """返回评估报告"""
    if not text or len(text) < 50:
        return {"score": 0, "issues": ["输出过短"]}
    issues = []
    score = 100

    # 1. 机械控制检测 - 真正的"步骤式"模板, 排除专业分镜 (Shot 1/2/3, Beat 1/2/3)
    import re
    # 真正的"机械步骤"模式: "Step 1: ... Step 2: ...", "第一步: ...第二步: ...第三步: ..."
    mechanical_patterns = [
        r"步骤\s*\d+[:：]",
        r"第[一二三四五]步[，,：:.]",
        r"Step\s*\d+[:：]",
        r"接下来.*?按照以下",
        r"在当今.*?的时代",
        r"此片段展示了",
        r"此镜头展现了",
        r"本段描述了",
    ]
    for pat in mechanical_patterns:
        if re.search(pat, text):
            issues.append(f"机械模板: '{pat}'")
            score -= 10
    # 排除专业分镜 (Shot 1/2/3 是合理的)
    if re.search(r"Shot\s*\d+", text) and not re.search(r"Step\s*\d+", text):
        pass  # 这是专业分镜, 不扣分

    # 2. AI味检测 - 空洞形容词
    ai_cliches = ["绝美伦比", "视觉盛宴", "精致入微", "震撼人心",
                  "令人惊叹", "无与伦比", "叹为观止", "精彩纷呈",
                  "美轮美奂", "巧夺天工", "史诗级", "独具匠心",
                  "渲染出", "展现出", "体现出", "彰显出", "凸显出"]
    for ac in ai_cliches:
        if ac in text:
            issues.append(f"AI味: '{ac}'")
            score -= 8

    # 3. 微表情/肢体语言关键词
    body_words = ["眼", "手", "背", "肩", "呼吸", "眉", "指", "步", "头", "脸"]
    body_count = sum(1 for w in body_words if w in text)
    if body_count < 2 and len(text) > 500:
        issues.append("缺微表情/肢体语言细节")
        score -= 15

    # 4. 留白/沉默关键词
    silence_words = ["沉默", "无声", "停顿", "留白", "空镜", "寂静", "呼吸声",
                    "安静", "静默", "余韵", "间奏", "间断"]
    silence_count = sum(1 for w in silence_words if w in text)
    if silence_count < 1 and len(text) > 500:
        issues.append("缺留白/沉默设计")
        score -= 10

    # 5. 光/音/色/空间氛围
    atmosphere_words = ["光", "影", "色", "声", "景深", "构图", "空间",
                        "色调", "明暗", "音", "环境", "质感", "温度", "湿度"]
    atmo_count = sum(1 for w in atmosphere_words if w in text)
    if atmo_count < 3 and len(text) > 500:
        issues.append(f"氛围词少({atmo_count}/13)")
        score -= 8

    # 6. 因果/叙事逻辑
    logic_words = ["因为", "所以", "但是", "然而", "于是", "然后", "由于", "尽管"]
    logic_count = sum(1 for w in logic_words if w in text)
    if logic_count < 1 and len(text) > 500:
        issues.append("缺叙事逻辑连接词")
        score -= 5

    return {
        "score": max(0, score),
        "issues": issues,
        "body_count": body_count,
        "silence_count": silence_count,
        "atmo_count": atmo_count,
        "logic_count": logic_count,
    }


# 跑全量
print("=" * 80)
print("内容质量全量审计 (6 导演 × 18 节点 = 108 输出)")
print("=" * 80)

results = []
total_outputs = 0
total_score = 0
total_issues = 0

for director, film, scene in DIRECTORS:
    print(f"\n{'='*80}")
    print(f"导演: {director} | 作品: {film} | 场景: {scene}")
    print(f"{'='*80}")
    for ntype in KEY_NODES:
        try:
            cls = NODE_MAP[ntype]
            inst = cls()
            kwargs = real_scenario(ntype, director, film, scene)
            fn = getattr(inst, cls.FUNCTION)
            ret = fn(**kwargs)
            if not isinstance(ret, tuple):
                ret = (ret,)
            for i, x in enumerate(ret):
                if x is None:
                    continue
                text = str(x)
                if not text.strip():
                    continue
                eval_result = evaluate_output(text)
                total_outputs += 1
                total_score += eval_result["score"]
                total_issues += len(eval_result["issues"])
                results.append({
                    "director": director, "film": film, "node": ntype,
                    "output_idx": i, "len": len(text),
                    "score": eval_result["score"],
                    "issues": eval_result["issues"],
                    "body": eval_result["body_count"],
                    "silence": eval_result["silence_count"],
                    "atmo": eval_result["atmo_count"],
                    "logic": eval_result["logic_count"],
                })
                # 只看每个节点第一个 output
                break
        except Exception as e:
            results.append({
                "director": director, "film": film, "node": ntype,
                "error": str(e)[:100],
            })

# 总结
print(f"\n{'='*80}")
print(f"总输出: {total_outputs}")
print(f"平均分: {total_score / max(1, total_outputs):.1f}/100")
print(f"总问题: {total_issues}")
print(f"{'='*80}")

# 找问题最多的节点
print(f"\n=== 问题节点排名 (按平均分) ===")
from collections import defaultdict
node_scores = defaultdict(list)
for r in results:
    if "score" in r:
        node_scores[r["node"]].append(r["score"])

for n, scores in sorted(node_scores.items(), key=lambda x: sum(x[1])/len(x[1])):
    avg = sum(scores) / len(scores)
    print(f"  {n}: 平均 {avg:.1f}/100 ({len(scores)} 输出)")

# 输出问题最严重的 10 个
print(f"\n=== Top 10 问题输出 (score < 60) ===")
bad = sorted([r for r in results if "score" in r and r["score"] < 60], key=lambda x: x["score"])[:10]
for r in bad:
    print(f"  [{r['director']} {r['film']}] {r['node']}.out{r['output_idx']}: {r['score']}/100")
    for iss in r["issues"][:3]:
        print(f"     - {iss}")

# 保存详细
with open(ROOT / "_audit_director.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n详细报告: _audit_director.json")
