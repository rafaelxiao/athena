import tushare as ts
import assistant as at
import analyst as al
import messenger as ms
import trader as tr
import matplotlib.pyplot as plt
import os

p = al.PriceDeviation()
s = p.__diff_lists__('000625',duration=360, smooth=7)
state = 'unhold'
list = []
i_hold = 0
for i in s:
    if i['smoothed difference'] >= 0:
        if i_hold < 0 and state == 'unhold':
            list.append({i['date']: 'buy'})
            state = 'hold'
    if i['smoothed difference'] < 0:
        if i_hold > 0 and state == 'hold':
            list.append({i['date']: 'sell'})
            state = 'unhold'
    i_hold = i['smoothed difference']
for i in list:
    print(i)