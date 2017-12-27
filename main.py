from configparser import ConfigParser
import sys
from Logic.gdax import Gdax

def main():
    config = ConfigParser()
    config.read('gdax.ini')
    gdax = Gdax(config)
    try:
        gdax.start_ticker_update()
        gdax.start_trades_update()
        gdax.start_historics_update()
        print(gdax.historics)
        while True:
            if input('Enter anything to quit: ') != "":
                gdax.stop_all_polls()
                break
    finally:
        gdax.stop_all_polls()

main()
