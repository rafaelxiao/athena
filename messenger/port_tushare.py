import tushare as ts
import assistant as at
import pandas as pd
import messenger as ms
import datetime, threading, queue, os

local_data = {'basics': 'data/basics.csv'}
board_type = {'sh': ['600', '601', '603'], 'sz': ['000'], 'cyb': ['300'], 'zxb': ['002']}
outstanding_multiple = [100000000, 100000]
largest_outstanding = 2000
volume_multiple = 100

def get_tick_data(code, date):
    '''
    Get the tick data of specific trading day
    :param code: string, stock index
    :param date: string, date, '2016-10-11'
    :return: a pandas frame of tick data
    '''
    tick_data = ts.get_tick_data(code, date)
    return tick_data

def get_stock_basics(local = False):
    '''
    Get the stock basic information
    :return: None
    '''
    path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), local_data['basics']))
    if local == True:
        basics = pd.read_csv(path, dtype=object)
        basics = basics.set_index('code')
    else:
        try:
            basics = ts.get_stock_basics()
            basics.to_csv(path, encoding='utf-8')
        except:
            basics = pd.read_csv(path, dtype=object)
            basics = basics.set_index('code')
    return basics

def get_stock_outstanding(code):
    '''
    Get the stock outstanding
    :param code: string, stock index
    :param save: int, specifying weather catch the basics to local
    :return: the share outstandings
    '''
    outstanding = ms.get_stock_basics(True).ix[code].outstanding
    if '.' in str(outstanding) and float(outstanding) <= float(largest_outstanding):
        multiple = outstanding_multiple[0]
    else:
        multiple = outstanding_multiple[1]
    outstanding = float(outstanding) * multiple
    outstanding = int(outstanding)
    return outstanding

def get_stock_total_shares(code):
    '''
    Get the stock total shares
    :param code: string, stock index
    :param save: int, specifying weather catch the basics to local
    :return: the total shares
    '''
    totals = ms.get_stock_basics(True).ix[code].totals
    if '.' in str(totals) and float(totals) <= float(largest_outstanding):
        multiple = outstanding_multiple[0]
    else:
        multiple = outstanding_multiple[1]
    totals = float(totals) * multiple
    totals = int(totals)
    return totals

def get_stock_code_by_type(type):
    '''
    Return a list of stock index in a specific group
    :param type: str, the board type
    :return: a list of index
    '''
    path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), local_data['basics']))
    basics = pd.read_csv(path, dtype='str')
    basics = basics.code[basics.code.str[:3].isin(board_type[type])]
    return basics.tolist()

def complete_stock_list():
    '''
    Generate a complete list of stock
    :return: A list of stock
    '''
    path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), local_data['basics']))
    list = pd.read_csv(path, dtype='str')
    list = list.code.tolist()
    return list

def get_stock_hist_data(code, date, type=''):
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
        volume = int(float(hist.volume)) * volume_multiple
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

def get_stock_hist_data_yesterday(code, date_t, type=''):
    '''
    Get the stock's data of the previous day of a specific day
    :param code: str, stock index
    :param date: str, date
    :param type: str, specify the value returned
    :return: a list of relevant information
    '''
    date = at.opening_days(code, 2, date_t)[0]
    return ms.get_stock_hist_data(code, date, type)

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

def get_stock_basics_dict(code):
    '''
    Return the stock basics in a dict
    :param code: str, stock index
    :return: a index
    '''
    content_list = ms.get_stock_basics(True).ix[code].to_dict()
    content_list['totals'] = ms.get_stock_total_shares(code)
    content_list['outstanding'] = ms.get_stock_outstanding(code)
    return content_list

def get_stock_report(code, year, quarter, type):
    '''
    Return the dict of inquired data
    :param code: str, stock index
    :param year: int, year
    :param quarter: int, quarter
    :param type: 'report', 'profit', 'operation', 'growth', 'debt', 'cash_flow'
    :return: the dict
    '''
    function_list = {
        'report': ts.get_report_data,
        'profit': ts.get_profit_data,
        'operation': ts.get_operation_data,
        'growth': ts.get_growth_data,
        'debt':ts.get_debtpaying_data,
        'cash_flow':ts.get_cashflow_data,
    }
    try:
        content_list = function_list[type](year, quarter).set_index('code').ix[code].to_dict()
        return content_list
    except:
        pass

def get_stock_report_frame(year, quarter, type):
    '''
    Return the data frame of inquired data
    :param year: int, year
    :param quarter: int, quarter
    :param type: 'report', 'profit', 'operation', 'growth', 'debt', 'cash_flow'
    :return: the data frame
    '''
    function_list = {
        'report': ts.get_report_data,
        'profit': ts.get_profit_data,
        'operation': ts.get_operation_data,
        'growth': ts.get_growth_data,
        'debt':ts.get_debtpaying_data,
        'cash_flow':ts.get_cashflow_data,
    }
    try:
        content_list = function_list[type](year, quarter).set_index('code')
        return content_list
    except:
        pass

def get_industry_classified():
    '''
    Return the industry classified DataFrame
    :return: the DataFrame
    '''
    content = ts.get_industry_classified()
    return content

def get_concept_classified():
    '''
    Return the concept classified DataFrame
    :return: the DataFrame
    '''
    content = ts.get_concept_classified()
    return content

def get_area_classified():
    '''
    Return the area classified DataFrame
    :return: the DataFrame
    '''
    content = ts.get_area_classified()
    return content