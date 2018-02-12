from Objects.gdax import BidAskStackType
from Objects.orders import Order
from Objects.orders import OrderStatus
from Logic.database import Database
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
import uuid
import pyodbc 
#import numpy as numpy
#import matplotlib.pyplot as plt
#import matplotlib.animation as animation



class WallType(Enum):
    NO_WALL = 0
    ASK_WALL = 1
    BID_WALL = 2

class Algorithm:
    BUY_SELL_AMOUNT = .002
    threshold = 0.005
    CURRENT_LIMIT_TO_VERIFY = 50

    def __init__(self):
        self.previous_type = BidAskStackType.NEITHER
        self.previous_amount = 0
        self.wall_type = WallType.NO_WALL
        self.current_type = BidAskStackType.NEITHER
        self.last_action = dt.datetime.now()
        self.last_print = dt.datetime.now()
        self.order_book = None
        self.temp_order = None
        self.database = Database()

    def set_order_book(self, order_book):
        self.order_book = order_book

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
        if ask_sum >= bid_sum * Decimal(1.5):
            return WallType.ASK_WALL
        elif bid_sum >= ask_sum * Decimal(1.5):
            return WallType.BID_WALL
        return WallType.NO_WALL

    def process_order_book(self, order_book, current_amount):
        try:
            self.wall_type = self.determine_wall_type(order_book, current_amount)
        except ValueError:
            pass        
        except Exception as e:
            order_book.Logs.error(message=e, location='process_order_book', additional_message=traceback.format_exc(), db_object=self.database)
    
    def gdax_main(self, order_book, gdax):
        try:
            self.current_type = order_book.OrderBookCollection.determine_if_sell_or_buy_bids_are_stacked(order_book)         
            current_amount = gdax.get_current_btc_cost(0)
            self.previous_amount = gdax.get_previous_amount(order_book.Orders.get_orders())
            wall_var = order_book.get_wall_info(self.previous_amount, gdax)
            self.check_if_order_complete(order_book, gdax)
            if self.wall_type != WallType.NO_WALL and (wall_var['side'] == 'sell' or wall_var['side'] == 'buy'):
                if ((dt.datetime.now() > self.last_action + dt.timedelta(seconds=60)) #60 second cooldown
                    and (current_amount - self.CURRENT_LIMIT_TO_VERIFY <= float(wall_var['amount']) <= current_amount + self.CURRENT_LIMIT_TO_VERIFY)):
                    if wall_var['side'] == 'sell' and self.wall_type == WallType.ASK_WALL:
                        self.sell_bitcoin_logic_limit(float(wall_var['amount']) - .01, gdax, order_book, self.BUY_SELL_AMOUNT)
                    else:
                        self.buy_bitcoin_logic_limit(float(wall_var['amount']) + .01, gdax, order_book)
        except ValueError:
            pass        
        except Exception as e:
            order_book.Logs.error(message=e, location='gdax_main', additional_message=traceback.format_exc(), db_object=self.database)

    def buy_bitcoin_logic_market(self, current_amount, gdax, order_book):
        if (round(1 - (current_amount / self.previous_amount), 4) > self.threshold):
            if gdax.get_current_usd_amount() >= self.BUY_SELL_AMOUNT * current_amount:
                response = gdax.buy_bitcoin_market(current_amount)
                try:
                    order = Order(response['id'], response['side'], response['size'], current_amount, self.previous_amount)
                    order_book.Orders.add_order(order)
                    self.update_previous_info()
                except:
                    print(traceback.format_exc())
                    print(response)
            else:
                order = Order('fake', 'buy', self.BUY_SELL_AMOUNT, current_amount, self.previous_amount, OrderStatus.REJECTED)
                self.database.insert_order_into_database(order)
                order_book.Orders.add_order(order)

    def buy_bitcoin_logic_limit(self, current_amount, gdax, order_book):
        if (round(1 - (current_amount / self.previous_amount), 4) > self.threshold):
            last_sell = self.get_last_sell(order_book)
            if last_sell is not None:
                size = round(self.determine_size(current_amount, last_sell.price), 8)
            else:
                size = self.BUY_SELL_AMOUNT
            if gdax.get_current_usd_amount() >= size * current_amount:
                response = gdax.buy_bitcoin_limit(str(size), round(current_amount, 2))
            elif gdax.get_current_usd_amount() >= self.BUY_SELL_AMOUNT * current_amount:
                response = gdax.buy_bitcoin_limit(str(self.BUY_SELL_AMOUNT), round(current_amount, 2))
            else:
                order = Order('fake', 'buy', self.BUY_SELL_AMOUNT, current_amount, self.previous_amount, OrderStatus.REJECTED)
                self.database.insert_order_into_database(order)
                order_book.Orders.add_order(order)
                self.update_previous_info()
                return
            try:
                order = Order(response['id'], response['side'], response['size'], current_amount, self.previous_amount)
                order_book.Orders.add_order(order)
                self.database.insert_order_into_database(order)
                if last_sell is not None: 
                    order_book.Orders.update_order(order=last_sell, balanced=True)
                    self.database.update_order_in_database(last_sell)
                self.update_previous_info()
            except:
                order_book.Logs.error(message=response, location='buy_bitcoin_logic_limit', additional_message=traceback.format_exc(), db_object=self.database)

    def determine_size(self, current_amount, last_sell_price):
        sell_total = float(str(last_sell_price)) * float(str(self.BUY_SELL_AMOUNT))
        potential_buy = current_amount * self.BUY_SELL_AMOUNT
        difference = sell_total - potential_buy
        profit_loss = difference / current_amount
        return profit_loss + self.BUY_SELL_AMOUNT

    def sell_bitcoin_logic_market(self, current_amount, gdax, order_book, size = .001):
        if (round(1 - (self.previous_amount / current_amount), 4) > self.threshold):
            if gdax.get_current_btc_amount() >= self.BUY_SELL_AMOUNT:
                response = gdax.sell_bitcoin_market(str(size))
                try:
                    order = Order(response['id'], response['side'], response['size'], current_amount, self.previous_amount)
                    order_book.Orders.add_order(order)
                    self.update_previous_info()
                except:
                    print(traceback.format_exc())
                    print(response)
            else:
                order = Order('fake', 'sell', self.BUY_SELL_AMOUNT, current_amount, self.previous_amount, OrderStatus.REJECTED)
                self.database.insert_order_into_database(order)
                order_book.Orders.add_order(order)

    def sell_bitcoin_logic_limit(self, current_amount, gdax, order_book, size = 0.001):
        if (round(1 - (self.previous_amount / current_amount), 4) > self.threshold):
            if gdax.get_current_btc_amount() >= self.BUY_SELL_AMOUNT:
                response = gdax.sell_bitcoin_limit(str(size), round(current_amount, 2))
                try:
                    order = Order(response['id'], response['side'], response['size'], current_amount, self.previous_amount)
                    order_book.Orders.add_order(order)
                    self.database.insert_order_into_database(order)
                    self.update_previous_info()                    
                except:
                    print(traceback.format_exc())
                    print(response)
            else:
                order = Order('fake', 'sell', self.BUY_SELL_AMOUNT, current_amount, self.previous_amount, OrderStatus.REJECTED)
                self.database.insert_order_into_database(order)
                order_book.Orders.add_order(order)

    def poll_print(self, order_book, gdax, threads):
        def print_stuff(order_book, gdax, threads):
            last_amount = 0
            while True:
                try:
                    if self.previous_amount != 0:
                        current_btc_bal = gdax.get_current_btc_amount()
                        last_amount = gdax.get_current_btc_cost(last_amount) 
                        os.system('cls' if os.name == 'nt' else 'clear')
                        if any(order_book.Logs.get_logs()):
                            print('Log(s): *********')
                            for log in order_book.Logs.get_logs():
                                print(' Time: {0}\n  Type: {1}\n  Message: {2}\n  Location: {3}\n'.format(log.time, log.type, log.message, log.location))
                        if any(order_book.Orders.OrdersList):
                            print('Order(s): ***********')
                            for order in order_book.Orders.OrdersList:
                                print('  Time: {0}\n  Side: {1}\n  Size: {2}\n  Price: {3}\n  Fees: {4}\n  Status: {5}\n  Balanced: {6}\n'.format(
                                    order.time, order.side, order.size, order.price, order.fill_fees, order.status, order.balanced
                                ))
                        if threads:
                            print('Threads: *********')
                            for thread in threads:
                                print('  Name: {0} | Status: {1}'.format(thread.name, 'Alive' if thread.isAlive() else 'Dead'))
                            print('')
                        print("""General Information: *******
   Current Time: {4} 
   Current USD: {0:.2f}   
   Current BTC Balance: {1:.8f} 
   Current BTC Value {5:.2f} 
   Current BTC Cost: {2:.3f} 
   Current Threshold: {8:.8f} 
   Previous BTC Cost: {3:.3f} 
   Previous Action Time: {7}
   Division: {6:.4f}"""
                            .format(gdax.get_current_usd_amount(), current_btc_bal, last_amount - .005, float(self.previous_amount), dt.datetime.now(),
                                    current_btc_bal * last_amount, 1 - (float(self.previous_amount) / last_amount), self.last_action, order_book.threshold_value ))
                        print('')
                        print('Enter an alpha value to quit: ', end='')
                        sys.stdout.flush()
                    time.sleep(5)
                except ValueError:
                    pass        
                except Exception as e:
                    order_book.Logs.error(message=e, location='print_stuff', additional_message=traceback.format_exc(), db_object=self.database)
                    print(traceback.format_exc())
        t = threading.Thread(args=(order_book, gdax, threads,), target=print_stuff)
        t.daemon = True
        t.start()   

    def get_last_sell(self, order_book, balanced_to_get = False):
        return next((x for x in order_book.Orders.get_orders()[::-1] if x.side == 'sell' and x.balanced == balanced_to_get and (x.status == OrderStatus.CLOSED or x.status == OrderStatus.OVERRIDE)), None)

    def check_if_order_complete(self, order_book, gdax):
        order_to_remove = None
        for order in order_book.Orders.OrdersList[::-1]:
            if order.status == OrderStatus.CANCELLED:
                if order.side == 'buy':
                    last_sell = self.get_last_sell(order_book, balanced_to_get=True)
                    if last_sell is not None: 
                        order_book.Orders.update_order(order=last_sell, balanced=False)
                        self.database.update_order_in_database(last_sell)
                order_to_remove = order
                break
        if order_to_remove != None:
            self.previous_amount = order_to_remove.previous_amount
            self.database.remove_order_from_database(order_to_remove)
            order_book.Orders.OrdersList.remove(order_to_remove)

    def update_previous_info(self):
        #self.previous_amount = current_amount
        self.last_action = dt.datetime.now()
