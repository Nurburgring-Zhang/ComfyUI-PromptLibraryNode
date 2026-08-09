# -*- coding: utf-8 -*-
"""
工作流生成器 v3.1 — Phase 36.6 (修正业务链)
==============================================

**Phase 36.6 关键认知**:
- 大部分 ComfyUI 节点是 widget 驱动的,没有"接收上游数据"的 input slot
- 只有少数节点有真"业务链 input slot":
  - ScriptBodyPro.故事架构_来自节点1 (来自 ScriptArchitecturePro)
  - DirectorStoryboardPro.剧本正文_来自节点2 (来自 ScriptBodyPro)
- 真实数据流 = **起点节点注入到下游 4 个 addon slot** (灵魂/审美/风格/资产)

**正确工作流设计**:
- 5 起点节点 (DirectorSoulNode / AestheticJudgmentPro / StyleGuidePro / AssetRegistry / DirectorIntentPro)
- 注入到所有下游 production 节点的 4 个 addon slot
- 业务链 (有 input slot 时) ScriptArchitecturePro → ScriptBodyPro → DirectorStoryboardPro
- 终节点 = 用户选定的 production 节点
"""
import json
import importlib.util
import sys
from pathlib import Path

ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("pkg_init", str(ROOT / "__init__.py"))
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)
NODE_MAP = pkg.NODE_CLASS_MAPPINGS

TYPE_COLOR = {
    "STRING": "#7f9e5a", "IMAGE": "#c08234", "LATENT": "#8a5fc2", "MODEL": "#b85a4e",
    "CONDITIONING": "#e08e45", "VAE": "#d65a8c", "CLIP": "#5a8fc2",
    "MASK": "#7f9e5a", "AUDIO": "#5a9ec2", "VIDEO": "#b85a4e",
    "INT": "#5a8fc2", "FLOAT": "#5a8fc2", "BOOLEAN": "#8a5fc2", "COMBO": "#e08e45",
}

STARTING = [
    ('n_soul', 'DirectorSoulNode', 100, 100),
    ('n_aest', 'AestheticJudgmentPro', 100, 250),
    ('n_style', 'StyleGuidePro', 100, 400),
    ('n_assets', 'AssetRegistry', 100, 550),
    ('n_intent', 'DirectorIntentPro', 100, 700),
]

# 4 个 addon (Phase 36.6 真实 slot 名)
ADDONS = ['灵魂addon', '审美addon', '风格addon', '资产addon']


def get_input_slots(cls):
    """返回 (kind, fname, fspec, is_input) — is_input=True 表示是 input slot, False 表示是 widget

    ComfyUI 加载规则:
    - required + 真 input 类型 (MODEL/CLIP/VAE/LATENT/IMAGE/MASK/CONDITIONING) → 真 input slot
    - optional + 任何类型 → input slot (可被 link 也可作 widget)
    - required + STRING/INT/FLOAT/BOOLEAN/COMBO → widget only
    """
    it = cls.INPUT_TYPES()
    slots = []
    INPUT_TYPES_SET = ("MODEL", "CLIP", "VAE", "CONDITIONING", "LATENT",
                        "IMAGE", "MASK", "AUDIO", "VIDEO", "STYLE_MODEL",
                        "GLIGEN", "UPSCALE_MODEL", "CONTROL_NET", "SIGMAS",
                        "NOISE", "SAMPLER", "STRING")
    for kind in ("required", "optional"):
        for fname, fspec in it.get(kind, {}).items():
            if isinstance(fspec, tuple) and len(fspec) >= 1:
                t = fspec[0]
            else:
                t = "STRING"
            t_str = str(t).upper() if not isinstance(t, list) else "COMBO"
            # required 字段: 只有真 input 类型才是 input slot
            # optional 字段: STRING 也是 input slot (可 link), 其他都是 widget 兼容
            if kind == "optional":
                # optional STRING = input slot, 其他类型 optional 实际少见但也按 widget 处理
                is_input = t_str in ("MODEL", "CLIP", "VAE", "CONDITIONING", "LATENT",
                                      "IMAGE", "MASK", "AUDIO", "VIDEO", "STRING")
            else:  # required
                is_input = t_str in ("MODEL", "CLIP", "VAE", "CONDITIONING", "LATENT",
                                      "IMAGE", "MASK", "AUDIO", "VIDEO")
            slots.append((kind, fname, fspec, is_input))
    return slots


