from Logic.math import Sign
from Objects.prices import Prices
from Objects.price import Price

class Algorithm:
    def __init__(self):
        self.downward_trend = False
        self.upward_trend = False
        self.spike_detected = False

    def analyze_last_prices(self, number_of_entries_to_analyze, price_list):
        total_change = 0
        last_entry = price_list[-1]
        for price in price_list[(number_of_entries_to_analyze * -1):number_of_entries_to_analyze - 1]:
            total_change += float(price.amount)
            current_change = float(price.amount) - float(last_entry.amount)
            print('Current: {0} Final: {1}'.format(price.amount, last_entry.amount))
            if Sign(current_change) == -1:
                self.downward_trend = True
                self.upward_trend = False
            elif Sign(current_change) == 1:
                self.upward_trend = True
                self.downward_trend = False
            else:
                self.downward_trend = False
                self.upward_trend = False

    def analyze_potential_spike(self, price_list):
        last_entry = price_list[-1]
        initial_price = float(last_entry.amount)
        last_price = float(price_list[-1].amount)
        price_difference = last_price - initial_price
        if (price_difference / last_price) > .01:
            self.spike_detected = True
