import Messenger
import Toolbox
import math, datetime

class KDJ:

    def series_of_data(self, code, days=9, start_date=''):
        days_list = Toolbox.number_of_days_before(code, days, start_date)
        data_list = []
        for i in days_list:
            data = Messenger.get_stock_hist_data(code, i)
            data_list.append(data)
        return data_list

    def less(self, value1, value2):
        if value2 < value1:
            return True

    def more(self, value1, value2):
        if value2 > value1:
            return True

    def rsv(self, code, days=9, start_date=''):
        list = self.series_of_data(code, days, start_date)
        extract_list = []
        for i in list:
            extract_list += i[2:6]
        c = float(list[0][3])
        l = float(Toolbox.pick_out(extract_list, self.less))
        h = float(Toolbox.pick_out(extract_list, self.more))
        rsv = (c - l) / (h - l) * 100
        return rsv

    def k(self, code, days=9, start_date=''):
        three_days = Toolbox.number_of_days_before(code, 3, start_date)
        k_list = []
        for i in three_days:
            k_list.append(self.rsv(code, days, i))

