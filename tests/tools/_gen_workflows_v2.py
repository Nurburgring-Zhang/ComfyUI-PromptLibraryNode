# -*- coding: utf-8 -*-
"""
工作流生成器 v2 - 真实 ComfyUI 工作流
- 每个 output 真实名字 (从 RETURN_NAMES)
- 每个 input slot 真实可连 (从 INPUT_TYPES)
- input slot 颜色: STRING=绿, 6个 addon 都接
- 起点节点无 input slot, 纯 widget
"""
import json, importlib.util
from pathlib import Path

ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
sys_path = str(ROOT)
import sys
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

# 用我们改造过的 __init__ (含 addon injector)
spec = importlib.util.spec_from_file_location("pkg_init", str(ROOT / "__init__.py"))
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)
NODE_MAP = pkg.NODE_CLASS_MAPPINGS


def get_input_slots(cls):
    """返回 list of (kind, name, schema),按 required 然后 optional 顺序"""
    it = cls.INPUT_TYPES()
    slots = []
    for kind in ("required", "optional"):
        for fname, fspec in it.get(kind, {}).items():
            slots.append((kind, fname, fspec))
    return slots


def get_output_info(cls):
    """返回 list of (name, type)"""
    rt = getattr(cls, "RETURN_TYPES", ()) or ()
    rn = getattr(cls, "RETURN_NAMES", None)
    if rn and len(rn) == len(rt):
        return list(zip(rn, rt))
    return [(f"out_{i}", t) for i, t in enumerate(rt)]


# ComfyUI type 颜色
TYPE_COLOR = {
    "STRING": "#7f9e5a",  # 绿
    "IMAGE": "#c08234",   # 黄
    "LATENT": "#8a5fc2",  # 紫
    "MODEL": "#b85a4e",   # 红
    "CONDITIONING": "#e08e45",  # 橙
    "VAE": "#d65a8c",     # 粉
    "CLIP": "#5a8fc2",    # 浅蓝
    "MASK": "#7f9e5a",    # 浅绿
    "AUDIO": "#5a9ec2",   # 蓝
    "VIDEO": "#b85a4e",   # 红
}


def make_node_def(nid, ntype, x, y, widgets=None):
    """构造一个完整的 ComfyUI 节点定义, 包含 input slots (link=None) 和 output (name from RETURN_NAMES)"""
    cls = NODE_MAP[ntype]
    inputs = []
    for kind, fname, fspec in get_input_slots(cls):
        # 解析 type
        if isinstance(fspec, tuple) and len(fspec) >= 1:
            t = fspec[0]
            opts = fspec[1] if len(fspec) > 1 and isinstance(fspec[1], dict) else {}
        else:
            t = "STRING"
            opts = {}
        if isinstance(t, list):
            tname = "COMBO"
        else:
            tname = str(t).upper()
        # widget value
        if widgets and fname in widgets:
            wval = widgets[fname]
        elif isinstance(t, list):
            wval = t[0] if t else ""
        else:
            s = tname
            if s == "INT": wval = 1
            elif s == "FLOAT": wval = 0.5
            elif s == "BOOLEAN": wval = True
            else: wval = ""
        inputs.append({
            "name": fname,
            "type": tname,
            "link": None,
            "widget": {"name": fname, "type": tname, "value": wval},
            "color": TYPE_COLOR.get(tname, "#7f9e5a"),
            "tooltip": opts.get("tooltip", ""),
        })
    outputs = []
    for oname, otype in get_output_info(cls):
        outputs.append({
            "name": oname,
            "type": str(otype).upper(),
            "links": [],
            "color": TYPE_COLOR.get(str(otype).upper(), "#7f9e5a"),
            "tooltip": "{}: {}".format(ntype, oname),
        })
    return {
        "id": nid,
        "type": ntype,
        "pos": [x, y],
        "size": [260, max(100, 30 + len(inputs) * 4)],
        "inputs": inputs,
        "outputs": outputs,
        "widgets_values": [inp["widget"]["value"] for inp in inputs],
        "properties": {},
    }


def find_input_slot_index(node_def, fname):
    """找 input field 在 node 中的 slot index"""
    for i, inp in enumerate(node_def["inputs"]):
        if inp["name"] == fname:
            return i
    return None


