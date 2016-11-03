import Engine, Messenger, Toolbox

def periodic_auction_scanner(code, days, start_date = ''):
    '''
    Scanner the periodic auction volume for multiple days
    :param code: the stock index
    :param days: the duration
    :param start_date: specifying the start date if needed
    :return: a list of (date, ratio) pairs
    '''
    outstanding = Messenger.get_stock_outstanding(code)
    list = []
    days_list = Toolbox.workday_list(days, start_date)
    for i in days_list:
        volume = Engine.periodic_auction_volume(code, i)
        ratio = float(volume / outstanding)
        ratio = round(ratio * 100, 5)
        pair = (Toolbox.date_decoding(i), ratio)
        list.append(pair)
    return list