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

class StratCarrier:

    def __init__(self, code, date, duration, smooth, discover_mode=False):
        h = al.PriceDeviation()
        if discover_mode == True:
            try:
                self.origin_list = h.price_diff_list_load(code, date, duration, smooth)
            except:
                h.price_diff_list_save(code, date, duration, smooth)
                self.origin_list = h.price_diff_list_load(code, date, duration, smooth)
        else:
            self.origin_list = h.show_difference_list(code, date, duration, smooth)
        self.code = code
        self.smooth = smooth
        self.date = date
        self.criteria_list = []
        self.action_list = []

    def print_list(self, type):
        list = []
        if type == 'criteria':
            list = self.criteria_list
        if type == 'origin':
            list = self.origin_list
        if type == 'action':
            list = [i for i in self.action_list if i['action'] != 'none']
        for i in list:
            print(i)

    def form_criteria_list(self, list):
        for i in list:
            for j in self.origin_list:
                if i['date'] == j['date']:
                    i['close'] = j['close']
                    i['open'] = j['open']
                    break
        for io in self.origin_list:
            existed = 0
            for jo in list:
                if io['date'] == jo['date']:
                    existed = 1
                    break
            if existed == 0:
                self.origin_list.remove(io)
        self.criteria_list = list

    def form_action_list(self, f_buy, f_sell, cut_off=1):
        hold = False
        ref_price = 0.0
        for i in range(len(self.criteria_list)):
            if not hold:
                date = self.criteria_list[i]['date']
                if f_buy(self.criteria_list[i]):
                    action = 'buy'
                    line = {'date': date, 'action': action}
                    if i != len(self.criteria_list) - 1:
                        self.action_list.append(line)
                        ref_price = self.criteria_list[i+1]['close']
                        hold = True
                else:
                    action = 'none'
                    line = {'date': date, 'action': action}
                    self.action_list.append(line)
            else:
                date = self.criteria_list[i]['date']
                action = 'sell'
                line = {'date': date, 'action': action}
                if self.criteria_list[i]['close'] < ref_price * (1 - cut_off):
                    self.action_list.append(line)
                    hold = False
                else:
                    if f_sell(self.criteria_list[i]):
                        self.action_list.append(line)
                        hold = False
                    else:
                        action = 'none'
                        line = {'date': date, 'action': action}
                        self.action_list.append(line)

    def implement(self, name_string, amount=100000, text_only=False):
        code = self.code
        date = self.date
        smooth = self.smooth
        i_start = 0
        for i_start in range(len(self.action_list)):
            if self.action_list[i_start]['action'] == 'buy':
                break
        action_list = self.action_list[i_start:]
        criteria_list = self.criteria_list[i_start:]
        account = tr.StockAccount(time = action_list[0]['date'])
        account = tr.StockAccount(account.save())
        account.deposit(amount, action_list[0]['date'])
        for i in range(len(action_list)):
            if i == len(action_list) - 1:
                account.deposit(0.01, date)
            else:
                if action_list[i]['action'] == 'buy' and action_list[i]['date'] != date:
                    date_i = action_list[i+1]['date']
                    price_i = criteria_list[i+1]['open']
                    account.buy(code, 1, price_i, date_i, True)
                if action_list[i]['action'] == 'sell' and action_list[i]['date'] != date:
                    date_i = action_list[i+1]['date']
                    price_i = criteria_list[i + 1]['open']
                    account.sell(code, 1, price_i, date_i)
        c_string = str(code) + '-' + str(smooth) + '-' + str(name_string)
        account.plot_performance_with_index(method='save', id=c_string, text_only=text_only)
