import assistant as at
import messenger as ms
import threading, queue

class MACD:

    '''
    Perform the calculation related to MACD
    '''

    def __close_price_list__(self, code, date, smooth, multi_threads=20):
        '''
        Get the price needed for calculation and return both days list and price list
        :param code: str, stock index
        :param date: str, the date
        :param smooth: int, the period taken into calculation
        :return: days list and price list
        '''
        days = (int(smooth / multi_threads) + 1) * multi_threads
        days_list = at.opening_days(code, days, date)
        close_price_list = []
        count = 1
        q = queue.Queue()
        start_pointer = 0
        def catch(code, date, stack):
            hold = ms.get_stock_hist_data(code, date)
            stack.put(hold)
        while start_pointer <= len(days_list) - multi_threads:
            thread = []
            for i in days_list[start_pointer : start_pointer + multi_threads]:
                t = threading.Thread(target=catch, args=(code, i, q))
                thread.append(t)
            for j in thread:
                j.start()
            for k in thread:
                k.join()
            at.process_monitor(count / (int(smooth / multi_threads) + 1) * 100)
            count += 1
            start_pointer += multi_threads
        while not q.empty():
            close_price_list.append(q.get())
        close_price_list = at.sort_list_by_date(close_price_list)
        close_price_list = close_price_list[-smooth:]
        return close_price_list

    def __calculate__(self, code, date, smooth, multi_threads=20):
        '''
        Caculate the MACD and return the data of all the period
        :param code: str, the stock index
        :param date: str, the date
        :param smooth: int, the smooth period
        :return: a list of relevant data within the smooth period
        '''
        close_price_with_date = self.__close_price_list__(code, date, smooth, multi_threads)
        days_list = [i[0] for i in close_price_with_date]
        close_price_list = [i[3] for i in close_price_with_date]
        ema_12_list = [0]
        ema_26_list = [0]
        dea_list = [0]
        diff_list = []
        bar_list = []
        for i in close_price_list:
            ema_12 = float(ema_12_list[-1]) * 11 / 13 + float(i) * 2 / 13
            ema_26 = float(ema_26_list[-1]) * 25 / 27 + float(i) * 2 / 27
            diff = ema_12 - ema_26
            dea = dea_list[-1] * 8 / 10 + diff * 2 / 10
            bar = 2 * (diff - dea)
            ema_12_list.append(ema_12)
            ema_26_list.append(ema_26)
            dea_list.append(dea)
            diff_list.append(diff)
            bar_list.append(bar)
        ema_12_list = ema_12_list[1:]
        ema_26_list = ema_26_list[1:]
        dea_list = dea_list[1:]
        data_list = []
        for i in range(len(days_list)):
            # (ema_12, ema_26, diff, dea, bar)
            data_unit = (days_list[i], (ema_12_list[i], ema_26_list[i], diff_list[i], dea_list[i], bar_list[i]))
            data_list.append(data_unit)
        return data_list

    def macd(self, code, date='', smooth=120, multi_threads=20):
        '''
        Return the macd relatives for a specific day
        :param code: str, the stock code
        :param date: str, the date
        :param smooth: int, the smooth period, default 120
        :return: (macd, diff, dea)
        '''
        macd = self.__calculate__(code, date, smooth, multi_threads)[-1][1]
        # (macd, diff, dea)
        return (macd[-1], macd[-3], macd[-2])

    def macd_of_a_period(self, code, duration, date='', smooth=120, multi_threads=20):
        '''
        Calculate the macd for a period in a less consuming fashion
        :param code: str, the stock code
        :param duration: int, the days demanded
        :param date: str, the date
        :param smooth: int, the smooth period, default 120
        :return: a list with each unit in (date, (macd, diff, dea))
        '''
        calculated_list = self.__calculate__(code, date, smooth + duration, multi_threads)
        macd_list = [(i[0], (i[1][-1], i[1][-3], i[1][-2])) for i in calculated_list[-duration:]]
        return macd_list