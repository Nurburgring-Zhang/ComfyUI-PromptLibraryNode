# -*- coding: utf-8 -*-
"""
灵魂注入器 (Phase 36.6 v4.1+)
====================================

**问题**:
- 节点的灵魂注入字段 (灵魂_主导情感, 灵魂_场景权重 等) 在 INPUT_TYPES().required 里
- ComfyUI 加载时它们是 widget, 不能被其他节点连接
- 工作流无法实现 "DirectorSoulNode → 其他节点" 的灵魂注入

**修复**:
- 给所有有灵魂字段的节点 (26 节点) 注入 "灵魂addon" optional input slot (STRING 类型)
- 节点同时保留原 required widget (用户可直接填)
- 业务链 slot (故事架构_来自节点1, 剧本正文_来自节点2) 已在 INPUT_TYPES.optional 中

**这是 Phase 36.6 v4 关键修复 — 演示欺骗 24.0**
"""
# 26 个有灵魂字段的节点 (从 INPUT_TYPES().required 扫描)
SOUL_NODES = [
    "ScriptArchitecturePro", "ScriptBodyPro", "DirectorStoryboardPro",
    "VerticalShortDramaPro", "HookMasterPro", "DialogueMasterPro",
    "CharacterArcPro", "DirectorIntentPro", "ArtDirectionPro",
    "SpatialConsistencyPro", "SilenceMasteryPro", "ConceptPitchPro",
    "WorldBuildingPro", "ThemePhilosophyPro", "SoundDesignPro",
    "MusicScorePro", "PerformanceDirectionPro", "CostumePropSetPro",
    "EditingPro", "ColorGradingPro", "VfxPro", "MvPro", "PictureBookPro",
    "InteractiveDramaPro", "QualityAssurancePro", "AestheticJudgmentPro",
    "CinematicStudio",  # 终节点, 也接受灵魂注入
    "UniversalDirectorPromptNode",  # 通用 6 模型, 也接受灵魂注入
]

# 5 起点 (无 input, 纯 widget)
STARTING_NODES = [
    "DirectorSoulNode",
    "StyleGuidePro",
    "AssetRegistry",
    "DirectorIntentPro",  # 既是起点又接受灵魂注入, 兼容
]

# 业务链 slot: ScriptBodyPro.故事架构_来自节点1 / DirectorStoryboardPro.剧本正文_来自节点2
# 已在节点 INPUT_TYPES.optional 中
