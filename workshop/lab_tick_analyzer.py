import tushare as ts
import assistant as at
import analyst as al
import messenger as ms
import trader as tr
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import time

get_tick_data = ms.get_tick_data
get_outstanding = ms.get_stock_outstanding
get_opening_days = at.opening_days
cut_config = 0.2

class TickAna:

    def __init__(self, code, date, cut=None):
        if cut == None:
            cut = cut_config
        frame = get_tick_data(code, date)
        frame['change'] = frame['change'].apply(lambda row: self.__clean_change__(row))
        self.__key_price__ = self.__get_key_price__(frame)
        self.__cut__ = cut
        self.__tick__ = frame
        self.__ticky__ = self.__exclude_aggregate_auction__(self.__tick__)

    def __clean_change__(self, string):
        value = 0
        if not string[1] == '-':
            if string[0] == '-':
                value = -1 * round(float(string[1:]), 2)
            else:
                value = round(float(string), 2)
        return value

    def __encode_time_stamp__(self, string):
        hour = int(string[:2])
        min = int(string[3:5])
        sec = int(string[6:8])
        time_stamp = (hour * 60 + min) * 60 + sec
        return time_stamp

    def __decode_time_stamp__(self, num, sep=':'):
        hour = int(num / 3600)
        min = int((num % 3600) / 60)
        sec = int(num % 60)
        string = sep.join([str(hour), str(min), str(sec)])
        return string

    def __exclude_aggregate_auction__(self, frame):
        frame['time_stamp'] = frame['time'].apply(lambda row: self.__encode_time_stamp__(row))
        starting_auction_time = self.__encode_time_stamp__('09:30:00')
        ending_auction_time = self.__encode_time_stamp__('15:00:00')
        frame = frame[frame['time_stamp'] > starting_auction_time]
        frame = frame[frame['time_stamp'] < ending_auction_time]
        frame = frame.drop('time_stamp', 1)
        return frame

    def __get_key_price__(self, frame):
        key_price = {}
        price_list = frame['price'].tolist()
        key_price['open'] = frame.loc[len(frame)-1]['price']
        key_price['close'] = frame.loc[0]['price']
        key_price['high'] = max(price_list)
        key_price['low'] = min(price_list)
        return key_price

    def __cut_price_into_group__(self):
        def group_func(x):
            amount = (x['amount']).sum()
            move = x['weighted_force'].sum()
            return pd.Series([amount, move], index=['amount', 'force'])

        frame = self.__ticky__
        high = self.__key_price__['high']
        low = self.__key_price__['low']

        cut_unit = self.__cut__
        cut_list = []
        for i in range(0, int(high / cut_unit)+2):
            if i * cut_unit >= low:
                cut_list.append(round((i - 1) * cut_unit, 2))
            if i * cut_unit >= high:
                cut_list.append(round((i) * cut_unit, 2))
                break


        frame = frame[frame['type'] != '中性盘']
        frame['force'] = abs(frame['change'] / frame['amount'] * 100000000)
        total_amount = frame['amount'].sum()
        frame['weighted_force'] = frame['force'] * frame['amount'] / total_amount

        frame = frame.groupby([pd.cut(frame['price'], cut_list), 'type']).apply(group_func)
        frame['force'] = round(frame['force'] / (frame['amount'] / total_amount), 2)
        return frame

    def summary(self):
        frame = self.__cut_price_into_group__()
        summary = {}
        for i, new_frame in frame.groupby(level=0):
            amount_buy, amount_sell, force_buy, force_sell = 0, 0, 0, 0
            range = i
            for j in new_frame.index:
                if j[1] == '买盘':
                    amount_buy = new_frame.loc[(i, '买盘')]['amount'] / 10000
                    force_buy = new_frame.loc[(i, '买盘')]['force']
                    if np.isnan(force_buy):
                        force_buy = 0
                    if np.isnan(amount_buy):
                        amount_buy = 0
                if j[1] == '卖盘':
                    amount_sell = new_frame.loc[(i, '卖盘')]['amount'] / 10000
                    force_sell = new_frame.loc[(i, '卖盘')]['force']
                    if np.isnan(force_sell):
                        force_sell = 0
                    if np.isnan(amount_sell):
                        amount_sell = 0

            amount_ratio = 0
            force_ratio = 0
            force_over = force_buy - force_sell
            if not 0 in [amount_buy, amount_sell, force_buy, force_sell]:
                amount_ratio = amount_buy / amount_sell
                force_ratio = abs(force_buy / force_sell)
            summary[range] = {
                'buy_amount': round(float(amount_buy), 2),
                'sell_amount': round(float(amount_sell), 2),
                'buy_effect': round(float(force_buy), 2),
                'sell_effect': round(float(force_sell), 2),
                'strength': round(float(amount_ratio), 2),
                'effectiveness': round(float(force_ratio), 2),
                'overpower': round(float(force_over), 2)
            }
        return summary

    def aggregate_summary(self):

        frame = self.__tick__
        frame = frame[frame['type'] != '中性盘']
        frame['force'] = abs(frame['change'] / frame['amount'] * 100000000)
        total_amount = frame['amount'].sum()
        frame['weighted_force'] = frame['force'] * frame['amount'] / total_amount

        frame = frame.groupby(['type'])['amount', 'weighted_force'].sum()
        frame['weighted_force'] = frame['weighted_force'] / (frame['amount'] / total_amount)
        frame.columns = frame.columns.str.replace('weighted_force', 'force')

        buy_amount = frame.loc['买盘', 'amount'] / 10000
        sell_amount = frame.loc['卖盘', 'amount'] / 10000
        buy_effect = frame.loc['买盘', 'force']
        sell_effect = frame.loc['卖盘', 'force']
        strength = buy_amount / sell_amount
        effectiveness = buy_effect / sell_effect
        overpower = buy_effect - sell_effect

        summary = {
            'buy_amount': round(float(buy_amount), 2),
            'sell_amount': round(float(sell_amount), 2),
            'buy_effect': round(float(buy_effect), 2),
            'sell_effect': round(float(sell_effect), 2),
            'strength': round(float(strength), 2),
            'effectiveness': round(float(effectiveness), 2),
            'overpower': round(float(overpower), 2)
        }
        return summary

