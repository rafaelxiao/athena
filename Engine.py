import math, datetime, time
import Messenger, Toolbox

def turnover(volume, code):
    '''
    Calculate the volume to outstanding ratio
    :param volume: int, the volume of transaction
    :param code: string, the stock index
    :return: float, the volume to outstanding ratio
    '''
    outstanding = Messenger.get_stock_outstanding(code)
    ratio = float(volume / outstanding)
    return ratio

def periodic_auction_volume(code, date):
    '''
    Get the volume during the periodic auction period
    :param code: string, stock index
    :param date: string, date in format '2016-10-11'
    :return: int, the volume
    '''
    tick_data = Messenger.get_tick_data(code, date)
    volume = tick_data[-1:].volume.values[0]
    if math.isnan(volume):
        volume = 0
    volume = 100 * volume
    volume = int(volume)
    return volume

class SmartMoney:
    '''
    Calculate the smart money emotion score
    '''

    def subset_tick_data(self, tick_data):
        '''
        Subsetting the tick data by each minute with transaction.
        :param tick_data: tick data in pandas frame format
        :return: a list groupby minutes, in (time_stamp, price, shares)
        '''
        sets = []
        time_sets = []
        for num in range(0, len(tick_data)-1):
            i = tick_data[num:num+1]
            hour = i.time.values[0][:2]
            minute = i.time.values[0][3:5]
            time_stamp = (hour, minute)
            if len(time_sets) == 0:
                time_sets.append([time_stamp, i.price.values[0], i.volume.values[0] * 100])
            else:
                if time_stamp == time_sets[-1][0]:
                    time_sets.append([time_stamp, i.price.values[0], i.volume.values[0] * 100])
                else:
                    sets.append(time_sets)
                    time_sets = []
                    time_sets.append([time_stamp, i.price.values[0], i.volume.values[0] * 100])
        return sets

    def range_in_duration(self, sub_set):
        '''
        Calculate the price range in a duration(subset)
        :param sub_set: the subsetted list
        :return: the price range
        '''
        min = 0
        max = 0
        for i in sub_set:
            if min == 0 and max == 0:
                min = i[1]
                max = i[1]
            elif i[1] < min:
                min = i[1]
            elif i[1] > max:
                max = i[1]
            else: pass
        range = abs(max - min)
        return range

    def volume_in_duration(self, sub_set):
        '''
        Calculate the volume in a duration(subset)
        :param sub_set: the subsetted list
        :return: the volume
        '''
        volume = 0
        for i in sub_set:
            volume += i[2]
        return volume

    def smart_level_of_duration(self, sub_set):
        '''
        Calculate the smart level of the duration(subset)
        :param sub_set: the subsetted list
        :return: the smart level
        '''
        range = self.range_in_duration(sub_set)
        volume = self.volume_in_duration(sub_set)
        smart_score = range / math.sqrt(volume)
        return smart_score

    def total_value_in_duration(self, sub_set):
        '''
        Calculate the total cash value of the duration(subset)
        :param sub_set: the subsetted list
        :return: the total cash value
        '''
        total_value = 0
        for i in sub_set:
            total_value += i[1] * i[2]
        return total_value

    def transform_set(self, set):
        '''
        Transform the set in a reorganized form
        :param set: the processed tick data
        :return: the transformed set
        '''
        transformed_set = []
        for i in set:
            time_stamp = i[0][0]
            volume = self.volume_in_duration(i)
            total_value = self.total_value_in_duration(i)
            smart_level = self.smart_level_of_duration(i)
            if math.isnan(smart_level) or math.isinf(smart_level):
                smart_level = 0.0
            transformed_set.append((time_stamp, volume, total_value, smart_level))
        return transformed_set

    def bubble_sort(self, transformed_set, attrs):
        '''
        Sort based on specific attribute
        :param transformed_set: the transformed set
        :return: the re-ordered set
        '''
        length = len(transformed_set)
        while length > 0:
            for i in range(length-1):
                if transformed_set[i][attrs] > transformed_set[i+1][attrs]:
                    hold = transformed_set[i+1]
                    transformed_set[i+1] = transformed_set[i]
                    transformed_set[i] = hold
            length -= 1

    def weighted_price(self, transformed_set):
        '''
        Calculate the weighted price in a set
        :param transformed_set: the transformed set
        :return: the weighted price
        '''
        volume = 0
        total_value = 0
        for i in transformed_set:
            volume += i[1]
            total_value += i[2]
        weight_price = total_value / volume
        return weight_price

    def emotion_factor(self, sorted_set):
        '''
        Calculate the smart money emotion score
        :param tranformed_set: the sorted set
        :return: the emotion score
        '''
        weighted_for_all = self.weighted_price(sorted_set)
        weighted_for_smart = self.weighted_price(sorted_set[int(len(sorted_set) * 0.8):])
        emotion_factor = weighted_for_smart / weighted_for_all
        return emotion_factor

    def calculate_smart_money_emotion(self, code, date):
        '''
        Calculate the smart money emotion score from stock index and date
        :param code: the stock index
        :param date: string, the desired date
        :return: the emotion score
        '''
        tick_data = Messenger.get_tick_data(code, date)
        subset = self.subset_tick_data(tick_data)
        transformed_set = self.transform_set(subset)
        self.bubble_sort(transformed_set, 3)
        smart_money_emotion = self.emotion_factor(transformed_set)
        return smart_money_emotion

    def high_time(self, code, date):
        '''
        Identify the high time when smart money are active
        :param code: the stock index
        :param date: string, the desired date
        :return: the list when smart money are active
        '''
        tick_data = Messenger.get_tick_data(code, date)
        subset = self.subset_tick_data(tick_data)
        transformed_set = self.transform_set(subset)
        self.bubble_sort(transformed_set, 3)
        high_time_list = transformed_set[int(len(transformed_set) * 0.8):]
        self.bubble_sort(high_time_list, 0)
        return high_time_list

