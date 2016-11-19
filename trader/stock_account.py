import time, datetime
import messenger as ms
import assistant as at

class Stock:
    '''
    A presentation of a stock hold
    '''

    def __initiate_a_stock__(self, code, price, volume):
        '''
        Initiate a stock with a data structure (code, price, volume)
        :param code: str, stock index
        :param price: float, the price of the stock
        :param volume: int, the volume of the stock
        :return: a set, (code, price, volume)
        '''
        return (code, price, volume)

    def __select_stock_code__(self, stock):
        '''
        Selector, select the stock code
        :param stock: the Stock data structure
        :return: str, the stock hold
        '''
        return stock[0]

    def __select_stock_volume__(self, stock):
        '''
        Selector, select the stock volume
        :param stock: the Stock data structure
        :return: int, the stock volume
        '''
        return stock[2]

    def __select_stock_price__(self, stock):
        '''
        Selector, select the stock price
        :param stock: the Stock data structure
        :return: float, the stock price
        '''
        return stock[1]

    def __value_a_stock__(self, stock):
        '''
        Get the value of a stock
        :param stock:  the Stock data structure
        :return: float, the value of the stock
        '''
        return stock[1] * stock[2]

    def __add_into_a_stock__(self, stock1, stock2):
        '''
        Add stock1 into the stock2 and generate a new Stock(data structure)
        :param stock1: Stock data structure
        :param stock2: Stock data structure
        :return: a new Stock data structure
        '''
        code = self.__select_stock_code__(stock1)
        value = self.__value_a_stock__(stock1) + self.__value_a_stock__(stock2)
        volume = self.__select_stock_volume__(stock1) + self.__select_stock_volume__(stock2)
        if volume != 0:
            price = value / volume
        else: price = 0
        return self.__initiate_a_stock__(code, price, volume)

    def __retrive_from_a_stock__(self, stock1, stock2):
        '''
        Retrieve stock1 into the stock2 and generate a new Stock(data structure)
        :param stock1: Stock data structure
        :param stock2: Stock data structure
        :return: a new Stock data structure
        '''
        code = self.__select_stock_code__(stock1)
        value = self.__value_a_stock__(stock2) - self.__value_a_stock__(stock1)
        volume = self.__select_stock_volume__(stock2) - self.__select_stock_volume__(stock1)
        if volume != 0:
            price = value / volume
        else: price = 0
        return self.__initiate_a_stock__(code, price, volume)

