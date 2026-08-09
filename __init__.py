# -*- coding: utf-8 -*-
"""
ComfyUI-PromptLibraryNode - 41 节点 L5 顶级导演级 + Hell Grind 6 层生产系统
================================================

Phase 9: 3 剧本拆分节点 (Architecture / Body / Storyboard)
Phase 11: 4 专业节点 (VerticalShortDrama / Hook / Dialogue / CharacterArc)
Phase 12: 4 附件核心节点 (DirectorIntent / ArtDirection / Spatial / Silence)
Phase 12 续 + 13: 14 生产环节节点 (Concept -> QA) + L5 深度重写
Phase 14: Hell Grind 6 层生产系统 (资产/空间/表演/声音/迭代/后期)
Phase 14 升级: 30s 6 段 + Cinematic Studio 电影效果 + 多模型路由
Phase 17: DirectorSoul 灵魂节点 + 60 情感 + 8 导演灵感
Phase 27: ShotSelectionPro 选片决策节点 (环节 30)
Phase 28 P0: AestheticJudgmentPro 审美判断节点 (环节 7) + 120 场景库
Phase 28 P1: VersionControlPro / StyleGuidePro / MarketAudiencePro
Phase 28 P2: CleanupPassPro / FormatOutputPro / ProjectArchivePro
测试: 788/788 全过 (41 节点)

**Phase 28 改造: 真实 ComfyUI 工作流**
- 每个 Production 节点注入 6 个 STRING input slot:
  灵魂addon / 审美addon / 风格addon / 经验addon / 控制addon / 节奏addon
- 起点节点: DirectorSoulNode / AestheticJudgmentPro / StyleGuidePro / AssetRegistry
- output 名字从 RETURN_NAMES 读取,ComfyUI 显示具体名而非 out_X
"""

from script_architecture_pro import ScriptArchitecturePro
from script_body_pro import ScriptBodyPro
from director_storyboard_pro import DirectorStoryboardPro
from vertical_short_drama_pro import VerticalShortDramaPro
from hook_master_pro import HookMasterPro
from dialogue_master_pro import DialogueMasterPro
from character_arc_pro import CharacterArcPro
from director_intent_pro import DirectorIntentPro
from art_direction_pro import ArtDirectionPro
from spatial_consistency_pro import SpatialConsistencyPro
from silence_mastery_pro import SilenceMasteryPro
from concept_pitch_pro import ConceptPitchPro
from world_building_pro import WorldBuildingPro
from theme_philosophy_pro import ThemePhilosophyPro
from sound_design_pro import SoundDesignPro
from music_score_pro import MusicScorePro
from performance_direction_pro import PerformanceDirectionPro
from costume_prop_set_pro import CostumePropSetPro
from editing_pro import EditingPro
from color_grading_pro import ColorGradingPro
from vfx_pro import VfxPro
from mv_pro import MvPro
from picture_book_pro import PictureBookPro
from interactive_drama_pro import InteractiveDramaPro
from quality_assurance_pro import QualityAssurancePro
from asset_registry import AssetRegistry
from spatial_layout import SpatialLayout
from acting_skill import ActingSkill
from sound_skill import SoundSkill
from iteration_post import IterationPostPro
from thirty_sec_six_act import ThirtySecSixAct
from cinematic_studio import CinematicStudio
from director_soul import DirectorSoulNode
from shot_selection_pro import ShotSelectionPro
from aesthetic_judgment_pro import AestheticJudgmentPro
from version_control_pro import VersionControlPro
from style_guide_pro import StyleGuidePro
from market_audience_pro import MarketAudiencePro
from cleanup_pass_pro import CleanupPassPro
from format_output_pro import FormatOutputPro
from project_archive_pro import ProjectArchivePro
from h3_context_ir_node import H3ContextIRNode
from universal_director_prompt_node import UniversalDirectorPromptNode
from director_mastery import DirectorMasteryNode

