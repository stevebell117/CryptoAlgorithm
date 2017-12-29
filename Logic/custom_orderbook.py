from gdax.order_book import OrderBook
from Objects.gdax import GdaxOrderBookInfoCollection

class CustomOrderBook(OrderBook):
    def __init__(self, product_id = 'BTC-USD'):
        super(CustomOrderBook, self).__init__(product_id = product_id)

        self._bid = None
        self._ask = None
        self._bid_depth = None
        self._ask_depth = None

    def on_message(self, message):
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
            #print('{} {} bid: {:.3f} @ {:.2f}\task: {:.3f} @ {:.2f}'.format(
            #    dt.datetime.now(), self.product_id, bid_depth, bid, ask_depth, ask))