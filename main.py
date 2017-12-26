from configparser import ConfigParser
import time
import sys
import json
from Logic.coinbase import Coinbase
from Logic.gdax import Gdax
from coinbase.wallet.model import APIObject
from Objects.prices import Prices
from Objects.price import Price
from Logic.algorithm import Algorithm
sys.path.append('C:\Python27\Lib\site-packages\coinbase-python')

def main():
    config = ConfigParser()
    #config.read('coinbase.ini')
    config.read('gdax.ini')
    current_btc_amount = 0
    #coinbase = Coinbase(config)
    algorithm = Algorithm()
    currency_code = 'USD'
    prices = Prices()

    #accounts = coinbase.client.get_accounts()

    #for account in accounts.data:
    #    balance = account.balance
    #    if balance.currency == 'BTC':
    #        current_btc_amount = float(balance.amount)
    #        break

    gdax = Gdax(config)

    #print(gdax.get_product_ticker())    
    #print(gdax.get_product_order_book())
    #print(gdax.get_product_trades())
    print(gdax.get_product_historic_rates())
    #print(gdax.get_product_24hr_stats())
    # coinbase.set_current_btc_amount(current_btc_amount)
    # coinbase_prices = coinbase.client._make_api_object(coinbase.client._get('v2', 'prices', 'BTC-USD', 'historic'), APIObject)
    # prices.assign_prices_from_history(coinbase_prices)
    # temp_price = Price()
    # runs = 1
    # while(1):
    #     price = coinbase.get_current_price(currency_code, prices)
    #     if(price != temp_price):
    #         print('CURRENT VALUE = ${0:.2f}. Current BTC = ${1:.2f}'.format(float(price.amount) * current_btc_amount, float(price.amount)))
    #         algorithm.analyze_last_prices(runs, prices.price_list)
    #         algorithm.analyze_potential_spike(prices.price_list)
    #         print(json.dumps(algorithm, default=lambda o: o.__dict__))
    #         temp_price = price
    #         runs += 1
    #     time.sleep(1)

main()