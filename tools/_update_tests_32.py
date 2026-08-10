# -*- coding: utf-8 -*-
"""更新测试到 32 节点"""
import os

files = ["test_full_audit.py", "test_e2e_full.py", "test_phase13_audit.py"]

# 通用替换
for fp in files:
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace("25 节点 (实际 %d)" % 25, "32 节点 (实际 %d)")
    c = c.replace("30 节点 (实际 %d)" % 30, "32 节点 (实际 %d)")
    c = c.replace('len(init.NODE_CLASS_MAPPINGS) == 30', 'len(init.NODE_CLASS_MAPPINGS) == 32')
    c = c.replace('len(init.NODE_CLASS_MAPPINGS)==30', 'len(init.NODE_CLASS_MAPPINGS)==32')
    c = c.replace('len(init.NODE_CLASS_MAPPINGS)==25', 'len(init.NODE_CLASS_MAPPINGS)==32')
    c = c.replace('len(init.NODE_DISPLAY_NAME_MAPPINGS)==30', 'len(init.NODE_DISPLAY_NAME_MAPPINGS)==32')
    c = c.replace('len(init.NODE_DISPLAY_NAME_MAPPINGS)==25', 'len(init.NODE_DISPLAY_NAME_MAPPINGS)==32')
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(c)
    print(f"{fp} updated")

# test_e2e_full.py 节点列表扩展
with open('test_e2e_full.py', 'r', encoding='utf-8') as f:
    c = f.read()
old = '        "SoundSkill", "IterationPostPro",\n]\nfor n in NODES_25:'
new = '        "SoundSkill", "IterationPostPro",\n        "ThirtySecSixAct", "CinematicStudio",\n]\nfor n in NODES_25:'
c = c.replace(old, new)
with open('test_e2e_full.py', 'w', encoding='utf-8') as f:
    f.write(c)
print("test_e2e_full.py 节点列表扩展完成")

# test_phase13_audit.py 节点列表扩展
with open('test_phase13_audit.py', 'r', encoding='utf-8') as f:
    c = f.read()
old = '                 "SoundSkill", "IterationPostPro"]:'
new = '                 "SoundSkill", "IterationPostPro",\n                 "ThirtySecSixAct", "CinematicStudio"]:'
c = c.replace(old, new)
with open('test_phase13_audit.py', 'w', encoding='utf-8') as f:
    f.write(c)
print("test_phase13_audit.py 节点列表扩展完成")
