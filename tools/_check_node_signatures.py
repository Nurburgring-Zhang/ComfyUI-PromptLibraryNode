# -*- coding: utf-8 -*-
"""检查所有节点的 INPUT_TYPES / RETURN_TYPES / RETURN_NAMES / CATEGORY / FUNCTION"""
import sys
sys.path.insert(0, '.')
import __init__ as pkg

results = []
for name, cls in pkg.NODE_CLASS_MAPPINGS.items():
    try:
        it = cls.INPUT_TYPES()
        rt = getattr(cls, 'RETURN_TYPES', ())
        rn = getattr(cls, 'RETURN_NAMES', ())
        cat = getattr(cls, 'CATEGORY', '')
        fn = getattr(cls, 'FUNCTION', '')
        results.append({
            'name': name,
            'req': len(it.get('required', {})),
            'opt': len(it.get('optional', {})),
            'hid': len(it.get('hidden', {})),
            'out': len(rt),
            'rn_ok': (len(rn) == len(rt)) if rn else None,
            'cat': cat,
            'fn': fn,
            'has_error': False,
        })
    except Exception as e:
        results.append({'name': name, 'error': str(e)[:120], 'has_error': True})

total = len(results)
errors = [r for r in results if r['has_error']]
ok = [r for r in results if not r['has_error']]
print('=== 节点签名检查 ===')
print('总计: %d 节点, 错误: %d, OK: %d' % (total, len(errors), len(ok)))
print()
for r in ok:
    flag = '' if r['rn_ok'] else ' ⚠️ RN不匹配'
    print('  %-30s | req=%2d opt=%2d | out=%d%s | fn=%s | cat=%s' % (
        r['name'], r['req'], r['opt'], r['out'], flag, r['fn'], r['cat']))
print()
print('=== 错误节点 ===')
for r in errors:
    print('  ❌ %s: %s' % (r['name'], r.get('error', '')))
