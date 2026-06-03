# ============================================================
# DirectorPromptPro — 逐分镜批次输出引擎
# ============================================================
# 核心能力：
#   1. 接收和PromptLibraryNodePro同样的参数
#   2. 但每次都只输出总纲 + 单个分镜
#   3. 按分镜数重复输出，形成批次
#   4. 每个分镜独立可用（带完整总纲）
# ============================================================
import os
import sys

# 确保节点目录在路径中
_node_dir = os.path.dirname(os.path.abspath(__file__))
if _node_dir not in sys.path:
    sys.path.insert(0, _node_dir)

from story_sense_data import STORY_SENSE_LIBRARY
from engine_story_arc import StoryArc, ShotConstraints, PromptSegmenter, CinematographyDirector
from pln_llm import call_ai
from pln_random import random_topic, random_character, random_env

from modes_storyboard import (
    _get_mode_name, _get_mode_style, _get_layout_desc,
)
from pln_utils import generate_negative_prompt
# [P2修复] 使用共享格式模板模块，消除与 modes_storyboard.py 之间约200行的重复代码
from format_templates import get_format_templates


# ============================================================
# 批处理入口 — 故事板模式（逐镜头输出）
# ============================================================
def process_storyboard_batched(mode, topic, character_desc, env_desc,
                                shot_count, style, color_tone, preferred_shot, camera_style,
                                api_url, api_key, model_name, temperature, max_tokens, ref_images,
                                pick_story_sense_fn):
    """
    逐镜头输出故事板。
    返回：PromptSegmenter.join_outputs(segments)
    每个segment = 总纲 + 第N个分镜内容
    """
    if not api_url or shot_count < 1:
        return ""
    
    # 获取故事弧
    sense_text = pick_story_sense_fn() if pick_story_sense_fn else ""
    story_arc = StoryArc(sense_text) if sense_text else None
    
    # 自动补全
    if not topic:
        topic = random_topic(mode)
    if not character_desc:
        character_desc = random_character(mode, topic)
    if not env_desc:
        env_desc = random_env(mode, topic)
    
    # 先构建一次总system prompt（不含故事感）
    mode_name = _get_mode_name(mode)
    mode_style = _get_mode_style(mode)
    layout_desc = _get_layout_desc(mode)
    
    # [P2修复] 使用共享格式模板，替代内联 _get_format_templates()
    fmt_templates = get_format_templates()
    format_section = fmt_templates.get(mode,
        "输出格式（标准故事板）\n每个镜头包含：景别+画面描述+运镜+转场+备注\n")
    
    # 构建总纲文本（共享）
    arc_text = sense_text if sense_text else ""
    header = (
        f"{mode}总纲\n"
        f"整体视觉风格：\n"
        f"风格为{style}，色彩基调偏向{color_tone}。\n"
        f"角色物品设定：\n"
        f"{(character_desc or '待定角色').replace(chr(10), ' ').rstrip()}\n"
        f"场景设定：\n"
        f"{(env_desc or '待定场景').rstrip()}\n"
    )
    
    segments = []
    constraints_tracker = ShotConstraints()
    
    for shot_idx in range(shot_count):
        # 计算当前镜头的故事弧信息
        arc_info = ""
        cinema_block = ""
        if story_arc:
            beat = story_arc.get_beat_for_shot(shot_idx, shot_count)
            # 用户的运镜偏好覆盖
            cam_text, cam_reason = CinematographyDirector.get_camera_directive(
                beat['intensity'], beat['pace'], camera_style or "")
            cinema = dict(beat.get('cinematography', {}))
            cinema['camera_movement'] = cam_text
            cinema['camera_reason'] = cam_reason
            # 估算预估总片长（用各镜头时长范围中点累加）
            est_total = 0.0
            for k in range(shot_count):
                kbeat = story_arc.get_beat_for_shot(k, shot_count)
                kdur = kbeat.get('cinematography', {}).get('duration_range', (3, 6))
                est_total += (kdur[0] + kdur[1]) / 2.0
            cinema_block = CinematographyDirector.build_block(
                cinema,
                cumulative_seconds=constraints_tracker.total_duration,
                total_estimated=est_total,
            )
            arc_info = (
                f"故事节拍：第{beat['beat_index']+1}/{beat['total_beats']}段 - {beat['beat_name']}\n"
                f"情绪目标：{beat['emotion_value']:.2f}（{', '.join(beat['emotion_tags'])}）\n"
                f"节奏：{beat['pace']} | 视觉强度：{beat['intensity']:.2f}\n"
                f"叙事功能：{beat['narrative_func']}\n"
                f"推荐景别：{'/'.join(beat['recommended_shot_types'])}\n"
            )
            if beat['is_final']:
                arc_info += "注意：这是结尾阶段的镜头，画面应具有收束感和余韵。\n"
        
        # 连续性约束
        constraint_text = constraints_tracker.get_constraints_text()
        
        # 构建system prompt
        sys_p = (
            f"{arc_text}\n"
            f"{arc_info}\n"
            f"你是一位世界顶级的{mode_name}导演兼分镜师。\n"
            f"当前输出：第{shot_idx+1}/{shot_count}个镜头\n\n"
            f"画面铁律（十二条红线）\n"
            f"1. 禁止抽象词：禁止「悲伤」「紧张」等情绪词，只用可见的描述来传递情绪。\n"
            f"2. 饱满叙事：每格3-6句话，充分描写场景氛围和角色动态，让画面生动丰满。\n"
            f"3. 镜头连续性：相邻镜头之间的角色位置、光线、道具必须一致。\n"
            f"4. 禁止参数：不能写焦距mm、色温K、分辨率dpi等数值参数。\n"
            f"5. 变化标注规则：仅在场景或角色有大的变化时，输出分镜场景或角色特征行。分镜场景：完整场景描述（地点、时间、光线、环境氛围，2-4句）。角色特征：仅在外貌/服装/状态有实质性变化时输出（换装/变脏/受伤/新增饰品等可见变化），描述变化了什么，2-3句。禁止写角色动作叙事（那是画面维度的事）。两者都变化时各一行。无变化时这两行不出现。其他字段正常输出。\n"
            f"6. 叙事功能仅在需要说明镜头作用时才输出，不是每个镜头都必须有。\n"
            f"7. 时空锚定：每格开头固定用「时间·空间」前缀（如「清晨·森林小屋厨房」「傍晚·湖边小码头」）。当时间或空间发生变化时，在先导句中明确标注「时间推进到…」或「场景切换到…」。\n"
            f"8. 180度不越轴：相邻镜头保持角色视线和站位方向一致（左侧机位/右侧机位锁定），禁止突然镜像翻转。\n"
            f"9. 单格凝固动作：每格只描述一个凝固的瞬间动作，禁止连续动作（如「跑向…然后跳起来」会导致画面鬼影）。\n"
            f"10. 场景切换时在首镜内增加场景描述和角色特征变化描述（换装/变脏等可见变化，无变化不写）。\n"
            f"11. 风格统一：所有镜头中角色外貌、服装、色彩基调必须保持严格一致（除非场景转换有明确交代）。每格开头重复主风格词。\n"
            f"12. 对话框绑定角色：多角色场景下，每个对话框必须明确指向该角色（如「指向[角色名]的对话框」「[角色名]头顶的气泡对话框」），禁止模糊的「有对话框」。旁白不加对话框。\n\n"
            f"{format_section}\n"
            f"{cinema_block}\n"
            f"{mode_style}\n"
            f"请直接输出第{shot_idx+1}个镜头的内容。只输出这一个镜头，不要输出其他镜头。\n"
            f"重要：输出中不要包含任何** - 等符号标记。直接输出纯文字。\n"
            f"当前需特别注意的连续性约束：\n{constraint_text}\n"
            f"场景/角色衔接提示：请确保本镜头与前一镜头的场景、角色位置、视线方向保持一致，\n"
            f"如有场景切换请明确标注「场景切换到…」，有角色变化请明确标注。\n"
        )
        
        # 构建user prompt
        user_prompt = (
            f"主题：{topic}\n"
            f"角色描述：{character_desc}\n"
            f"环境背景：{env_desc}\n"
            f"当前是第{shot_idx+1}个镜头，共{shot_count}个镜头。\n"
            f"风格：{style}\n"
            f"请只输出这第{shot_idx+1}个镜头的内容。\n"
        )
        
        # 调用LLM
        ai_result, err = call_ai(api_url, api_key, model_name, sys_p, user_prompt, temperature, max_tokens)
        
        # 组装完整输出：总纲 + 本镜头
        shot_output = (
            f"{header}\n"
            f"【镜头{shot_idx+1}/{shot_count}】\n"
            f"{ai_result}\n" if ai_result else f"{header}\n【镜头{shot_idx+1}/{shot_count}】\n（AI调用失败）\n"
        )
        
        # 解析约束数据（如果有）
        if ai_result:
            shot_data = _parse_shot_data(ai_result)
            constraints_tracker.record_shot(shot_data)
        
        segments.append(shot_output)
    
    return PromptSegmenter.join_outputs(segments)


