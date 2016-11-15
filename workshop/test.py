import assistant as at
import analyst as al
import agent as ag
import trader as tr
import analyst as al
import workshop.lab as lab
import time
import threading


start = time.clock()
s = lab.MACDWithKDJ()
z = s.__macd_and_kdj_list__('600313', 20, '2016-11-10')
# z = s.__macd__('600313', 20, '2016-11-10')
for i in z:
    print(i)
end = time.clock()
print("read: %f s"% (end - start))




