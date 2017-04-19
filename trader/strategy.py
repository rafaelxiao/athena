import analyst as al
import trader as tr
import messenger as ms
import assistant as at
import time, datetime
import copy
import os
import math
import matplotlib.pyplot as plt
import matplotlib.finance as mpf
import matplotlib.gridspec as gridspec
from matplotlib.dates import date2num, DateFormatter, WeekdayLocator, DayLocator, MONDAY

def diff_line_strategy(code_list, date_list, duration, smooth, amount=100000):

    for code in code_list:
        for date in date_list:
            try:
                p = al.PriceDeviation()
                s = p.__diff_lists__(code, date=date, duration=duration, smooth=smooth)
                state = 'unhold'
                list = []
                i_hold = 0
                for i in s:
                    if i['smoothed difference'] >= 0:
                        if i_hold < 0 and state == 'unhold':
                            list.append({'date' : i['date'], 'signal': 'buy'})
                            state = 'hold'
                    if i['smoothed difference'] < 0:
                        if i_hold > 0 and state == 'hold':
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

                account.plot_performance_with_index(method='save', id=code)
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