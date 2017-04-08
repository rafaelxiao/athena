import tushare as ts
import assistant as at
import analyst as al
import messenger as ms
import matplotlib.pyplot as plt
import os

h = al.PriceDeviation()

'''
for i in h.__diff_lists_multi_smoothing__('600313', smooth=[3, 10]):
    for j in i:
        print("%s: %s"%(j, i[j]))
    print('---------------')
'''
h.plot_difference_multi_smoothing('600313', [7, 15, 30], duration=900, period_length=300, type='save')
