import tushare as ts
import assistant as at
import messenger as ms
import matplotlib.pyplot as plt

def see(code, date):

    t = ts.get_tick_data(code, date)
    tbuy = t[t.type == '买盘']
    tsell = t[t.type == '卖盘']
    # outstanding = ms.get_stock_outstanding(code)
    outstanding = 1082000000
    # tbuy_mean = tbuy.price.mean()
    # tsell_mean = tsell.price.mean()
    tbuy_amout = tbuy.amount.sum()
    tsell_amount = tsell.amount.sum()
    # tbuy_avg_mean = tbuy.amount.sum() / tbuy.volume.sum() / 100
    # tsell_avg_mean = tsell.amount.sum() / tsell.volume.sum() / 100

    return (tbuy_amout - tsell_amount)/outstanding

def see_series(code, date='', duration=10):
    days = ms.get_series_hist_data(code, duration, date)
    list = []
    z = days[0][0]
    for i in range(len(days)):

        date = days[i][0]
        gap = float(days[i][3]) - float(days[i][2])
        open = float(z[3])
        # open = float(z[3])
        z = days[i]
        rangex = see(code, days[i][0])
        list.append((date, gap, rangex, open))


    return list

def sufficiency(code, date='', duration = 30, rangex =1):
    days = ms.get_series_hist_data(code, duration, date)
    list = []
    hold = 0
    sh = 0
    for i in range(len(days)):
        dates = days[i][0]
        c = see_series(code, dates, rangex)
        sum1 = 0
        sum2 = 0
        for k in c:
            sum1 += k[1]
            sum2 += k[2]
        if sum1 >= sum2:
            sign = 1
        else: sign = -1
        suff = abs((sum1 -sum2)/ k[3] * 100) * sign
        s = 2/3 * sh + 1/3 * suff
        sh = s
        hold += suff
        unit = (dates, sum1, sum2, suff, hold, s)
        list.append(unit)
        at.process_monitor(i / len(days) * 100)
    return list

c = sufficiency('600362', date='2016-02-02', duration=120)

for i in c:
    if i[5]>1 or i[5]<-1:
        print(i)

xs = []
ys = []

for h in c:
    xs.append(at.date_encoding(h[0]))
    ys.append(h[5])

plt.plot(xs, ys)
plt.show()

