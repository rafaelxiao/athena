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

s = Workshop.KDJ()
z = s.rsv('600313')
print(z)