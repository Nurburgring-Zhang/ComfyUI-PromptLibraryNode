import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode')
print('=== 测试 __init__.py 全部 import (模拟 ComfyUI 启动) ===')
try:
    import __init__ as pl
    print(f'[OK] __init__ import 成功')
    print(f'  NODE_CLASS_MAPPINGS 节点总数: {len(pl.NODE_CLASS_MAPPINGS)}')
    print(f'  NODE_DISPLAY_NAME_MAPPINGS 节点总数: {len(pl.NODE_DISPLAY_NAME_MAPPINGS)}')
    # DirectorMasteryNode 在不在
    if 'DirectorMasteryNode' in pl.NODE_CLASS_MAPPINGS:
        cls = pl.NODE_CLASS_MAPPINGS['DirectorMasteryNode']
        print(f'  [OK] DirectorMasteryNode 已注册: {cls.__name__}')
        print(f'    CATEGORY: {cls.CATEGORY}')
        print(f'    RETURN_NAMES: {cls.RETURN_NAMES}')
        print(f'    DISPLAY_NAME: {pl.NODE_DISPLAY_NAME_MAPPINGS.get("DirectorMasteryNode", "(none)")!r}')
    else:
        print('  [FAIL] DirectorMasteryNode 没注册！')
    # 列出所有 PromptLibrary 节点 (按 CATEGORY 分类)
    print()
    print('=== 所有 PromptLibrary/* 节点按 CATEGORY 分类 ===')
    by_cat = {}
    for name, cls in pl.NODE_CLASS_MAPPINGS.items():
        cat = getattr(cls, 'CATEGORY', '(无)')
        if 'PromptLibrary' in cat:
            by_cat.setdefault(cat, []).append(name)
    for cat in sorted(by_cat.keys()):
        nodes = by_cat[cat]
        print(f'\n[{cat}] ({len(nodes)} 节点)')
        for n in sorted(nodes):
            display = pl.NODE_DISPLAY_NAME_MAPPINGS.get(n, n)
            print(f'  - {n} → {display[:50]}')
except Exception as e:
    import traceback
    print(f'[FAIL] __init__ import 失败: {e}')
    traceback.print_exc()
