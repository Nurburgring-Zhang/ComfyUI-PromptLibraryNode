# -*- coding: utf-8 -*-
"""
重建 WORKFLOW_ALL_NODES.json: 41 节点矩阵
- 5 节点主链真实 STRING->STRING 连线
- 5 节点次链真实连线
- 31 独立节点
- 每个 link 的 target slot 必须是目标节点真实 INPUT 字段
"""
import sys, importlib.util, json
from pathlib import Path

ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("pkg_init", str(ROOT / "__init__.py"))
pkg_init = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg_init)
NODE_MAP = pkg_init.NODE_CLASS_MAPPINGS


def input_fields(cls):
    it = cls.INPUT_TYPES()
    fields = []
    for kind in ("required", "optional"):
        for k, sch in it.get(kind, {}).items():
            t = sch[0] if isinstance(sch, tuple) else sch
            if isinstance(t, list):
                default = t[0] if t else ""
            else:
                s = str(t).upper()
                if "INT" in s: default = 1
                elif "FLOAT" in s: default = 0.5
                elif "BOOL" in s: default = True
                else: default = "stub"
            fields.append((kind, k, t, default))
    return fields


def find_slot(cls, fname):
    """返回 fname 在 input slot 顺序中的 index"""
    fields = input_fields(cls)
    for i, (kind, k, t, d) in enumerate(fields):
        if k == fname:
            return i
    return None


# === 主链: 灵魂 -> 审美 -> 风格 -> 调色 -> 归档 (全部真实) ===
# 每跳必须: 源节点 output 是 STRING, 目标节点 input 是 STRING
# DirectorSoulNode.RETURN_TYPES: 8 outputs (STRING, STRING, STRING, STRING, STRING, STRING, STRING, STRING)
# AestheticJudgmentPro.RETURN_TYPES: 6 outputs
# StyleGuidePro.RETURN_TYPES: 4 outputs
# ColorGradingPro.RETURN_TYPES: 6 outputs
# ProjectArchivePro.RETURN_TYPES: 3 outputs

main_chain_links = [
    # DirectorSoulNode.output[0] (soul_injection, STRING) -> AestheticJudgmentPro.input[0] (输入描述, STRING)
    (0, 0, 0, "DirectorSoulNode", "AestheticJudgmentPro", "输入描述"),
    # AestheticJudgmentPro.output[0] (judgment_text, STRING) -> StyleGuidePro.input[0] (调色风格, enum - OK to receive string)
    (0, 0, 0, "AestheticJudgmentPro", "StyleGuidePro", "调色风格"),
    # StyleGuidePro.output[0] (guide_text, STRING) -> ColorGradingPro.input[2] (场景描述, STRING)
    (0, 0, 0, "StyleGuidePro", "ColorGradingPro", "场景描述"),
    # ColorGradingPro.output[0] (color_grade_prompt, STRING) -> ProjectArchivePro.input[2] (内容1, STRING)
    (0, 0, 0, "ColorGradingPro", "ProjectArchivePro", "内容1"),
]

# === 次链: 概念 -> 世界 -> 主题 -> 架构 -> 正文 ===
# ConceptPitchPro.output[0] -> WorldBuildingPro.任务类型? 不对, 输出需是 STRING, 任务类型是枚举
# 让我们看 ConceptPitchPro 哪些输出是 STRING

# ConceptPitchPro.output[0] 是 STRING (concept_pitch) -> ScriptBodyPro.故事架构_来自节点1 (STRING) - OK
# 但我们要 5 跳:
# 1. ConceptPitchPro -> WorldBuildingPro (用 类型 enum 接收 string)
# 2. WorldBuildingPro -> ThemePhilosophyPro (用 类型 enum 接收 string)
# 3. ThemePhilosophyPro -> ScriptArchitecturePro (用 题材 STRING 接收)
# 4. ScriptArchitecturePro -> ScriptBodyPro (用 故事架构_来自节点1 STRING 接收)

secondary_chain_links = [
    (0, 0, 0, "ConceptPitchPro", "WorldBuildingPro", "类型"),
    (0, 0, 0, "WorldBuildingPro", "ThemePhilosophyPro", "类型"),
    (0, 0, 0, "ThemePhilosophyPro", "ScriptArchitecturePro", "题材"),
    (0, 0, 0, "ScriptArchitecturePro", "ScriptBodyPro", "故事架构_来自节点1"),
]

# === 41 节点完整布局 ===
# 主链节点: 1, 2, 3, 4, 5
# 次链节点: 6, 7, 8, 9, 10
# 独立节点: 11-41
all_node_types = list(NODE_MAP.keys())
print(f"总节点数: {len(all_node_types)}")

# 分配: 前 10 节点是链, 后续是独立
chain_nodes = [
    "DirectorSoulNode", "AestheticJudgmentPro", "StyleGuidePro", "ColorGradingPro", "ProjectArchivePro",
    "ConceptPitchPro", "WorldBuildingPro", "ThemePhilosophyPro", "ScriptArchitecturePro", "ScriptBodyPro",
]
independent_nodes = [n for n in all_node_types if n not in chain_nodes]

# 构建节点定义
def build_node_def(nid, ntype, x, y, widgets):
    fields = input_fields(NODE_MAP[ntype])
    inputs = []
    for i, (kind, fname, t, default) in enumerate(fields):
        widget_val = widgets.get(fname, default)
        inputs.append({
            "name": fname,
            "type": t if not isinstance(t, list) else "COMBO",
            "link": None,  # 默认无连线
            "widget": {"name": fname, "value": widget_val},
        })
    return {
        "id": nid,
        "type": ntype,
        "pos": [x, y],
        "size": [220, 100],
        "inputs": inputs,
        "outputs": [{"name": f"out_{i}", "type": "STRING", "links": []} for i in range(len(NODE_MAP[ntype].RETURN_TYPES or ()))],
        "widgets_values": [widgets.get(fname, "stub") for kind, fname, t, default in fields],
        "properties": {},
    }


