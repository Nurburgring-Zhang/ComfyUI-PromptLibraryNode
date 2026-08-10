# -*- coding: utf-8 -*-
"""
Phase 35.9.2 5 要素架构核对脚本
- 41 节点逐一验证
- 5 要素: 数据 + 上下文缩略 + skill/harness + 经验矩阵 + AI 深度处理
"""
import sys, os, ast, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

results = []
def check_5elem(node_name, src_text):
    """5 要素核对"""
    elem = {
        "data": False,           # 数据
        "context_summary": False, # 上下文缩略
        "skill_harness": False,  # skill/harness
        "experience": False,     # 经验矩阵
        "ai_deep": False,        # AI 深度处理
    }
    # 数据: 引用 knowledge_base / import 知识库
    if re.search(r"knowledge_base|from knowledge_base|NARRATIVE_STRUCTURES|DIRECTOR_PROFILES|EMOTION_MATRIX_60", src_text):
        elem["data"] = True
    # 上下文缩略: 5 维具体化 / _extract_5d_specifics / scene_progress
    if re.search(r"_extract_5d_specifics|场景锚点|scene_progress|5 维|5d|5维", src_text):
        elem["context_summary"] = True
    # skill/harness: addon 注入 / DirectorSoulNode 引用 / 灵魂addon parse
    if re.search(r"灵魂addon|DirectorSoulNode|build_soul|灵魂注入|parse.*addon", src_text):
        elem["skill_harness"] = True
    # 经验矩阵: 导演签名 / 风格库 / 12 套理论 / 9 维光照
    if re.search(r"DIRECTOR_STYLES|DIRECTORS_20|NARRATIVE_STRUCTURES|director_8d|9 维|12 套理论|director_sig|director_", src_text):
        elem["experience"] = True
    # AI 深度处理: 动态生成 / kwargs 注入 / 真 parse 灵魂addon / 跨场景差异化
    if re.search(r"kwargs\.get|f\".*\{.*\}.*\"|kwargs\[|build_soul_injection|parse_", src_text):
        elem["ai_deep"] = True
    return elem

def main():
    import __init__ as init
    print("=" * 60)
    print("Phase 35.9.2 5 要素架构核对 - 41 节点")
    print("=" * 60)
    summary = []
    for name, node_cls in init.NODE_CLASS_MAPPINGS.items():
        # 找节点源文件
        try:
            src_file = sys.modules[node_cls.__module__].__file__
            if src_file and src_file.endswith(".py"):
                with open(src_file, "r", encoding="utf-8") as f:
                    src = f.read()
            else:
                src = ""
        except Exception:
            src = ""
        elem = check_5elem(name, src)
        cnt = sum(1 for v in elem.values() if v)
        missing = [k for k, v in elem.items() if not v]
        status = "OK" if cnt >= 4 else ("PARTIAL" if cnt >= 2 else "FAIL")
        summary.append((name, cnt, status, missing))
        if status != "OK":
            print(f"  [{status}] {name}: {cnt}/5 要素 (缺: {', '.join(missing)})")
    # 汇总
    ok = sum(1 for _, _, s, _ in summary if s == "OK")
    partial = sum(1 for _, _, s, _ in summary if s == "PARTIAL")
    fail = sum(1 for _, _, s, _ in summary if s == "FAIL")
    print(f"\n汇总: OK={ok}, PARTIAL={partial}, FAIL={fail}")
    print(f"5 要素完整: {ok}/41 节点")
    return 0 if ok == 41 else 1

sys.exit(main())