def add_link(links, src_node, src_slot, tgt_node, tgt_field, link_id):
    """真实加一条 link"""
    tgt_idx = find_input_slot_index(tgt_node, tgt_field)
    if tgt_idx is None:
        # 改为显式 print
        print(f"    [WARN] link #{link_id} 失败: 目标节点 {tgt_node['type']} 无 input '{tgt_field}'")
        return None
    if src_slot >= len(src_node["outputs"]):
        print(f"    [WARN] link #{link_id} 失败: 源节点 {src_node['type']} 无 output slot {src_slot}")
        return None
    link = [link_id, src_node["id"], src_slot, tgt_node["id"], tgt_idx, "STRING"]
    links.append(link)
    # 更新 node 的 link 引用
    src_node["outputs"][src_slot]["links"].append(link_id)
    tgt_node["inputs"][tgt_idx]["link"] = link_id
    return link


# ============================================================
# 1. WORKFLOW_END_TO_END: 9 节点, 真实工作流
#    起点 4 (灵魂/审美/风格/节奏) → 5 中间节点
# ============================================================
def gen_workflow_end_to_end():
    nodes = []
    # 起点节点 (无 input slot, 纯 widget) - 6 个 addon 起点
    n_soul = make_node_def(1, "DirectorSoulNode", 100, 100)
    n_aest = make_node_def(2, "AestheticJudgmentPro", 100, 300)
    n_style = make_node_def(3, "StyleGuidePro", 100, 500)
    n_edit = make_node_def(4, "EditingPro", 100, 700)
    n_intent = make_node_def(5, "DirectorIntentPro", 100, 900)
    n_p14asset = make_node_def(6, "AssetRegistry", 100, 1100)
    nodes.extend([n_soul, n_aest, n_style, n_edit, n_intent, n_p14asset])
    # 中间节点 (有 6 addon input slot)
    n_arch = make_node_def(7, "ScriptArchitecturePro", 500, 100)
    n_body = make_node_def(8, "ScriptBodyPro", 500, 300)
    n_story = make_node_def(9, "DirectorStoryboardPro", 500, 500)
    n_color = make_node_def(10, "ColorGradingPro", 500, 700)
    n_qa = make_node_def(11, "QualityAssurancePro", 500, 900)
    nodes.extend([n_arch, n_body, n_story, n_color, n_qa])

    links = []
    lid = 1
    # ===== 6 个 Production 节点都接 6 个 addon =====
    for tgt in [n_arch, n_body, n_story, n_color, n_qa]:
        add_link(links, n_soul, 0, tgt, "灵魂addon", lid); lid += 1
        add_link(links, n_aest, 0, tgt, "审美addon", lid); lid += 1
        add_link(links, n_style, 0, tgt, "风格addon", lid); lid += 1
        add_link(links, n_p14asset, 0, tgt, "经验addon", lid); lid += 1
        add_link(links, n_intent, 0, tgt, "控制addon", lid); lid += 1
        add_link(links, n_edit, 0, tgt, "节奏addon", lid); lid += 1
    # 生产链: ScriptArchitecturePro -> ScriptBodyPro -> DirectorStoryboardPro -> ColorGradingPro
    add_link(links, n_arch, 0, n_body, "故事架构_来自节点1", lid); lid += 1
    add_link(links, n_body, 0, n_story, "剧本正文_来自节点2", lid); lid += 1
    add_link(links, n_story, 0, n_color, "场景描述", lid); lid += 1
    add_link(links, n_color, 0, n_qa, "场景描述", lid); lid += 1
    return _wrap_wf("端到端工作流 v2", "Phase 28 改造 - 真实 input/output 接口", nodes, links)


def _wrap_wf(name, phase, nodes, links):
    return {
        "last_node_id": max(n["id"] for n in nodes),
        "last_link_id": max((l[0] for l in links), default=0),
        "nodes": nodes,
        "links": links,
        "groups": [],
        "config": {},
        "extra": {
            "workflow_info": {
                "name": name,
                "phase": phase,
                "total_nodes": len(nodes),
                "total_links": len(links),
                "node_types": sorted(set(n["type"] for n in nodes)),
                "input_addons": ["灵魂addon", "审美addon", "风格addon", "经验addon", "控制addon", "节奏addon"],
                "output_types": sorted(set(o["type"] for n in nodes for o in n["outputs"])),
                "real_workflow": True,
            }
        },
        "version": 0.4,
    }


# 保存
def save_wf(filename, wf):
    path = ROOT / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)
    print(f"  生成 {filename}: {len(wf['nodes'])} 节点, {len(wf['links'])} links")


