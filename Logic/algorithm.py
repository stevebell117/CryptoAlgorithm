from Logic.math import Sign
from Objects.prices import Prices
from Objects.price import Price
from Objects.gdax import BidAskStackType
from Objects.gdax import ChangeType
from itertools import groupby
from operator import itemgetter
import datetime as dt
import time
from decimal import Decimal
import traceback

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
            threshold = 0.0075
            self.current_type = order_book.OrderBookCollection.determine_if_sell_or_buy_bids_are_stacked()         
            current_amount = float(order_book.OrderBookCollection.last_amount)
            if current_amount != 0 and self.previous_amount == 0:
                self.previous_amount = current_amount
                print('Starting amount {0} @ {1}'.format(current_amount, dt.datetime.now()))
                return
            if self.current_type != BidAskStackType.NEITHER and self.previous_type != self.current_type:
                if self.sum_order_book is True:
                    self.previous_type = self.current_type                  
                    if self.current_type == BidAskStackType.STACKED_ASK:
                        if 1 - (self.previous_amount / current_amount) > threshold:
                            #Consider sell
                            print('{2} SELL - Current: {0} | Previous: {1} | Division: {3} ***********************'.format(current_amount, self.previous_amount, dt.datetime.now(), 1 - (self.previous_amount / current_amount)))
                            if gdax.get_current_btc_amount() >= .0001:
                                response = gdax.sell_bitcoin('.0001', current_amount)
                                try:
                                    print('Size: {0:.4f}'.format(response['size']))
                                except:
                                    print(response)
                            self.previous_amount = current_amount
                    elif self.current_type == BidAskStackType.STACKED_BID:
                        if 1 - (current_amount / self.previous_amount) > threshold:
                            #Consider buy
                            print('{2} BUY - Current: {0} | Previous: {1} | Division: {3} **************************'.format(current_amount, self.previous_amount, dt.datetime.now(), 1 - (current_amount / self.previous_amount)))
                            if gdax.get_current_usd_amount() >= .0001 * current_amount:
                                response = gdax.buy_bitcoin('.0001', current_amount)
                                try:
                                    print('Existing USD: {0:.6f} | Specified Buy: {1:.2f}'.format(response['funds'], response['specified_funds']))
                                except:
                                    print(response)
                            self.previous_amount = current_amount
        except:
            print(traceback.format_exc())
