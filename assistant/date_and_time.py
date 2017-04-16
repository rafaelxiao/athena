import datetime
import messenger as ms
import assistant as at

# The stock index to generate openning days
opening_days_tester = '399300'

def date_encoding(date_string):
    '''
    Encoding a string into a date format.
    :param date_string: a string in format like "2016-01-02"
    :return: an encoded date format
    '''
    encoded = datetime.date(int(date_string[0:4]), int(date_string[5:7]), int(date_string[8:10]))
    return encoded

def date_decoding(date):
    '''
    Decoding a date format into a string.
    :param date: an encoded date format
    :return: a string in format like "2016-01-02"
    '''
    decoded = date.strftime("%Y-%m-%d")
    return decoded

def workday_list(days, start_date = ''):
    '''
    Generating a list of workdays.
    :param days: int, specifying the range before start date
    :param start_date: a string in format like "2016-01-02"
    :return: a list containing date format elements
    '''
    if start_date != '':
        start_date = date_encoding(start_date)
    else:
        start_date = datetime.date.today()
    list = []
    days_count = 0
    days_valid = 0
    while days_valid < days:
        day = start_date - datetime.timedelta(days_count)
        if day.weekday() < 5:
            list.append(day)
            days_valid += 1
        days_count += 1
    return list

def opening_days(code=opening_days_tester, days=10, start_date='', multi_threads = 20):
    '''
    Generate a list of days when data available for the stock
    :param code: str, stock index
    :param days: int, the number of days
    :param start_date: str, the start date
    :param multi_threads: int, the number of threads, default 20
    :return: the list of days
    '''
    list = ms.get_series_hist_data(code, days, start_date, multi_threads)
    list = [i[0] for i in list]
    return list

def is_opening_day(code, date):
    result = False
    list = opening_days(code, 1, date, 1)
    if len(list) >= 1:
        if list[0] == date:
            result = True
    return result

def next_opening_day(code, date, shifter=1):

    def shift_one_day(date):
        result = at.date_decoding(at.date_encoding(date) + datetime.timedelta(shifter))
        return result

    count = 0
    result = None
    while True:
        if is_opening_day(code, date):
            result = date
            break
        elif count>= 300:
            break
        else:
            date = shift_one_day(date)
            count += 1

    return result


class TimeStamp:
    '''
    A class to represent the time
    '''

    def make_time(self, hour, minute):
        hour = hour % 24
        minute = minute % 60
        return (hour, minute)

    def select_hour(self, time_stamp):
        return time_stamp[0]

    def select_minute(self, time_stamp):
        return time_stamp[1]

    def time_to_value(self, time_stamp):
        value = time_stamp[0] * 60 + time_stamp[1]
        return value

    def value_to_time(self, value):
        hour = int(value / 60)
        minute = value % 60
        time_stamp = self.make_time(hour, minute)
        return time_stamp

    def add_time(self, time_stamp, increment):
        time_stamp = self.time_to_value(time_stamp)
        time_stamp = time_stamp + increment
        time_stamp = self.value_to_time(time_stamp)
        return time_stamp

    def equal(self, time_stamp_1, time_stamp_2):
        time_stamp_1 = self.time_to_value(time_stamp_1)
        time_stamp_2 = self.time_to_value(time_stamp_2)
        return time_stamp_1 == time_stamp_2

    def less_than(self, time_stamp_1, time_stamp_2):
        time_stamp_1 = self.time_to_value(time_stamp_1)
        time_stamp_2 = self.time_to_value(time_stamp_2)
        return time_stamp_1 < time_stamp_2

def time_list():
    '''
    Generate a time list of trade opening time
    :return: a list in format (hour, minute)
    '''
    TS = TimeStamp()
    open = TS.make_time(9, 30)
    close = TS.make_time(15, 1)
    noon_break = (TS.make_time(11, 31), TS.make_time(13, 0))
    time_list = []
    i = open
    while TS.less_than(i, close):
        if TS.less_than(i, noon_break[0]) or not TS.less_than(i, noon_break[1]):
            time_list.append(i)
        i = TS.add_time(i, 1)
    return time_list

def split_period(start_date, total_length, period_lengh):
    '''
    Split the time in to several period, which each unit with 'start_date' and 'days'
    :param start_date: the start date of the whole period
    :param total_length: the total length
    :param period_length: the length of each period
    :return: a list of dictionary with 'start_date' and 'days'
    '''
    if start_date == '':
        start_date = date_decoding(datetime.date.today())
    periods_number = int(total_length / period_lengh)
    periods_last = total_length % period_lengh
    periods_list = []
    for i in range(periods_number):
        periods_unit = {}
        periods_unit['start_date'] = date_decoding(date_encoding(start_date) - datetime.timedelta(i * period_lengh))
        periods_unit['days'] = period_lengh
        periods_list.append(periods_unit)
    if total_length % period_lengh != 0:
        periods_unit = {}
        periods_unit['start_date'] = date_decoding(date_encoding(start_date) - datetime.timedelta(periods_number * period_lengh))
        periods_unit['days'] = periods_last
        periods_list.append(periods_unit)
    return periods_list[::-1]

