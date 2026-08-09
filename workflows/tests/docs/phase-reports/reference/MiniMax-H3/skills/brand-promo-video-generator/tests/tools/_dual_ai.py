# -*- coding: utf-8 -*-
"""
Step 2: 双 AI 互审 - M3 生成输出, M2.7 审查
- M3 (主) 是我自己用的模型
- M2.7 (副) 是不同版本, 用作独立审查者
"""
import sys, importlib.util, json, subprocess
from pathlib import Path

ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("pkg_init", str(ROOT / "__init__.py"))
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)


def call_llm(model, prompt, system=None, max_tokens=4000, temperature=0.3):
    """调用 LLM (用 llm-call 脚本)"""
    import sys as _sys
    args = [
        _sys.executable,  # 用同一个 Python
        r"C:\Users\wilde\.minimax\.builtin-skills\llm-call\scripts\llm_call.py",
        "--model", model,
        "--prompt", prompt,
        "--max-tokens", str(max_tokens),
        "--temperature", str(temperature),
    ]
    if system:
        args.extend(["--system", system])
    env = {**__import__("os").environ, "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(args, capture_output=True, timeout=300, env=env)
    if result.returncode != 0:
        return f"[ERROR: {result.stderr.decode('utf-8', errors='replace')[:500]}]"
    return result.stdout.decode("utf-8", errors="replace").strip()


# === Step 2a: 拿 4 个关键节点的输出 (M3 视角) ===
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

print("=" * 80)
print("双 AI 互审 - M3 生成, M2.7 审查")
print("=" * 80)

# 拿 4 节点的输出
print("\n=== Step 2a: 拿节点输出 (M3) ===")
node_outputs = {}
for ntype, (kwargs, method) in WKW.items():
    inst = pkg.NODE_CLASS_MAPPINGS[ntype]()
    ret = getattr(inst, method)(**kwargs)
    if not isinstance(ret, tuple):
        ret = (ret,)
    node_outputs[ntype] = str(ret[0])
    print(f"  [{ntype}] 长度: {len(node_outputs[ntype])}")

# === Step 2b: M2.7 审查 (独立审查) ===
print("\n=== Step 2b: M2.7 独立审查 ===")

review_system = """你是 M2.7, 一个独立 AI 审查员, 任务是审阅 M3 (另一个 AI 模型) 生成的"导演级 prompt 节点"输出。
你要诚实、专业、不留情面地找问题, 不能客气。

评估维度 (8 维):
1. 反 AI 味: 是否还有"绝美/史诗/完美/精致"等空洞形容词?
2. 反机械控制: 是否用"第一步/第二部"模板? 还是实战口吻?
3. 微表情/肢体: 眼/手/背/呼吸 5+ 个身体部位词?
4. 留白/沉默: 沉默/停顿/空镜 3+ 词?
5. 氛围词: 光/影/色/音/景深 5+ 词?
6. 叙事逻辑: 因为/所以/但是 1+ 词?
7. 故事线: 起承转合清晰?
8. 情节严谨: 时代/地点/物件具体?

每个维度评分 0-12.5 (8 维共 100 分).

输出格式严格 JSON:
{
  "node": "节点名",
  "score": 0-100,
  "dimension_scores": {
    "反AI味": 0-12.5,
    "反机械控制": 0-12.5,
    "微表情/肢体": 0-12.5,
    "留白/沉默": 0-12.5,
    "氛围词": 0-12.5,
    "叙事逻辑": 0-12.5,
    "故事线": 0-12.5,
    "情节严谨": 0-12.5
  },
  "issues": ["具体问题 1", "具体问题 2", ...],
  "must_fix": ["必须修复的 1", "必须修复的 2"],
  "can_ignore": ["可以接受的 1", "可以接受的 2"]
}
"""

results = []
for ntype, output in node_outputs.items():
    print(f"\n--- M2.7 审查 {ntype} ---")
    # 截取前 6000 字符 (避免太长)
    truncated = output[:6000]
    prompt = f"""请审查以下 M3 生成的"导演级 prompt 节点"输出, 这是节点 {ntype} 的完整输出:

```
{truncated}
```

请用 JSON 格式给出审查结果。"""
    review = call_llm(
        "minimax/MiniMax-M2.7",
        prompt,
        system=review_system,
        max_tokens=2000,
        temperature=0.2,
    )
    print(f"  M2.7 审查长度: {len(review)}")
    print(f"  前 500 字符: {review[:500]}")
    # 尝试解析 JSON
    json_str = review
    if "```json" in review:
        json_str = review.split("```json")[1].split("```")[0].strip()
    elif "```" in review:
        json_str = review.split("```")[1].split("```")[0].strip()
    try:
        review_data = json.loads(json_str)
        review_data["node"] = ntype
        results.append(review_data)
    except Exception as e:
        print(f"  [JSON 解析失败: {e}]")
        results.append({"node": ntype, "raw": review[:1000]})

# 保存
with open(ROOT / "_dual_ai_review.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n=== 保存到 _dual_ai_review.json ===")

# 总结
print("\n=== M2.7 审查总结 ===")
for r in results:
    if "score" in r:
        print(f"\n[{r['node']}] 分数: {r['score']}/100")
        if "dimension_scores" in r:
            for k, v in r['dimension_scores'].items():
                print(f"  {k}: {v}/12.5")
        if "issues" in r:
            print(f"  问题 ({len(r['issues'])}):")
            for iss in r['issues'][:5]:
                print(f"    - {iss}")
        if "must_fix" in r:
            print(f"  必须修复:")
            for f in r['must_fix'][:3]:
                print(f"    ! {f}")
