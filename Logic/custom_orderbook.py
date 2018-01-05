from gdax.order_book import OrderBook
from Objects.gdax import GdaxOrderBookInfoCollection
from Objects.gdax import GdaxHistoric
from Logic.algorithm import Algorithm
from Objects.orders import Orders
from itertools import groupby
from operator import itemgetter
from Objects.orders import Order
import datetime as dt
import sys
import copy

class CustomOrderBook(OrderBook):
    def __init__(self,  gdax_object, product_id = 'BTC-USD'):
        super(CustomOrderBook, self).__init__(product_id = product_id)

        self._bid = None
        self._ask = None
        self._bid_depth = None
        self._ask_depth = None
        self.OrderBookCollection = GdaxOrderBookInfoCollection()
        self.historics = GdaxHistoric()
        self.Algorithm = Algorithm()
        self.gdax = gdax_object
        self.Orders = Orders()
        self.index_walls = dict()

    def on_message(self, message):
        try:
            super(CustomOrderBook, self).on_message(message)

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
                self.OrderBookCollection.add_new_row(bid, ask, bid_depth, ask_depth)
                self.OrderBookCollection.last_amount = bid
                self.historics.do_something_with_historical_row(bid, ask, dt.datetime.now())
                self.get_nearest_wall_distances()
                
                #print('{} {} bid: {:.3f} @ {:.2f}\task: {:.3f} @ {:.2f}'.format(dt.datetime.now(), self.product_id, bid_depth, bid, ask_depth, ask))
        except:
            print('EXCEPTION IN ON_MESSAGE: {0}'.format(sys.exc_info()[0]))
    
    def get_nearest_wall_distances(self):
        def get_index_of_bid_wall(current_book):
            first = itemgetter(0)
            second = itemgetter(1)
            sorted_asks = [(k, sum(item[1] for item in tups_to_sum)) for k, tups_to_sum in groupby(sorted(current_book['asks'], key=first), key=first)]
            if len(sorted_asks) < 15:
                return {}
            slice_sorted_asks = sorted_asks[:15]
            value = max(slice_sorted_asks, key=second)
            return {"bid_index":slice_sorted_asks.index(value), "bid_value":value[1]}
        def get_index_of_ask_wall(current_book):
            first = itemgetter(0)
            second = itemgetter(1)
            sorted_bids = [(k, sum(item[1] for item in tups_to_sum)) for k, tups_to_sum in groupby(sorted(current_book['bids'], key=first), key=first)] 
            if len(sorted_bids) < 15:
                return {}
            slice_sorted_bids = sorted_bids[-15:]
            value = max(slice_sorted_bids, key=second)
            return {"ask_index":abs(slice_sorted_bids.index(value) - 14), "ask_value":value[1]}
        current_book = self.get_current_book()
        index_walls = {**get_index_of_bid_wall(current_book), **get_index_of_ask_wall(current_book)}
        self.index_walls = index_walls