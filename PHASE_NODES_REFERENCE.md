# Phase 14 节点代码 - 必须留根说明

**重要**: 这 10 个 `phase14_*.py` 文件**必须留在根目录**，不能移入子目录。

## 原因

`__init__.py` 第 51-57 行直接 `from phase14_xxx import ...` 顶级导入：

```python
from phase14_asset_registry import Phase14AssetRegistry        # 51
from phase14_spatial_layout import Phase14SpatialLayout         # 52
from phase14_acting_skill import Phase14ActingSkill             # 53
from phase14_sound_skill import Phase14SoundSkill               # 54
from phase14_iteration_post import IterationPostPro             # 55
from phase14_30s_six_act import Phase14_30sSixAct                # 56
from phase14_cinematic_studio import Phase14_CinematicStudio    # 57
```

ComfyUI 节点加载时执行 `__init__.py`，期望这些模块在 Python 路径（根目录）下。

## 10 个 phase14_*.py 全部被 import (跨文件验证)

| 文件 | 被谁 import | 关键 import 行 |
|------|-------------|----------------|
| `phase14_asset_registry.py` | `__init__.py` (L51) | `from phase14_asset_registry import Phase14AssetRegistry` |
| `phase14_spatial_layout.py` | `__init__.py` (L52) | `from phase14_spatial_layout import Phase14SpatialLayout` |
| `phase14_acting_skill.py` | `__init__.py` (L53) | `from phase14_acting_skill import Phase14ActingSkill` |
| `phase14_sound_skill.py` | `__init__.py` (L54) | `from phase14_sound_skill import Phase14SoundSkill` |
| `phase14_iteration_post.py` | `__init__.py` (L55) | `from phase14_iteration_post import IterationPostPro` |
| `phase14_30s_six_act.py` | `__init__.py` (L56) + `phase14_30s_six_act.py:39` | `from phase14_six_documents import ASSET_REGISTRY` + `from phase14_style_prefix import STYLE_PREFIX` |
| `phase14_cinematic_studio.py` | `__init__.py` (L57) + `phase14_cinematic_studio.py:32-33` | 同上 |
| `phase14_master_orchestrator.py` | character_arc/concept_pitch/director_storyboard/theme_philosophy (4 个) | `from phase14_master_orchestrator import (...)` |
| `phase14_six_documents.py` | phase14_30s_six_act / phase14_cinematic_studio / phase14_master_orchestrator (3 个) | `from phase14_six_documents import ASSET_REGISTRY` |
| `phase14_style_prefix.py` | character_arc/concept_pitch/director_storyboard/phase14_30s_six_act/phase14_cinematic_studio/phase14_master_orchestrator/theme_philosophy (7 个) | `from phase14_style_prefix import STYLE_PREFIX, FIFTEEN_BLOCKS` |

## 后果

如果移到子目录:
1. `__init__.py` 找不到模块 → 43 节点加载失败
2. 内部 cross-import 失败 → ComfyUI 启动 crash
3. 所有 851+118 = 969 个测试失败

## 解决方案

**保持现状** (推荐) - 这 10 个 phase14_*.py 留在根目录 + `__init__.py` 直接顶级导入。

**或者** (如要目录化):
- 改 `__init__.py` 用 `sys.path.insert(0, ...)` + 改所有 import 为相对路径
- 工作量大且风险高，不推荐

## Phase 36.4 文件整理结论

- ✅ 7 个 PHASE_*.md 报告归档到 `docs/phase-reports/`
- ✅ 10 个 phase14_*.py 全部留根（必需）
- ✅ 根目录现在干净：只 5 个必要 Python + 1 个 README.md + 1 个 PHASE_NODES_REFERENCE.md
