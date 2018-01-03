from gdax import AuthenticatedClient
from Objects.gdax import GdaxTicker
from Objects.gdax import GdaxTrades 
from Objects.gdax import GdaxHistoric
from Objects.gdax import BidAskStackType
from Objects.gdax import ChangeType
from Logic.custom_orderbook import CustomOrderBook
import sys
from gdax.order_book import OrderBook
import datetime as dt
import threading
import time
import gdax as gdax_lib
import inspect
from Logic.algorithm import Algorithm

class Gdax:
    def __init__(self, config):
        self.temp = 0
        self.client = AuthenticatedClient(config['DEFAULT']['api_key'], config['DEFAULT']['api_secret'], config['DEFAULT']['passphrase'])
        self.ticker = GdaxTicker()
        self.trades = GdaxTrades()
        self.historics = GdaxHistoric()
        self.current_trend = ChangeType.NO_CHANGE
        self.btc_account = config['DEFAULT']['btc_account']
        self.usd_account = config['DEFAULT']['usd_account']
    
    def get_current_btc_amount(self):
        return float(self.client.get_account(self.btc_account)['available'])

    def get_current_usd_amount(self):
        return float(self.client.get_account(self.usd_account)['available'])

    def get_product_order_book(self, product = 'BTC-USD'):
        return self.client.get_product_order_book(product)

    def get_product_ticker(self, product = 'BTC-USD'):
        return self.client.get_product_ticker(product_id=product) 

    def get_product_trades(self, product = 'BTC-USD'):
        return self.client.get_product_trades(product) 

    def get_product_historic_rates(self, product = 'BTC-USD', granularity = 60):
        return self.client.get_product_historic_rates(product, granularity = granularity)

    def get_product_24hr_stats(self, product = 'BTC-USD'):
        return self.client.get_product_24hr_stats(product)

    def stop_all_polls(self):
        sys.exit()

    def start_ticker_update(self):
        def poll_ticker_update(gdax):
            while(True):
                ticker_info = gdax.get_product_ticker()
                gdax.ticker.add_row_to_ticker(ticker_info)
                time.sleep(.05)
        t = threading.Thread(args=(self,), target=poll_ticker_update)
        t.daemon = True
        t.start()

    def start_trades_update(self):
        def poll_trades_update(gdax):
            while(True):
                trades_info = gdax.get_product_trades()
                gdax.trades.add_rows_to_trades(trades_info)
                time.sleep(.05)
        t = threading.Thread(args=(self,), target=poll_trades_update)
        t.daemon = True
        t.start()

    def start_historics_update(self):
        def poll_historics_update(gdax):
            while(True):
                historic_info = gdax.get_product_historic_rates()
                gdax.historics.add_rows_to_history(historic_info)
                time.sleep(15)
        t = threading.Thread(args=(self,), target=poll_historics_update)
        t.daemon = True
        t.start()

    def print_historics_sorted(self):
        temp = [x.__dict__ for x in self.historics.historics]
        for x in sorted(temp, key=lambda x_key: x_key['time']):
            print(x)

    def print_trades_sorted(self):
        temp = [x.__dict__ for x in self.trades.trades]
        for x in sorted(temp, key=lambda x_key: x_key['time']):
            print(x)

    def print_tickers_sorted(self):
        temp = [x.__dict__ for x in self.ticker.ticker]
        for x in sorted(temp, key=lambda x_key: x_key['time']):
            print(x)

    def sell_bitcoin(self, size = 0, price = 0):
        return self.client.sell(size = str(size), #USD
                product_id = 'BTC-USD',
                type = 'market')

    def buy_bitcoin(self, size = 0, price = 0):
        usd = round(self.get_current_usd_amount() * .99, 2)
        #actual_size = round(usd / price, 4)
        #if actual_size >= .0001:
        return self.client.buy(funds = str(usd), #USD
            product_id = 'BTC-USD',
            type = 'market')

    def get_orders(self):
        return self.client.get_orders()        

    def start_order_book_poll(self):
        def poll_order_book(gdax):
            order_book, algorithm = CustomOrderBook(gdax), Algorithm()
            order_book.start()
            algorithm.gdax_main(order_book, gdax)
            order_book.close()
        t = threading.Thread(args=(self,), target=poll_order_book)
        t.daemon = True
        t.start()       
