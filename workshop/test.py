import sys
import os
cwd = os.path.dirname(os.getcwd())
sys.path.append(cwd)
import analyst as al
import assistant as at
import messenger as ms
import agent as ag
import random

'''
count = 0
while count <= 10:
        try:
                codes_list = ['000043', '002407', '600053', '000002', '600118']
                dates_list = ['2015-07-28', '2011-10-32', '2013-01-03', '2014-02-10', '2010-01-09']
                code = random.sample(codes_list, 1)
                date = random.sample(dates_list, 1)
                codes_list = list(set(codes_list) - set(code))
                dates_list = list(set(dates_list) - set(date))
                print(code, date)
                ag.list_for_price_deviation(code, duration=350, date=date[0])
                count += 1
        except:
                count += 1
'''
'''
list = ['002561', '002074', '603099', '603883', '002405', '000762', '600175', \
        '600295', '000022', '601006', '000039', '601038', '600081', '600006', \
        '601880']
'''
# list = ['600313', '000625', '000022', '002074', '603979', '000043', '600824', \
#        '600558', '603099', '000301', '002107', '000514']

'''
list = [i for i in ms.complete_stock_list() if i[0] != '3']
random.shuffle(list)
date_list = ['2010-10-30', '2012-05-30', '2013-07-28', '2014-06-29']
list = list[:150]
print(list)
i = 0
while i < 150:
    date_i = str(random.sample(date_list, 1)[0])
    print(date_i)
    the_list = [list[i]]
    ag.list_for_price_deviation(the_list, date_i, duration=200)
    i += 1
'''

# list = ['600313', '603979', '000022', '000625', '000514', '002074', '600340', '000615', \
#       '600266', '002146', '000401', '000709', '002616', '600550']

# list = ['600050']
# ag.list_for_price_deviation(list, duration=300)

list = random.sample([i for i in ms.complete_stock_list() if i[0] != '3'], 100)
print(list)
smooth = [10, 30]
h = al.PriceDeviation()
for i in list:
       try:
              h.plot_difference_multi_smoothing(i, smooth, date='2012-10-30', duration=900, period_length=300, type='save')
       except:
              pass

# h = al.PriceDeviation()
# h.plot_difference('000401', date='2012-05-30', duration=300, smooth=20, type='save')
# h = al.PriceDeviation()
# s = h.__measure_diff__('600313', '2017-03-15')
# s = ms.get_stock_hist_data('600313', '2017-03-15')
