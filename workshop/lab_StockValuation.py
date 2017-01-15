import tushare as ts
import assistant as at
import analyst as al
import messenger as ms

class StockValue:

    def __init__(self):
        return None

s = ms.get_stock_report('600313', 2016, 2, 'debt')
print(s)