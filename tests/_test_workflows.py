# -*- coding: utf-8 -*-
"""
工作流验证测试 - 17 个真生产工作流 (Phase 36.6)

Phase 36.6 修正:
- 之前 9 个工作流是"2 列堆叠"演示欺骗, 已删除 (备份到 archive/_trash/)
- 现在 17 个工作流是真生产流程, 5 起点注入 + production 节点 + 终节点

验证项:
- JSON 有效
- 节点 ID 连续
- 节点类型有效
- 至少 1 个起点节点
- 起点节点至少 1 个 output 被消费
- 下游节点 addon 注入率 >= 50%
- links 密度 >= 2.0
- 节点数 5-30 范围
- 死节点 0
"""
import json
import os
import sys

WORKFLOWS = [
    # (filename, expected_nodes_min, expected_min_links, description)
    ("WORKFLOW_FILM_PRODUCTION.json", 18, 70, "电影生产 (60-120min)"),
    ("WORKFLOW_SHORT_DRAMA_30S.json", 8, 25, "30s 短剧 6 段"),
    ("WORKFLOW_VERTICAL_SHORT_DRAMA.json", 8, 25, "竖屏短剧 (1-3min)"),
    ("WORKFLOW_DOUYIN_HOOK.json", 7, 20, "抖音/快手 3-7s"),
    ("WORKFLOW_FEATURE_SCRIPT.json", 8, 30, "完整剧本 (60-120min)"),
    ("WORKFLOW_STORYBOARD.json", 8, 25, "完整分镜 (L1-L7)"),
    ("WORKFLOW_MV.json", 7, 20, "MV 音乐视频 (3-5min)"),
    ("WORKFLOW_PICTURE_BOOK.json", 6, 15, "绘本 (5-10min)"),
    ("WORKFLOW_INTERACTIVE_DRAMA.json", 8, 25, "互动剧 (30-60min)"),
    ("WORKFLOW_BRAND_FILM.json", 8, 25, "品牌宣传 (60-180s)"),
    ("WORKFLOW_MINIMALIST_PRODUCT_AD.json", 6, 15, "极简产品广告 (15-30s)"),
    ("WORKFLOW_SOUND_DESIGN.json", 8, 25, "完整声音设计"),
    ("WORKFLOW_COLOR_GRADING.json", 6, 15, "完整调色 (60-30-10)"),
    ("WORKFLOW_3D_ANIMATION.json", 8, 25, "3D 动画短片"),
    ("WORKFLOW_H3_PRODUCTION.json", 6, 15, "H3 多模态生产"),
    ("WORKFLOW_UNIVERSAL_6MODELS.json", 6, 20, "6 大模型通用 prompt"),
    ("WORKFLOW_QA_PUBLISH.json", 8, 25, "质量审核 + 发布"),
]

# 41 + 2 = 43 节点清单 (Phase 36 加 H3/Universal)
VALID_NODES = {
    "ScriptArchitecturePro", "ScriptBodyPro", "DirectorStoryboardPro",
    "VerticalShortDramaPro", "HookMasterPro", "DialogueMasterPro", "CharacterArcPro",
    "DirectorIntentPro", "ArtDirectionPro", "SpatialConsistencyPro", "SilenceMasteryPro",
    "ConceptPitchPro", "WorldBuildingPro", "ThemePhilosophyPro", "SoundDesignPro",
    "MusicScorePro", "PerformanceDirectionPro", "CostumePropSetPro", "EditingPro",
    "ColorGradingPro", "VfxPro", "MvPro", "PictureBookPro", "InteractiveDramaPro",
    "QualityAssurancePro",
    "AssetRegistry", "SpatialLayout", "ActingSkill",
    "SoundSkill", "IterationPostPro", "ThirtySecSixAct", "CinematicStudio",
    "DirectorSoulNode", "ShotSelectionPro",
    "AestheticJudgmentPro", "VersionControlPro", "StyleGuidePro", "MarketAudiencePro",
    "CleanupPassPro", "FormatOutputPro", "ProjectArchivePro",
    # Phase 36.2/36.3 新增
    "H3ContextIRNode", "UniversalDirectorPromptNode",
}

# 5 起点节点
STARTING_NODES = {
    "DirectorSoulNode", "AestheticJudgmentPro", "StyleGuidePro",
    "AssetRegistry", "DirectorIntentPro",
}