def _parse_shot_data(raw_text):
    """从LLM输出中提取结构化镜头数据用于约束跟踪"""
    data = {}
    for line in raw_text.split('\n'):
        line = line.strip()
        if line.startswith('景别：'):
            data['shot_type'] = line.replace('景别：', '').strip()
        elif line.startswith('分镜场景：'):
            data['scene'] = line.replace('分镜场景：', '').strip()
        elif line.startswith('角色特征：'):
            data['characters'] = line.replace('角色特征：', '').strip()
        elif line.startswith('运镜：'):
            data['camera'] = line.replace('运镜：', '').strip()
        elif line.startswith('转场：'):
            data['transition'] = line.replace('转场：', '').strip()
        elif line.startswith('时长：'):
            try:
                dur_str = line.replace('时长：', '').strip().replace('秒', '').strip()
                data['duration'] = float(dur_str)
            except ValueError:
                pass
    return data


# ============================================================
# 绘本模式批处理 — 逐页输出
# ============================================================
def process_picture_book_batched(topic, character_desc, env_desc, pages,
                                  style, color_tone, text_amount, age_group,
                                  api_url, api_key, model_name, temperature, max_tokens, ref_images,
                                  pick_story_sense_fn):
    if not api_url or pages < 1:
        return ""

    sense_text = pick_story_sense_fn() if pick_story_sense_fn else ""
    story_arc = StoryArc(sense_text) if sense_text else None

    if not topic:
        topic = random_topic("绘本模式")
    if not character_desc:
        character_desc = random_character("绘本模式", topic)
    if not env_desc:
        env_desc = random_env("绘本模式", topic)

    # 年龄段指南
    age_guide = {
        "0-3岁低幼": "适合0-3岁婴儿/幼儿的绘本：每页画面简单，主体突出，色彩鲜明对比强，线条简洁圆润。文字极短（每页5-15字），句式重复，节奏感强。主题为日常生活认知。",
        "3-6岁幼儿": "适合3-6岁幼儿园儿童：画面丰富但有清晰视觉焦点，色彩温暖明亮。文字每页20-40字，故事有简单情节结构。角色形象可爱，表情丰富。",
        "6-9岁学龄": "适合6-9岁小学生：画面细节丰富，有多层景深和复杂构图。文字每页30-60字，故事有完整起承转合。主题涉及勇气/成长/科学/历史等。",
        "9-12岁少年": "适合9-12岁少年的插画书/图像小说：画面更写实或更具艺术风格，文字每页50-100字，故事可以有多条线索和深层寓意。",
    }
    age_text = age_guide.get(age_group, age_guide["3-6岁幼儿"])

    header = (
        f"绘本总纲\n"
        f"整体视觉风格：\n风格偏向{style}，整体色调为{color_tone}，适合{age_group}年龄段。\n"
        f"角色物品设定：\n{(character_desc or '待定角色').rstrip()}\n"
        f"场景设定：\n{env_desc or '待定场景'}\n"
        f"核心叙事设定：\n共{pages}页，文字量{text_amount}。故事结构完整。\n"
    )

    segments = []
    for page in range(pages):
        # 绘本影视语言指导：静态画面 → 阅读视线/构图节奏/翻页转场
        cinema_block = ""
        if story_arc:
            beat = story_arc.get_beat_for_shot(page, pages)
            cinema = beat.get('cinematography', {})
            dur = cinema.get('duration_range', (5, 8))
            cinema_block = (
                f"【大师级绘本视觉指导】\n"
                f"▸ 推荐阅读时长：{dur[0]}-{dur[1]}秒（亲子朗读节奏参考）\n"
                f"▸ 视线引导：{cinema.get('camera_movement', '居中构图')}（"
                f"将运镜方式转译为静态构图：固定=对称居中｜推=主体放大｜跟=视线引导路径｜手持=活泼跳跃感）\n"
                f"▸ 翻页转场：{cinema.get('transition', '硬切')}（"
                f"绘本翻页对应电影转场：硬切=干脆翻页｜叠化=半透明叠印｜淡入=留白引入｜淡出=黑场收束）\n"
                f"▸ 情绪曲线：当前节拍「{beat['beat_name']}」情绪值 {beat['emotion_value']:.2f}，"
                f"配合色彩温度（暖={beat['emotion_value']:.0%}*暖，冷=反向）。\n"
            )
        sys_p = (
            f"{sense_text}\n"
            f"你是一位世界顶级的儿童绘本作家兼插画师。\n"
            f"当前输出：第{page+1}/{pages}页\n\n"
            f"输出格式\n以'【第N页】'开头，每页包含以下7个维度：\n\n"
            f"1. 时间·空间锚定\n"
            f"2. 画面描述：用孩子的眼睛看世界，2-4句\n"
            f"3. 分镜场景：有场景变化时输出，无变化不出现\n"
            f"4. 角色特征：仅在变化时输出，禁止写角色动作叙事\n"
            f"5. 文案：绘本正文文字，适合亲子朗读\n"
            f"6. 视觉连续性提示\n"
            f"7. 构图与景别说明\n"
            f"8. 阅读时长：X秒（按上方推荐范围给出，便于亲子朗读）\n"
            f"9. 翻页转场：（按上方推荐转场名）\n\n"
            f"创作原则：不说教公式、五感锚定法、情绪始终正向\n"
            f"年龄段适配：{age_text}\n"
            f"{cinema_block}\n"
            f"请直接输出第{page+1}页的内容。只输出这一页。\n"
            f"重要：输出中不要包含任何符号标记。直接输出纯文字。\n"
        )
        user_prompt = (
            f"故事主题：{topic or '童话森林探险'}\n"
            f"角色描述：{character_desc}\n"
            f"环境背景：{env_desc}\n"
            f"当前是第{page+1}页，共{pages}页。\n"
            f"风格：{style}，色调：{color_tone}\n"
            f"请只输出这第{page+1}页的内容。\n"
        )

        ai_result, err = call_ai(api_url, api_key, model_name, sys_p, user_prompt, temperature, max_tokens)

        page_output = (
            f"{header}\n"
            f"【第{page+1}/{pages}页】\n"
            f"{ai_result}\n" if ai_result else f"{header}\n【第{page+1}/{pages}页】\n（AI调用失败）\n"
        )
        segments.append(page_output)

    return PromptSegmenter.join_outputs(segments)


