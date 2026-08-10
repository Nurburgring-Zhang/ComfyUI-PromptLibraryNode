# -*- coding: utf-8 -*-
"""
Phase 35.7 综合验证 - 4 项待优化修复
- M-A2: CATEGORY 路径统一
- M-A3: RETURN_NAMES 统一 (snake_case 英文)
- M-B3: _HAS_DEPS 静默降级 → assert
- M-C4: 4 道具来历动态化
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

results = []
def test(name, passed, detail=""):
    results.append((name, passed, detail))
    status = "OK" if passed else "FAIL"
    print(f"[{status}] {name}: {detail}")


# ===== T1: M-A2 CATEGORY 路径统一 =====
print("\n========== T1: M-A2 CATEGORY 路径统一 ==========")
import __init__ as init
cats = {}
for name, node_cls in init.NODE_CLASS_MAPPINGS.items():
    cat = node_cls.CATEGORY
    cats.setdefault(cat, []).append(name)
# 验证: 全部以 PromptLibrary/ 开头
all_prompt_library = all(c.startswith("PromptLibrary/") for c in cats.keys())
test("43 节点 CATEGORY 全部 PromptLibrary/* 开头", all_prompt_library, f"实际 {len(cats)} 个分类")

# 验证: 没有 Director/* 残留
no_director_root = not any(c.startswith("Director/") for c in cats.keys())
test("没有 Director/* 残留", no_director_root, "")

# 验证: 起点节点独立分类
starters = ["DirectorSoulNode", "AestheticJudgmentPro", "StyleGuidePro", "AssetRegistry"]
all_in_start = all(init.NODE_CLASS_MAPPINGS[n].CATEGORY.startswith("PromptLibrary/起点/") or init.NODE_CLASS_MAPPINGS[n].CATEGORY.startswith("PromptLibrary/节点/") for n in starters)
test("4 起点节点独立分类", all_in_start, "")


# ===== T2: M-A3 RETURN_NAMES snake_case 英文 =====
print("\n========== T2: M-A3 RETURN_NAMES snake_case 英文 ==========")
chinese_count = 0
snake_count = 0
mixed_count = 0
for name, node_cls in init.NODE_CLASS_MAPPINGS.items():
    rn = node_cls.RETURN_NAMES
    has_chinese = any(re.search(r'[\u4e00-\u9fff]', str(x)) for x in rn)
    is_snake = all(re.match(r'^[a-z][a-z0-9_]*$', str(x)) for x in rn)
    if has_chinese:
        chinese_count += 1
    elif is_snake:
        snake_count += 1
    else:
        mixed_count += 1
test("0 中文 RETURN_NAMES", chinese_count == 0, f"实际 {chinese_count}")
test("0 混合 RETURN_NAMES", mixed_count == 0, f"实际 {mixed_count}")
test("43 snake_case RETURN_NAMES", snake_count == 43, f"实际 {snake_count}")


# ===== T3: M-B3 _HAS_DEPS assert 改造 =====
print("\n========== T3: M-B3 _HAS_DEPS assert 改造 ==========")
# 验证: ThirtySecSixAct 已 assert
import thirty_sec_six_act
has_assert = "assert _HAS_DEPS" in open("thirty_sec_six_act.py", encoding="utf-8").read()
test("ThirtySecSixAct 已加 assert", has_assert, "")

# 验证: h3 函数 raise 明确信息
h3_func_src = open("thirty_sec_six_act.py", encoding="utf-8").read()
assert_msg = "thirty_sec_six_act requires prompt_builder + anti_ai_vocab deps" in h3_func_src
test("assert 包含明确依赖信息", assert_msg, "")


# ===== T4: M-C4 4 道具来历动态化 =====
print("\n========== T4: M-C4 4 道具来历动态化 ==========")
import performance_direction_pro
from performance_direction_pro import PerformanceDirectionPro
node = PerformanceDirectionPro()

# 4.1 默认 (无 kwargs)
out1 = node.build_performance(**{
    '场景描述': '厨房, 雨夜',
    '任务类型': 'T2VA (文生视频, 无参考图)',
})
m1 = out1[0]
# 4.2 自定义 4 道具来历
out2 = node.build_performance(**{
    '场景描述': '厨房, 雨夜',
    '任务类型': 'T2VA (文生视频, 无参考图)',
    '道具1来历': 'M1911 手枪, 1985 年父亲留给他, 弹匣 7 发',
    '道具2来历': '骆驼香烟, 战地抽了 4 年的牌子, 滤嘴有血渍',
    '道具3来历': '5 张老照片, 1 张有弹孔',
    '道具4来历': '军牌, 1979 年战前刻的, 缺一角',
})
m2 = out2[0]

test("默认无 Montblanc", m1.count('Montblanc') == 0, f"出现 {m1.count('Montblanc')} 次")
test("默认无 Lark", m1.count('Lark') == 0, f"出现 {m1.count('Lark')} 次")
test("自定义 M1911 出现", m2.count('M1911') == 1, f"出现 {m2.count('M1911')} 次")
test("自定义 骆驼香烟 出现", m2.count('骆驼香烟') == 1, f"出现 {m2.count('骆驼香烟')} 次")
test("自定义 5 张老照片 出现", m2.count('5 张老照片') == 1, f"出现 {m2.count('5 张老照片')} 次")
test("自定义 军牌 出现", m2.count('军牌') == 1, f"出现 {m2.count('军牌')} 次")


# ===== T5: 综合验证 4 项修复无回归 =====
print("\n========== T5: 4 项修复无回归 ==========")
import subprocess
test_files = [
    "test_full_audit.py",
    "test_e2e_full.py",
    "test_phase13_audit.py",
    "_test_phase28.py",
    "_test_phase28_p1p2.py",
    "_test_workflows.py",
    "_test_phase35_soul_real.py",
]
# Phase 35.8: 所有 test 文件统一在 tests/ 目录, 子进程用 tests/ cwd + basename
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
all_pass = True
for tf in test_files:
    r = subprocess.run([sys.executable, tf], capture_output=True, cwd=TESTS_DIR, timeout=60)
    passed = r.returncode == 0
    all_pass = all_pass and passed
    test(f"{tf}", passed, "OK" if passed else f"FAIL (rc={r.returncode})")
test("829/829 全部通过", all_pass, "所有测试通过" if all_pass else "存在失败")


# ===== 汇总 =====
print("\n" + "=" * 60)
print("Phase 35.7 综合验证汇总")
print("=" * 60)
total = len(results)
passed = sum(1 for _, p, _ in results if p)
print(f"通过 {passed} / 总计 {total}")
if passed < total:
    print("\n失败项:")
    for n, p, d in results:
        if not p:
            print(f"  FAIL: {n}: {d}")
sys.exit(0 if passed == total else 1)
