from gdax import AuthenticatedClient
from Objects.gdax import GdaxTicker
from Objects.gdax import GdaxTrades 
from Objects.gdax import GdaxHistoric
import sys
import threading
import time

class Gdax:
    def __init__(self, config):
        self.temp = 0
        self.client = AuthenticatedClient(config['DEFAULT']['api_key'], config['DEFAULT']['api_secret'], config['DEFAULT']['passphrase'])
        self.ticker = GdaxTicker()
        self.trades = GdaxTrades()
        self.historics = GdaxHistoric()

    def get_product_order_book(self, product = 'BTC-USD'):
        return self.client.get_product_order_book(product)

    def get_product_ticker(self, product = 'BTC-USD'):
        return self.client.get_product_ticker(product_id=product) 

    def get_product_trades(self, product = 'BTC-USD'):
        return self.client.get_product_trades(product) 

    def get_product_historic_rates(self, product = 'BTC-USD', granularity = 0):
        if granularity == 0:
            return self.client.get_product_historic_rates(product)
        else:
            return self.client.get_product_historic_rates(product, granularity = granularity)

    def get_product_24hr_stats(self, product = 'BTC-USD'):
        return self.client.get_product_24hr_stats(product)

    def stop_all_polls(self):
        sys.exit()

    def start_ticker_update(self):
        t = threading.Thread(target=self.poll_ticker_update)
        t.daemon = True
        t.start()

    def poll_ticker_update(self):
        while(True):
            ticker_info = self.get_product_ticker()
            self.ticker.add_row_to_ticker(ticker_info)
            time.sleep(.5)

    def start_trades_update(self):
        t = threading.Thread(target=self.poll_trades_update)
        t.daemon = True
        t.start()

    def poll_trades_update(self):
        while(True):
            trades_info = self.get_product_trades()
            self.trades.add_rows_to_trades(trades_info)
            time.sleep(.5)
    
    def start_historics_update(self):
        t = threading.Thread(target=self.poll_historics_update)
        t.daemon = True
        t.start()

    def poll_historics_update(self):
        while(True):
            historic_info = self.get_product_historic_rates()
            self.historics.add_rows_to_history(historic_info)
            time.sleep(10000)
    