# ============================================================
# 短剧模式批处理 — 逐镜头输出
# ============================================================
def process_short_drama_batched(topic, character_desc, env_desc, shot_count,
                                 style, rhythm, camera_style, color_tone,
                                 api_url, api_key, model_name, temperature, max_tokens, ref_images,
                                 pick_story_sense_fn):
    if not api_url or shot_count < 1:
        return ""

    sense_text = pick_story_sense_fn() if pick_story_sense_fn else ""
    story_arc = StoryArc(sense_text) if sense_text else None

    if not topic:
        topic = random_topic("短剧模式")
    if not character_desc:
        character_desc = random_character("短剧模式", topic)
    if not env_desc:
        env_desc = random_env("短剧模式", topic)

    header = (
        f"短剧总纲\n"
        f"整体视觉风格：风格为{style}，节奏{rhythm}，色彩调性偏向{color_tone}。竖屏9:16垂直构图。\n"
        f"角色物品设定：\n{(character_desc or '待定角色').rstrip()}\n"
        f"场景设定：\n{env_desc or '待定场景'}\n"
    )

    segments = []
    constraints_tracker = ShotConstraints()
    for shot in range(shot_count):
        # 短剧影视语言指导（竖屏快节奏专用）
        cinema_block = ""
        if story_arc:
            beat = story_arc.get_beat_for_shot(shot, shot_count)
            # 竖屏专用：将常规运镜偏好替换为竖屏运镜
            user_pref = camera_style or ""
            if "竖屏" not in user_pref:
                user_pref = f"竖屏{user_pref}" if user_pref else ""
            cam_text, cam_reason = CinematographyDirector.get_camera_directive(
                beat['intensity'], beat['pace'], user_pref)
            cinema = dict(beat.get('cinematography', {}))
            cinema['camera_movement'] = cam_text
            cinema['camera_reason'] = cam_reason + "（竖屏构图：纵向运动优于横向）"
            # 短剧节奏强调更短：每个时长上限-1秒
            dur = cinema.get('duration_range', (1, 3))
            cinema['duration_range'] = (max(1, dur[0] - 1), max(2, dur[1] - 1))
            cinema['duration_hint'] = f"{cinema['duration_range'][0]}-{cinema['duration_range'][1]}秒"
            est_total = sum(
                (story_arc.get_beat_for_shot(k, shot_count).get('cinematography', {}).get('duration_range', (1, 3))[0]
                 + story_arc.get_beat_for_shot(k, shot_count).get('cinematography', {}).get('duration_range', (1, 3))[1]) / 2.0
                for k in range(shot_count)
            )
            cinema_block = CinematographyDirector.build_block(
                cinema,
                cumulative_seconds=constraints_tracker.total_duration,
                total_estimated=est_total,
            )
        sys_p = (
            f"{sense_text}\n"
            f"你是一位世界顶级的AI短剧导演兼分镜编剧。\n"
            f"当前输出：第{shot+1}/{shot_count}个镜头\n\n"
            f"画面铁律\n"
            f"1. 禁止抽象词，只用可见描述\n"
            f"2. 竖屏视觉：9:16比例\n"
            f"3. 时空锚定：每镜开头固定时间·空间前缀\n"
            f"4. 180度不越轴\n"
            f"5. 单镜凝固动作，禁止连续动作\n"
            f"6. 风格统一：角色外貌、服装、色彩基调所有镜头严格一致\n"
            f"7. 对话框绑定角色\n\n"
            f"输出格式\n以镜头N：标题开头。\n"
            f"脚本正文后输出：景别、台词、运镜（按上方推荐）、转场（按上方推荐）、时长：X秒（按上方推荐范围）、备注\n"
            f"{cinema_block}\n"
            f"当前需特别注意的连续性约束：\n{constraints_tracker.get_constraints_text()}\n"
            f"请直接输出第{shot+1}个镜头的内容。只输出这一个镜头。\n"
            f"重要：输出中不要包含任何符号标记。直接输出纯文字。\n"
        )
        user_prompt = (
            f"故事主题：{topic or '穿越时空的爱恋'}\n"
            f"角色描述：{character_desc}\n"
            f"环境背景：{env_desc}\n"
            f"当前是第{shot+1}个镜头，共{shot_count}个镜头。\n"
            f"风格：{style}，节奏：{rhythm}\n"
            f"请只输出这第{shot+1}个镜头的内容。\n"
        )

        ai_result, err = call_ai(api_url, api_key, model_name, sys_p, user_prompt, temperature, max_tokens)

        shot_output = (
            f"{header}\n"
            f"【镜头{shot+1}/{shot_count}】\n"
            f"{ai_result}\n" if ai_result else f"{header}\n【镜头{shot+1}/{shot_count}】\n（AI调用失败）\n"
        )
        # 解析约束数据
        if ai_result:
            shot_data = _parse_shot_data(ai_result)
            constraints_tracker.record_shot(shot_data)
        segments.append(shot_output)

    return PromptSegmenter.join_outputs(segments)


