import analyst as al
import trader as tr
import messenger as ms
import assistant as at
import time, datetime
import copy
import os
import math
import matplotlib.pyplot as plt
import matplotlib.finance as mpf
import matplotlib.gridspec as gridspec
from matplotlib.dates import date2num, DateFormatter, WeekdayLocator, DayLocator, MONDAY

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
            unit = self.make_a_unit(unit['name'], unit['amount'], unit['ratio'])
            if not self.is_valid_unit(unit):
                unit = origin
        return unit

class Portfolio():

    def __init__(self, text = None, base = 'cash'):
        self.unit_splitter = '|u|'
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
        content = self.unit_splitter.join([str(i) for i in self.portfolio])
        return content

    def __load__(self, text):
        try:
            content = text.split(self.unit_splitter)
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
                amount_existed = self.agent_unit.show_amount(self.portfolio[idx])
                ratio_existed = self.agent_unit.show_ratio(self.portfolio[idx])
                total_amount = unit['amount'] + amount_existed
                if ratio_update == True:
                    ratio = unit['ratio']
                elif total_amount == 0:
                    ratio = 0.0
                    if idx == 0:
                        ratio = ratio_existed
                else:
                    ratio = (unit['ratio'] * unit['amount'] + amount_existed * ratio_existed) / total_amount
                self.portfolio[idx] = self.agent_unit.update(total_amount, self.portfolio[idx], 'amount')
                self.portfolio[idx] = self.agent_unit.update(ratio, self.portfolio[idx], 'ratio')

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

    def show(self, name=None, type='name'):
        content = None
        if name == None:
            name = self.portfolio[0]['name']
        idx = self.__find_index__(name)
        if idx != -1:
            content = self.portfolio[idx][type]
        return content

    def update_ratio(self, name, ratio):
        idx = self.__find_index__(name)
        if idx != -1:
            updated = dict(self.portfolio[idx])
            updated = self.agent_unit.update(ratio, updated, 'ratio')
            if updated != self.portfolio[idx]:
                self.portfolio[idx] = updated

