import json
d = json.load(open('WORKFLOW_END_TO_END.json', encoding='utf-8'))
print('=== DirectorSoulNode (起点) ===')
n = d['nodes'][0]
print('type:', n['type'])
print('id:', n['id'])
print()
print('Inputs ({} 个):'.format(len(n['inputs'])))
for i, inp in enumerate(n['inputs']):
    w = inp.get('widget')
    if isinstance(w, dict):
        w = w.get('value', '')
    w_str = str(w)[:30] if w else ''
    print('  [{}] name={} type={} link={} widget={}'.format(i, inp['name'], inp['type'], inp.get('link'), w_str))
print()
print('Outputs ({} 个):'.format(len(n['outputs'])))
for i, out in enumerate(n['outputs']):
    print('  [{}] name={} type={} color={} links={}'.format(i, out['name'], out['type'], out.get('color', '?'), out.get('links', [])))

print()
print('=== ColorGradingPro (中间态) ===')
n = next(x for x in d['nodes'] if x['type'] == 'ColorGradingPro')
print('type:', n['type'])
print()
print('Inputs ({} 个, 找 addon):'.format(len(n['inputs'])))
addon_found = []
for i, inp in enumerate(n['inputs']):
    if 'addon' in inp['name']:
        addon_found.append((i, inp['name'], inp.get('link')))
        print('  [{}] name={} link={} <- 接上游'.format(i, inp['name'], inp.get('link')))
print()
print('addon slots 接入数: {}/6'.format(sum(1 for _, _, l in addon_found if l is not None)))
print()
print('Outputs ({} 个, 真实名字):'.format(len(n['outputs'])))
for i, out in enumerate(n['outputs']):
    print('  [{}] name={} type={} color={}'.format(i, out['name'], out['type'], out.get('color', '?')))
