'''
start = time.clock()
s = lab.MACDWithKDJ()
z = s.__macd_and_kdj_list__('600313', 20, '2016-11-10')
# z = s.__macd__('600313', 20, '2016-11-10')
for i in z:
    print(i)
end = time.clock()
print("read: %f s"% (end - start))
'''
'''
s = ms.get_series_hist_data('002466',500)
z = al.MACD().macd_of_a_period('002466', 500)
# y = al.KDJ().kdj_of_a_period('002466', 500)
h = 0
list = []
for i in range(len(s)):
    date = s[i][0]
    macd = z[i][1][0]
    h += macd * 100
    unit = (date, macd, h)
    list.append(unit)


list = []
for i in range(len(s)):
    date = s[i][0]
    price = s[i][3]
    macd = z[i][1][0]
    d = y[i][1][1]
    j = y[i][1][2]
    unit = (date, float(price) / macd, j - d, d, j)
    list.append(unit)

for i in list:
    # if (i[1] < 200 and i[1] > 0) and i[2] > 10 and i[3] < 40 and i[4] > h[4]:
        print(i)
'''


class MACDWithKDJ():

    def __init__(self):
        self.__stock_account__ = tr.StockAccount()
        self.__calculate_macd__ = al.MACD()
        self.__calculate_kdj__ = al.KDJ()

    def __macd__(self, code, duration, date='', smooth=120):
        macd_list = self.__calculate_macd__.macd_of_a_period(code, duration, date, smooth)
        return macd_list

    def __kdj__(self, code, duration, date='', smooth=30):
        kdj_list = self.__calculate_kdj__.kdj_of_a_period(code, duration, date, smooth=smooth)
        return kdj_list

    def __macd_and_kdj_list__(self, code, duration, date='', smooth=30):
        kdj_list = self.__kdj__(code, duration, date, smooth)
        macd_list = self.__macd__(code, duration, date, smooth + 90)
        content_list = []
        motion = 'start'
        for i in range(len(kdj_list)):
            date = kdj_list[i][0]
            k = kdj_list[i][1][0]
            d= kdj_list[i][1][1]
            j = kdj_list[i][1][2]
            macd = macd_list[i][1][0]
            unit = (kdj_list[i][0], (kdj_list[i][1][0], kdj_list[i][1][1], kdj_list[i][1][2], macd_list[i][1][0]))
            content_list.append(unit)
        return content_list