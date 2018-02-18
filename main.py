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
        gdax.start_order_book_poll()
        while True:
            inp = input('Enter an alpha value to quit: ')
            side = 'sell'
            value = inp
            if inp != "":
                if inp[len(inp)-1].isalpha():
                    if inp[len(inp)-1] == 'b':
                        side = 'buy'
                        value = inp[0:len(inp)-2]
                float_value, bool_value = floatTryParse(value)
                if bool_value is True:
                    gdax.override_order(float_value, side)
                else:
                    gdax.stop_all_polls()
                    break                
    except:
        print(traceback.format_exc())
    finally:
        gdax.stop_all_polls()

main()
