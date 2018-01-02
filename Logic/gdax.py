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

class Gdax:
    def __init__(self, config):
        self.temp = 0
        self.client = AuthenticatedClient(config['DEFAULT']['api_key'], config['DEFAULT']['api_secret'], config['DEFAULT']['passphrase'])
        self.ticker = GdaxTicker()
        self.trades = GdaxTrades()
        self.historics = GdaxHistoric()
        self.trend = ChangeType.NO_CHANGE
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
                time.sleep(.5)
        t = threading.Thread(args=(self,), target=poll_ticker_update)
        t.daemon = True
        t.start()

    def start_trades_update(self):
        def poll_trades_update(gdax):
            while(True):
                trades_info = gdax.get_product_trades()
                gdax.trades.add_rows_to_trades(trades_info)
                time.sleep(.5)
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

    def get_orders(self, gdax_client):
        return gdax_client.get_orders()        

    def start_order_book_poll(self):
        def poll_order_book(gdax):
            threshold = 0.0075
            order_book = CustomOrderBook(self)
            order_book.start()
            previous_type, previous_amount = BidAskStackType.NEITHER, 0
            while(True):
                current_type = order_book.OrderBookCollection.determine_if_sell_or_buy_bids_are_stacked()     
                current_amount = float(order_book.OrderBookCollection.last_amount)
                if current_type != BidAskStackType.NEITHER and previous_type != current_type:
                    if previous_amount == 0:
                        previous_amount = current_amount
                        print('Starting amount {0} @ {1}'.format(current_amount, dt.datetime.now()))
                        pass
                    if previous_amount == current_amount:
                        pass
                    time.sleep(6) #Make sure it wasn't a random push that got balanced out within n seconds to ruin the trend
                    current_type = order_book.OrderBookCollection.determine_if_sell_or_buy_bids_are_stacked()  
                    if current_type == BidAskStackType.STACKED_ASK:
                        if 1 - (previous_amount / current_amount) > threshold:
                            #Consider sell
                            print('{2} SELL - Current: {0} | Previous: {1} | Division: {3}'.format(current_amount, previous_amount, dt.datetime.now(), 1 - (previous_amount / current_amount)))
                            if self.get_current_btc_amount() >= .0001:
                                response = self.sell_bitcoin('.0001', current_amount)
                                try:
                                    print('Size: {0:.4f}'.format(response['size']))
                                except:
                                    print(response)
                            previous_amount = current_amount
                    elif current_type == BidAskStackType.STACKED_BID:
                        if 1 - (current_amount / previous_amount) > threshold:
                            #Consider buy
                            print('{2} BUY - Current: {0} | Previous: {1} | Division: {3}'.format(current_amount, previous_amount, dt.datetime.now(), 1 - (current_amount / previous_amount)))
                            if self.get_current_usd_amount() >= .0001 * current_amount:
                                response = self.buy_bitcoin('.0001', current_amount)
                                try:
                                    print('Existing USD: {0:.6f} | Specified Buy: {1:.2f}'.format(response['funds'], response['specified_funds']))
                                except:
                                    print(response)
                            previous_amount = current_amount                        
                time.sleep(1)
            order_book.close()
        t = threading.Thread(args=(self,), target=poll_order_book)
        t.daemon = True
        t.start()       
