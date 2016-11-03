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
