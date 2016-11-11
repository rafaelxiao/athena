import Engine, Messenger, Agent, Toolbox, Workshop
import sys
import time

'''
x = Agent.periodic_auction_scanner('600313', 5)
for i in x:
    print(i)
'''

s = Engine.StockAccount()

s.deposit_cash(100)
print(s.cash)
print(s.original_cash)

s.buy('600313', 1, 30)

print(s.stock_hold)
print(s.cash)
print(s.balance())

s.buy('600222', 1, 50)

print(s.stock_hold)
print(s.cash)
print(s.balance())