# -*- coding: utf-8 -*-
from director_storyboard_pro import DirectorStoryboardPro

# Acceptance test from task description (using actual INPUT_TYPES param names)
node = DirectorStoryboardPro()
results = {}
for emo in ['loneliness', 'fear', 'warm_regret']:
    out = node.build(
        **{'\u5267\u672c\u6b63\u6587_\u6765\u81ea\u8282\u70b92': '\u7236\u4eb2\u5728\u53a8\u623f, \u96e8\u591c, 1998\u5e74\u54c8\u5c14\u6ee8, \u51c6\u5907\u665a\u996d',
           '\u7075\u9b42_\u4e3b\u5bfc\u60c5\u611f': emo,
           '\u7075\u9b42_\u573a\u666f\u6743\u91cd': 0.8,
           '\u7075\u9b42_\u6b21\u8981\u60c5\u611f': 'none',
           '\u7075\u9b42_\u878d\u5408\u6a21\u5f0f': 'auto',
        },
    )
    results[emo] = out[0]

# All 3 outputs must be different
print('loneliness != fear:', results['loneliness'] != results['fear'])
print('loneliness != warm_regret:', results['loneliness'] != results['warm_regret'])
print('fear != warm_regret:', results['fear'] != results['warm_regret'])
print()

# Check emotion name appears in output
for emo in ['loneliness', 'fear', 'warm_regret']:
    if emo == 'loneliness':
        expected_names = ['Loneliness', '\u5b64\u72ec']
    elif emo == 'fear':
        expected_names = ['Apprehension', '\u5fe7\u8651', '\u6050\u6015', 'Fear', 'Terror']
    else:
        expected_names = ['Warm Regret', '\u6e29\u6696', '\u9057\u61be', 'Warm']
    has = any(n in results[emo] for n in expected_names)
    print(f'{emo} contains emotion name: {has}')

# Check shot 1 is different
print()
print('Shot 1 diff:')
NL = chr(10)
for emo, txt in results.items():
    idx = txt.find('[Shot 1]')
    shot1 = txt[idx:idx+200].replace(NL, ' ')
    print(f'  {emo}: {shot1[:200]}')
