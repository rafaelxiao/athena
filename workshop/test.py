import analyst as al
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

list = ['600585', '002304']
ag.list_for_price_deviation(list, duration=200)
