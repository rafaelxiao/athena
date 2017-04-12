import analyst as al
import trader as tr
import messenger as ms
import assistant as at
import time, datetime
import copy

class Portfolio():
    '''
    Basic functions of a porfolio
    '''

    def __init__(self):
        '''
        Initiate, create a portfolio list and a unit_ratio
        :return:
        '''
        self.unit_ratio = float(1)
        self.portfolio = []

    def __repr__(self):
        '''
        Present the value of portfolio
        :return: the value of portfolio
        '''
        text_string = []
        if len(self.portfolio) > 0:
            for i in self.portfolio:
                text_string.append('name: %s, amount: %.2f, ratio: %.2f'%(i['name'], i['amount'], i['ratio']))
        text_string = '|'.join(text_string)
        text_string = '\'' + text_string + '\''
        return text_string

    def __find_index__(self, name):
        '''
        Find the index by name in the portfolio list
        :param name: str
        :return: int, the index
        '''
        for i in range(len(self.portfolio)):
            if self.portfolio[i]['name'] == name:
                return i
        return -1

    def __is_valid_input__(self, name, amount=0.0, ratio=0.0):
        '''
        Test if an input is validate
        :param name: str
        :param amount: float or int
        :param ratio: float or int
        :return: boolean
        '''
        amount = self.__covert_to_float__(amount)
        ratio = self.__covert_to_float__(ratio)
        if isinstance(name, str) and isinstance(amount, float) and isinstance(ratio, float):
            if amount >= 0 and ratio >= 0:
                return True
        else:
            return False

    def __covert_to_float__(self, number):
        '''
        Covert to float if success
        :param number: any type
        :return: float or nothing
        '''
        try:
            number = float(number)
        except:
            pass
        return number

    def add(self, name, amount, ratio):
        '''
        Add a entry to the portfolio list
        :param name: str
        :param amount: int or float
        :param ratio: int or float
        :return: None
        '''
        amount = self.__covert_to_float__(amount)
        ratio = self.__covert_to_float__(ratio)
        if len(self.portfolio) == 0:
            ratio = 1.0
        if self.__is_valid_input__(name, amount, ratio):
            line = {'name': name, 'amount': amount, 'ratio': ratio}
            idx = self.__find_index__(name)
            if idx == -1:
                self.portfolio.append(line)
            else:
                self.portfolio[idx] = line

    def remove(self, name):
        '''
        Remove a entry from the portfolio list, will not remove the base line
        :param name: str
        :return: None
        '''
        if self.__is_valid_input__(name):
            idx = self.__find_index__(name)
            if idx != -1 and idx != 0:
                self.portfolio.remove(self.portfolio[idx])

    def change_base(self, name):
        '''
        Change the base line of the portfolio
        :param name: str
        :return: None
        '''
        if self.__is_valid_input__(name):
            idx = self.__find_index__(name)
            if idx != -1:
                converter = self.portfolio[idx]['ratio']
                for i in range(len(self.portfolio)):
                    self.portfolio[i]['ratio'] = self.portfolio[i]['ratio'] / converter
                new_base = self.portfolio[idx]
                self.portfolio.remove(self.portfolio[idx])
                self.portfolio = [new_base] + self.portfolio

    def value_one(self, name, amount=0.0, ratio=0.0, new=False):
        '''
        Return the value of a line
        :param name: str
        :return: float
        '''
        amount = self.__covert_to_float__(amount)
        ratio = self.__covert_to_float__(ratio)
        if self.__is_valid_input__(name):
            idx = self.__find_index__(name)
            if idx != -1 and new == False:
                amount = self.portfolio[idx]['amount']
                ratio = self.portfolio[idx]['ratio']
            value = self.unit_ratio * amount * ratio
            return value

    def value_portfolio(self):
        '''
        Value the entire portfolio
        :return: float
        '''
        total_value = 0.0
        for i in self.portfolio:
            total_value += self.value_one(i['name'])
        return total_value

    def update_name(self, new_name, old_name):
        '''
        Update the name of one line
        :param new_name: str
        :param old_name: str
        :return: None
        '''
        if self.__is_valid_input__(new_name) and self.__is_valid_input__(old_name):
            idx = self.__find_index__(old_name)
            if idx != -1:
                self.portfolio[idx]['name'] = new_name

    def update_amount(self, name, amount, aggregate=False):
        '''
        Update the amount of one line
        :param name: str
        :param amount: int or float
        :param aggregate: boolean
        :return: None
        '''
        if self.__is_valid_input__(name, amount=abs(amount)):
            idx = self.__find_index__(name)
            if idx != -1:
                ratio = self.portfolio[idx]['ratio']
                if aggregate != False:
                    amount = self.portfolio[idx]['amount'] + amount
                self.add(name, amount, ratio)

    def update_ratio(self, name, ratio):
        '''
        Update the ratio of one line
        :param name: str
        :param ratio: int or float
        :return: None
        '''
        if self.__is_valid_input__(name, ratio=ratio):
            idx = self.__find_index__(name)
            if idx != -1:
                amount = self.portfolio[idx]['amount']
                self.add(name, amount, ratio)

    def update_unit_ratio(self, number):
        '''
        Update the unit ratio
        :param number: int or float
        :return: None
        '''
        try:
            number = float(number)
            self.unit_ratio = number
        except:
            pass

    def show_amount(self, name):
        '''
        Return the amount of a specific category
        :param name: str
        :return: float, the amount
        '''
        if self.__is_valid_input__(name):
            idx = self.__find_index__(name)
            if idx != -1:
                return self.portfolio[idx]['amount']
        else:
            return 0.0


