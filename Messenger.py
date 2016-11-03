import tushare as ts

def get_tick_data(code, date):
    '''
    Get the tick data of specific trading day
    :param code: string, stock index
    :param date: string, date, '2016-10-11'
    :return: a pandas frame of tick data
    '''
    tick_data = ts.get_tick_data(code, date)
    return tick_data

def get_stock_outstanding(code):
    '''
    Get the stock outstanding
    :param code: string, stock index
    :return: the share outstandings
    '''
    outstanding = ts.get_stock_basics().ix[code].outstanding
    outstanding = outstanding * 10000
    outstanding = int(outstanding)
    return outstanding
