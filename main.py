from configparser import ConfigParser
import sys
import json
from Logic.gdax import Gdax
import gdax as gdax_lib
from gdax.order_book import OrderBook
import inspect
import time

def main():
    config = ConfigParser()
    config.read('gdax.ini')
    gdax = Gdax(config)
    try:
        #gdax.start_ticker_update()
        #gdax.start_trades_update()
        #gdax.start_historics_update()
        gdax.start_order_book_poll()
        while True:
            inp = input('Enter anything to quit: ')
            if inp != "" :
                gdax.stop_all_polls()
                break
    except Exception as e:
        print(e)
    finally:
        gdax.stop_all_polls()

main()
