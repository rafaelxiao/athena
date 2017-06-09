import sys
import os
cwd = os.path.dirname(os.getcwd())
sys.path.append(cwd)
import analyst as al
import assistant as at
import messenger as ms
import trader as tr
import random
import numpy as np
import tensorflow as tf
from sklearn import svm

gap_list = [7]
code_list = ['000625', '600313', '002074']

h = al.PriceDeviation()
output = []
for code in code_list:
    for gap in gap_list:
        try:
            origin_data = h.show_difference_list(code, date='2015-06-04', duration=350, smooth=gap)
            y = [(origin_data[i]['close'] - origin_data[i - (gap - 1)]['open']) / origin_data[i - (gap - 1)]['open'] for i in range(len(origin_data[gap:]))]
            x = [[i['smoothed theoretical'], i['smoothed difference']] for i in origin_data[:-gap]]
            x_train, x_test, y_train, y_test = x[:60], x[60:], y[:60], y[60:]
            clf = svm.SVR(kernel='linear')
            clf.fit(x_train, y_train)
            accuracy = clf.score(x_test, y_test)
            output.append([code, gap, accuracy])
        except:
            pass
for i in output:
    print(i)