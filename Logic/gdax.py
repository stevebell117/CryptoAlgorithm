from gdax_lib import AuthenticatedClient
from Objects.gdax import GdaxTicker
from Objects.gdax import GdaxTrades 
from Objects.gdax import GdaxHistoric
from Objects.gdax import BidAskStackType
from Objects.gdax import ChangeType
from Objects.orders import Order
from Logic.custom_orderbook import CustomOrderBook
from Logic.custom_orderbook import CustomOrderBookRun
import sys
import json
from gdax_lib.order_book import OrderBook
import datetime as dt
import threading
import time
import gdax as gdax_lib
import inspect
import traceback
from Logic.algorithm import Algorithm
from Objects.orders import OrderStatus
import uuid

class Gdax:
    def __init__(self, config):
        self.temp = 0
        self.client = AuthenticatedClient(config['DEFAULT']['api_key'], config['DEFAULT']['api_secret'], config['DEFAULT']['passphrase'])
        self.ticker = GdaxTicker()
        self.trades = GdaxTrades()
        self.historics = GdaxHistoric()
        self.algorithm = None
        self.current_trend = ChangeType.NO_CHANGE
        self.btc_account = config['DEFAULT']['btc_account']
        self.usd_account = config['DEFAULT']['usd_account']
    
    def get_current_btc_amount(self):
        return float(self.client.get_account(self.btc_account)['available'])

    def get_current_btc_cost(self, current_cost):
        potential_price = self.client.get_product_ticker(product_id='BTC-USD')
        if 'price' in potential_price:
            return float((potential_price['price']))
        else:
            return current_cost

    #This method is ridiculously complex.
    def get_previous_amount(self, orders):
        if orders and (orders[-1].status == OrderStatus.OPEN or orders[-1].status == OrderStatus.OVERRIDE or orders[-1].status == OrderStatus.REJECTED):
            return orders[-1].price
        else:
            orders = self.get_account_history()
            order_id = orders[0][0]['details']['order_id']
            order = self.get_fills(order_id)
            return float(order[0][0]['price'])

    def get_current_usd_amount(self):
        return float(self.client.get_account(self.usd_account)['available'])

    def get_account_history(self, account_id=None):
        if account_id is None:
            return self.client.get_account_history(self.btc_account)
        else:
            return self.client.get_account_history(account_id)

    def get_fills(self, order_id=None):
        if order_id is None:
            return self.client.get_fills()
        else:
            return self.client.get_fills(order_id=order_id)
    
    def get_product_order_book(self, product = 'BTC-USD'):
        return self.client.get_product_order_book(product)

    def get_product_ticker(self, product = 'BTC-USD'):
        return self.client.get_product_ticker(product_id=product) 

    def get_product_trades(self, product = 'BTC-USD'):
        return self.client.get_product_trades(product) 

    def get_product_historic_rates(self, product = 'BTC-USD', granularity = 60, start = None, end = None):
        if start is not None and end is not None:
            return self.client.get_product_historic_rates(product, granularity=granularity, start=start, end=end)
        elif start is not None:
            return self.client.get_product_historic_rates(product, granularity=granularity, start=start)
        elif end is not None:
            return self.client.get_product_historic_rates(product, granularity=granularity, end=end)
        else:
            return self.client.get_product_historic_rates(product, granularity=granularity)

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
        t.name = 'poll_ticker_update'
        t.start()
        return t

    def start_trading(self, order_book, algorithm):
        def poll_trading(order_book, algorithm, gdax):
            while(True):
                algorithm.gdax_main(order_book, gdax)
                time.sleep(.2)
        t = threading.Thread(args=(order_book,algorithm,self,), target=poll_trading)
        t.daemon = True
        t.name = 'poll_trading (gdax_main)'
        t.start()
        return t

    def start_trades_update(self):
        def poll_trades_update(gdax):
            while(True):
                trades_info = gdax.get_product_trades()
                gdax.trades.add_rows_to_trades(trades_info)
                time.sleep(.05)
        t = threading.Thread(args=(self,), target=poll_trades_update)
        t.daemon = True
        t.name = 'poll_trades_update'
        t.start()
        return t

    def start_historics_update(self):
        def poll_historics_update(gdax):
            first_run = True
            while(True):
                if first_run is True:
                    historic_info = gdax.get_product_historic_rates()
                    #first_run = False
                else:
                    #TODO: This is borked, figure it out later
                    print((dt.datetime.now() - dt.timedelta(minutes=5)).isoformat())
                    historic_info = gdax.get_product_historic_rates(start=(dt.datetime.now() - dt.timedelta(minutes=5)).isoformat(), end=dt.datetime.now().isoformat())
                gdax.historics.add_rows_to_history(historic_info)
                #gdax.print_historics_sorted()
                time.sleep(45)
        t = threading.Thread(args=(self,), target=poll_historics_update)
        t.daemon = True
        t.name = 'poll_historics_update'
        t.start()
        return t

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

    def sell_bitcoin_limit(self, size = 0, price = 0):
        return self.client.sell(size = str(size),
                price = str(price), #USD
                product_id = 'BTC-USD',
                time_in_force = 'GTT',
                cancel_after = 'min',
                post_only = True)

    def sell_bitcoin_market(self, size = 0):
        return self.client.sell(size = str(size),
                product_id = 'BTC-USD',
                type = 'market')

    def buy_bitcoin_limit(self, size = 0, price = 0):
        usd = round(self.get_current_usd_amount(), 2)

        #actual_size = round(usd / price, 4)
        #if actual_size >= .0001:
        return self.client.buy(size = str(size),
            price = str(price), #USD
            product_id = 'BTC-USD',
            time_in_force = 'GTT',
            cancel_after = 'min',
            post_only = True)

    def buy_bitcoin_market(self, price = 0):
        usd = round(self.get_current_usd_amount(), 2)
        actual_size = round(usd / price, 4)
        if actual_size >= .0001:
            fund = price * .0001
            return self.client.buy(funds = str(round(fund, 2)), #USD
                product_id = 'BTC-USD',
                type = 'market')

    def get_orders(self):
        return self.client.get_orders()

    def update_algorithm_previous_amount(self, amount):
        self.algorithm.previous_amount = amount        

    def assign_algorithm_order_book(self, order_book):
        self.algorithm.set_order_book(order_book)

    def override_order(self, value, side):
        order = Order('fake', side, self.algorithm.BUY_SELL_AMOUNT, value, value, OrderStatus.OVERRIDE)
        self.algorithm.order_book.Orders.add_order(order)

    # This is the main polling entry
    def start_order_book_poll(self):
        def poll_order_book(gdax):
            order_book, self.algorithm = CustomOrderBookRun(gdax), Algorithm()
            threads = list()
            order_book.start()
            self.algorithm.order_book = order_book
            threads.append(threading.current_thread())
            threads.append(self.start_trading(order_book, self.algorithm))
            threads.append(self.start_order_poll(order_book))
            threads.append(order_book.thread)
            #threads.append(self.start_historics_update())
            self.algorithm.poll_print(order_book, gdax, threads)
            current_cost = 0
            while True:
                try:
                    current_cost = gdax.get_current_btc_cost(current_cost)
                    if current_cost != 0:
                        self.algorithm.process_order_book(order_book, current_cost)
                        order_book.get_nearest_wall_distances(current_cost, order_book.order_book_btc.get_current_book())
                    time.sleep(.3)
                except KeyboardInterrupt:
                    order_book.close()
                except ValueError:
                    pass   
                except Exception as e:
                    order_book.Logs.error(e, 'poll_order_book')  
               
        t = threading.Thread(args=(self,), target=poll_order_book)
        t.daemon = True
        t.name = 'poll_order_book'
        t.start()
        return t

    def start_order_poll(self, order_book):
        def poll_orders(order_book, gdax):
            while True:
                try:
                    for order in order_book.Orders.OrdersList:
                        if order.order_id == 'fake':
                            continue
                        order_status = gdax.client.get_order(order.order_id)
                        if 'message' in order_status or order_status['status'] == 'cancelled' or order_status['status'] == 'rejected':
                            order_book.Orders.update_order(order.order_id, status = OrderStatus.CANCELLED)
                        elif order_status['status'] == 'done':
                            order_book.Orders.update_order(order.order_id, done_reason = order_status['done_reason'], status = OrderStatus.CLOSED, fill_fees = float(order_status['fill_fees']))
                        elif order_status['status'] == 'open':
                            continue
                        else:
                            if order_status not in order_book.Logs.get_logs():
                                order_book.Logs.info(order_status, 'poll_orders')
                    time.sleep(10) 
                except Exception as e:
                    order_book.Logs.error(e, 'poll_orders')
                    #print('EXCEPTION IN POLL ORDERS: {0}'.format(traceback.format_exc())) 
        t = threading.Thread(args=(order_book, self,), target=poll_orders)
        t.daemon = True
        t.name = 'poll_orders'
        t.start()
        return t 
