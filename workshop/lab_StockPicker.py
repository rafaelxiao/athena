import messenger as ms
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

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

    def find_top(self, classifier, klass, indicator, top=0.1, largest=True, func='basics', year=0, quarter=0, positive=True, save_excel=False):
        frame = self.__get_data__(classifier, klass, func, year, quarter)
        frame = frame[frame[indicator].notnull()]
        if positive == True:
            frame = frame[frame[indicator] > 0]
        if largest == True:
            bar = frame[indicator].quantile(1 - top)
            content = frame[frame[indicator] >= bar].sort_values(by = indicator, ascending=False)
        elif largest == False:
            bar = frame[indicator].quantile(top)
            content = frame[frame[indicator] <= bar].sort_values(by = indicator, ascending=True)
        else:
            return None
        if save_excel == True:
            if func == 'basics':
                content.to_excel('%s-%s.xlsx'%(klass, indicator))
            else:
                content.to_excel('%s-%s-%s-%s.xlsx'%(klass, indicator, year, quarter))
        else:
            return content

h = StockPicker()
h.find_top('industry', '玻璃行业', 'pe', largest=False, save_excel=True, top=1)