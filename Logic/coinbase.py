from coinbase.wallet.client import Client

class Coinbase():
    def __init__(self, config):
        self.client = Client(config['DEFAULT']['api_key'], config['DEFAULT']['api_secret'])
        self.current_btc_amount = 0
        self.last_price = 0

    def set_current_btc_amount(self, current_btc_amount):
        self.current_btc_amount = current_btc_amount

    def get_current_price(self, currency_code, prices):
        price = self.client.get_spot_price(currency=currency_code)
        if self.last_price != float(price.amount):
            self.last_price = float(price.amount)
            prices.add_new_price(price.amount)
            temp_prices = prices.get_last_prices(len(prices.price_list))
        return price
