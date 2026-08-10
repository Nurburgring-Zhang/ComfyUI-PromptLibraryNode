# -*- coding: utf-8 -*-
import re
fp = r'D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode\tools\_gen_workflows_v3.py'
with open(fp, 'r', encoding='utf-8') as f:
    text = f.read()
calls = re.findall(r'wb\.link\(([^)]+)\)', text)
print(f'总 wb.link 调用数: {len(calls)}')
for c in calls:
    parts = [p.strip() for p in c.split(',')]
    if len(parts) >= 4:
        print(f'  src={parts[1]!r}  tgt={parts[3]!r}')
