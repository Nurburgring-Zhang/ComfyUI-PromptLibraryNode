# 工作流模板总览 (Workflows Overview)

> **v3.1 - 2026-08-09**
> **3 个端到端工作流模板 JSON**
> **所有模板都注入灵魂 (Phase 17)**

---

## 工作流模板清单

| # | 文件 | 节点数 | 场景 | 导演 | 灵魂情感 |
|---|---|---|---|---|---|
| 1 | `WORKFLOW_END_TO_END.json` | 9 | 父女在厨房, 雨夜, 1998 年哈尔滨 | 王家卫 | loneliness + longing F3 |
| 2 | `WORKFLOW_SHORT_DRAMA.json` | 6 | 女主被陷害入狱, 30 分钟短剧 | 诺兰 | fear + anger F5 矛盾 |
| 3 | `WORKFLOW_MV.json` | 5 | MV: 男孩雨夜寻找已逝爱人, 240 秒 | 王家卫 | longing + tenderness F2 |

---

## 1. WORKFLOW_END_TO_END.json (9 节点 - 完整电影流水线)

**场景**: 父女在厨房, 雨夜, 1998 年哈尔滨
**导演**: 王家卫
**灵魂**: loneliness + longing, F3 50/50 融合, intensity 0.7

**节点链路**:
```
DirectorSoulNode (灵魂)
    ↓
ScriptArchitecturePro → ScriptBodyPro → DirectorStoryboardPro (Phase 9 剧本三件套)
    ↓
ConceptPitchPro → ArtDirectionPro → EditingPro (L5 导演级)
    ↓
DirectorIntentPro → QualityAssurancePro (附件 + 质检)
```

**真实灵感时刻匹配** (Phase 17.7):
- 王家卫 / 花样年华 / 走廊擦肩
- 王家卫 / 重庆森林 / 凤梨罐头
- 王家卫 / 春光乍泄 / 瀑布缺席

**适合**: 完整电影 / 剧集前期开发, 9 节点全流程

---

## 2. WORKFLOW_SHORT_DRAMA.json (6 节点 - 短剧流水线)

**场景**: 女主被陷害入狱, 越狱反击, 30 分钟
**导演**: 诺兰
**灵魂**: fear + anger, F5 矛盾情感爆炸, intensity 0.85

**节点链路**:
```
DirectorSoulNode (灵魂)
    ↓
VerticalShortDramaPro → HookMasterPro → DialogueMasterPro (短剧核心 3 件)
    ↓
CharacterArcPro → EditingPro (角色弧光 + 剪辑)
```

**真实灵感时刻匹配** (Phase 17.7):
- 诺兰 / 盗梦空间 / 巴黎爆破
- 诺兰 / 记忆碎片 / 黑白彩色
- 诺兰 / 黑暗骑士 / 小丑递笔

**适合**: 竖屏短剧 / ReelShort / 抖音 / 30 分钟剧集, 节奏感强

---

## 3. WORKFLOW_MV.json (5 节点 - MV 流水线)

**场景**: MV: 男孩在雨夜城市里寻找已逝的爱人, 240 秒
**导演**: 王家卫
**灵魂**: longing + tenderness, F2 70/30 主次融合, intensity 0.7

**节点链路**:
```
DirectorSoulNode (灵魂)
    ↓
MvPro → MusicScorePro → SoundDesignPro (MV 导演 + 音乐 + 声音)
    ↓
EditingPro (剪辑)
```

**真实灵感时刻匹配** (Phase 17.7):
- 王家卫 / 花样年华 / 走廊擦肩
- 王家卫 / 一代宗师 / 火车站月台
- 王家卫 / 堕落天使 / 深夜火锅

**适合**: MV 拍摄, 240 秒 = 4 分钟, 完整音乐 + 声音 + 剪辑

---

## 怎么用

### 在 ComfyUI 中加载

1. 启动 ComfyUI
2. **File → Load** → 选择 `WORKFLOW_*.json` 之一
3. 工作流自动加载到画布
4. 检查所有节点的输入字段 (有些可能有 `*` 警告表示可优化)
5. **Queue Prompt** (Ctrl+Enter) 执行

### 自定义场景

修改节点的输入字段:
- `场景描述` - 改成你的故事
- `导演风格` - 选你喜欢的导演
- 4 灵魂字段 - 调整情感 + 强度

### 串联 3 个工作流

如果想做"短剧 → 剪辑 → MV"的混合:
- 用 `WORKFLOW_SHORT_DRAMA.json` 做前 6 节点
- 加载 `WORKFLOW_MV.json` 
- 把 `WORKFLOW_SHORT_DRAMA` 的 DialogueMasterPro 输出接到 `WORKFLOW_MV` 的 MvPro 输入
- 整体作为一条管线

---

## 自定义工作流

要创建自己的流水线:
1. 右键 → Add Node → PromptLibrary
2. 拖出节点
3. 把一个节点的输出端口 (右边) 拉到另一个节点的输入端口 (左边)
4. 调整输入参数
5. File → Save (保存到 `workflows/` 目录)

**最少必连**: 每个节点连入 `DirectorSoulNode` (单独放一个灵魂节点作为"种子")

---

## 节点调用顺序建议

| 任务类型 | 建议流水线 |
|---|---|
| **电影 / 剧集** | ScriptArchitecturePro → ScriptBodyPro → DirectorStoryboardPro → ConceptPitchPro → ArtDirectionPro → EditingPro |
| **短剧** | VerticalShortDramaPro → HookMasterPro → DialogueMasterPro → CharacterArcPro → EditingPro |
| **MV** | MvPro → MusicScorePro → SoundDesignPro → EditingPro |
| **故事绘本** | PictureBookPro → EditingPro |
| **互动剧** | InteractiveDramaPro → EditingPro |
| **纪录片** | ScriptBodyPro → ConceptPitchPro → EditingPro |
| **VFX 重头戏** | VfxPro → ConceptPitchPro → EditingPro |

---

## 真实剧本测试 (Phase 20 验证)

3 个工作流都用真实电影场景做验证, 597 测试 + 端到端真不同:

| 真实电影 | 场景 | 验证工作流 |
|---|---|---|
| 《花样年华》走廊擦肩 | 父女, 王家卫, loneliness+longing | `WORKFLOW_END_TO_END.json` |
| 《盗梦空间》巴黎爆破 | 梦中, 诺兰, fear+awe | `WORKFLOW_SHORT_DRAMA.json` (情感相近) |
| 《步履不停》长子忌日 | 家庭, 是枝裕和, warm_regret+tenderness | 自定义 (用 END_TO_END 改导演) |

---

**发布日期**: 2026-08-09
**3 个工作流模板**: 端到端 / 短剧 / MV
**灵魂节点统一接入**: 所有工作流从 `DirectorSoulNode` 开始
**GitHub 仓库**: 待推送 (需要仓库地址)
