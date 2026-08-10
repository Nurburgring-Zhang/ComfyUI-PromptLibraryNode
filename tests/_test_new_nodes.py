# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from thirty_sec_six_act import ThirtySecSixAct, build_six_act_30s, SIX_ACT_30S
print('30s 6 段测试:')
print(f'  阶段数: {len(SIX_ACT_30S)}')
for act in SIX_ACT_30S:
    sid = act['id']
    stage = act['stage']
    time = act['time']
    dur = act['duration']
    print(f'    {sid}. {stage} ({time}, {dur}s)')
print()
n = ThirtySecSixAct()
print(f'  节点: {n.RETURN_NAMES}')
print()
print('Cinematic Studio 测试:')
import cinematic_studio as cs
print(f'  23 特效: {len(cs.CINEMATIC_EFFECTS_23)}')
print(f'  模型数: {len(cs.MODEL_REGISTRY)}')
recs = cs.route_model('venom_symbiote', '赛博朋克夜晚', 5, 'zh')
print(f'  路由推荐: {recs}')
m = cs.CinematicStudio()
print(f'  节点: {m.RETURN_NAMES}')

print()
print('=== 测试 build_six_act_30s 输出 ===')
overview = build_six_act_30s()
print(f'长度: {len(overview)} 字符')
print(overview[:1500])
