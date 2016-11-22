import analyst as al
import messenger as ms


h = al.PriceDeviation()
# list = ms.get_stock_code_by_type('cyb')


h.plot_difference('600571', duration=120)

'''
for i in list:
    try:
        h.plot_difference(i, type='save')
    except:
        pass
'''