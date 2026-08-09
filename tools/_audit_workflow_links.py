# -*- coding: utf-8 -*-
"""
深度审查 5: 工作流 JSON 连线真实性
- 每个 link 的 [target_node_id, target_slot] 必须对应目标节点的 INPUT_TYPES 字段
- 这是用户最关心的"真实连线"验证
"""
import sys, importlib.util, json
from pathlib import Path

ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("pkg_init", str(ROOT / "__init__.py"))
pkg_init = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg_init)
NODE_MAP = pkg_init.NODE_CLASS_MAPPINGS

# 收集每个节点的输入字段名 (按位置)
def get_input_slots(cls):
    """返回 list, 顺序是 ComfyUI 实际显示顺序 (required 然后 optional)"""
    it = cls.INPUT_TYPES()
    slots = []
    for kind in ("required", "optional"):
        for fname, fspec in it.get(kind, {}).items():
            slots.append((kind, fname))
    return slots


# 1. 先收集所有节点的 input slot 名
node_to_slots = {}
for name, cls in NODE_MAP.items():
    node_to_slots[name] = get_input_slots(cls)

# 2. 扫所有 WORKFLOW_*.json
workflows = sorted(ROOT.glob("WORKFLOW_*.json"))
print(f"=== 工作流 JSON 连线真实性审查 ===\n")
print(f"找到 {len(workflows)} 个工作流\n")

total_links = 0
total_real = 0
total_problems = []

for wf in workflows:
    try:
        data = json.loads(wf.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ {wf.name} 解析失败: {e}")
        continue

    nodes = data.get("nodes", [])
    # 建立 node_id -> (node_type, slots)
    id_to_node = {}
    for n in nodes:
        nid = n.get("id")
        ntype = n.get("type")
        id_to_node[nid] = (ntype, node_to_slots.get(ntype, []))

    links = data.get("links", [])
    print(f"--- {wf.name}: {len(nodes)} nodes, {len(links)} links ---")
    real_in_wf = 0
    for ln in links:
        # link 格式: [link_id, source_node_id, source_slot, target_node_id, target_slot, type]
        if not isinstance(ln, (list, tuple)) or len(ln) < 6:
            continue
        link_id, src_id, src_slot, tgt_id, tgt_slot, ltype = ln[:6]
        total_links += 1
        if tgt_id not in id_to_node:
            total_problems.append((wf.name, f"link#{link_id} target #{tgt_id} not in workflow"))
            continue
        ntype, slots = id_to_node[tgt_id]
        # target_slot 是 index, 必须在 slots 范围内
        if tgt_slot is None or tgt_slot < 0 or tgt_slot >= len(slots):
            total_problems.append((wf.name, f"link#{link_id} -> {ntype}.slot[{tgt_slot}] out of range (slots={len(slots)})"))
            continue
        kind, fname = slots[tgt_slot]
        real_in_wf += 1
        total_real += 1
        print(f"  ✓ link #{link_id}: node#{src_id} -> {ntype}.{fname}  ({kind})")

    print(f"  真实连线: {real_in_wf}/{len(links)}\n")

print(f"\n=== 总计 ===")
print(f"总 link 数: {total_links}")
print(f"真实可连: {total_real}")
print(f"问题: {len(total_problems)}")
for wf, p in total_problems[:30]:
    print(f"  ❌ [{wf}] {p}")
if not total_problems:
    print("\n✅ 所有工作流的 link 全部对应到目标节点的真实 INPUT 字段")
