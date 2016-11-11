import math, datetime
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

    def get_price_with_date(self, f, code, date=datetime.date.today()):
        '''
        Get the relevant information of a specific day, defaults today
        :param f: a function take (code, date) as input and return a value
        :param code: str, stock index
        :param date: str, date
        :return: float, a price value
        '''
        if date != datetime.date.today():
            date = Toolbox.date_encoding(date)
        if date.weekday() == 5:
            date = date - datetime.timedelta(1)
        elif date.weekday() == 6:
            date = date - datetime.timedelta(2)
        else: pass
        date = Toolbox.date_decoding(date)
        return f(code, date)

    def current_price_list(self):
        '''
        Generate a list of price, accordance with the stock hold account
        :return: a list with current price
        '''
        current_price_list = []
        for i in self.stock_hold:
            f = Messenger.get_stock_open_price
            code = self.select_stock_code(i)
            close_price = self.get_price_with_date(f, code)
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

