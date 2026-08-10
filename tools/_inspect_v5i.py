"""Phase 36.6 v5i: 验证 WORKFLOW_FILM_PRODUCTION.json 链接完整性"""
import json

with open('workflows/WORKFLOW_FILM_PRODUCTION.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

links = data.get('links', [])
print(f'WORKFLOW_FILM_PRODUCTION links 总数: {len(links)}')

for n in data.get('nodes', []):
    if 'CinematicStudio' in n.get('type', ''):
        print(f'CinematicStudio node id: {n["id"]}')
        print(f'  输入 input 数量: {len(n.get("inputs", []))}')
        for inp in n.get('inputs', []):
            print(f'    {inp.get("name")}: link {inp.get("link")}')
