import analyst as al
import trader as tr
import messenger as ms
import assistant as at
import time, datetime

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

    def __value_a_line__(self, name):
        '''
        Return the value of a line
        :param name: str
        :return: float
        '''
        if self.__is_valid_input__(name):
            idx = self.__find_index__(name)
            if idx != -1:
                value = self.unit_ratio * self.portfolio[idx]['ratio'] * self.portfolio[idx]['amount']
                return value

    def value_portfolio(self):
        '''
        Value the entire portfolio
        :return: float
        '''
        total_value = 0.0
        for i in self.portfolio:
            total_value += self.__value_a_line__(i['name'])
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


