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
        gdax.start_ticker_update()
        gdax.start_trades_update()
        gdax.start_historics_update()
        while True:
            inp = input('Enter anything to quit, press Enter to update: ')
            if inp != "" :
                gdax.stop_all_polls()
                break
            else:
                order_book = OrderBook()
                order_book.start()                
                time.sleep(10)
                order_book.close()
                
                #gdax.print_historics_sorted()
                #print('*******************************************************\n')
                #gdax.print_trades_sorted()
                #print('*******************************************************\n')
                #gdax.print_tickers_sorted()
    except Exception as e:
        print(e)
    finally:
        gdax.stop_all_polls()

main()

#This gives a active flow of the order feed. Consider implementing this after initial runs (complexity grows immensely with this thing...)
