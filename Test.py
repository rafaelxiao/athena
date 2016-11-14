import Engine, Messenger, Agent, Toolbox, Workshop
import sys
import time, datetime

'''
x = Agent.periodic_auction_scanner('600313', 5)
for i in x:
    print(i)
'''
'''
s = Engine.StockAccount()
s.open_an_new_account(1000000)
s.buy('600313', 6, 1000)
s.buy('600222', 8, 2000)

print(s.stock_hold)
print(s.balance())
print(s.current_value_of_account())
'''

s = Engine.MACD()
z = s.macd_of_a_period('600313', 30)
# z = s.kdj('600313', smooth=30)
# z = s.rsv('600313', '2016-11-10')
for i in z:
    print(i)