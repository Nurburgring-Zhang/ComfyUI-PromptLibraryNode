# -*- coding: utf-8 -*-
"""最终清理: 清空所有 _*.py 临时脚本 (除保留的)"""
import os

KEEP = {
    "_check_keys.py",          # 节点类检查 (一次性, 但保留)
    "_rebuild_init.py",        # __init__.py 重建 (保留以防)
    "_test_new_nodes.py",      # 新节点验证 (保留)
    "_update_tests.py",        # 27 节点更新
    "_update_tests_32.py",     # 32 节点更新
    "_append_phase14.md",      # Phase 14 报告
    "_final_cleanup.py",       # 自己
}

cwd = os.path.dirname(os.path.abspath(__file__))
os.chdir(cwd)

cleared = 0
for fn in sorted(os.listdir(".")):
    if fn.startswith("_") and fn.endswith(".py") and fn not in KEEP:
        try:
            with open(fn, "w", encoding="utf-8") as f:
                f.write("# -*- coding: utf-8 -*-\n# (临时脚本已清理, 内容不再需要)\n")
            cleared += 1
        except Exception as e:
            print(f"  跳过 {fn}: {e}")

# 也清理 _*.txt
for fn in sorted(os.listdir(".")):
    if fn.startswith("_") and fn.endswith(".txt"):
        try:
            with open(fn, "w", encoding="utf-8") as f:
                f.write("(临时文件已清理)\n")
            cleared += 1
        except Exception as e:
            print(f"  跳过 {fn}: {e}")

print(f"已清空 {cleared} 个临时脚本/文件")
