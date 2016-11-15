import math
import messenger as ms

class SmartMoney:
    '''
    Calculate the smart money emotion score
    '''

    def __subset_tick_data__(self, tick_data):
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

    def __range_in_duration__(self, sub_set):
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

    def __volume_in_duration__(self, sub_set):
        '''
        Calculate the volume in a duration(subset)
        :param sub_set: the subsetted list
        :return: the volume
        '''
        volume = 0
        for i in sub_set:
            volume += i[2]
        return volume

    def __smart_level_of_duration__(self, sub_set):
        '''
        Calculate the smart level of the duration(subset)
        :param sub_set: the subsetted list
        :return: the smart level
        '''
        range = self.__range_in_duration__(sub_set)
        volume = self.__volume_in_duration__(sub_set)
        smart_score = range / math.sqrt(volume)
        return smart_score

    def __total_value_in_duration__(self, sub_set):
        '''
        Calculate the total cash value of the duration(subset)
        :param sub_set: the subsetted list
        :return: the total cash value
        '''
        total_value = 0
        for i in sub_set:
            total_value += i[1] * i[2]
        return total_value

    def __transform_set__(self, set):
        '''
        Transform the set in a reorganized form
        :param set: the processed tick data
        :return: the transformed set
        '''
        transformed_set = []
        for i in set:
            time_stamp = i[0][0]
            volume = self.__volume_in_duration__(i)
            total_value = self.__total_value_in_duration__(i)
            smart_level = self.__smart_level_of_duration__(i)
            if math.isnan(smart_level) or math.isinf(smart_level):
                smart_level = 0.0
            transformed_set.append((time_stamp, volume, total_value, smart_level))
        return transformed_set

    def __bubble_sort__(self, transformed_set, attrs):
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

    def __weighted_price__(self, transformed_set):
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

    def __emotion_factor__(self, sorted_set):
        '''
        Calculate the smart money emotion score
        :param tranformed_set: the sorted set
        :return: the emotion score
        '''
        weighted_for_all = self.__weighted_price__(sorted_set)
        weighted_for_smart = self.__weighted_price__(sorted_set[int(len(sorted_set) * 0.8):])
        emotion_factor = weighted_for_smart / weighted_for_all
        return emotion_factor

    def calculate_smart_money_emotion(self, code, date):
        '''
        Calculate the smart money emotion score from stock index and date
        :param code: the stock index
        :param date: string, the desired date
        :return: the emotion score
        '''
        tick_data = ms.get_tick_data(code, date)
        subset = self.__subset_tick_data__(tick_data)
        transformed_set = self.__transform_set__(subset)
        self.__bubble_sort__(transformed_set, 3)
        smart_money_emotion = self.__emotion_factor__(transformed_set)
        return smart_money_emotion

    def high_time(self, code, date):
        '''
        Identify the high time when smart money are active
        :param code: the stock index
        :param date: string, the desired date
        :return: the list when smart money are active
        '''
        tick_data = ms.get_tick_data(code, date)
        subset = self.__subset_tick_data__(tick_data)
        transformed_set = self.__transform_set__(subset)
        self.__bubble_sort__(transformed_set, 3)
        high_time_list = transformed_set[int(len(transformed_set) * 0.8):]
        self.__bubble_sort__(high_time_list, 0)
        return high_time_list