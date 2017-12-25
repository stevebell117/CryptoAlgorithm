from Logic.math import Sign
from Objects.prices import Prices
from Objects.price import Price

class Algorithm:
    def __init__(self):
        self.downward_trend = False
        self.upward_trend = False
        self.spike_detected = False

    def analyze_last_prices(self, number_of_entries_to_analyze, price_list):
        self.determine_trend(price_list[(number_of_entries_to_analyze * -1):])

    def determine_trend(self, prices):
        increasing, decreasing = 0, 0
        self.upward_trend, self.downward_trend = False, False
        index = -1
        last_price = prices[0]
        for price in prices:
            print('{0} : {1}'.format(last_price.amount, price.amount))
            if float(last_price.amount) < float(price.amount):
                increasing += 1
                decreasing -= 1
            elif float(last_price.amount) > float(price.amount):
                decreasing += 1
                increasing -= 1    
            index += 1    
            last_price = prices[index]
        if increasing > decreasing:
            self.upward_trend = True
        elif increasing < decreasing:
            self.downward_trend = True            

    def analyze_potential_spike(self, price_list):
        initial_price, last_price = float(price_list[0].amount), float(price_list[-1].amount)
        price_difference = last_price - initial_price
        if (price_difference / last_price) > .01:
            self.spike_detected = True