# ============================================================
# 儿童内容模式批处理（4种） — 逐片段/逐页输出
# ============================================================
def process_child_batched(mode, topic, character_desc, env_desc, count,
                           age_group, art_style,
                           api_url, api_key, model_name, temperature, max_tokens, ref_images,
                           pick_story_sense_fn):
    if not api_url or count < 1:
        return ""

    sense_text = pick_story_sense_fn() if pick_story_sense_fn else ""
    story_arc = StoryArc(sense_text) if sense_text else None

    if not topic:
        topic = random_topic(mode)
    if not character_desc:
        character_desc = random_character(mode, topic)
    if not env_desc:
        env_desc = random_env(mode, topic)

    # 年龄段描述
    age_desc = {
        "0-3岁低幼": "画面简单主体突出，色彩鲜明对比强，线条简洁圆润。文字极短（每页5-15字），句式重复有节奏感。",
        "3-6岁幼儿": "画面丰富有清晰视觉焦点，色彩温暖明亮。文字每段10-30字，故事有简单情节。角色形象可爱。",
        "6-9岁学龄": "画面细节丰富，文字每段20-50字，故事有完整起承转合。可涉及勇气/成长/科学等主题。",
    }
    age_text = age_desc.get(age_group, age_desc["3-6岁幼儿"])

    style_map = {
        "水彩插画": "水彩晕染风格，色彩柔和通透，边缘自然过渡",
        "卡通动画": "明亮卡通风格，粗轮廓线，纯色填充，表情夸张可爱",
        "彩铅手绘": "彩色铅笔手绘质感，线条有铅笔纹理",
        "黏土定格": "黏土定格动画风格，立体感强",
        "扁平矢量": "扁平矢量插画风格，简洁几何形状",
    }
    style_text = style_map.get(art_style, style_map["卡通动画"])

    header = (
        f"{mode}总纲\n"
        f"整体视觉风格：画风采用{art_style}，适合{age_group}年龄段。色彩鲜明活泼。\n"
        f"角色物品设定：\n{(character_desc or '待定角色').rstrip()}\n"
        f"场景设定：\n{env_desc or '待定场景'}\n"
    )

    # 模式专用格式描述
    format_desc = {
        "儿童视频格式一": """输出格式
每个片段按以下顺序输出：
1. 时间·空间锚定
2. 场景描述：用孩子的语言，2-3句
3. 动态描述【动态】：动效和运动方式
4. 分镜场景：有变化时输出
5. 角色特征：有变化时输出
6. 旁白/对话：多角色时标注角色名
7. 特效/TIPS：可选""",
        "儿童视频格式二": """输出结构
严格按四幕叙事结构：第一幕起 / 第二幕承 / 第三幕转 / 第四幕合
每个片段输出维度：场景、画面描述、旁白、对话、TIPS""",
        "儿童微动视频/GIF": """输出格式
每页严格按以下维度输出：
核心动作、画面、动效（标注循环方式）""",
        "儿童绘本格式": """输出格式
每页严格按以下维度输出：
画面、文案、旁白/对话、视觉连续性提示、构图与景别""",
    }
    fmt = format_desc.get(mode, "请按标准格式输出")

    segments = []
    for idx in range(count):
        unit_name = "片段" if mode != "儿童绘本格式" else "页"
        # 儿童内容影视语言指导
        cinema_block = ""
        if story_arc:
            beat = story_arc.get_beat_for_shot(idx, count)
            cinema = beat.get('cinematography', {})
            dur = cinema.get('duration_range', (3, 6))
            # 儿童内容情绪保持正向：将低情绪强度转译为温暖运镜
            cam_movement = cinema.get('camera_movement', '固定机位')
            if mode == "儿童微动视频/GIF":
                cinema_block = (
                    f"【大师级儿童动效指导】\n"
                    f"▸ 推荐循环时长：{dur[0]}-{dur[1]}秒（动效循环节奏）\n"
                    f"▸ 视觉运动：{cam_movement}（动效幅度比常规大1.5倍，富有童趣）\n"
                    f"▸ 循环方式：无缝循环 / 来回摆动 / 单次播放（按内容选择）\n"
                    f"▸ 情绪节拍：「{beat['beat_name']}」({beat['narrative_func']})\n"
                )
            elif mode == "儿童绘本格式":
                cinema_block = (
                    f"【大师级儿童绘本视觉指导】\n"
                    f"▸ 推荐阅读时长：{dur[0]}-{dur[1]}秒（亲子朗读参考）\n"
                    f"▸ 视线引导：{cam_movement}（静态构图：固定=对称居中｜推=放大主体｜跟=视线路径）\n"
                    f"▸ 翻页转场：{cinema.get('transition', '硬切')}\n"
                    f"▸ 情绪温度：「{beat['beat_name']}」({beat['narrative_func']})，色彩温暖明亮\n"
                )
            else:  # 儿童视频格式一/二
                cinema_block = (
                    f"【大师级儿童视频影视指导】\n"
                    f"▸ 推荐时长：{dur[0]}-{dur[1]}秒（适合儿童注意力跨度）\n"
                    f"▸ 推荐运镜：{cam_movement}（运动幅度比常规大1.5倍，节奏活泼）\n"
                    f"▸ 推荐转场：{cinema.get('transition', '硬切')}（避免突兀转场惊吓低龄观众）\n"
                    f"▸ 情绪节拍：「{beat['beat_name']}」({beat['narrative_func']})，整体保持正向温暖\n"
                )
        sys_p = (
            f"{sense_text}\n"
            f"你是一位世界顶级的儿童动画编剧兼分镜师。\n"
            f"当前输出：第{idx+1}/{count}个{unit_name}\n\n"
            f"{fmt}\n\n"
            f"创作原则\n- 不说教公式\n- 角色一致性锚定\n- 变化必须可见\n- 八大红线：不越轴、不跳时间、不连续动作、透视正确、风格统一、不抽象词、绑定对话框、时空锚定\n"
            f"- 情绪始终正向\n\n"
            f"年龄段适配：{age_text}\n"
            f"画面风格：{style_text}\n"
            f"{cinema_block}\n"
            f"请直接输出第{idx+1}个{unit_name}的内容。只输出这一个{unit_name}。\n"
            f"重要：输出中不要包含任何符号标记。直接输出纯文字。\n"
        )
        user_prompt = (
            f"故事主题：{topic or '小动物的冒险'}\n"
            f"角色描述：{character_desc}\n"
            f"环境背景：{env_desc}\n"
            f"当前是第{idx+1}个{unit_name}，共{count}个。\n"
            f"请只输出这一个。\n"
        )

        ai_result, err = call_ai(api_url, api_key, model_name, sys_p, user_prompt, temperature, max_tokens)

        unit_output = (
            f"{header}\n"
            f"【{unit_name}{idx+1}/{count}】\n"
            f"{ai_result}\n" if ai_result else f"{header}\n【{unit_name}{idx+1}/{count}】\n（AI调用失败）\n"
        )
        segments.append(unit_output)

    return PromptSegmenter.join_outputs(segments)