# 4 个 addon slot 名
ADDON_NAMES = {"灵魂addon", "审美addon", "风格addon", "资产addon"}

passed, failed = 0, 0
def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
        print("[OK] " + name)
    else:
        failed += 1
        print("[FAIL] " + name)


print("=" * 70)
print("Phase 36.6: 17 个真生产工作流验证测试")
print("=" * 70)

WORKFLOWS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workflows")

for filename, expected_nodes_min, expected_min_links, phase in WORKFLOWS:
    print("\n--- {} ({}) ---".format(filename, phase))
    filepath = os.path.join(WORKFLOWS_DIR, filename)
    check("文件存在", os.path.exists(filepath))
    if not os.path.exists(filepath):
        continue
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        check("JSON 解析", True)
    except Exception as e:
        check("JSON 解析 ({})".format(e), False)
        continue

    # 节点数 >= 期望
    actual_nodes = len(data.get("nodes", []))
    check("节点数 >= {} (实际 {})".format(expected_nodes_min, actual_nodes), actual_nodes >= expected_nodes_min)

    # 节点 ID 连续
    ids = [n.get("id") for n in data.get("nodes", [])]
    expected_ids = list(range(1, len(ids) + 1))
    check("节点 ID 连续 1-{}".format(len(ids)), ids == expected_ids)

    # 节点类型有效
    types = [n.get("type") for n in data.get("nodes", [])]
    invalid = [t for t in types if t not in VALID_NODES]
    check("节点类型有效 ({})".format(invalid if invalid else "全部"), len(invalid) == 0)

    # links 数
    actual_links = len(data.get("links", []))
    check("Links >= {} (实际 {})".format(expected_min_links, actual_links), actual_links >= expected_min_links)

    # links 密度
    density = actual_links / actual_nodes if actual_nodes else 0
    check("Links 密度 >= 2.0 (实际 {:.1f})".format(density), density >= 2.0)

    # 至少 1 个起点节点
    starting_count = sum(1 for t in types if t in STARTING_NODES)
    check("至少 1 个起点节点 (实际 {})".format(starting_count), starting_count >= 1)

    # 5 起点消费: 5 个起点都至少 1 个 output 被消费
    starting_consumed = 0
    for n in data.get("nodes", []):
        if n.get("type") in STARTING_NODES:
            for o in n.get("outputs", []):
                if o.get("links") and len(o["links"]) > 0:
                    starting_consumed += 1
                    break
    check("5 起点都至少 1 个 output 被消费 (实际 {}/5)".format(starting_consumed), starting_consumed >= 5)

    # 下游节点 addon 注入率
    downstream_nodes = [n for n in data.get("nodes", []) if n.get("type") not in STARTING_NODES]
    addon_injected = 0
    for n in downstream_nodes:
        for i in n.get("inputs", []):
            if i.get("link") is not None and i.get("name") in ADDON_NAMES:
                addon_injected += 1
                break
    addon_rate = addon_injected / len(downstream_nodes) if downstream_nodes else 0
    check("下游节点 addon 注入率 >= 50% (实际 {:.0%}, {}/{})".format(
        addon_rate, addon_injected, len(downstream_nodes)), addon_rate >= 0.5)

    # 死节点 0 (既无 input 也无 addon 注入)
    dead_nodes = []
    for n in data.get("nodes", []):
        if n.get("type") in STARTING_NODES:
            continue
        has_input = any(i.get("link") is not None for i in n.get("inputs", []))
        if not has_input:
            dead_nodes.append(n.get("type"))
    check("死节点 0 (实际 {}: {})".format(len(dead_nodes), dead_nodes), not dead_nodes)

    # 终节点明确 (有 target_output_node metadata)
    info = data.get("extra", {}).get("workflow_info", {})
    target = info.get("target_output_node", "")
    check("终节点明确 (target={})".format(target), bool(target))


print()
print("=" * 70)
print("测试汇总: 通过 {} / 失败 {} / 总计 {}".format(passed, failed, passed + failed))
print("=" * 70)
if failed == 0:
    print("\n[PASS] 17 个真生产工作流全部通过验证")
    sys.exit(0)
else:
    print(f"\n[FAIL] {failed} 项失败")
    sys.exit(1)
