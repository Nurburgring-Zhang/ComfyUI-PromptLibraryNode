import sys, importlib.util
from pathlib import Path
ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("pkg_init", str(ROOT / "__init__.py"))
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)

# 真实场景: 王家卫 2046 雨夜酒店
kwargs = {
    "任务类型": "single_scene",
    "类型": "剧情短片",
    "场景描述": "2046 - 雨夜, 酒店走廊, 男人写小说, 孤独时空",
    "导演风格": "王家卫",
    "情绪节奏": "低 - 悬置",
    "切点策略": "动作中切",
    "长镜占比": 0.6,
    "跳切场景": "敲门声",
    "蒙太奇": "是",
    "静音切": "是",
    "镜头类型": "中景",
    "启用反AI规则": True,
}

# EditingPro
n = pkg.NODE_CLASS_MAPPINGS['EditingPro']()
ret = n.build_edit(**kwargs)
print("=" * 80)
print("EditingPro 输出:")
print("=" * 80)
for i, x in enumerate(ret):
    print("\n[OUTPUT {}] (长度: {})".format(i, len(str(x))))
    print(str(x)[:3000])

# PerformanceDirectionPro
print()
print("=" * 80)
print("PerformanceDirectionPro 输出:")
print("=" * 80)
n2 = pkg.NODE_CLASS_MAPPINGS['PerformanceDirectionPro']()
kwargs2 = {
    "任务类型": "single_scene",
    "类型": "剧情短片",
    "场景描述": "2046 - 雨夜, 酒店走廊, 男人写小说, 孤独时空",
    "导演风格": "王家卫",
    "情绪基调": "孤独",
    "潜文本_情感": "等待与失去",
    "导演意图_观众应感到": "时空交错的怅惘",
    "关键道具": "钢笔, 烟, 打字机",
    "关键参考片": "2046, 花样年华",
    "启用反AI规则": True,
}
ret2 = n2.build_performance(**kwargs2)
for i, x in enumerate(ret2):
    print("\n[OUTPUT {}] (长度: {})".format(i, len(str(x))))
    print(str(x)[:3000])
