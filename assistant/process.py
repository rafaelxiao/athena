import sys, time
import assistant as at

def process_monitor(percent):
    '''
    Show the process with a bar
    :param percent: int, the percent completed
    :return: None
    '''
    percent = int(percent)
    completed = '|'
    uncompleted = ' '
    percent_monitor = '  %d%%' %percent
    bar = completed * percent + uncompleted * (100 - percent) + percent_monitor
    sys.stdout.write('\r')
    sys.stdout.write(bar)
    sys.stdout.flush()
    if percent == 100:
        print('\r')

def pick_out(list, f):
    '''
    Select the extreme value in the list
    :param list: the list
    :param f: the function to set the comparison rule
    :return: the extreme value
    '''
    hold = list[0]
    for i in range(len(list) - 1):
        if f(hold, list[i+1]):
            hold = list[i+1]
    return hold

def sort_list_by_date(list):
    '''
    Sort the list by date
    :param list: the original list
    :return: the sorted list
    '''
    def greater(value1, value2):
            if at.date_encoding(value1[0]) > at.date_encoding(value2[0]):
                return True
    i = len(list)
    while i > 0:
        for j in range(i - 1):
            if greater(list[j], list[j + 1]):
                hold = list[j]
                list[j] = list[j + 1]
                list[j + 1] = hold
        i -= 1
    return list

# Running time
def running_time(func, args):
    '''
    Print the running time of a function
    :param func: the function
    :param args: the input of the function
    :return: None
    '''
    start = time.clock()
    func(args)
    end = time.clock()
    print("Running time: %f s" % (end - start))