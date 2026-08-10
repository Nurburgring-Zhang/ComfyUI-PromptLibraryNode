# -*- coding: utf-8 -*-
"""
模拟 ComfyUI 前端 LiteGraph 加载节点的完整流程
================================================
1. 读 /object_info 拿 INPUT_TYPES schema
2. 加载工作流 JSON
3. 调 LiteGraph.createNode(type, data) 流程
4. 验证 widgets_values 真的被填到 widget.value
"""
import sys
import json
sys.path.insert(0, '.')
import __init__ as pkg

# 1. 模拟 /object_info
def get_object_info(nodename):
    cls = pkg.NODE_CLASS_MAPPINGS[nodename]
    return {
        "input": cls.INPUT_TYPES(),
        "output": list(getattr(cls, "RETURN_TYPES", ()) or ()),
        "output_name": list(getattr(cls, "RETURN_NAMES", ()) or ()),
        "name": nodename,
        "display_name": nodename,
        "category": getattr(cls, "CATEGORY", ""),
        "function": getattr(cls, "FUNCTION", ""),
    }

# 2. 模拟 LiteGraph 加载
def litegraph_load_node(node_data):
    """完全模拟 ComfyUI 前端 LiteGraph.createNode(type, data) 流程"""
    ntype = node_data["type"]
    info = get_object_info(ntype)

    # 1. LiteGraph.createNode 会 new classObj() — 但实际前端是直接构造
    # 2. 然后调 INPUT_TYPES() 拿 schema
    # 3. 按 schema 创建 widget
    widgets = []
    for fname, fspec in info["input"].get("required", {}).items():
        if isinstance(fspec, tuple) and len(fspec) >= 1:
            t = fspec[0]
            opts = fspec[1] if len(fspec) > 1 and isinstance(fspec[1], dict) else {}
        else:
            t = "STRING"
            opts = {}
        # 简化 widget: 只记 type + name
        widgets.append({
            "name": fname,
            "type": "COMBO" if isinstance(t, list) else str(t).upper(),
            "value": None,  # 默认未填
        })

    # 4. 把 widgets_values 填到 widget.value
    wv = node_data.get("widgets_values", [])
    print('Node: %s, widgets=%d, widgets_values=%d' % (ntype, len(widgets), len(wv)))
    for i, w in enumerate(widgets):
        if i < len(wv):
            w["value"] = wv[i]
        else:
            w["value"] = "MISSING"  # widgets_values 长度不够

    return widgets


# 3. 加载实际工作流 JSON
wf_path = 'workflows/MEGA_TEXT_TO_VIDEO_FILM.json'
with open(wf_path, 'r', encoding='utf-8') as f:
    wf = json.load(f)

issues = []
for n in wf["nodes"]:
    widgets = litegraph_load_node(n)
    for w in widgets:
        if w["value"] is None or w["value"] == "MISSING" or w["value"] == "UNKNOWN":
            issues.append('%s.%s = %r' % (n["type"], w["name"], w["value"]))

print('=' * 70)
print('LiteGraph 加载模拟')
print('=' * 70)
print('节点: %d' % len(wf["nodes"]))
print('问题: %d' % len(issues))
if issues:
    print('=== 问题清单 (前 30) ===')
    for i in issues[:30]:
        print('  %s' % i)
    if len(issues) > 30:
        print('  ... 还有 %d' % (len(issues) - 30))
else:
    print('=== 全部 OK, widgets_values 全部对齐 ===')