class TickAnne:

    def __init__(self, code, date, duration, cut=None):
        if cut == None:
            cut = cut_config
        self.__dates__ = get_opening_days(code, duration, date)
        self.__combined_dict__ = self.__process__(self.__combine__(code, cut))

    def __combine__(self, code, cut):

        def dict_append(unit, dict):
            dict = dict
            for key in unit:
                if key in dict:
                    old = dict[key]
                    added = unit[key]
                    buy_amount = old['buy_amount'] + added['buy_amount']
                    sell_amount = old['sell_amount'] + added['sell_amount']
                    buy_effect = (old['buy_effect'] * old['buy_amount'] +
                                  added['buy_effect'] * added['buy_amount']) / \
                                 (old['buy_amount'] + added['buy_amount'])
                    sell_effect = (old['sell_effect'] * old['sell_amount'] +
                                  added['sell_effect'] * added['sell_amount']) / \
                                 (old['sell_amount'] + added['sell_amount'])
                    dict[key] = {
                        'buy_amount': round(float(buy_amount), 2),
                        'sell_amount': round(float(sell_amount), 2),
                        'buy_effect': round(float(buy_effect), 2),
                        'sell_effect': round(float(sell_effect), 2)
                    }
                else:
                    dict[key] = unit[key]
            return dict

        combined_dict = {}
        for date in self.__dates__:
            t = TickAna(code, date, cut)
            summa = t.summary()
            for key in summa:
                unit = {}
                key_list = key.split(',')
                price = round((float(key_list[0][1:]) + float(key_list[1][1:-1])) / 2, 2)
                buy_amount = summa[key]['buy_amount']
                sell_amount = summa[key]['sell_amount']
                buy_effect = summa[key]['buy_effect']
                sell_effect = summa[key]['sell_effect']
                unit[price] = {
                    'buy_amount': round(float(buy_amount), 2),
                    'sell_amount': round(float(sell_amount), 2),
                    'buy_effect': round(float(buy_effect), 2),
                    'sell_effect': round(float(sell_effect), 2)
                }
                combined_dict = dict_append(unit, combined_dict)
        return combined_dict

    def __process__(self, dict):

        def total_amount(type, dict):
            total = 0
            for i in dict:
                total += dict[i][type]
            return total

        total_buy_amount = total_amount('buy_amount', dict)
        total_sell_amount = total_amount('sell_amount', dict)

        for i in dict:
            dict[i]['buy_percent'] = round(dict[i]['buy_amount'] / total_buy_amount * 100, 2)
            dict[i]['sell_percent'] = round(dict[i]['sell_amount'] / total_sell_amount * 100, 2)

            if dict[i]['sell_amount'] == 0:
                dict[i]['strength'] = 0
            else:
                dict[i]['strength'] = round(dict[i]['buy_amount'] / dict[i]['sell_amount'], 2)

            if dict[i]['sell_effect'] == 0:
                dict[i]['effectiveness'] = 0
            else:
                dict[i]['effectiveness'] = round(dict[i]['buy_effect'] / dict[i]['sell_effect'], 2)

            dict[i]['overpower'] = round(dict[i]['buy_effect'] - dict[i]['sell_effect'], 2)

        return dict

    def top_statistics(self, top=3):

        def get_top(top, type, dict):
            list = []
            for i in dict:
                list.append(dict[i][type])
            list = sorted(list, reverse=True)[:top]
            output = {}
            for k in list:
                for j in dict:
                    if dict[j][type] == k:
                        output[j] = {type: dict[j][type]}
                        break
            return output

        dict = self.__combined_dict__
        top_dict = {}
        top_dict['top %s buy percent' % top] = get_top(top, 'buy_percent', dict)
        top_dict['top %s sell percent' % top] = get_top(top, 'sell_percent', dict)
        top_dict['top %s buy effect' % top] = get_top(top, 'buy_effect', dict)
        top_dict['top %s sell effect' % top] = get_top(top, 'sell_effect', dict)
        top_dict['top %s strength' % top] = get_top(top, 'strength', dict)
        top_dict['top %s effectiveness' % top] = get_top(top, 'effectiveness', dict)
        top_dict['top %s overpower' % top] = get_top(top, 'overpower', dict)

        return top_dict

