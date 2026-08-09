# -*- coding: utf-8 -*-
"""Phase 20 端到端真实剧本验证 - 拿 3 个真实剧本片段跑灵魂节点全流程"""
import sys, os
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from director_soul import soul_inject_simple, get_inspiration_moments

# 3 个真实剧本片段（来自用户之前的工作或公开案例）
SCENARIOS = [
    {
        "name": "1. 《花样年华》走廊擦肩",
        "primary": "loneliness",
        "secondary": ["longing"],
        "scene_weight": 0.7,
        "director": "王家卫",
        "scene_context": "走廊, 1962 年香港, 周慕云与苏丽珍深夜偶遇, 旗袍, 慢镜头, 老歌",
    },
    {
        "name": "2. 《盗梦空间》巴黎爆破",
        "primary": "fear",
        "secondary": ["awe"],
        "scene_weight": 0.95,
        "director": "诺兰",
        "scene_context": "梦中巴黎, 咖啡馆, 楼层折叠爆破, 6 个月实拍, 旋转走廊, IMAX",
    },
    {
        "name": "3. 《步履不停》长子忌日",
        "primary": "warm_regret",
        "secondary": ["tenderness"],
        "scene_weight": 0.5,
        "director": "是枝裕和",
        "scene_context": "日本横滨老宅, 长子忌日, 全家聚会, 母亲做菜, 饭桌长镜, 黄昏",
    },
]

for s in SCENARIOS:
    print("=" * 70)
    print(s["name"])
    print("=" * 70)
    print(f"输入: primary={s['primary']} secondary={s['secondary']} director={s['director']}")
    print(f"场景: {s['scene_context']}")
    print()
    inj, fused, state, dims = soul_inject_simple(
        primary=s["primary"],
        secondary=s["secondary"],
        scene_weight=s["scene_weight"],
        director=s["director"],
        scene_context=s["scene_context"],
    )
    print(f"【灵魂融合结果】")
    print(f"  主导情感: {fused.get('name')}")
    print(f"  强度: {fused.get('intensity')}, 极性: {fused.get('polarity')}, 唤醒度: {fused.get('arousal')}")
    print(f"  融合模式: {fused.get('fusion_mode')}")
    print()
    print(f"【灵魂状态】")
    for k in ['inspiration', 'fatigue', 'doubt', 'rebelliousness', 'mental_state']:
        print(f"  {k}: {state.get(k)}")
    print()
    moments = get_inspiration_moments(fused, s["director"], count=2)
    print(f"【真实灵感时刻】 (匹配 {len(moments)} 条)")
    for i, m in enumerate(moments, 1):
        print(f"  {i}. {m['导演']}《{m['作品']}》- {m['场景']}")
        print(f"     情感: {m['情感核心']} | 镜头: {m['镜头技术']}")
        print(f"     {m['Prompt 片段']}")
    print()
    # 注入字符串长度
    print(f"【完整注入字符串长度】: {len(inj)} 字符")
    print()
