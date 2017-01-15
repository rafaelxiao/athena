import analyst as al
import assistant as at
import messenger as ms
import agent as ag
import random

def post_buy_stop_scanner(list, date='', duration=90, bar=2.5, cut = 2/3):
    h = al.PriceDeviation()
    output_list = []
    filtered_output_list = []
    content = {}
    for code in list:
        try:
            list = h.show_difference_list(code, date=date, duration=duration)
            signal = 0
            min = 0
            max = 0
            final = {'code': code, 'signal':[], 'min':[], 'max':[]}
            for i in list:
                if signal == 0:
                    if i[4] > 0 and i[3] < 0 and abs(i[4]) / abs(i[3]) >= bar:
                        signal = 1
                        final['signal'] = i
                if signal == 1:
                    if min == 0:
                        max = i[2]
                        min = i[2]
                        final['min'] = i
                        final['max'] = i
                    else:
                        if i[2] <= min:
                            min = i[2]
                            final['min'] = i
                        if i[2] >= max:
                            max = i[2]
                            final['max'] = i
            if final['signal'] != []:
                output_list.append(final)
        except: pass

    for io in output_list:
        if at.date_encoding(io['min'][0]) < at.date_encoding(io['max'][0]):
            if at.date_encoding(io['signal'][0]) < at.date_encoding(io['min'][0]):
                if io['min'][2] < io['signal'][2] * cut:
                    filtered_output_list.append(io)

    content['rate'] = len(filtered_output_list) / len(output_list)
    content['signal'] = output_list
    content['success'] = filtered_output_list
    return content

list = ms.complete_stock_list()
list = [i for i in list if i[0] != '3']
list = random.sample(list, 50)
print(list)
scanned = post_buy_stop_scanner(list, bar=2, duration=90)

with open('saved.txt', 'w') as f:
    f.write(str(scanned['rate']))
    f.write('\n' * 2)
    f.write('signal')
    f.write('\n' * 2)
    for iu in scanned['signal']:
        for name in iu:
            f.write(str(name))
            f.write(': ')
            f.write(str(iu[name]))
            f.write('\n')
        f.write('\n')
    f.write('success')
    f.write('\n' * 2)
    for iu in scanned['success']:
        for name in iu:
            f.write(str(name))
            f.write(': ')
            f.write(str(iu[name]))
            f.write('\n')
        f.write('\n')


