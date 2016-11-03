import math
import Messenger

def turnover(volume, code):
    '''
    Calculate the volume to outstanding ratio
    :param volume: int, the volume of transaction
    :param code: string, the stock index
    :return: float, the volume to outstanding ratio
    '''
    outstanding = Messenger.get_stock_outstanding(code)
    ratio = float(volume / outstanding)
    return ratio

def periodic_auction_volume(code, date):
    '''
    Get the volume during the periodic auction period
    :param code: string, stock index
    :param date: string, date in format '2016-10-11'
    :return: int, the volume
    '''
    tick_data = Messenger.get_tick_data(code, date)
    volume = tick_data[-1:].volume.values[0]
    if math.isnan(volume):
        volume = 0
    volume = 100 * volume
    volume = int(volume)
    return volume

class SmartMoney:
    '''
    Calculate the smart money emotion score
    '''

    def subset_tick_data(self, tick_data):
        '''
        Subsetting the tick data by each minute with transaction.
        :param tick_data: tick data in pandas frame format
        :return: a list groupby minutes, in (time_stamp, price, shares)
        '''
        sets = []
        time_sets = []
        for num in range(0, len(tick_data)-1):
            i = tick_data[num:num+1]
            hour = i.time.values[0][:2]
            minute = i.time.values[0][3:5]
            time_stamp = (hour, minute)
            if len(time_sets) == 0:
                time_sets.append([time_stamp, i.price.values[0], i.volume.values[0] * 100])
            else:
                if time_stamp == time_sets[-1][0]:
                    time_sets.append([time_stamp, i.price.values[0], i.volume.values[0] * 100])
                else:
                    sets.append(time_sets)
                    time_sets = []
                    time_sets.append([time_stamp, i.price.values[0], i.volume.values[0] * 100])
        return sets

    def range_in_duration(self, sub_set):
        '''
        Calculate the price range in a duration(subset)
        :param sub_set: the subsetted list
        :return: the price range
        '''
        min = 0
        max = 0
        for i in sub_set:
            if min == 0 and max == 0:
                min = i[1]
                max = i[1]
            elif i[1] < min:
                min = i[1]
            elif i[1] > max:
                max = i[1]
            else: pass
        range = abs(max - min)
        return range

    def volume_in_duration(self, sub_set):
        '''
        Calculate the volume in a duration(subset)
        :param sub_set: the subsetted list
        :return: the volume
        '''
        volume = 0
        for i in sub_set:
            volume += i[2]
        return volume

    def smart_level_of_duration(self, sub_set):
        '''
        Calculate the smart level of the duration(subset)
        :param sub_set: the subsetted list
        :return: the smart level
        '''
        range = self.range_in_duration(sub_set)
        volume = self.volume_in_duration(sub_set)
        smart_score = range / math.sqrt(volume)
        return smart_score

    def total_value_in_duration(self, sub_set):
        '''
        Calculate the total cash value of the duration(subset)
        :param sub_set: the subsetted list
        :return: the total cash value
        '''
        total_value = 0
        for i in sub_set:
            total_value += i[1] * i[2]
        return total_value

    def transform_set(self, set):
        '''
        Transform the set in a reorganized form
        :param set: the processed tick data
        :return: the transformed set
        '''
        transformed_set = []
        for i in set:
            time_stamp = i[0][0]
            volume = self.volume_in_duration(i)
            total_value = self.total_value_in_duration(i)
            smart_level = self.smart_level_of_duration(i)
            if math.isnan(smart_level) or math.isinf(smart_level):
                smart_level = 0.0
            transformed_set.append((time_stamp, volume, total_value, smart_level))
        return transformed_set

    def bubble_sort(self, transformed_set, attrs):
        '''
        Sort based on specific attribute
        :param transformed_set: the transformed set
        :return: the re-ordered set
        '''
        length = len(transformed_set)
        while length > 0:
            for i in range(length-1):
                if transformed_set[i][attrs] > transformed_set[i+1][attrs]:
                    hold = transformed_set[i+1]
                    transformed_set[i+1] = transformed_set[i]
                    transformed_set[i] = hold
            length -= 1

    def weighted_price(self, transformed_set):
        '''
        Calculate the weighted price in a set
        :param transformed_set: the transformed set
        :return: the weighted price
        '''
        volume = 0
        total_value = 0
        for i in transformed_set:
            volume += i[1]
            total_value += i[2]
        weight_price = total_value / volume
        return weight_price

    def emotion_factor(self, sorted_set):
        '''
        Calculate the smart money emotion score
        :param tranformed_set: the sorted set
        :return: the emotion score
        '''
        weighted_for_all = self.weighted_price(sorted_set)
        weighted_for_smart = self.weighted_price(sorted_set[int(len(sorted_set) * 0.8):])
        emotion_factor = weighted_for_smart / weighted_for_all
        return emotion_factor

    def calculate_smart_money_emotion(self, code, date):
        '''
        Calculate the smart money emotion score from stock index and date
        :param code: the stock index
        :param date: string, the desired date
        :return: the emotion score
        '''
        tick_data = Messenger.get_tick_data(code, date)
        subset = self.subset_tick_data(tick_data)
        transformed_set = self.transform_set(subset)
        self.bubble_sort(transformed_set, 3)
        smart_money_emotion = self.emotion_factor(transformed_set)
        return smart_money_emotion

    def high_time(self, code, date):
        '''
        Identify the high time when smart money are active
        :param code: the stock index
        :param date: string, the desired date
        :return: the list when smart money are active
        '''
        tick_data = Messenger.get_tick_data(code, date)
        subset = self.subset_tick_data(tick_data)
        transformed_set = self.transform_set(subset)
        self.bubble_sort(transformed_set, 3)
        high_time_list = transformed_set[int(len(transformed_set) * 0.8):]
        self.bubble_sort(high_time_list, 0)
        return high_time_list