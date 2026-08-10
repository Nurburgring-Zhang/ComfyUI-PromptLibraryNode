"""验证脚本"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import web_research_director_db as db

print('=== 35位导演 ===')
for i, name in enumerate(sorted(db.DIRECTOR_PROFILES.keys()), 1):
    p = db.get_director_profile(name)
    has_all = all(k in p for k in ['core_style', 'techniques', 'scenes_examples', 'anti_ai_warning', 'source'])
    tn = len(p['techniques'])
    sn = len(p['scenes_examples'])
    status = 'OK' if has_all and tn >= 3 and sn >= 2 else 'WARN'
    print(f'{i:2d}. [{status}] {name:12s} tech={tn} scenes={sn}')

print()
print('=== 6维对比 ===')
for name, dims in db.DIRECTOR_SIX_DIM.items():
    scores = [v for k, v in dims.items() if k != chr(0x4F9D) + chr(0x636E)]
    avg = sum(scores) / 6
    print(f'{name}: E{scores[0]} B{scores[1]} R{scores[2]} L{scores[3]} C{scores[4]} T{scores[5]} | avg={avg:.1f}')

print()
print('=== 100场景采样 ===')
for i in [0, 12, 28, 40, 52, 62, 74, 84, 99]:
    s = db.SCENE_DATABASE[i]
    n = s['name']
    r = s['reference']
    print(f'  {i+1:3d}. {n} | {r}')

print()
print('=== 关键样本 ===')
w = db.get_director_profile('王家卫')
print('Wong:', w['core_style'][:60])
print('Anti-AI:', w['anti_ai_warning'][:60])
print('Quote:', db.get_random_quote())
print('Fact:', db.get_random_fact()[:70])
print('雨搜索:', len(db.search_scene('雨')), '个')
