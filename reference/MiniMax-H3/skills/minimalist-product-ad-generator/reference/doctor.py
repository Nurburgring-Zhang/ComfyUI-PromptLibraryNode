# -*- coding: utf-8 -*-
"""
ComfyUI-PromptLibraryNode 自检脚本
==================================

当节点不显示 / 模式不工作 / 数据不生效时,运行此脚本:
    python doctor.py

诊断 5 大类问题:
    1. 安装路径 (custom_nodes 目录结构)
    2. Python 环境 (依赖、版本、编码)
    3. 模块导入 (各子模块是否正常)
    4. 节点注册 (NODE_CLASS_MAPPINGS 是否齐全)
    5. 知识库完整性 (数据是否齐全)
    6. API 可达性 (如果填了 API 地址)
"""
import os
import sys
import json
import traceback
from datetime import datetime

# Windows console 编码修复
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 颜色输出 (Windows 10+ ANSI 支持)
class C:
    GRN = "\033[92m"   # 绿
    RED = "\033[91m"   # 红
    YEL = "\033[93m"   # 黄
    CYN = "\033[96m"   # 青
    DIM = "\033[90m"   # 灰
    RST = "\033[0m"    # 重置
    BLD = "\033[1m"    # 加粗

def ok(msg):  return f"  {C.GRN}✓{C.RST} {msg}"
def bad(msg): return f"  {C.RED}✗{C.RST} {msg}"
def warn(msg):return f"  {C.YEL}!{C.RST} {msg}"
def info(msg):return f"  {C.DIM}·{C.RST} {msg}"
def head(t):  return f"\n{C.BLD}{C.CYN}== {t} =={C.RST}"

# ---------- 1. 安装路径 ----------
def check_install_path():
    print(head("1. 安装路径检查"))
    issues = []
    here = os.path.dirname(os.path.abspath(__file__))
    print(info(f"脚本所在: {here}"))
    print(info(f"上级目录: {os.path.dirname(here)}"))
    
    # 检查 __init__.py 存在
    init = os.path.join(here, "__init__.py")
    if not os.path.exists(init):
        issues.append(("FATAL", f"__init__.py 不存在!当前目录不是有效 ComfyUI 节点"))
        return issues
    
    print(ok(f"__init__.py 存在 ({os.path.getsize(init)} 字节)"))
    
    # 检查是否是 custom_nodes 的直接子目录
    parent = os.path.basename(here)
    grandparent = os.path.basename(os.path.dirname(here))
    
    if "custom_nodes" in os.path.dirname(here).lower():
        if os.path.dirname(here).lower().endswith("custom_nodes"):
            print(ok(f"位于 custom_nodes 直接子目录 (正确)"))
        else:
            print(warn(f"位于 {grandparent} 的子目录,可能多套了一层"))
            issues.append(("WARN", f"建议把 {parent} 目录直接放到 custom_nodes/ 下"))
    else:
        issues.append(("FATAL", f"不在 custom_nodes 目录树中!必须放在 ComfyUI/custom_nodes/{parent}/"))
    
    # 必备文件
    required_files = ["__init__.py", "pyproject.toml", "pln_utils.py", "pln_llm.py", "director_engine.py"]
    for f in required_files:
        p = os.path.join(here, f)
        if os.path.exists(p):
            print(ok(f"必需文件存在: {f}"))
        else:
            print(bad(f"必需文件缺失: {f}"))
            issues.append(("FATAL", f"缺少 {f},压缩包可能不完整"))
    
    return issues

# ---------- 2. Python 环境 ----------
def check_python_env():
    print(head("2. Python 环境检查"))
    issues = []
    
    # 版本
    v = sys.version_info
    if v >= (3, 9):
        print(ok(f"Python {v.major}.{v.minor}.{v.micro} (>=3.9)"))
    else:
        print(bad(f"Python {v.major}.{v.minor} (<3.9,可能不兼容)"))
        issues.append(("FATAL", "需要 Python 3.9+"))
    
    # 编码
    enc = sys.getdefaultencoding()
    if enc.lower() in ("utf-8", "utf8"):
        print(ok(f"默认编码 UTF-8"))
    else:
        print(warn(f"默认编码 {enc} (建议 UTF-8)"))
    
    # 关键依赖
    deps = {
        "torch": "PyTorch (ComfyUI 核心)",
        "PIL": "Pillow (图像处理)",
        "numpy": "NumPy (数值计算)",
    }
    for mod, name in deps.items():
        try:
            __import__(mod)
            print(ok(f"{name} 已安装"))
        except ImportError:
            print(bad(f"{name} 未安装"))
            issues.append(("WARN", f"请先在 ComfyUI 环境安装 {name}: pip install {mod}"))
    
    return issues

