import messenger as ms
import assistant as at
import threading, queue, os, math
import matplotlib.pyplot as plt
import matplotlib.finance as mpf
import matplotlib.gridspec as gridspec
from matplotlib.dates import date2num, DateFormatter, WeekdayLocator, DayLocator, MONDAY
import pandas as pd
from scipy.stats.stats import pearsonr

# The data extracted from the tick data
tick_type = {'buy': '买盘', 'sell': '卖盘'}
# The data index when extracting form the hist data
hist_type = {'date': 0, 'code': 1, 'open': 2, 'close': 3, 'high': 4, 'low': 5, 'volume': 6}
# The price used for calculation of the percent changed
reference_price = 'close'
# The support line  in the graph
figure_deviation_line = [-2, -1, 0, 1, 2]
# The smoothing method
smooth = 3
# The smoothing period
leading_smooth = 30
# The default analysis duration
default_range = 30
# The number of threads used when fetching data
threads_of_catch = 20
# The graph height in hundred pixels
graph_height = 10
# A warning displayed when data is incomplete
the_warning = 'Data corrupted'
# Use yesterday's close price when values 1, instead of today's open price
yesterday_close = 1


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
        if yesterday_close == 1:
            hist_y = ms.get_stock_hist_data_yesterday(hist[1], hist[0])
            close_yesterday = float(hist_y[hist_type['close']])
            close = float(hist[hist_type['close']])
            return (close - close_yesterday)
        else:
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
            cash_outflow = tick[tick.type == str(tick_type['sell'])].amount.sum()
        except:
            return float(0)
        return float(cash_inflow - cash_outflow)

    def __weighted_net_cash_flow__(self, tick, outstanding):
        '''
        Calculate the weighted net cash flow of the trading day
        :param tick: a Pandas DataFrame of tick data
        :return: the weighted net cash flow amount
        '''
        try:
            def get_weighted_flow(tick):
                try:
                    weighted_flow = (- math.log(tick['volume'] * 100 / outstanding, math.e) + 1) * tick['amount']
                    return float(weighted_flow)
                except:
                    return float(0)
            tick['weighted'] = tick.apply(get_weighted_flow, axis=1)
            cash_inflow = tick[tick.type == str(tick_type['buy'])].weighted.sum()
            cash_outflow = tick[tick.type == str(tick_type['sell'])].weighted.sum()
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
            volume = float(hist[6])
            turnover = float(volume / outstanding)
            theoretical_change = self.__net_cash_flow__(tick) * (-math.log(turnover, math.e) + 1) / outstanding
            # theoretical_change = self.__weighted_net_cash_flow__(tick, outstanding) / outstanding
        else:
            theoretical_change = float(0)
        open = hist[2]
        close = hist[3]
        high = hist[4]
        low = hist[5]
        volume = hist[6]
        reference = self.__reference_price__(hist)
        diff = self.__price_diff__(actual_change, theoretical_change)
        content = {'date': date, 'code': code, 'open': open, 'close': close, 'high': high, 'low': low, 'volume': volume, \
                   'reference': reference, 'actual change': actual_change, 'theoretical change': theoretical_change, \
                   'difference': diff}
        return content

    def __diff_lists__(self, code, date='', duration=default_range, smooth = smooth, leading_smooth=leading_smooth, threads=threads_of_catch):
        '''
        Generate a list of price differences along the date
        :param code: str, stock index
        :param date: str, date
        :param duration: int, the demanded duration
        :param smooth: int, the smooth method
        :param leading_smooth: int, the leading smooth period
        :param threads: int, the number of threads used
        :return: a list in form of (date, code, open, close, actual_percent, theoretical_percent, diff_percent, smoothed_actual, smoothed_theoretical, smoothed_diff)
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
        if len(origin_list) > 0:
            percent_list = []
            reference_h = origin_list[0]['reference']
            for io in origin_list:
                # (date, code, open, close, reference, actual_change, theoretical_change, diff)
                c_date = io['date']
                c_code = io['code']
                open = io['open']
                close = io['close']
                high = io['high']
                low = io['low']
                volume = io['volume']
                c_actual_change = self.__price_diff_percentage__(io['actual change'], reference_h)
                c_theoretical_change = self.__price_diff_percentage__(io['theoretical change'], reference_h)
                c_diff = self.__price_diff_percentage__(io['difference'], reference_h)
                percent_list_line = {'date': c_date, 'code': c_code, 'open': open, 'close': close, 'high': high, \
                                     'low': low, 'volume': volume, 'actual change': c_actual_change, \
                                     'theoretical change': c_theoretical_change, 'difference': c_diff}
                percent_list.append(percent_list_line)
                reference_h = io['reference']
            smoothed_theoretical = [i['theoretical change'] for i in percent_list]
            smoothed_actual = [i['actual change'] for i in percent_list]
            smoothed_change = [i['difference'] for i in percent_list]
            smoothed_theoretical = self.__smooth__(smoothed_theoretical, smooth)
            smoothed_change = self.__smooth__(smoothed_change, smooth)
            for ip in range(len(percent_list)):
                percent_list[ip]['smoothed actual'] = smoothed_actual[ip]
                percent_list[ip]['smoothed theoretical'] = smoothed_theoretical[ip]
                percent_list[ip]['smoothed difference'] = smoothed_change[ip]
            return percent_list[-duration:]
        else: return None

    def __diff_lists_multi_smoothing__(self, code, smooth, date='', duration=default_range, leading_smooth=leading_smooth, threads=threads_of_catch):
        '''
        Generate a list of price differences along the date with multi-smoothing
        :param code: str, stock index
        :param date: str, date
        :param duration: int, the demanded duration
        :param smooth: list, the smooth method
        :param leading_smooth: int, the leading smooth period
        :param threads: int, the number of threads used
        :return: a list in form of (date, code, open, close, actual_percent, theoretical_percent, diff_percent, smoothed_actual, smoothed_theoretical, smoothed_diff)
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
        if len(origin_list) > 0:
            percent_list = []
            reference_h = origin_list[0]['reference']
            for io in origin_list:
                # (date, code, open, close, reference, actual_change, theoretical_change, diff)
                c_date = io['date']
                c_code = io['code']
                open = io['open']
                close = io['close']
                high = io['high']
                low = io['low']
                volume = io['volume']
                c_actual_change = self.__price_diff_percentage__(io['actual change'], reference_h)
                c_theoretical_change = self.__price_diff_percentage__(io['theoretical change'], reference_h)
                c_diff = self.__price_diff_percentage__(io['difference'], reference_h)
                percent_list_line = {'date': c_date, 'code': c_code, 'open': open, 'close': close, 'high': high, \
                                     'low': low, 'volume': volume, 'actual change': c_actual_change, \
                                     'theoretical change': c_theoretical_change, 'difference': c_diff}
                percent_list.append(percent_list_line)
                reference_h = io['reference']
            smoothed_theoretical_holder = [i['theoretical change'] for i in percent_list]
            smoothed_actual = [i['actual change'] for i in percent_list]
            smoothed_change_holder = [i['difference'] for i in percent_list]
            smoothed_theoretical = []
            smoothed_change = []
            for ism in smooth:
                smoothed_theoretical.append(self.__smooth__(smoothed_theoretical_holder, ism))
                smoothed_change.append(self.__smooth__(smoothed_change_holder, ism))
            for ip in range(len(percent_list)):
                percent_list[ip]['smoothed actual'] = smoothed_actual[ip]
                for ismx in range(len(smoothed_theoretical)):
                    percent_list[ip]['smoothed theoretical %s' % smooth[ismx]] = smoothed_theoretical[ismx][ip]
                    percent_list[ip]['smoothed difference %s' % smooth[ismx]] = smoothed_change[ismx][ip]
            return percent_list[-duration:]
        else: return None

    def show_difference(self, code, date=''):
        '''
        Show the difference in percent between actual and theoretical price
        :param code: str, stock index
        :param date: str, date
        :return: the actual price change percent, theoretical price change percent and percent of difference
        '''
        date = self.__opening_dates__(code, 1, date)
        list = self.__measure_diff__(code, date)
        reference_price = list['reference']
        theo_change = list['theoretical change']
        actual_change = list['actual change']
        diff = list['difference']
        theo_change_percent = self.__price_diff_percentage__(theo_change, reference_price)
        actual_change_percent = self.__price_diff_percentage__(actual_change, reference_price)
        diff_percent = self.__price_diff_percentage__(diff, reference_price)
        return (actual_change_percent, theo_change_percent, diff_percent)

    def show_difference_list(self, code, date='', duration=default_range, smooth = smooth, leading_smooth=leading_smooth, threads=threads_of_catch):
        '''
        Generate a list of price difference and other information
        :param code: str, stock index
        :param date: str, date
        :param duration: int, the analysis duration
        :param smooth: int, the smooth method
        :param leading_smooth: int, the leading smooth period
        :param threads: int, the number of threads used
        :return: a list in form (date, code, close_price, actual_percent, theoretical_percent, diff_percent)
        '''
        #(date, code, open, close, actual, theoretical, diff, smoothed)
        list = self.__diff_lists__(code, date, duration, smooth, leading_smooth, threads)
        output_list = []
        if list != None:
            for i in range(len(list)):
                o_date = list[i]['date']
                o_code = list[i]['code']
                o_close = list[i]['close']
                o_theo_smoothed = list[i]['smoothed theoretical']
                o_diff_smoothed = list[i]['smoothed difference']
                output_list.append((o_date, o_code, o_close, o_theo_smoothed, o_diff_smoothed))
            return output_list
        else:
            print(the_warning)

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
            x = [i['smoothed difference'] for i in list]
        else:
            x = [i['smoothed difference'] for i in list[:-trace_back]]
        y = [float(i['close']) for i in list[trace_back:]]
        return pearsonr(x, y)

    def plot_difference(self, code, date='', duration=default_range, smooth = smooth, leading_smooth=leading_smooth, threads=threads_of_catch, period_length = 0, type='show', height = graph_height):
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
        if period_length == 0:
            period_length = duration
        periods_list = at.split_period(date, duration, period_length)
        for i in periods_list:
            date = i['start_date']
            duration = i['days']
            #(date, code, open, close, actual, theoretical, diff, smoothed)
            list = self.__diff_lists__(code, date, duration, smooth, leading_smooth, threads)
            if list != None:
                x_date = [date2num(at.date_encoding(i['date'])) for i in list]
                max_volume = max([i['volume'] for i in list])
                y_price = [(date2num(at.date_encoding(i['date'])), i['open'], i['close'], i['high'], i['low']) for i in list]
                y_deviation = [i['smoothed difference'] for i in list]
                y_theo = [i['smoothed theoretical'] for i in list]
                y_theo = [i for i in y_theo]
                y_volume = [(date2num(at.date_encoding(i['date'])), i['open'], i['high'], i['low'], i['close'], i['volume'] / max_volume) for i in list]
                support_line = []
                for i in range(len(figure_deviation_line)):
                    support_line.append([figure_deviation_line[i] for k in list])
                # fig, price = plt.subplots()
                fig = plt.figure()
                sub_plots = gridspec.GridSpec(2, 1, height_ratios=[5,1])
                sub_plots.update(wspace=0.001, hspace=0.001)
                price = plt.subplot(sub_plots[0])
                price.xaxis_date()

                mondays = WeekdayLocator(MONDAY)
                alldays = DayLocator()
                weekFormatter = DateFormatter('%b %d')
                price.xaxis.set_major_locator(mondays)
                price.xaxis.set_minor_locator(alldays)
                price.xaxis.set_major_formatter(weekFormatter)
                price.xaxis_date()

                deviation = price.twinx()
                volume = plt.subplot(sub_plots[1], sharex = price)
                mpf.candlestick_ochl(price, y_price, width=0.8, colorup='r', colordown='g', alpha=0.8)
                deviation.plot(x_date, y_deviation, 'g')
                deviation.plot(x_date, y_theo, 'y')
                for j in support_line:
                    deviation.plot(x_date, j, 'y:')
                price.set_ylabel('price')
                price.get_xaxis().set_visible(False)
                deviation.set_ylabel('deviation')
                mpf.volume_overlay3(volume, y_volume, width=10, colorup='r', colordown='g', alpha=0.8)
                volume.get_yaxis().set_visible(False)
                volume.set_xlabel("%s %s %i" %(code, list[-1]['date'], smooth))
                volume.set_ylim(0, 1)

                if type == "show":
                    plt.show()
                if type == "save":
                    try:
                        os.mkdir(os.path.join(os.getcwd(), 'graph'))
                    except:
                        pass
                    path = os.path.join(os.getcwd(), 'graph/%s-%s-%i-%i.png'%(code, list[-1]['date'], duration, smooth))
                    fig.set_size_inches(math.sqrt(int(duration)) * height / 3, height)
                    plt.savefig(path)
            else:
                print(the_warning)

    def plot_difference_multi_smoothing(self, code, smooth, date='', duration=default_range, leading_smooth=leading_smooth, threads=threads_of_catch, period_length = 0, type='show', height = graph_height):
        '''
        Plot the difference with multiple smoothing method
        :param code: str, stock index
        :param date: str, date
        :param duration: int, the analysis duration
        :param smooth: list, the smooth method
        :param leading_smooth: int, the leading smooth period
        :param threads: int, the number of threads used
        :param type: show or save the figure
        :return: None
        '''
        if period_length == 0:
            period_length = duration
        periods_list = at.split_period(date, duration, period_length)
        for i in periods_list:
            date = i['start_date']
            duration = i['days']
            #(date, code, open, close, actual, theoretical, diff, smoothed)
            list = self.__diff_lists_multi_smoothing__(code, smooth, date, duration, leading_smooth, threads)
            if list != None:
                x_date = [date2num(at.date_encoding(i['date'])) for i in list]
                max_volume = max([i['volume'] for i in list])
                y_price = [(date2num(at.date_encoding(i['date'])), i['open'], i['close'], i['high'], i['low']) for i in list]
                y_deviation_list = {}
                for idv in smooth:
                    y_deviation_list['smoothed difference %s'%idv] = [i['smoothed difference %s'%idv] for i in list]
                # y_deviation = [i['smoothed difference'] for i in list]
                # y_theo = [i['smoothed theoretical'] for i in list]
                # y_theo = [i for i in y_theo]
                y_volume = [(date2num(at.date_encoding(i['date'])), i['open'], i['high'], i['low'], i['close'], i['volume'] / max_volume) for i in list]
                support_line = []
                for i in range(len(figure_deviation_line)):
                    support_line.append([figure_deviation_line[i] for k in list])
                # fig, price = plt.subplots()
                fig = plt.figure()
                sub_plots = gridspec.GridSpec(2, 1, height_ratios=[5,1])
                sub_plots.update(wspace=0.001, hspace=0.001)
                price = plt.subplot(sub_plots[0])
                price.xaxis_date()

                mondays = WeekdayLocator(MONDAY)
                alldays = DayLocator()
                weekFormatter = DateFormatter('%b %d')
                price.xaxis.set_major_locator(mondays)
                price.xaxis.set_minor_locator(alldays)
                price.xaxis.set_major_formatter(weekFormatter)
                price.xaxis_date()

                deviation = price.twinx()
                volume = plt.subplot(sub_plots[1], sharex = price)
                mpf.candlestick_ochl(price, y_price, width=0.8, colorup='r', colordown='g', alpha=0.8)

                def pick_clor(color_list, idx):
                    length = len(color_list)
                    try:
                        if idx == 0:
                            return color_list[0]
                        else:
                            return color_list[idx % length]
                    except:
                        return color_list[0]

                color_list = ['g', 'y', 'b', 'r']
                for idvc in range(len(smooth)):
                    deviation.plot(x_date, y_deviation_list['smoothed difference %s'%smooth[idvc]], pick_clor(color_list, idvc))
                for j in support_line:
                    deviation.plot(x_date, j, 'y:')
                price.set_ylabel('price')
                price.get_xaxis().set_visible(False)
                deviation.set_ylabel('deviation')
                mpf.volume_overlay3(volume, y_volume, width=10, colorup='r', colordown='g', alpha=0.8)
                volume.get_yaxis().set_visible(False)
                smooth_tag = '-'.join([str(i) for i in smooth])
                volume.set_xlabel("%s %s %s" %(code, list[-1]['date'], smooth_tag))
                volume.set_ylim(0, 1)
                if type == "show":
                    plt.show()
                if type == "save":
                    try:
                        os.mkdir(os.path.join(os.getcwd(), 'graph'))
                    except:
                        pass
                    path = os.path.join(os.getcwd(), 'graph/%s-%s-%i-%s.png'%(code, list[-1]['date'], duration, smooth_tag))
                    fig.set_size_inches(math.sqrt(int(duration)) * height / 3, height)
                    plt.savefig(path)
            else:
                print(the_warning)