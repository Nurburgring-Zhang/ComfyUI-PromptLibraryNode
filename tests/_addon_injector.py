# -*- coding: utf-8 -*-
"""
Addon 注入器 - 统一给 Production 节点加 6 个 STRING input slot
- 灵魂addon: 接 DirectorSoulNode.soul_injection
- 审美addon: 接 AestheticJudgmentPro.judgment_main
- 风格addon: 接 StyleGuidePro.guide_main
- 经验addon: 接 Phase14Xxx 的经验输出
- 控制addon: 接 DirectorIntentPro.intent_main
- 节奏addon: 接 EditingPro.edit_main
"""
# ComfyUI STRING 颜色 = 绿色
# 这些 addon 是 forceInput 的 input slot, 用户必须接上游节点
# 但保留默认值, 让节点独立可用

ADDON_INPUTS = {
    "灵魂addon": {
        "default": "",
        "tooltip": "【接入上游】DirectorSoulNode 的灵魂注入输出 (8 维情感/状态/导演签名)\n"
                   "起点节点: DirectorSoulNode (无上游,纯 widget 即可启动)"
    },
    "审美addon": {
        "default": "",
        "tooltip": "【接入上游】AestheticJudgmentPro 的审美判断输出 (8原则+6导演+120场景)\n"
                   "起点节点: AestheticJudgmentPro"
    },
    "风格addon": {
        "default": "",
        "tooltip": "【接入上游】StyleGuidePro 的风格指南输出 (5调色+5配色+6导演+20口诀)\n"
                   "起点节点: StyleGuidePro"
    },
    "经验addon": {
        "default": "",
        "tooltip": "【接入上游】Phase14 系列 (资产/空间/表演/声音/迭代) 的经验矩阵输出\n"
                   "起点节点: AssetRegistry / SpatialLayout / ActingSkill / SoundSkill"
    },
    "控制addon": {
        "default": "",
        "tooltip": "【接入上游】DirectorIntentPro 的导演意图输出 (4 类意图)\n"
                   "起点节点: DirectorIntentPro"
    },
    "节奏addon": {
        "default": "",
        "tooltip": "【接入上游】EditingPro 的剪辑节奏输出 (情绪节奏+切点策略+长镜+跳切+蒙太奇)\n"
                   "起点节点: EditingPro"
    },
}


def make_addon_input(tooltip_text):
    """返回一个 ComfyUI STRING input slot schema, forceInput 强制作为 input 接口"""
    return ("STRING", {"default": "", "multiline": True, "forceInput": True, "tooltip": tooltip_text})


def inject_addon_inputs(cls, addon_keys=None):
    """
    给节点类注入 6 个 STRING input slot (在 optional 里)
    节点主入口函数用 **kwargs 接收, 所以不需要改源码
    """
    if addon_keys is None:
        addon_keys = list(ADDON_INPUTS.keys())

    # INPUT_TYPES 在 ComfyUI 中是 classmethod 或 static method
    # 我们用 static method 包装更简单
    original_input_types = cls.INPUT_TYPES

    # 检测原 INPUT_TYPES 是 classmethod 还是 staticmethod
    if isinstance(original_input_types, classmethod):
        original_func = original_input_types.__func__
    else:
        original_func = original_input_types

    def new_input_types(*args, **kwargs):
        # 调用原函数 (可能是 classmethod/staticmethod, 尝试不同调用方式)
        try:
            result = original_input_types()
        except TypeError:
            try:
                result = original_input_types.__func__()
            except Exception:
                result = original_input_types(cls)
        if not isinstance(result, dict):
            return result
        # 确保有 optional
        if "optional" not in result:
            result["optional"] = {}
        for key in addon_keys:
            if key not in result["optional"]:
                info = ADDON_INPUTS[key]
                result["optional"][key] = make_addon_input(info["tooltip"])
        return result

    # 用 classmethod 替换 (ComfyUI 标准是 classmethod)
    cls.INPUT_TYPES = classmethod(new_input_types)
    return cls


# 哪些节点是 Production 节点 (中间态, 需要 input slot)
# 起点节点 (无 input slot,纯 widget): DirectorSoulNode, AestheticJudgmentPro, StyleGuidePro
# Phase14 系列: 部分是起点 (AssetRegistry), 部分是中间态
# 工具节点 (ProjectArchivePro / FormatOutputPro / CleanupPassPro): 终态, 接受 input

PRODUCTION_NODES = [
    # Phase 9 (剧本)
    "ScriptArchitecturePro",      # 中间 (接 ConceptPitchPro)
    "ScriptBodyPro",              # 中间 (接 ScriptArchitecturePro)
    "DirectorStoryboardPro",      # 中间 (接 ScriptBodyPro)
    # Phase 11 (专业)
    "VerticalShortDramaPro",      # 中间
    "HookMasterPro",              # 中间
    "DialogueMasterPro",          # 中间
    "CharacterArcPro",            # 中间
    # Phase 12 (附件)
    "DirectorIntentPro",          # 中间
    "ArtDirectionPro",            # 中间
    "SpatialConsistencyPro",      # 中间
    "SilenceMasteryPro",          # 中间
    # Phase 12续+13 (生产环节)
    "ConceptPitchPro",            # 中间 (有灵魂/审美/风格 addon)
    "WorldBuildingPro",           # 中间
    "ThemePhilosophyPro",         # 中间
    "SoundDesignPro",             # 中间
    "MusicScorePro",              # 中间
    "PerformanceDirectionPro",    # 中间
    "CostumePropSetPro",          # 中间
    "EditingPro",                 # 中间
    "ColorGradingPro",            # 中间
    "VfxPro",                     # 中间
    "MvPro",                      # 中间
    "PictureBookPro",             # 中间
    "InteractiveDramaPro",        # 中间
    "QualityAssurancePro",        # 中间
    # Phase 14 (Hell Grind)
    "SpatialLayout",       # 中间 (接 AssetRegistry)
    "ActingSkill",         # 中间
    "SoundSkill",          # 中间
    "IterationPostPro",           # 中间
    "ThirtySecSixAct",          # 中间
    "CinematicStudio",    # 中间
    # Phase 27
    "ShotSelectionPro",           # 中间
    # Phase 28 P1+P2
    "VersionControlPro",          # 中间
    "MarketAudiencePro",          # 中间
    "CleanupPassPro",             # 中间
    "FormatOutputPro",            # 中间
    "ProjectArchivePro",          # 终态
    # 起点节点 (无 input slot)
    # DirectorSoulNode - 起点, 纯 widget
    # AestheticJudgmentPro - 起点, 纯 widget
    # StyleGuidePro - 起点, 纯 widget
    # AssetRegistry - 起点 (资产注册)
]

# 起点节点 (纯 widget,无 input slot)
STARTING_NODES = [
    "DirectorSoulNode",
    "AestheticJudgmentPro",
    "StyleGuidePro",
    "AssetRegistry",
]
