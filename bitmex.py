import datetime
from pprint import pprint
import time
import taliber
import ccxt
import time as sleep
import requests
import discord_notify as noot
import config

apikey = config.apikey
secret = config.secret
positionsize = config.positionsize
lostcut = config.lostcut / 100

def chart(num, ptn, dt):    #1なら終値、2なら出来高
    list1 = []
    for i in range(num):
        for item in response["result"]["1800"]:
            if item[0] == dt:
                if ptn == 1:
                    list1 += [item[4]]
                else:
                    list1 += [item[5]]

        dt = dt-1800
        i += 1
    return list1

def bitmex():
    bitmex = ccxt.bitmex({
        'apiKey': apikey,
        'secret': secret
        })
      
    return bitmex


lasttime = 0
create_order = ""
stop_id = ''

while True:
    dt = time.time()
    dt = dt - dt % 1800
    i = 0

    list1 = []
    list2 = []

    if lasttime != dt:
        response = requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc?periods=1800")
        response = response.json()
        list1 = chart(50, 1, dt)
        sma = taliber.sma(list1)
        print(sma)

        list1 = chart(63, 1, dt)
        list2 = chart(63, 2, dt)
        vwma = taliber.vwma(list1, list2)

        list1 = chart(52, 1, dt)
        ema = taliber.ema(list1)

        list1 = chart(68, 1, dt)
        wma = taliber.wma(list1)

        signal = ( vwma + ema + wma ) / 3
        print(signal)


        balance = bitmex().private_get_position()
        positionsize = balance[0]['currentQty']
        currentprice = bitmex().fetch_ticker('BTC/USD')
        currentprice = currentprice['ask']

        try:
            if signal > sma and positionsize < positionsize:
                symbol = "BTC/USD"
                cancel_order = bitmex().cancel_order(stop_id, symbol)

                ordersize = positionsize - positionsize
                symbol = 'BTC/USD'
                type = 'Market'
                side = 'Buy'
                create_order = bitmex().create_order(symbol, type, side, ordersize)

                symbol = "BTC/USD"
                type = "stop" 
                side = "sell"
                amount = positionsize
                price = None
                stop_price = currentprice * (1 - lostcut)
                stop_price = (stop_price // 0.5 + 1 ) / 2
                print(stop_price)
                params = { "stopPx" : stop_price }
                create_order = bitmex().create_order(symbol, type, side, positionsize, price, params)
                stop_id = create_order["id"]
                
            elif signal < sma and positionsize > -positionsize:
                symbol = "BTC/USD"
                cancel_order = bitmex().cancel_order(stop_id, symbol)

                ordersize = positionsize + positionsize
                symbol = 'BTC/USD'
                type = 'Market'
                side = 'Sell'
                create_order = bitmex().create_order(symbol, type, side, ordersize)

                symbol = "BTC/USD"
                type = "stop" 
                side = "buy"
                amount = positionsize
                price = None
                stop_price = currentprice * (1 + lostcut)
                stop_price = (stop_price // 0.5 - 1 ) / 2
                print(stop_price)
                params = { "stopPx" : stop_price }
                create_order = bitmex().create_order(symbol, type, side, positionsize, price, params)
                stop_id = create_order["id"]

            pprint(create_order)
            create_order = ""
            corrateral = bitmex().fetch_balance()['BTC']['total']
            noot.noot(str(float(corrateral) * 1000000) + "BTC")
        except ccxt.BaseError as e:
            print("Failed Post Order : " + str(e))
            time.sleep(20)
        
    lasttime = dt