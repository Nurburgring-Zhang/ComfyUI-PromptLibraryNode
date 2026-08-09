# -*- coding: utf-8 -*-
"""统计工作流节点使用情况"""
import json
import os

WORKFLOWS = [
    "WORKFLOW_END_TO_END.json",
    "WORKFLOW_SHORT_DRAMA.json",
    "WORKFLOW_MV.json",
    "WORKFLOW_AESTHETIC_FULL.json",
    "WORKFLOW_VERSIONED_PIPELINE.json",
    "WORKFLOW_MARKET_AWARE.json",
    "WORKFLOW_CLEANUP_PUBLISH.json",
    "WORKFLOW_MV_V2.json",
]

# 统计每个节点被多少工作流使用
from collections import Counter
usage = Counter()
per_workflow = {}

for wf in WORKFLOWS:
    if not os.path.exists(wf):
        continue
    with open(wf, "r", encoding="utf-8") as f:
        data = json.load(f)
    types = [n.get("type") for n in data.get("nodes", [])]
    per_workflow[wf] = types
    for t in types:
        usage[t] += 1

# 排序
print("=" * 60)
print("8 个工作流统计")
print("=" * 60)
print(f"\n总工作流: 8")
total_nodes_used = sum(usage.values())
print(f"总节点实例: {total_nodes_used}")
print(f"被使用的不重复节点: {len(usage)}")

print(f"\n--- 各工作流节点数 ---")
for wf, types in per_workflow.items():
    print(f"  {wf}: {len(types)} 节点")

print(f"\n--- 节点使用频次 (降序) ---")
for node, count in sorted(usage.items(), key=lambda x: -x[1]):
    print(f"  {count}x {node}")