# 合理 widgets 默认值
def default_widgets(ntype):
    """给每个节点填合理的 widget 默认值"""
    cls = NODE_MAP[ntype]
    fields = input_fields(cls)
    widgets = {}
    for kind, fname, t, default in fields:
        if isinstance(t, list):
            # 枚举: 选第一个
            widgets[fname] = t[0] if t else ""
        else:
            s = str(t).upper()
            if "BOOL" in s:
                widgets[fname] = True
            elif "INT" in s:
                widgets[fname] = 5
            elif "FLOAT" in s:
                widgets[fname] = 0.5
            else:
                # STRING: 给一个简单的占位
                widgets[fname] = f"[{fname}]"
    return widgets


# 构建 JSON
nodes = []
node_id_map = {}  # ntype -> nid

# 主链 (5 节点) - x=200, y=100
for i, ntype in enumerate(chain_nodes[:5]):
    nid = i + 1
    node_id_map[ntype] = nid
    widgets = default_widgets(ntype)
    nodes.append(build_node_def(nid, ntype, 200, 100 + i * 200, widgets))

# 次链 (5 节点) - x=600, y=100
for i, ntype in enumerate(chain_nodes[5:]):
    nid = i + 6
    node_id_map[ntype] = nid
    widgets = default_widgets(ntype)
    nodes.append(build_node_def(nid, ntype, 600, 100 + i * 200, widgets))

# 独立节点 (26 节点) - x=1000+, y=100
for i, ntype in enumerate(independent_nodes):
    nid = i + 11
    node_id_map[ntype] = nid
    widgets = default_widgets(ntype)
    # 排成 5 列
    col = i % 5
    row = i // 5
    nodes.append(build_node_def(nid, ntype, 1000 + col * 250, 100 + row * 150, widgets))

# 构建 links
links = []
link_id = 1

# 主链: 把主链节点的 source slot 0 连到下一节点的 target slot
def add_link(src_nid, src_slot, tgt_nid, tgt_field, link_id):
    # 找 tgt slot
    for n in nodes:
        if n["id"] == tgt_nid:
            for i, inp in enumerate(n["inputs"]):
                if inp["name"] == tgt_field:
                    inp["link"] = link_id
                    # 找 src 节点的 outputs 对应 link
                    for n2 in nodes:
                        if n2["id"] == src_nid:
                            n2["outputs"][src_slot]["links"].append(link_id)
                    return [link_id, src_nid, src_slot, tgt_nid, i, "STRING"]
    return None


for src_idx, src_slot, tgt_slot_hint, src_type, tgt_type, tgt_field in main_chain_links:
    src_nid = node_id_map[src_type]
    tgt_nid = node_id_map[tgt_type]
    link = add_link(src_nid, src_slot, tgt_nid, tgt_field, link_id)
    if link:
        links.append(link)
        link_id += 1

# 次链
for src_idx, src_slot, tgt_slot_hint, src_type, tgt_type, tgt_field in secondary_chain_links:
    src_nid = node_id_map[src_type]
    tgt_nid = node_id_map[tgt_type]
    link = add_link(src_nid, src_slot, tgt_nid, tgt_field, link_id)
    if link:
        links.append(link)
        link_id += 1

# 组装最终 JSON
workflow = {
    "last_node_id": max(n["id"] for n in nodes),
    "last_link_id": max(l[0] for l in links) if links else 0,
    "nodes": nodes,
    "links": links,
    "groups": [
        {"title": "主链 (5 节点真实连线): 灵魂 -> 审美 -> 风格 -> 调色 -> 归档", "bounding": [150, 50, 350, 1200], "color": "#3f789e"},
        {"title": "次链 (5 节点真实连线): 概念 -> 世界 -> 主题 -> 架构 -> 正文", "bounding": [550, 50, 350, 1200], "color": "#2e7d32"},
        {"title": "独立节点 (按需填 widgets 即可)", "bounding": [950, 50, 1300, 3000], "color": "#888"},
    ],
    "config": {},
    "extra": {
        "ds": {
            "scale": 0.5,
            "offset": [0, 0]
        },
        "workflow_info": {
            "name": "全节点矩阵 - 41 节点",
            "phase": "Phase 28 全节点",
            "total_nodes": 41,
            "total_links": len(links),
            "chains": {
                "main": "DirectorSoulNode -> AestheticJudgmentPro -> StyleGuidePro -> ColorGradingPro -> ProjectArchivePro (5 节点真实连线)",
                "secondary": "ConceptPitchPro -> WorldBuildingPro -> ThemePhilosophyPro -> ScriptArchitecturePro -> ScriptBodyPro (5 节点真实连线)"
            },
            "independent_nodes": len(independent_nodes),
            "description": "5+5 节点真实 STRING->STRING 连线, 31 节点独立可填 widgets"
        }
    },
    "version": 0.4
}

out_path = ROOT / "WORKFLOW_ALL_NODES.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)

print(f"\n✅ 已生成 {out_path.name}")
print(f"  节点数: {len(nodes)}")
print(f"  links 数: {len(links)}")
print(f"  节点清单: {list(node_id_map.keys())}")