class Stock:
    '''
    A presentation of a stock hold
    '''

    def initiate_a_stock(self, code, price, volume):
        '''
        Initiate a stock with a data structure (code, price, volume)
        :param code: str, stock index
        :param price: float, the price of the stock
        :param volume: int, the volume of the stock
        :return: a set, (code, price, volume)
        '''
        return (code, price, volume)

    def select_stock_code(self, stock):
        '''
        Selector, select the stock code
        :param stock: the Stock data structure
        :return: str, the stock hold
        '''
        return stock[0]

    def select_stock_volume(self, stock):
        '''
        Selector, select the stock volume
        :param stock: the Stock data structure
        :return: int, the stock volume
        '''
        return stock[2]

    def select_stock_price(self, stock):
        '''
        Selector, select the stock price
        :param stock: the Stock data structure
        :return: float, the stock price
        '''
        return stock[1]

    def value_a_stock(self, stock):
        '''
        Get the value of a stock
        :param stock:  the Stock data structure
        :return: float, the value of the stock
        '''
        return stock[1] * stock[2]

    def add_into_a_stock(self, stock1, stock2):
        '''
        Add stock1 into the stock2 and generate a new Stock(data structure)
        :param stock1: Stock data structure
        :param stock2: Stock data structure
        :return: a new Stock data structure
        '''
        code = self.select_stock_code(stock1)
        value = self.value_a_stock(stock1) + self.value_a_stock(stock2)
        volume = self.select_stock_volume(stock1) + self.select_stock_volume(stock2)
        if volume != 0:
            price = value / volume
        else: price = 0
        return self.initiate_a_stock(code, price, volume)

    def retrive_from_a_stock(self, stock1, stock2):
        '''
        Retrieve stock1 into the stock2 and generate a new Stock(data structure)
        :param stock1: Stock data structure
        :param stock2: Stock data structure
        :return: a new Stock data structure
        '''
        code = self.select_stock_code(stock1)
        value = self.value_a_stock(stock2) - self.value_a_stock(stock1)
        volume = self.select_stock_volume(stock2) - self.select_stock_volume(stock1)
        if volume != 0:
            price = value / volume
        else: price = 0
        return self.initiate_a_stock(code, price, volume)

