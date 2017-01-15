import tushare as ts
import assistant as at
import analyst as al
import messenger as ms
import matplotlib.pyplot as plt
import random

def stop_structure(code, date, type='long', top_n = 10, top_percent=0):

    def subset_big_and_small(tick, thread, type):
        if type == 'big':
            return tick[tick.amount >= thread]
        if type == 'small':
            return tick[tick.amount < thread]

    def subset_buy_and_sell(tick, type):
        if type == 'buy':
            return tick[tick.type == '买盘']
        if type == 'sell':
            return tick[tick.type == '卖盘']

    try:
        tick = ms.get_tick_data(code, date)

        high_band_price_thread = tick.price.max() * (1 - top_percent / 100)

        high_band = tick[tick.price >= high_band_price_thread]
        large_amount_thread = high_band.sort_values('amount', ascending = False).head(top_n)['amount'].iloc[-1]

        high_band_big = subset_big_and_small(high_band, large_amount_thread, 'big')
        high_band_small = subset_big_and_small(high_band, large_amount_thread, 'small')

        high_band_big_buy = subset_buy_and_sell(high_band_big, 'buy')
        high_band_big_sell = subset_buy_and_sell(high_band_big, 'sell')
        high_band_small_buy = subset_buy_and_sell(high_band_small, 'buy')
        high_band_small_sell = subset_buy_and_sell(high_band_small, 'sell')

        total_volume = tick.volume.sum()
        outstanding = ms.get_stock_outstanding(code)
        turnover = total_volume * 10000 / outstanding
        high_band_total_volume = high_band.volume.sum()

        high_band_big_buy_volume = high_band_big_buy.volume.sum()
        high_band_big_sell_volume = high_band_big_sell.volume.sum()
        high_band_small_buy_volume = high_band_small_buy.volume.sum()
        high_band_small_sell_volume = high_band_small_sell.volume.sum()

        '''
        content_raw = [turnover, \
                       high_band_total_volume / total_volume * 100, \
                       high_band_big_buy_volume / total_volume * 100, \
                       high_band_big_sell_volume / total_volume * 100, \
                       high_band_small_buy_volume / total_volume * 100, \
                       high_band_small_sell_volume / total_volume * 100]
        '''
        content_raw = [turnover, \
                       high_band_total_volume / outstanding * 10000, \
                       high_band_big_buy_volume / outstanding * 10000, \
                       high_band_big_sell_volume / outstanding * 10000, \
                       high_band_small_buy_volume / outstanding * 10000, \
                       high_band_small_sell_volume / outstanding * 10000]

        content = []
        for i in content_raw:
            content.append(float(round(i, 2)))

        return [date] + content

    except: pass

code = '600679'
dates = "2016-11-10, 2016-11-15, 2016-11-16, 2016-11-18, 2016-11-21, 2016-11-22, 2016-12-08, 2016-12-09, 2016-12-12, 2016-12-14, 2016-12-16, 2016-12-22"
date_list = [i.replace(' ', '') for i in dates.split(',')]
for i in date_list:
    print(stop_structure(code, i))