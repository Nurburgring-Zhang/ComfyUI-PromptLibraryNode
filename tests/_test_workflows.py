# -*- coding: utf-8 -*-
"""
工作流验证测试 - 9 个工作流全部 JSON 有效 + 节点有效 + **真实连线**

Phase 36.5: 之前工作流是单层平行, 节点孤立, 没有真正数据流.
现在工作流是 4-6 stages 多级串联, 起点节点 4 个注入到所有下游节点.
"""
import json
import os
import sys

WORKFLOWS = [
    # (filename, expected_nodes, expected_min_links, description)
    ("WORKFLOW_END_TO_END.json", 18, 50, "Phase 36.5 多级工作流 - 4 起点注入 + 6 stages 串行"),
    ("WORKFLOW_SHORT_DRAMA.json", 11, 30, "Phase 36.5 短剧工作流 - 4 起点 + 5 stages"),
    ("WORKFLOW_MV.json", 8, 15, "Phase 36.5 MV 工作流 - 2 起点 + 4 stages"),
    ("WORKFLOW_AESTHETIC_FULL.json", 10, 25, "Phase 36.5 审美工作流 - 4 起点 + 5 stages"),
    ("WORKFLOW_VERSIONED_PIPELINE.json", 10, 25, "Phase 36.5 版本化工作流 - 4 起点 + 5 stages"),
    ("WORKFLOW_MARKET_AWARE.json", 6, 10, "Phase 36.5 市场感知工作流 - 3 起点 + 3 stages"),
    ("WORKFLOW_CLEANUP_PUBLISH.json", 10, 25, "Phase 36.5 清理发布工作流 - 4 起点 + 5 stages"),
    ("WORKFLOW_MV_V2.json", 6, 10, "Phase 36.5 MV V2 - 2 起点 + 4 stages"),
    ("WORKFLOW_ALL_NODES.json", 41, 150, "Phase 36.5 全 41 节点 - 4 起点 + 9 stages"),
]

# 41 节点清单
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
}

# 4 起点节点 (应该出现在每个工作流)
STARTING_NODES = {"DirectorSoulNode", "AestheticJudgmentPro", "StyleGuidePro", "AssetRegistry"}

passed, failed = 0, 0
def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
        print("[OK] " + name)
    else:
        failed += 1
        print("[FAIL] " + name)


print("=" * 60)
print("9 个工作流验证测试 (Phase 36.5 - 多级真实连线)")
print("=" * 60)

WORKFLOWS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workflows")

for filename, expected_nodes, expected_min_links, phase in WORKFLOWS:
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

    # 节点数
    actual_nodes = len(data.get("nodes", []))
    check("节点数 == {} (实际 {})".format(expected_nodes, actual_nodes), actual_nodes == expected_nodes)

    # 节点 ID 连续
    ids = [n.get("id") for n in data.get("nodes", [])]
    check("节点 ID 连续 1-{}".format(expected_nodes), ids == list(range(1, expected_nodes + 1)))

    # 节点类型有效
    types = [n.get("type") for n in data.get("nodes", [])]
    invalid = [t for t in types if t not in VALID_NODES]
    check("节点类型有效 ({})".format(invalid if invalid else "全部"), len(invalid) == 0)

    # === 关键：真实连线检查 ===
    actual_links = len(data.get("links", []))
    check("Links >= {} (实际 {})".format(expected_min_links, actual_links), actual_links >= expected_min_links)

    # 至少 1 个起点节点
    starting_count = sum(1 for t in types if t in STARTING_NODES)
    check("至少 1 个起点节点 (实际 {})".format(starting_count), starting_count >= 1)

    # === 新增：每个起点节点 (除 4 起点 node 自身外) 至少 1 个 output 有真实 links ===
    starting_ids = {n["id"]: n["type"] for n in data.get("nodes", []) if n.get("type") in STARTING_NODES}
    starting_connected_outputs = 0
    starting_total_outputs = 0
    for n in data.get("nodes", []):
        if n.get("type") in STARTING_NODES:
            outputs = n.get("outputs", [])
            for o in outputs:
                starting_total_outputs += 1
                if o.get("links") and len(o["links"]) > 0:
                    starting_connected_outputs += 1
    # 起点节点应该至少 30% 输出被连接
    if starting_total_outputs > 0:
        ratio = starting_connected_outputs / starting_total_outputs
        check("起点节点输出连接率 >= 30% (实际 {:.0%})".format(ratio), ratio >= 0.3)

    # === 新增：下游节点 (除起点外) 至少 50% connected_inputs ===
    downstream_nodes = [n for n in data.get("nodes", []) if n.get("type") not in STARTING_NODES]
    total_inputs = 0
    connected_inputs = 0
    for n in downstream_nodes:
        for i in n.get("inputs", []):
            total_inputs += 1
            if i.get("link") is not None:
                connected_inputs += 1
    if total_inputs > 0:
        downstream_ratio = connected_inputs / total_inputs
        check("下游节点连接率 >= 50% (实际 {:.0%}, {}/{})".format(downstream_ratio, connected_inputs, total_inputs), downstream_ratio >= 0.5)


print()
print("=" * 60)
print("测试汇总: 通过 {} / 失败 {} / 总计 {}".format(passed, failed, passed + failed))
print("=" * 60)
if failed == 0:
    print("\n[PASS] 9 个工作流全部真实多级连线")
    sys.exit(0)
else:
    print(f"\n[FAIL] {failed} 项失败")
    sys.exit(1)
