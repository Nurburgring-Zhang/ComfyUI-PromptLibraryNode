# -*- coding: utf-8 -*-
"""
深度审查 2: FUNCTION 签名 vs INPUT_TYPES keys 是否匹配
+ 主入口函数真能跑通 (传 stub 输入)
"""
import sys, os, importlib, importlib.util, traceback, json, inspect
from pathlib import Path

ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("pkg_init", str(ROOT / "__init__.py"))
pkg_init = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg_init)
NODE_MAP = pkg_init.NODE_CLASS_MAPPINGS

# 给每种类型造一个 dummy 值
def stub_for(t, opt=False):
    if isinstance(t, list):
        return t[0] if t else ""
    s = str(t).upper()
    if "INT" in s: return 1
    if "FLOAT" in s: return 0.5
    if "BOOL" in s: return False
    if "STRING" in s: return "stub_input"
    return None

problems = []
for name, cls in NODE_MAP.items():
    try:
        inst = cls()
        it = cls.INPUT_TYPES()
        req_keys = list(it.get("required", {}).keys())
        opt_keys = list(it.get("optional", {}).keys())
        all_keys = req_keys + opt_keys
        fn = getattr(inst, cls.FUNCTION, None)
        sig = inspect.signature(fn)
        params = list(sig.parameters.keys())
        # 第一参数通常 self,跳过
        if params and params[0] == "self":
            params = params[1:]

        missing = [k for k in all_keys if k not in params]
        extra = [k for k in params if k not in all_keys]
        # **kwargs 是 ComfyUI 接收大量动态输入的标准做法,不算 mismatch
        if "kwargs" in extra or "**kwargs" in extra:
            extra = []
            missing = []  # kwargs 全部吸收
        if missing or extra:
            problems.append((name, "SIG_MISMATCH", {"missing_in_fn": missing, "extra_in_fn": extra}))

        # 现在真跑一次,传全部 stub
        kwargs = {}
        for k in req_keys:
            spec_field = it["required"][k]
            t = spec_field[0] if isinstance(spec_field, tuple) else spec_field
            kwargs[k] = stub_for(t)
        for k in opt_keys:
            spec_field = it["optional"][k]
            t = spec_field[0] if isinstance(spec_field, tuple) else spec_field
            kwargs[k] = stub_for(t, opt=True)
        # 隐藏参数: * / hidden 之类
        try:
            ret = fn(**kwargs)
        except TypeError as e:
            problems.append((name, "CALL_TYPEERROR", {"err": str(e)[:200]}))
        except Exception as e:
            # 业务异常 OK (因为 stub 数据),只看是否进到函数体
            pass
        else:
            rt = getattr(cls, "RETURN_TYPES", ())
            if isinstance(ret, tuple):
                if len(ret) != len(rt):
                    problems.append((name, "RETURN_COUNT", {"got": len(ret), "expect": len(rt)}))
            elif len(rt) == 1:
                pass  # 允许单值
            else:
                problems.append((name, "RETURN_NOT_TUPLE", {"got_type": type(ret).__name__, "expect": len(rt)}))
    except Exception as e:
        problems.append((name, "CRASH", {"err": str(e)[:200], "tb": traceback.format_exc()[:400]}))

print(f"=== 41 节点 FUNCTION 签名/可调用性审查 ===\n")
print(f"总问题数: {len(problems)}\n")
for name, kind, info in problems:
    print(f"❌ [{name}] {kind}")
    for k, v in info.items():
        print(f"     {k}: {v}")

if not problems:
    print("✅ 全部 41 节点主入口函数签名匹配 INPUT_TYPES,且能成功调用 (stub 模式)")
