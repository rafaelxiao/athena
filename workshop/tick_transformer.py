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
get_opening_days = at.opening_days
date_encoding = at.date_encoding
date_decoding = at.date_decoding
progress_bar = at.process_monitor

class TickTransformer:

    def __init__(self, code, date, duration):
        dates = get_opening_days(code, duration, date)
        self.__info__ = {'code': code, 'date': date, 'duration': duration}
        self.__ticks__ = {}
        count = 0
        for date in dates:
            try:
                count += 1
                tick = get_tick_data(code, date)
                tick['change'] = tick['change'].apply(lambda x: self.__clean_change__(x))
                if tick.loc[0, 'time'][:5] != 'alert':
                    self.__ticks__[date] = tick
            except:
                pass
            progress_bar(count / len(dates) * 100)

    def __clean_change__(self, string):
        value = 0
        if not string[1] == '-':
            if string[0] == '-':
                value = -1 * round(float(string[1:]), 2)
            else:
                value = round(float(string), 2)
        if value >= 1:
            value = 0
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

    def __get_dates__(self):
        dates = [i for i in self.__ticks__]
        return dates

    def __get_tick__(self, date):
        tick = None
        dates = self.__get_dates__()
        if date in dates:
            tick = self.__ticks__[date]
        return tick

    def __get_column__(self, date, column):
        tick = self.__get_tick__(date)
        list = tick.loc[:, column].tolist()
        return list

    def __get_key_stats__(self, date, type):
        key_price = {}
        tick = self.__get_tick__(date)
        key_price['open'] = tick.loc[len(tick)-1, 'price']
        key_price['close'] = tick.loc[0, 'price']
        key_price['high'] = tick.loc[:, 'price'].max()
        key_price['low'] = tick.loc[:, 'price'].min()
        key_price['volume'] = tick.loc[:, 'volume'].sum()
        key_price['amount'] = tick.loc[:, 'amount'].sum()
        return key_price[type]

    def __generate_group_list__(self, low, high, interval, start=0):
        list = []
        for i in range(0, int((high - start) / interval) + 2):
            if start + i * interval >= low:
                    list.append(round(start + (i - 1) * interval, 2))
            if start + i * interval >= high:
                list.append(round(start + i * interval, 2))
                break
        return list

    def __assign_group__(self, tick, column, group_list, type=''):

        def find_group(num, list, type):
            group = 0
            if num <= list[-1]:
                for i in sorted(list):
                    if i >= num:
                        break
                    else: group += 1
            if type == 'range':
                if group == 0:
                    group = 'out of range'
                else:
                    group = '%.2f - %.2f'%(list[group-1], list[group])
            if type == 'mean':
                if group != 0:
                    group = round(float((list[group-1] + list[group]) / 2), 2)
            return group

        tick['group'] = tick.loc[:, column].apply(lambda x: find_group(x, group_list, type))
        return tick

    def __dict_to_frame__(self, dict):
        dates = sorted(list(set([date_encoding(i[0]) for i in dict])))
        dates = [date_decoding(i) for i in dates]
        prices = sorted(list(set([i[1] for i in dict])), reverse=True)
        frame = pd.DataFrame(index=prices, columns=dates, data=0)
        for i in dict:
            frame.loc[i[1], i[0]] = dict[i]
        return frame

    def __get_order_type_details__(self, group_interval, amount_threshold=0, index_type='', order_type=''):
        dates = [i for i in self.__ticks__]
        dict = {}
        for date in dates:
            tick = self.__get_tick__(date)
            tick = self.__exclude_aggregate_auction__(tick)
            high = self.__get_key_stats__(date, 'high')
            low = self.__get_key_stats__(date, 'low')
            if order_type != '':
                tick = tick.loc[tick.type == order_type]
            group_list = self.__generate_group_list__(low, high, group_interval)
            tick = self.__assign_group__(tick, 'price', group_list, index_type)
            tick = pd.DataFrame(tick.groupby(by=['group'])['amount'].sum())
            if amount_threshold != 0:
                tick = tick.loc[tick.amount >= amount_threshold * 10000]
            for i in tick.index.values:
                name = (date, i)
                value = tick.loc[i, 'amount']
                if name in dict:
                    dict[name] = round((value / 10000) + dict[name], 2)
                else:
                    dict[name] = round(value / 10000, 2)
        frame = self.__dict_to_frame__(dict)
        return frame

    def __get_effect_details__(self, group_interval, amount_threshold=0, index_type='', order_type=''):
        dates = [i for i in self.__ticks__]
        dict = {}
        for date in dates:
            tick = self.__get_tick__(date)
            tick = self.__exclude_aggregate_auction__(tick)
            high = self.__get_key_stats__(date, 'high')
            low = self.__get_key_stats__(date, 'low')
            if order_type != '':
                tick = tick.loc[tick.type == order_type]
            group_list = self.__generate_group_list__(low, high, group_interval)
            tick = self.__assign_group__(tick, 'price', group_list, index_type)
            amount_sum = tick['amount'].sum()
            tick['effect'] = abs(tick['change'] / amount_sum * 10000000)
            tick = pd.DataFrame(tick.groupby(by=['group'])['effect', 'amount'].sum())
            tick['effect'] = tick['effect'] / (tick['amount'] / amount_sum)
            if amount_threshold != 0:
                tick = tick.loc[tick.amount >= amount_threshold * 10000]
            tick = tick.drop('amount', axis=1)
            for i in tick.index.values:
                name = (date, i)
                value = tick.loc[i, 'effect']
                if name in dict:
                    dict[name] = round(value, 2)
                else:
                    dict[name] = round(value, 2)
        frame = self.__dict_to_frame__(dict)
        return frame

    def __save_to_excel__(self, frame, key_word):
        dir_path = os.path.join(os.getcwd(), 'tick_details')
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        code = self.__info__['code']
        date = self.__info__['date']
        duration = self.__info__['duration']
        file_path = os.path.join(dir_path, '%s-%s-%s-%s.xlsx'%(key_word, code, date, duration))
        writer = pd.ExcelWriter(file_path)
        frame.to_excel(writer)
        writer.save()

    def unveil_sum(self, group_interval, amount_threshold=0, index_type='range'):
        dates = [i for i in self.__ticks__]
        dict = {}
        for date in dates:
            tick = self.__get_tick__(date)
            high = self.__get_key_stats__(date, 'high')
            low = self.__get_key_stats__(date, 'low')
            group_list = self.__generate_group_list__(low, high, group_interval)
            tick = self.__assign_group__(tick, 'price', group_list, index_type)
            tick = pd.DataFrame(tick.groupby(by='group')['amount'].sum())
            if amount_threshold != 0:
                tick = tick.loc[tick.amount >= amount_threshold * 10000]
            for i in tick.index.values:
                name = (date, i)
                value = tick.loc[i, 'amount']
                if name in dict:
                    dict[name] = round((value / 10000) + dict[name], 2)
                else:
                    dict[name] = round(value / 10000, 2)
        frame = self.__dict_to_frame__(dict)
        self.__save_to_excel__(frame, 'sum')

    def unveil_order(self, group_interval, amount_threshold=0, index_type='range', order_type='net'):
        frame = []
        if order_type == 'buy':
            frame = self.__get_order_type_details__(group_interval, amount_threshold, index_type, '买盘')
        elif order_type == 'sell':
            frame = self.__get_order_type_details__(group_interval, amount_threshold, index_type, '卖盘')
        elif order_type == 'net':
            buy_frame = self.__get_order_type_details__(group_interval, amount_threshold, index_type, '买盘')
            sell_frame = self.__get_order_type_details__(group_interval, amount_threshold, index_type, '卖盘')
            sell_frame = sell_frame.loc[:, :] * -1
            frame = buy_frame.add(sell_frame).sort_index(ascending=False)
        else: pass
        if len(frame) > 0:
            self.__save_to_excel__(frame, 'order-%s'%order_type)

    def unveil_effect(self, group_interval, amount_threshold=0, index_type='range', order_type='net'):
        frame = []
        if order_type == 'buy':
            frame = self.__get_effect_details__(group_interval, amount_threshold, index_type, '买盘')
        elif order_type == 'sell':
            frame = self.__get_effect_details__(group_interval, amount_threshold, index_type, '卖盘')
        elif order_type == 'net':
            buy_frame = self.__get_effect_details__(group_interval, amount_threshold, index_type, '买盘')
            sell_frame = self.__get_effect_details__(group_interval, amount_threshold, index_type, '卖盘')
            sell_frame = sell_frame.loc[:, :] * -1
            frame = buy_frame.add(sell_frame).sort_index(ascending=False)
        else: pass
        if len(frame) > 0:
            self.__save_to_excel__(frame, 'effect-%s'%order_type)

h = ms.TickData()
h.update('600313')
t = TickTransformer('600313', '2017-06-22', 200)
t.unveil_effect(0.2, order_type='net')
t.unveil_order(0.2, order_type='net')
