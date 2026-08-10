import importlib.util
from pathlib import Path
ROOT = Path(r'D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode')
spec = importlib.util.spec_from_file_location('pkg_init', str(ROOT / '__init__.py'))
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)
n = pkg.NODE_CLASS_MAPPINGS['DirectorSoulNode']()
ret = n.build_soul(
    主导情感='loneliness', 次要情感_1='longing', 次要情感_2='tenderness',
    次要情感_3='remorse', 次要情感_4='nostalgia',
    融合模式='F2_双情感主次融合', 主导权重=0.6, 创造力=0.85, 想象力=0.85,
    艺术表达=0.90, 镜头技巧=0.88, 氛围掌控=0.93, 灵感指数=0.7,
    疲劳指数=0.3, 怀疑指数=0.5, 叛逆指数=0.6,
    导演='王家卫', 场景描述='2046 - 雨夜, 酒店走廊, 男人写小说, 孤独时空',
    故事强度=0.7, 场景进度=0.4,
)
text = str(ret[0])
print('总长度:', len(text))
addons = ['EDITING', 'PERFORMANCE', 'SILENCE', 'COLOR', 'WORLDBUILDING', 'THEME',
          'ART', 'SPATIAL', 'SOUND', 'MUSIC', 'INTENT', 'STORYBOARD', 'CHARACTER', 'QA']
for a in addons:
    found = '===END_{}_ADDON==='.format(a) in text
    print('  {}_ADDON: {}'.format(a, 'OK' if found else 'MISSING'))
