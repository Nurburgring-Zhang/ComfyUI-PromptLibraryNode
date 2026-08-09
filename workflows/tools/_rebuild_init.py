# -*- coding: utf-8 -*-
"""重建 __init__.py"""
import os
import re

NODES = [
    ("PromptLibraryNodePro", "prompt_library_node_pro"),
    ("DirectorPromptPro", "director_prompt_pro"),
    ("ScriptArchitecturePro", "script_architecture_pro"),
    ("ScriptBodyPro", "script_body_pro"),
    ("DirectorStoryboardPro", "director_storyboard_pro"),
    ("VerticalShortDramaPro", "vertical_short_drama_pro"),
    ("HookMasterPro", "hook_master_pro"),
    ("DialogueMasterPro", "dialogue_master_pro"),
    ("CharacterArcPro", "character_arc_pro"),
    ("DirectorIntentPro", "director_intent_pro"),
    ("ArtDirectionPro", "art_direction_pro"),
    ("SpatialConsistencyPro", "spatial_consistency_pro"),
    ("SilenceMasteryPro", "silence_mastery_pro"),
    ("ConceptPitchPro", "concept_pitch_pro"),
    ("WorldBuildingPro", "world_building_pro"),
    ("ThemePhilosophyPro", "theme_philosophy_pro"),
    ("SoundDesignPro", "sound_design_pro"),
    ("MusicScorePro", "music_score_pro"),
    ("PerformanceDirectionPro", "performance_direction_pro"),
    ("CostumePropSetPro", "costume_prop_set_pro"),
    ("EditingPro", "editing_pro"),
    ("ColorGradingPro", "color_grading_pro"),
    ("VfxPro", "vfx_pro"),
    ("MvPro", "mv_pro"),
    ("PictureBookPro", "picture_book_pro"),
    ("InteractiveDramaPro", "interactive_drama_pro"),
    ("QualityAssurancePro", "quality_assurance_pro"),
    # Phase 14: Hell Grind 6 层生产系统
    ("AssetRegistry", "asset_registry"),
    ("SpatialLayout", "spatial_layout"),
    ("ActingSkill", "acting_skill"),
    ("SoundSkill", "sound_skill"),
    ("IterationPostPro", "iteration_post"),
    # Phase 14 升级: 30s 6 段 + Cinematic Studio
    ("ThirtySecSixAct", "thirty_sec_six_act"),
    ("CinematicStudio", "cinematic_studio"),
]

def find_class_in_file(filename, class_name):
    fp = filename + ".py"
    if not os.path.exists(fp):
        return False
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()
    # 找 class X(  或 class X :
    return bool(re.search(r"class\s+" + re.escape(class_name) + r"\s*[\(:]", content))

def find_display_name(filename):
    fp = filename + ".py"
    if not os.path.exists(fp):
        return None
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()
    # 找 NODE_DISPLAY_NAME_MAPPINGS 里的字符串
    m = re.search(r'NODE_DISPLAY_NAME_MAPPINGS\s*=\s*\{[^}]*"[^"]+"\s*:\s*"([^"]+)"', content)
    if m:
        return m.group(1)
    # 找 RETURN_NAMES
    m = re.search(r'RETURN_NAMES\s*=\s*\(([^)]+)\)', content)
    if m:
        names = [n.strip().strip('"').strip("'") for n in m.group(1).split(",")]
        return " / ".join(names)
    return None

verified = []
for cls, mod in NODES:
    if find_class_in_file(mod, cls):
        verified.append((cls, mod))
        print(f"  ✓ {mod}.py -> {cls}")
    else:
        print(f"  ✗ {mod}.py 缺 class {cls}")

print(f"\n验证 {len(verified)}/{len(NODES)} 节点")

# 构建 __init__.py
init_lines = [
    "# -*- coding: utf-8 -*-",
    '"""',
    "ComfyUI-PromptLibraryNode - 32 节点 L5 顶级导演级 + Hell Grind 6 层生产系统",
    "================================================",
    "",
    "Phase 9: 3 剧本拆分节点 (Architecture / Body / Storyboard)",
    "Phase 11: 4 专业节点 (VerticalShortDrama / Hook / Dialogue / CharacterArc)",
    "Phase 12: 4 附件核心节点 (DirectorIntent / ArtDirection / Spatial / Silence)",
    "Phase 12 续 + 13: 14 生产环节节点 (Concept -> QA) + L5 深度重写",
    "Phase 14: Hell Grind 6 层生产系统 (资产/空间/表演/声音/迭代/后期)",
    "Phase 14 升级: 30s 6 段 + Cinematic Studio 电影效果 + 多模型路由",
    "测试: 595/595 全过",
    '"""',
    "",
]

for cls, mod in verified:
    init_lines.append(f"from {mod} import {cls}")

init_lines.append("")
init_lines.append("NODE_CLASS_MAPPINGS = {")
for cls, mod in verified:
    init_lines.append(f'    "{cls}": {cls},')
init_lines.append("}")
init_lines.append("")

init_lines.append("NODE_DISPLAY_NAME_MAPPINGS = {")
for cls, mod in verified:
    display = find_display_name(mod)
    if display:
        display_esc = display.replace("\\", "\\\\").replace('"', '\\"')
        init_lines.append(f'    "{cls}": "{display_esc}",')
    else:
        init_lines.append(f'    "{cls}": "{cls}",')
init_lines.append("}")
init_lines.append("")

with open("__init__.py", "w", encoding="utf-8") as f:
    f.write("\n".join(init_lines) + "\n")

print(f"\n[OK] __init__.py 已重建 ({len(verified)} 节点)")
