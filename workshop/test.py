import sys
import os
cwd = os.path.dirname(os.getcwd())
sys.path.append(cwd)
import analyst as al
import assistant as at
import messenger as ms
import agent as ag
import trader as tr
import random

# code_list = ms.complete_stock_list()
# random.shuffle(code_list)
# print(code_list)
date_list = ['2012-11-30', '2017-04-14', '2016-01-30']
# smooth_list = [3, 7, 15, 30]
code_list = ['000022', '000625', '600313', '002074', '603979', '600824', '600558']
# date_list = ['2017-04-19']
'''
for date in date_list:
    for smooth in smooth_list:
        ag.list_for_price_deviation(code_list, date, duration=300, smooth=smooth)
'''
# for bar in [0.3, 0.0, 0.5]:
#    tr.diff_line_strategy(code_list, date_list, 300, 7, bar=bar)
# tr.diff_line_double_duration(code_list, date_list, 300, [15, 45])


# ag.list_for_price_deviation(['600750', '600773'], date='2014-07-28', duration=300, smooth=7)
# ag.list_for_price_deviation(['600860', '601008'], date='2010-07-09', duration=300, smooth=7)
ag.list_for_price_deviation(['600519'], date='2017-04-14', duration=300, smooth=7)

