from gdax import AuthenticatedClient

class Gdax:
    def __init__(self, config):
        self.temp = 0
        self.client = AuthenticatedClient(config['DEFAULT']['api_key'], config['DEFAULT']['api_secret'], config['DEFAULT']['passphrase'])

    def get_product_order_book(self, product = 'BTC-USD'):
        return self.client.get_product_order_book(product)

    def get_product_ticker(self, product = 'BTC-USD'):
        return self.client.get_product_ticker(product) 

    def get_product_trades(self, product = 'BTC-USD'):
        return self.client.get_product_trades(product) 

    def get_product_historic_rates(self, product = 'BTC-USD', granularity = 0):
        if granularity == 0:
            return self.client.get_product_historic_rates(product)
        else:
            return self.client.get_product_historic_rates(product, granularity = granularity)

    def get_product_24hr_stats(self, product = 'BTC-USD'):
        return self.client.get_product_24hr_stats(product) 
    