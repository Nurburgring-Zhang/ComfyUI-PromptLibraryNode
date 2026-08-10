import importlib.util
from pathlib import Path
ROOT = Path(r'D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode')
spec = importlib.util.spec_from_file_location('pkg_init', str(ROOT / '__init__.py'))
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)

for n in ['ConceptPitchPro', 'DirectorStoryboardPro', 'ColorGradingPro', 'DirectorSoulNode', 'AestheticJudgmentPro', 'StyleGuidePro']:
    cls = pkg.NODE_CLASS_MAPPINGS[n]
    it = cls.INPUT_TYPES()
    rn = getattr(cls, 'RETURN_NAMES', None)
    rt = getattr(cls, 'RETURN_TYPES', None)
    print('\n=== {} ==='.format(n))
    print('  RETURN_TYPES: {}'.format(rt))
    print('  RETURN_NAMES: {}'.format(rn))
    print('  required: {}'.format(len(it['required'])))
    print('  optional: {}'.format(len(it.get('optional', {}))))
    print('  required first 8: {}'.format(list(it['required'].keys())[:8]))
