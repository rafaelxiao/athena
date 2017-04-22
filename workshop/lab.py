import tushare as ts
import assistant as at
import analyst as al
import messenger as ms
import trader as tr
import matplotlib.pyplot as plt
import os
import numpy as np

code = '000022'
date = '2017-04-14'
duration = 300
smooth = 7

p = al.PriceDeviation()
p.price_diff_list_save(code, date, duration, smooth)
list = p.price_diff_list_load(code, date, duration, smooth)

sub_list = []
for k in list:
    print(k)
    sub_list.append(k['smoothed difference'])

print(np.average(sub_list))