from datetime import datetime
import dateutil.parser
import json

class GdaxTicker():
    def __init__(self):
        self.ticker = list()

    def add_row_to_ticker(self, ticker_row):
        row = GdaxTickerRow()
        row.populate_ticker_row(ticker_row)
        if(len(self.ticker) > 200):
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
            if(len(self.trades) > 200):
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
        self.time = datetime.isoformat(datetime.strptime(trade_object["time"], '%Y-%m-%dT%H:%M:%S.%fZ'))

class GdaxHistoric():
    def __init__(self):
        self.historics = list()

    def add_rows_to_history(self, history_rows):
        for history_row in history_rows:
            row = GdaxHistoricRow()
            row.populate_historic_row(history_row)
            if len(self.historics) > 200:
                self.historics.pop(0)
            if any(x.time == history_row[0] for x in self.historics) is False:
                self.historics.append(row)

class GdaxHistoricRow():
    def __init__(self):
        self.low = 0
        self.high = 0
        self.time = datetime.now()
        self.open = 0
        self.close = 0
        self.volume = 0

    def populate_historic_row(self, trade_object):
        self.time = float(trade_object[0]) #We'll need to just determine seconds by doing 24 * 60 * 60 to determine a day before entry...
        self.low = float(trade_object[1])
        self.high = float(trade_object[2])
        self.open = float(trade_object[3])
        self.close = float(trade_object[4])
        self.volume = float(trade_object[5])