def get_output_info(cls):
    rt = getattr(cls, "RETURN_TYPES", ()) or ()
    rn = getattr(cls, "RETURN_NAMES", None)
    if rn and len(rn) == len(rt):
        return list(zip(rn, rt))
    return [(f"out_{i}", t) for i, t in enumerate(rt)]


# Phase 36.6 v5e: 真实业务链注入
# 起点节点的真实 output (基于 INPUT_TYPES 实际 RETURN_NAMES):
#   - DirectorSoulNode.output[0] 灵魂注入 (STRING)
#   - DirectorSoulNode.output[6] 场景提示词addon (STRING)
#   - DirectorSoulNode.output[7] H3对齐addon (STRING)
#   - AestheticJudgmentPro.output[0] 审美判断 (STRING)
#   - StyleGuidePro.output[0] 风格指南 (STRING)
#   - AssetRegistry.output[0] 资产描述符 (STRING)
#   - DirectorIntentPro.output[0] 意图声明 (STRING)
#
# production 节点实际有的 STRING input slot (真实存在):
#   - 灵魂注入 (DirectorSoulNode.output[0])
#   - 导演意图_观众应感到 (DirectorIntentPro.output[0])
#   - 上游_故事架构 (ScriptArchitecturePro.output[0])
#   - 上游_剧本正文 (ScriptBodyPro.output[0])
#   - 故事架构_来自节点1 (ScriptArchitecturePro.output[0])
#   - 剧本正文_来自节点2 (ScriptBodyPro.output[0])
#
# 起点 → production 真实注入映射 (src_node_type, src_output_index, tgt_field_name)
STARTING_INJECTIONS = [
    # 灵魂注入: 5 个起点节点的"灵魂注入"相关 output 都尝试链入 "灵魂注入" slot
    # 但只有 DirectorSoulNode.output[0] 叫"灵魂注入"
    ("DirectorSoulNode", 0, "灵魂注入"),
    # 意图注入: DirectorIntentPro → "导演意图_观众应感到"
    ("DirectorIntentPro", 0, "导演意图_观众应感到"),
]


def find_input_slot_index(node_def, fname):
    for i, inp in enumerate(node_def["inputs"]):
        if inp["name"] == fname:
            return i
    return None


def find_output_slot_index(node_def, oname):
    for i, out in enumerate(node_def.get("outputs", [])):
        if out.get("name") == oname:
            return i
    return 0  # 默认 0


def make_node_def(nid, ntype, x, y, widgets=None, label=None):
    cls = NODE_MAP[ntype]
    inputs = []  # 真 input slot
    widgets_list = []  # widget 列表 (用于显示)
    widgets_values = []  # widget 值
    for kind, fname, fspec, is_input in get_input_slots(cls):
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
        # 默认值
        if widgets and fname in widgets:
            wval = widgets[fname]
        elif isinstance(t, list):
            wval = t[0] if t else ""
        else:
            s = tname
            if s == "INT": wval = 0
            elif s == "FLOAT": wval = 1.0
            elif s == "BOOLEAN": wval = False
            else: wval = ""
        if is_input:
            # 真 input slot (在 inputs 数组里, link=None 等连接)
            inputs.append({
                "name": fname,  # **关键: name 用 INPUT_TYPES 的原始小写英文 (model/positive/negative/latent_image)**
                "type": tname,
                "link": None,
                "color": TYPE_COLOR.get(tname, "#7f9e5a"),
                "tooltip": opts.get("tooltip", ""),
            })
        else:
            # widget (在 widgets_values 里, 不进 inputs 数组)
            widgets_list.append(fname)
            widgets_values.append(wval)
    outputs = []
    for oname, otype in get_output_info(cls):
        outputs.append({
            "name": oname,
            "type": str(otype).upper(),
            "links": [],
            "color": TYPE_COLOR.get(str(otype).upper(), "#7f9e5a"),
            "slot_index": len(outputs),
        })
    return {
        "id": nid,
        "type": ntype,
        "pos": [x, y],
        "size": [260, max(100, 30 + (len(inputs) + len(widgets_list)) * 4)],
        "inputs": inputs,         # **只有真 input slot, name 用英文小写**
        "outputs": outputs,
        "widgets_values": widgets_values,  # **只有 widget 值**
        "title": label or ntype,
        "properties": {},
    }


def find_input_slot_index(node_def, fname):
    for i, inp in enumerate(node_def["inputs"]):
        if inp["name"] == fname:
            return i
    return None


