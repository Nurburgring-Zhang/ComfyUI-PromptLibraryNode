# -*- coding: utf-8 -*-
"""
ComfyUI-PromptLibraryNode - 32 节点 L5 顶级导演级 + Hell Grind 6 层生产系统
================================================

Phase 9: 3 剧本拆分节点 (Architecture / Body / Storyboard)
Phase 11: 4 专业节点 (VerticalShortDrama / Hook / Dialogue / CharacterArc)
Phase 12: 4 附件核心节点 (DirectorIntent / ArtDirection / Spatial / Silence)
Phase 12 续 + 13: 14 生产环节节点 (Concept -> QA) + L5 深度重写
Phase 14: Hell Grind 6 层生产系统 (资产/空间/表演/声音/迭代/后期)
Phase 14 升级: 30s 6 段 + Cinematic Studio 电影效果 + 多模型路由
测试: 595/595 全过
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
from phase14_asset_registry import Phase14AssetRegistry
from phase14_spatial_layout import Phase14SpatialLayout
from phase14_acting_skill import Phase14ActingSkill
from phase14_sound_skill import Phase14SoundSkill
from phase14_iteration_post import IterationPostPro
from phase14_30s_six_act import Phase14_30sSixAct
from phase14_cinematic_studio import Phase14_CinematicStudio
from director_soul import DirectorSoulNode

NODE_CLASS_MAPPINGS = {
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
    "Phase14AssetRegistry": Phase14AssetRegistry,
    "Phase14SpatialLayout": Phase14SpatialLayout,
    "Phase14ActingSkill": Phase14ActingSkill,
    "Phase14SoundSkill": Phase14SoundSkill,
    "IterationPostPro": IterationPostPro,
    "Phase14_30sSixAct": Phase14_30sSixAct,
    "Phase14_CinematicStudio": Phase14_CinematicStudio,
    "DirectorSoulNode": DirectorSoulNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ScriptArchitecturePro": "📖 剧本架构 (1/3)",
    "ScriptBodyPro": "📜 剧本正文 (2/3)",
    "DirectorStoryboardPro": "🎬 导演分镜 (3/3)",
    "VerticalShortDramaPro": "📱 垂直短剧 (4/7)",
    "HookMasterPro": "🎣 钩子大师 (5/7)",
    "DialogueMasterPro": "💬 对白大师 (6/7)",
    "CharacterArcPro": "👤 角色弧光 (7/7)",
    "DirectorIntentPro": "🎯 导演意图 (附件核心)",
    "ArtDirectionPro": "🎨 美术指导 (附件核心)",
    "SpatialConsistencyPro": "📐 空间一致性 (附件核心)",
    "SilenceMasteryPro": "🤫 沉默大师 (附件核心)",
    "ConceptPitchPro": "💡 概念立项 (环节 1) — L5 重写",
    "WorldBuildingPro": "🌍 世界设定 (环节 3) — L5 重写",
    "ThemePhilosophyPro": "🧠 主题哲学 (环节 4) — L5 重写",
    "SoundDesignPro": "🔊 声音设计 (环节 13) — L5 重写",
    "MusicScorePro": "🎼 音乐配乐 (环节 14) — L5 重写",
    "PerformanceDirectionPro": "🎭 表演指导 (环节 17) — L5 重写",
    "CostumePropSetPro": "👘 服化道 (环节 19) — L5 重写",
    "EditingPro": "✂️ 剪辑 (环节 28) — L5 重写",
    "ColorGradingPro": "🎨 调色 (环节 32) — L5 重写",
    "VfxPro": "✨ VFX (环节 33) — L5 重写",
    "MvPro": "🎵 MV 导演 (环节 39) — L5 重写",
    "PictureBookPro": "📚 故事绘本 (环节 40) — L5 重写",
    "InteractiveDramaPro": "🎮 互动剧 (环节 41) — L5 重写",
    "QualityAssurancePro": "✅ 质量 QA (环节 34) — L5 重写",
    "Phase14AssetRegistry": "📦 资产注册表 (Phase 14)",
    "Phase14SpatialLayout": "🗺️ Phase 14 GEO 空间布局 (Higgsfield 体系)",
    "Phase14ActingSkill": "five_pillars / action_timing / emotion_to_action / living_human_rules / inner_monologue / full_acting_prompt",
    "Phase14SoundSkill": "🔊 Phase14 声音层专家 (Higgsfield AUDIO 块架构)",
    "IterationPostPro": "🔁 迭代 + 后期 (Phase 14) — Higgsfield 5 铁律",
    "Phase14_30sSixAct": "six_act_overview / act_1_establish / act_2_introduce / act_3_interact / act_4_conflict / act_5_climax / act_6_hook / h3_three_fields_prompt",
    "Phase14_CinematicStudio": "effects_23_overview / selected_model / model_weakness_avoidance / character_consistency_workflow / 11_stage_pipeline / 6_documents / h3_prompt",
    "DirectorSoulNode": "soul_injection / fused_emotion / emotion_dimensions / soul_dimensions / soul_state / director_signature / scene_prompt_addon / h3_alignment_addon",
}