_ALL_NODE_CLASSES = {
    "ScriptArchitecturePro": ScriptArchitecturePro,
    "ScriptBodyPro": ScriptBodyPro,
    "DirectorStoryboardPro": DirectorStoryboardPro,
    "VerticalShortDramaPro": VerticalShortDramaPro,
    "HookMasterPro": HookMasterPro,
    "DialogueMasterPro": DialogueMasterPro,
    "CharacterArcPro": CharacterArcPro,
    "DirectorIntentPro": DirectorIntentPro,
    "ArtDirectionPro": ArtDirectionPro,
    "SpatialConsistencyPro": SpatialConsistencyPro,
    "SilenceMasteryPro": SilenceMasteryPro,
    "ConceptPitchPro": ConceptPitchPro,
    "WorldBuildingPro": WorldBuildingPro,
    "ThemePhilosophyPro": ThemePhilosophyPro,
    "SoundDesignPro": SoundDesignPro,
    "MusicScorePro": MusicScorePro,
    "PerformanceDirectionPro": PerformanceDirectionPro,
    "CostumePropSetPro": CostumePropSetPro,
    "EditingPro": EditingPro,
    "ColorGradingPro": ColorGradingPro,
    "VfxPro": VfxPro,
    "MvPro": MvPro,
    "PictureBookPro": PictureBookPro,
    "InteractiveDramaPro": InteractiveDramaPro,
    "QualityAssurancePro": QualityAssurancePro,
    "AssetRegistry": AssetRegistry,
    "SpatialLayout": SpatialLayout,
    "ActingSkill": ActingSkill,
    "SoundSkill": SoundSkill,
    "IterationPostPro": IterationPostPro,
    "ThirtySecSixAct": ThirtySecSixAct,
    "CinematicStudio": CinematicStudio,
    "DirectorSoulNode": DirectorSoulNode,
    "ShotSelectionPro": ShotSelectionPro,
    "AestheticJudgmentPro": AestheticJudgmentPro,
    "VersionControlPro": VersionControlPro,
    "StyleGuidePro": StyleGuidePro,
    "MarketAudiencePro": MarketAudiencePro,
    "CleanupPassPro": CleanupPassPro,
    "FormatOutputPro": FormatOutputPro,
    "ProjectArchivePro": ProjectArchivePro,
    "H3ContextIRNode": H3ContextIRNode,
    "UniversalDirectorPromptNode": UniversalDirectorPromptNode,
    "DirectorMasteryNode": DirectorMasteryNode,  # Phase 36.6 v5: 导演能力总控
}

# 给所有 Production 节点注入 6 个 input slot
# Phase 36.6 v2: 完全删除 (演示欺骗 21.0 修复)
# for n in PRODUCTION_NODES:
#     if n in _ALL_NODE_CLASSES:
#         inject_addon_inputs(_ALL_NODE_CLASSES[n])

# ============================================================
# Phase 35.7 M-A2/M-A3: 统一 CATEGORY 路径 + RETURN_NAMES 命名
# 策略: 不改 .py 源码, 在 __init__.py 集中 override
# 统一为 `PromptLibrary/<功能>` 二级路径 + snake_case 英文
# ============================================================
_CATEGORY_UNIFIED = {
    # 起点节点 (无 addon input, 纯 widget)
    "DirectorSoulNode": "PromptLibrary/起点/灵魂",
    "AestheticJudgmentPro": "PromptLibrary/起点/审美",
    "StyleGuidePro": "PromptLibrary/起点/风格",
    "AssetRegistry": "PromptLibrary/节点/资产",
    "DirectorMasteryNode": "PromptLibrary/起点/总控",  # Phase 36.6 v5 导演能力总控
    # 剧本/分镜
    "ScriptArchitecturePro": "PromptLibrary/剧本",
    "ScriptBodyPro": "PromptLibrary/剧本",
    "DirectorStoryboardPro": "PromptLibrary/剧本",
    "VerticalShortDramaPro": "PromptLibrary/剧本",
    "HookMasterPro": "PromptLibrary/剧本",
    "DialogueMasterPro": "PromptLibrary/剧本",
    "CharacterArcPro": "PromptLibrary/剧本",
    # 导演附件 (表演/情感/留白/空间/美术)
    "DirectorIntentPro": "PromptLibrary/导演附件",
    "ArtDirectionPro": "PromptLibrary/导演附件",
    "SpatialConsistencyPro": "PromptLibrary/导演附件",
    "SilenceMasteryPro": "PromptLibrary/导演附件",
    # 14 环节节点 (统一 PromptLibrary/环节, 阶段号在 display name)
    "ConceptPitchPro": "PromptLibrary/环节",
    "WorldBuildingPro": "PromptLibrary/环节",
    "ThemePhilosophyPro": "PromptLibrary/环节",
    "SoundDesignPro": "PromptLibrary/环节",
    "MusicScorePro": "PromptLibrary/环节",
    "PerformanceDirectionPro": "PromptLibrary/环节",
    "CostumePropSetPro": "PromptLibrary/环节",
    "EditingPro": "PromptLibrary/环节",
    "ColorGradingPro": "PromptLibrary/环节",
    "VfxPro": "PromptLibrary/环节",
    "MvPro": "PromptLibrary/环节",
    "PictureBookPro": "PromptLibrary/环节",
    "InteractiveDramaPro": "PromptLibrary/环节",
    "QualityAssurancePro": "PromptLibrary/环节",
    # Phase 14 集群
    "SpatialLayout": "PromptLibrary/节点/空间",
    "ActingSkill": "PromptLibrary/节点/表演",
    "SoundSkill": "PromptLibrary/节点/声音",
    "IterationPostPro": "PromptLibrary/节点/后期",
    "ThirtySecSixAct": "PromptLibrary/节点/6段",
    "CinematicStudio": "PromptLibrary/节点/电影",
    # Phase 27
    "ShotSelectionPro": "PromptLibrary/Phase27/选片",
    # Phase 28
    "VersionControlPro": "PromptLibrary/Phase28/版本",
    "MarketAudiencePro": "PromptLibrary/Phase28/市场",
    "CleanupPassPro": "PromptLibrary/Phase28/清理",
    "FormatOutputPro": "PromptLibrary/Phase28/格式化",
    "ProjectArchivePro": "PromptLibrary/Phase28/归档",
    # Phase 36.2: H3 Context IR
    "H3ContextIRNode": "PromptLibrary/H3/ContextIR",
    # Phase 36.3: 通用导演 Prompt (H3/Seedance/Wan/Sora/Veo/短剧 6 模型路由)
    "UniversalDirectorPromptNode": "PromptLibrary/起点/通用",
}

