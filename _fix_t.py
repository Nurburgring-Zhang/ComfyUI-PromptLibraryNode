# -*- coding: utf-8 -*-
import sys
files = ['test_full_audit.py', 'test_e2e_full.py', 'test_phase13_audit.py']
for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    c2 = c
    c2 = c2.replace('33 节点', '34 节点')
    c2 = c2.replace('==33)', '==34)')
    c2 = c2.replace('==33,', '==34,')
    if c2 != c:
        with open(f, 'w', encoding='utf-8') as fp:
            fp.write(c2)
        print('Updated', f)
    else:
        print('No change to', f)
