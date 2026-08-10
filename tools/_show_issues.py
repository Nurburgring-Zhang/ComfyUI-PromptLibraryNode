import json
d = json.load(open('_audit_director.json', encoding='utf-8'))
for node in ['EditingPro', 'ConceptPitchPro', 'PerformanceDirectionPro', 'ColorGradingPro', 'SoundDesignPro', 'MusicScorePro']:
    print('\n=== {} ==='.format(node))
    bad = [r for r in d if r.get('node') == node and 'issues' in r]
    for r in bad:
        print('  [{} {}] score={}, body={}, silence={}, atmo={}, logic={}'.format(
            r['director'], r['film'], r['score'], r.get('body', 0), r.get('silence', 0),
            r.get('atmo', 0), r.get('logic', 0)))
        for iss in r['issues']:
            print('    - {}'.format(iss))