def save_tick_summary(code_list, date, duration, detail=True, cut=None):
    path = os.path.join(os.getcwd(), 'tick_summary')
    if not os.path.exists(path):
        os.mkdir(path)
    for code in code_list:
        date_list = at.opening_days(code, duration, date)
        file_path = os.path.join(path, '%s-%s-%s.txt'%(code, date, duration))
        count = 0
        with open(file_path, 'w') as w:
            for date in date_list:
                count += 1
                w.writelines('%s\n'%date)
                w.writelines('\n')
                t = TickAna(code, date, cut)

                aggre_summary = t.aggregate_summary()

                w.writelines('\t%s\n' % 'Summary')
                w.writelines('\t\tbuy amount: %s\n' % aggre_summary['buy_amount'])
                w.writelines('\t\tsell amount: %s\n' % aggre_summary['sell_amount'])
                w.writelines('\t\tbuy effect: %s\n' % aggre_summary['buy_effect'])
                w.writelines('\t\tsell effect: %s\n' % aggre_summary['sell_effect'])
                w.writelines('\t\tstrength: %s\n' % aggre_summary['strength'])
                w.writelines('\t\teffectiveness: %s\n' % aggre_summary['effectiveness'])
                w.writelines('\t\toverpower: %s\n' % aggre_summary['overpower'])
                w.writelines('\n')

                if detail == True:
                    summary = t.summary()
                    for i in summary:
                        w.writelines('\t%s\n' % i)
                        w.writelines('\t\tbuy amount: %s\n' % summary[i]['buy_amount'])
                        w.writelines('\t\tsell amount: %s\n' % summary[i]['sell_amount'])
                        w.writelines('\t\tbuy effect: %s\n' % summary[i]['buy_effect'])
                        w.writelines('\t\tsell effect: %s\n' % summary[i]['sell_effect'])
                        w.writelines('\t\tstrength: %s\n' % summary[i]['strength'])
                        w.writelines('\t\teffectiveness: %s\n' % summary[i]['effectiveness'])
                        w.writelines('\t\toverpower: %s\n' % summary[i]['overpower'])
                        w.writelines('\n')
                    w.writelines('\n')
                at.process_monitor(count / len(date_list) * 100)

def save_period_tick_summary(code_list, date, duration, cut=None):
    path = os.path.join(os.getcwd(), 'tick_summary')
    if not os.path.exists(path):
        os.mkdir(path)
    count = 0
    for code in code_list:
        count += 1
        file_path = os.path.join(path, '%s-period-summary-%s-%s.txt'%(code, date, duration))
        with open(file_path, 'w') as w:
            t = TickAnne(code, date, duration, cut)
            dict = t.__combined_dict__
            for i in sorted(dict):
                w.writelines('%s\n'%i)
                w.writelines('\n')
                w.writelines('\tbuy percent: %s\n' % dict[i]['buy_percent'])
                w.writelines('\tsell percent: %s\n' % dict[i]['sell_percent'])
                w.writelines('\tbuy effect: %s\n' % dict[i]['buy_effect'])
                w.writelines('\tsell effect: %s\n' % dict[i]['sell_effect'])
                w.writelines('\tstrength: %s\n' % dict[i]['strength'])
                w.writelines('\teffectiveness: %s\n' % dict[i]['effectiveness'])
                w.writelines('\toverpower: %s\n' % dict[i]['overpower'])
                w.writelines('\n')
        at.process_monitor(count / len(code_list) * 100)

def save_period_tick_top_summary(code_list, date, duration, top=3, cut=None):
    path = os.path.join(os.getcwd(), 'tick_summary')
    if not os.path.exists(path):
        os.mkdir(path)
    count = 0
    for code in code_list:
        count += 1
        file_path = os.path.join(path, '%s-period-top-summary-%s-%s.txt'%(code, date, duration))
        with open(file_path, 'w') as w:
            t = TickAnne(code, date, duration, cut)
            top_dict = t.top_statistics(top)
            for i in top_dict:
                w.writelines('%s\n'%i)
                w.writelines('\n')
                for j in top_dict[i]:
                    price = j
                    for k in top_dict[i][j]:
                        percent = top_dict[i][j][k]
                        text = k.replace('_', ' ')
                        w.writelines('\tprice: %s\t%s: %s\n'%(price, text, percent))
                w.writelines('\n' * 2)
        at.process_monitor(count / len(code_list) * 100)


# t = TickAnne('002074', '2017-06-14', 10, 0.2)
#for i in sorted(t.__combined_dict__):
#   print(i, t.__combined_dict__[i])

# top = t.top_statistics(4)

# t.summary()
# t.aggregate_summary()


code_list = ['002074', '000625']

# save_period_tick_summary(code_list, '2017-06-14', 5, 0.1)
# save_period_tick_top_summary(code_list, '2017-06-14', 5, 10, 0.1)
save_tick_summary(code_list, '2017-06-15', 50, False)