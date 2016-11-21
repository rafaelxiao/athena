import messenger as ms
import assistant as at
import threading, queue, os
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr

# The data extracted from the tick data
tick_type = {'buy': '买盘', 'sell': '卖盘'}
# The data index when extracting form the hist data
hist_type = {'date': 0, 'code': 1, 'open': 2, 'close': 3, 'high': 4, 'low': 5, 'volume': 6}
# The price used for calculation of the percent changed
reference_price = 'close'
# The support line  in the graph
figure_deviation_line = [-1, 0, 1]
# The smoothing method
smooth = 3
# The smoothing period
leading_smooth = 30
# The default analysis duration
default_range = 30
# The number of threads used when fetching data
threads_of_catch = 20


class PriceDeviation:

    def __get_hist_data__(self, code, date):
        '''
        Import the hist data
        :param code: str, stock index
        :param date: str, date
        :return: a list of hist data in form (date, code, open, close, high, low, volume)
        '''
        hist = ms.get_stock_hist_data(code, date)
        return hist

    def __get_tick_data__(self, code, date):
        '''
        Import the tick data
        :param code: str, stock index
        :param date: str, date
        :return: a Pandas DataFrame of tick data
        '''
        tick = ms.get_tick_data(code, date)
        return tick

    def __price_change__(self, hist):
        '''
        Return the price change in the trading day
        :param hist: list in form (date, code, open, close, high, low, volume)
        :return: the price change
        '''
        open = float(hist[hist_type['open']])
        close = float(hist[hist_type['close']])
        return (close - open)

    def __reference_price__(self, hist):
        '''
        Return the denominator when calculating percent changed
        :param hist: list in form (date, code, open, close, high, low, volume)
        :return: the reference price
        '''
        reference = float(hist[hist_type[reference_price]])
        return reference

    def __net_cash_flow__(self, tick):
        '''
        Calculate the net cash flow of the trading day
        :param tick: a Pandas DataFrame of tick data
        :return: the net cash flow amount
        '''
        try:
            cash_inflow = tick[tick.type == str(tick_type['buy'])].amount.sum()
            cash_outflow = tick[tick.type == tick_type['sell']].amount.sum()
        except:
            return float(0)
        return float(cash_inflow - cash_outflow)

    def __stock_outstanding__(self, code, date='', outstanding=0):
        '''
        Get the stock outstanding
        :param code: str, stock index
        :param date: for use in the following functions
        :param outstanding: use to control whether providing a outstanding number directly
        :return: int, the stock outstanding
        '''
        if outstanding == 0:
            outstanding = ms.get_stock_outstanding(code)
        return outstanding

    def __price_diff__(self, actual, theoretical):
        '''
        Calculate the difference between actual and theoretical price change
        :param actual: the actual price change of the trading day
        :param theoretical: the theoretical price change calculated by cash flow
        :return: float, the price difference
        '''
        if actual >= theoretical:
            direction = 1
        else:
            direction = -1
        drive = abs(actual - theoretical) * direction
        return drive

    def __price_diff_percentage__(self, diff, reference):
        '''
        Calculate percentage of price change using reference price
        :param diff: the price difference
        :param reference: the reference price
        :return: the percent
        '''
        if reference == 0:
            return 0
        else:
            return diff / reference * 100

    def __opening_dates__(self, code, days, date=''):
        '''
        Get the opening trading days
        :param code: str, stock index
        :param days: int, the duration
        :param date: str, start date
        :return: a list of opening days
        '''
        days = at.opening_days(code, days, date)
        if len(days) == 1:
            return days[0]
        else:
            return days

    def __smooth__(self, list, smooth):
        '''
        The smooth procedure for the calculated figures
        :param list: a list of figures
        :param smooth: the smooth period
        :return: the smoothed list
        '''
        if smooth==0:
            smooth = 1
        hold = list[0]
        output = []
        for i in list:
            i = float(i)
            value = (smooth - 1) / smooth * hold + 1 / smooth * i
            output.append(value)
            hold = value
        return output

    def __measure_diff__(self, code, date, outstanding=0):
        '''
        Calculated the price difference and return the a comprehensive list
        :param code: str, stock index
        :param date: str, date
        :param outstanding: int, the stock outstanding
        :return: a list in form (date, code, open, close, reference, actual_change, theoretical_change, diff)
        '''
        # A function to get hist or tick data
        def hist_or_tick(code, date, f, queue,):
            content = f(code, date)
            queue.put(content)
        # A function to return stock outstanding
        def get_outstanding(code, date, f, queue, outstanding=outstanding):
            if outstanding == 0:
                content = f(code, date)
                queue.put(content)
            else:
                queue.put(outstanding)
        hist = []
        tick = []
        outstanding = 0
        # Multi-threading
        hist_q = queue.Queue()
        tick_q = queue.Queue()
        outstanding_q = queue.Queue()
        t1 = threading.Thread(target=hist_or_tick, args=(code, date, self.__get_hist_data__, hist_q))
        t2 = threading.Thread(target=hist_or_tick, args=(code, date, self.__get_tick_data__, tick_q))
        t3 = threading.Thread(target=get_outstanding, args=(code, date, self.__stock_outstanding__, outstanding_q))
        t1.start()
        t2.start()
        t3.start()
        t1.join()
        t2.join()
        t3.join()
        while not hist_q.empty():
            hist = hist_q.get()
        while not tick_q.empty():
            tick = tick_q.get()
        while not outstanding_q.empty():
            outstanding = outstanding_q.get()
        actual_change = self.__price_change__(hist)
        if outstanding != 0:
            theoretical_change = self.__net_cash_flow__(tick) / outstanding
        else:
            theoretical_change = float(0)
        open = hist[2]
        close = hist[3]
        reference = self.__reference_price__(hist)
        diff = self.__price_diff__(actual_change, theoretical_change)
        return (date, code, open, close, reference, actual_change, theoretical_change, diff)

    def __diff_lists__(self, code, date='', duration=default_range, smooth = smooth, leading_smooth=leading_smooth, threads=threads_of_catch):
        '''
        Generate a list of price differences along the date
        :param code: str, stock index
        :param date: str, date
        :param duration: int, the demanded duration
        :param smooth: int, the smooth method
        :param leading_smooth: int, the leading smooth period
        :param threads: int, the number of threads used
        :return: a list in form of (date, code, open, close, actual_percent, theoretical_percent, diff_percent])
        '''
        def catch(code, date, outstanding, f, queue):
            content = f(code, date, outstanding)
            queue.put(content)
        # Generate a days list that is the integral multiple of the threads
        forwarding_days = (int((duration + leading_smooth) / threads + 1) * threads)
        days_list = (self.__opening_dates__(code, forwarding_days, date))
        # Multi-threading with looping
        q = queue.Queue()
        origin_list = []
        pointer = 0
        outstanding = ms.get_stock_outstanding(code)
        while pointer <= len(days_list) - threads:
            thread = []
            for i in days_list[pointer : pointer + threads]:
                t = threading.Thread(target=catch, args=(code, i, outstanding, self.__measure_diff__, q))
                thread.append(t)
            for j in thread:
                j.start()
            for k in thread:
                k.join()
            at.process_monitor((pointer + threads) / len(days_list) * 100)
            pointer += threads
        while not q.empty():
            origin_list.append(q.get())
        origin_list = at.sort_list_by_date(origin_list)
        # Re-construct for the final output list
        percent_list = []
        reference_h = origin_list[0][4]
        for io in origin_list:
            # (date, code, open, close, reference, actual_change, theoretical_change, diff)
            c_date = io[0]
            c_code = io[1]
            open = io[2]
            close = io[3]
            c_actual_change = self.__price_diff_percentage__(io[5], reference_h)
            c_theoretical_change = self.__price_diff_percentage__(io[6], reference_h)
            c_diff = self.__price_diff_percentage__(io[7], reference_h)
            percent_list.append([c_date, c_code, open, close, c_actual_change, c_theoretical_change, c_diff])
            reference_h = io[4]
        smoothed_change = [i[-1] for i in percent_list]
        smoothed_change = self.__smooth__(smoothed_change, smooth)
        for ip in range(len(percent_list)):
            percent_list[ip].append(smoothed_change[ip])
        return percent_list[-duration:]

    def show_difference(self, code, date=''):
        '''
        Show the difference in percent between actual and theoretical price
        :param code: str, stock index
        :param date: str, date
        :return: the difference in percent
        '''
        date = self.__opening_dates__(code, 1, date)
        list = self.__measure_diff__(code, date)
        reference_price = list[4]
        diff = list[7]
        diff_percent = self.__price_diff_percentage__(diff, reference_price)
        return diff_percent

    def show_difference_list(self, code, date='', duration=default_range, smooth = smooth, leading_smooth=leading_smooth, threads=threads_of_catch):
        '''
        Generate a list of price difference and other information
        :param code: str, stock index
        :param date: str, date
        :param duration: int, the analysis duration
        :param smooth: int, the smooth method
        :param leading_smooth: int, the leading smooth period
        :param threads: int, the number of threads used
        :return: a list in form (date, code, close_price, diff_percent)
        '''
        #(date, code, open, close, actual, theoretical, diff, smoothed)
        list = self.__diff_lists__(code, date, duration, smooth, leading_smooth, threads)
        output_list = []
        for i in list:
            o_date = i[0]
            o_code = i[1]
            o_close = i[3]
            o_diff_percent = i[7]
            output_list.append((o_date, o_code, o_close, o_diff_percent))
        return output_list

    def show_correlation(self, code, trace_back = 1, date='', duration=default_range, smooth = smooth, leading_smooth=leading_smooth, threads=threads_of_catch):
        '''
        Calculated the correlation between price difference and actual price
        :param code: str, stock index
        :param trace_back: the trace back days
        :param date: str, date
        :param duration: int, the analysis period
        :param smooth: int, the smooth method
        :param leading_smooth: int, the leading smooth period
        :param threads: int, the number of threads used
        :return: the correlation and p_value
        '''
        list = self.__diff_lists__(code, date, duration, smooth, leading_smooth, threads)
        if trace_back < 0:
            trace_back = 0
        if trace_back == 0:
            x = [i[-1] for i in list]
        else:
            x = [i[-1] for i in list[:-trace_back]]
        y = [float(i[3]) for i in list[trace_back:]]
        return pearsonr(x, y)

    def plot_difference(self, code, date='', duration=default_range, smooth = smooth, leading_smooth=leading_smooth, threads=threads_of_catch, type='show'):
        '''
        Plot the difference with price
        :param code: str, stock index
        :param date: str, date
        :param duration: int, the analysis duration
        :param smooth: int, the smooth method
        :param leading_smooth: int, the leading smooth period
        :param threads: int, the number of threads used
        :param type: show or save the figure
        :return: None
        '''
        #(date, code, open, close, actual, theoretical, diff, smoothed)
        list = self.__diff_lists__(code, date, duration, smooth, leading_smooth, threads)
        x_date = [at.date_encoding(i[0]) for i in list]
        y_price = [i[3] for i in list]
        y_deviation = [i[7] for i in list]
        y_deviation_mid = [figure_deviation_line[1] for i in list]
        y_deviation_up = [figure_deviation_line[2] for i in list]
        y_deviation_down = [figure_deviation_line[0] for i in list]
        fig, price = plt.subplots()
        deviation = price.twinx()
        price.plot(x_date, y_price, 'b-')
        deviation.plot(x_date, y_deviation, 'g--')
        deviation.plot(x_date, y_deviation_up, 'y:')
        deviation.plot(x_date, y_deviation_down, 'y:')
        deviation.plot(x_date, y_deviation_mid, 'y:')
        price.set_xlabel("%s %s %i" %(code, list[-1][0], smooth))
        price.set_ylabel('price', color='b')
        deviation.set_ylabel('deviation', color='g')
        if type == "show":
            plt.show()
        if type == "save":
            try:
                os.mkdir(os.path.join(os.getcwd(), 'graph'))
            except:
                pass
            path = os.path.join(os.getcwd(), 'graph/%s-%s-%i.png'%(code, list[-1][0], smooth))
            plt.savefig(path)



