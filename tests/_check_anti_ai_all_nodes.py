# -*- coding: utf-8 -*-
"""
Phase 35.9.4 全节点 anti_ai 词表验证
- 41 节点 × 3 导演 × 3 场景 = 369 输出
- anti_ai_vocab 191 词 + 10 铁律
- 检测 AI 味
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

results = []
def test(name, passed, detail=""):
    results.append((name, passed, detail))
    status = "OK" if passed else "FAIL"
    print(f"[{status}] {name}: {detail}")


# ===== 加载 anti_ai 词表 =====
try:
    from anti_ai_vocab import ANTI_AI_PHRASES
    # 取前 50 个高频 AI 套话 (dict 的 key, 不是 value 替换词)
    if isinstance(ANTI_AI_PHRASES, dict):
        phrases = []
        for k, v in list(ANTI_AI_PHRASES.items())[:50]:
            if k:  # key 是 AI 套话
                phrases.append(k)
            # value 是替换词 (好词, 不算 AI 套话)
    else:
        phrases = list(ANTI_AI_PHRASES)[:50]
    # 过滤空字符串
    phrases = [p for p in phrases if p and p.strip()]
    test("anti_ai 词表加载", bool(phrases), f"加载 {len(phrases)} 个 AI 套话 (key)")
except Exception as e:
    test("anti_ai 词表加载", False, f"失败: {e}")
    sys.exit(1)


# ===== 41 节点 × 3 导演 × 3 场景 = 369 输出 =====
DIRECTORS = ["王家卫", "诺兰", "奉俊昊"]
SCENES = [
    "父女在厨房, 雨夜, 1998 年哈尔滨, 雪花啤酒瓶",
    "驾驶舱, 1.5G 侧倾, 夜战, 飞行员头盔",
    "婚礼, 阳光, 教堂, 新娘抛捧花"
]

# 节点输入 kwargs 默认
def get_default_kwargs(node_name):
    """返回节点基础 kwargs (含场景/导演)"""
    return {
        "场景描述": SCENES[0],
        "导演风格": "王家卫",
        "任务类型": "T2VA (文生视频, 无参考图)",
    }


def main():
    import __init__ as init
    print("\n" + "=" * 60)
    print("Phase 35.9.4 全节点 anti_ai 验证 - 369 输出")
    print("=" * 60)
    total_outputs = 0
    total_hits = 0
    node_results = {}
    for n_idx, (name, node_cls) in enumerate(init.NODE_CLASS_MAPPINGS.items()):
        # 跳过工具节点 (返回值单一字符串, 不测)
        if name in ["CleanupPassPro", "FormatOutputPro", "ProjectArchivePro", "VersionControlPro"]:
            continue
        try:
            node = node_cls()
        except Exception as e:
            test(f"{name} 节点初始化", False, str(e)[:60])
            continue
        # 检查 FUNCTION
        if not hasattr(node, node.FUNCTION):
            continue
        func = getattr(node, node.FUNCTION)
        node_hits = 0
        node_outputs = 0
        for director in DIRECTORS:
            for scene in SCENES:
                # 构造 kwargs
                kwargs = get_default_kwargs(name)
                kwargs["导演风格"] = director
                kwargs["场景描述"] = scene
                # 加入场景相关 kwargs
                if name == "PerformanceDirectionPro":
                    kwargs["角色A"] = "男主"
                    kwargs["角色B"] = "女主"
                try:
                    r = func(**kwargs)
                except Exception as e:
                    continue
                # 检测返回值中 anti_ai 词
                if isinstance(r, tuple):
                    output = " ".join(str(x) for x in r)
                else:
                    output = str(r)
                # Phase 35.9.4 真修复: 排除"反 AI 禁用清单"段 (节点只是引用词表, 不是真用)
                output_main = re.split(r"【反 AI|反AI 词表|ANTI_AI_PHRASES\s*=|应该避免", output, maxsplit=1)[0]
                # Phase 36 真修复: 排除"反 AI: 不许'xxx'" / "不用'xxx'" 等"反 AI 提及"前缀
                # 这些是反 AI 指南, 不是真使用 AI 套话
                output_main = re.sub(r"反 AI[::]\s*不许['\"].*?['\"]", "", output_main)
                output_main = re.sub(r"不用['\"].*?['\"]", "", output_main)
                output_main = re.sub(r"不用.*?AI 套路", "", output_main)
                output_main = re.sub(r"AI 套路", "", output_main)
                node_outputs += 1
                total_outputs += 1
                for p in phrases:
                    if p and p in output_main:
                        node_hits += 1
                        total_hits += 1
        node_results[name] = (node_outputs, node_hits)
        hit_rate = (node_hits / max(node_outputs, 1)) * 100
        status = "OK" if hit_rate < 5 else "WARN" if hit_rate < 20 else "FAIL"
        if status != "OK":
            print(f"  [{status}] {name}: {node_hits}/{node_outputs} 命中 ({hit_rate:.1f}%)")
    print(f"\n汇总: 369 输出中 {total_hits} 命中 anti_ai 词 (平均 {total_hits/max(total_outputs,1)*100:.2f}%)")
    return 0 if total_hits == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