class Account():

    def __init__(self):
        self.account = []
        time = 'Initiate'
        portfolio = Portfolio()
        portfolio.add('cash', 0, 1)
        log = 'Initiate the account'
        self.account.append({'time': time, 'portfolio': portfolio, 'log': log})

    def __repr__(self):
        output = ''
        for i in self.account:
            text = """
            Time: %s
            Portfolio: %s
            Log: %s
            """%(i['time'], i['portfolio'], i['log'])
            output += text
        return output

    def __pass__(self):
        new_line = copy.deepcopy(self.account[-1]['portfolio'])
        return new_line

    def __add_entry__(self, time, portfolio, log):
        last_line = self.account[-1]
        new_line = {'time': time, 'portfolio': portfolio, 'log': log}
        if last_line != new_line:
            self.account.append(new_line)

    def __log__(self, time, name, amount, action):
        text = '%s, %s %.2f %s'%(time, action, amount, name)
        return text

    def __time_compare__(self, time1, time2, f):
        if time2 == 'Initiate':
            return True
        return f(time1, time2)

    def __date_compare__(self, time1, time2):
        time1 = at.date_encoding(time1)
        time2 = at.date_encoding(time2)
        if time1 > time2:
            return True
        else:
            return False

    def __time_validation__(self, time):
        last_time = self.account[-1]['time']
        return self.__time_compare__(time, last_time, self.__date_compare__)


    def deposit(self, amount, time):
        if amount > 0:
            if self.__time_validation__(time):
                portfolio = self.__pass__()
                log = self.__log__(time, 'cash', amount, 'deposit')
                if len(self.account) != 1:
                    portfolio.update_amount('cash', amount, True)
                else:
                    portfolio.update_amount('cash', amount, False)
                self.__add_entry__(time, portfolio, log)

    def __has_sufficient_fund__(self, amount):
        if amount <= self.account[-1]['portfolio'].show_amount('cash'):
            return True
        else:
            return False

    def withdraw(self, amount, time):
        if amount > 0 and self.__has_sufficient_fund__(amount):
            if self.__time_validation__(time):
                portfolio = self.__pass__()
                log = self.__log__(time, 'cash', amount, 'withdraw')
                portfolio.update_amount('cash', -amount, True)
                self.__add_entry__(time, portfolio, log)



acc = Account()
acc.deposit(100, '2016-05-30')
acc.withdraw(101, '2017-03-20')
print(acc)