import tushare as ts
import assistant as at
import analyst as al
import messenger as ms
import trader as tr
import matplotlib.pyplot as plt
import os
import numpy as np
import threading
from multiprocessing import Process

code = ['000625', '600313', '002074']
date = ['2017-05-03', '2012-11-30']
duration = 300
smooth = 3

def diff_and_actual_count_strategy(code_list, date_list, bar=0, spots=None, type='combine', length=15, duration=300, discover_mode=True, text_only=False, loose_cut=0.1, gain_cut=0.2):
    for code in code_list:
        for date in date_list:
            try:
                if spots == None:
                    spots = [1/5, 2/5, 3/5, 4/5]
                duration = length + duration
                if type == 'combine':
                    total_count = length * 2
                else:
                    total_count = length
                h = al.PriceDevAna()
                s = tr.StratCarrier(code, date, duration, smooth, discover_mode)
                origin_list = s.origin_list
                criteria_list = h.group_count_detail(origin_list, [bar], type, length, 1)
                s.form_criteria_list(criteria_list)
                s.print_list('criteria')
                def f_buy(i):
                    result = False
                    thres = int(total_count * spots[1])
                    count = 0
                    for k in i['detail']:
                        count = i['detail'][k]
                    if count >= thres:
                        result = True
                    return result
                def f_sell(i):
                    result = False
                    thres = int(total_count * spots[2])
                    count = 0
                    for k in i['detail']:
                        count = i['detail'][k]
                    if count < thres:
                        result = True
                    return result
                def f_reach(i):
                    result = False
                    thres = int(total_count * spots[3])
                    count = 0
                    for k in i['detail']:
                        count = i['detail'][k]
                    if count >= thres:
                        result = True
                    return result
                def f_enter(i):
                    result = False
                    thres = int(total_count * spots[0])
                    count = 0
                    for k in i['detail']:
                        count = i['detail'][k]
                    if count < thres:
                        result = True
                    return result
                s.form_action_list_with_spots(f_buy, f_sell, f_enter, f_reach, loose_cut, gain_cut)
                s.print_list('action')
                name_string = '-'.join([str(int(total_count * i)) for i in spots])
                s.implement(name_string, text_only=text_only)
            except:
                pass

# diff_and_actual_count_strategy([code], [date], duration=300, discover_mode=True)
def diff_and_actual_count_strategy_multi_proccessing(code_list, date_list, bar=0, accept=2/3, type='combine', length=15, duration=300, discover_mode=True, text_only=False, process=5):
    duration = length + duration
    def implement(code, date):
        if type == 'combine':
            total_count = length * 2
        else:
            total_count = length
        h = al.PriceDevAna()
        s = tr.StratCarrier(code, date, duration, smooth, discover_mode)
        origin_list = s.origin_list
        criteria_list = h.group_count_detail(origin_list, [bar], type, length, 1)
        s.form_criteria_list(criteria_list)
        s.print_list('criteria')
        def f_buy(i):
            result = False
            thres = int(total_count * accept)
            count = 0
            for k in i['detail']:
                count = i['detail'][k]
            if count >= thres:
                result = True
            return result
        def f_sell(i):
            result = False
            thres = int(total_count * accept)
            count = 0
            for k in i['detail']:
                count = i['detail'][k]
            if count < thres:
                result = True
            return result
        s.form_action_list(f_buy, f_sell)
        s.print_list('action')
        name_string = str(int(total_count * accept))
        s.implement(name_string, text_only=text_only)
    process_list = []
    for code in code_list:
        for date in date_list:
            process_list.append(Process(target=implement, args=(code, date)))
    for pi in process_list:
        pi.start()
    for pk in process_list:
        pk.join()


# diff_and_actual_count_strategy_multi_proccessing(code, date, 0, 2/3, 'combine', 15, 300, True, False)
# diff_and_actual_count_strategy(code, date, 0, type='combine', spots=[4/10, 5/10, 6/10, 7/10], length=15, duration=300, loose_cut=0.1, gain_cut=0.2, discover_mode=True)
# tr.list_for_price_deviation(['600313'], duration=300)
h = ms.TickData()

code_list = ['002074', '000625']
'''
for code in code_list:
    # h.deposit('002074', '2017-06-02', '2017-06-08', time_sleep=3)
    # h.update(code, time_sleep=3, quick=True)
    h.show_dates('002074')
    tr.list_for_price_deviation([code], date='2017-06-04', duration=100)
'''
h = ms.TickData()
for code in code_list:
    h.update(code)
tr.list_for_price_deviation(code_list, duration=100)