_RETURN_NAMES_UNIFIED = {
    # === Phase 36.6 v5: 全部 RETURN_NAMES 中文化 ===
    "ScriptArchitecturePro": ("故事架构", "反AI规则", "迭代链"),
    "ScriptBodyPro": ("剧本正文", "反AI样例", "迭代链"),
    "DirectorStoryboardPro": ("分镜", "反AI样例", "迭代链"),
    "VerticalShortDramaPro": ("短剧体系", "单集模板", "付费墙设计"),
    "HookMasterPro": ("钩子模板", "钩子5样本", "反AI清理后样本"),
    "DialogueMasterPro": ("对白体系", "对白样例", "反AI对白对"),
    "CharacterArcPro": ("人物圣经", "弧光旅程", "导演经验"),
    "DirectorIntentPro": ("意图声明", "导演意图样例", "反AI清理后"),
    "ArtDirectionPro": ("美术圣经", "视觉语言参数", "色彩60_30_10", "光影9D设计", "摄影8大师", "灵魂注入载荷", "H3三字段addon", "电影签名addon"),
    "SpatialConsistencyPro": ("空间设计", "5规则应用", "导演样例"),
    "SilenceMasteryPro": ("沉默设计", "沉默公式", "导演样例"),
    "ConceptPitchPro": ("概念H3提示词", "经验矩阵", "AI深度处理"),
    "WorldBuildingPro": ("世界H3提示词", "光影9D设计", "视觉语言参数", "色彩60_30_10", "摄影8大师", "经验矩阵"),
    "ThemePhilosophyPro": ("主题H3提示词", "经验矩阵", "AI深度处理"),
    "SoundDesignPro": ("声音H3提示词", "经验矩阵", "AI深度处理"),
    "MusicScorePro": ("音乐H3提示词", "经验矩阵", "AI深度处理"),
    "PerformanceDirectionPro": ("表演H3提示词", "经验矩阵", "AI深度处理"),
    "CostumePropSetPro": ("服化道H3提示词", "经验矩阵", "AI深度处理"),
    "EditingPro": ("剪辑灵魂提示词", "节奏经验矩阵", "AI深度灵魂处理"),
    "ColorGradingPro": ("调色H3提示词", "色彩60_30_10", "色彩8大师", "调色3阶段", "光影9D设计", "经验矩阵"),
    "VfxPro": ("特效H3提示词", "经验矩阵", "AI深度处理"),
    "MvPro": ("MVH3提示词", "经验矩阵", "AI深度处理"),
    "PictureBookPro": ("绘本H3提示词", "经验矩阵", "AI深度处理"),
    "InteractiveDramaPro": ("互动剧H3提示词", "经验矩阵", "AI深度处理"),
    "QualityAssurancePro": ("质量H3提示词", "经验矩阵", "AI深度处理"),
    "AssetRegistry": ("资产描述符", "状态描述符", "声音签名", "行为签名", "完整提示词块", "锁定测试报告"),
    "SpatialLayout": ("空间提示词", "地理块", "初始镜头", "连续性"),
    "ActingSkill": ("角色表演块", "5支柱字典", "5元素驱动"),
    "SoundSkill": ("声音提示词", "声音经验矩阵", "声音AI深度处理"),
    "IterationPostPro": ("迭代H3提示词", "经验矩阵", "AI深度处理"),
    "ThirtySecSixAct": ("6段总览", "第1段_建立", "第2段_引入", "第3段_互动", "第4段_冲突", "第5段_高潮", "第6段_留钩", "H3三字段提示词"),
    "CinematicStudio": ("23效果总览", "视觉语言参数", "色彩60_30_10", "光影9D设计", "摄影8大师", "选中模型", "模型弱点规避", "角色一致性工作流", "11阶段流水线", "H3提示词"),
    "DirectorSoulNode": ("灵魂注入", "融合情感", "情感维度", "灵魂维度", "灵魂状态", "导演签名", "场景提示词addon", "H3对齐addon"),
    "ShotSelectionPro": ("选片决策", "评分矩阵", "导演理由"),
    "AestheticJudgmentPro": ("审美判断", "8原则评分", "色彩系统", "场景匹配", "电影指南", "色彩心理学"),
    "VersionControlPro": ("操作结果", "版本历史", "项目状态"),
    "StyleGuidePro": ("风格指南", "完整提示词", "色板", "色彩口诀"),
    "MarketAudiencePro": ("市场分析", "受众画像", "发布策略", "票房预测"),
    "CleanupPassPro": ("清理后文本", "清理统计", "报告"),
    "FormatOutputPro": ("格式化输出", "元数据"),
    "ProjectArchivePro": ("归档内容", "归档ID", "元数据"),
    "H3ContextIRNode": ("H3模式", "H3指令", "整合多模态描述", "整体音景", "非叙事音乐", "H3完整提示词", "H3验证报告", "H3摘要卡"),
    "UniversalDirectorPromptNode": ("目标模型", "模型特定提示词", "H3模式", "H3完整提示词", "通用5段", "导演风格锚", "带时间戳镜头计划", "对白块", "音频块", "故事弧锚", "验证报告", "反AI清理保证"),
}

