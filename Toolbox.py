import datetime

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
