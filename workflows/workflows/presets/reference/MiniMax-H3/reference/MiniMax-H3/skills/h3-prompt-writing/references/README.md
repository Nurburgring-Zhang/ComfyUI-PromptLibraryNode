# PromptLibraryNode Pro + DirectorPromptPro

> **v3.1 - 灵魂节点 (Director Soul) 已上线** (2026-08-09)
> **26 节点接入灵魂 + 60 情感矩阵 + 28 真实电影灵感时刻 + 597 测试全过**

两个 ComfyUI 节点,帮你写提示词和生成故事板,内置世界顶级导演集群能力 + 导演灵魂注入系统。

---

## 🆕 v3.1 灵魂节点 (Phase 17)

### 灵魂节点 v1.0 (DirectorSoulNode)

| 模块 | 规模 |
|------|------|
| **60 情感矩阵** | Plutchik 24 + Izard 6 + 复合 8 + 状态 10 + 复杂 12 (含东方 4 + 矛盾 4 + 哲学 4) |
| **88 情感别名** | 8 基础 / 24 子词 / 60+ 中文,全自动 alias 解析 |
| **7 融合公式** | F1-F7 覆盖 70% 单情感 / 25% 双情感 / 5% 复杂场景 |
| **10 灵魂维度** | 创造力/想象力/艺术表达/镜头/氛围/精神/灵感/叛逆/怀疑/突破 |
| **灵魂状态** | 灵感/疲劳/怀疑/叛逆/精神状态,基于 scene_progress 动态计算 |
| **场景权重** | 5 大场景类型自动推断融合模式 |
| **灵感时刻** | 28 个真实电影引用,替代凭空编写的灵感时刻 |
| **8 输出字段** | 完整注入 + 融合档案 + 维度 + 状态 + 签名 + prompt 增强 + H3 对齐 |

### 8 大世界顶级导演 28 个真实灵感时刻 (Phase 17.7)

| 导演 | 真实电影引用数 | 代表作 |
|------|------|------|
| **王家卫** | 5 | 花样年华 / 重庆森林 / 春光乍泄 / 一代宗师 / 堕落天使 |
| **诺兰** | 5 | 盗梦空间 / 记忆碎片 / 黑暗骑士 / 星际穿越 / 信条 |
| **奉俊昊** | 3 | 寄生虫 / 母亲 / 雪国列车 |
| **黑泽明** | 3 | 七武士 / 罗生门 / 乱 |
| **是枝裕和** | 3 | 步履不停 / 小偷家族 / 无人知晓 |
| **塔可夫斯基** | 3 | 乡愁 / 镜子 / 潜行者 |
| **侯孝贤** | 3 | 刺客聂隐娘 / 悲情城市 / 海上花 |
| **大卫·芬奇** | 3 | 七宗罪 / 搏击俱乐部 / 社交网络 |

每条包含 8 字段: 导演/作品/场景/情感核心/镜头技术/技术原因/灵魂维度/Prompt 片段

### 26 节点接入灵魂 (Phase 17.5 + 17.6)

**Phase 17.5 4 核心** (深度接入):
- `concept_pitch_pro` / `director_intent_pro` / `editing_pro` / `art_direction_pro`

**Phase 17.6 21 _pro.py 节点** (批 1-6):
- 叙事/剧本 4: script_architecture / script_body / director_storyboard / vertical_short_drama
- 角色/对话 4: hook_master / dialogue_master / character_arc / spatial_consistency
- 主题/世界 4: silence_mastery / world_building / theme_philosophy / sound_design
- 表演/服装 4: music_score / performance_direction / costume_prop_set / color_grading
- 后期/特效 4: vfx_pro / mv_pro / picture_book / interactive_drama
- 质检 1: quality_assurance

每个节点统一接入:
- INPUT_TYPES 暴露 4 灵魂字段
- 调用 `director_soul.soul_inject_simple` 统一 wrapper
- 主输出头部加【灵魂核心 - XXX驱动】段
- 真实灵感时刻自动匹配 + 拼装

### 端到端真实剧本验证 (Phase 20)

3 个真实剧本片段 + 灵魂节点全流程完美工作:
- 《花样年华》走廊擦肩 (王家卫 / loneliness + longing) → 匹配 2 个真实电影
- 《盗梦空间》巴黎爆破 (诺兰 / fear + awe) → 匹配 2 个真实电影
- 《步履不停》长子忌日 (是枝裕和 / warm_regret + tenderness) → 匹配 2 个真实电影

---

## ✨ V4.0 世界级导演引擎 (2026-08 升级)

DirectorPromptPro 已升级为**知识库驱动的世界级导演集群引擎**:

| 模块 | 规模 |
|------|------|
| 导演风格库 | **63位** (IMDB Top 250全谱系 + 亚洲大师 + 新锐短剧/短视频导演) |
| 类型片视觉语言 | **22种** (含穿越/赛博朋克/武侠/心理/伪纪录/黑色/歌舞/生存/家庭/复仇) |
| 摄影语言 | 10景别 + 18运镜 + 镜头语言/景深/高级布光/视觉节奏 |
| 表演系统 | 9基础 + 23进阶微表情 + Laban + 角色原型 + 群体调度 |
| 叙事结构 | 12种 + 短剧微叙事 |

