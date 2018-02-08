from gdax_lib.order_book import OrderBook
from gdax_lib.websocket_client import WebsocketClient
from Objects.gdax import GdaxOrderBookInfoCollection
from Objects.gdax import GdaxHistoric
from Logic.algorithm import Algorithm
from Objects.orders import Orders
from itertools import groupby
from operator import itemgetter
from Objects.orders import Order
from enum import Enum
from Objects.log import Logs
import time
import datetime as dt
import sys
import traceback
import copy

class CustomOrderBook(OrderBook):
    def __init__(self, product_id='BTC-USD', log_to=None):
        super(CustomOrderBook, self).__init__(product_id = product_id)

        self._bid = None
        self._ask = None
        self._bid_depth = None
        self._ask_depth = None

    def process_message(self, message):
        if message.get('product_id') == self.product_id:
            super(CustomOrderBook, self).process_message(message)

            try:
                bid = self.get_bid()
                bids = self.get_bids(bid)
                bid_depth = sum([b['size'] for b in bids])
                ask = self.get_ask()
                asks = self.get_asks(ask)
                ask_depth = sum([a['size'] for a in asks])

                if self._bid == bid and self._ask == ask and self._bid_depth == bid_depth and self._ask_depth == ask_depth:
                    # If there are no changes to the bid-ask spread since the last update, no need to print
                    pass
                else:
                    # If there are differences, update the cache
                    self._bid = bid
                    self._ask = ask
                    self._bid_depth = bid_depth
                    self._ask_depth = ask_depth

                    #print('{} {} bid: {:.3f} @ {:.2f}\task: {:.3f} @ {:.2f}'.format(dt.datetime.now(), self.product_id, bid_depth, bid, ask_depth, ask))
            except Exception as e:
                pass


class CustomOrderBookRun(WebsocketClient):   
    def get_current_book(self):
        return self.order_book_btc.get_current_book()

    def on_open(self):
        self.products = ['BTC-USD']
        self.url = "wss://ws-feed.gdax.com/"
        self.order_book_btc = CustomOrderBook(product_id='BTC-USD')    
        self.OrderBookCollection = GdaxOrderBookInfoCollection()
        self.historics = GdaxHistoric()
        self.Algorithm = Algorithm()
        self.Orders = Orders()
        self.Logs = Logs()
        self.index_walls = dict()

    def on_message(self, msg):
        try:
            self.order_book_btc.process_message(msg)
        except Exception as e:
            self.Logs.error(e, 'custom_orderbook on_message')
        if len(self.OrderBookCollection.OrderBookCollection) > 200:
            self.OrderBookCollection.OrderBookCollection.pop(0)
            self.OrderBookCollection.add_new_row(self.order_book_btc._bid, self.order_book_btc._ask, self.order_book_btc._bid_depth, self.order_book_btc._ask_depth)

    def get_nearest_wall_distances(self, current_amount, order_book):
        def get_index_of_ask_wall(current_book, current_amount):
            first, second = itemgetter(0), itemgetter(1)
            sorted_asks = [(k, sum(item[1] for item in tups_to_sum if item[0] >= current_amount)) for k, tups_to_sum in groupby(sorted(current_book['asks'], key=first), key=first)]
            if len(sorted_asks) < 15:
                return {"ask_index": -1, "ask_value": 0, "ask_amount": 0}
            slice_sorted_asks = sorted_asks[:15]
            value = max(slice_sorted_asks, key=second)
            return {"ask_index":slice_sorted_asks.index(value), "ask_value":value[1], "ask_amount": value[0]}
        def get_index_of_bid_wall(current_book, current_amount):
            first, second = itemgetter(0), itemgetter(1)
            sorted_bids = [(k, sum(item[1] for item in tups_to_sum if item[0] <= current_amount)) for k, tups_to_sum in groupby(sorted(current_book['bids'], key=first), key=first)] 
            if len(sorted_bids) < 15:
                return {"bid_index": -1, "bid_value": 0, "bid_amount": 0}
            slice_sorted_bids = sorted_bids[-15:]
            value = max(slice_sorted_bids, key=second)
            return {"bid_index":abs(slice_sorted_bids.index(value) - 14), "bid_value":value[1], "bid_amount": value[0]}
        index_walls = {**get_index_of_bid_wall(order_book, current_amount), **get_index_of_ask_wall(order_book, current_amount)}
        self.index_walls = index_walls

    def get_wall_info(self, previous_amount):
        if len(self.index_walls) > 0:
            ask_index = float(self.index_walls["ask_index"])
            ask_value = float(self.index_walls["ask_value"])
            ask_amount = float(self.index_walls["ask_amount"])
            bid_index = float(self.index_walls["bid_index"])
            bid_value = float(self.index_walls["bid_value"])
            bid_amount = float(self.index_walls["bid_amount"])
            # if ask_index < 2 and bid_index < 2:
            #     return {'side': '', 'amount': 0}
            if (  ask_index - 4 <= bid_index <= ask_index + 4 and 
                    bid_index - 4 <= ask_index <= bid_index + 4 and
                    ask_value - 7 <= bid_value <= ask_value + 7 and 
                    bid_value - 7 <= ask_value <= bid_value + 7): 
                return {'side': '', 'amount': 0}
            elif (ask_index > 4 and ask_value > 14
               and bid_index < 4 and bid_value < 14):
                return {'side': 'buy', 'amount': bid_amount}
            elif (bid_index > 4 and bid_value > 14
               and ask_index < 4 and ask_value < 14):
                return {'side': 'sell', 'amount': ask_amount}
            return {'side': '', 'amount': 0}
        else:
            return {'side': '', 'amount': 0} 