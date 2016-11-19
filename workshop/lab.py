import analyst as al
import trader as tr
import messenger as ms
import assistant as at
import time, datetime

class StockHold:

    def initiate(self, code, volume, price):
        stock = (str(code), int(volume), float(price))
        return stock

    def __select__(self, stock, type='code'):
        if type == 'code':
            return stock[0]
        if type == 'volume':
            return stock[1]
        if type == 'price':
            return stock[2]
        return None

    def __value__(self, stock):
        value = self.__select__(stock, 'volume') * self.__select__(stock, 'price')
        return value


    def add(self, new, original):
        if self.__select__(new, 'code') == self.__select__(original, 'code'):
            code = self.__select__(new, 'code')
            volume = self.__select__(new, 'volume') + self.__select__(original, 'volume')
            if volume != 0:
                cost_price = (self.__value__(new) + self.__value__(original)) / volume
            else: return original
            stock = self.initiate(code, volume, cost_price)
            return stock
        else: return original

    def retrieve(self, out, original):
        if self.__select__(out, 'code') == self.__select__(original, 'code'):
            code = self.__select__(out, 'code')
            volume = self.__select__(original, 'volume') - self.__select__(out, 'volume')
            if volume != 0:
                cost_price = (self.__value__(original) - self.__value__(out)) / volume
            else: return None
            stock = self.initiate(code, volume, cost_price)
            return stock
        else:
            return None

class StockAccount:

    def __init__(self):
        self.__cash__ = 0
        self.__stock_hold__ = []
        self.__stock_log__ = []
        self.__stock_handle__ = StockHold()

    def log(self, stock_hold, date=''):
        if date == '':
            date = at.date_decoding(datetime.date.today())
        stock_hold = stock_hold
        current_price_list = []
        for i in stock_hold:
            current_price = ms.get_stock_hist_data(i[0], date, 'close')
            current_price_list.append(current_price)
        line = (date, stock_hold, current_price_list)
        self.__stock_log__ += line
        return line