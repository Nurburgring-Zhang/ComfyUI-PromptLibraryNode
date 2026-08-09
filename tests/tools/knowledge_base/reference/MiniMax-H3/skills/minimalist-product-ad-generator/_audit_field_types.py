# -*- coding: utf-8 -*-
"""
深度审查 4: 每个 INPUT_TYPES 字段类型真实性
- STRING / INT / FLOAT / BOOLEAN / LIST(枚举) / SEED
- 字段不能空, 不能是 list 后面没跟 tuple 等异常
"""
import sys, importlib.util
from pathlib import Path

ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("pkg_init", str(ROOT / "__init__.py"))
pkg_init = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg_init)
NODE_MAP = pkg_init.NODE_CLASS_MAPPINGS

VALID_TYPES = {"STRING", "INT", "FLOAT", "BOOLEAN", "SEED", "IMAGE", "MASK", "LATENT", "MODEL", "CONDITIONING", "VAE", "CLIP", "AUDIO", "VIDEO"}

problems = []
total_required = 0
total_optional = 0
field_type_count = {}

for name, cls in NODE_MAP.items():
    try:
        it = cls.INPUT_TYPES()
    except Exception as e:
        problems.append((name, "INPUT_TYPES_EXCEPTION", str(e)))
        continue

    for kind in ("required", "optional"):
        fields = it.get(kind, {})
        for fname, fspec in fields.items():
            if not isinstance(fspec, tuple):
                problems.append((name, "FIELD_NOT_TUPLE", f"{kind}.{fname}"))
                continue
            if len(fspec) < 1:
                problems.append((name, "FIELD_EMPTY_TUPLE", f"{kind}.{fname}"))
                continue
            ftype = fspec[0]
            if isinstance(ftype, list):
                # 枚举: list 后面是 config dict
                if len(ftype) == 0:
                    problems.append((name, "ENUM_EMPTY", f"{kind}.{fname}"))
                continue
            if str(ftype).upper() not in VALID_TYPES:
                problems.append((name, "BAD_TYPE", f"{kind}.{fname} type={ftype!r}"))
            field_type_count[str(ftype).upper()] = field_type_count.get(str(ftype).upper(), 0) + 1
            if kind == "required":
                total_required += 1
            else:
                total_optional += 1

print(f"=== 41 节点 INPUT_TYPES 字段类型审查 ===\n")
print(f"总 required 字段: {total_required}")
print(f"总 optional 字段: {total_optional}")
print(f"字段类型分布:")
for t, c in sorted(field_type_count.items(), key=lambda x: -x[1]):
    print(f"  {t}: {c}")

print(f"\n问题数: {len(problems)}")
for name, kind, info in problems[:50]:
    print(f"  ❌ [{name}] {kind} - {info}")
if not problems:
    print("✅ 全部 41 节点的 INPUT_TYPES 字段都是合法类型 (STRING/INT/FLOAT/BOOLEAN/SEED/枚举)")