class StockAccount(Stock):
    '''
    A stock account with functionality
    '''

    def __init__(self):
        '''
        Initiate the StockAccount, with float represent cash & original_cash, set represent stock hold
        :return: None
        '''
        self.original_cash = float()
        self.cash = float()
        self.stock_hold = []

    def find_stock(self, stock):
        '''
        Search a stock from the stock hold set to see if it is exist
        :param stock: a Stock data structure
        :return: the index if existed, otherwise -1
        '''
        if (len(self.stock_hold)) >= 1:
            for i in range(len(self.stock_hold)):
                if self.select_stock_code(stock) == self.select_stock_code(self.stock_hold[i]):
                    return i
            return -1
        else: return -1

    def clean_stock_hold(self):
        '''
        Clear the stock that is empty from the stock hold
        :return: None
        '''
        for i in self.stock_hold:
            if i[2] == 0:
                idx = self.find_stock(i)
                del self.stock_hold[idx]

    def value_stock_hold(self, stock_hold_list):
        '''
        Valuate the all the stock hold
        :param stock_hold_list: the stock hold list needed to be valued
        :return: float, the value
        '''
        balance = 0
        for i in stock_hold_list:
            balance += self.value_a_stock(i)
        return balance

    def deposit_cash(self, amount):
        '''
        The procedure to deposit cash into the account
        :param amount: float, the cash amount
        :return: None
        '''
        self.cash += amount
        self.original_cash += amount

    def withdraw_cash(self, amount):
        '''
        The procedure to withdraw cash from the account
        :param amount: float, the cash amount
        :return: None
        '''
        if amount > self.cash:
            amount = self.cash
        self.cash -= amount
        self.original_cash -= amount
        return amount

    def investment_return(self):
        '''
        Calculate the investment return of the account
        :return: float, the investment return
        '''
        if self.original_cash == 0:
            return 0
        else:
            return self.balance() / self.original_cash

    def balance(self):
        '''
        Valuate the account
        :return: float, the total balance of the account
        '''
        stock_value = self.value_stock_hold(self.stock_hold)
        balance = self.cash + stock_value
        return balance

    def present_value_of_a_stock(self, code, price):
        '''
        Value a stock with current price
        :param code: str, the stock index
        :param price: float, the current stock price
        :return: the present value of the stock
        '''
        volume = 0
        stock = self.initiate_a_stock(code, price, volume)
        i = self.find_stock(stock)
        if i >= 0:
            volume = self.select_stock_volume(self.stock_hold[i])
        stock = self.initiate_a_stock(code, price, volume)
        value = self.value_a_stock(stock)
        return value

    def origin_value_of_a_stock(self, code):
        '''
        Value a stock with purchase price
        :param code: str, the stock index
        :return: the original value of the stock
        '''
        volume = 0
        price = 0
        stock = self.initiate_a_stock(code, price, volume)
        i = self.find_stock(stock)
        if i >= 0:
            volume = self.select_stock_volume(self.stock_hold[i])
            price = self.select_stock_price(self.stock_hold[i])
        stock = self.initiate_a_stock(code, price, volume)
        value = self.value_a_stock(stock)
        return value

    def buy(self, code, price, volume):
        '''
        The procedure to buy a stock into the account
        :param code: str, the stock index
        :param price: float, the stock price
        :param volume: int, the stock volume
        :return: None
        '''
        stock = self.initiate_a_stock(code, price, volume)
        value = self.value_a_stock(stock)
        if value <= self.cash:
            self.cash -= value
            i = self.find_stock(stock)
            if i >= 0:
                self.stock_hold[i] = self.add_into_a_stock(stock, self.stock_hold[i])
            else:
                self.stock_hold.append(stock)

    def sell(self, code, price, volume):
        '''
        The procedure to sell a stock from the account
        :param code: str, the stock index
        :param price: float, the stock price
        :param volume: int, the stock volume
        :return: None
        '''
        stock = self.initiate_a_stock(code, price, volume)
        i = self.find_stock(stock)
        if i >= 0:
            if volume <= self.select_stock_volume(self.stock_hold[i]):
                self.cash += self.value_a_stock(stock)
                self.stock_hold[i] = self.retrive_from_a_stock(stock, self.stock_hold[i])
        self.clean_stock_hold()

    def reset_the_account(self):
        '''
        Reset the account
        :return: None
        '''
        self.__init__()

    def open_an_new_account(self, amount):
        '''
        :param amount: float, the cash investment
        :return:
        '''
        self.reset_the_account()
        self.deposit_cash(amount)

    def get_price_with_date(self, f, code, date=datetime.date.today(), type = 'List'):
        '''
        Get the relevant information of a specific day, defaults today
        :param f: a function take (code, date) as input and return a value
        :param code: str, stock index
        :param date: str, date
        :return: float, a price value
        '''
        now = time.strftime("%X", time.localtime())
        if date != datetime.date.today():
            date = Toolbox.date_encoding(date)
        if int(now[:1]) < 16:
            date = date - datetime.timedelta(1)
        if date.weekday() == 5:
            date = date - datetime.timedelta(1)
        elif date.weekday() == 6:
            date = date - datetime.timedelta(2)
        else: pass
        date = Toolbox.date_decoding(date)
        return f(code, date, type)

    def current_price_list(self):
        '''
        Generate a list of price, accordance with the stock hold account
        :return: a list with current price
        '''
        current_price_list = []
        for i in self.stock_hold:
            f = Messenger.get_stock_hist_data
            code = self.select_stock_code(i)
            close_price = self.get_price_with_date(f, code, type = 'close')
            current_price_list.append(close_price)
        return current_price_list

    def current_value_of_account(self):
        '''
        Get the current value of the stock hold account
        :return: float, the current value of the account
        '''
        list = self.current_price_list()
        stock_hold = []
        for i in range(len(list)):
            code = self.select_stock_code(self.stock_hold[i])
            volume = self.select_stock_volume(self.stock_hold[i])
            price = float(list[i])
            hold = self.initiate_a_stock(code, price, volume)
            stock_hold.append(hold)
        value = self.value_stock_hold(stock_hold) + self.cash
        return value