class Account():

    def __init__(self, text=None, time='', base='cash'):
        self.functions = self.__import_functions__()
        self.agent_portfolio = Portfolio
        self.unit_splitter = '|a|'
        if self.__is_valid_time__(time):
            self.account = []
            portfolio = self.agent_portfolio(base).save()
            log = self.__log__(time, base)
            self.__make_a_entry__(time, portfolio, log)
        if text != None:
            loaded = self.__load__(text)
            if loaded != None:
                self.account = loaded

    def save(self):
        content = self.unit_splitter.join([str(i) for i in self.account])
        return content

    def __load__(self, text):
        try:
            content = text.split(self.unit_splitter)
            for i in range(len(content)):
                content[i] = eval(content[i])
        except:
            content = None
        return content

    def __make_a_entry__(self, time, portfolio_text, log):
        content = {}
        content['time'] = time
        content['portfolio'] = portfolio_text
        idx = self.__find_index__(time)
        if idx != -1:
            content['log'] = self.account[idx]['log'] + [log]
            self.account[idx] = content
        else:
            content['log'] = [log]
            self.account.append(content)

    def __log__(self, time, name, action='', amount=0.0, ratio=0.0):
        if len(self.account) == 0:
            log = 'initiate account'
        else:
            log = '%s, %s %.2f %s at %.2f'%(time, action, amount, name, ratio)
        return log

    def __import_functions__(self):
        function_list = {}
        function_list['date_encoding'] = at.date_encoding
        return function_list

    def __is_valid_date___(self, date):
        result = False
        try:
            self.functions['date_encoding'](date)
            result = True
        except: pass
        return result

    def __is_valid_time__(self, time):
        result = False
        checkers = [self.__is_valid_date___]
        for i in checkers:
            if i(time) == True:
                result = True
        return result

    def __is_date_after__(self, date1, date2, allow_equal=False):
        result = False
        f = self.functions['date_encoding']
        if self.__is_valid_date___(date1) and self.__is_valid_date___(date2):
            tester = f(date1) > f(date2)
            if allow_equal:
                tester = f(date1) >= f(date2)
            if tester:
                result = True
        return result

    def __is_after__(self, time1, time2, allow_equal=False):
        result = False
        checkers = [self.__is_date_after__]
        for i in checkers:
            if i(time1, time2, allow_equal) == True:
                result = True
        return result

    def __last_time__(self):
        last_time = self.account[-1]['time']
        return last_time

    def __last_portfolio_text__(self):
        last_portfolio_text = self.account[-1]['portfolio']
        return last_portfolio_text

    def deposit(self, time, amount):
        if self.__is_valid_time__(time):
            if self.__is_after__(time, self.__last_time__(), True):
                original_portfolio_text = self.__last_portfolio_text__()
                portfolio = self.agent_portfolio(original_portfolio_text)
                portfolio.deposit(amount)
                new_portfolio_text = portfolio.save()
                if original_portfolio_text != new_portfolio_text:
                    name = portfolio.show()
                    # amount = portfolio.show(name, 'amount')
                    log = self.__log__(time, name, 'deposit', amount, 1.0)
                    self.__make_a_entry__(time, new_portfolio_text, log)

    def withdraw(self, time, amount):
        if self.__is_valid_time__(time):
            if self.__is_after__(time, self.__last_time__(), True):
                original_portfolio_text = self.__last_portfolio_text__()
                portfolio = self.agent_portfolio(original_portfolio_text)
                portfolio.withdraw(amount)
                new_portfolio_text = portfolio.save()
                if original_portfolio_text != new_portfolio_text:
                    name = portfolio.show()
                    # amount = portfolio.show(name, 'amount')
                    log = self.__log__(time, name, 'withdraw', amount, 1.0)
                    self.__make_a_entry__(time, new_portfolio_text, log)

    def buy(self, time, name, amount, ratio):
        if self.__is_valid_time__(time):
            if self.__is_after__(time, self.__last_time__(), True):
                original_portfolio_text = self.__last_portfolio_text__()
                portfolio = self.agent_portfolio(original_portfolio_text)
                portfolio.buy(name, amount, ratio)
                new_portfolio_text = portfolio.save()
                if original_portfolio_text != new_portfolio_text:
                    log = self.__log__(time, name, 'buy', amount, ratio)
                    self.__make_a_entry__(time, new_portfolio_text, log)

    def sell(self, time, name, amount, ratio):
        if self.__is_valid_time__(time):
            if self.__is_after__(time, self.__last_time__(), True):
                original_portfolio_text = self.__last_portfolio_text__()
                portfolio = self.agent_portfolio(original_portfolio_text)
                portfolio.sell(name, amount, ratio)
                new_portfolio_text = portfolio.save()
                if original_portfolio_text != new_portfolio_text:
                    log = self.__log__(time, name, 'sell', amount, ratio)
                    self.__make_a_entry__(time, new_portfolio_text, log)

    def account_dict(self):
        content = []
        for i in self.account:
            portfolio_holder = self.agent_portfolio(i['portfolio'])
            time = i['time']
            portfolio = portfolio_holder.portfolio
            log = i['log']
            value = portfolio_holder.value_porfolio()
            line = {'time': time, 'portfolio': portfolio, 'value': value, 'log': log}
            content.append(line)
        return content

    def line_detail(self, time):
        content = {}
        if self.__is_valid_time__(time):
            dict = self.account_dict()
            idx = self.__find_index__(time, dict)
            if idx != -1:
                content = dict[idx]
        return content

    def print_line(self, time):
        content = self.line_detail(time)
        if content != {}:
            print('Time: %s'%content['time'])
            print('Portfolio:')
            for j in content['portfolio']:
                print('\tName: %s, Amount: %.2f, Ratio: %.2f'%(j['name'], j['amount'], j['ratio']))
            print('Value: %.2f'%content['value'])
            print('Log:')
            for k in content['log']:
                print('\t%s'%k)
            print('\n')

    def print_account(self):
        print('----------------')
        content = self.account_dict()
        for i in content:
            time = i['time']
            self.print_line(time)

    def __find_index__(self, time, dict=None):
        idx = -1
        if self.__is_valid_time__(time):
            if dict == None:
                dict = self.account
            for i in range(len(dict)):
                if time == dict[i]['time']:
                    idx = i
                    break
        return idx

    def update(self, time, update_dict=None, fill_blank=False, fill_behind=True):

        if update_dict == None:
            update_dict = {}

        def update(dict, portfolio_text):
            portfolio = self.agent_portfolio(portfolio_text)
            if dict != {}:
                for (i, j) in dict.items():
                    portfolio.update_ratio(i, j)
                portfolio_text_updated = portfolio.save()
                if portfolio_text_updated != portfolio_text:
                    portfolio_text = portfolio_text_updated
            return portfolio_text

        if self.__is_valid_time__(time):
            idx = self.__find_index__(time)
            if idx != -1:
                pointer = dict(self.account[idx])
                if update_dict != {}:
                    pointer['portfolio'] = update(update_dict, pointer['portfolio'])
                    pointer['time'] = time
                    if pointer['portfolio'] != self.account[idx]['portfolio']:
                        self.account[idx] = pointer
                        if fill_behind == True:
                            for j in self.account[idx+1:]:
                                j['portfolio'] = update(update_dict, j['portfolio'])
            else:
                idx = -1
                for i in self.account:
                    if self.__is_after__(time, i['time']):
                        idx += 1
                    else:
                        break
                if idx != -1:
                    pointer = dict(self.account[idx])
                    if update_dict != {}:
                        pointer['portfolio'] = update(update_dict, pointer['portfolio'])
                        pointer['time'] = time
                        if pointer['portfolio'] != self.account[idx]['portfolio']:
                            self.account.insert(idx+1, pointer)
                            if fill_behind == True:
                                for j in self.account[idx+2:]:
                                    j['portfolio'] = update(update_dict, j['portfolio'])
                    else:
                        if fill_blank == True:
                            pointer['portfolio'] = update(update_dict, pointer['portfolio'])
                            pointer['time'] = time
                            self.account.insert(idx+1, pointer)

