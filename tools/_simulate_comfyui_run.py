# -*- coding: utf-8 -*-
"""
模拟 ComfyUI 真实调用方式, 验证每个节点能真跑通:
1. 从 INPUT_TYPES 拿所有 required + optional 字段
2. 用每个字段的 default 值构造 kwargs
3. 调 cls.FUNCTION(**kwargs)
4. 检查返回值数量 == RETURN_TYPES 数量
5. 每个返回值都能 str() (字符串/张量/字典)

完全模拟 ComfyUI 内部 nodes.py 的 execute() 流程.
"""
import sys
sys.path.insert(0, '.')
import __init__ as pkg

OK = 0
FAIL = []
NO_FN = []
NO_DEF = []

for name, cls in pkg.NODE_CLASS_MAPPINGS.items():
    fn_name = getattr(cls, 'FUNCTION', None)
    if not fn_name or not hasattr(cls, fn_name):
        NO_FN.append(name)
        continue
    fn = getattr(cls, fn_name)
    if not callable(fn):
        NO_FN.append(name)
        continue

    # 真正实例化 (ComfyUI 内部就是这么干的)
    try:
        instance = cls()
    except Exception as e:
        FAIL.append((name, 'InitError: %s' % str(e)[:200], fn_name))
        continue

    # 拿 input schema
    it = cls.INPUT_TYPES()
    required = it.get('required', {})
    optional = it.get('optional', {})

    # 构造默认值 kwargs
    kwargs = {}
    has_no_default = []
    for kind, fields in [('required', required), ('optional', optional)]:
        for fname, fspec in fields.items():
            if isinstance(fspec, tuple) and len(fspec) >= 1:
                t = fspec[0]
                opts = fspec[1] if len(fspec) > 1 and isinstance(fspec[1], dict) else {}
            else:
                t = 'STRING'
                opts = {}

            # COMBO 必有 default
            if isinstance(t, list):
                if not t:
                    has_no_default.append((fname, 'COMBO empty'))
                    continue
                kwargs[fname] = t[0]
            else:
                tname = str(t).upper()
                if 'default' in opts:
                    kwargs[fname] = opts['default']
                elif tname == 'INT':
                    mn = opts.get('min', 0)
                    mx = opts.get('max', 100)
                    kwargs[fname] = (mn + mx) // 2
                elif tname == 'FLOAT':
                    mn = opts.get('min', 0.0)
                    mx = opts.get('max', 1.0)
                    kwargs[fname] = (mn + mx) / 2
                elif tname == 'BOOLEAN':
                    kwargs[fname] = opts.get('default', False) if 'default' in opts else False
                else:
                    # STRING 没 default → 用 ""
                    kwargs[fname] = opts.get('default', '') if 'default' in opts else ''

    # 真正调用 (instance.FUNCTION(**kwargs))
    try:
        out = fn(instance, **kwargs)
    except TypeError as e:
        # 函数签名对不上
        FAIL.append((name, 'TypeError: %s' % str(e)[:200], fn_name))
        continue
    except Exception as e:
        # 节点逻辑报错 — ComfyUI 里也会卡住
        FAIL.append((name, 'RuntimeError: %s' % str(e)[:200], fn_name))
        continue

    # 检查返回值数量
    expected = len(getattr(cls, 'RETURN_TYPES', ()) or ())
    if isinstance(out, dict):
        actual = len(out)
    elif isinstance(out, (tuple, list)):
        actual = len(out)
    else:
        actual = 1

    if actual != expected:
        FAIL.append((name, 'RETURN 数量不匹配: 实际=%d 期望=%d' % (actual, expected), fn_name))
        continue

    # 检查每个返回值可序列化 (str)
    if isinstance(out, dict):
        for k, v in out.items():
            try:
                str(v)[:100]
            except Exception as e:
                FAIL.append((name, 'RETURN[%s] 不可 str: %s' % (k, e), fn_name))
                break
        else:
            OK += 1
    elif isinstance(out, (tuple, list)):
        for i, v in enumerate(out):
            try:
                str(v)[:100]
            except Exception as e:
                FAIL.append((name, 'RETURN[%d] 不可 str: %s' % (i, e), fn_name))
                break
        else:
            OK += 1
    else:
        try:
            str(out)[:100]
            OK += 1
        except Exception as e:
            FAIL.append((name, 'RETURN 不可 str: %s' % e, fn_name))

print('=' * 70)
print('ComfyUI 真实调用模拟 (FUNCTION 真正跑一遍)')
print('=' * 70)
print('总计: 43 节点')
print('OK: %d' % OK)
print('FAIL: %d' % len(FAIL))
print('NO_FN: %d' % len(NO_FN))
print()
if FAIL:
    print('=== 失败节点 ===')
    for name, err, fn in FAIL:
        print('  [FAIL] %s (fn=%s)' % (name, fn))
        print('     %s' % err)
if NO_FN:
    print('=== 无 FUNCTION ===')
    for n in NO_FN:
        print('  [NO_FN] %s' % n)

print()
print('=' * 70)
print('OK 节点: %d / 43' % OK)
print('=' * 70)
