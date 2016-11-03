import tushare as ts
import datetime

class FlowTracker:

    def get_tick_data(self, stock_idx, date):
        return ts.get_tick_data(stock_idx, date)

    def get_type(self, tick_data):
        buy_in = tick_data[tick_data.type == '买盘'].type.count()
        sell_out = tick_data[tick_data.type == '卖盘'].type.count()
        neutral = tick_data[tick_data.type == '中性盘'].type.count()
        return (buy_in, sell_out, neutral)

    def summarize(self, stock_idx, date):
        tick_data = self.get_tick_data(stock_idx, date)
        type = self.get_type(tick_data)
        print(type[0], type[1], type[2])

    def periodic_auction(self, stock_idx, days, start_date=datetime.date.today()):
        if start_date != datetime.date.today():
            start_date = datetime.date(int(start_date[0:4]), int(start_date[5:7]), int(start_date[8:10]))
        list = []
        i = 0
        j = 0
        outstanding = ts.get_stock_basics().ix[stock_idx].outstanding
        while j < days:
            date = start_date - datetime.timedelta(i)
            if date.weekday() < 5:
                date_str = date.strftime("%Y-%m-%d")
                try:
                    data = ts.get_tick_data(stock_idx, date_str)
                    list.append([date_str,  data[-1:].volume.values[0] / outstanding])
                    j += 1
                except: pass
            i += 1
        return list

    def danger_spotter(self):
        watchlist = []
        idx = ts.get_stock_basics().index
        print('List Ready!!!')
        for i in idx:
            try:
                result = self.periodic_auction(i, 3)
                bar = 0
                for j in result:
                    bar += float(j[1]) / len(result)
                print(bar, i/len(idx))
                if bar > 0.01:
                    watchlist.append(i)
            except: pass
        print(i)






f = FlowTracker()
# f.danger_spotter()
print(f.periodic_auction('600313', 10, '2016-02-17'))
