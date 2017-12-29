from datetime import datetime
import dateutil.parser
from enum import Enum
import json

max_list_size_for_entries = 300

class GdaxTicker():
    def __init__(self):
        self.ticker = list()

    def add_row_to_ticker(self, ticker_row):
        row = GdaxTickerRow()
        row.populate_ticker_row(ticker_row)
        if(len(self.ticker) > max_list_size_for_entries):
            self.ticker.pop(0)
        if any(x.trade_id == ticker_row["trade_id"] for x in self.ticker) is False:
            self.ticker.append(row)

class GdaxTickerRow():
    def __init__(self):
        self.trade_id = ''
        self.price = 0
        self.size = 0
        self.bid = 0
        self.ask = 0
        self.volume = 0
        self.time = datetime.now()

    def populate_ticker_row(self, ticker_object):
        self.trade_id = ticker_object["trade_id"]
        self.price = float(ticker_object["price"])
        self.size = float(ticker_object["size"])
        self.bid = float(ticker_object["bid"])
        self.ask = float(ticker_object["ask"])
        self.volume = float(ticker_object["volume"])
        self.time = datetime.isoformat(datetime.strptime(ticker_object["time"], '%Y-%m-%dT%H:%M:%S.%fZ'))

class GdaxTrades():
    def __init__(self):
        self.trades = list()

    def add_rows_to_trades(self, trades_rows):
        for trade_row in trades_rows:
            row = GdaxTradeRow()
            row.populate_trade_row(trade_row)
            if(len(self.trades) > max_list_size_for_entries):
                self.trades.pop(0)
            if any(x.trade_id == trade_row["trade_id"] for x in self.trades) is False:
                self.trades.append(row)

class GdaxTradeRow():
    def __init__(self):
        self.trade_id=''
        self.price = 0
        self.size = 0
        self.side = ""
        self.time = datetime.now()

    def populate_trade_row(self, trade_object):
        self.trade_id = trade_object["trade_id"]
        self.price = float(trade_object["price"])
        self.size = float(trade_object["size"])
        self.side = trade_object["side"]
        try:
            self.time = datetime.isoformat(datetime.strptime(trade_object["time"], '%Y-%m-%dT%H:%M:%S.%fZ'))
        except:
            self.time = datetime.isoformat(datetime.strptime(trade_object["time"], '%Y-%m-%dT%H:%M:%SZ'))

class GdaxHistoric():
    def __init__(self):
        self.historics = list()

    def add_rows_to_history(self, history_rows):
        for history_row in history_rows:
            if any(x.time == history_row[0] for x in self.historics) is False:
                row = GdaxHistoricRow()
                row.populate_historic_row(history_row)
                if len(self.historics) > max_list_size_for_entries:
                    self.historics.pop(0)
                self.historics.append(row)

class GdaxHistoricRow:
    def __init__(self):
        self.low = 0
        self.high = 0
        self.time = datetime.now()
        self.open = 0
        self.close = 0
        self.volume = 0
        self.change_type = ChangeType.NO_CHANGE

    def populate_historic_row(self, trade_object):
        self.time = float(trade_object[0]) #We'll need to just determine seconds by doing 24 * 60 * 60 to determine a day before entry...
        self.low = float(trade_object[1])
        self.high = float(trade_object[2])
        self.open = float(trade_object[3])
        self.close = float(trade_object[4])
        self.volume = float(trade_object[5])
        difference_in_period = self.close - self.open
        if difference_in_period > 0 and abs(difference_in_period / self.open) < .0005:
            self.change_type = ChangeType.NO_CHANGE
        elif difference_in_period > 0 and difference_in_period / self.open < .005:
            self.change_type = ChangeType.RISE
        elif difference_in_period > 0 and difference_in_period / self.open >= .005:
            self.change_type = ChangeType.SHARP_RISE
        elif difference_in_period < 0 and difference_in_period / self.open < .005:
            self.change_type = ChangeType.FALL
        elif difference_in_period < 0 and difference_in_period / self.open >= .005:
            self.change_type = ChangeType.SHARP_FALL

class GdaxOrderBookInfoCollection():
    def __init__(self):
        self.OrderBookCollection = list()

    class GdaxOrderBookInfo():
        def __init__(self, bid = None, ask = None, bid_depth = None, ask_depth = None):
            self._bid = bid
            self._ask = ask
            self._bid_depth = bid_depth
            self._ask_depth = ask_depth

    def add_new_row(self, bid = None, ask = None, bid_depth = None, ask_depth = None):
        new_row = self.GdaxOrderBookInfo(bid, ask, bid_depth, ask_depth)
        if len(self.OrderBookCollection) > 500:
            self.OrderBookCollection.pop(0)
        self.OrderBookCollection.append(new_row)

    def determine_if_sell_or_buy_bids_are_stacked(self):
        last_bid_depth = 0
        last_ask_depth = 0
        if len(self.OrderBookCollection) < 20:
            pass
        else:
            for order_info in self.OrderBookCollection[-20:]:
                if order_info._bid_depth < 3 and order_info._ask_depth < 3:
                    break #nothing to do here, get out and retry on next cycle
                elif order_info._bid_depth > 3 and order_info._ask_depth < 3 and last_ask_depth == 0:
                    last_bid_depth = order_info._bid_depth
                elif order_info._bid_depth < 3 and order_info._ask_depth > 3 and last_bid_depth == 0:
                    last_ask_depth = order_info._ask_depth
                else:
                    break
        if last_ask_depth > 0:
            return BidAskStackType.STACKED_ASK
        elif last_bid_depth > 0:
            return BidAskStackType.STACKED_BID
        return BidAskStackType.NEITHER

class ChangeType(Enum):
    NO_CHANGE = 0
    RISE = 1
    SHARP_RISE = 2
    FALL = 3
    SHARP_FALL = 4

class BidAskStackType(Enum):
    NEITHER = 0
    STACKED_BID = 1
    STACKED_ASK = 2

# class GdaxOrderBookInfo():
#     class OrderInfo():
#         def __init__(self):
#             self.order_id = ''
#             self.size = 0
#             self.price = 0
#             self.side = 'sell'

#     def __init__(self, side = 'sell', price = 0):
#         self.type = SocketType.RECEIVED
#         self.side = side
#         self.price = price
#         self.remaining_size = 0

#     def populate_row(self, row_data):
#         if row_data['type'] == 'done' or row_data['type'] == 'open':
#            self.remaining_size = float(row_data['remaining_size'])
#         elif row_data['type'] == 'received':
#             self.remaining_size += row_data['size']
#         if self.remaining_size == 0:
#             return True
#         return False