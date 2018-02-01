from Objects.gdax import BidAskStackType
from Objects.orders import Order
from Objects.orders import OrderStatus
from itertools import groupby
from operator import itemgetter
import datetime as dt
import time
import os
from decimal import Decimal
import traceback
from enum import Enum
import threading
import sys
from Objects.log import LogType
#import numpy as numpy
#import matplotlib.pyplot as plt
#import matplotlib.animation as animation

BUY_SELL_AMOUNT = .002
threshold = 0.005

class WallType(Enum):
    NO_WALL = 0
    ASK_WALL = 1
    BID_WALL = 2

class Algorithm:
    def __init__(self):
        self.previous_type = BidAskStackType.NEITHER
        self.previous_amount = 0
        self.wall_type = WallType.NO_WALL
        self.current_type = BidAskStackType.NEITHER
        self.last_action = dt.datetime.now()
        self.last_print = dt.datetime.now()

    def get_sorted_asks(self, current_book, current_amount):
        first = itemgetter(0)
        return [(k, sum(item[1] for item in tups_to_sum if item[0] >= current_amount)) for k, tups_to_sum in groupby(sorted(current_book['asks'], key=first), key=first)]
    
    def get_sorted_bids(self, current_book, current_amount):
        first = itemgetter(0)
        return [(k, sum(item[1] for item in tups_to_sum if item[0] <= current_amount)) for k, tups_to_sum in groupby(sorted(current_book['bids'], key=first), key=first)]

    def determine_wall_type(self, order_book, current_amount):
        current_book = order_book.get_current_book()
        asks, bids = self.get_sorted_asks(current_book, current_amount), self.get_sorted_bids(current_book, current_amount)
        ask_sizes, bid_sizes = ([x[1] for x in asks]), ([x[1] for x in bids])
        bid_sum, ask_sum = sum(bid_sizes[-15:]), sum(ask_sizes[:15])
        #print('ask_sum {0} | bid_sum {1} | {2}'.format(ask_sum, bid_sum, current_type))
        if ask_sum >= bid_sum * Decimal(1.5):
            return WallType.ASK_WALL
        elif bid_sum >= ask_sum * Decimal(1.5):
            return WallType.BID_WALL
        return WallType.NO_WALL

    def process_order_book(self, order_book, current_amount):
        try:
            self.wall_type = self.determine_wall_type(order_book, current_amount)
        except Exception as e:
            order_book.Logs.error(e, 'process_order_book')
            #print('ERROR IN PROCESS_ORDER_BOOK {0}'.format(traceback.format_exc()))
    
    def gdax_main(self, order_book, gdax):
        try:
            self.current_type = order_book.OrderBookCollection.determine_if_sell_or_buy_bids_are_stacked(order_book)         
            current_amount = gdax.get_current_btc_cost(0)
            if self.previous_amount == 0:
                self.previous_amount = current_amount
                if current_amount != 0: print('Starting amount {0} @ {1}'.format(current_amount, dt.datetime.now()))
                return
            wall_var = order_book.determine_if_wall_is_coming(self.previous_amount)
            self.check_if_order_complete(order_book, gdax)
            if self.wall_type != WallType.NO_WALL:
                if wall_var['side'] == 'sell' or wall_var['side'] == 'buy':
                    if dt.datetime.now() > self.last_action + dt.timedelta(seconds=30): #30 second cooldown
                        if wall_var['side'] == 'sell' and self.wall_type == WallType.ASK_WALL:
                            self.sell_bitcoin_logic_limit(float(wall_var['amount']) - .01, gdax, order_book)
                        else:
                            self.buy_bitcoin_logic_limit(float(wall_var['amount']) + .01, gdax, order_book)
        except Exception as e:
            order_book.Logs.error(e, 'gdax_main')
            #print('ERROR IN GDAX MAIN {0}'.format(traceback.format_exc()))

    def buy_bitcoin_logic_market(self, current_amount, gdax, order_book):
        if (round(1 - (current_amount / self.previous_amount), 4) > threshold):
            #Consider buy
            #print('{2} BUY MARKET - Current: {0} | Previous: {1} | Division: {3} **************************'.format(current_amount, self.previous_amount, dt.datetime.now(), 1 - (current_amount / self.previous_amount)))
            if gdax.get_current_usd_amount() >= BUY_SELL_AMOUNT * current_amount:
                response = gdax.buy_bitcoin_market(current_amount)
                try:
                    order = Order(response['id'], response['side'], response['size'], current_amount, self.previous_amount)
                    order_book.Orders.add_order(order)
                except:
                    print(traceback.format_exc())
                    print(response)
            else:
                print('Insufficient funds')
            self.update_previous_info(current_amount)

    def buy_bitcoin_logic_limit(self, current_amount, gdax, order_book):
        if (round(1 - (current_amount / self.previous_amount), 4) > threshold):
            #Consider buy
            #print('{2} BUY LIMIT - Current: {0} | Previous: {1} | Division: {3} **************************'.format(current_amount, self.previous_amount, dt.datetime.now(), 1 - (current_amount / self.previous_amount)))
            if gdax.get_current_usd_amount() >= BUY_SELL_AMOUNT * current_amount:
                response = gdax.buy_bitcoin_limit(str(BUY_SELL_AMOUNT), round(current_amount, 2))
                try:
                    order = Order(response['id'], response['side'], response['size'], current_amount, self.previous_amount)
                    order_book.Orders.add_order(order)
                except:
                    print(traceback.format_exc())
                    print(response)
            else:
                print('Insufficient funds')
            self.update_previous_info(current_amount)

    def sell_bitcoin_logic_market(self, current_amount, gdax, order_book, size = BUY_SELL_AMOUNT):
        if (round(1 - (self.previous_amount / current_amount), 4) > threshold):
            #Consider sell
            #print('{2} SELL MARKET - Current: {0} | Previous: {1} | Division: {3} ***********************'.format(current_amount, self.previous_amount, dt.datetime.now(), 1 - (self.previous_amount / current_amount)))
            if gdax.get_current_btc_amount() >= BUY_SELL_AMOUNT:
                response = gdax.sell_bitcoin_market(str(size))
                try:
                    order = Order(response['id'], response['side'], response['size'], current_amount, self.previous_amount)
                    order_book.Orders.add_order(order)
                except:
                    print(traceback.format_exc())
                    print(response)
            else:
                print('Insufficient funds')
            self.update_previous_info(current_amount)

    def sell_bitcoin_logic_limit(self, current_amount, gdax, order_book, size = BUY_SELL_AMOUNT):
        if (round(1 - (self.previous_amount / current_amount), 4) > threshold):
            #Consider sell
            #print('{2} SELL LIMIT - Current: {0} | Previous: {1} | Division: {3} ***********************'.format(current_amount, self.previous_amount, dt.datetime.now(), 1 - (self.previous_amount / current_amount)))
            if gdax.get_current_btc_amount() >= BUY_SELL_AMOUNT:
                response = gdax.sell_bitcoin_limit(str(size), round(current_amount, 2))
                try:
                    order = Order(response['id'], response['side'], response['size'], current_amount, self.previous_amount)
                    order_book.Orders.add_order(order)                    
                except:
                    print(traceback.format_exc())
                    print(response)
            else:
                print('Insufficient funds')
            self.update_previous_info(current_amount)

    def poll_print(self, order_book, gdax):
        def print_stuff(order_book, gdax):
            last_amount = 0
            while True:
                try:
                    if self.previous_amount != 0:
                        current_btc_bal = gdax.get_current_btc_amount()
                        current_book = order_book.get_current_book()
                        if not current_book:
                            continue
                        last_amount = gdax.get_current_btc_cost(last_amount) 
                        os.system('cls' if os.name == 'nt' else 'clear')
                        if any(order_book.Logs.get_logs()):
                            print('Log(s): *********')
                            for log in order_book.Logs.get_logs():
                                print(' Time: {0}\n  Type: {1}\n  Message: {2}\n  Location: {3}\n'.format(log.time, log.type, log.message, log.location))
                        if any(order_book.Orders.OrdersList):
                            print('Order(s): ***********')
                            for order in order_book.Orders.OrdersList:
                                print('  Time: {0}\n  Side: {1}\n  Size: {2}\n  Price: {3}\n  Fees: {4}\n  Status: {5}\n'.format(
                                    order.time, order.side, order.size, order.price, order.fill_fees, order.status
                                ))
                        print('**** {4} ****\n  Current USD: {0:.2f} \n  Current BTC Balance: {1:.8f} \n  Current BTC Value {5:.2f} \n  Current BTC Cost: {2:.3f} \n  Previous BTC Cost: {3:.3f} \n  Previous Action Time: {7} \n  Division: {6:.4f}'
                            .format(gdax.get_current_usd_amount(), current_btc_bal, last_amount - .005, float(self.previous_amount), dt.datetime.now(),
                                    current_btc_bal * last_amount, 1 - (float(self.previous_amount) / last_amount), self.last_action))
                        print('')
                        print('Enter an alpha value to quit: ', end='')
                        sys.stdout.flush()
                    time.sleep(15)
                except Exception as e:
                    order_book.Logs.error(e, 'print_stuff')
                    print(traceback.format_exc())
        t = threading.Thread(args=(order_book, gdax,), target=print_stuff)
        t.daemon = True
        t.start()   

    def check_if_order_complete(self, order_book, gdax):
        order_to_remove = None
        for order in order_book.Orders.OrdersList[::-1]:
            if order.status == OrderStatus.CANCELLED:
                order_to_remove = order
                break
        if order_to_remove != None:
        #     print('Limit {0} order failed. Doing Market.'.format(order_to_remove.side))
        #     if order_to_remove.side == 'buy':
        #         self.buy_bitcoin_logic_market(float(order_to_remove.price), gdax, order_book)
        #     else:
        #         self.sell_bitcoin_logic_market(float(order_to_remove.size), gdax, order_book)
            self.previous_amount = order_to_remove.previous_amount
            order_book.Orders.OrdersList.remove(order_to_remove)

    def update_previous_info(self, current_amount):
        self.previous_amount = current_amount
        self.last_action = dt.datetime.now()

    ## Something to consider bringing back
    # def plot_entries(self, order_book):
    #     current_book = order_book.get_current_book()
    #     sorted_asks = self.get_sorted_asks(current_book)
    #     sorted_bids = self.get_sorted_bids(current_book)

    #     fig = plt.figure()
    #     ax1 = fig.subplots()

    #     def temp(self):
    #         ax1.clear()
    #         ax1.plot(sorted_asks[0], sorted_asks[1])
    #         ax1.plot(sorted_bids[0], sorted_bids[1])

    #     ani = animation.FuncAnimation(fig, temp, interval=1000)
    #     plt.xlabel('Prices')
    #     plt.ylabel('Amounts')
    #     plt.legend(['asks', 'bids'])
    #     plt.show()

