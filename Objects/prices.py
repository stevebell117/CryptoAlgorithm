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
        first_price = price_collection[0].amount
        last_price = price_collection[-1].amount
        return last_price - first_price

    def add_new_price(self, price_amount):
        new_price = Price()
        new_price.amount = price_amount
        self.price_list.append(new_price)
