# -*- coding: utf-8 -*-
from market_audience_pro import MarketAudiencePro
from cleanup_pass_pro import CleanupPassPro
from format_output_pro import FormatOutputPro
from project_archive_pro import ProjectArchivePro

print('--- MarketAudiencePro: 真实档期分析 (用 FLOAT) ---')
n = MarketAudiencePro()
ret = n.analyze(
    类型='剧情',
    档期='暑期档',
    市场定位='腰部',
    导演知名度=0.85,
    演员阵容=0.75,
    营销预算=0.65,
    质量评分=0.80,
)
print(f'输出长度: {sum(len(str(x)) for x in ret)} 字符')
for i, x in enumerate(ret):
    print(f'output[{i}]: {str(x)[:200]}')

print()
print('--- CleanupPassPro: 清理含反 AI 词的真实文本 ---')
n = CleanupPassPro()
text = '在这个绝美伦比的画面中, 一道惊艳的光影效果映入眼帘, 精致的细节展示了精湛的工艺, 这是一个史诗级的视觉盛宴'
ret = n.cleanup(
    输入文本=text,
    移除反AI词=True,
    移除重复句=True,
    移除模板表达=True,
    标准化空白=True,
    移除空行=True,
)
print(f'输出长度: {sum(len(str(x)) for x in ret)} 字符')
print(f'输入: {text}')
print(f'输出: {ret[0]}')

print()
print('--- FormatOutputPro: 真实 markdown 格式 ---')
n = FormatOutputPro()
ret = n.format(
    输入文本='第一段内容: 雨夜, 男人独自走在街上',
    格式='markdown',
    标题='剧本 v1',
)
print(f'输出长度: {sum(len(str(x)) for x in ret)} 字符')
for i, x in enumerate(ret):
    print(f'output[{i}]: {str(x)[:200]}')

print()
print('--- ProjectArchivePro: 真实归档 ---')
n = ProjectArchivePro()
ret = n.archive(
    项目名='雨夜咖啡馆_v1',
    格式='zip',
    内容1='第一段内容: 雨夜, 男人独自走在街上',
    内容2='第二段内容: 咖啡馆里她递来一杯拿铁',
    内容3='第三段内容: 两人重新开始对话',
    元数据JSON='{"version": "1.0", "author": "导演"}',
)
print(f'输出长度: {sum(len(str(x)) for x in ret)} 字符')
for i, x in enumerate(ret):
    print(f'output[{i}]: {str(x)[:200]}')
