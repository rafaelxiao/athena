import sys
import os
cwd = os.path.dirname(os.getcwd())
sys.path.append(cwd)
import analyst as al
import assistant as at
import messenger as ms
import agent as ag
import trader as tr
import random

code_list = ms.complete_stock_list()
random.shuffle(code_list)
print(code_list)
date_list = ['2016-04-30', '2014-05-06', '2010-02-03', '2013-11-11', '2015-01-03']

tr.diff_line_strategy(code_list, date_list, 300, 7)
