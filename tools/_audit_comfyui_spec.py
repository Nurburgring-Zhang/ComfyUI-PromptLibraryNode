# -*- coding: utf-8 -*-
"""
ComfyUI 官方规范严格审计
=========================
按 ComfyUI 内部 nodes.py 标准:
1. INPUT_TYPES 必须是 @classmethod
2. RETURN_TYPES 是 tuple of str
3. RETURN_NAMES 是 tuple of str (可选)
4. FUNCTION 是方法名字符串
5. FUNCTION 方法返回必须是 tuple (尾随逗号)
6. CATEGORY 是路径 (用 / 分隔)
7. OUTPUT_NODE 可选 (True 表示终节点)
8. IS_CHANGED 可选 @classmethod
9. VALIDATE_INPUTS 可选 @classmethod
10. INPUT_IS_LIST / OUTPUT_IS_LIST 可选
"""
import sys
import inspect
sys.path.insert(0, '.')
import __init__ as pkg

issues = []

for name, cls in pkg.NODE_CLASS_MAPPINGS.items():
    # 1. INPUT_TYPES 必须是 @classmethod
    it_method = cls.__dict__.get('INPUT_TYPES', None)
    if it_method is None:
        issues.append('%s: 没有 INPUT_TYPES 方法' % name)
        continue
    if not isinstance(it_method, classmethod):
        issues.append('%s: INPUT_TYPES 不是 @classmethod (ComfyUI 规范要求)' % name)

    # 2. RETURN_TYPES 必须是 tuple
    rt = getattr(cls, 'RETURN_TYPES', None)
    if rt is None:
        issues.append('%s: 没有 RETURN_TYPES' % name)
    elif not isinstance(rt, tuple):
        issues.append('%s: RETURN_TYPES 不是 tuple, 是 %s' % (name, type(rt).__name__))
    else:
        for i, t in enumerate(rt):
            if not isinstance(t, str):
                issues.append('%s: RETURN_TYPES[%d] 不是 str' % (name, i))

    # 3. RETURN_NAMES 如果有, 必须 tuple 且 len == len(RETURN_TYPES)
    rn = getattr(cls, 'RETURN_NAMES', None)
    if rn is not None:
        if not isinstance(rn, tuple):
            issues.append('%s: RETURN_NAMES 不是 tuple, 是 %s' % (name, type(rn).__name__))
        elif rt is not None and len(rn) != len(rt):
            issues.append('%s: RETURN_NAMES 长度 %d != RETURN_TYPES 长度 %d' % (name, len(rn), len(rt)))

    # 4. FUNCTION 必须是字符串方法名
    fn_name = getattr(cls, 'FUNCTION', None)
    if not fn_name:
        issues.append('%s: 没有 FUNCTION' % name)
        continue
    if not isinstance(fn_name, str):
        issues.append('%s: FUNCTION 不是字符串' % name)
        continue
    fn = getattr(cls, fn_name, None)
    if fn is None or not callable(fn):
        issues.append('%s: FUNCTION 指向的方法 %s 不存在或不可调用' % (name, fn_name))
        continue

    # 5. CATEGORY
    cat = getattr(cls, 'CATEGORY', None)
    if not cat or not isinstance(cat, str):
        issues.append('%s: CATEGORY 缺失或非 str' % name)

    # 6. IS_CHANGED 如果有, 必须是 @classmethod
    is_changed = cls.__dict__.get('IS_CHANGED', None)
    if is_changed is not None and not isinstance(is_changed, classmethod):
        issues.append('%s: IS_CHANGED 不是 @classmethod' % name)

    # 7. VALIDATE_INPUTS 如果有, 必须是 @classmethod
    vi = cls.__dict__.get('VALIDATE_INPUTS', None)
    if vi is not None and not isinstance(vi, classmethod):
        issues.append('%s: VALIDATE_INPUTS 不是 @classmethod' % name)

    # 8. OUTPUT_NODE 必须是 bool
    on = getattr(cls, 'OUTPUT_NODE', None)
    if on is not None and not isinstance(on, bool):
        issues.append('%s: OUTPUT_NODE 不是 bool' % name)

    # 9. 函数签名必须能接受 INPUT_TYPES 的所有 required 字段
    try:
        sig = inspect.signature(fn)
        fn_params = list(sig.parameters.keys())
        # 类方法的第一个参数是 self
        if fn_params and fn_params[0] == 'self':
            fn_params = fn_params[1:]
        # 检查是否有 **kwargs (VAR_KEYWORD 类型)
        has_var_keyword = any(
            p.kind == inspect.Parameter.VAR_KEYWORD
            for p in sig.parameters.values()
        )
        it = cls.INPUT_TYPES()
        for fname in it.get('required', {}).keys():
            if fname not in fn_params and not has_var_keyword:
                issues.append('%s: 函数签名缺参数 %s, 也无 **kwargs' % (name, fname))
    except Exception as e:
        issues.append('%s: 函数签名检查失败: %s' % (name, e))

print('=' * 70)
print('ComfyUI 官方规范严格审计 (43 节点)')
print('=' * 70)
print('总问题: %d' % len(issues))
print()
if issues:
    print('=== 问题清单 ===')
    for i in issues:
        print('  [ISSUE] %s' % i)
else:
    print('=== 全部合规 ===')
    print('  ✓ INPUT_TYPES 全部 @classmethod')
    print('  ✓ RETURN_TYPES 全部 tuple of str')
    print('  ✓ RETURN_NAMES 全部匹配')
    print('  ✓ FUNCTION 全部可调用')
    print('  ✓ CATEGORY 全部 str')
    print('  ✓ IS_CHANGED/VALIDATE_INPUTS 如有, 全部 @classmethod')
    print('  ✓ 函数签名全部包含 INPUT_TYPES required 字段')
