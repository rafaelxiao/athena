import analyst as al
import trader as tr
import messenger as ms
import assistant as at
import time, datetime
import copy

class Unit():

    def __is_correct_type__(self, name, amount, ratio):
        name_type = isinstance(name, str)
        amount_type = isinstance(amount, float)
        ratio_type = isinstance(ratio, float)
        if name_type and amount_type and ratio_type:
            return True
        else:
            return False

    def __is_valid_inputs__(self, name, amount, ratio):
        valid = False
        if self.__is_correct_type__(name, amount, ratio):
            valid = True
        return valid

    def is_valid_unit(self, unit):
        try:
            name = unit['name']
            amount = unit['amount']
            ratio = unit['ratio']
            if self.__is_valid_inputs__(name, amount, ratio):
                return True
            else:
                return False
        except:
            return False

    def __convert_to_float__(self, number):
        try:
            number = float(number)
            return number
        except:
            return number

    def make_a_unit(self, name, amount, ratio):
        amount = self.__convert_to_float__(amount)
        ratio = self.__convert_to_float__(ratio)
        if self.__is_valid_inputs__(name, amount, ratio):
            content = {'name': name, 'amount': amount, 'ratio': ratio}
        else:
            content = {}
        return content

    def show_amount(self, unit):
        if self.is_valid_unit(unit):
            return unit['amount']
        else:
            return 0

    def show_ratio(self, unit):
        if self.is_valid_unit(unit):
            return unit['ratio']
        else:
            return 0

    def update(self, content, unit, type):
        if self.is_valid_unit(unit):
            origin = dict(unit)
            unit[type] = content
            if not self.is_valid_unit(unit):
                unit = origin
        return unit

class Portfolio():

    def __init__(self, text = None, base = 'cash'):
        self.unit_spliter = '|'
        self.agent_unit = Unit()
        self.portfolio = []
        base_unit = self.agent_unit.make_a_unit(base, 0, 1)
        if self.agent_unit.is_valid_unit(base_unit):
            self.portfolio.append(base_unit)
        if text != None:
            loaded = self.__load__(text)
            if loaded != None:
                self.portfolio = loaded

    def save(self):
        content = self.unit_spliter.join([str(i) for i in self.portfolio])
        return content

    def __load__(self, text):
        try:
            content = text.split(self.unit_spliter)
            for i in range(len(content)):
                content[i] = eval(content[i])
        except:
            content = None
        return content

    def __find_index__(self, name):
        idx = -1
        for i in range(len(self.portfolio)):
            if self.portfolio[i]['name'] == name:
                idx = i
                break
        return idx

    def __check__(self):
        blank = []
        for i in range(1, len(self.portfolio)):
            if self.portfolio[i]['amount'] == 0.0:
                blank.append(self.portfolio[i])
        for j in blank:
            self.portfolio.remove(j)

    def __combine__(self, unit, ratio_update=False):
        if self.agent_unit.is_valid_unit(unit):
            idx = self.__find_index__(unit['name'])
            if idx == -1:
                self.portfolio.append(unit)
            else:
                unit['amount'] = unit['amount'] + self.agent_unit.show_amount(self.portfolio[idx])
                self.portfolio[idx] = self.agent_unit.update(unit['amount'], self.portfolio[idx], 'amount')
                if ratio_update == True:
                    self.portfolio[idx] = self.agent_unit.update(unit['ratio'], self.portfolio[idx], 'ratio')

    def __update_ratio__(self, name, ratio):
        entry = self.agent_unit.make_a_unit(name, 0, ratio)
        if self.agent_unit.is_valid_unit(entry):
            idx = self.__find_index__(name)
            if idx != -1:
                self.__combine__(entry, True)

    def __get_value__(self, name, type):
        idx = self.__find_index__(name)
        value = None
        if idx != -1:
            if type == 'amount':
                value = self.agent_unit.show_amount(self.portfolio[idx])
            elif type == 'ratio':
                value = self.agent_unit.show_ratio(self.portfolio[idx])
            else: pass
        return value

    def __value__(self, unit):
        value = 0.0
        if self.agent_unit.is_valid_unit(unit):
            amount = self.agent_unit.show_amount(unit)
            ratio = self.agent_unit.show_ratio(unit)
            value = amount * ratio
        return value

    def __value_a_unit__(self, name):
        value = 0.0
        idx = self.__find_index__(name)
        if idx != -1:
            value = self.__value__(self.portfolio[idx])
        return value

    def __sufficient_fund__(self, unit):
        result = False
        fund = self.__get_value__(self.portfolio[0]['name'], 'amount')
        cost = self.__value__(unit)
        if fund >= cost:
            result = True
        return result

    def buy(self, name, amount, ratio):
        entry = self.agent_unit.make_a_unit(name, amount, ratio)
        if self.agent_unit.is_valid_unit(entry):
            if self.__sufficient_fund__(entry):
                cost = self.__value__(entry)
                base_renew = self.agent_unit.make_a_unit(self.portfolio[0]['name'], -cost, 1)
                self.__combine__(base_renew)
                self.__combine__(entry)
                self.__check__()

    def deposit(self, amount):
        entry = self.agent_unit.make_a_unit(self.portfolio[0]['name'], amount, self.portfolio[0]['ratio'])
        if self.agent_unit.is_valid_unit(entry):
            self.__combine__(entry)

    def withdraw(self, amount):
        entry = self.agent_unit.make_a_unit(self.portfolio[0]['name'], amount, self.portfolio[0]['ratio'])
        if self.agent_unit.is_valid_unit(entry):
            if self.__sufficient_fund__(entry):
                cost = self.__value__(entry)
                self.agent_unit.update(-cost, entry, 'amount')
                self.__combine__(entry)

    def sell(self, name, amount, ratio):
        entry = self.agent_unit.make_a_unit(name, -amount, ratio)
        if self.agent_unit.is_valid_unit(entry):
            amount_available = self.__get_value__(entry['name'], 'amount')
            if amount_available != None:
                if amount_available >= -entry['amount']:
                    gain = -self.__value__(entry)
                    base_renew = self.agent_unit.make_a_unit(self.portfolio[0]['name'], gain, 1)
                    self.__combine__(base_renew)
                    self.__combine__(entry)
                    self.__check__()

    def value_porfolio(self):
        total = 0.0
        for i in self.portfolio:
            total += self.__value__(i)
        return total