def add_link(links, src_node, src_slot, tgt_node, tgt_field, link_id):
    """真实加一条 link (若 tgt_field 不存在则失败返回 None)"""
    tgt_idx = find_input_slot_index(tgt_node, tgt_field)
    if tgt_idx is None:
        return None
    if src_slot >= len(src_node["outputs"]):
        return None
    link = [link_id, src_node["id"], src_slot, tgt_node["id"], tgt_idx, "STRING"]
    links.append(link)
    src_node["outputs"][src_slot]["links"].append(link_id)
    tgt_node["inputs"][tgt_idx]["link"] = link_id
    return link


def add_starting_injection(links, starting_nodes, tgt_node, lid_start):
    """Phase 36.6 v5e: 基于 STARTING_INJECTIONS 真实映射, 链入真实存在的 slot"""
    lid = lid_start
    starting_types = {n["type"] for n, _ in starting_nodes}
    for src_type, src_slot, tgt_field in STARTING_INJECTIONS:
        if src_type not in starting_types:
            continue
        # 找 src 节点
        src_node = next((n for n, _ in starting_nodes if n["type"] == src_type), None)
        if not src_node:
            continue
        if add_link(links, src_node, src_slot, tgt_node, tgt_field, lid):
            lid += 1
    return lid


def make_workflow(name, desc, video_type, target_node, nodes, links):
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
                "description": desc,
                "video_type": video_type,
                "target_output_node": target_node,
                "total_nodes": len(nodes),
                "total_links": len(links),
                "node_types": sorted(set(n["type"] for n in nodes)),
                "real_workflow": True,
            }
        },
        "version": 0.4,
    }


def save_wf(filename, wf):
    path = ROOT / "workflows" / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)
    info = wf["extra"]["workflow_info"]
    print("  {}: {} 节点, {} links, 终节点: {}".format(
        filename, info['total_nodes'], info['total_links'], info['target_output_node']))


