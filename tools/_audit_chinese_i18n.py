# -*- coding: utf-8 -*-
"""全面中文化 + 整体架构重构
- 所有 RETURN_NAMES 改中文
- 所有 input slot 名中文化
- 添加 导演能力总控节点
- UNet/CLIP/VAE 拆开 (3 个原生节点)
- 重做工作流
"""
import sys
sys.path.insert(0, '.')
import __init__ as pkg

# 1. 列出所有英文 RETURN_NAMES
for name, cls in pkg.NODE_CLASS_MAPPINGS.items():
    rn = getattr(cls, 'RETURN_NAMES', None)
    if rn is None: continue
    has_english = any(any(c.isascii() and c.isalpha() for c in str(x)) and not str(x).replace('_','').isalnum() == False for x in rn)
    has_mixed = any('_' in str(x) and any(c.isascii() and c.isalpha() for c in str(x).split('_')[0]) for x in rn)
    english_items = [str(x) for x in rn if any(c.isalpha() and c.isascii() for c in str(x))]
    if english_items:
        print('%s: %s' % (name, english_items))
