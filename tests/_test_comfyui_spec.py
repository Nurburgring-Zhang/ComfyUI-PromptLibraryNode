# -*- coding: utf-8 -*-
"""
Phase 36.6 v5: ComfyUI 节点规范审计
====================================
8 项 ComfyUI 节点规范检查:
1. @classmethod INPUT_TYPES
2. tuple RETURN_TYPES
3. 函数签名 **kwargs (允许其他参数)
4. RETURN_NAMES 长度匹配 RETURN_TYPES
5. CATEGORY str 路径
6. OUTPUT_NODE bool (可选)
7. IS_CHANGED / VALIDATE_INPUTS @classmethod (可选)
8. NODE_CLASS_MAPPINGS 中能找到
"""
import sys, os, inspect, ast
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode')

try:
    import __init__ as pl
except Exception as e:
    print(f'[FATAL] __init__.py import 失败: {e}')
    sys.exit(1)

print(f'=== ComfyUI 规范审计: {len(pl.NODE_CLASS_MAPPINGS)} 节点 ===\n')

violations = []
checked = 0
for name, cls in pl.NODE_CLASS_MAPPINGS.items():
    checked += 1
    item = {'node': name, 'class': cls.__name__, 'issues': []}
    try:
        # 1. @classmethod INPUT_TYPES
        inp = getattr(cls, 'INPUT_TYPES', None)
        if not callable(inp):
            item['issues'].append('INPUT_TYPES 不可调用')
        # 调用一次确认能跑
        try:
            ret = cls.INPUT_TYPES()
            assert isinstance(ret, dict), f'INPUT_TYPES() 返回非 dict: {type(ret)}'
            assert 'required' in ret, '缺 required 字段'
        except Exception as e:
            item['issues'].append(f'INPUT_TYPES() 调用失败: {e}')
        # 2. tuple RETURN_TYPES
        rt = getattr(cls, 'RETURN_TYPES', None)
        if not isinstance(rt, tuple) or len(rt) == 0:
            item['issues'].append(f'RETURN_TYPES 不是非空 tuple: {rt!r}')
        # 3. 函数签名 **kwargs (FUNCTION 方法)
        func_name = getattr(cls, 'FUNCTION', None)
        if not func_name:
            item['issues'].append('缺 FUNCTION 字段')
        elif not hasattr(cls, func_name):
            item['issues'].append(f'FUNCTION 方法 {func_name} 不存在')
        else:
            func = getattr(cls, func_name)
            try:
                sig = inspect.signature(func)
                has_var_keyword = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
                if not has_var_keyword:
                    item['issues'].append(f'FUNCTION {func_name} 缺 **kwargs (ComfyUI 必须)')
            except (ValueError, TypeError):
                item['issues'].append(f'FUNCTION {func_name} 签名解析失败')
        # 4. RETURN_NAMES 长度匹配 (如果有)
        rn = getattr(cls, 'RETURN_NAMES', None)
        if rn is not None:
            if not isinstance(rn, tuple):
                item['issues'].append(f'RETURN_NAMES 不是 tuple: {rn!r}')
            elif len(rn) != len(rt):
                item['issues'].append(f'RETURN_NAMES 长度 {len(rn)} != RETURN_TYPES 长度 {len(rt)}')
        # 5. CATEGORY
        cat = getattr(cls, 'CATEGORY', None)
        if not cat or not isinstance(cat, str) or '/' not in cat:
            item['issues'].append(f'CATEGORY 不合法: {cat!r}')
        # 6. OUTPUT_NODE bool (允许不存在, 默认 False)
        on = getattr(cls, 'OUTPUT_NODE', False)
        if not isinstance(on, bool):
            item['issues'].append(f'OUTPUT_NODE 不是 bool: {on!r}')
        # 7. IS_CHANGED / VALIDATE_INPUTS (允许不存在)
        for opt in ('IS_CHANGED', 'VALIDATE_INPUTS'):
            v = getattr(cls, opt, None)
            if v is not None and not callable(v):
                item['issues'].append(f'{opt} 存在但不可调用')
    except Exception as e:
        item['issues'].append(f'审计过程异常: {e}')
    if item['issues']:
        violations.append(item)

print(f'审计节点: {checked}')
print(f'违规节点: {len(violations)}\n')
for v in violations:
    print(f'  [FAIL] {v["node"]:35s}  {v["class"]}')
    for issue in v['issues']:
        print(f'         - {issue}')

if not violations:
    print(f'  [OK] 所有 {checked} 节点 ComfyUI 规范合规')
print(f'\n=== 总计 {checked - len(violations)}/{checked} 规范合规 ===')
sys.exit(0 if not violations else 1)