class StockAccount():

    def __init__(self, text=None, time=''):
        self.functions = self.__import_functions__()
        self.performance = StockAccountPerformance()
        self.account = []
        loaded = self.__load__(text)
        if loaded != None:
            self.captain = Account(loaded['captain'])
            self.first_mate = Account(loaded['first_mate'])
            self.total_investment = loaded['total_investment']
        else:
            time = self.__opening_day__('399300', time)
            self.captain = Account(time=time, base='cash')
            self.first_mate = Account(time=time, base='cash')
            self.total_investment = 0.0
        self.__auto_combine__()
        self.reference_price = 'close'
        self.fee = {'tax': 0.001, 'transfer': 1, 'service': 0.0005}
        self.stock_list = self.functions['complete_stock_list']()

    def __import_functions__(self):
        function_list = {}
        function_list['complete_stock_list'] = ms.complete_stock_list
        function_list['opening_days'] = at.opening_days
        function_list['get_hist_data'] = ms.get_stock_hist_data
        function_list['date_encoding'] = at.date_encoding
        function_list['progress_bar'] = at.process_monitor
        function_list['next_opening_day'] = at.next_opening_day
        return function_list

    def __fee_calculator__(self, price, shares, type):
        fee = 0.0
        transfer = shares / 1000 * self.fee['transfer']
        if transfer <= 1:
            transfer = 1
        tax = price * shares * self.fee['tax']
        service = price * shares * self.fee['service']
        if type == 'buy':
            fee = service + transfer
        if type == 'sell':
            fee = service + transfer + tax
        return fee

    def save(self):
        content = {}
        content['captain'] = self.captain.save()
        content['first_mate'] = self.first_mate.save()
        content['total_investment'] = self.total_investment
        return str(content)

    def __load__(self, text):
        try:
            content = eval(text)
        except:
            content = None
        return content

    def __operation_complete__(self, shifted_account, original_account):
        result = False
        if shifted_account.save() != original_account.save():
            result = True
        return result

    def __opening_day__(self, code, date):
        opening_day = self.functions['opening_days'](code=code, days=1, start_date=date, multi_threads = 1)[0]
        return opening_day

    def __get_reference_price__(self, code, date, ref_price):
        price = ref_price
        try:
            price = self.functions['get_hist_data'](code, date, self.reference_price)
        except:
            pass
        return price

    def __reflect_in_first_mate__(self):
        dict = self.first_mate.account_dict()
        self.first_mate = copy.deepcopy(self.captain)
        for i in dict:
            for j in i['portfolio']:
                self.first_mate.update(i['time'], {j['name']: j['ratio']})

    def __combine__(self, captain, first_mate):
        dict = []
        main = captain.account_dict()
        support = first_mate.account_dict()
        for i in range(len(main)):
            line = {}
            line['date'] = main[i]['time']
            line['cash'] = main[i]['portfolio'][0]['amount']
            line['cost'] = main[i]['value']
            line['value'] = support[i]['value']
            portfolio_list = []
            for k in range(1, len(main[i]['portfolio'])):
                portfolio = {}
                portfolio['code'] = main[i]['portfolio'][k]['name']
                portfolio['shares'] = main[i]['portfolio'][k]['amount']
                portfolio['price'] = main[i]['portfolio'][k]['ratio']
                portfolio['market'] = support[i]['portfolio'][k]['ratio']
                portfolio_list.append(portfolio)
            line['portfolio'] = portfolio_list
            log_list = []
            for j in main[i]['log']:
                log_list.append(j)
            line['log'] = log_list
            dict.append(line)
        return dict

    def __output_dict__(self, dict=None):
        if dict == None:
            dict = self.account
        text = ''
        for i in dict:
            text += ('\n')
            text += ('Date: %s\n'%i['date'])
            text += ('Cash: %.2f\n'%i['cash'])
            text += ('Portfolio:\n')
            for k in i['portfolio']:
                text += ('\tCode: %s, Amount: %.2f, Bought Price: %.2f, Market Price: %.2f\n'%(k['code'], k['shares'], k['price'], k['market']))
            text += ('Cost: %.2f, Value: %.2f\n'%(i['cost'], i['value']))
            text += ('Log:\n')
            for j in i['log']:
                text += ('\t%s\n'%j)
        return text

    def __auto_combine__(self):
        dict = self.__combine__(self.captain, self.first_mate)
        self.account = dict

    def print_dict(self, dict=None):
        if dict == None:
            dict = self.account
        for i in dict:
            print('\n')
            print('Date: %s'%i['date'])
            print('Cash: %.2f'%i['cash'])
            print('Portfolio:')
            for k in i['portfolio']:
                print('\tCode: %s, Amount: %.2f, Bought Price: %.2f, Market Price: %.2f'%(k['code'], k['shares'], k['price'], k['market']))
            print('Cost: %.2f, Value: %.2f'%(i['cost'], i['value']))
            print('Log:')
            for j in i['log']:
                print('\t%s'%j)

    def print_last(self):
        self.print_dict(self.account[-1:])

    def amount(self, code):
        amount = 0.0
        if len(self.account) >= 1:
            dict = self.account[-1]
            for i in dict['portfolio']:
                if i['code'] == code:
                    amount = i['shares']
        return amount

    def __convert_to_float__(self, number):
        result = None
        try:
            result = float(number)
        except:
            pass
        return result

    def __buy_amount_calculator__(self, ratio, price, in_graph=False):
        result = 0.0
        ratio = self.__convert_to_float__(ratio)
        price = self.__convert_to_float__(price)
        if ratio != None and price != None:
            cash_available = self.cash()
            result = int(((cash_available / price) * ratio) / 100) * 100
            if in_graph == True:
                result += 0.01
        return result

    def buy(self, code, quantity, price, date, in_graph=False):
        if quantity <= 1:
            quantity = self.__buy_amount_calculator__(quantity, price, in_graph)
        if code in self.stock_list:
            date = self.__opening_day__(code, date)
            original = copy.deepcopy(self.captain)
            self.captain.buy(date, code, quantity, price)
            if self.__operation_complete__(self.captain, original):
                fee = self.__fee_calculator__(price, quantity, 'buy')
                self.captain.withdraw(date, fee)
                ref_price = self.__get_reference_price__(code, date, price)
                self.__reflect_in_first_mate__()
                self.first_mate.update(date, {code: ref_price})
                self.__auto_combine__()

    def cash(self):
        return self.account[-1]['cash']

    def deposit(self, quantity, date):
        date = self.__opening_day__('399300', date)
        dict = list(self.account)
        self.captain.deposit(date, quantity)
        self.first_mate.deposit(date, quantity)
        self.__auto_combine__()
        if dict != self.account:
            self.total_investment += quantity

    def withdraw(self, quaitity, date):
        date = self.__opening_day__('399300', date)
        dict = list(self.account)
        self.captain.withdraw(date, quaitity)
        self.first_mate.withdraw(date, quaitity)
        self.__auto_combine__()
        if dict != self.account:
            self.total_investment -= quaitity

    def __sell_amount_calculator__(self, ratio, price, code):
        result = 0.0
        ratio = self.__convert_to_float__(ratio)
        price = self.__convert_to_float__(price)
        if ratio != None and price != None:
            amount_available = self.amount(code)
            result = int(amount_available * ratio / 100) * 100
        return result

    def sell(self, code, quantity, price, date):
        if quantity <= 1:
            quantity = self.__sell_amount_calculator__(quantity, price, code)
        if code in self.stock_list:
            date = self.__opening_day__(code, date)
            original = copy.deepcopy(self.captain)
            self.captain.sell(date, code, quantity, price)
            if self.__operation_complete__(self.captain, original):
                fee = self.__fee_calculator__(price, quantity, 'sell')
                self.captain.withdraw(date, fee)
                ref_price = self.__get_reference_price__(code, date, price)
                self.__reflect_in_first_mate__()
                self.first_mate.update(date, {code: ref_price})
                self.__auto_combine__()

    def fill(self, progress_bar=True):

        def date_filled_list():
            date_filled = []
            date_existed = [i['date'] for i in self.account]
            start_date = date_existed[0]
            end_date = date_existed[-1]
            duration = (self.functions['date_encoding'](end_date) - self.functions['date_encoding'](start_date)).days
            opening_days_list = self.functions['opening_days'](days=duration, start_date=end_date)
            for i in opening_days_list:
                if self.functions['date_encoding'](i) > self.functions['date_encoding'](start_date):
                    if self.functions['date_encoding'](i) < self.functions['date_encoding'](end_date):
                        if i not in date_existed:
                            date_filled.append(i)
            return date_filled

        date_filled_list = date_filled_list()
        captain = copy.deepcopy(self.captain)
        first_mate = copy.deepcopy(self.first_mate)
        for i in date_filled_list:
            captain.update(i, fill_blank=True)
            first_mate.update(i, fill_blank=True)

        first_mate_dict = first_mate.account_dict()
        count = 1
        for k in date_filled_list:
            for ki in first_mate_dict:
                if ki['time'] == k:
                    update_dict = {}
                    for kc in ki['portfolio'][1:]:
                        update_dict[kc['name']] = self.__get_reference_price__(kc['name'], k, kc['ratio'])
                    first_mate.update(k, update_dict)
            if progress_bar == True:
                self.functions['progress_bar'](count * 100 / len(date_filled_list))
                count += 1

        content = self.__combine__(captain, first_mate)
        return content

    def plot_performance_with_index(self, idx='sh', type='close', method='show', id=''):
        filled = self.fill()[1:]
        list = self.performance.performance_with_index(filled, idx, type)
        length = len(list)

        x_date = [date2num(self.functions['date_encoding'](i['date'])) for i in list]
        y_portfolio_return = [i['portfolio_value_change'] for i in list]
        y_market_return = [i['market_value_change'] for i in list]
        y_price_return = [i['price_value_change'] for i in list]

        fig, portfolio_return = plt.subplots()
        mondays = WeekdayLocator(MONDAY)
        alldays = DayLocator()
        weekFormatter = DateFormatter('%b %d')
        portfolio_return.xaxis.set_major_locator(mondays)
        portfolio_return.xaxis.set_minor_locator(alldays)
        portfolio_return.xaxis.set_major_formatter(weekFormatter)
        portfolio_return.xaxis_date()
        portfolio_return.plot(x_date, y_portfolio_return, 'b-')
        portfolio_return.plot(x_date, y_market_return, 'y-')
        portfolio_return.plot(x_date, y_price_return, 'g-')
        portfolio_return.set_ylabel('Return')
        portfolio_return.set_xlabel('%s to %s, Portfolio vs Market'%(list[0]['date'], list[-1]['date']))
        if method == 'show':
            plt.show()
        if method == 'save':
            try:
                os.mkdir(os.path.join(os.getcwd(), 'graph'))
            except:
                pass
            path = os.path.join(os.getcwd(), 'graph/%s%sto%s'%('%s '%id, list[0]['date'], list[-1]['date']))
            fig.set_size_inches(math.sqrt(int(length)) * 10 / 3, 10)
            plt.savefig(path)
            with open('%s.txt'%path, 'w') as f:
                text = self.__output_dict__()
                f.write(text)

