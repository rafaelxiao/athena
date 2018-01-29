import sys
import os
cwd = os.path.dirname(os.getcwd())
sys.path.append(cwd)
import analyst as al
import assistant as at
import messenger as ms
import datetime
import trader as tr
import random
import numpy as np
import tensorflow as tf
from sklearn import svm


code_list = ['000625', '601318', '000022']

h = ms.TickData()
s = h.show_stocks()
for code in code_list:
    h.update(code)

tr.list_for_price_deviation(code_list, duration=300, smooth=3)
