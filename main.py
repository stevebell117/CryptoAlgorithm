from configparser import ConfigParser
import sys
import json
from Logic.gdax import Gdax
from gdax_lib.order_book import OrderBook
import inspect
import time
import datetime as dt
import traceback

def floatTryParse(value):
    try:
        return float(value), True
    except ValueError:
        return value, False

def main():
    config = ConfigParser()
    config.read('gdax.ini')
    gdax = Gdax(config)
    try:
        gdax.start_historics_update()
        gdax.start_order_book_poll()
        while True:
            inp = input('Enter an alpha value to quit: ')
            if inp != "":
                float_value, bool_value = floatTryParse(inp)
                if bool_value is True:
                    gdax.update_algorithm_previous_amount(float_value)
                else:
                    gdax.stop_all_polls()
                    break                
    except:
        print(traceback.format_exc())
    finally:
        gdax.stop_all_polls()

main()
