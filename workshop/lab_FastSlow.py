import analyst as al

code = '000401'
date = '2012-05-30'
duration = 10
fast_smooth = 10
slow_smooth = 30

h = al.PriceDeviation()

fast = h.show_difference_list(code, date, duration, fast_smooth)
slow = h.show_difference_list(code, date, duration, slow_smooth)

'''
for i in fast:
    fast[i]['fast'] = fast[i]['smoothed_difference']
    fast[i]['slow'] = slow[i]['smoothed_difference']
'''

for i in fast:
    print(fast[i])
    print(slow[i])