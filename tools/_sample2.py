import sys, importlib.util
from pathlib import Path
ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("pkg_init", str(ROOT / "__init__.py"))
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)


def show(ntype, kwargs, method):
    print('=' * 80)
    print('{} 输出:'.format(ntype))
    print('=' * 80)
    inst = pkg.NODE_CLASS_MAPPINGS[ntype]()
    ret = getattr(inst, method)(**kwargs)
    for i, x in enumerate(ret):
        print('\n[OUTPUT {}] (长度: {})'.format(i, len(str(x))))
        print(str(x)[:2500])
    print()


# ConceptPitchPro
show('ConceptPitchPro', {
    '任务类型': 'single_scene',
    '类型': '剧情短片',
    '场景描述': '2046 - 雨夜, 酒店走廊, 男人写小说, 孤独时空',
    '导演风格': '王家卫',
    '情绪基调': '孤独',
    '潜文本_情感': '等待与失去',
    '导演意图_观众应感到': '时空交错的怅惘',
    '关键道具': '钢笔, 烟, 打字机',
    '关键参考片': '2046, 花样年华',
    '启用反AI规则': True,
    '灵魂融合情感': 'tender',
    '灵魂融合权重': '0.6',
    '灵魂融合模式': 'auto',
    '灵魂维度JSON': '{}',
    '灵魂状态JSON': '{}',
    '灵魂导演': '王家卫',
}, 'build_concept')

# PerformanceDirectionPro
show('PerformanceDirectionPro', {
    '任务类型': 'single_scene',
    '类型': '剧情短片',
    '场景描述': '2046 - 雨夜, 酒店走廊, 男人写小说, 孤独时空',
    '导演风格': '王家卫',
    '情绪基调': '孤独',
    '潜文本_情感': '等待与失去',
    '导演意图_观众应感到': '时空交错的怅惘',
    '关键道具': '钢笔, 烟, 打字机',
    '关键参考片': '2046, 花样年华',
    '启用反AI规则': True,
}, 'build_performance')

# ColorGradingPro
show('ColorGradingPro', {
    '任务类型': 'single_scene',
    '类型': '剧情短片',
    '场景描述': '2046 - 雨夜, 酒店走廊, 男人写小说, 孤独时空',
    '导演风格': '王家卫',
    '色彩风格': '低饱和度',
    '焦段': '50mm',
    '光圈': 'f2.8',
    '景别': '中景',
    '构图法则': '三分法',
    '主色_60': '冷蓝灰',
    '辅色_30': '暖橘',
    '点缀色_10': '深红',
    '一级调色': 'normal',
    '二级调色': 'normal',
    '创意调色': 'normal',
    '光源类型': '自然光',
    '光影方向': '侧光',
    '色温': '5600K',
    '比例': '16:9',
    '时间': '黄昏',
}, 'build_color')

# SoundDesignPro
show('SoundDesignPro', {
    '任务类型': 'single_scene',
    '类型': '剧情短片',
    '场景描述': '2046 - 雨夜, 酒店走廊, 男人写小说, 孤独时空',
    '导演风格': '王家卫',
    '情绪基调': '孤独',
    '潜文本_情感': '等待与失去',
    '导演意图_观众应感到': '时空交错的怅惘',
    '关键道具': '钢笔, 烟, 打字机',
    '关键参考片': '2046, 花样年华',
    '启用反AI规则': True,
}, 'build_sound')
