import Engine, Messenger, Agent

e = Engine.SmartMoney()
s = e.calculate_smart_money_emotion('600313', '2016-11-01')
print(s)