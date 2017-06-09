import json
import os, sys
import numpy as np
import tushare as ts
import pandas as pd
import datetime, time
import messenger as ms

class TickData:

    def __init__(self, address=None):
        if address == None:
            address = ms.data_warehouse
        self.__address__ = address

    def __fetch__(self, code, date, dict):
        tick = ts.get_tick_data(code, date)
        if tick.ix[0].time[:5] != 'alert':
            tick = json.dumps(tick.to_json())
            dict[date] = tick

    def __date_existed__(self, date, dict):
        result = False
        for i in dict:
            if date == i:
                result = True
                break
        return result

    def __get_year_and_month__(self, date):
        year_and_month = date[:7]
        return year_and_month

    def __process_monitor__(self, percent):
        percent = int(percent)
        completed = '|'
        uncompleted = ' '
        percent_monitor = '  %d%%' % percent
        bar = completed * percent + uncompleted * (100 - percent) + percent_monitor
        sys.stdout.write('\r')
        sys.stdout.write(bar)
        sys.stdout.flush()
        if percent == 100:
            print('\r')

    def __date_encoding__(self, date_string):
        encoded = datetime.date(int(date_string[0:4]), int(date_string[5:7]), int(date_string[8:10]))
        return encoded

    def __date_decoding__(self, date):
        decoded = date.strftime("%Y-%m-%d")
        return decoded

    def __is_date_after__(self, date1, date2):
        result = False
        date1 = self.__date_encoding__(date1)
        date2 = self.__date_encoding__(date2)
        if date1 > date2:
            result = True
        return result

    def __sort_date_list__(self, date_list):
        length = len(date_list)
        while length > 0:
            for i in range(length - 1):
                if self.__is_date_after__(date_list[i], date_list[i+1]):
                    hold = date_list[i+1]
                    date_list[i+1] = date_list[i]
                    date_list[i] = hold
            length -= 1
        return date_list

    def __store_index__(self, code, date):
        path = os.path.join(self.__get_directory__(code), '%s.json' % 'index')
        idx_list = self.__load_index__(code)
        if date not in idx_list:
            idx_list.append(date)
        idx_list = self.__sort_date_list__(idx_list)
        with open(path, 'w') as index_file:
            index_file.write(json.dumps(idx_list))

    def __load_index__(self, code):
        idx_list = []
        path = os.path.join(self.__get_directory__(code), '%s.json' % 'index')
        if os.path.exists(path):
            with open(path, 'r') as index_file:
                idx_list = json.loads(index_file.read())
        return idx_list

    def __store__(self, code, date, dict):
        ori_date = date
        date = self.__get_year_and_month__(date)
        path = os.path.join(self.__get_directory__(code), '%s.json' %date)
        if dict != {}:
            with open(path, 'w') as json_file:
                json_file.write(json.dumps(dict))
                self.__store_index__(code, ori_date)

    def __load__(self, code, date):
        dict = {}
        if len(date) != 7:
            date = self.__get_year_and_month__(date)
        path = os.path.join(self.__get_directory__(code), '%s.json' %date)
        if os.path.exists(path):
            with open(path, 'r') as json_file:
                read = json_file.read()
                dict = json.loads(read)
        return dict

    def __get_directory__(self, code=None, name='ticks'):
        if code == None:
            path = os.path.join(self.__address__, '%s'%name)
        else:
            try:
                os.mkdir(os.path.join(self.__address__, name, code))
            except:
                pass
            path = os.path.join(self.__address__, '%s'%name, '%s'%code)
        return path

    def __get_one_tick__(self, code, date):
        path = os.path.join(self.__get_directory__(code), '%s.json'%self.__get_year_and_month__(date))
        if os.path.exists(path):
            dic = self.__load__(code, date)
        else:
            dic = {}
        self.__fetch__(code, date, dic)
        self.__store__(code, date, dic)

    def get_tick_data(self, code, date):
        content = None
        year_and_month = self.__get_year_and_month__(date)
        path = os.path.join(self.__get_directory__(code), '%s.json'%year_and_month)
        if os.path.exists(path):
            dic = self.__load__(code, year_and_month)
            if dic != {}:
                for i in dic:
                    if date == i:
                        content = pd.read_json(eval(dic[i]))
                        content.sort_index(inplace=True)
        return content

    def __generate_date_list_local__(self, start, end):
        date_list = []
        start = self.__date_encoding__(start)
        end = self.__date_encoding__(end)
        pointer = start
        while pointer <= end:
            if pointer.weekday() <= 4:
                date_list.append(self.__date_decoding__(pointer))
            pointer += datetime.timedelta(1)
        return date_list

    def __generate_date_list__(self, code, start, end):
        frame = ts.get_k_data(code, start, end)
        date_list = []
        for i, j in frame.iterrows():
            date_list.append(j['date'])
        return date_list

    def show_dates_hard(self, code, short=False):
        path = self.__get_directory__(code)
        date_list = []
        file_list = [i for i in os.listdir(path) if i[0] != '.']
        if short == True:
            file_list = [file_list[0], file_list[-1]]
        for i in file_list:
            date = i[:7]
            dict = self.__load__(code, date)
            for i in dict:
                date_list.append(i)
        date_list = self.__sort_date_list__(date_list)
        if short:
            date_list = [date_list[0], date_list[-1]]
        return date_list

    def show_dates(self, code, short=False):
        date_list = self.__load_index__(code)
        if short:
            date_list = [date_list[0], date_list[-1]]
        return date_list

    def show_stocks(self):
        stocks = []
        path = self.__get_directory__()
        for i in os.listdir(path):
            if i[0] != '.':
                stocks.append(i)
        return stocks

    def deposit(self, code, start, end, time_sleep=3, progress_bar=True):
        date_list = self.__generate_date_list__(code, start, end)
        date_existed = self.show_dates(code)
        length = len(date_list)
        count = 0
        error_count = 0
        sleep_count = 0
        for date in date_list:
            count += 1
            if date not in date_existed:
                try:
                    time.sleep(time_sleep)
                    self.__get_one_tick__(code, date)
                    error_count = 0
                    sleep_count = 0
                except:
                    error_count += 1
                    if error_count >= 10:
                        time.sleep(300 * np.sqrt(time_sleep))
                        error_count = 0
                        sleep_count += 1
                    if sleep_count >= 10:
                        raise
                    pass
            if progress_bar == True:
                self.__process_monitor__(count / length * 100)
        path = self.__get_directory__(code)
        if len(os.listdir(path)) == 0:
            os.rmdir(path)

    def update(self, code, time_sleep=1, progress_bar=True, quick=False):
        if quick == True:
            start = self.show_dates(code)[-1]
        else:
            start = self.show_dates(code)[0]
        end = self.__date_decoding__(datetime.date.today())
        self.deposit(code, start, end, time_sleep, progress_bar)