# ============================================================
# 2. WORKFLOW_SHORT_DRAMA: 短剧 (6 节点)
# ============================================================
def gen_workflow_short_drama():
    nodes = []
    n_soul = make_node_def(1, "DirectorSoulNode", 100, 100)
    n_aest = make_node_def(2, "AestheticJudgmentPro", 100, 300)
    n_style = make_node_def(3, "StyleGuidePro", 100, 500)
    n_edit = make_node_def(4, "EditingPro", 100, 700)
    nodes.extend([n_soul, n_aest, n_style, n_edit])
    n_vs = make_node_def(5, "VerticalShortDramaPro", 500, 100)
    n_hook = make_node_def(6, "HookMasterPro", 500, 300)
    n_dial = make_node_def(7, "DialogueMasterPro", 500, 500)
    n_arc = make_node_def(8, "CharacterArcPro", 500, 700)
    nodes.extend([n_vs, n_hook, n_dial, n_arc])

    links = []
    lid = 1
    add_link(links, n_soul, 0, n_vs, "灵魂addon", lid); lid += 1
    add_link(links, n_soul, 0, n_hook, "灵魂addon", lid); lid += 1
    add_link(links, n_soul, 0, n_dial, "灵魂addon", lid); lid += 1
    add_link(links, n_soul, 0, n_arc, "灵魂addon", lid); lid += 1
    add_link(links, n_aest, 0, n_vs, "审美addon", lid); lid += 1
    add_link(links, n_aest, 0, n_hook, "审美addon", lid); lid += 1
    add_link(links, n_style, 0, n_vs, "风格addon", lid); lid += 1
    add_link(links, n_style, 0, n_dial, "风格addon", lid); lid += 1
    add_link(links, n_edit, 0, n_vs, "节奏addon", lid); lid += 1
    add_link(links, n_edit, 0, n_hook, "节奏addon", lid); lid += 1
    return _wrap_wf("短剧工作流 v2", "Phase 28 改造 - 真实 input/output 接口", nodes, links)


# ============================================================
# 3. WORKFLOW_MV: MV (5 节点)
# ============================================================
def gen_workflow_mv():
    nodes = []
    n_soul = make_node_def(1, "DirectorSoulNode", 100, 100)
    n_aest = make_node_def(2, "AestheticJudgmentPro", 100, 300)
    n_style = make_node_def(3, "StyleGuidePro", 100, 500)
    nodes.extend([n_soul, n_aest, n_style])
    n_mv = make_node_def(4, "MvPro", 500, 100)
    n_music = make_node_def(5, "MusicScorePro", 500, 300)
    n_sound = make_node_def(6, "SoundDesignPro", 500, 500)
    nodes.extend([n_mv, n_music, n_sound])

    links = []
    lid = 1
    add_link(links, n_soul, 0, n_mv, "灵魂addon", lid); lid += 1
    add_link(links, n_soul, 0, n_music, "灵魂addon", lid); lid += 1
    add_link(links, n_soul, 0, n_sound, "灵魂addon", lid); lid += 1
    add_link(links, n_aest, 0, n_mv, "审美addon", lid); lid += 1
    add_link(links, n_aest, 0, n_music, "审美addon", lid); lid += 1
    add_link(links, n_style, 0, n_mv, "风格addon", lid); lid += 1
    add_link(links, n_style, 0, n_sound, "风格addon", lid); lid += 1
    return _wrap_wf("MV 工作流 v2", "Phase 28 改造 - 真实 input/output 接口", nodes, links)


