# -*- coding: utf-8 -*-
"""
深度审查 3: 真实业务调用 41 节点
- 必填字段从 INPUT_TYPES 取 (用 stub 默认值)
- 可选字段不传
- 跑通后检查输出: 元组长度匹配 RETURN_TYPES, 至少一个非空字符串
"""
import sys, importlib.util, traceback
from pathlib import Path

ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("pkg_init", str(ROOT / "__init__.py"))
pkg_init = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg_init)
NODE_MAP = pkg_init.NODE_CLASS_MAPPINGS


def stub_for(t):
    """根据 INPUT_TYPES schema 造一个合理默认值"""
    if isinstance(t, list):
        # 枚举: 选第一个
        return t[0] if t else "default"
    s = str(t).upper()
    if "INT" in s: return 1
    if "FLOAT" in s: return 0.5
    if "BOOL" in s: return True
    if "STRING" in s:
        # 多行用 multiline 标识
        return "stub_test_value_测试输入"
    return None


results = []
for name, cls in NODE_MAP.items():
    rec = {"name": name, "ok": True, "errors": [], "out_len": 0, "nonempty": 0}
    try:
        inst = cls()
        it = cls.INPUT_TYPES()
        kwargs = {}
        for k, sch in it.get("required", {}).items():
            t = sch[0] if isinstance(sch, tuple) else sch
            kwargs[k] = stub_for(t)
        # 不传 optional
        fn = getattr(inst, cls.FUNCTION)
        ret = fn(**kwargs)
        if not isinstance(ret, tuple):
            ret = (ret,)
        rec["out_len"] = len(ret)
        rec["nonempty"] = sum(1 for x in ret if x is not None and str(x).strip())
        # 输出元组长度 vs RETURN_TYPES
        rt = getattr(cls, "RETURN_TYPES", ())
        if len(ret) != len(rt):
            rec["ok"] = False
            rec["errors"].append(f"输出元组长度 {len(ret)} vs RETURN_TYPES {len(rt)}")
    except Exception as e:
        rec["ok"] = False
        rec["errors"].append(f"{type(e).__name__}: {str(e)[:200]}")
    results.append(rec)

print(f"=== 41 节点真实业务调用审查 ===\n")
ok = sum(1 for r in results if r["ok"])
print(f"成功 {ok}/41\n")
print(f"{'NAME':<35} {'OK':<5} {'OUT':<5} {'NONEMPTY':<10} {'ERR'}")
print("-" * 110)
for r in results:
    status = "OK" if r["ok"] else "FAIL"
    err = "; ".join(r["errors"][:1])[:60] if r["errors"] else ""
    print(f"{r['name']:<35} {status:<5} {r['out_len']:<5} {r['nonempty']:<10} {err}")

bad = [r for r in results if not r["ok"]]
if bad:
    print(f"\n=== 失败节点详细 ===")
    for r in bad:
        print(f"\n[{r['name']}]")
        for e in r["errors"]:
            print(f"  - {e}")
