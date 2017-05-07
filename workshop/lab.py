import tushare as ts
import assistant as at
import analyst as al
import messenger as ms
import trader as tr
import matplotlib.pyplot as plt
import os
import numpy as np

code = '000625'
date = '2017-05-03'
duration = 315
smooth = 3

h = al.PriceDevAna()
h.group_count_detail_print(code, date, [0], length=15, duration=duration, type='combine', discover_mode=True, day_interval=1)