**核心能力:**
- **故事前文系统** — 每个分镜输出前携带前面故事大纲,确保镜头延续性与一致性
- **张弛有度节奏系统** — 识别蓄势/拐点/爆发/喘息/余韵,防连续高潮脱敏
- **按叙事功能推断表演情绪** — 不再用纯数值映射,冷开场→复仇前的平静,暗线→愧疚,识破→毁灭性领悟
- **导演+类型→叙事结构自动适配** — 徐克+神话→英雄之旅,Hitchcock+悬疑→悬疑揭秘
- **63位导演下拉可选**,涵盖黄金时代/艺术电影/新好莱坞/当代/亚洲/国际/短剧/新媒体

节点输入新增可选: 导演风格(63位)/叙事结构/短剧类型/目标受众,全部透传至引擎。

---

![PromptLibraryNode Pro 在 ComfyUI 中的界面](web/screenshot_workflow.png)

---

## 节点总览

| 节点 | 名称 | 输出端口 | 说明 |
|------|------|----------|------|
| **DirectorSoulNode** | 导演灵魂节点 (Phase 17) | 8 | 60 情感 + 7 融合 + 10 维度 + 28 真实灵感时刻 |
| PromptLibraryNodePro | 提示词库节点 Pro V20.5 | 5 | 多功能提示词工具 + 故事板生成 |
| DirectorPromptPro | 导演分镜批次输出 V1.0 | 2 | 逐镜头批次输出,每段总纲+单分镜 |

## 安装

1. 复制整个 `ComfyUI-PromptLibraryNode` 目录到 ComfyUI 的 `custom_nodes/` 下
2. 重启 ComfyUI, 节点出现在 `PromptLibrary/` 分类下

## 使用示例

```python
# 灵魂节点调用
from director_soul import soul_inject_simple

# 真实剧本片段
inj, fused, state, dims = soul_inject_simple(
    primary="loneliness",
    secondary=["longing"],
    scene_weight=0.7,
    director="王家卫",
    scene_context="走廊, 1962 年香港, 周慕云与苏丽珍深夜偶遇, 旗袍, 慢镜头, 老歌",
)
# inj 包含完整灵魂融合 + 灵魂状态 + 10 维度 + 真实灵感时刻 (花样年华走廊擦肩 + 重庆森林凤梨罐头)
```

```python
# 其他节点接入灵魂 (统一 pattern)
from director_soul import soul_inject_simple

def build_my_node(self, **kwargs):
    # ... 解析输入 ...
    inj, fused, soul_state, soul_dims = soul_inject_simple(
        primary=kwargs.get("灵魂_主导情感", "auto"),
        scene_weight=float(kwargs.get("灵魂_场景权重", 0.5)),
        director=kwargs.get("导演风格", ""),
        secondary=[...] if ... else None,
        fusion_mode=kwargs.get("灵魂_融合模式", "auto"),
        scene_context=scene,
    )
    # 拼装到主输出
    main_output = inj + "\n" + ...
    return (main_output, ...)
```

## 文档

- `PHASE_17_DEVELOPMENT_PLAN.md` - 灵魂节点开发计划
- `PHASE_17_DUAL_AI_AUDIT.md` - 灵魂节点双 AI 互审
- `PHASE_17_7_INSPIRATION_DB.md` - 28 真实灵感时刻详解
- `PHASE_19_DUAL_AI_AUDIT.md` - 综合双 AI 互审
- `RELEASE_NOTES_v3.1.md` - v3.1 Release Notes
- `RELEASE_NOTES_v3.0.md` - v3.0 Release Notes
- `AUDIT_REPORT.md` - 总审计报告
- `MASTER_PLAN.md` - 项目总体计划
- `INSTALL_GUIDE.md` - 安装指南

## 测试

597/597 测试通过 (test_full_audit 92 + test_e2e_full 200 + test_phase13_audit 305)

```bash
cd ComfyUI-PromptLibraryNode
python test_full_audit.py
python test_e2e_full.py
python test_phase13_audit.py
```

## 端到端真实剧本验证

```bash
python _e2e_validation.py
# 跑 3 个真实剧本片段 (花样年华/盗梦空间/步履不停) + 灵魂节点全流程
```

## 项目状态

- **节点总数**: 27 (1 灵魂节点 + 25 _pro.py 节点接入灵魂 + 1 director_prompt_pro)
- **测试基线**: 597/597 ✅
- **真实电影引用**: 28 个真实灵感时刻 (8 大导演)
- **情感覆盖**: 60 情感 + 88 别名
- **融合算法**: 7 公式 (F1-F7)
- **灵魂维度**: 10 维 (创造力/想象力/...)
- **Git commits**: 23 (Phase 17.5 + 17.6 批 1-6 + 17.7 + 19 + 20 + 21)

## ⚠️ 诚实承认的局限

1. 灵魂节点是"资深副导演水平", 不是"顶级导演水平" - 5 大根本差距
2. 75-80% 接近, 95%+ 需要 AI 真的有了"灵魂"
3. 节点接入深度不均 (editing 最深, 其他 21 节点是"附加灵魂段")
4. 测试通过 ≠ 质量顶级 (测试是功能性, 不是质量性)

## 下一步

- **Phase 18** 节点去模板化 - 给关键节点加"决策层" (多候选 + 动态选优)
- **Phase 22+** 灵感时刻持续加 (28 → 50+)
- **Phase 23** GitHub 推送
- **Phase 24** 端到端真实剧本测试扩展
- **Phase 25** 真实导演反馈收集

---

**发布日期**: 2026-08-09
**作者**: Mavis (主 agent) + 用户 (格林) 协作
**License**: 待定
