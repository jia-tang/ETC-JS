#!/usr/bin/python
# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json

from timeit import default_timer as timer
from datetime import timedelta
# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name = "teamync"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index = 0
prod_exchange_hostname = "production"

port = 25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile("rw", 1)


def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")


def read_from_exchange(exchange):
    return json.loads(exchange.readline())

# ~~~~~============== Helper ==============~~~~~
prod_types = ['BOND', 'VALE', 'VALBZ', 'GS', 'MS', 'WFC', 'XLF']
prod_limits = {}

live_buy_prices = {}
live_sell_prices = {}

live_buy_avg = {}
live_sell_avg = {}

prod_limits["BOND"] = 100
prod_limits['VALE'] = 10
prod_limits['VALBZ'] = 10
prod_limits['GS'] = 100
prod_limits['MS'] = 100
prod_limits['WFC'] = 100
prod_limits['XLF'] = 100


# ~~~~~============== MAIN LOOP ==============~~~~~


def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    
    buy_bond = {"type": "add", "order_id": 1, "symbol": "BOND", "dir": "BUY", "price": 999, "size": 10}
    sell_bond = {"type": "add", "order_id": 2, "symbol": "BOND", "dir": "SELL", "price": 1001, "size": 10}
    cancel_buy = {"type": "cancel", "order_id": 1}
    # write_to_exchange(exchange, buy_bond)
    # write_to_exchange(exchange, sell_bond)
    

    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    
    start = timer()
    while True:
       # if sell and price <= 1k, BUY
        message = read_from_exchange(exchange)
        # if message["type"] == "book" and message["symbol"] == "VALE":
        #     print(message)
        # if message["type"] == "fill" or message["type"] == "VALEBZ": 
        #     print(message)
        
        if message["type"] == "book":
            prod = message["symbol"]

            if 'buy' in message.keys():
                if len(message['buy']) != 0:
                    live_buy_prices[prod] = message['buy'][0][0]
            if 'sell' in message.keys():
                if len(message['sell']) != 0:
                    live_sell_prices[prod] = message['sell'][0][0]

            if "BOND" in live_sell_prices and "GS" in live_sell_prices and "MS" in live_sell_prices and "WFC" in live_sell_prices and "XLF" in live_sell_prices :
                val=1
                others_buy = live_sell_prices["BOND"]*3+live_sell_prices["GS"]*2+live_sell_prices["MS"]*3+live_sell_prices["WFC"]*2
                others_sell = live_buy_prices["BOND"]*3+live_buy_prices["GS"]*2+live_buy_prices["MS"]*3+live_buy_prices["WFC"]*2
                
                XLF_sell = 10 * live_sell_prices["XLF"]
                XLF_buy = 10 * live_buy_prices["XLF"]

                if others_sell < XLF_buy:
                    
                    sell_XLF = {"type": "add", "order_id": 3, "symbol": "XLF", "dir": "SELL", "price": live_buy_prices["XLF"], "size": 10*val}

                    buy_BOND = {"type": "add", "order_id": 4, "symbol": "BOND", "dir": "BUY", "price": live_sell_prices["BOND"], "size": 3*val}
                    buy_GS = {"type": "add", "order_id": 5, "symbol": "GS", "dir": "BUY", "price": live_sell_prices["GS"], "size": 2*val}
                    buy_MS = {"type": "add", "order_id": 6, "symbol": "MS", "dir": "BUY", "price": live_sell_prices["MS"], "size": 3*val}
                    buy_WFC = {"type": "add", "order_id": 7, "symbol": "WFC", "dir": "BUY", "price": live_sell_prices["WFC"], "size": 2*val}

                    write_to_exchange(exchange, sell_XLF)
                    write_to_exchange(exchange, buy_BOND)
                    write_to_exchange(exchange, buy_GS)
                    write_to_exchange(exchange, buy_MS)
                    write_to_exchange(exchange, buy_WFC)

                if others_buy > XLF_sell:
                    
                    buy_XLF = {"type": "add", "order_id": 8, "symbol": "XLF", "dir": "BUY", "price": live_sell_prices["XLF"], "size": 10*val}

                    sell_BOND = {"type": "add", "order_id": 9, "symbol": "BOND", "dir": "SELL", "price": live_buy_prices["BOND"], "size": 3*val}
                    sell_GS = {"type": "add", "order_id": 10, "symbol": "GS", "dir": "SELL", "price": live_buy_prices["GS"], "size": 2*val}
                    sell_MS = {"type": "add", "order_id": 11, "symbol": "MS", "dir": "SELL", "price": live_buy_prices["MS"], "size": 3*val}
                    sell_WFC = {"type": "add", "order_id": 12, "symbol": "WFC", "dir": "SELL", "price": live_buy_prices["WFC"], "size": 2*val}

                    write_to_exchange(exchange, buy_XLF)
                    write_to_exchange(exchange, sell_BOND)
                    write_to_exchange(exchange, sell_GS)
                    write_to_exchange(exchange, sell_MS)
                    write_to_exchange(exchange, sell_WFC)
                

                # else:

                #     buy_XLF = {"type": "add", "order_id": 3, "symbol": "VALE", "dir": "BUY", "price": live_buy_prices["XLF"], "size": 10}

                #     sell_BOND = {"type": "add", "order_id": 3, "symbol": "BOND", "dir": "SELL", "price": live_sell_prices["BOND"], "size": 3}
                #     sell_GS = {"type": "add", "order_id": 3, "symbol": "GS", "dir": "SELL", "price": live_sell_prices["GS"], "size": 2}
                #     sell_MS = {"type": "add", "order_id": 3, "symbol": "MS", "dir": "SELL", "price": live_sell_prices["MS"], "size": 3}
                #     sell_WFC = {"type": "add", "order_id": 3, "symbol": "WFC", "dir": "SELL", "price": live_sell_prices["WFC"], "size": 2}

                #     write_to_exchange(exchange, buy_XLF)
                #     write_to_exchange(exchange, sell_BOND)
                #     write_to_exchange(exchange, sell_GS)
                #     write_to_exchange(exchange, sell_MS)
                #     write_to_exchange(exchange, sell_WFC)


            # if "VALE" in live_sell_prices and "VALBZ" in live_sell_prices:
            #     VALE_sell = live_sell_prices["VALE"]
            #     VALE_buy = live_buy_prices["VALE"]
            #     VALBZ_sell = live_sell_prices["VALBZ"]
            #     VALBZ_buy = live_buy_prices["VALBZ"]

            #     if VALE_buy < VALBZ_sell:
            #         buy_VALE = {"type": "add", "order_id": 3, "symbol": "VALE", "dir": "BUY", "price": VALE_buy, "size": 10}
            #         sell_VALBZ = {"type": "add", "order_id": 4, "symbol": "VALBZ", "dir": "SELL", "price": VALBZ_sell, "size": 10}
            #         write_to_exchange(exchange, buy_VALE)
            #         write_to_exchange(exchange, sell_VALBZ)
            #         print("VALE_buy < VALBZ_sell: ", str(VALE_buy - VALBZ_sell))

            #     if VALE_sell < VALBZ_buy:
            #         buy_VALE = {"type": "add", "order_id": 3, "symbol": "VALE", "dir": "BUY", "price": VALE_sell, "size": 10}
            #         sell_VALBZ = {"type": "add", "order_id": 4, "symbol": "VALBZ", "dir": "SELL", "price": VALBZ_buy, "size": 10}
            #         write_to_exchange(exchange, buy_VALE)
            #         write_to_exchange(exchange, sell_VALBZ)
            #         print("VALE_sell < VALBZ_buy: ", str(VALE_sell - VALBZ_buy))



        if message["type"] == "fill": 
            print(message)






    #  now = timer()
    #  if int(timedelta(seconds = now-start)) % 30 == 0:
    #    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    #   # print(type(message))
    #   #  print(message)
        if message["type"] == "close":
            print("The round has ended")
            break


if __name__ == "__main__":
    main()
