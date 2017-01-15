import tushare as ts
import assistant as at
import analyst as al
import messenger as ms
import matplotlib.pyplot as plt
import random

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
        # thread = int(tick.amount.quantile(1 - bar))
        thread = tick.sort_values('amount', ascending = False).head(10)['amount'].iloc[-1]
        outstanding = ms.get_stock_outstanding(code)
        total_volume = tick.volume.sum() * 100
        turnover = total_volume / outstanding * 100
        big = subset_big_and_small(tick, thread, 'big')
        small = subset_big_and_small(tick, thread, 'small')
        big_buy_volume = subset_buy_and_sell(big, 'buy').volume.sum()
        big_sell_volume = subset_buy_and_sell(big, 'sell').volume.sum()
        small_buy_volume = subset_buy_and_sell(small, 'buy').volume.sum()
        small_sell_volume = subset_buy_and_sell(small, 'sell').volume.sum()
        big_buy_amount = subset_buy_and_sell(big, 'buy').amount.sum()
        big_sell_amount = subset_buy_and_sell(big, 'sell').amount.sum()
        small_buy_amount = subset_buy_and_sell(small, 'buy').amount.sum()
        small_sell_amount = subset_buy_and_sell(small, 'sell').amount.sum()
        big_buy_ratio = float(big_buy_volume / big_sell_volume)
        small_buy_ratio = float(small_buy_volume / small_sell_volume)
        big_buy_avg_price = float(big_buy_amount / big_buy_volume / 100)
        big_sell_avg_price = float(big_sell_amount / big_sell_volume / 100)
        small_buy_avg_price = float(small_buy_amount / small_buy_volume / 100)
        small_sell_avg_price = float(small_sell_amount / small_sell_volume / 100)
        price_diff = float(big.amount.sum() / big.volume.sum() - small.amount.sum() / small.volume.sum())
        total_volume_percent = float(big.volume.sum() / (total_volume / 100)) * 100
        content_raw = [thread, turnover, big_buy_ratio, small_buy_ratio, total_volume_percent, price_diff, big_buy_avg_price, big_sell_avg_price, small_buy_avg_price, small_sell_avg_price, big_buy_volume - big_sell_volume, small_buy_volume - small_sell_volume]
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
            tick_struc[2] >= filter['turnover'],
            tick_struc[3] >= filter['big_buy_ratio'],
            # tick_struc[4] <= filter['small_buy_ratio'],
            # tick_struc[3] / tick_struc[4] > filter['big_small_difference'] or tick_struc[3] / tick_struc[4] < 1 / filter['big_small_difference']
            ]
            if all_true(criteria_list):
                return tick_struc
            else:
                return None
        else:
            return tick_struc
    except: return None

def tick_structure_to_list(code_list, days, bar, filter = None, start_date = ''):
    try:
        for code in code_list:
            struc_list = []
            days_list = at.opening_days(code, days, start_date)
            for day in days_list:
                tick_struc = tick_structure(code, day, bar)
                if filter != None:
                    fil_tick_struc = tick_structure_filter(tick_struc, filter)
                    if fil_tick_struc != None:
                        struc_list.append(fil_tick_struc)
                else:
                    struc_list.append(tick_struc)
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

def draw_sample(list, size):
    if len(list) >= size:
        subset = random.sample(list, size)
        list = [i for i in list if i not in subset]
        return [subset, list]
    else:
        return list

filter = {'turnover': 8, 'big_buy_ratio': 2, 'small_buy_ratio': 1.3, 'big_small_difference': 3}

# code_list = ms.complete_stock_list()
# code_list = [i for i in code_list if i[0] != '3']
code_list = ['603099']
random.shuffle(code_list)
print(code_list)

# code_list = ['600824', '603099', '000043', '002269', '000301', '600558', '002561']
tick_structure_to_list(code_list, 150, 0.001)