import assistant as at
import analyst as al
import agent as ag
import trader as tr
import analyst as al
import workshop.lab as lab
import time
import threading
import math
import messenger as ms
import matplotlib.pyplot as plt
'''
s = lab.Stock()

z = s.initiate('600313', 500, 2)

x = s.initiate('600313', 200, 4)

y = s.initiate('600333', 500, 2)

print(z)
print(s.add(z, y))
print(s.add(z, x))
print(s.retrieve(z, z))

'''
'''
s = ms.get_series_hist_data('002427',500)
z = al.MACD().macd_of_a_period('002427', 500)
y = al.KDJ().kdj_of_a_period('002427', 500)
list = []
for i in range(len(s)):
    date = s[i][0]
    price = s[i][3]
    macd = z[i][1][0]
    d = y[i][1][1]
    j = y[i][1][2]
    # unit = (date, price, macd, float(price) / math.log(float(macd)))
    unit = (date, float(price)/macd, d, j, d-j)
    list.append(unit)

for k in list:
    if k[1]>-100 and k[1] < 0and k[3]<5 and k[4]>30:
        print(k)
'''
x=[1,2,3,4,5]
y=[7,2,1,3,2]
plt.plot(x,y)
plt.show()