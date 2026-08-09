# -*- coding: utf-8 -*-
"""
工作流验证测试 - 8 个工作流全部 JSON 有效 + 节点 ID 有效
"""
import json
import os
import sys

WORKFLOWS = [
    ("WORKFLOW_END_TO_END.json", 9, "Phase 25"),
    ("WORKFLOW_SHORT_DRAMA.json", 6, "Phase 25"),
    ("WORKFLOW_MV.json", 5, "Phase 25"),
    ("WORKFLOW_AESTHETIC_FULL.json", 8, "Phase 28 P0"),
    ("WORKFLOW_VERSIONED_PIPELINE.json", 10, "Phase 28 P1"),
    ("WORKFLOW_MARKET_AWARE.json", 6, "Phase 28 P1"),
    ("WORKFLOW_CLEANUP_PUBLISH.json", 6, "Phase 28 P2"),
    ("WORKFLOW_MV_V2.json", 6, "Phase 28 P0+P1"),
    ("WORKFLOW_ALL_NODES.json", 41, "Phase 28 全节点"),
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
    "Phase14AssetRegistry", "Phase14SpatialLayout", "Phase14ActingSkill",
    "Phase14SoundSkill", "IterationPostPro", "Phase14_30sSixAct", "Phase14_CinematicStudio",
    "DirectorSoulNode", "ShotSelectionPro",
    "AestheticJudgmentPro", "VersionControlPro", "StyleGuidePro", "MarketAudiencePro",
    "CleanupPassPro", "FormatOutputPro", "ProjectArchivePro",
}

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
print("8 个工作流验证测试 (Phase 25 + Phase 28)")
print("=" * 60)

for filename, expected_nodes, phase in WORKFLOWS:
    print("\n--- {} ({}) ---".format(filename, phase))
    check("文件存在", os.path.exists(filename))
    if not os.path.exists(filename):
        continue
    try:
        with open(filename, "r", encoding="utf-8") as f:
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

    # 链接有效 (ALL_NODES 是矩阵, 31 节点独立, 期望少量真实 link)
    links = data.get("links", [])
    if filename == "WORKFLOW_ALL_NODES.json":
        # ALL_NODES 是矩阵工作流,只有主链 5 + 次链 5 = 8 真实 link
        check("链接数 == 8 (主链 5 + 次链 5, 31 节点独立) (实际 {})".format(len(links)), len(links) == 8)
    else:
        check("链接数 >= {}".format(actual_nodes - 1), len(links) >= actual_nodes - 1)

    # 元信息
    info = data.get("extra", {}).get("workflow_info", {})
    check("workflow_info.name", "name" in info)
    check("workflow_info.phase", "phase" in info)
    check("workflow_info.total_nodes == {}".format(expected_nodes), info.get("total_nodes") == expected_nodes)

print()
print("=" * 60)
print("工作流验证: 通过 {} / 失败 {} / 总计 {}".format(passed, failed, passed + failed))
print("=" * 60)
sys.exit(0 if failed == 0 else 1)
