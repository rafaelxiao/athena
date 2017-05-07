import analyst as al
import trader as tr
import messenger as ms
import assistant as at
import numpy as np
import time, datetime
import copy
import os
import math
import matplotlib.pyplot as plt
import matplotlib.finance as mpf
import matplotlib.gridspec as gridspec
from matplotlib.dates import date2num, DateFormatter, WeekdayLocator, DayLocator, MONDAY

def diff_line_strategy(code_list, date_list, duration, smooth, bbar=0.0, sbar=0.0, amount=100000, text_only=False):

    for code in code_list:
        for date in date_list:
            try:
                p = al.PriceDeviation()
                s = p.__diff_lists__(code, date=date, duration=duration, smooth=smooth)
                state = 'unhold'
                list = []
                i_hold = 0.0
                for i in s:
                    if i['smoothed difference'] >= bbar:
                        if i_hold < bbar and state == 'unhold':
                            list.append({'date' : i['date'], 'signal': 'buy'})
                            state = 'hold'
                    if i['smoothed difference'] < sbar:
                        if i_hold >= sbar and state == 'hold':
                            list.append({'date' : i['date'], 'signal': 'sell'})
                            state = 'unhold'
                    i_hold = i['smoothed difference']

                account = tr.StockAccount(time=at.next_opening_day(code, list[0]['date']))
                account = tr.StockAccount(account.save())
                account.deposit(amount, at.next_opening_day(code, list[0]['date']))
                for i in range(len(list)):
                    if list[i]['signal'] == 'buy' and list[i]['date'] != date:
                        date_i = at.next_opening_day(code, list[i]['date'], default_shift=True)
                        account.buy(code, 1, ms.get_stock_hist_data(code, date_i, 'open'), date_i, True)
                    if list[i]['signal'] == 'sell' and list[i]['date'] != date:
                        date_i = at.next_opening_day(code, list[i]['date'], default_shift=True)
                        account.sell(code, 1, ms.get_stock_hist_data(code, date_i, 'open'), date_i)
                    if list[i] == list[-1]:
                        account.deposit(0.01, date)
                id = str(code) + '-' + str(smooth) + '-' + str(int(bbar*100)) + '-' + str(int(sbar*100))
                account.plot_performance_with_index(method='save', id=id, text_only=text_only)
            except:
                pass

def diff_line_double_duration(code_list, date_list, duration, smooth, amount=100000):

    for code in code_list:
        for date in date_list:
            try:
                p = al.PriceDeviation()
                s = p.__diff_lists_multi_smoothing__(code, smooth, date, duration)
                state = 'unhold'
                list = []
                i_hold_fast = s[0]['smoothed difference %s'%smooth[0]]
                i_hold_slow = s[0]['smoothed difference %s'%smooth[1]]
                for i in s:
                    if i['smoothed difference %s'%smooth[0]] >= i['smoothed difference %s'%smooth[1]]:
                        if i_hold_fast < i_hold_slow and state == 'unhold':
                            list.append({'date' : i['date'], 'signal': 'buy'})
                            state = 'hold'
                    if i['smoothed difference %s'%smooth[0]] < i['smoothed difference %s'%smooth[1]]:
                        if i_hold_fast > i_hold_slow and state == 'hold':
                            list.append({'date' : i['date'], 'signal': 'sell'})
                            state = 'unhold'
                    i_hold_fast = i['smoothed difference %s'%smooth[0]]
                    i_hold_slow = i['smoothed difference %s'%smooth[1]]


                account = tr.StockAccount(time=at.next_opening_day(code, list[0]['date']))
                account = tr.StockAccount(account.save())
                account.deposit(amount, at.next_opening_day(code, list[0]['date']))
                for i in range(len(list)):
                    if list[i]['signal'] == 'buy' and list[i]['date'] != date:
                        date_i = at.next_opening_day(code, list[i]['date'], default_shift=True)
                        account.buy(code, 1, ms.get_stock_hist_data(code, date_i, 'open'), date_i, True)
                    if list[i]['signal'] == 'sell' and list[i]['date'] != date:
                        date_i = at.next_opening_day(code, list[i]['date'], default_shift=True)
                        account.sell(code, 1, ms.get_stock_hist_data(code, date_i, 'open'), date_i)
                    if list[i] == list[-1]:
                        account.deposit(0.01, date)

                account.plot_performance_with_index(method='save', id=code)
            except:
                pass

