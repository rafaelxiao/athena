import sys

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