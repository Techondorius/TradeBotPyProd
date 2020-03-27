import time
import requests

def  sma(prices):
    nums = len(prices)
    return sum(prices) / nums

def vwma(prices, volumes):
    nums = len(prices)
    calc = 0
    top = 0
    bot = 0
    for calc in range(nums):
        top = top + prices[calc] * volumes[calc]
        bot = bot + volumes[calc]
        calc += 1

    return top / bot

def ema(prices):
    nums = len(prices)
    top = sum(prices)

    top += prices[-1]
    nums +=1
    return top / nums

def wma(prices):
    nums = len(prices)
    i = 0
    top = 0
    bot = 0
    for i in range(nums):
        coef = nums - i
        top += coef * prices[i]
        bot = bot + i
        i += 1
    bot = bot + len(prices)
    return top / bot

# def chart(num, ptn, dt):    #1なら終値、2なら出来高
#     list1 = []
#     for i in range(num):
#         for item in response["result"]["1800"]:
#             if item[0] == dt:
#                 if ptn == 1:
#                     list1 += [item[4]]
#                 else:
#                     list1 += [item[5]]

#         dt = dt-1800
#         i += 1
#     return list1

# dt = time.time()
# list1 = chart(52, 1, dt)
# list2 = chart(52, 2, dt)
# print(sma(list1))