# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
import __init__ as pkg
cls = pkg.NODE_CLASS_MAPPINGS['WorldBuildingPro']
opt = cls.INPUT_TYPES().get('optional', {})
print('WorldBuildingPro.灵魂addon in optional:', '灵魂addon' in opt)
print('Optional keys:', list(opt.keys())[:5])
print()
cls2 = pkg.NODE_CLASS_MAPPINGS['ConceptPitchPro']
opt2 = cls2.INPUT_TYPES().get('optional', {})
print('ConceptPitchPro.灵魂addon in optional:', '灵魂addon' in opt2)
