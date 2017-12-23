import sys
sys.path.append('C:\Python27\Lib\site-packages\coinbase-python')

from pprint import pprint
import time
from configparser import ConfigParser
from Objects.prices import Prices
from coinbase.wallet.client import Client

def main():
    config = ConfigParser()
    config.read('coinbase.ini')
    client = Client(config['DEFAULT']['api_key'], config['DEFAULT']['api_secret'])

    currency_code = 'USD'
    last_ten_prices = []
    last_price = 0

    prices = Prices()
    while(1):
        price = client.get_spot_price(currency=currency_code)
        if last_price != price.amount:
            last_price = price.amount
            prices.add_new_price(price.amount)
            temp_prices = prices.get_last_prices(len(prices.price_list))
            print(repr(temp_prices))
            
        time.sleep(1)


main()