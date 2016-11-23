import analyst as al
import messenger as ms


h = al.PriceDeviation()
# list = ms.get_stock_code_by_type('cyb')


h.plot_difference('601668', duration=30)

'''
c = h.__diff_lists__('600313', '2016-11-22')
for i in c:
    print(i)
'''
'''
for i in list:
    try:
        h.plot_difference(i, type='save')
    except:
        pass
'''