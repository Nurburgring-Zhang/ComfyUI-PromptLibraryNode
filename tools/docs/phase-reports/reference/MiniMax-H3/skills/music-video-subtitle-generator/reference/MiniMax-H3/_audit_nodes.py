# -*- coding: utf-8 -*-
"""
41 节点诚实审查:
  1. 导入成功?
  2. INPUT_TYPES() 返回 dict 且有 required/optional?
  3. RETURN_TYPES / RETURN_NAMES 列出?
  4. FUNCTION 存在?
  5. 主入口函数签名参数与 INPUT_TYPES 是否匹配?
  6. inputs 是不是真的能被 ComfyUI 渲染 (字符串/数字/枚举/组合框)?
"""

import sys, os, importlib, traceback, json
from pathlib import Path

ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
sys.path.insert(0, str(ROOT))

import importlib.util
spec = importlib.util.spec_from_file_location("pkg_init", str(ROOT / "__init__.py"))
pkg_init = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg_init)

NODE_MAP = pkg_init.NODE_CLASS_MAPPINGS
print(f"=== 总注册节点数: {len(NODE_MAP)} ===\n")

report = []
for name, cls in NODE_MAP.items():
    row = {"name": name, "ok": True, "errors": [], "info": {}}
    try:
        # 1. INPUT_TYPES
        it = cls.INPUT_TYPES()
        if not isinstance(it, dict):
            row["ok"] = False
            row["errors"].append("INPUT_TYPES() did not return dict")
        else:
            req = it.get("required", {})
            opt = it.get("optional", {})
            row["info"]["required_keys"] = list(req.keys())
            row["info"]["optional_keys"] = list(opt.keys())
            row["info"]["required_count"] = len(req)
            row["info"]["optional_count"] = len(opt)

        # 2. RETURN_TYPES
        rt = getattr(cls, "RETURN_TYPES", None)
        if not rt:
            row["ok"] = False
            row["errors"].append("RETURN_TYPES missing or empty")
        else:
            row["info"]["return_types"] = list(rt)
            row["info"]["return_count"] = len(rt)

        # 3. RETURN_NAMES
        rn = getattr(cls, "RETURN_NAMES", None)
        if rn:
            row["info"]["return_names"] = list(rn)
        else:
            row["info"]["return_names"] = None

        # 4. FUNCTION
        fn_name = getattr(cls, "FUNCTION", None)
        if not fn_name:
            row["ok"] = False
            row["errors"].append("FUNCTION missing")
        else:
            row["info"]["function"] = fn_name
            fn = getattr(cls(), fn_name, None)
            if fn is None:
                row["ok"] = False
                row["errors"].append(f"FUNCTION '{fn_name}' not on instance")
            else:
                import inspect
                sig = inspect.signature(fn)
                row["info"]["fn_params"] = list(sig.parameters.keys())

        # 5. CATEGORY
        cat = getattr(cls, "CATEGORY", None)
        row["info"]["category"] = cat

    except Exception as e:
        row["ok"] = False
        row["errors"].append(f"Exception: {e!r}")
        row["errors"].append(traceback.format_exc())

    report.append(row)

# 输出报告
print(f"{'NAME':<35} {'OK':<5} {'IN_REQ':<7} {'IN_OPT':<7} {'OUT':<5} {'FN':<30} {'ERR'}")
print("-" * 150)
ok_count = 0
for r in report:
    status = "✅" if r["ok"] else "❌"
    if r["ok"]:
        ok_count += 1
    req = r["info"].get("required_count", "-")
    opt = r["info"].get("optional_count", "-")
    out = r["info"].get("return_count", "-")
    fn = r["info"].get("function", "-") or "-"
    err = "; ".join(r["errors"][:2])[:60] if r["errors"] else ""
    print(f"{r['name']:<35} {status:<5} {req:<7} {opt:<7} {out:<5} {fn:<30} {err}")

print(f"\n=== {ok_count}/{len(report)} 节点基本结构正常 ===\n")

# 详细列出有问题的节点
bad = [r for r in report if not r["ok"]]
if bad:
    print("=== 有问题的节点 ===")
    for r in bad:
        print(f"\n[{r['name']}]")
        for e in r["errors"]:
            print(f"  - {e}")

# 写入 JSON 详细报告
with open(ROOT / "_audit_nodes_detail.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2, default=str)
print(f"\n详细报告: {ROOT / '_audit_nodes_detail.json'}")
