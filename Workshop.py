import Messenger
import Toolbox
import math, datetime

class KDJ:

    def series_of_data(self, code, days=9, start_date=''):
        '''
        Generate a series of data for the duration demanded
        :param code: str, stock index
        :param days: int, the duration
        :param start_date: str, the start date
        :return: a list contains the data for each days
        '''
        days_list = Toolbox.number_of_days_before(code, days, start_date)
        data_list = []
        for i in days_list:
            data = Messenger.get_stock_hist_data(code, i)
            data_list.append(data)
        return data_list

    def less(self, value1, value2):
        '''
        A fuction to return the smaller value
        :param value1:
        :param value2:
        :return: the smaller value
        '''
        if float(value2) < float(value1):
            return True

    def more(self, value1, value2):
        '''
        A function to return the larger value
        :param value1:
        :param value2:
        :return: the larger value
        '''
        if float(value2) > float(value1):
            return True

    def rsv(self, code, date='', method=9):
        '''
        Calculate the rsv for for the date needed
        :param code: str, stock index
        :param date: str, the date of rsv calculated, default today
        :param method: the range took into the calculation, default 9 days
        :return: the rsv value
        '''
        list = self.series_of_data(code, method, date)
        extract_list = []
        for i in list:
            extract_list += i[2:6]
        c = float(list[0][3])
        l = float(Toolbox.pick_out(extract_list, self.less))
        h = float(Toolbox.pick_out(extract_list, self.more))
        rsv = (c - l) / (h - l) * 100
        return rsv

    def kdj(self, code, date='', method=9, smooth=30):
        '''
        Return the (k, d, j) given a specific time
        :param code: str, stock index
        :param date: str, the date needed
        :param method: the range took into the calculation, default 9 days
        :param smooth: the smooth period, default 30 days
        :return: the value, (k, d, j)
        '''
        rsv_list = []
        days_list = Toolbox.number_of_days_before(code, smooth, date)
        count = 1
        for i in days_list:
            rsv_h = self.rsv(code, i, method)
            rsv_list.append(rsv_h)
            Toolbox.process_monitor(count / len(days_list) * 100)
            count += 1
        k_line = [50]
        d_line = [50]
        for j in rsv_list[::-1]:
            k_hold = j / 3 + 2 * k_line[-1] / 3
            k_line.append(k_hold)
            d_hold = k_line[-1] / 3 + 2 * d_line[-1] / 3
            d_line.append(d_hold)
        k = k_line[-1]
        d = d_line[-1]
        j = 3 * k - 2 * d
        return (k, d, j)

    def kdj_of_a_period(self, code, duration, start_date='', method = 9, smooth=30):
        '''
        Calculate a series of kdj in a relatively less consuming manner
        :param code: str, stock index
        :param duration: int, the duration of the period demanded
        :param start_date: str, the start date
        :param method: the range took into calculation, default 9 days
        :param smooth: the smooth period, default 30 days
        :return: a series of kdj in a form of (date, (k, d, j))
        '''
        rsv_list = []
        days_list = Toolbox.number_of_days_before(code, smooth + duration, start_date)
        count = 1
        for i in days_list:
            rsv_h = self.rsv(code, i, method)
            rsv_list.append(rsv_h)
            Toolbox.process_monitor(count / len(days_list) * 100)
            count += 1
        k_line = [50]
        d_line = [50]
        for j in rsv_list[::-1]:
            k_hold = j / 3 + 2 * k_line[-1] / 3
            k_line.append(k_hold)
            d_hold = k_line[-1] / 3 + 2 * d_line[-1] / 3
            d_line.append(d_hold)
        output_list = []
        for io in range(duration):
            date = days_list[::-1][io - duration]
            k = k_line[io - duration]
            d = d_line[io - duration]
            j = 3 * k - 2 * d
            output_list.append((date, (k, d, j)))
        return output_list

