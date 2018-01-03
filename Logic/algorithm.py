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

class Algorithm:
    def gdax_main(self, order_book, gdax):
        slept = False
        threshold = 0.0075
        previous_type, previous_amount = BidAskStackType.NEITHER, 0
        while True:
            current_type = order_book.OrderBookCollection.determine_if_sell_or_buy_bids_are_stacked()     
            current_amount = float(order_book.OrderBookCollection.last_amount)
            if current_amount != 0 and previous_amount == 0:
                previous_amount = current_amount
                print('Starting amount {0} @ {1}'.format(current_amount, dt.datetime.now()))
                continue
            if current_type != BidAskStackType.NEITHER and previous_type != current_type:
                if previous_amount == current_amount:
                    continue
                sum_order_book = self.determine_sum_order_book(order_book, current_type)
                if sum_order_book is True:
                    if slept is False:
                        time.sleep(6) #Make sure it wasn't a random push that got balanced out within n seconds to ruin the trend
                        slept = True
                        continue
                    else:
                        slept = False                        
                    if current_type == BidAskStackType.STACKED_ASK:
                        if 1 - (previous_amount / current_amount) > threshold:
                            #Consider sell
                            print('{2} SELL - Current: {0} | Previous: {1} | Division: {3} ***********************'.format(current_amount, previous_amount, dt.datetime.now(), 1 - (previous_amount / current_amount)))
                            if gdax.get_current_btc_amount() >= .0001:
                                response = gdax.sell_bitcoin('.0001', current_amount)
                                try:
                                    print('Size: {0:.4f}'.format(response['size']))
                                except:
                                    print(response)
                            previous_amount = current_amount
                    elif current_type == BidAskStackType.STACKED_BID:
                        if 1 - (current_amount / previous_amount) > threshold:
                            #Consider buy
                            print('{2} BUY - Current: {0} | Previous: {1} | Division: {3} **************************'.format(current_amount, previous_amount, dt.datetime.now(), 1 - (current_amount / previous_amount)))
                            if gdax.get_current_usd_amount() >= .0001 * current_amount:
                                response = gdax.buy_bitcoin('.0001', current_amount)
                                try:
                                    print('Existing USD: {0:.6f} | Specified Buy: {1:.2f}'.format(response['funds'], response['specified_funds']))
                                except:
                                    print(response)
                            previous_amount = current_amount

    def determine_sum_order_book(self, order_book, current_type):
        asks = self.get_sorted_asks(order_book)
        bids = self.get_sorted_bids(order_book)
        ask_sizes = ([x[1] for x in asks])
        bid_sizes = ([x[1] for x in bids])
        bid_sum = sum(bid_sizes[-15:])
        ask_sum = sum(ask_sizes[:15])
        if current_type == BidAskStackType.STACKED_ASK:
            return ask_sum >= bid_sum * Decimal(1.25)
        elif current_type == BidAskStackType.STACKED_BID:
            return bid_sum >= ask_sum * Decimal(1.25)
        return False

    def get_sorted_asks(self, order_book):
        first = itemgetter(0)
        return [(k, sum(item[1] for item in tups_to_sum)) for k, tups_to_sum in groupby(sorted(order_book.get_current_book()['asks'], key=first), key=first)]
    
    def get_sorted_bids(self, order_book):
        first = itemgetter(0)
        return [(k, sum(item[1] for item in tups_to_sum)) for k, tups_to_sum in groupby(sorted(order_book.get_current_book()['bids'], key=first), key=first)]                        
