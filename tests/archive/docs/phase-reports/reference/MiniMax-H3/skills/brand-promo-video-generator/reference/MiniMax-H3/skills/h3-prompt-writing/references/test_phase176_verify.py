# -*- coding: utf-8 -*-
"""Phase 17.6 最终验收 — API + 灵魂字段 + 3 情感差异 + 597 测试"""
import sys
sys.path.insert(0, r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")

import __init__ as init
from vertical_short_drama_pro import VerticalShortDramaPro

# 1. API 检查
print("=" * 60)
print("1. API 完整性检查")
print("=" * 60)
n = VerticalShortDramaPro()
print(f"  类名: VerticalShortDramaPro -> {'OK' if 'VerticalShortDramaPro' in init.NODE_CLASS_MAPPINGS else 'FAIL'}")
print(f"  RETURN_TYPES: {n.RETURN_TYPES}")
print(f"  RETURN_NAMES: {n.RETURN_NAMES}")
print(f"  FUNCTION: {n.FUNCTION}")
print(f"  CATEGORY: {n.CATEGORY}")

# 2. 灵魂字段检查
print()
print("=" * 60)
print("2. 灵魂 INPUT_TYPES 字段检查")
print("=" * 60)
schema = n.INPUT_TYPES()
opt = schema.get("optional", {})
required = ["灵魂_主导情感", "灵魂_场景权重", "灵魂_次要情感"]
for k in required:
    in_opt = k in opt
    in_req = k in schema.get("required", {})
    print(f"  {k}: {'optional' if in_opt else 'required' if in_req else 'MISSING!'}")

# 3. 3 情感差异
print()
print("=" * 60)
print("3. 3 情感差异检查 (loneliness / fear / joy)")
print("=" * 60)
base = dict(
    套路_11选1="穿越", 爆款公式_8选1="plateau_cliff",
    反转类型="identity_reveal", 角色弧_7选1="positive_arc",
    余韵强度="level_3_medium", 总集数=80, 单集时长秒=90,
    付费卡点位置_第几集=8, 爽虐甜比例_532="5 爽 / 3 虐 / 2 甜",
    钩子强度_1_10=9, 前3秒冲突类型="身份揭秘",
    对白最大字数=12, 主角性别="女", 画风="现代都市", 受众="女频",
    目标平台="ReelShort", 字幕语言="双语", 启用反AI规则=True,
)
outs = {}
for emo in ["loneliness", "fear", "joy"]:
    kw = dict(base)
    kw["灵魂_主导情感"] = emo
    kw["灵魂_场景权重"] = 0.7
    s, e, p = n.build_short_drama(**kw)
    outs[emo] = (s, e, p)

# 派别应该不同
print()
print("  派别 (system prompt):")
for emo, (s, e, p) in outs.items():
    for line in s.split("\n"):
        if "灵魂派别" in line and "示例" not in line:
            print(f"    {emo:10s} -> {line.strip()}")
            break

# 反转 archetype 应该不同
print()
print("  反转 archetype:")
for emo, (s, e, p) in outs.items():
    for line in e.split("\n"):
        if "第一次反转铺垫" in line:
            print(f"    {emo:10s} -> {line.strip()}")
            break

# 钩子 archetype
print()
print("  钩子 archetype:")
for emo, (s, e, p) in outs.items():
    for line in e.split("\n"):
        if "黄金开篇" in line:
            print(f"    {emo:10s} -> {line.strip()}")
            break

# 哈希三方互不相同
print()
print("  三方互不相同?")
sys_hashes = {emo: hash(outs[emo][0]) for emo in outs}
ep_hashes = {emo: hash(outs[emo][1]) for emo in outs}
pw_hashes = {emo: hash(outs[emo][2]) for emo in outs}
print(f"    system 唯一: {len(set(sys_hashes.values())) == 3}")
print(f"    episode 唯一: {len(set(ep_hashes.values())) == 3}")
print(f"    paywall 唯一: {len(set(pw_hashes.values())) == 3}")

# 4. 默认 (不传灵魂) 仍可工作 — 跟原 API 一致
print()
print("=" * 60)
print("4. 默认模式 (无灵魂参数) 仍可工作")
print("=" * 60)
s, e, p = n.build_short_drama(**base)
print(f"  system 长度: {len(s)}  (要求 > 500)")
print(f"  episode 长度: {len(e)}  (要求 > 500)")
print(f"  paywall 长度: {len(p)}  (要求 > 200)")
print(f"  全部通过? {len(s) > 500 and len(e) > 500 and len(p) > 200}")

# 5. 597 测试套件
print()
print("=" * 60)
print("5. 597 测试套件")
print("=" * 60)
print("  (看下面的脚本输出)")