# ---------- 3. 模块导入 ----------
def check_module_imports():
    print(head("3. 节点模块导入检查"))
    issues = []
    
    # 把自己加入 path
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    
    modules = [
        ("story_sense_data", "故事感总纲库"),
        ("pln_llm", "AI API 调用"),
        ("pln_utils", "工具函数"),
        ("pln_random", "随机生成"),
        ("modes_storyboard", "故事板模式"),
        ("modes_book", "绘本模式"),
        ("modes_drama", "短剧模式"),
        ("modes_child", "儿童内容模式"),
        ("modes_design", "专业设计模式"),
        ("engine_story_arc", "故事弧引擎"),
        ("director_engine", "导演引擎"),
        ("director_pro", "批次输出引擎"),
        ("format_templates", "格式模板"),
        ("knowledge_base.director_styles", "导演风格库"),
        ("knowledge_base.tag_taxonomy", "标签分类库"),
        ("knowledge_base.director_pipeline", "导演工作流"),
        ("knowledge_base.narrative_structures", "叙事结构"),
        ("knowledge_base.works_corpus", "作品库(基础)"),
        ("knowledge_base.works_corpus_extended", "作品库(扩展)"),
        ("knowledge_base.works_rich", "作品库(电视剧)"),
        ("knowledge_base.works_hot_shortform", "作品库(短剧)"),
    ]
    
    for mod_name, label in modules:
        try:
            __import__(mod_name)
            print(ok(f"{label} ({mod_name})"))
        except ImportError as e:
            print(bad(f"{label} ({mod_name}): {e}"))
            issues.append(("FATAL", f"模块 {mod_name} 导入失败"))
        except Exception as e:
            print(bad(f"{label} ({mod_name}): {type(e).__name__}: {e}"))
            issues.append(("WARN", f"模块 {mod_name} 运行时错误"))
    
    return issues

# ---------- 4. 节点注册 ----------
def check_node_registration():
    print(head("4. 节点注册检查"))
    issues = []
    
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    
    try:
        import __init__ as node
        print(ok("__init__.py 已加载"))
    except Exception as e:
        print(bad(f"__init__.py 加载失败: {e}"))
        traceback.print_exc()
        issues.append(("FATAL", "__init__.py 无法加载"))
        return issues
    
    # 必备属性
    for attr in ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]:
        if hasattr(node, attr):
            val = getattr(node, attr)
            print(ok(f"{attr} 存在: {val if attr != 'NODE_CLASS_MAPPINGS' else list(val.keys())}"))
        else:
            print(bad(f"{attr} 缺失"))
            issues.append(("FATAL", f"{attr} 缺失,ComfyUI 无法识别节点"))
    
    # 节点类属性
    if hasattr(node, "NODE_CLASS_MAPPINGS"):
        for cname, cls in node.NODE_CLASS_MAPPINGS.items():
            for attr in ["INPUT_TYPES", "RETURN_TYPES", "FUNCTION", "CATEGORY"]:
                if hasattr(cls, attr):
                    print(ok(f"  {cname}.{attr} 存在"))
                else:
                    print(bad(f"  {cname}.{attr} 缺失"))
                    issues.append(("FATAL", f"节点类 {cname} 缺 {attr}"))
    
    return issues