def diff_line_multi_line(code_list, date_list, buy_line=0.0, sell_line=0.0, exit_days=7, smooth=7, duration=300, amount=100000, text_only=False, discover_mode=False):
    h = al.PriceDeviation()
    for code in code_list:
        for date in date_list:
            try:
                if discover_mode == True:
                    try:
                        origin_list = h.price_diff_list_load(code, date, duration, smooth)
                    except:
                        h.price_diff_list_save(code, date, duration, smooth)
                        origin_list = h.price_diff_list_load(code, date, duration, smooth)
                else:
                    origin_list = h.show_difference_list(code, date, duration, smooth)
                hold = False
                through = False
                exit_count = 0
                action_list = []
                pre_value = 0.0
                for i in origin_list:
                    date = i['date']
                    value = i['smoothed difference']
                    exit_count += 1
                    if not hold:
                        if pre_value <= buy_line and value >= buy_line:
                            signal = 'buy'
                            line = {'date': date, 'signal': signal}
                            action_list.append(line)
                            exit_count = 0
                            hold = True
                    else:
                        if not through and pre_value >= sell_line:
                            through = True
                        if not through:
                            if value < buy_line:
                                signal = 'sell'
                                line = {'date': date, 'signal': signal}
                                action_list.append(line)
                                hold = False
                        else:
                            if value < sell_line:
                                signal = 'sell'
                                line = {'date': date, 'signal': signal}
                                action_list.append(line)
                                hold = False
                                through = False
                                '''
                                if exit_count >= exit_days:
                                if value <= sell_line:
                                    signal = 'sell'
                                    line = {'date': date, 'signal': signal}
                                    action_list.append(line)
                                    hold = False
                                '''
                    pre_value = value
                account = tr.StockAccount(time=at.next_opening_day(code, action_list[0]['date']))
                account = tr.StockAccount(account.save())
                account.deposit(amount, at.next_opening_day(code, action_list[0]['date']))
                for i in range(len(action_list)):
                    if action_list[i]['signal'] == 'buy' and action_list[i]['date'] != date:
                        date_i = at.next_opening_day(code, action_list[i]['date'], default_shift=True)
                        account.buy(code, 1, ms.get_stock_hist_data(code, date_i, 'open'), date_i, True)
                    if action_list[i]['signal'] == 'sell' and action_list[i]['date'] != date:
                        date_i = at.next_opening_day(code, action_list[i]['date'], default_shift=True)
                        account.sell(code, 1, ms.get_stock_hist_data(code, date_i, 'open'), date_i)
                    if action_list[i] == action_list[-1]:
                        account.deposit(0.01, date)
                id = str(code) + '-' + str(smooth) + '-' + str(int(buy_line*100)) + '-' + str(int(sell_line*100))
                account.plot_performance_with_index(method='save', id=id, text_only=text_only)
            except:
                pass

def top_mean_strategy(code_list, date_list, bar=0.0, outlier=3, smooth=3, duration=300, length=30, amount=100000, text_only=False, top_thread=0.0, bottom_thread=0.0, discover_mode=False):
    duration = duration + length
    for code in code_list:
        for date in date_list:
            try:
                s = tr.StratCarrier(code, date, duration, smooth, discover_mode)
                p = al.PriceDevAna()
                origin_list = s.origin_list
                avg_value_list = []
                for i in range(length, len(origin_list)):
                    processed_list = p.get_tops_and_bottoms(origin_list[i-length:i], 'smoothed difference', top_thread=top_thread, top_outlier=outlier)
                    top_avg = np.average(processed_list['top'])
                    bottom_avg = np.average(processed_list['bottom'])
                    if np.isnan(top_avg):
                        top_avg = 0.0
                    if np.isnan(bottom_avg):
                        bottom_avg = 0.0
                    line = {'date': origin_list[i]['date'], 'avg_tops': top_avg, 'avg_bottoms': bottom_avg}
                    avg_value_list.append(line)
                s.form_criteria_list(avg_value_list)
                s.print_list('criteria')
                def f_buy(i):
                    result = False
                    if i['avg_tops'] >= bar:
                        result = True
                    return result
                def f_sell(i):
                    result = False
                    if i['avg_tops'] < bar:
                        result = True
                    return result
                s.form_action_list(f_buy, f_sell)
                s.print_list('action')
                name_string = '-' + str(int(bar * 100))
                s.implement(name_string)
            except:
                pass

def diff_area_strategy(code_list, date_list, mood_bar=10.0, cash_bar=-5.0, outlier=3, smooth=3, duration=300, length=30, amount=100000, text_only=False, top_thread=0.0, bottom_thread=0.0, discover_mode=False):
    duration = duration + length
    for code in code_list:
        for date in date_list:
            s = tr.StratCarrier(code, date, duration=duration, smooth=smooth, discover_mode=discover_mode)
            p_list = []
            for i in range(length, len(s.origin_list)):
                mood_sum = np.sum([k['smoothed difference'] for k in s.origin_list[i - length:i]])
                cash_sum = np.sum([k['smoothed actual'] for k in s.origin_list[i-length:i]])
                line = {'date': s.origin_list[i]['date'], 'mood': mood_sum, 'cash': cash_sum}
                p_list.append(line)
            s.form_criteria_list(p_list)
            s.print_list('criteria')
            def f_buy(k):
                result = False
                if k['mood'] >= mood_bar and k['cash'] >= cash_bar:
                    result = True
                return result
            def f_sell(k):
                result = False
                if k['mood'] < mood_bar or k['cash'] < cash_bar:
                    result = True
                return result
            s.form_action_list(f_buy, f_sell)
            s.print_list('action')
            s.implement(str(int(mood_bar))+ '-' + str(int(cash_bar)))
