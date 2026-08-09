import os
# 修复 4 个测试文件 - dirname 两次
for f in ['test_e2e_full.py', 'test_full_audit.py', 'test_phase13_audit.py', 'test_phase176_verify.py']:
    with open(f, 'r', encoding='utf-8') as h:
        content = h.read()
    old = "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))"
    new = "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))"
    content = content.replace(old, new)
    with open(f, 'w', encoding='utf-8') as h:
        h.write(content)
    print('Fixed:', f)