# 工作流通用结构
def build_wf(name, desc, video_type, target_node, production_nodes, business_chain=None):
    """
    通用工作流构建:
    - 5 个起点节点
    - N 个 production 节点
    - 起点注入到所有 production 节点的 4 个 addon slot
    - 可选业务链 (如 ScriptArch → ScriptBody → Storyboard)
    """
    nodes = []
    lid = 1

    # 5 个起点节点
    starting_nodes = []
    for var, ntype, x, y in STARTING:
        n = make_node_def(len(nodes) + 1, ntype, x, y)
        starting_nodes.append((n, 0))  # src_slot=0 (主输出)
        nodes.append(n)

    # production 节点
    for i, ntype in enumerate(production_nodes):
        n = make_node_def(len(nodes) + 1, ntype, 500 + (i // 5) * 400, 100 + (i % 5) * 150)
        nodes.append(n)

    links = []
    # Phase 36.6 v5e: 起点注入到 production 节点 (基于真实存在的 slot)
    for tgt in nodes:
        if tgt['type'] in [s[1] for s in STARTING]:
            continue
        lid = add_starting_injection(links, starting_nodes, tgt, lid)

    # 业务链 (如果有)
    if business_chain:
        for src_name, src_slot, tgt_name, tgt_field in business_chain:
            src_node = next((n for n in nodes if n['type'] == src_name), None)
            tgt_node = next((n for n in nodes if n['type'] == tgt_name), None)
            if src_node and tgt_node:
                if add_link(links, src_node, src_slot, tgt_node, tgt_field, lid):
                    lid += 1

    return make_workflow(name, desc, video_type, target_node, nodes, links), starting_nodes


# ============================================================
# 1. 电影 (60-120min) - 22 节点, 终节点 CinematicStudio
# ============================================================
def gen_film_production():
    production_nodes = [
        "ScriptArchitecturePro", "ScriptBodyPro", "DirectorStoryboardPro",
        "ConceptPitchPro", "WorldBuildingPro", "ThemePhilosophyPro",
        "ArtDirectionPro", "SpatialLayout", "ActingSkill", "CostumePropSetPro",
        "SoundDesignPro", "MusicScorePro", "SilenceMasteryPro",
        "ColorGradingPro", "VfxPro", "EditingPro", "IterationPostPro",
        "CinematicStudio",
    ]
    business_chain = [
        ("ScriptArchitecturePro", 0, "ScriptBodyPro", "故事架构_来自节点1"),
        ("ScriptBodyPro", 0, "DirectorStoryboardPro", "剧本正文_来自节点2"),
    ]
    wf, _ = build_wf(
        "电影生产工作流", "完整 60-120min 电影, 6 环节 + Phase14 全程 + 迭代",
        "电影 (60-120min)", "CinematicStudio", production_nodes, business_chain)
    return wf


# ============================================================
# 2. 30s 短剧 6 段 - 9 节点, 终节点 ThirtySecSixAct
# ============================================================
def gen_short_drama_30s():
    production_nodes = [
        "ScriptArchitecturePro", "ScriptBodyPro", "HookMasterPro",
        "PerformanceDirectionPro", "DirectorStoryboardPro", "ThirtySecSixAct",
    ]
    business_chain = [
        ("ScriptArchitecturePro", 0, "ScriptBodyPro", "故事架构_来自节点1"),
        ("ScriptBodyPro", 0, "DirectorStoryboardPro", "剧本正文_来自节点2"),
    ]
    wf, _ = build_wf(
        "30秒短剧 6 段工作流", "短视频钩子 → 6 段 (建立/引入/互动/冲突/高潮/留钩)",
        "短剧 30s 6 段", "ThirtySecSixAct", production_nodes, business_chain)
    return wf


# ============================================================
# 3. 竖屏短剧 (1-3min) - 终节点 VerticalShortDramaPro
# ============================================================
def gen_vertical_short_drama():
    production_nodes = [
        "VerticalShortDramaPro", "DialogueMasterPro", "HookMasterPro",
        "CharacterArcPro", "ShotSelectionPro", "PerformanceDirectionPro",
    ]
    wf, _ = build_wf(
        "竖屏短剧工作流", "1-3min 竖屏短剧, 钩子+爽点+付费墙",
        "竖屏短剧 (1-3min)", "VerticalShortDramaPro", production_nodes)
    return wf


# ============================================================
# 4. 抖音钩子 (3-7s) - 终节点 HookMasterPro + ThirtySecSixAct
# ============================================================
def gen_douyin_hook():
    production_nodes = [
        "HookMasterPro", "DirectorStoryboardPro", "CostumePropSetPro",
        "PerformanceDirectionPro", "ThirtySecSixAct",
    ]
    business_chain = [
        ("ScriptArchitecturePro", 0, "ScriptBodyPro", "故事架构_来自节点1"),
    ]
    wf, _ = build_wf(
        "抖音钩子短视频工作流", "3-7s 强钩子短视频, 反差/悬念/情感冲击",
        "抖音/快手 3-7s", "HookMasterPro + ThirtySecSixAct", production_nodes)
    return wf


# ============================================================
# 5. 完整剧本 - 终节点 ScriptBodyPro + DialogueMasterPro
# ============================================================
def gen_feature_script():
    production_nodes = [
        "ConceptPitchPro", "WorldBuildingPro", "ThemePhilosophyPro",
        "ScriptArchitecturePro", "ScriptBodyPro", "CharacterArcPro",
        "DialogueMasterPro",
    ]
    business_chain = [
        ("ScriptArchitecturePro", 0, "ScriptBodyPro", "故事架构_来自节点1"),
    ]
    wf, _ = build_wf(
        "完整剧本工作流", "概念→世界观→主题→架构→主体→人物→对白",
        "完整剧本 (60-120min)", "ScriptBodyPro + DialogueMasterPro",
        production_nodes, business_chain)
    return wf


# ============================================================
# 6. 完整分镜 - 终节点 DirectorStoryboardPro
# ============================================================
def gen_storyboard():
    production_nodes = [
        "ScriptArchitecturePro", "ScriptBodyPro", "CharacterArcPro",
        "DirectorStoryboardPro", "ArtDirectionPro", "ShotSelectionPro",
    ]
    business_chain = [
        ("ScriptArchitecturePro", 0, "ScriptBodyPro", "故事架构_来自节点1"),
        ("ScriptBodyPro", 0, "DirectorStoryboardPro", "剧本正文_来自节点2"),
    ]
    wf, _ = build_wf(
        "完整分镜工作流", "剧本→分镜→镜头选择→美术指导",
        "完整分镜 (L1-L7 7层)", "DirectorStoryboardPro", production_nodes, business_chain)
    return wf


# ============================================================
# 7. MV (3-5min) - 终节点 MvPro + MusicScorePro
# ============================================================
def gen_mv():
    production_nodes = [
        "MvPro", "DirectorStoryboardPro", "MusicScorePro", "EditingPro",
        "ColorGradingPro",
    ]
    wf, _ = build_wf(
        "MV 音乐视频工作流", "3-5min MV, 音乐驱动 + 视觉叙事 + 剪辑节奏",
        "MV 音乐视频 (3-5min)", "MvPro + MusicScorePro", production_nodes)
    return wf


# ============================================================
# 8. 绘本 (5-10min) - 终节点 PictureBookPro
# ============================================================
def gen_picture_book():
    production_nodes = [
        "PictureBookPro", "WorldBuildingPro", "CharacterArcPro", "ArtDirectionPro",
    ]
    wf, _ = build_wf(
        "绘本工作流", "5-10min 儿童绘本, 视觉连续性 + 5 维感官 + 留白节奏",
        "绘本 (5-10min)", "PictureBookPro", production_nodes)
    return wf


# ============================================================
# 9. 互动剧 (30-60min) - 终节点 InteractiveDramaPro
# ============================================================
def gen_interactive_drama():
    production_nodes = [
        "ScriptArchitecturePro", "ScriptBodyPro", "InteractiveDramaPro",
        "DialogueMasterPro", "CharacterArcPro", "DirectorStoryboardPro",
    ]
    business_chain = [
        ("ScriptArchitecturePro", 0, "ScriptBodyPro", "故事架构_来自节点1"),
        ("ScriptBodyPro", 0, "DirectorStoryboardPro", "剧本正文_来自节点2"),
    ]
    wf, _ = build_wf(
        "互动剧工作流", "30-60min 互动剧, 多分支选择 + 关键节点 + 状态追踪",
        "互动剧 (30-60min)", "InteractiveDramaPro", production_nodes, business_chain)
    return wf


# ============================================================
# 10. 品牌宣传片 (60-180s) - 终节点 CinematicStudio
# ============================================================
def gen_brand_film():
    production_nodes = [
        "ConceptPitchPro", "ScriptBodyPro", "ArtDirectionPro",
        "DirectorStoryboardPro", "ThirtySecSixAct", "CinematicStudio",
    ]
    business_chain = [
        ("ScriptArchitecturePro", 0, "ScriptBodyPro", "故事架构_来自节点1"),
    ]
    wf, _ = build_wf(
        "品牌宣传片工作流", "60-180s 品牌片, 概念→品牌叙事→视觉锤→多模型发布",
        "品牌宣传 (60-180s)", "CinematicStudio", production_nodes, business_chain)
    return wf


# ============================================================
# 11. 极简产品广告 (15-30s) - 终节点 CinematicStudio
# ============================================================
def gen_minimalist_product_ad():
    production_nodes = [
        "ConceptPitchPro", "ArtDirectionPro", "DirectorStoryboardPro",
        "CinematicStudio",
    ]
    wf, _ = build_wf(
        "极简产品广告工作流", "15-30s 极简产品广告, 视觉锤 + 一句卖点",
        "极简产品广告 (15-30s)", "CinematicStudio", production_nodes)
    return wf


# ============================================================
# 12. 完整声音设计 - 终节点 SoundDesignPro + MusicScorePro
# ============================================================
def gen_sound_design():
    production_nodes = [
        "DirectorStoryboardPro", "SoundDesignPro", "MusicScorePro",
        "SilenceMasteryPro", "SoundSkill", "EditingPro",
    ]
    wf, _ = build_wf(
        "完整声音设计工作流", "分镜→声音设计→音乐→沉默→声音技能→剪辑",
        "完整声音设计", "SoundDesignPro + MusicScorePro", production_nodes)
    return wf


# ============================================================
# 13. 完整调色 - 终节点 ColorGradingPro
# ============================================================
def gen_color_grading():
    production_nodes = [
        "DirectorStoryboardPro", "ArtDirectionPro", "ColorGradingPro", "VfxPro",
    ]
    wf, _ = build_wf(
        "完整调色工作流", "分镜→美术→调色 (60-30-10) → 特效",
        "完整调色 (60-30-10)", "ColorGradingPro", production_nodes)
    return wf


# ============================================================
# 14. 3D 动画短片 - 终节点 CinematicStudio (3D 模式)
# ============================================================
def gen_3d_animation():
    production_nodes = [
        "ConceptPitchPro", "WorldBuildingPro", "DirectorStoryboardPro",
        "ArtDirectionPro", "ActingSkill", "CinematicStudio",
    ]
    wf, _ = build_wf(
        "3D 动画短片工作流", "3D 动画短片, 角色一致性 + 物理真实 + 多角度镜头",
        "3D 动画短片", "CinematicStudio (3D 模式)", production_nodes)
    return wf


# ============================================================
# 15. H3 多模态生产 - 终节点 H3ContextIRNode
# ============================================================
def gen_h3_production():
    production_nodes = [
        "ScriptArchitecturePro", "DirectorStoryboardPro", "CinematicStudio",
        "H3ContextIRNode",
    ]
    business_chain = [
        ("ScriptArchitecturePro", 0, "ScriptBodyPro", "故事架构_来自节点1"),
    ]
    wf, _ = build_wf(
        "H3 多模态生产工作流", "MiniMax H3 5 模式 (T2VA/I2VA/FL2VA/L2VA/Ref2VA) + 4 reference labels",
        "H3 多模态生产", "H3ContextIRNode", production_nodes, business_chain)
    return wf


# ============================================================
# 16. 6 大模型通用 prompt - 终节点 UniversalDirectorPromptNode
# ============================================================
def gen_universal_6models():
    production_nodes = [
        "ScriptArchitecturePro", "ScriptBodyPro", "DirectorStoryboardPro",
        "ArtDirectionPro", "UniversalDirectorPromptNode",
    ]
    business_chain = [
        ("ScriptArchitecturePro", 0, "ScriptBodyPro", "故事架构_来自节点1"),
        ("ScriptBodyPro", 0, "DirectorStoryboardPro", "剧本正文_来自节点2"),
    ]
    wf, _ = build_wf(
        "6 大模型通用 prompt 工作流",
        "H3/Seedance/Wan/Sora/Veo/短剧 6 模型路由 + 通用 5 段 (SUBJECT/STYLE/SHOT/ACTION/AUDIO)",
        "6 大模型通用 prompt", "UniversalDirectorPromptNode",
        production_nodes, business_chain)
    return wf


# ============================================================
# 17. 质量审核 + 发布 - 终节点 ProjectArchivePro
# ============================================================
def gen_qa_publish():
    production_nodes = [
        "QualityAssurancePro", "CleanupPassPro", "VersionControlPro",
        "FormatOutputPro", "MarketAudiencePro", "ProjectArchivePro",
    ]
    wf, _ = build_wf(
        "质量审核 + 发布工作流", "QA → Cleanup → 版本控制 → 格式化 → 市场分析 → 归档",
        "质量审核 + 发布", "ProjectArchivePro", production_nodes)
    return wf


# ============================================================
# 主入口
# ============================================================
def main():
    generators = [
        (gen_film_production, "WORKFLOW_FILM_PRODUCTION.json"),
        (gen_short_drama_30s, "WORKFLOW_SHORT_DRAMA_30S.json"),
        (gen_vertical_short_drama, "WORKFLOW_VERTICAL_SHORT_DRAMA.json"),
        (gen_douyin_hook, "WORKFLOW_DOUYIN_HOOK.json"),
        (gen_feature_script, "WORKFLOW_FEATURE_SCRIPT.json"),
        (gen_storyboard, "WORKFLOW_STORYBOARD.json"),
        (gen_mv, "WORKFLOW_MV.json"),
        (gen_picture_book, "WORKFLOW_PICTURE_BOOK.json"),
        (gen_interactive_drama, "WORKFLOW_INTERACTIVE_DRAMA.json"),
        (gen_brand_film, "WORKFLOW_BRAND_FILM.json"),
        (gen_minimalist_product_ad, "WORKFLOW_MINIMALIST_PRODUCT_AD.json"),
        (gen_sound_design, "WORKFLOW_SOUND_DESIGN.json"),
        (gen_color_grading, "WORKFLOW_COLOR_GRADING.json"),
        (gen_3d_animation, "WORKFLOW_3D_ANIMATION.json"),
        (gen_h3_production, "WORKFLOW_H3_PRODUCTION.json"),
        (gen_universal_6models, "WORKFLOW_UNIVERSAL_6MODELS.json"),
        (gen_qa_publish, "WORKFLOW_QA_PUBLISH.json"),
    ]
    print("=" * 70)
    print("Phase 36.6: 17 个真生产工作流 (覆盖项目所有视频类型)")
    print("=" * 70)
    for gen_func, filename in generators:
        wf = gen_func()
        save_wf(filename, wf)
    print()
    print("=" * 70)
    print("生成完成: {} 个工作流".format(len(generators)))
    print("=" * 70)


if __name__ == "__main__":
    main()