# ============================================================
# 4. WORKFLOW_AESTHETIC_FULL: 审美全流程 (8 节点)
# ============================================================
def gen_workflow_aesthetic():
    nodes = []
    n_soul = make_node_def(1, "DirectorSoulNode", 100, 100)
    n_aest = make_node_def(2, "AestheticJudgmentPro", 100, 300)
    n_style = make_node_def(3, "StyleGuidePro", 100, 500)
    n_edit = make_node_def(4, "EditingPro", 100, 700)
    n_intent = make_node_def(5, "DirectorIntentPro", 100, 900)
    nodes.extend([n_soul, n_aest, n_style, n_edit, n_intent])
    n_art = make_node_def(6, "ArtDirectionPro", 500, 100)
    n_spatial = make_node_def(7, "SpatialConsistencyPro", 500, 300)
    n_shot = make_node_def(8, "ShotSelectionPro", 500, 500)
    nodes.extend([n_art, n_spatial, n_shot])

    links = []
    lid = 1
    add_link(links, n_soul, 0, n_art, "灵魂主导情感", lid); lid += 1
    add_link(links, n_soul, 0, n_art, "灵魂addon", lid); lid += 1
    add_link(links, n_aest, 0, n_spatial, "空间类型", lid); lid += 1
    add_link(links, n_aest, 0, n_spatial, "审美addon", lid); lid += 1
    add_link(links, n_style, 0, n_art, "风格addon", lid); lid += 1
    add_link(links, n_style, 0, n_art, "颜色", lid); lid += 1
    add_link(links, n_edit, 0, n_shot, "节奏addon", lid); lid += 1
    add_link(links, n_edit, 0, n_shot, "候选1", lid); lid += 1
    add_link(links, n_soul, 0, n_shot, "灵魂addon", lid); lid += 1
    return _wrap_wf("审美全流程 v2", "Phase 28 改造 - 真实 input/output 接口", nodes, links)


# ============================================================
# 5. WORKFLOW_VERSIONED_PIPELINE: 版本化 (10 节点)
# ============================================================
def gen_workflow_versioned():
    nodes = []
    n_soul = make_node_def(1, "DirectorSoulNode", 100, 100)
    n_aest = make_node_def(2, "AestheticJudgmentPro", 100, 300)
    n_style = make_node_def(3, "StyleGuidePro", 100, 500)
    n_intent = make_node_def(4, "DirectorIntentPro", 100, 700)
    nodes.extend([n_soul, n_aest, n_style, n_intent])
    n_body = make_node_def(5, "ScriptBodyPro", 500, 100)
    n_story = make_node_def(6, "DirectorStoryboardPro", 500, 300)
    n_shot = make_node_def(7, "ShotSelectionPro", 500, 500)
    n_ver = make_node_def(8, "VersionControlPro", 500, 700)
    n_archive = make_node_def(9, "ProjectArchivePro", 500, 900)
    n_qa = make_node_def(10, "QualityAssurancePro", 500, 1100)
    nodes.extend([n_body, n_story, n_shot, n_ver, n_archive, n_qa])

    links = []
    lid = 1
    add_link(links, n_soul, 0, n_body, "灵魂addon", lid); lid += 1
    add_link(links, n_soul, 0, n_story, "灵魂addon", lid); lid += 1
    add_link(links, n_soul, 0, n_shot, "灵魂addon", lid); lid += 1
    add_link(links, n_aest, 0, n_body, "审美addon", lid); lid += 1
    add_link(links, n_aest, 0, n_story, "审美addon", lid); lid += 1
    add_link(links, n_aest, 0, n_shot, "审美addon", lid); lid += 1
    add_link(links, n_style, 0, n_body, "风格addon", lid); lid += 1
    add_link(links, n_style, 0, n_story, "风格addon", lid); lid += 1
    add_link(links, n_intent, 0, n_story, "控制addon", lid); lid += 1
    add_link(links, n_intent, 0, n_body, "控制addon", lid); lid += 1
    add_link(links, n_body, 0, n_story, "剧本正文_来自节点2", lid); lid += 1
    add_link(links, n_story, 0, n_shot, "候选1", lid); lid += 1
    add_link(links, n_story, 0, n_archive, "内容1", lid); lid += 1
    add_link(links, n_body, 0, n_archive, "内容2", lid); lid += 1
    add_link(links, n_shot, 0, n_archive, "内容3", lid); lid += 1
    add_link(links, n_body, 0, n_ver, "项目名", lid); lid += 1
    add_link(links, n_story, 0, n_qa, "场景描述", lid); lid += 1
    return _wrap_wf("版本化工作流 v2", "Phase 28 改造 - 真实 input/output 接口", nodes, links)


