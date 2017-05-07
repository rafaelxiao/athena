import messenger as ms
import analyst as al
import assistant as at
import os, threading, queue

# Error Message
error_message = "Data corrupted"

def periodic_auction_scanner(code, days, start_date='', progress_bar=1):
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
            if progress_bar == 1:
                at.process_monitor(count / len(days_list) * 100)
            count += 1
        return content_list
    except:
        print(error_message)

def list_for_price_deviation(list, date='', duration=90, smooth=3):
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
            h.plot_difference(i, date, duration, type='save', smooth=smooth)



def peak_scanner(date='', peak_scanner_duration=10, peak_signal_bar=0.1, peak_scanner_threads=20, peak_scanner_stepper=10):
    '''
    Scan the stock with peak signal
    :param date: str, date
    :param peak_scanner_duration: int, the duration with each scan
    :param peak_signal_bar: float, the threshold of signal ratio
    :param peak_scanner_threads: int, the threads used
    :param peak_scanner_stepper: int, the multiplier to set the quantity of each step
    :return: A stock list
    '''
    try:
        list = ms.complete_stock_list()
        def catch(i, f, q, p):
            result = f(i, peak_scanner_duration, date)
            q.put((i, result))
            p.put((i, result))
        def save(output, list_length, mark='final'):
            path = os.path.join(os.getcwd(), 'peak_signal_%s.txt'%mark)
            with open(path, 'w') as r:
                r.write(str(len(output)) + '/' + str(list_length) + ', ' + str(round(float(len(output) / list_length) * 100, 2)) + '%' )
                r.write('\n' * 2)
                for ko in output:
                    r.write(ko[0]+'\n')
                r.write('\n' * 2)
                for k in output:
                    r.write(k[0]+'\n')
                    r.writelines([str(i[0]) + ',' + str(i[1]) + '\n' for i in k[1]])
                    r.write('\n')
        scanned = []
        output = []
        step_scanned = []
        step_output = []
        step_mark = 0
        q = queue.Queue()
        p = queue.Queue()
        step_iter = 0
        for i in range(0, len(list), peak_scanner_threads):
            t = []
            if i + peak_scanner_threads < len(list):
                for io in list[i : i + peak_scanner_threads]:
                    t.append(threading.Thread(target=catch, args=(io, periodic_auction_scanner, q, p)))
                    step_iter += 1
                for iu in t:
                    iu.start()
                for iz in t:
                    iz.join()
            else:
                for ii in list[i:]:
                    t.append(threading.Thread(target=catch, args=(ii, periodic_auction_scanner, q, p)))
                    step_iter += 1
                for iu in t:
                    iu.start()
                for iz in t:
                    iz.join()
            if step_iter >= peak_scanner_stepper * peak_scanner_threads:
                step_mark += 1
                while not p.empty():
                    step_scanned.append(p.get())
                for iy in step_scanned:
                    for jy in iy[1]:
                        if float(jy[-1]) >= float(peak_signal_bar):
                            step_output.append(iy)
                            break
                save(step_output, step_iter, str(step_mark))
                step_iter = 0
                step_scanned = []
                step_output = []
                p = queue.Queue()
        while not q.empty():
            scanned.append(q.get())
        for i in scanned:
            for j in i[1]:
                if float(j[-1]) >= float(peak_signal_bar):
                    output.append(i)
                    break
        save(output, len(list))
    except: pass

