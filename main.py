from configparser import ConfigParser
import time
import sys
from Logic.coinbase import Coinbase
from Objects.prices import Prices
from Objects.price import Price
from Logic.algorithm import Algorithm
sys.path.append('C:\Python27\Lib\site-packages\coinbase-python')

def main():
    config = ConfigParser()
    config.read('coinbase.ini')
    current_btc_amount = 0
    coinbase = Coinbase(config)
    algorithm = Algorithm()
    currency_code = 'USD'
    prices = Prices()

    accounts = coinbase.client.get_accounts()

    for account in accounts.data:
        balance = account.balance
        if balance.currency == 'BTC':
            current_btc_amount = float(balance.amount)
            break

    coinbase.set_current_btc_amount(current_btc_amount)
    temp_price = Price()
    while(1):
        price = coinbase.get_current_price(currency_code, prices)
        if(price != temp_price):
            print('CURRENT VALUE = ${0:.2f}. Current BTC = ${1:.2f}'.format(float(price.amount) * current_btc_amount, float(price.amount)))
            algorithm.analyze_last_prices(len(prices.price_list), prices.price_list)
            print('Upward Trend? {0}'.format(algorithm.upward_trend))
            print('Downward Trend? {0}'.format(algorithm.downward_trend))
            algorithm.analyze_potential_spike(prices.price_list)
            print('Spike Detected? {0}'.format(algorithm.spike_detected))

            temp_price = price
        time.sleep(1)


main()