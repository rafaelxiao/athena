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

def get_stock_hist_data(code, date):
    '''
    Get the stock's data of a specific day
    :param code: str, stock index
    :param date: str, date
    :return: a list of relevant information
    '''
    hist = ts.get_k_data(code, start=date, end=date)
    hist = hist.iloc[0]
    open = hist.open
    close = hist.close
    high = hist.high
    low = hist.low
    volume = int(float(hist.volume)) * 100
    list = (date, code, open, close, high, low, volume)
    return list

def get_stock_open_price(code, date):
    '''
    Get the open price of a specific day
    :param code: str, stock index
    :param date: str, date
    :return: float, open price
    '''
    open = get_stock_hist_data(code, date)[2]
    return open

def get_stock_close_price(code, date):
    '''
    Get the close price of a specific day
    :param code: str, stock index
    :param date: str, date
    :return: float, close price
    '''
    close = get_stock_hist_data(code, date)[3]
    return close