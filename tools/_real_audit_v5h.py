# -*- coding: utf-8 -*-
"""
Phase 36.6 v5h: 真实评估 — 实际跑每个节点的 build() 看输出
零虚假: 不用"分数高 = 可用", 实际执行 build() 看是否真有内容
"""
import importlib.util
import inspect
import sys
from pathlib import Path

ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("pkg_init", str(ROOT / "__init__.py"))
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)
NODE_MAP = pkg.NODE_CLASS_MAPPINGS


def real_test_node(ntype, cls):
    """实际执行节点的 build() 验证"""
    try:
        it = cls.INPUT_TYPES()
    except Exception as e:
        return ("FAIL", "INPUT_TYPES 失败: {}".format(e))

    required = it.get("required", {})
    optional = it.get("optional", {})

    # 1. 收集所有必填参数 (取默认值)
    kwargs = {}
    missing = []
    for k, sch in required.items():
        if isinstance(sch, tuple) and len(sch) >= 2 and isinstance(sch[1], dict):
            if "default" in sch[1]:
                kwargs[k] = sch[1]["default"]
            else:
                # 尝试从枚举列表取第一个
                if isinstance(sch[0], list) and sch[0]:
                    kwargs[k] = sch[0][0]
                else:
                    missing.append(k)
        else:
            missing.append(k)

    # 2. 收集所有 optional 参数
    for k, sch in optional.items():
        if isinstance(sch, tuple) and len(sch) >= 2 and isinstance(sch[1], dict):
            if "default" in sch[1]:
                kwargs[k] = sch[1]["default"]
            else:
                kwargs[k] = ""

    # 3. 4 路 injection 提供真实内容
    kwargs["灵魂注入"] = "[灵魂注入] 测试数据: 60 情感 + 10 维度"
    kwargs["审美注入"] = "[审美判断] 测试数据: 8 原则 + 120 场景"
    kwargs["风格注入"] = "[风格指南] 测试数据: 5 调色 + 8 摄影指导"
    kwargs["导演意图"] = "[导演意图] 测试数据: 4 类意图"

    # 4. 实际调用 build()
    func_name = getattr(cls, "FUNCTION", None)
    if not func_name or not hasattr(cls, func_name):
        return ("FAIL", "FUNCTION 不存在")
    try:
        result = getattr(cls(), func_name)(**kwargs)
    except Exception as e:
        return ("FAIL", "build() 失败: {}".format(str(e)[:200]))

    # 5. 检查输出
    if not isinstance(result, tuple):
        return ("FAIL", "build() 返回不是 tuple")

    rt = getattr(cls, "RETURN_TYPES", ()) or ()
    if len(result) != len(rt):
        return ("WARN", "返回 {} 个, RETURN_TYPES 声明 {} 个".format(len(result), len(rt)))

    # 6. 检查 4 路 injection 是否被使用 (查 build 输出是否包含 injection 关键词)
    injection_used = False
    for item in result:
        if isinstance(item, str):
            if "灵魂注入" in item or "审美判断" in item or "风格指南" in item or "导演意图" in item:
                if "Phase 36.6 v5g" in item or "测试数据" in item:
                    injection_used = True
                    break

    # 7. 检查输出是否有实质内容
    real_content = sum(1 for item in result if isinstance(item, str) and len(item) > 50)
    total_str = sum(1 for item in result if isinstance(item, str))

    if not injection_used:
        return ("PARTIAL", "4 路 injection 接收但未集成 (假 link)")
    if real_content == 0:
        return ("WARN", "build() 输出空字符串")
    return ("PASS", "{} 个有内容, injection 集成".format(real_content))


def main():
    print("=" * 80)
    print("Phase 36.6 v5h: 真实评估 44 节点 (实际跑 build())")
    print("=" * 80)

    results = []
    for ntype, cls in NODE_MAP.items():
        status, reason = real_test_node(ntype, cls)
        results.append((ntype, status, reason))

    # 按 status 排序
    order = {"FAIL": 0, "WARN": 1, "PARTIAL": 2, "PASS": 3}
    results.sort(key=lambda x: (order.get(x[1], 4), x[0]))

    fail = sum(1 for r in results if r[1] == "FAIL")
    warn = sum(1 for r in results if r[1] == "WARN")
    partial = sum(1 for r in results if r[1] == "PARTIAL")
    passed = sum(1 for r in results if r[1] == "PASS")

    print()
    print("FAIL ({})".format(fail))
    print("-" * 80)
    for ntype, status, reason in results:
        if status == "FAIL":
            print("  {}: {}".format(ntype, reason))

    print()
    print("WARN ({})".format(warn))
    print("-" * 80)
    for ntype, status, reason in results:
        if status == "WARN":
            print("  {}: {}".format(ntype, reason))

    print()
    print("PARTIAL ({})".format(partial))
    print("-" * 80)
    for ntype, status, reason in results:
        if status == "PARTIAL":
            print("  {}: {}".format(ntype, reason))

    print()
    print("PASS ({})".format(passed))
    print("-" * 80)
    for ntype, status, reason in results:
        if status == "PASS":
            print("  {}: {}".format(ntype, reason))

    print()
    print("=" * 80)
    print("真实评估: {} FAIL, {} WARN, {} PARTIAL, {} PASS".format(fail, warn, partial, passed))
    print("=" * 80)
    print("0 虚假容忍: 真实情况是 — {} 个节点 build() 没用 4 路 injection".format(partial))


if __name__ == "__main__":
    main()
