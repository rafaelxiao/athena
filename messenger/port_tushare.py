import tushare as ts
import assistant as at
import datetime, threading, queue, os

basic_csv = 'basic.csv'

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
    # outstanding = ts.get_stock_basics().ix[code].outstanding
    # outstanding = outstanding * 10000
    # outstanding = int(outstanding)
    # return outstanding
    return 1338000000

def save_basic():
    '''
    Save the stock basics into a csv file
    :return:
    '''
    basic = ts.get_stock_basics()
    path = os.path.join(basic_csv)
    basic.to_csv(path)

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

def get_series_hist_data(code, days, start_date = '', multi_threads = 20):
    '''
    Gather the stock data for a range of days
    :param code: str, stock index
    :param days: int, the number of days
    :param start_date: str, the start date
    :param multi_threads: int, the number of threads, default 20
    :return: a list for the data of a series of dates
    '''
    if start_date != '':
        start_date = at.date_encoding(start_date)
    else:
        start_date = datetime.date.today()
    def record_thread_result(code, date, q, q_n):
        result = get_stock_hist_data(code, date)
        if result == None:
            q_n.put(result)
        else:
            q.put(result)
    q = queue.Queue()
    q_n = queue.Queue()
    list = []
    while q.qsize() < days and q_n.qsize() < days * 2:
        threads = []
        for days_back in range(0, multi_threads):
            day_mark = start_date - datetime.timedelta(days_back)
            threads.append(threading.Thread(target=record_thread_result, args=(code, at.date_decoding(day_mark), q, q_n)))
        for t in threads:
            t.start()
        for n in threads:
            n.join()
        start_date -= datetime.timedelta(multi_threads)
    while not q.empty():
        list.append(q.get())
    list = at.sort_list_by_date(list)
    list = list[-days:]
    return list