# ============================================================
# 专业设计模式批处理（8种） — 逐张/逐组输出
# ============================================================
def process_design_batched(mode, topic, character_desc, env_desc, count,
                            style, color_tone, product_material, product_color,
                            shoot_angle, lighting_scheme, bg_type,
                            api_url, api_key, model_name, temperature, max_tokens, ref_images,
                            pick_story_sense_fn):
    if not api_url or count < 1:
        return ""

    # 设计模式：使用故事弧驱动情绪节拍，但仅作为视觉氛围参考
    sense_text = pick_story_sense_fn() if pick_story_sense_fn else ""
    story_arc = StoryArc(sense_text) if sense_text else None

    if not topic:
        topic = random_topic(mode)
    if not character_desc:
        character_desc = random_character(mode, topic)
    if not env_desc:
        env_desc = random_env(mode, topic)

    # [P0修复] 从 modes_design 延迟导入各设计模式的 prompt 构建函数
    # 使用 try/except 守卫，避免模块不存在时崩溃
    try:
        from modes_design import (
            _build_ecommerce_prompt, _build_poster_prompt, _build_brand_prompt,
            _build_ppt_prompt, _build_logic_diagram_prompt, _build_three_view_prompt,
            _build_exploded_view_prompt, _build_pipeline_diagram_prompt,
        )
    except ImportError:
        return f"[提示] 设计模式「{mode}」需要安装 modes_design 模块才能使用。"

    builder_map = {
        "电商套图": _build_ecommerce_prompt,
        "海报设计": _build_poster_prompt,
        "品牌设计": _build_brand_prompt,
        "PPT设计": _build_ppt_prompt,
        "逻辑关系图设计": _build_logic_diagram_prompt,
        "三视图设计": _build_three_view_prompt,
        "爆炸拆解图设计": _build_exploded_view_prompt,
        "流水线图设计": _build_pipeline_diagram_prompt,
    }

    builder = builder_map.get(mode)
    if not builder:
        return ""

    # 先构建一次系统提示词
    sys_p = builder(topic, character_desc, env_desc, count, style, color_tone,
                    product_material, product_color, shoot_angle, lighting_scheme, bg_type, [])

    segments = []
    for idx in range(count):
        # 设计模式视觉指导：将情绪节拍转译为视觉节奏/视线引导
        cinema_block = ""
        if story_arc:
            beat = story_arc.get_beat_for_shot(idx, count)
            cinema = beat.get('cinematography', {})
            cinema_block = (
                f"【大师级视觉节奏指导】\n"
                f"▸ 视觉强度等级：{beat['intensity']:.2f}（"
                f"低=极简留白｜中=平衡构图｜高=视觉冲击/对角线动势）\n"
                f"▸ 视线引导：{cinema.get('camera_movement', '居中构图')}（"
                f"静态设计的视线路径：固定=对称稳定｜推=主体放大居中｜跟=Z字形/F字形动线｜手持=活泼跳跃）\n"
                f"▸ 情绪氛围：「{beat['beat_name']}」({beat['narrative_func']}) "
                f"→ 色温/对比度/留白比例配合调整\n"
                f"▸ 张力分布：当前节拍位于故事 {beat['story_progress']:.0%}，"
                f"对应设计中的视觉张力（开场=克制铺陈｜中段=信息密度｜高潮=主角核心放大｜收尾=空灵收束）\n"
            )
        user_prompt = (
            f"设计主题：{topic or '未指定'}\n"
            f"角色/主体描述：{character_desc}\n" if character_desc else ""
            f"环境/场景：{env_desc}\n" if env_desc else ""
            f"当前是第{idx+1}张/组，共{count}张/组。\n"
            f"{cinema_block}\n"
            f"请只输出第{idx+1}张/组的设计内容。不要包含其他张的内容。\n"
        )

        ai_result, err = call_ai(api_url, api_key, model_name, sys_p, user_prompt, temperature, max_tokens)

        unit_output = (
            f"{mode}总纲\n"
            f"设计主题：{topic or '未指定'}\n"
            f"风格：{style} | 色彩：{color_tone}\n\n"
            f"【设计{idx+1}/{count}】\n"
            f"{ai_result}\n" if ai_result else f"【设计{idx+1}/{count}】\n（AI调用失败）\n"
        )
        segments.append(unit_output)

    return PromptSegmenter.join_outputs(segments)
