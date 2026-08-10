# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
content = open(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode\h3_context_ir_node.py", encoding="utf-8").read()
checks = [
    "_WEB_DIRECTOR_PROFILES",
    "_WEB_SCENE_DATABASE",
    "_WEB_QUOTES",
    "director_soul",
    "director_styles",
    "director_real_scripts",
    "director_engine",
    "universal_director_prompt_node",
    "master_director_data",
    "_fallback_output",
    "H3_DIRECTOR_PROFILES_FALLBACK",
]
for c in checks:
    print(f"  {c}: {c in content}")
print()
print(f"file size: {len(content)} chars")
print(f"line count: {len(content.splitlines())}")
