# -*- coding: utf-8 -*-
"""
Phase 28 P0 专项测试 - AestheticJudgmentPro + scene_library
"""
import os, sys
# Phase 35.8: 移到 tests/ 后用上级目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import scene_library
import aesthetic_judgment_pro
from scene_library import get_stats, get_scenes_by_director, get_scenes_by_type, scene_to_prompt
from aesthetic_judgment_pro import (
    AestheticJudgmentPro, AESTHETIC_PRINCIPLES_8, DIRECTOR_COLOR_SYSTEMS_6,
    CINEMATOGRAPHY_5, judge_aesthetic,
)

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
print("Phase 28 P0 专项测试 - AestheticJudgmentPro + scene_library")
print("=" * 60)

# ============================================================
# 场景库测试
# ============================================================
print("\n--- 场景库 (scene_library) ---")
s = get_stats()
check("场景库总数 >= 100 (实际 {})".format(s["total"]), s["total"] >= 100)
check("场景库类型数 == 8", s["types_count"] == 8)
check("STUDIO_INTERIOR 至少 10 个", s["by_type"].get("STUDIO_INTERIOR", 0) >= 10)
check("NATURE_EXTERIOR 至少 15 个", s["by_type"].get("NATURE_EXTERIOR", 0) >= 15)
check("URBAN_EXTERIOR 至少 20 个", s["by_type"].get("URBAN_EXTERIOR", 0) >= 20)
check("URBAN_INTERIOR 至少 15 个", s["by_type"].get("URBAN_INTERIOR", 0) >= 15)
check("PERIOD_FILM_LOCATION 至少 10 个", s["by_type"].get("PERIOD_FILM_LOCATION", 0) >= 10)
check("VIRTUAL_SCENE 至少 8 个", s["by_type"].get("VIRTUAL_SCENE", 0) >= 8)
check("PSYCHE_SPACE 至少 5 个", s["by_type"].get("PSYCHE_SPACE", 0) >= 5)
check("DREAM_MEMORY 至少 5 个", s["by_type"].get("DREAM_MEMORY", 0) >= 5)

# 6 大导演场景匹配
for d in ["王家卫", "侯孝贤", "是枝裕和", "塔可夫斯基", "诺兰", "陈凯歌", "韦斯·安德森", "宫崎骏", "李安", "黑泽明"]:
    scenes = get_scenes_by_director(d)
    check("导演 {} 场景匹配 ({} 个)".format(d, len(scenes)), len(scenes) >= 1)

# 场景字段完整
hk = scene_library.get_scene_by_id("urban_hk_neon_street")
check("urban_hk_neon_street 字段完整", hk is not None and all(k in hk for k in ["id", "name", "type", "desc", "light", "color", "lens", "sound", "ref", "mood"]))

# 场景转 prompt
p = scene_to_prompt(hk)
check("scene_to_prompt 输出", len(p) > 100 and "【" in p)

# ============================================================
# 审美判断测试
# ============================================================
print("\n--- 审美判断 (AestheticJudgmentPro) ---")

# 8 美学原则
check("AESTHETIC_PRINCIPLES_8 == 8 个", len(AESTHETIC_PRINCIPLES_8) == 8)
for p_name in ["1_调和", "2_主题", "3_变化", "4_平衡", "5_连贯", "6_对称", "7_比例", "8_韵律"]:
    check("原则 {} 存在".format(p_name), p_name in AESTHETIC_PRINCIPLES_8)

# 6 导演色彩体系
check("DIRECTOR_COLOR_SYSTEMS_6 == 6 个", len(DIRECTOR_COLOR_SYSTEMS_6) == 6)
for d in ["王家卫", "韦斯·安德森", "陈凯歌", "诺兰", "塔可夫斯基", "黑泽明"]:
    check("导演体系 {} 存在".format(d), d in DIRECTOR_COLOR_SYSTEMS_6)

# 5 维摄影指导
check("CINEMATOGRAPHY_5 == 5 个", len(CINEMATOGRAPHY_5) == 5)

# 评分函数 - 6 导演
test_cases = [
    ("王家卫 重庆森林 霓虹 雨夜 孤独", "王家卫"),
    ("韦斯·安德森 布达佩斯 对称 千禧粉", "韦斯·安德森"),
    ("陈凯歌 妖猫传 唐代 红 金", "陈凯歌"),
    ("诺兰 盗梦空间 冷色调 高对比", "诺兰"),
    ("塔可夫斯基 长镜头 诗意 水", "塔可夫斯基"),
    ("黑泽明 七武士 武士道 动态构图", "黑泽明"),
]
for text, expected_director in test_cases:
    r = judge_aesthetic(input_text=text, director="")
    detected = r["directors"][0] if r["directors"] else ""
    check("检测导演 {} (输入: {})".format(expected_director, text[:20]), detected == expected_director)

# 场景自动匹配
r = judge_aesthetic(input_text="重庆森林 香港 霓虹")
check("场景自动匹配 (香港霓虹)", r["scene_match"] is not None and "hk" in r["scene_match"]["id"].lower())

# 评分总分
r = judge_aesthetic(input_text="对称 调和 韵律 主题")
check("8 原则总分 0-1 范围 (实际 {})".format(r["total"]), 0.0 <= r["total"] <= 1.0)

# 节点类测试
check("INPUT_TYPES 有 '输入描述'", "输入描述" in AestheticJudgmentPro.INPUT_TYPES()["required"])
check("INPUT_TYPES 有 '导演风格'", "导演风格" in AestheticJudgmentPro.INPUT_TYPES()["required"])
check("INPUT_TYPES 有 '场景类型'", "场景类型" in AestheticJudgmentPro.INPUT_TYPES()["required"])
check("RETURN_TYPES 是 6 元组", len(AestheticJudgmentPro.RETURN_TYPES) == 6)
check("FUNCTION = judge", AestheticJudgmentPro.FUNCTION == "judge")
check("CATEGORY = Director/Aesthetic", AestheticJudgmentPro.CATEGORY == "Director/Aesthetic")

# 节点实际调用测试
node = AestheticJudgmentPro()
result = node.judge(
    输入描述="王家卫重庆森林 霓虹街道 雨夜 孤独",
    导演风格="auto",
    场景类型="auto",
)
check("节点调用返回 6 元组", len(result) == 6)
check("节点判断非空", len(result[0]) > 50)
check("8 原则评分是 JSON", "{" in result[1] and "}" in result[1])
check("色彩体系 JSON", "director" in result[2])
check("场景匹配", len(result[3]) > 30)
check("摄影指导 JSON", "构图" in result[4])
check("色彩心理学 JSON", "[" in result[5] or "]" in result[5])

print()
print("=" * 60)
print("Phase 28 P0 测试: 通过 {} / 失败 {} / 总计 {}".format(passed, failed, passed + failed))
print("=" * 60)
sys.exit(0 if failed == 0 else 1)
