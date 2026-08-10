# -*- coding: utf-8 -*-
"""更新测试到 30 节点 + 加 Phase 14 节点清单"""
import os

# test_full_audit.py
with open('test_full_audit.py', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('NODE_CLASS_MAPPINGS 25 节点', 'NODE_CLASS_MAPPINGS 30 节点')
c = c.replace('len(init.NODE_DISPLAY_NAME_MAPPINGS)==25', 'len(init.NODE_DISPLAY_NAME_MAPPINGS)==30')
c = c.replace('25 节点 (实际 %d)' % 25, '30 节点 (实际 %d)')
with open('test_full_audit.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('test_full_audit.py updated')

# test_e2e_full.py
with open('test_e2e_full.py', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('len(init.NODE_CLASS_MAPPINGS) == 25', 'len(init.NODE_CLASS_MAPPINGS) == 30')
c = c.replace('25 节点: 3+4+4+14 拆/专业/附件/环节', '30 节点: 3+4+4+14 拆/专业/附件/环节 + 5 Phase14')
# 在节点列表加 5 个 Phase 14
old = '        "QualityAssurancePro",\n]\nfor n in NODES_25:'
new = '        "QualityAssurancePro",\n        "AssetRegistry", "SpatialLayout", "ActingSkill",\n        "SoundSkill", "IterationPostPro",\n]\nfor n in NODES_25:'
c = c.replace(old, new)
with open('test_e2e_full.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('test_e2e_full.py updated')

# test_phase13_audit.py
with open('test_phase13_audit.py', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('len(init.NODE_CLASS_MAPPINGS) == 25', 'len(init.NODE_CLASS_MAPPINGS) == 30')
c = c.replace('25 节点注册 (实际 %d)' % 25, '30 节点注册 (实际 %d)')
old = '                 "InteractiveDramaPro", "QualityAssurancePro"]:'
new = '                 "InteractiveDramaPro", "QualityAssurancePro",\n                 "AssetRegistry", "SpatialLayout", "ActingSkill",\n                 "SoundSkill", "IterationPostPro"]:'
c = c.replace(old, new)
with open('test_phase13_audit.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('test_phase13_audit.py updated')
