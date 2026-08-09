import sys
sys.stdout.reconfigure(encoding='utf-8')
from director_intent_pro import DirectorIntentPro
n = DirectorIntentPro()
o = n.build_intent(
    场景类型='对话',
    场景描述='父女厨房雨夜',
    角色A='父亲',
    角色B='女儿',
    灵魂_主导情感='longing',
    灵魂_次要情感_1='remorse',
    灵魂_融合模式='F3_双情感对等融合',
    导演风格='王家卫',
    启用反AI规则=True,
)
s = o[0]

# Check all required sections
checks = {
    '5 维意图': all(k in s for k in ['感受意图', '情感意图', '关系意图', '主题意图', '留白意图']),
    '11 维导演控制': '11 维导演控制' in s,
    '空镜': '空镜' in s,
    '留白': '留白' in s,
    '氛围渲染': '氛围渲染' in s,
    '悬疑': '悬疑' in s,
    '多线': '多线' in s,
    '反转': '反转' in s,
    '高潮': '高潮' in s,
    '余韵': '余韵' in s,
    '推进节奏': '推进节奏' in s,
    '感情控制': '感情控制' in s,
    '角色塑造': '角色塑造' in s,
    '3 留白 + 3 运镜': '3 留白 + 3 运镜' in s,
    '物件留白': '物件留白' in s,
    '时间留白': '时间留白' in s,
    '沉默留白': '沉默留白' in s,
    '推近': '推近' in s,
    '后拉': '后拉' in s,
    '横移': '横移' in s,
    '8 大顶级导演': '8 大顶级导演' in s,
    '15 导演': '15 导演' in s,
    'H3 三大字段': 'H3 三大字段' in s,
    'INTEGRATED_MULTIMODAL_DESCRIPTION': 'INTEGRATED_MULTIMODAL_DESCRIPTION' in s,
    'OVERALL_SOUNDSCAPE': 'OVERALL_SOUNDSCAPE' in s,
    'NON_DIEGETIC_MUSIC': 'NON_DIEGETIC_MUSIC' in s,
    '5 要素架构': '5 要素架构' in s,
    '灵魂深度处理': '灵魂深度处理' in s,
    '灵魂融合层': '灵魂融合层' in s,
    '数据层': '数据层' in s,
    '反 AI 词表': '反 AI' in s,
    '60+ 情感': '60+' in s,
    '10 灵魂维度': '10 灵魂维度' in s,
    '灵魂状态': '灵魂状态' in s,
    '王家卫': '王家卫' in s,
    '诺兰': '诺兰' in s,
    'PTA': 'PTA' in s,
    '奉俊昊': '奉俊昊' in s,
    '黑泽明': '黑泽明' in s,
    '库斯杜力卡': '库斯杜力卡' in s,
    '塔可夫斯基': '塔可夫斯基' in s,
    '约阿希姆': '约阿希姆' in s,
    '权力动态': '权力动态' in s,
    '极性': '极性' in s,
}
total = len(checks)
passed = sum(1 for v in checks.values() if v)
print('通过: {0}/{1}'.format(passed, total))
for k, v in checks.items():
    mark = 'OK' if v else 'FAIL'
    print('  [{0}] {1}'.format(mark, k))

# Check samples output too
print()
print('--- Samples output (output[1]) ---')
s2 = o[1]
checks2 = {
    '15 导演真实意图样本': '15 导演真实意图样本' in s2,
    '8 大顶级导演灵魂签名': '8 大顶级' in s2 or '8 顶级导演灵魂签名' in s2,
    '真实电影案例研究': '真实电影案例研究' in s2,
    '8 导演的 11 维控制': '11 维控制' in s2,
    '8 导演的 60+ 情感使用频率': '60+ 情感使用频率' in s2,
    '8 导演灵魂维度分布': '8 导演的灵魂维度分布' in s2,
    '关键场景模型': '关键场景模型' in s2,
    '反 AI 风格特征': '反 AI 风格特征' in s2,
    '反 AI 词表': '反 AI 词表' in s2,
}
total2 = len(checks2)
passed2 = sum(1 for v in checks2.values() if v)
print('Samples 通过: {0}/{1}'.format(passed2, total2))
for k, v in checks2.items():
    mark = 'OK' if v else 'FAIL'
    print('  [{0}] {1}'.format(mark, k))
