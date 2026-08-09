# Project: ComfyUI-StringConstructor

**URL:** https://github.com/Lex-DRL/ComfyUI-StringConstructor
**Author:** Lex-DRL
**License:** open source
**类别:** ComfyUI 提示词工程/工程师节点 (方向 4)

---

## 项目哲学

> "Simple is better than complex." — Zen of Python

String Constructor (Text-Formatting) nodes ... for ComfyUI.

**核心方法论:**
- Build your dictionary of available text chunks once.
- Pass it further as a single line (bus/pipe design).
- Easily reuse these sub-strings to build as many variations of a prompt as needed.
- It's especially handy for regional prompting (aka area composition).

**警告:** v3.x 起,所有字典构建节点已抽取到独立的 **🗂️ Dict Tools** 节点包。

---

## 核心节点

### 1. The Main Node - String Formatter
- 期望一个输入(完整"library" dictionary)
- 使用 Python 的 string formatting 语法 `{{key_name}}` 引用
- 单节点、单输入、单一文本字段

### 2. Helper Nodes for Dictionaries
- **Dict from Text** - 99% 场景够用,解析单段文本,按空行分割成块
  - 第一行 = key,其余行 = value
- **Add String to Dict** - 添加单个条目
- **Add ANY to Dict** - 添加任意类型 (float, int 等)
- **Extract String from Dict** - 提取单个元素
- **Validate Dict** - 验证所有 key 命名正确

### 3. Helper Nodes for Preview
- **Preview Dict** - 调试字典构建

---

## 字符串格式化语法

用 `{key_name}` 在大括号中引用(无空格):

```python
{
    "model_prefix": "score_9, score_8_up, score_7_up",
    "char1_short": "1boy, blond, short hair",
    "char1_long": "1boy, smiling, blue eyes, blond, short hair,[NEW LINE HERE] wearing a leather jacket, sitting on a bike"
}
```

**命名规则:** Python 变量命名限制 - 仅 ASCII 字母、数字、下划线;不能以数字开头。

✅ 有效: `valid_name`, `_other_valid_name_`, `YetAnother_ValidName___`, `name4`
❌ 无效: `wrong name with spaces`, `wrong-name.with:punctuation`, `4name`

---

## ⭐⭐⭐⭐⭐ 递归格式化 (Recursive Formatting) - 核心创新!

### 原理
格式化字符串时,允许 chunks 相互引用,解锁巨大可能性 - 比如构建**整个描述层次结构**(针对不同分辨率定制)或用于高级用户的**条件字符串格式化**。

### 负向提示词示例 (实际工作)
```
bad_quality(worst quality:1.2), (low quality:1.2), (normal quality:1.2), lowres
bad_anatomy_shortbad anatomy
bad_anatomy_extraugly, unnatural body, error
bad_anatomy_long{bad_anatomy_short}, {bad_anatomy_extra}
bad_hands_shortbad hands
bad_hands_extraextra finger, missing fingers
bad_hands_long{bad_hands_short}, {bad_anatomy_long}, {bad_hands_extra}
bad_eyes_shortimperfect eyes, skewed eyes
bad_face_short{bad_eyes_short}, unnatural face
bad_face_long{bad_face_short}, {bad_anatomy_long}
bad_limbs_shortextra limb, missing limbs
bad_human_long{bad_anatomy_short}, {bad_hands_short}, {bad_face_short}, {bad_anatomy_extra}, {bad_limbs_short}
watermarksignature, watermarks
neg_common{bad_quality}, {watermark}, {bad_human_long}
```

### ⚠️ 警告
循环引用会导致无限循环!节点在大约 1k 递归层后报错,所以是安全的。但仍然要注意。

---

## 高级话题

### 模式作为字典的一部分
通过递归格式化,可以把模板本身放进字典。甚至可以同时放正向/负向 prompt 在里面,然后在 KSampler 之前用 String Formatter 节点解包。

