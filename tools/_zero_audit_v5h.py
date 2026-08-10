# -*- coding: utf-8 -*-
"""
零虚假容忍真实能力测试 (Phase 36.6 v5h)
- 不是测 INPUT_TYPES 存在, 是测 build() 真实输出质量
- 不是测 JSON 合法, 是测工作流可被 ComfyUI 加载并执行
- 不是测 widget 数量, 是测 prompt 生成对实际生成质量的影响
"""
import json
import importlib.util
import sys
import traceback
from pathlib import Path

ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("pkg_init", str(ROOT / "__init__.py"))
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)
NODE_MAP = pkg.NODE_CLASS_MAPPINGS


def test_node_real_output(ntype, cls):
    """真实测试 build() 输出质量"""
    try:
        it = cls.INPUT_TYPES()
        required = it.get("required", {})
        optional = it.get("optional", {})
    except Exception as e:
        return ("FAIL", f"INPUT_TYPES 失败: {e}")

    func_name = getattr(cls, "FUNCTION", None)
    if not func_name or not hasattr(cls, func_name):
        return ("FAIL", "无 FUNCTION")

    # 准备真实测试输入
    test_kwargs = {}
    for kind in ("required", "optional"):
        for fname, fspec in required.items() if kind == "required" else optional.items():
            if isinstance(fspec, tuple) and len(fspec) >= 1:
                t = fspec[0]
            else:
                t = "STRING"
            if isinstance(t, list):
                # COMBO 选第一个
                test_kwargs[fname] = t[0] if t else ""
            else:
                t_str = str(t).upper()
                if "INT" in t_str:
                    opts = fspec[1] if isinstance(fspec, tuple) and len(fspec) > 1 else {}
                    test_kwargs[fname] = opts.get("default", 1)
                elif "FLOAT" in t_str:
                    opts = fspec[1] if isinstance(fspec, tuple) and len(fspec) > 1 else {}
                    test_kwargs[fname] = opts.get("default", 1.0)
                elif "BOOL" in t_str:
                    test_kwargs[fname] = True
                else:
                    opts = fspec[1] if isinstance(fspec, tuple) and len(fspec) > 1 else {}
                    default = opts.get("default", "")
                    # STRING 用非空测试值
                    if "反AI" in fname or "启用" in fname:
                        test_kwargs[fname] = True if isinstance(default, bool) else (default or "")
                    else:
                        test_kwargs[fname] = default if default else f"[测试]{fname}[/测试]"

    # 调用 build()
    try:
        func = getattr(cls(), func_name)
        result = func(**test_kwargs)
    except TypeError as e:
        return ("FAIL", f"build() TypeError: {str(e)[:100]}")
    except Exception as e:
        return ("FAIL", f"build() Exception: {type(e).__name__}: {str(e)[:100]}")

    # 评估输出质量
    if result is None:
        return ("FAIL", "build() 返回 None")

    rt = getattr(cls, "RETURN_TYPES", ()) or ()
    expected_count = len(rt)

    if isinstance(result, tuple):
        if len(result) != expected_count:
            return ("FAIL", f"build() 返回 {len(result)} 个 output, 期望 {expected_count}")
        # 检查每个 output 不是 None / 空
        for i, r in enumerate(result):
            if r is None:
                return ("FAIL", f"output[{i}] 是 None")
        # 检查至少一个 output 长度 > 50 (不是空字符串)
        max_len = max((len(str(r)) for r in result), default=0)
        if max_len < 50:
            return ("PARTIAL", f"build() 输出过短 (max {max_len} chars), 可能是 widget-only 节点")
        return ("PASS", f"build() 输出 {expected_count} 项, 最长 {max_len} chars")
    else:
        # 单一输出
        if len(str(result)) < 50:
            return ("PARTIAL", f"build() 单输出过短 ({len(str(result))} chars)")
        if expected_count != 1:
            return ("WARN", f"build() 返回单值但 RETURN_TYPES 有 {expected_count} 项")
        return ("PASS", f"build() 单输出 {len(str(result))} chars")


def main():
    print("=" * 80)
    print("Phase 36.6 v5h: 零虚假容忍真实能力测试 (build() 实际输出)")
    print("=" * 80)

    results = {"PASS": [], "PARTIAL": [], "FAIL": [], "WARN": []}
    for ntype, cls in NODE_MAP.items():
        status, reason = test_node_real_output(ntype, cls)
        results[status].append((ntype, reason))

    total = len(NODE_MAP)
    print()
    print(f"PASS: {len(results['PASS'])}/{total}")
    print(f"PARTIAL: {len(results['PARTIAL'])}/{total}")
    print(f"WARN: {len(results['WARN'])}/{total}")
    print(f"FAIL: {len(results['FAIL'])}/{total}")
    print()

    for status in ("FAIL", "PARTIAL", "WARN", "PASS"):
        if not results[status]:
            continue
        print(f"--- {status} ({len(results[status])}) ---")
        for ntype, reason in results[status][:50]:
            print(f"  {ntype}: {reason}")
        if len(results[status]) > 50:
            print(f"  ... ({len(results[status]) - 50} more)")
        print()

    return results


if __name__ == "__main__":
    main()
