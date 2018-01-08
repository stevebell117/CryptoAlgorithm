from Objects.gdax import BidAskStackType
from Objects.gdax import ChangeType
from Objects.orders import Orders
from Objects.orders import Order
from Objects.orders import OrderStatus
from itertools import groupby
from operator import itemgetter
import datetime as dt
import time
from decimal import Decimal
import traceback
import json
import threading

class Algorithm:
    def __init__(self):
        self.previous_type = BidAskStackType.NEITHER
        self.previous_amount = 0
        self.sum_order_book = False
        self.current_type = BidAskStackType.NEITHER

    def process_order_book(self, order_book):
        def determine_sum_order_book(order_book, current_type):
            def get_sorted_asks(current_book):
                first = itemgetter(0)
                return [(k, sum(item[1] for item in tups_to_sum)) for k, tups_to_sum in groupby(sorted(current_book['asks'], key=first), key=first)]
                
            def get_sorted_bids(current_book):
                first = itemgetter(0)
                return [(k, sum(item[1] for item in tups_to_sum)) for k, tups_to_sum in groupby(sorted(current_book['bids'], key=first), key=first)] 
            current_book = order_book.get_current_book()
            asks = get_sorted_asks(current_book)
            bids = get_sorted_bids(current_book)
            ask_sizes = ([x[1] for x in asks])
            bid_sizes = ([x[1] for x in bids])
            bid_sum = sum(bid_sizes[-15:])
            ask_sum = sum(ask_sizes[:15])
            if current_type == BidAskStackType.STACKED_ASK:
                return ask_sum >= bid_sum * Decimal(1.5)
            elif current_type == BidAskStackType.STACKED_BID:
                return bid_sum >= ask_sum * Decimal(1.5)
            return False
        try:
            self.sum_order_book = determine_sum_order_book(order_book, self.current_type)
        except:
            print(traceback.format_exc())
    
    def gdax_main(self, order_book, gdax):
        try:
            threshold = 0.01
            #self.current_type = order_book.OrderBookCollection.determine_if_sell_or_buy_bids_are_stacked()         
            current_amount = float(order_book.OrderBookCollection.last_amount)
            if self.previous_amount == 0:
                self.previous_amount = current_amount
                if current_amount != 0: print('Starting amount {0} @ {1}'.format(current_amount, dt.datetime.now()))
                return
            wall_var = order_book.determine_if_wall_is_coming()
            if wall_var['side'] == 'sell' or wall_var['side'] == 'buy':
                if wall_var['side'] == 'sell':
                    self.sell_bitcoin_logic_limit(float(wall_var['amount']), threshold, gdax, order_book)
                else:
                    self.buy_bitcoin_logic_limit(float(wall_var['amount']), threshold, gdax, order_book) 
            elif (self.current_type != BidAskStackType.NEITHER and self.previous_type != self.current_type):
                if self.sum_order_book is True:
                    self.previous_type = self.current_type                  
                    if self.current_type == BidAskStackType.STACKED_ASK:
                        self.sell_bitcoin_logic_market(current_amount, threshold, gdax, order_book)
                    elif self.current_type == BidAskStackType.STACKED_BID:
                        self.buy_bitcoin_logic_market(current_amount, threshold, gdax, order_book)
        except:
            print(traceback.format_exc())

    def buy_bitcoin_logic_market(self, current_amount, threshold, gdax, order_book):
        if (1 - (current_amount / self.previous_amount) > threshold):
            #Consider buy
            print('{2} BUY MARKET - Current: {0} | Previous: {1} | Division: {3} **************************'.format(current_amount, self.previous_amount, dt.datetime.now(), 1 - (current_amount / self.previous_amount)))
            if gdax.get_current_usd_amount() >= .0001 * current_amount:
                response = gdax.buy_bitcoin_market('.0001', current_amount)
                try:
                    print('Specified Buy: {0:.2f}'.format(float(response['price'])))
                    order = Order(response['id'], response['side'], response['size'], response['created_at'], current_amount)
                    order_book.Orders.add_order(order)
                    time.sleep(60)
                    order_status = gdax.client.get_order(order.order_id)
                    if order_status['status'] == 'done' or order_status['status'] == 'cancelled':
                        order_book.Orders.update_order(response['id'], status = OrderStatus.CLOSED)
                except:
                    print(traceback.format_exc())
                    print(response)
            else:
                print('Insufficient funds')
            self.previous_amount = current_amount

    def buy_bitcoin_logic_limit(self, current_amount, threshold, gdax, order_book):
        if (1 - (current_amount / self.previous_amount) > threshold):
            #Consider buy
            print('{2} BUY LIMIT - Current: {0} | Previous: {1} | Division: {3} **************************'.format(current_amount, self.previous_amount, dt.datetime.now(), 1 - (current_amount / self.previous_amount)))
            if gdax.get_current_usd_amount() >= .0001 * current_amount:
                response = gdax.buy_bitcoin_limit('.0001', round(current_amount, 2))
                try:
                    print('Specified Buy: {0:.2f}'.format(float(response['price'])))
                    order = Order(response['id'], response['side'], response['size'], response['created_at'], current_amount)
                    order_book.Orders.add_order(order)
                    time.sleep(60)
                    order_status = gdax.client.get_order(order.order_id)
                    if order_status['status'] == 'done' or order_status['status'] == 'cancelled':
                        order_book.Orders.update_order(response['id'], status = OrderStatus.CLOSED)
                except:
                    print(traceback.format_exc())
                    print(response)
            else:
                print('Insufficient funds')
            self.previous_amount = current_amount

    def sell_bitcoin_logic_market(self, current_amount, threshold, gdax, order_book, size = .0001):
        if (1 - (self.previous_amount / current_amount) > threshold):
            #Consider sell
            print('{2} SELL MARKET - Current: {0} | Previous: {1} | Division: {3} ***********************'.format(current_amount, self.previous_amount, dt.datetime.now(), 1 - (self.previous_amount / current_amount)))
            if gdax.get_current_btc_amount() >= .0001:
                response = gdax.sell_bitcoin_market(str(size))
                try:
                    print('Size: {0:.4f}'.format(float(response['size'])))
                    order = Order(response['id'], response['side'], response['size'], response['created_at'], current_amount)
                    order_book.Orders.add_order(order)
                    time.sleep(60)
                    order_status = gdax.client.get_order(order.order_id)
                    if order_status['status'] == 'done' or order_status['status'] == 'cancelled':
                        order_book.Orders.update_order(response['id'], status = OrderStatus.CLOSED)
                except:
                    print(traceback.format_exc())
                    print(response)
            else:
                print('Insufficient funds')
            self.previous_amount = current_amount

    def sell_bitcoin_logic_limit(self, current_amount, threshold, gdax, order_book, size = .0001):
        if (1 - (self.previous_amount / current_amount) > threshold):
            #Consider sell
            print('{2} SELL LIMIT - Current: {0} | Previous: {1} | Division: {3} ***********************'.format(current_amount, self.previous_amount, dt.datetime.now(), 1 - (self.previous_amount / current_amount)))
            if gdax.get_current_btc_amount() >= .0001:
                response = gdax.sell_bitcoin_limit(str(size), round(current_amount, 2))
                try:
                    print('Size: {0:.4f}'.format(float(response['size'])))
                    order = Order(response['id'], response['side'], response['size'], response['created_at'], current_amount)
                    order_book.Orders.add_order(order)
                    time.sleep(60)
                    order_status = gdax.client.get_order(order.order_id)
                    if order_status['status'] == 'done' or order_status['status'] == 'cancelled':
                        order_book.Orders.update_order(response['id'], status = OrderStatus.CLOSED)
                except:
                    print(traceback.format_exc())
                    print(response)
            else:
                print('Insufficient funds')
            self.previous_amount = current_amount

    def poll_print_for_console(self, order_book, gdax):
        def print_stuff(order_book, gdax):
            while True:
                if self.previous_amount != 0:
                    current_btc_bal = gdax.get_current_btc_amount()
                    last_amount = float(order_book.OrderBookCollection.last_amount)
                    print('{4} Current USD: {0:.2f} | Current BTC Balance: {1:.8f} | Current Value {5:.2f} | Current BTC Cost: {2:.3f} | Previous BTC Cost: {3:.3f} | Division: {6:.4f}'
                        .format(gdax.get_current_usd_amount(), current_btc_bal, last_amount + .005, float(self.previous_amount), dt.datetime.now(),
                                current_btc_bal * last_amount, 1 - (float(self.previous_amount) / last_amount)))
                    if any(order_book.Orders.OrdersList):
                        print('Orders: ***************************************************************** ')
                        [print(x.__dict__) for x in order_book.Orders.OrdersList]
                        print('')
                time.sleep(15)
        t = threading.Thread(args=(order_book, gdax,), target=print_stuff)
        t.daemon = True
        t.start()