# ============================================================
# 6. WORKFLOW_MARKET_AWARE: 市场导向 (6 节点)
# ============================================================
def gen_workflow_market():
    nodes = []
    n_soul = make_node_def(1, "DirectorSoulNode", 100, 100)
    n_aest = make_node_def(2, "AestheticJudgmentPro", 100, 300)
    n_style = make_node_def(3, "StyleGuidePro", 100, 500)
    nodes.extend([n_soul, n_aest, n_style])
    n_pitch = make_node_def(4, "ConceptPitchPro", 500, 100)
    n_story = make_node_def(5, "DirectorStoryboardPro", 500, 300)
    n_market = make_node_def(6, "MarketAudiencePro", 500, 500)
    nodes.extend([n_pitch, n_story, n_market])

    links = []
    lid = 1
    add_link(links, n_soul, 0, n_pitch, "灵魂addon", lid); lid += 1
    add_link(links, n_soul, 0, n_story, "灵魂addon", lid); lid += 1
    add_link(links, n_aest, 0, n_pitch, "审美addon", lid); lid += 1
    add_link(links, n_aest, 0, n_story, "审美addon", lid); lid += 1
    add_link(links, n_style, 0, n_pitch, "风格addon", lid); lid += 1
    add_link(links, n_style, 0, n_story, "风格addon", lid); lid += 1
    add_link(links, n_pitch, 0, n_story, "剧本正文_来自节点2", lid); lid += 1
    add_link(links, n_soul, 0, n_market, "类型", lid); lid += 1
    return _wrap_wf("市场导向工作流 v2", "Phase 28 改造 - 真实 input/output 接口", nodes, links)


# ============================================================
# 7. WORKFLOW_CLEANUP_PUBLISH: 清理发布 (6 节点)
# ============================================================
def gen_workflow_cleanup():
    nodes = []
    n_soul = make_node_def(1, "DirectorSoulNode", 100, 100)
    n_aest = make_node_def(2, "AestheticJudgmentPro", 100, 300)
    n_style = make_node_def(3, "StyleGuidePro", 100, 500)
    n_intent = make_node_def(4, "DirectorIntentPro", 100, 700)
    n_edit = make_node_def(5, "EditingPro", 100, 900)
    nodes.extend([n_soul, n_aest, n_style, n_intent, n_edit])
    n_cleanup = make_node_def(6, "CleanupPassPro", 500, 100)
    n_format = make_node_def(7, "FormatOutputPro", 500, 300)
    n_archive = make_node_def(8, "ProjectArchivePro", 500, 500)
    n_qa = make_node_def(9, "QualityAssurancePro", 500, 700)
    nodes.extend([n_cleanup, n_format, n_archive, n_qa])

    links = []
    lid = 1
    add_link(links, n_soul, 0, n_cleanup, "灵魂addon", lid); lid += 1
    add_link(links, n_aest, 0, n_cleanup, "审美addon", lid); lid += 1
    add_link(links, n_style, 0, n_cleanup, "风格addon", lid); lid += 1
    add_link(links, n_intent, 0, n_cleanup, "控制addon", lid); lid += 1
    add_link(links, n_soul, 0, n_format, "灵魂addon", lid); lid += 1
    add_link(links, n_aest, 0, n_format, "审美addon", lid); lid += 1
    add_link(links, n_style, 0, n_format, "风格addon", lid); lid += 1
    add_link(links, n_edit, 0, n_format, "节奏addon", lid); lid += 1
    add_link(links, n_soul, 0, n_archive, "灵魂addon", lid); lid += 1
    add_link(links, n_aest, 0, n_archive, "审美addon", lid); lid += 1
    add_link(links, n_style, 0, n_archive, "风格addon", lid); lid += 1
    add_link(links, n_intent, 0, n_archive, "控制addon", lid); lid += 1
    add_link(links, n_soul, 0, n_qa, "灵魂addon", lid); lid += 1
    add_link(links, n_aest, 0, n_qa, "审美addon", lid); lid += 1
    add_link(links, n_style, 0, n_qa, "风格addon", lid); lid += 1
    add_link(links, n_edit, 0, n_qa, "节奏addon", lid); lid += 1
    add_link(links, n_intent, 0, n_qa, "控制addon", lid); lid += 1
    add_link(links, n_cleanup, 0, n_format, "输入文本", lid); lid += 1
    add_link(links, n_format, 0, n_archive, "内容1", lid); lid += 1
    return _wrap_wf("清理发布工作流 v2", "Phase 28 改造 - 真实 input/output 接口", nodes, links)


