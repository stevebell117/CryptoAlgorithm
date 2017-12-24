from Objects.price import Price

class Prices():    
    def __init__(self):
        self.price_list = []

    def get_prices_count(self):
        return len(self.price_list)

    def get_last_prices(self, number_of_prices):
        actual_prices_returned = number_of_prices
        if len(self.price_list) < number_of_prices:
            actual_prices_returned = len(self.price_list)
        return self.price_list[(actual_prices_returned * -1):]

    def get_price_list(self):
        return self.price_list

    def get_price_difference_from_collection(self, price_collection):
        first_price = float(price_collection[0].amount)
        last_price = float(price_collection[-1].amount)
        return last_price - first_price

    def add_new_price(self, price_amount):
        new_price = Price()
        new_price.amount = price_amount
        self.price_list.append(new_price)

    def average_time_between_prices(self):
        total_time_in_seconds = 0
        total_times = 0
        last_minute = self.price_list[0].date_and_time.minute
        for price in self.price_list:
            if total_times != 0:
                total_time_in_seconds += float(price.date_and_time.second)
            if(price.date_and_time.minute > last_minute):
                total_time_in_seconds += ((float(price.date_and_time.minute) - float(last_minute)) * 60) - price.date_and_time.second
                last_minute = price.date_and_time.minute
            total_times += 1
        
        return total_time_in_seconds / total_times
            
