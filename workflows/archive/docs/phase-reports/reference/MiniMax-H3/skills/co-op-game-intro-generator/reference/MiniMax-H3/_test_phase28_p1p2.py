# -*- coding: utf-8 -*-
"""
Phase 28 P1+P2 专项测试 - VersionControlPro / StyleGuidePro / MarketAudiencePro / CleanupPassPro / FormatOutputPro / ProjectArchivePro
"""
import sys
sys.path.insert(0, '.')
import version_control_pro
import style_guide_pro
import market_audience_pro
import cleanup_pass_pro
import format_output_pro
import project_archive_pro

from version_control_pro import VersionControlPro, VersionTree, manage_version, get_tree
from style_guide_pro import StyleGuidePro, generate_style_guide, COLOR_STYLES_5, COLOR_SCHEMES_5, GRADING_TIPS_20
from market_audience_pro import MarketAudiencePro, predict_box_office, GENRE_AUDIENCE_8, RELEASE_PERIODS_5, MARKET_POSITION_3
from cleanup_pass_pro import CleanupPassPro, cleanup_text
from format_output_pro import FormatOutputPro, to_markdown, to_json, to_yaml, to_xml, to_html, to_csv, to_srt
from project_archive_pro import ProjectArchivePro, create_archive

passed, failed = 0, 0
def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
        print("[OK] " + name)
    else:
        failed += 1
        print("[FAIL] " + name)


print("=" * 60)
print("Phase 28 P1+P2 专项测试 - 6 个新节点")
print("=" * 60)

# ============================================================
# VersionControlPro
# ============================================================
print("\n--- VersionControlPro ---")
tree = VersionTree("test_project")
v1 = tree.commit("v1.0", "初始版本", {"director": "王家卫"}, scores={"total": 0.7})
v2 = tree.commit("v1.1", "改进版", {"director": "王家卫", "scene": "hk_neon"}, scores={"total": 0.85}, parent=v1)
check("commit 创建版本", v1 is not None and v2 is not None)
check("head 切换", tree.head == v2)
check("log 数量 == 2", len(tree.log()) == 2)
tree.tag(v2, "v1.0_release")
check("tag 成功", "v1.0_release" in tree.tags)
tree.set_state(v1, "ARCHIVED")
check("set_state 成功", tree.versions[v1]["state"] == "ARCHIVED")
v3 = tree.rollback(v1)
check("rollback 创建新版本", v3 is not None and v3 != v1)
best = tree.get_best("total", 2)
check("get_best 排序", len(best) == 2 and best[0][0] >= best[1][0])

node = VersionControlPro()
result = node.control(项目名="vc_test", 操作="log")
check("VersionControlPro 节点返回 3 元组", len(result) == 3)
check("log 操作历史", "vc_test" in result[2])

# ============================================================
# StyleGuidePro
# ============================================================
print("\n--- StyleGuidePro ---")
check("COLOR_STYLES_5 == 5", len(COLOR_STYLES_5) == 5)
check("COLOR_SCHEMES_5 == 5", len(COLOR_SCHEMES_5) == 5)
check("GRADING_TIPS_20 == 20", len(GRADING_TIPS_20) == 20)

g = generate_style_guide("梦幻", "互补色", "王家卫")
check("generate_style_guide 完整", "调色风格" in g and "配色方案" in g and "full_prompt" in g)
check("full_prompt 非空", len(g["full_prompt"]) > 0)

node = StyleGuidePro()
result = node.guide(调色风格="梦幻", 配色方案="互补色", 导演体系="王家卫")
check("StyleGuidePro 节点返回 4 元组", len(result) == 4)
check("风格指南输出", "梦幻" in result[0])
check("完整 prompt 输出", len(result[1]) > 0)

# ============================================================
# MarketAudiencePro
# ============================================================
print("\n--- MarketAudiencePro ---")
check("GENRE_AUDIENCE_8 == 8", len(GENRE_AUDIENCE_8) == 8)
check("RELEASE_PERIODS_5 == 5", len(RELEASE_PERIODS_5) == 5)
check("MARKET_POSITION_3 == 3", len(MARKET_POSITION_3) == 3)

r = predict_box_office("动作", "暑期档", 0.7, 0.6, 0.5, 0.7, "腰部")
check("predict_box_office 完整", "score" in r and "box_office_estimate_yi" in r and "risk_level" in r and "recommendation" in r)
check("score 0-1 范围", 0 <= r["score"] <= 1)
check("票房预估 > 0", r["box_office_estimate_yi"] > 0)

node = MarketAudiencePro()
result = node.analyze(类型="动作", 档期="暑期档", 市场定位="腰部")
check("MarketAudiencePro 节点返回 4 元组", len(result) == 4)
check("市场分析输出", "动作" in result[0] and "暑期档" in result[0])
check("受众画像输出", "主要" in result[1])
check("档期策略输出", "档期" in result[2])
check("票房预测 JSON", "score" in result[3])

# ============================================================
# CleanupPassPro
# ============================================================
print("\n--- CleanupPassPro ---")
sample = "随着时代的不断发展, 我们要重视这个角色. 这个角色很神秘. 首先, 其次, 最后, 综上所述, 这个人很厉害."
cleaned = cleanup_text(sample)
check("cleanup_text 移除模板表达", "随着" not in cleaned or "综上所述" not in cleaned)
check("cleanup_text 非空", len(cleaned) > 0)

node = CleanupPassPro()
result = node.cleanup(输入文本=sample)
check("CleanupPassPro 节点返回 3 元组", len(result) == 3)
check("清理后文本非空", len(result[0]) > 0)
check("清理统计 JSON", "original_length" in result[1])
check("报告", "清理完成" in result[2])

# ============================================================
# FormatOutputPro
# ============================================================
print("\n--- FormatOutputPro ---")
sample_text = "这是第一行\n这是第二行\n这是第三行"
check("to_markdown", "# 输出" in to_markdown(sample_text))
check("to_json 包装", '"content"' in to_json(sample_text))
check("to_yaml", "content: |" in to_yaml(sample_text))
check("to_xml", "<output>" in to_xml(sample_text))
check("to_html", "<!DOCTYPE html>" in to_html(sample_text))
check("to_csv", '"这是第一行"' in to_csv(sample_text))
check("to_srt", "00:00:00,000" in to_srt(sample_text))

node = FormatOutputPro()
result = node.format(输入文本=sample_text, 格式="markdown")
check("FormatOutputPro 节点返回 2 元组", len(result) == 2)
check("markdown 输出", "# 输出" in result[0])

# ============================================================
# ProjectArchivePro
# ============================================================
print("\n--- ProjectArchivePro ---")
arc = create_archive("test", {"item": "value"}, {"author": "tester"})
check("create_archive ID", "arc_" in arc["archive_id"])
check("create_archive hash", len(arc["content_hash"]) == 32)
check("create_archive size", arc["size_bytes"] > 0)

node = ProjectArchivePro()
result = node.archive(项目名="p_test", 格式="json", 内容1="内容A", 元数据JSON='{"key": "val"}')
check("ProjectArchivePro 节点返回 3 元组", len(result) == 3)
check("归档内容 JSON", '"project_name"' in result[0] and '"p_test"' in result[0])
check("归档 ID", "arc_" in result[1])
check("元信息", "items_count" in result[2])

print()
print("=" * 60)
print("Phase 28 P1+P2 测试: 通过 {} / 失败 {} / 总计 {}".format(passed, failed, passed + failed))
print("=" * 60)
sys.exit(0 if failed == 0 else 1)
