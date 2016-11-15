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

def get_stock_hist_data(code, date, type = ' '):
    '''
    Get the stock's data of a specific day
    :param code: str, stock index
    :param date: str, date
    :param type: str, specify the value returned
    :return: a list of relevant information
    '''
    try:
        hist = ts.get_k_data(code, start=date, end=date)
        hist = hist.iloc[0]
        open = hist.open
        close = hist.close
        high = hist.high
        low = hist.low
        volume = int(float(hist.volume)) * 100
        list = (date, code, open, close, high, low, volume)
        if type == 'open':
            return list[2]
        elif type == 'close':
            return list[3]
        elif type == 'high':
            return list[4]
        elif type == 'low':
            return list[5]
        elif type == 'volume':
            return list[6]
        else:
            return list
    except: pass