class StockAccountPerformance():

    def __init__(self):
        self.date_encoding = at.date_encoding

    def __return_index__(self, dict):
        result = []
        if len(dict) >= 0:
            for i in dict:
                line = {}
                line['date'] = i['date']
                line['value'] = i['value']
                line['index'] = i['value'] / i['cost']
                line['change'] = (i['value'] / i['cost'] - 1) * 100
                result.append(line)
        return result

    def __price_return_index__(self, dict):

        def avg_price(portfolio):
            average = 0.0
            num = len(portfolio)
            if num > 0:
                for i in portfolio:
                    average += i['market'] / num
            return average
        base = 0.0
        for j in dict:
            base = avg_price(j['portfolio'])
            if base != 0.0:
                break
        result = []
        if len(dict) >= 0:
            for i in dict:
                line = {}
                line['date'] = i['date']
                line['price'] = avg_price(i['portfolio'])
                line['index'] = line['price'] / base
                line['change'] = (line['index'] - 1) * 100
                result.append(line)
        return result


    def __market_return_index__(self, dict, idx='sh', type='close'):
        result = []
        base = ms.get_index(dict[0]['date'], idx, type)
        start = dict[0]['date']
        end = dict[-1]['date']
        duration = (self.date_encoding(end) - self.date_encoding(start)).days
        if duration > 0:
            idx_list = ms.get_index(start, idx, type, duration)
            for i in dict:
                for j in idx_list:
                    if i['date'] == j['date']:
                        line = {}
                        line['date'] = i['date']
                        line['index'] = j['index'] / base
                        line['change'] = ((line['index'] - 1) * 100)
                        result.append(line)
                        break
        return result

    def performance_with_index(self, dict, idx='sh', type='close'):
        result = []
        if len(dict[-1]['portfolio']) >= 0:
            portfolio_performance_list = self.__return_index__(dict)
            market_performance_list = self.__market_return_index__(dict, idx, type)
            price_performance_list = self.__price_return_index__(dict)
            for i in portfolio_performance_list:
                for j in market_performance_list:
                    if i['date'] == j['date']:
                        for k in price_performance_list:
                            if j['date'] == k['date']:
                                line = {}
                                line['date'] = i['date']
                                line['portfolio_value'] = i['value']
                                line['portfolio_return_index'] = i['index']
                                line['portfolio_value_change'] = i['change']
                                line['market_return_index'] = j['index']
                                line['market_value_change'] = j['change']
                                line['price_return_index'] = k['index']
                                line['price_value_change'] = k['change']
                                result.append(line)
                                break
                        break
        return result

def portfolio_performance(list, idx='sh', type='close', method='save'):
    list_loaded = list.strip().split('\n')
    list_loaded = [i.strip() for i in list_loaded]
    list = []
    for i in list_loaded:
        line = {}
        split = i.split(',')
        line['date'] = split[0]
        line['action'] = split[1].strip().split(' ')
        list.append(line)
    account = StockAccount(time = list[0]['date'])
    account.deposit(float(list[0]['action'][1]), list[0]['date'])
    for j in list[1:]:
        date = j['date']
        buy_or_sell = j['action'][0]
        amount = float(j['action'][1])
        code = j['action'][2]
        price = float(j['action'][-1])
        if buy_or_sell == 'buy':
            account.buy(code, amount, price, date)
        if buy_or_sell == 'sell':
            account.sell(code, amount, price, date)
    account.plot_performance_with_index(idx, type, method)