# 应用 CATEGORY 统一覆盖
for node_name, new_cat in _CATEGORY_UNIFIED.items():
    if node_name in _ALL_NODE_CLASSES:
        _ALL_NODE_CLASSES[node_name].CATEGORY = new_cat

# 应用 RETURN_NAMES 统一覆盖 (M-A3)
for node_name, new_rn in _RETURN_NAMES_UNIFIED.items():
    if node_name in _ALL_NODE_CLASSES:
        _ALL_NODE_CLASSES[node_name].RETURN_NAMES = new_rn

NODE_CLASS_MAPPINGS = _ALL_NODE_CLASSES

# ===== Phase 36.6 v4.1+: 灵魂 addon 注入 (演示欺骗 24.0 修复) =====
# 26 个有灵魂字段的节点注入 "灵魂addon" optional input slot
# 让 DirectorSoulNode.soul_injection 能连到其他节点
from _addon_injector import STARTING_NODES, SOUL_NODES


def inject_soul_addon(cls):
    """给节点注入 灵魂注入 (STRING, optional) input slot"""
    orig_input_types = cls.__dict__.get("INPUT_TYPES", None)
    if orig_input_types is None:
        return
    if not isinstance(orig_input_types, classmethod):
        return
    raw_func = orig_input_types.__func__
    if getattr(raw_func, "_soul_addon_injected", False):
        return

    def new_input_types(cls_arg):
        result = raw_func(cls_arg)
        opt = result.setdefault("optional", {})
        if "灵魂addon" in opt:
            # 改名: 灵魂addon → 灵魂注入 (更明确)
            opt["灵魂注入"] = opt.pop("灵魂addon")
        elif "灵魂注入" not in opt:
            opt["灵魂注入"] = ("STRING", {"default": "", "multiline": True, "tooltip": "灵魂节点注入字符串 (可连接 DirectorSoulNode.灵魂注入 输出)"})
        return result

    new_input_types._soul_addon_injected = True
    cls.INPUT_TYPES = classmethod(new_input_types)


