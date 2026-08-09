# -*- coding: utf-8 -*-
"""
Phase 36.6 v5: 43+1 节点可运行测试基线
========================================
- 验证 NODE_CLASS_MAPPINGS 全部节点能 import + 实例化 + build_mastery/build_xxx 调用不抛
- 不接真实 ComfyUI，只测纯 Python 层
- 检查项: import / 节点类 / CATEGORY / RETURN_TYPES / RETURN_NAMES / FUNCTION / INPUT_TYPES 合法 / build 调用成功
"""
import sys, os, traceback
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode')

ok = 0
fail = 0
results = []

try:
    import __init__ as pl
except Exception as e:
    print(f'[FATAL] __init__.py import 失败: {e}')
    traceback.print_exc()
    sys.exit(1)

print(f'=== 节点可运行测试: {len(pl.NODE_CLASS_MAPPINGS)} 节点 ===\n')

for name, cls in pl.NODE_CLASS_MAPPINGS.items():
    item = {'node': name, 'class': cls.__name__, 'checks': []}
    try:
        # 1. 节点类存在
        assert cls is not None, 'class is None'
        item['checks'].append(('class', 'ok'))
        # 2. CATEGORY
        cat = getattr(cls, 'CATEGORY', '')
        assert cat and isinstance(cat, str) and '/' in cat, f'CATEGORY 错误: {cat!r}'
        item['checks'].append(('CATEGORY', cat))
        # 3. RETURN_TYPES
        rt = getattr(cls, 'RETURN_TYPES', None)
        assert rt and isinstance(rt, tuple) and len(rt) > 0, f'RETURN_TYPES 错误: {rt!r}'
        item['checks'].append(('RETURN_TYPES', str(rt)))
        # 4. RETURN_NAMES (可选但要有, 长度匹配)
        rn = getattr(cls, 'RETURN_NAMES', None)
        if rn is None:
            item['checks'].append(('RETURN_NAMES', 'None (允许)'))
        else:
            assert isinstance(rn, tuple) and len(rn) == len(rt), f'RETURN_NAMES 长度不匹配 RETURN_TYPES'
            item['checks'].append(('RETURN_NAMES', str(rn[:3]) + ('...' if len(rn) > 3 else '')))
        # 5. FUNCTION
        func_name = getattr(cls, 'FUNCTION', None)
        assert func_name and hasattr(cls, func_name), f'FUNCTION 不存在: {func_name}'
        item['checks'].append(('FUNCTION', func_name))
        # 6. INPUT_TYPES
        inp = cls.INPUT_TYPES()
        assert isinstance(inp, dict), f'INPUT_TYPES 返回非 dict'
        assert 'required' in inp, f'INPUT_TYPES 缺 required'
        item['checks'].append(('INPUT_TYPES', f'req={len(inp.get("required", {}))} opt={len(inp.get("optional", {}))}'))
        # 7. 试运行
        req = inp.get('required', {})
        kwargs = {}
        for k, v in req.items():
            if isinstance(v, tuple) and len(v) >= 2 and isinstance(v[1], dict):
                kwargs[k] = v[1].get('default', '')
            elif isinstance(v, tuple) and len(v) >= 1 and isinstance(v[0], list):
                kwargs[k] = v[0][0] if v[0] else ''
            else:
                kwargs[k] = ''
        # 也加 optional (用 default)
        for k, v in inp.get('optional', {}).items():
            if isinstance(v, tuple) and len(v) >= 2 and isinstance(v[1], dict):
                kwargs[k] = v[1].get('default', '')
        inst = cls()
        result = getattr(inst, func_name)(**kwargs)
        assert isinstance(result, tuple) and len(result) == len(rt), f'build 返回 {len(result)} 值, 期望 {len(rt)}'
        item['checks'].append(('build_call', f'returned {len(result)} values'))
        # PASS
        ok += 1
        item['status'] = 'PASS'
    except Exception as e:
        fail += 1
        item['status'] = 'FAIL'
        item['error'] = f'{type(e).__name__}: {e}'
    results.append(item)

# 汇总
print(f'PASS: {ok} / FAIL: {fail} / 总数: {len(results)}\n')
for r in results:
    if r['status'] == 'PASS':
        print(f'  [OK]   {r["node"]:35s}  {r["class"]}')
    else:
        print(f'  [FAIL] {r["node"]:35s}  {r["error"]}')

print(f'\n=== 总计 {ok}/{len(results)} 通过 ===')
sys.exit(0 if fail == 0 else 1)
