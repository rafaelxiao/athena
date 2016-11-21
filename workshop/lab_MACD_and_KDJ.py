import trader as tr
import analyst as al

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