# WORKFLOW_PRESETS/ - 节点预设库

> **v3.1 - 2026-08-09**
> **节点字段预设, 可复制粘贴到 ComfyUI**
> **5 个真实剧本场景预设 (Phase 27 准备扩展到 10+)**

---

## 怎么用

### 方法 1: 手动复制粘贴 (目前方式)

1. 打开 JSON 文件 (e.g. `01_父女厨房_王家卫_雨夜.json`)
2. 在 ComfyUI 中添加节点 (e.g. `ScriptArchitecturePro`)
3. 双击节点 → 在右侧参数面板, 按 JSON 中的 `node_settings.ScriptArchitecturePro` 字段填入

### 方法 2: 直接复制 JSON 到剪贴板

- 每个 JSON 都有 `node_settings.<节点名>` 块
- 复制对应块的字段值, 粘贴到 ComfyUI 节点输入

### 方法 3: 编程加载 (Phase 28 实现)

```python
import json
from pathlib import Path

preset = json.loads(Path("WORKFLOW_PRESETS/01_xxx.json").read_text())
# 假设节点 Python 类有 widget_values 注入
node = ScriptArchitecturePro()
output = node.build_architecture(**preset["node_settings"]["ScriptArchitecturePro"])
```

---

## 5 个预设清单

| 文件 | 场景 | 导演 | 灵魂 | 风格 |
|---|---|---|---|---|
| `01_父女厨房_王家卫_雨夜.json` | 父女在厨房, 雨夜, 1998 哈尔滨 | 王家卫 | loneliness+longing F3 | 慢镜头, 留白, 旗袍 |
| `02_女主入狱_诺兰_短剧.json` | 女主被陷害入狱, 30 分钟 | 诺兰 | fear+anger F5 矛盾 | 节奏感, 强冲突 |
| `03_雨夜MV_王家卫_慢歌.json` | 男孩雨夜寻已逝爱人, 240 秒 | 王家卫 | longing+tenderness F2 | 慢歌, 4 分钟 |
| `04_父子重逢_侯孝贤_沉默.json` | 父子十年后重逢, 饭桌 | 侯孝贤 | warm_regret+chou 静 | 沉默, 长镜 |
| `05_巴士顶端_奉俊昊_母亲.json` | 母亲在巴士顶为弱智儿子跳舞 | 奉俊昊 | tenderness+despair F3 | 远景, 静止 |

---

## 预设覆盖 9 节点 (按工作流)

每个预设覆盖 9 节点:
1. DirectorSoulNode
2. ScriptArchitecturePro
3. ScriptBodyPro
4. DirectorStoryboardPro
5. ConceptPitchPro
6. ArtDirectionPro
7. EditingPro
8. DirectorIntentPro
9. QualityAssurancePro

**完整 9 节点流水线** (按 WORKFLOW_END_TO_END.json 顺序)

---

## 用户可以编辑任何字段

**所有字段都是"参考值"**, 用户可改任何:
- 场景描述 (改你想做的故事)
- 导演风格 (改你喜欢的导演)
- 4 灵魂字段 (改情感/强度/次要/融合模式)
- 所有其他字段 (焦段/光圈/光影/...)

---

## 5 个预设详解

### 01. 父女厨房_王家卫_雨夜
- **场景**: 父女在厨房, 雨夜, 1998 年哈尔滨
- **真实灵感时刻匹配**: 花样年华走廊擦肩 + 重庆森林凤梨罐头 + 春光乍泄瀑布缺席
- **灵魂状态**: inspiration 0.93 / fatigue 0.53 / doubt 0.38 / rebel 0.75 / mental lucid
- **导演节奏签名**: 王家卫起手 13.4s (最慢), BPM 56-70, 慢镜头, 留白

### 02. 女主入狱_诺兰_短剧
- **场景**: 女主被陷害入狱, 越狱反击, 30 分钟
- **真实灵感时刻匹配**: 盗梦空间巴黎爆破 + 记忆碎片黑白彩色 + 黑暗骑士小丑递笔
- **灵魂状态**: inspiration 0.93 / fatigue 0.53 / doubt 0.23 / rebel 0.88 / mental lucid
- **导演节奏签名**: 诺兰起手 10.4s (短), BPM 98-130 (疾驰), 时间结构

### 03. 雨夜MV_王家卫_慢歌
- **场景**: MV: 男孩在雨夜城市里寻找已逝的爱人, 240 秒
- **真实灵感时刻匹配**: 花样年华走廊 + 一代宗师火车站 + 堕落天使火锅
- **灵魂状态**: longing 0.7 主 + tenderness 0.3 次
- **导演节奏签名**: 王家卫 慢歌, 60s BPM

### 04. 父子重逢_侯孝贤_沉默
- **场景**: 父子十年后重逢, 饭桌 (具体场景: 父亲 60 岁, 儿子 30 岁, 父亲因病去世前最后聚餐)
- **真实灵感时刻匹配**: 刺客聂隐娘山中静坐 + 悲情城市林家客厅 + 海上花室内长镜
- **灵魂状态**: warm_regret + chou (中式愁绪)
- **导演节奏签名**: 侯孝贤长镜, 固定, 自然光

### 05. 巴士顶端_奉俊昊_母亲
- **场景**: 母亲站在巴士顶为弱智儿子跳舞 (2009 奉俊昊《母亲》)
- **真实灵感时刻匹配**: 寄生虫暴雨倒流 + 母亲巴士顶 + 雪国列车车厢
- **灵魂状态**: tenderness + despair
- **导演节奏签名**: 奉俊昊 静止, 远景, 突然音乐

---

## 怎么扩展 (Phase 28+)

可以加 5-10 个新预设:
- 06_黑帮_科波拉_教父.json (3 小时)
- 07_战争_诺兰_敦刻尔克.json (90 分钟)
- 08_东方奇幻_侯孝贤_刺客.json (武侠)
- 09_太空_维伦纽瓦_降临.json (科幻)
- 10_动画_宫崎骏_龙猫.json (动画)

每个预设都是真实电影 + 真实导演 + 真实灵感时刻, 帮用户"快速开始"

---

**发布日期**: 2026-08-09
**5 个预设** (Phase 27 准备扩展)
**33 节点全覆盖** (8 能力 57% 实现, 42 环节 80% 覆盖)
**零虚假容忍**: 已诚实标注 75% 接近, 不是 100% 世界顶级
