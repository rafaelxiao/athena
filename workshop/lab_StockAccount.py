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
        self.__cash__ = float(0)
        self.__investment__ = float(0)
        self.__stock_hold__ = []
        self.__stock_log__ = []
        self.__stock_handle__ = StockHold()

    def __log__(self, text, date='', stock_hold=''):
        print('x', self.__stock_log__)
        if date == '':
            date = at.date_decoding(datetime.date.today())
        if stock_hold == '':
            # Copy the value, not referencing it
            stock_hold = list(self.__stock_hold__)
        cash = self.__cash__
        repeat_counter = 0
        for j in self.__stock_log__:
            if date == j[0]:
                repeat_counter += 1
        line = (date, repeat_counter, text, cash, stock_hold)
        self.__stock_log__.append(line)
        self.__sort_log__()
        return line

    def __sort_log__(self):
        def greater(value_1, value_2):
            if at.date_encoding(value_1[0]) > at.date_encoding(value_2[0]):
                return True
            elif at.date_encoding(value_1[0]) == at.date_encoding(value_2[0]) and value_1[1] > value_2[1]:
                return True
            else: return False
        i = len(self.__stock_log__)
        while i > 0:
            for j in range(i - 1):
                if greater(self.__stock_log__[j], self.__stock_log__[j + 1]):
                    h = self.__stock_log__[j]
                    self.__stock_log__[j] = self.__stock_log__[j + 1]
                    self.__stock_log__[j + 1] = h
            i -= 1

    def __stock_existed__(self, stock):
        code = self.__stock_handle__.__select__(stock, type='code')
        for i in range(len(self.__stock_hold__)):
            if code == self.__stock_handle__.__select__(self.__stock_hold__[i], type='code'):
                return i
        return -1

    def deposit_cash(self, cash_amount, date=''):
        cash_amount = float(cash_amount)
        self.__cash__ += cash_amount
        self.__investment__ += cash_amount
        self.__log__('deposit %i cash' % round(cash_amount, 2), date)
        return self.__cash__

    def withdraw_cash(self, cash_amount, date=''):
        if cash_amount < self.__cash__ and cash_amount < self.__investment__:
            cash_amount = float(cash_amount)
            self.__cash__ -= cash_amount
            self.__investment__ -= cash_amount
            self.__log__("withdraw %i cash" % round(cash_amount, 2), date)
            return self.__cash__

    def show_account(self):
        info = self.__stock_log__[-1]
        print('Cash: %i, Stock: %s'%(info[-2], info[-1]) )
        return (info[-2], info[-1])

    def buy(self, code, volume, price=float(0), date='', type='close'):
        if price == 0:
            try:
                price = float(ms.get_stock_hist_data(code, date, type))
            except:
                print('Stock not existed')
                return None
        stock = self.__stock_handle__.initiate(code, volume, price)
        cost = self.__stock_handle__.__value__(stock)
        if cost < self.__cash__:
            self.__cash__ -= cost
            i = self.__stock_existed__(stock)
            if i > -1:
                stock_added = self.__stock_handle__.add(stock, self.__stock_hold__[i])
                self.__stock_hold__[i] = stock_added
            else:
                self.__stock_hold__.append(stock)
            self.__log__('buy %i shares of %s at price %.2f'%(volume, code, price), date)
            return stock
        else:
            print('Insufficient fund')
            return None

    def sell(self, code, volume, price=float(0), date='', type='close'):
        if price == 0:
            try:
                price = float(ms.get_stock_hist_data(code, date, type))
            except:
                print('Stock not existed')
                return None
        stock = self.__stock_handle__.initiate(code, volume, price)
        i = self.__stock_existed__(stock)
        if i > -1:
            value = self.__stock_handle__.__value__(stock)
            self.__cash__ += value
            stock_retrieved = self.__stock_handle__.retrieve(stock, self.__stock_hold__[i])
            self.__stock_hold__[i] = stock_retrieved
            self.__log__('sell %i shares of %s at price %.2f'%(volume, code, price), date)
            return stock
        else:
            price('The stock is not in the account')
            return None


i = StockAccount()
i.deposit_cash(100)
i.deposit_cash(153, '2015-11-13')
i.deposit_cash(125300)
i.withdraw_cash(100, '2016-11-21')
i.buy('600313', 300)
i.buy('600313', 100, 6.8)
i.buy('221361', 100, 2.7)
i.sell('600313', 100)
i.sell('600313', 200, 6.5)
i.sell('786231', 200)
for z in i.__stock_log__:
    print(z)
i.show_account()