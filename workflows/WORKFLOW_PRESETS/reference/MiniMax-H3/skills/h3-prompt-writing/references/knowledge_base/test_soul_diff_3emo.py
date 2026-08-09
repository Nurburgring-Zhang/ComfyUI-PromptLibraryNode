# -*- coding: utf-8 -*-
"""3 情感差异化验证 — 验收用"""
import sys
sys.path.insert(0, r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")

from vertical_short_drama_pro import VerticalShortDramaPro

n = VerticalShortDramaPro()
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
    print(f"=== {emo} ===")
    print(f"  system 长度={len(s)}  包含'灵魂'? {'灵魂' in s}  包含'派别'? {'派别' in s}")
    print(f"  episode 长度={len(e)}  包含'派别'? {'派别' in e}  包含'情感主调'? {'情感主调' in e}")
    print(f"  paywall 长度={len(p)}  包含'派别'? {'派别' in p}")

print()
print("=== 三情感 system 文本哈希: 三者真的不同? ===")
hashes = {emo: hash(outs[emo][0]) for emo in outs}
print(hashes)
print(f"  互相不同? {len(set(hashes.values())) == 3}")
hashes_e = {emo: hash(outs[emo][1]) for emo in outs}
print("=== episode 哈希 ===")
print(hashes_e)
print(f"  互相不同? {len(set(hashes_e.values())) == 3}")
hashes_p = {emo: hash(outs[emo][2]) for emo in outs}
print("=== paywall 哈希 ===")
print(hashes_p)
print(f"  互相不同? {len(set(hashes_p.values())) == 3}")

# 抓钩子/爽点/反转的关键行做对比
print()
print("=== 钩子原型对比 (来自 episode_template) ===")
for emo, (s, e, p) in outs.items():
    # 找 0-3s 行后面的 "钩子原型"
    for line in e.split("\n"):
        if "钩子原型:" in line or "情感主调" in line or "派别:" in line:
            print(f"  {emo:10s}  {line.strip()[:120]}")
            break

print()
print("=== 爽点策略 (paywall 设计中) ===")
for emo, (s, e, p) in outs.items():
    if "本剧情感主调" in e:
        # 截取前 200 字
        idx = e.find("本剧情感主调")
        print(f"  {emo}: {e[idx:idx+150]}")
        break

print()
print("=== 反转策略 (episode 中) ===")
for emo, (s, e, p) in outs.items():
    if "反转原型" in e or "第一次反转铺垫" in e:
        # 找反转部分
        for i, line in enumerate(e.split("\n")):
            if "第一次反转铺垫" in line or "反转原型" in line:
                print(f"  {emo}: {line.strip()[:120]}")
                break