class StockAccount(Stock):
    '''
    A stock account with functionality
    '''

    def __init__(self):
        '''
        Initiate the StockAccount, with float represent cash & original cash, set represent stock hold
        :return: None
        '''
        self.__original_cash__ = float()
        self.__cash__ = float()
        self.__stock_hold__ = []
        self.__log__ = []

    def __find_stock__(self, stock):
        '''
        Search a stock from the stock hold set to see if it is exist
        :param stock: a Stock data structure
        :return: the index if existed, otherwise -1
        '''
        if (len(self.__stock_hold__)) >= 1:
            for i in range(len(self.__stock_hold__)):
                if self.__select_stock_code__(stock) == self.__select_stock_code__(self.__stock_hold__[i]):
                    return i
            return -1
        else: return -1

    def __clean_stock_hold__(self):
        '''
        Clear the stock that is empty from the stock hold
        :return: None
        '''
        for i in self.__stock_hold__:
            if i[2] == 0:
                idx = self.__find_stock__(i)
                del self.__stock_hold__[idx]

    def __value_stock_hold__(self, stock_hold_list):
        '''
        Valuate the all the stock hold
        :param stock_hold_list: the stock hold list needed to be valued
        :return: float, the value
        '''
        balance = 0
        for i in stock_hold_list:
            balance += self.__value_a_stock__(i)
        return balance

    def deposit_cash(self, amount):
        '''
        The procedure to deposit cash into the account
        :param amount: float, the cash amount
        :return: None
        '''
        self.__cash__ += amount
        self.__original_cash__ += amount

    def withdraw_cash(self, amount):
        '''
        The procedure to withdraw cash from the account
        :param amount: float, the cash amount
        :return: None
        '''
        if amount > self.__cash__:
            amount = self.__cash__
        self.__cash__ -= amount
        self.__original_cash__ -= amount
        return amount

    def investment_return(self):
        '''
        Calculate the investment return of the account
        :return: float, the investment return
        '''
        if self.__original_cash__ == 0:
            return 0
        else:
            return self.balance() / self.__original_cash__

    def balance(self):
        '''
        Valuate the account
        :return: float, the total balance of the account
        '''
        stock_value = self.__value_stock_hold__(self.__stock_hold__)
        balance = self.__cash__ + stock_value
        return balance

    def present_value_of_a_stock(self, code, price):
        '''
        Value a stock with current price
        :param code: str, the stock index
        :param price: float, the current stock price
        :return: the present value of the stock
        '''
        volume = 0
        stock = self.__initiate_a_stock__(code, price, volume)
        i = self.__find_stock__(stock)
        if i >= 0:
            volume = self.__select_stock_volume__(self.__stock_hold__[i])
        stock = self.__initiate_a_stock__(code, price, volume)
        value = self.__value_a_stock__(stock)
        return value

    def origin_value_of_a_stock(self, code):
        '''
        Value a stock with purchase price
        :param code: str, the stock index
        :return: the original value of the stock
        '''
        volume = 0
        price = 0
        stock = self.__initiate_a_stock__(code, price, volume)
        i = self.__find_stock__(stock)
        if i >= 0:
            volume = self.__select_stock_volume__(self.__stock_hold__[i])
            price = self.__select_stock_price__(self.__stock_hold__[i])
        stock = self.__initiate_a_stock__(code, price, volume)
        value = self.__value_a_stock__(stock)
        return value

    def buy(self, code, price, volume):
        '''
        The procedure to buy a stock into the account
        :param code: str, the stock index
        :param price: float, the stock price
        :param volume: int, the stock volume
        :return: None
        '''
        stock = self.__initiate_a_stock__(code, price, volume)
        value = self.__value_a_stock__(stock)
        if value <= self.__cash__:
            self.__cash__ -= value
            i = self.__find_stock__(stock)
            if i >= 0:
                self.__stock_hold__[i] = self.__add_into_a_stock__(stock, self.__stock_hold__[i])
            else:
                self.__stock_hold__.append(stock)

    def sell(self, code, price, volume):
        '''
        The procedure to sell a stock from the account
        :param code: str, the stock index
        :param price: float, the stock price
        :param volume: int, the stock volume
        :return: None
        '''
        stock = self.__initiate_a_stock__(code, price, volume)
        i = self.__find_stock__(stock)
        if i >= 0:
            if volume <= self.__select_stock_volume__(self.__stock_hold__[i]):
                self.__cash__ += self.__value_a_stock__(stock)
                self.__stock_hold__[i] = self.__retrive_from_a_stock__(stock, self.__stock_hold__[i])
        self.__clean_stock_hold__()

    def __reset_the_account__(self):
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
        self.__reset_the_account__()
        self.deposit_cash(amount)

    def __get_price_with_date__(self, f, code, date=datetime.date.today(), type = 'List'):
        '''
        Get the relevant information of a specific day, defaults today
        :param f: a function take (code, date) as input and return a value
        :param code: str, stock index
        :param date: str, date
        :return: float, a price value
        '''
        now = time.strftime("%X", time.localtime())
        if date != datetime.date.today():
            date = at.date_encoding(date)
        if int(now[:1]) < 16:
            date = date - datetime.timedelta(1)
        if date.weekday() == 5:
            date = date - datetime.timedelta(1)
        elif date.weekday() == 6:
            date = date - datetime.timedelta(2)
        else: pass
        date = at.date_decoding(date)
        return f(code, date, type)

    def current_price_list(self):
        '''
        Generate a list of price, accordance with the stock hold account
        :return: a list with current price
        '''
        current_price_list = []
        for i in self.__stock_hold__:
            f = ms.get_stock_hist_data
            code = self.__select_stock_code__(i)
            close_price = self.__get_price_with_date__(f, code, type = 'close')
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
            code = self.__select_stock_code__(self.__stock_hold__[i])
            volume = self.__select_stock_volume__(self.__stock_hold__[i])
            price = float(list[i])
            hold = self.__initiate_a_stock__(code, price, volume)
            stock_hold.append(hold)
        value = self.__value_stock_hold__(stock_hold) + self.__cash__
        return value

    def show_stock(self):
        '''
        Show the account stock details
        :return: the account stock details
        '''
        return self.__stock_hold__

    def show_cash(self):
        '''
        Show the cash available
        :return: the cash available
        '''
        return self.__cash__