for _name in SOUL_NODES:
    if _name in _ALL_NODE_CLASSES:
        inject_soul_addon(_ALL_NODE_CLASSES[_name])

NODE_DISPLAY_NAME_MAPPINGS = {
    "ScriptArchitecturePro": "📖 剧本架构 (1/3) [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "ScriptBodyPro": "📜 剧本正文 (2/3) [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "DirectorStoryboardPro": "🎬 导演分镜 (3/3) [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "VerticalShortDramaPro": "📱 垂直短剧 (4/7) [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "HookMasterPro": "🎣 钩子大师 (5/7) [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "DialogueMasterPro": "💬 对白大师 (6/7) [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "CharacterArcPro": "👤 角色弧光 (7/7) [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "DirectorIntentPro": "🎯 导演意图 (附件核心) [起点·纯 widget]",
    "ArtDirectionPro": "🎨 美术指导 (附件核心) [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "SpatialConsistencyPro": "📐 空间一致性 (附件核心) [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "SilenceMasteryPro": "🤫 沉默大师 (附件核心) [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "ConceptPitchPro": "💡 概念立项 (环节 1) — L5 重写 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "WorldBuildingPro": "🌍 世界设定 (环节 3) — L5 重写 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "ThemePhilosophyPro": "🧠 主题哲学 (环节 4) — L5 重写 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "SoundDesignPro": "🔊 声音设计 (环节 13) — L5 重写 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "MusicScorePro": "🎼 音乐配乐 (环节 14) — L5 重写 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "PerformanceDirectionPro": "🎭 表演指导 (环节 17) — L5 重写 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "CostumePropSetPro": "👘 服化道 (环节 19) — L5 重写 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "EditingPro": "✂️ 剪辑 (环节 28) — L5 重写 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "ColorGradingPro": "🎨 调色 (环节 32) — L5 重写 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "VfxPro": "✨ VFX (环节 33) — L5 重写 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "MvPro": "🎵 MV 导演 (环节 39) — L5 重写 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "PictureBookPro": "📚 故事绘本 (环节 40) — L5 重写 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "InteractiveDramaPro": "🎮 互动剧 (环节 41) — L5 重写 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "QualityAssurancePro": "✅ 质量 QA (环节 34) — L5 重写 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "AssetRegistry": "📦 资产注册表 [起点·纯 widget]",
    "SpatialLayout": "🗺️ GEO 空间布局 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "ActingSkill": "🎭 表演层专家 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "SoundSkill": "🔊 声音层专家 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "IterationPostPro": "🔁 迭代 + 后期 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "ThirtySecSixAct": "📜 30s 6 段 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "CinematicStudio": "🎬 电影工作室 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "DirectorSoulNode": "💀 导演灵魂 (60情感+10维度+7融合) [起点·纯 widget]",
    "ShotSelectionPro": "🎯 选片决策 (环节 30) — Phase 27 P0 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "AestheticJudgmentPro": "🎨 审美判断 (环节 7) — Phase 28 P0 [起点·纯 widget]",
    "VersionControlPro": "🔀 版本控制 (环节 35) — Phase 28 P1 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "StyleGuidePro": "🎨 风格指南 (环节 8) — Phase 28 P1 [起点·纯 widget]",
    "MarketAudiencePro": "📊 市场受众 (环节 36) — Phase 28 P1 [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "CleanupPassPro": "🧹 清理通道 (P2) [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "FormatOutputPro": "📐 格式化输出 (P2) [中间态·可接灵魂/审美/风格/经验/控制/节奏]",
    "ProjectArchivePro": "📦 项目归档 (P2) [终态·可接所有上游]",
    "H3ContextIRNode": "🎬 H3 Context IR (MiniMax-H3 框架转换 5 模式) [起点·纯 widget]",
    "UniversalDirectorPromptNode": "🎬 通用导演 Prompt (H3/Seedance/Wan/Sora/Veo/短剧 6 模型路由) [起点·纯 widget]",
    # Phase 36.6 v5: 导演能力总控节点 (1 节点 = 4 起点聚合)
    "DirectorMasteryNode": "🎬 导演能力总控 (灵魂+审美+风格+意图 4 合 1) [起点·纯 widget] — 拖 1 个节点 = 拖 4 个",
}
