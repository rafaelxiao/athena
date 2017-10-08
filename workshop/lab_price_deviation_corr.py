import messenger as ms
import analyst as al
import numpy as np
import assistant as at
import matplotlib.pyplot as plt

h = al.PriceDeviation()
h.price_diff_list_save('002415', date='2017-06-28', duration=600, smooth=3)
origin_data = h.price_diff_list_load('002415', date='2017-06-28', duration=600, smooth=3)
origin_data = origin_data[-200:]

result = []
date_list = []
for i in range(30, len(origin_data)):
    date = origin_data[i]['date']

    sub_list = origin_data[i-30:i]
    diff_list = [i['smoothed difference'] for i in sub_list]
    theo_list = [i['smoothed theoretical'] for i in sub_list]
    corr = np.correlate(diff_list, theo_list)
    print(date, corr)
    result.append(corr)
    date_list.append(at.date_encoding(date))

plt.plot(date_list, result)
plt.show()