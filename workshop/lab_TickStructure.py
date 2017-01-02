import tushare as ts
import assistant as at
import analyst as al
import messenger as ms
import matplotlib.pyplot as plt
import os

def tick_structure(code, date, bar):
    # Subset big and small
    def subset_big_and_small(tick, thread, type):
        if type == 'big':
            return tick[tick.amount >= thread]
        if type == 'small':
            return tick[tick.amount < thread]
    # Subset buy and sell
    def subset_buy_and_sell(tick, type):
        if type == 'buy':
            return tick[tick.type == '买盘']
        if type == 'sell':
            return tick[tick.type == '卖盘']
    try:
        tick = ms.get_tick_data(code, date)
        thread = int(tick.amount.quantile(1 - bar))
        outstanding = ms.get_stock_outstanding(code)
        total_volume = tick.volume.sum() * 100
        turnover = total_volume / outstanding * 100
        big = subset_big_and_small(tick, thread, 'big')
        small = subset_big_and_small(tick, thread, 'small')
        big_buy_volume = subset_buy_and_sell(big, 'buy').volume.sum()
        big_sell_volume = subset_buy_and_sell(big, 'sell').volume.sum()
        small_buy_volume = subset_buy_and_sell(small, 'buy').volume.sum()
        small_sell_volume = subset_buy_and_sell(small, 'sell').volume.sum()
        big_buy_ratio = float(big_buy_volume / big_sell_volume)
        small_buy_ratio = float(small_buy_volume / small_sell_volume)
        content_raw = [thread, turnover, big_buy_ratio, small_buy_ratio]
        content = [date] + [round(i, 2) for i in content_raw]
        return content

    except: return None

def tick_structure_filter(tick_struc, filter = None):
    def all_true(list):
        count = 0
        for i in range(len(list)):
            if list[i] == True:
                count += 1
                continue
            else:
                break
        if count == len(list):
            return True
        else:
            return False
    try:
        if filter != None:
            criteria_list = [
            tick_struc[2] > filter['turnover'],
            tick_struc[3] > filter['big_buy_ratio'],
            tick_struc[4] < filter['small_buy_ratio'],
            ]
            if all_true(criteria_list):
                return tick_struc
            else:
                return None
        else:
            return tick_struc
    except: return None

def tick_structure_to_list(code_list, days, filter, bar, start_date = ''):
    try:
        for code in code_list:
            struc_list = []
            days_list = at.opening_days(code, days, start_date)
            for day in days_list:
                tick_struc = tick_structure(code, day, bar)
                fil_tick_struc = tick_structure_filter(tick_struc, filter)
                if fil_tick_struc != None:
                    struc_list.append(fil_tick_struc)
            if len(struc_list) > 0:
                # path = os.path.join(os.getcwd(), 'list/%s.txt'%code)
                with open('%s.txt'%code, 'w') as f:
                    formatted_line = []
                    for line in struc_list:
                        line = str(line)
                        mark_list = ['[', ']', '\'']
                        for mark in mark_list:
                            line = line.replace(mark, '')
                        formatted_line.append(line + '\n')
                    f.writelines(formatted_line)
    except: pass

filter = {'turnover': 10, 'big_buy_ratio': 1.5, 'small_buy_ratio': 1.3}
code_list = ['601116']
tick_structure_to_list(code_list, 50, filter, 0.1)