# ---------- 5. 知识库完整性 ----------
def check_knowledge_base():
    print(head("5. 知识库完整性检查"))
    issues = []
    
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    
    try:
        from knowledge_base.director_styles import DIRECTOR_STYLES, DIRECTOR_DECISION
        from knowledge_base.director_pipeline import DIRECTOR_PIPELINE
        from knowledge_base.narrative_structures import NARRATIVE_STRUCTURES, NARRATIVE_DECISION
        from knowledge_base.tag_taxonomy import TAG_TAXONOMY
        from knowledge_base.style_subdivisions import STYLE_SUBDIVISIONS
        from story_sense_data import STORY_SENSE_LIBRARY
        from knowledge_base.works_corpus import WORKS_INDEX
    except Exception as e:
        print(bad(f"知识库导入失败: {e}"))
        return [("FATAL", "知识库模块无法导入")]
    
    # 导演数量
    cats = DIRECTOR_STYLES.get("director_categories", {})
    total = sum(len(v) for v in cats.values())
    print(info(f"导演总数: {total} (分类: {len(cats)})"))
    
    # 字段覆盖率
    required_fields = ["cn", "signature", "visual_techniques", "narrative_principle", "applicable_genres"]
    deep_fields = ["era", "characteristics", "visual_style", "camera", "color_palette",
                   "narrative_traits", "works", "lighting", "composition", "rhythm_preference",
                   "emotional_signature", "sound_music", "failure_modes", "measurement", "alternatives"]
    
    basic_ok = 0
    deep_ok = 0
    for cat_key, dir_keys in cats.items():
        for dk in dir_keys:
            d = DIRECTOR_STYLES.get(dk, {})
            if all(f in d for f in required_fields):
                basic_ok += 1
            deep_count = sum(1 for f in deep_fields if f in d and d[f])
            if deep_count >= 5:
                deep_ok += 1
    
    print(ok(f"基础 5 字段完整: {basic_ok}/{total}"))
    print(info(f"深度字段(5+)完整: {deep_ok}/{total}"))
    if deep_ok < total * 0.8:
        warn(f"建议运行 Phase 1 补全导演档案")
        issues.append(("WARN", f"{total - deep_ok} 个导演档案需要补全"))
    
    # 决策层
    print(info(f"DIRECTOR_DECISION: {len(DIRECTOR_DECISION)} 条"))
    print(info(f"DIRECTOR_PIPELINE: {len(DIRECTOR_PIPELINE)} 条"))
    print(info(f"NARRATIVE_STRUCTURES: {len(NARRATIVE_STRUCTURES)}"))
    print(info(f"NARRATIVE_DECISION: {len(NARRATIVE_DECISION)} 条"))
    print(info(f"TAG_TAXONOMY L1: {len(TAG_TAXONOMY)}"))
    print(info(f"STYLE_SUBDIVISIONS: {len(STYLE_SUBDIVISIONS)}"))
    print(info(f"STORY_SENSE_LIBRARY: {len(STORY_SENSE_LIBRARY)} 条"))
    print(info(f"WORKS_INDEX: {len(WORKS_INDEX) if isinstance(WORKS_INDEX, (list, dict)) else 'N/A'}"))
    
    # 作品库
    for mod_name, label in [
        ("knowledge_base.works_corpus_extended", "扩展作品库"),
        ("knowledge_base.works_rich", "电视剧作品库"),
        ("knowledge_base.works_hot_shortform", "短剧作品库"),
    ]:
        try:
            m = __import__(mod_name, fromlist=["*"])
            dicts = {a: len(getattr(m, a)) for a in dir(m) if not a.startswith("_") and isinstance(getattr(m, a), dict)}
            total_w = sum(dicts.values())
            if total_w == 0:
                print(bad(f"{label} 为空!需要补全"))
                issues.append(("WARN", f"{label} 空模块"))
            else:
                print(ok(f"{label} 共 {total_w} 项"))
        except Exception as e:
            print(warn(f"{label} 加载失败: {e}"))
    
    return issues

# ---------- 6. API 可达性 ----------
def check_api(api_url=None):
    print(head("6. API 可达性检查(可选)"))
    if not api_url:
        print(info("未提供 API URL,跳过"))
        return []
    
    issues = []
    try:
        import requests
        # 简单 GET 测试
        r = requests.get(api_url.replace("/v1/chat/completions", "/v1/models"), timeout=5)
        if r.status_code == 200:
            print(ok(f"API 可达 ({r.status_code})"))
        else:
            print(warn(f"API 返回 {r.status_code}"))
            issues.append(("WARN", f"API 返回非 200: {r.status_code}"))
    except ImportError:
        print(warn("requests 未安装,跳过"))
    except Exception as e:
        print(bad(f"API 不可达: {e}"))
        issues.append(("WARN", "API 不可达,模式选择 != 关闭 时将无法生成"))
    
    return issues

# ---------- 主流程 ----------
def main():
    print(f"\n{C.BLD}ComfyUI-PromptLibraryNode 自检 v1.0{C.RST}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    
    all_issues = []
    all_issues += check_install_path()
    all_issues += check_python_env()
    all_issues += check_module_imports()
    all_issues += check_node_registration()
    all_issues += check_knowledge_base()
    
    # API 可选
    api = os.environ.get("PLN_API_URL")
    if api:
        all_issues += check_api(api)
    
    # 总结
    print(head("诊断总结"))
    fatal = [i for i in all_issues if i[0] == "FATAL"]
    warn_list = [i for i in all_issues if i[0] == "WARN"]
    
    if not all_issues:
        print(ok(f"{C.GRN}全部检查通过!{C.RST}"))
        print(info("重启 ComfyUI 即可看到节点"))
        return 0
    else:
        if fatal:
            print(bad(f"{C.RED}{len(fatal)} 个致命问题:{C.RST}"))
            for _, msg in fatal:
                print(f"     - {msg}")
        if warn_list:
            print(warn(f"{len(warn_list)} 个警告:"))
            for _, msg in warn_list:
                print(f"     - {msg}")
        
        print()
        print(info("建议:"))
        print(info("  1. 重启 ComfyUI 看是否解决问题"))
        print(info("  2. 查看 INSTALL_GUIDE.md"))
        print(info("  3. 在 ComfyUI 启动日志里搜 'PromptLibrary' 关键词"))
        return 1 if fatal else 0

if __name__ == "__main__":
    sys.exit(main())