这个能力**彻底改变工作流构建方式**:
- 为特定 KSampler 构建 prompt 实际上是**免费的**(字典配置正确)
- string-formatting/text-encoding 几乎也是免费的
- 不再需要传递预编码 conditioning 的"意大利面条"
- 只需在字典中设置几个"开关"键,在工作流中只传递**单一字典**

### 大括号转义
- **Safe mode** ✨ v1.1.0 新增:遇到无法格式化的内容时,保留原样
- **手动转义** - 用 `{{` 和 `}}` 表示字面 `{` 和 `}`

### 动态模式 (条件格式化)
```
{{character_ }} - safe mode off
{character_ } - safe mode on
```
加上 `active_char` = "1" 的字符串,`character_1` 的值就会被注入!

这是**用数据(而非代码)表示整个逻辑树**!

---

## 实现细节 (程序员参考)

内部实现仅使用 Python 内置的 `str.format_map()` 与来自 Format-Dict 的 keyword 参数。任何"复杂"格式化模式都可用。

`Add ANY to Format-Dict` 节点就是为这个而存在。

---

## 与我们项目的关系

**类别: 强借鉴 (技术核心) + 互补 (格式化层)**

### ⭐⭐⭐⭐⭐ 递归格式化 / 模板继承 (核心借鉴!)

**这是 StringConstructor 最值得我们学习的设计!**

我们当前的问题:
- 我们的 `script_body_pro.py` 输出 25 段,每段重复大量公共元素(质量标签、负面词)
- 修改一个质量标签需要修改 25 处

**借鉴方案:**
```python
# 当前 (我们的做法)
shot_1_prompt = "masterpiece, best quality, 1girl, ..."  # 质量标签重复 25 次
shot_2_prompt = "masterpiece, best quality, 1girl, ..."  # 修改很痛苦

# 借鉴 StringConstructor 后的做法
quality_pos = "masterpiece, best quality"
character = "1girl, blue hair"
shot_1_prompt = "{quality_pos}, {character}, in a garden"  # 模板化
shot_2_prompt = "{quality_pos}, {character}, in a library"  # 一处修改全局生效
```

### ⭐⭐⭐⭐⭐ 字典/Bus 设计 (高借鉴!)

**借鉴方向:**
- 我们当前每个节点单独工作
- 应学习 **bus/pipe design**:
  - 创建 `story_dict` 一次性包含所有内容(角色/场景/导演/质量)
  - 在工作流中只传递这个 dict
  - 任意节点用 `{key}` 引用

### ⭐⭐⭐⭐ 条件格式化 (中借鉴)

**借鉴方向:**
- 我们的 `director_pro.py` 中导演风格"权重混搭":
  - `active_director = "1"` → 用 `徐克` 风格
  - `active_director = "2"` → 用 `黑泽明` 风格
  - 通过字典中的 `director_1`, `director_2` 切换

### 直接给我们的改进方向

1. **`pln_utils.py` 增加 FormatDict 机制**:
   - 创建 `StoryDict` 全局字典
   - 节点间传递单一字典而不是多个字段
   - 任意节点可访问 `{quality}`, `{director}`, `{character}` 等

2. **`script_body_pro.py` 重构**:
   - 把重复的 25 段质量标签抽到字典
   - 使用递归引用减少 70% 代码量
   - 修一处全 25 段生效

3. **`director_pro.py` 增强**:
   - 导演风格"权重混搭": `徐克 0.6 + 黑泽明 0.4`
   - 动态切换"主导演"

4. **新节点 `prompt_template_pro.py`**:
   - 完全照搬 StringConstructor 设计
   - 我们的"特色": 内置导演/类型片/质量库

### 互补关系
- StringConstructor = **底层格式化机制** (字典+递归)
- 我们 = **导演领域知识** (导演/类型片库)
- 完美组合: 我们的导演知识库 → StringConstructor 字典 → 25 段导演风格化分镜