# ============================================================
# 8. WORKFLOW_MV_V2: MV v2 (6 节点)
# ============================================================
def gen_workflow_mv_v2():
    nodes = []
    n_soul = make_node_def(1, "DirectorSoulNode", 100, 100)
    n_aest = make_node_def(2, "AestheticJudgmentPro", 100, 300)
    n_style = make_node_def(3, "StyleGuidePro", 100, 500)
    nodes.extend([n_soul, n_aest, n_style])
    n_mv = make_node_def(4, "MvPro", 500, 100)
    n_music = make_node_def(5, "MusicScorePro", 500, 300)
    n_color = make_node_def(6, "ColorGradingPro", 500, 500)
    nodes.extend([n_mv, n_music, n_color])

    links = []
    lid = 1
    add_link(links, n_soul, 0, n_mv, "灵魂addon", lid); lid += 1
    add_link(links, n_soul, 0, n_music, "灵魂addon", lid); lid += 1
    add_link(links, n_soul, 0, n_color, "灵魂addon", lid); lid += 1
    add_link(links, n_aest, 0, n_mv, "审美addon", lid); lid += 1
    add_link(links, n_aest, 0, n_music, "审美addon", lid); lid += 1
    add_link(links, n_aest, 0, n_color, "审美addon", lid); lid += 1
    add_link(links, n_style, 0, n_mv, "类型", lid); lid += 1
    add_link(links, n_style, 0, n_music, "类型", lid); lid += 1
    add_link(links, n_style, 0, n_color, "类型", lid); lid += 1
    return _wrap_wf("MV 工作流 v2", "Phase 28 改造 - 真实 input/output 接口", nodes, links)


# ============================================================
# 9. WORKFLOW_ALL_NODES: 41 节点矩阵
# ============================================================
def gen_workflow_all_nodes():
    nodes = []
    # 起点节点 (4 个, 纯 widget)
    start = ["DirectorSoulNode", "AestheticJudgmentPro", "StyleGuidePro", "EditingPro", "DirectorIntentPro", "AssetRegistry"]
    for i, n in enumerate(start):
        nodes.append(make_node_def(i+1, n, 100, 100 + i*150))
    # 中间 + 终态节点 (其余 35 个)
    rest = [n for n in NODE_MAP if n not in start]
    for i, n in enumerate(rest):
        nodes.append(make_node_def(i+len(start)+1, n, 600, 100 + (i%10)*150))

    # 真实连接: 每个中间节点接 6 个 addon (从 6 个起点)
    links = []
    lid = 1
    soul_node = next(n for n in nodes if n["type"] == "DirectorSoulNode")
    aest_node = next(n for n in nodes if n["type"] == "AestheticJudgmentPro")
    style_node = next(n for n in nodes if n["type"] == "StyleGuidePro")
    edit_node = next(n for n in nodes if n["type"] == "EditingPro")
    intent_node = next(n for n in nodes if n["type"] == "DirectorIntentPro")
    p14_node = next(n for n in nodes if n["type"] == "AssetRegistry")

    for n in nodes:
        if n["type"] in start:
            continue
        # 6 个 addon
        for slot_idx, addon_name in [(0, "灵魂addon"), (0, "审美addon"), (0, "风格addon")]:
            pass  # 下面统一做

    for n in nodes:
        if n["type"] in start:
            continue
        add_link(links, soul_node, 0, n, "灵魂addon", lid); lid += 1
        add_link(links, aest_node, 0, n, "审美addon", lid); lid += 1
        add_link(links, style_node, 0, n, "风格addon", lid); lid += 1
        add_link(links, edit_node, 0, n, "节奏addon", lid); lid += 1
        add_link(links, intent_node, 0, n, "控制addon", lid); lid += 1
        add_link(links, p14_node, 0, n, "经验addon", lid); lid += 1

    return _wrap_wf("全节点矩阵 v2", "Phase 28 改造 - 41 节点, 6 addon 全连", nodes, links)


# 生成所有
print("=== 生成 v2 工作流 (真实 input/output 接口) ===\n")
save_wf("WORKFLOW_END_TO_END.json", gen_workflow_end_to_end())
save_wf("WORKFLOW_SHORT_DRAMA.json", gen_workflow_short_drama())
save_wf("WORKFLOW_MV.json", gen_workflow_mv())
save_wf("WORKFLOW_AESTHETIC_FULL.json", gen_workflow_aesthetic())
save_wf("WORKFLOW_VERSIONED_PIPELINE.json", gen_workflow_versioned())
save_wf("WORKFLOW_MARKET_AWARE.json", gen_workflow_market())
save_wf("WORKFLOW_CLEANUP_PUBLISH.json", gen_workflow_cleanup())
save_wf("WORKFLOW_MV_V2.json", gen_workflow_mv_v2())
save_wf("WORKFLOW_ALL_NODES.json", gen_workflow_all_nodes())
print("\n✅ 9 个工作流全部升级到 v2")
