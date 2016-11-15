import messenger as ms
import analyst as al
import assistant as at

def periodic_auction_scanner(code, days, start_date=''):
    '''
    Scanner the periodic auction volume for multiple days
    :param code: the stock index
    :param days: the duration
    :param start_date: specifying the start date if needed
    :return: a list of (date, ratio) pairs
    '''
    outstanding = ms.get_stock_outstanding(code)
    content_list = []
    days_list = at.opening_days(code, days, start_date)
    count = 1
    for i in days_list:
        volume = al.periodic_auction_volume(code, i)
        ratio = float(volume / outstanding)
        ratio = round(ratio * 100, 5)
        pair = (i, ratio)
        content_list.append(pair)
        at.process_monitor(count / len(days_list) * 100)
        count += 1
    return content_list