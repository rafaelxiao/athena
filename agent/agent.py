import messenger as ms
import analyst as al
import assistant as at
import os, threading, queue

# Error Message
error_message = "Data corrupted"
# Peak signal bar
peak_signal_bar = 0.1
# Peak scanner duration
peak_scanner_duration = 10
# Peak scanner threads
peak_scanner_threads = 20

def periodic_auction_scanner(code, days, start_date=''):
    '''
    Scanner the periodic auction volume for multiple days
    :param code: the stock index
    :param days: the duration
    :param start_date: specifying the start date if needed
    :return: a list of (date, ratio) pairs
    '''
    try:
        outstanding = ms.get_stock_outstanding(code)
        content_list = []
        days_list = at.opening_days(code, days, start_date)
        count = 1
        for i in days_list:
            volume = al.periodic_auction_volume(code, i)
            ratio = float(volume / outstanding)
            ratio = round(ratio * 100, 5)
            pair = (i, ratio)
            content_list.append(pair)
            at.process_monitor(count / len(days_list) * 100)
            count += 1
        return content_list
    except:
        print(error_message)

def list_for_price_deviation(list, date='', duration=90):
    '''
    For a collection of intrested stocks, plot the price deviation graph and save figures
    :param list: a list of stock code
    :param date: str, date
    :param duration: int, duration
    :return: None
    '''
    h = al.PriceDeviation()
    valid_code = ms.get_stock_basics().index.values.tolist()
    for i in list:
        if i in valid_code:
            h.plot_difference(i, date, duration, type='save')

def peak_scanner():
    '''
    Scan and list the stock with peak signal
    :return: A list of stock
    '''
    try:
        list = ms.complete_stock_list()
        def catch(i, f, q):
            result = f(i, peak_scanner_duration)
            q.put((i, result))
        scanned = []
        output = []
        t = []
        q = queue.Queue()
        for i in range(0, len(list), peak_scanner_duration):
            if i + peak_scanner_duration < len(list):
                for io in list[i : i +peak_scanner_duration]:
                    t.append(threading.Thread(target=catch, args=(io, periodic_auction_scanner, q)))
            else:
                for ii in list[i:]:
                    t.append(threading.Thread(target=catch, args=(ii, periodic_auction_scanner, q)))
        for iu in t:
            iu.start()
        for iz in t:
            iz.join()
        while not q.empty():
            scanned.append(q.get())
        for i in scanned:
            for j in i[1]:
                if float(j[-1]) >= float(peak_signal_bar):
                    output.append(i)
                    break
        path = os.path.join(os.getcwd(), 'peak_signal.txt')
        with open(path, 'w') as r:
            r.write(str(len(output)) + '/' + str(len(list)) + ', ' + str(round(float(len(output) / len(list)) * 100, 2)) + '%' )
            r.write('\n' * 2)
            for ko in output:
                r.write(ko[0]+'\n')
            r.write('\n' * 2)
            for k in output:
                r.write(k[0]+'\n')
                r.writelines([str(i[0]) + ',' + str(i[1]) + '\n' for i in k[1]])
                r.write('\n')
    except: pass