class KDJ:
    '''
    Perform the kdj computation
    '''

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

    def kdj_of_a_period(self, code, duration, start_date="", method = 9, smooth=30):
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

class MACD:

    '''
    Perform the calculation related to MACD
    '''

    def close_price_list(self, code, date, smooth):
        '''
        Get the price needed for calculation and return both days list and price list
        :param code: str, stock index
        :param date: str, the date
        :param smooth: int, the period taken into calculation
        :return: days list and price list
        '''
        days_list = Toolbox.number_of_days_before(code, smooth, date)
        close_price_list = []
        count = 1
        for i in days_list:
            close_price = Messenger.get_stock_hist_data(code, i, type='close')
            close_price_list.append(close_price)
            Toolbox.process_monitor(count / len(days_list) * 100)
            count += 1
        return (days_list[::-1], close_price_list[::-1])

    def caculate(self, code, date, smooth):
        '''
        Caculate the MACD and return the data of all the period
        :param code: str, the stock index
        :param date: str, the date
        :param smooth: int, the smooth period
        :return: a list of relevant data within the smooth period
        '''
        close_price_with_date = self.close_price_list(code, date, smooth)
        days_list = close_price_with_date[0]
        close_price_list = close_price_with_date[1]
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

    def macd(self, code, date='', smooth=120):
        '''
        Return the macd relatives for a specific day
        :param code: str, the stock code
        :param date: str, the date
        :param smooth: int, the smooth period, default 120
        :return: (macd, diff, dea)
        '''
        macd = self.caculate(code, date, smooth)[-1][1]
        # (macd, diff, dea)
        return (macd[-1], macd[-3], macd[-2])

    def macd_of_a_period(self, code, duration, date='', smooth=120):
        '''
        Calculate the macd for a period in a less consuming fashion
        :param code: str, the stock code
        :param duration: int, the days demanded
        :param date: str, the date
        :param smooth: int, the smooth period, default 120
        :return: a list with each unit in (date, (macd, diff, dea))
        '''
        calculated_list = self.caculate(code, date, smooth + duration)
        macd_list = [(i[0], (i[1][-1], i[1][-3], i[1][-2])) for i in calculated_list[-duration:]]
        return macd_list