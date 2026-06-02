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
from engine_story_arc import StoryArc, ShotConstraints, PromptSegmenter
from pln_llm import call_ai
from pln_random import random_topic, random_character, random_env

from modes_storyboard import (
    _get_mode_name, _get_mode_style, _get_layout_desc,
)
from pln_utils import generate_negative_prompt


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
    
    # 读取格式模板
    format_templates = _get_format_templates()
    format_section = format_templates.get(mode,
        "输出格式（标准故事板）\n每个镜头包含：景别+画面描述+运镜+转场+备注\n")
    
    # 构建总纲文本（共享）
    arc_text = sense_text if sense_text else ""
    header = (
        f"{mode}总纲\n"
        f"整体视觉风格：\n"
        f"风格为{style}，色彩基调偏向{color_tone}。\n"
        f"角色物品设定：\n"
        f"{(character_desc or '待定角色').replace(chr(10), chr(10)).rstrip()}\n"
        f"场景设定：\n"
        f"{(env_desc or '待定场景').rstrip()}\n"
    )
    
    segments = []
    constraints_tracker = ShotConstraints()
    
    for shot_idx in range(shot_count):
        # 计算当前镜头的故事弧信息
        arc_info = ""
        if story_arc:
            beat = story_arc.get_beat_for_shot(shot_idx, shot_count)
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


