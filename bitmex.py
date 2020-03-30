import datetime
from pprint import pprint
import time
import taliber
import ccxt
import time as sleep
import requests
import configparser

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
        'apiKey': inifile.get('api-info', 'APIkey'),
        'secret': inifile.get('api-info', 'APIsecret'),
        })

    return bitmex


lasttime = 0
create_order = ""
lostcut_id = ""

inifile = configparser.ConfigParser()
inifile.read('config.ini', 'UTF-8')
size = int(inifile.get('trade-info', 'amount'))
lostcut = int(inifile.get('trade-info', 'lostcut'))

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
        if balance == []:
            positionsize = 0
        else:
            positionsize = balance[0]['currentQty']
        currentprice = bitmex().fetch_ticker('BTC/USD')
        currentprice = currentprice['ask']

        try:
            if signal > sma:
                print("L")
                if positionsize < size:    #long

                    #損切キャンセル処理
                    try:
                        print("発注")
                        symbol = "BTC/USD"
                        cancel_order = bitmex().cancel_order(stop_id, symbol)
                    except ccxt.BaseError as e:
                        print("損切なし")


                    ordersize = size - positionsize
                    symbol = 'BTC/USD'
                    type = 'Market'
                    side = 'Buy'
                    create_order = bitmex().create_order(symbol, type, side, ordersize)
                    create_order = create_order["amount"]

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
                else:
                    print("発注不要")
                    create_order = str(positionsize)
            elif signal < sma:
                print("S")
                if positionsize > 0 - size:

                    #損切キャンセル処理
                    try:
                        print("発注")
                        symbol = "BTC/USD"
                        cancel_order = bitmex().cancel_order(stop_id, symbol)
                    except ccxt.BaseError as e:
                        print("損切なし")
                    
                    ordersize = size + positionsize
                    symbol = 'BTC/USD'
                    type = 'Market'
                    side = 'Sell'
                    create_order = bitmex().create_order(symbol, type, side, ordersize)
                    create_order = create_order["amount"]

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
                else:
                    print("発注不要")
                    create_order = str(positionsize)
            print("現在のポジション : " + create_order)

        except ccxt.BaseError as e:
            print("発注失敗")
            time.sleep(20)

    lasttime = dt
