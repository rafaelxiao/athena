import messenger as ms
import numpy as np

class StockPicker:

    def __get_stock_list__(self, classifier, type):
        column = 'c_name'
        if classifier == 'industry':
            f = ms.get_industry_classified
        elif classifier == 'concept':
            f = ms.get_concept_classified
        else:
            return None
        frame = f()
        content = frame[frame['%s'%column] == type].code.tolist()
        return content

    def __get_data_frame__(self, list, func='basics', year=0, quarter=0):
        if func == 'basics':
            frame = ms.get_stock_basics()
        else:
            frame = ms.get_stock_report_frame(year, quarter, func)
        return frame.ix[list]

    def __get_data__(self, classifier, type, func='basics', year=0, quarter=0):
        list = self.__get_stock_list__(classifier, type)
        frame = self.__get_data_frame__(list, func, year, quarter)
        return frame

    def find_outliers(self, classifier, klass, indicator, positive=1, multiple=2, func='basics', year=0, quarter=0):
        frame = self.__get_data__(classifier, klass, func, year, quarter)
        frame = frame[frame[indicator].notnull()]
        frame = frame[frame[indicator] > 0]
        list = frame[indicator].tolist()
        mean = np.mean(list)
        print(mean)
        std = np.std(list)
        print(std)
        if positive == 1:
            bar = mean + multiple * std
            content = frame[frame[indicator] > bar]
        if positive == 0:
            bar = mean - multiple * std
            content = frame[frame[indicator] < bar]
        content.to_excel('%s.xlsx'%klass)

'''
mark = '环保行业'
picker = StockPicker()
data = picker.get_data('industry', mark)
data = data[data.pe.notnull()]
data = data[data.pe > 0]
bar = data.pe.quantile(0.25)
data = data[data.pe < bar]
data.to_excel('%s.xlsx'%mark)
print(data)
'''

picker = StockPicker()
picker.find_outliers('industry', '商业百货', 'pe', 1)