def _get_format_templates():
    """返回所有格式模板（与modes_storyboard严格同步）"""
    return {
        "电影分镜": (
            "输出格式（电影分镜专用）\n"
            "每个镜头严格按以下格式输出：\n\n"
            "【Shot N】\n"
            "景别：极远景/全景/中景/近景/特写/极特写（始终输出）\n"
            "分镜场景：有场景变化时输出完整场景描述（地点、时间、光线、环境氛围，2-4句）。无变化时不出现\n"
            "角色特征：仅在角色外貌/服装/状态有实质性变化时输出（换装/变脏/受伤/新增饰品等可见变化）。禁止写角色在做什么（那是画面维度的事）。无变化时此行整行不出现。\n"
            "画面：围绕这三层展开——①角色在做什么（具体动作）②场景里发生了什么能推动剧情的事③光线和色彩在说什么情绪。3-6句，像给小说写段落，让读者眼睛里有画面。\n"
            "运镜：固定/推/拉/摇/移/跟/升降/手持 + 速度 + 角度\n"
            "转场：硬切/叠化/淡入淡出/划像/匹配剪辑\n"
            "时长：X秒\n"
            "叙事功能：必要时才输出。\n\n"
            "电影分镜创作原则\n"
            "- 节奏变化：交替使用远景/中景/近景/特写，避免连续3个同景别\n"
            "- 180度法则：保持角色视线的方向连续性\n"
            "- 情绪弧线：每个情节节拍对应视觉色温变化（暖=安全/冷=危机）\n"
        ),
        "广告故事板": (
            "输出格式（广告故事板专用）\n"
            "每个镜头按以下格式输出：\n\n"
            "【Shot N】\n"
            "分镜场景：有场景变化时输出完整场景描述（地点、时间、光线、环境氛围，2-4句）。无变化时不出现\n"
            "角色特征：仅在角色外貌/服装/状态有实质性变化时输出（换装/变脏/受伤/新增饰品等可见变化）。禁止写角色在做什么（那是画面维度的事）。无变化时此行整行不出现。\n"
            "画面：产品在场景里是怎样的存在——它在被使用、被注视还是被环境烘托？周围的人和物跟它是什么关系？光线是突出它的质感还是它的情绪？2-4句。\n"
            "卖点传达：这个镜头在传递什么信息——是功能卖点、情感诉求还是品牌态度\n"
            "拍摄方式：产品机位+镜头焦距+运动方式\n"
            "品牌元素：LOGO在哪出现、品牌色怎么用、Slogan什么时候出现\n"
            "时长：X秒 | 节奏提示：快切还是留白\n\n"
            "广告故事板创作原则\n"
            "- 每个镜头必须服务于品牌信息的传递，不能游离于核心卖点之外\n"
            "- 前3秒抓住注意力，中间展示卖点，最后3秒强化品牌记忆\n"
            "- 产品在画面中的比例：开场全景(20%)→中景展示(40%)→特写质感(60%)\n"
        ),
        "动画故事板": (
            "输出格式（动画故事板专用）\n"
            "每个镜头按以下格式输出：\n\n"
            "【Shot N】\n"
            "分镜场景：有场景变化时输出完整场景描述（地点、时间、光线、环境氛围，2-4句）。无变化时不出现\n"
            "角色特征：仅在角色外貌/服装/状态有实质性变化时输出（换装/变脏/受伤/新增饰品等可见变化）。禁止写角色在做什么（那是画面维度的事）。无变化时此行整行不出现。\n"
            "画面描述：角色在做什么、表情是什么样、场景里发生了什么——但要记住这是动画，动作幅度比现实大，表情比现实夸张，物体可以有违反物理规律的变形。3-5句。\n"
            "关键帧：动作起/中/止三帧的关键姿态描述\n"
            "表情/动作：该镜头角色需要表现的核心情绪和肢体语言\n"
            "特效提示：粒子/烟雾/魔法/变形等动画特效的时机和方式\n"
            "时长：X秒（动画通常12-24帧/秒）\n\n"
            "动画故事板创作原则\n"
            "- 动作幅度比实拍电影大1.5-2倍，表情更夸张\n"
            "- 关键帧之间必须包含中间帧的动作提示（物理解算/变形路线）\n"
            "- 色彩和形状跟随情绪变化（快乐=鲜亮暖色/悲伤=冷暗模糊）\n"
        ),
        "漫画分镜": (
            "输出格式（漫画分镜专用）\n"
            "按页面布局输出，每个页面包含3-4格：\n\n"
            "【第X页】\n"
            "页面布局: [2×2格/3×1横条/1大格+3小格等]\n"
            "---\n"
            "格1\n"
            "分镜场景：有场景变化时输出完整场景描述（地点、时间、光线、环境氛围，2-4句）。无变化时不出现\n"
            "角色特征：仅在角色外貌/服装/状态有实质性变化时输出（换装/变脏/受伤/新增饰品等可见变化）。禁止写角色在做什么（那是画面维度的事）。无变化时此行整行不出现。\n"
            "画面描述：位置、角色在做什么、透视角度、这格在整个页面里扮演什么角色（定场/推进/高潮/收尾）\n"
            "对话框位置：左上/右中/下方——注意阅读顺序，不要让对话框挡住重要画面\n"
            "文本内容：要有对话的节奏感，短句为主\n"
            "拟声词提示：什么声音、多大、什么字体风格\n"
            "格2\n"
            "...\n\n"
            "漫画分镜创作原则\n"
            "- 阅读顺序：从左到右+从上到下（日式从右到左需标注）\n"
            "- 大格用于情绪高潮/场景全景/关键动作，小格用于对话/细节\n"
            "- 拟声词要用文字写出来（如'砰！''哗啦—'）并标注字体大小\n"
        ),
        "MV故事板": (
            "输出格式（MV故事板专用）\n"
            "每个镜头按以下格式输出：\n\n"
            "【Shot N】\n"
            "歌词段落：对应的歌词文本\n"
            "画面：歌词说了一件事，但画面可以讲另一层故事——或者画面对位歌词、或者反差、或者延展歌词的意境。2-4句。\n"
            "音乐配合：这镜头卡在哪个音乐节点上——前奏、主歌进鼓、副歌爆发、桥段转调？乐器/节奏变化怎么跟画面切换咬合。\n"
            "色彩调性：这镜头的主色调，以及它跟前一个镜头的色彩怎么过渡（硬切/渐变色/补色跳转）\n"
            "剪辑点：XX秒对应歌曲XX歌词/旋律节点\n\n"
            "MV故事板创作原则\n"
            "- 主歌部分：以叙事/角色状态为主，镜头节奏舒缓\n"
            "- 副歌/高潮部分：画面冲击力最大化，快速剪辑+特效\n"
            "- 歌词可视化：避免字面翻译歌词，而是将歌曲的情绪视觉化\n"
        ),
        "教程步骤": (
            "输出格式（教程步骤专用）\n"
            "按步骤编号顺序输出：\n\n"
            "【步骤X】\n"
            "标题：本步骤的核心操作名称\n"
            "画面：动手之前是什么状态，动手之后变成什么样。手部动作+界面变化+工具使用，2-3句。重点在'操作前vs操作后'的对比。\n"
            "操作说明：具体干什么——点击哪里、输入什么、拖拽到什么位置。越具体越好。\n"
            "重点提示：这里容易错在什么地方，搞错了怎么补救。\n"
            "完成状态：这步做完后应该看到什么效果\n\n"
            "教程步骤创作原则\n"
            "- 每步只教一个操作，步骤之间逻辑递进\n"
            "- 画面用箭头/标注/放大镜效果指示操作位置\n"
            "- 总步骤数不超过10步，超过则分组（第1部分/第2部分）\n"
        ),
        "短视频分镜": (
            "输出格式（短视频分镜专用）\n"
            "竖屏9:16，每个镜头1-3秒。每个镜头输出：\n\n"
            "【镜头N】\n"
            "画面：角色在做什么、画面里有什么吸引眼球的东西、这个镜头在1-3秒内怎么抓住人不让划走。1-2句。\n"
            "字幕/文本：画面叠加的文字——不超过8个字，要一眼看完\n"
            "音效/配乐：用BGM情绪带动画面——节奏点、音效、人声什么时候进\n"
            "转场：滑入/缩放/闪切/无缝转场\n"
            "心理时间：这个镜头在观众感觉里是快还是慢——快=激动/兴奋，慢=沉浸/情绪\n\n"
            "短视频分镜创作原则\n"
            "- 前3秒必须制造钩子（反直觉画面/问题提问/视觉冲击）\n"
            "- 每5-7秒一个信息点，每15秒一个转折/悬念\n"
            "- 竖屏构图：主体占据画面中上60%，底部留字幕空间\n"
            "- 画面文字：不超过10字/屏，大字号+高对比色\n"
        ),
        "品牌故事板": (
            "输出格式（品牌故事板专用）\n"
            "每个镜头按以下格式输出：\n\n"
            "【Shot N】\n"
            "画面：场景+角色+品牌元素怎么自然融入画面——不是生硬摆LOGO，而是让品牌成为场景的一部分。2-4句。\n"
            "品牌VI体现：这镜头里品牌色出现在哪里？LOGO以什么方式被看到？\n"
            "情感调性：这个镜头想让观众感受到什么——信任/活力/优雅/创新/安心\n"
            "文案参考：配合这个镜头的旁白或字幕大概写什么方向\n"
            "时长：X秒 | 节奏：舒缓还是紧凑\n\n"
            "品牌故事板创作原则\n"
            "- 品牌色占画面比例：主色60%+辅色30%+强调色10%\n"
            "- LOGO只在品牌记忆点出现（开场定调/高潮情感/结尾收束）\n"
            "- 品牌人格化：镜头语言本身反映品牌调性（高端=稳重镜头/活力=运动镜头）\n"
        ),
        "剧情分镜": (
            "输出格式（剧情分镜专用）\n"
            "以剧本式格式输出，每个镜头包含：\n\n"
            "【场景N】\n"
            "内/外景-地点-时间\n"
            "画面描述：角色在做什么、周围的环境是什么样的、空气中是什么氛围——3-6句，像在跟读者讲'你站在这场景里会看到什么、感觉到什么'。\n"
            "角色情绪：这镜头里角色处在什么状态——紧张/松弛/期待/疲惫，不写'他很难过'，写'他盯着窗外不说话，手指在桌沿反复摩挲'\n"
            "戏剧冲突：这镜头里矛盾在哪——两个人目标不同？信息不对称？情绪错位？还是外部压力在逼近？\n"
            "镜头语言：景别+机位+运动方式——镜头本身也在讲故事\n"
            "对白/独白：写出对话，每句话要么推进剧情要么揭示性格\n\n"
            "剧情分镜创作原则\n"
            "- 三幕结构：第一幕建立角色关系，第二幕冲突升级，第三幕高潮解决\n"
            "- 冲突密度递增：前30%大冲突间隔5分钟，后30%间隔1分钟\n"
            "- 每个镜头揭示一条新信息或推动情节发展，不能有冗余镜头\n"
            "- 对白精简：每句话要么推进剧情，要么揭示角色性格\n"
        ),
    }
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
            f"7. 构图与景别说明\n\n"
            f"创作原则：不说教公式、五感锚定法、情绪始终正向\n"
            f"年龄段适配：{age_text}\n"
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
    for shot in range(shot_count):
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
            f"脚本正文后输出：景别、台词、运镜、备注\n"
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
        sys_p = (
            f"{sense_text}\n"
            f"你是一位世界顶级的儿童动画编剧兼分镜师。\n"
            f"当前输出：第{idx+1}/{count}个{unit_name}\n\n"
            f"{fmt}\n\n"
            f"创作原则\n- 不说教公式\n- 角色一致性锚定\n- 变化必须可见\n- 八大红线：不越轴、不跳时间、不连续动作、透视正确、风格统一、不抽象词、绑定对话框、时空锚定\n"
            f"- 情绪始终正向\n\n"
            f"年龄段适配：{age_text}\n"
            f"画面风格：{style_text}\n"
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

    if not topic:
        topic = random_topic(mode)
    if not character_desc:
        character_desc = random_character(mode, topic)
    if not env_desc:
        env_desc = random_env(mode, topic)

    # 从modes_design导入各设计模式的prompt构建
    from modes_design import (
        _build_ecommerce_prompt, _build_poster_prompt, _build_brand_prompt,
        _build_ppt_prompt, _build_logic_diagram_prompt, _build_three_view_prompt,
        _build_exploded_view_prompt, _build_pipeline_diagram_prompt,
    )

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

    # 先构建系统提示词
    sys_p = builder(topic, character_desc, env_desc, count, style, color_tone,
                    product_material, product_color, shoot_angle, lighting_scheme, bg_type, [])

    segments = []
    for idx in range(count):
        user_prompt = (
            f"设计主题：{topic or '未指定'}\n"
            f"角色/主体描述：{character_desc}\n" if character_desc else ""
            f"环境/场景：{env_desc}\n" if env_desc else ""
            f"当前是第{idx+1}张/组，共{count}张/组。\n"
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
