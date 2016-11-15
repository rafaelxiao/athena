import math
import messenger as ms

def turnover(volume, code):
    '''
    Calculate the volume to outstanding ratio
    :param volume: int, the volume of transaction
    :param code: string, the stock index
    :return: float, the volume to outstanding ratio
    '''
    outstanding = ms.get_stock_outstanding(code)
    ratio = float(volume / outstanding)
    return ratio

def periodic_auction_volume(code, date):
    '''
    Get the volume during the periodic auction period
    :param code: string, stock index
    :param date: string, date in format '2016-10-11'
    :return: int, the volume
    '''
    tick_data = ms.get_tick_data(code, date)
    volume = tick_data[-1:].volume.values[0]
    if math.isnan(volume):
        volume = 0
    volume = 100 * volume
    volume = int(volume)
    return volume






