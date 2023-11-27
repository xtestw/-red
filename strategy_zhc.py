#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import time
import tushare
import requests
stockWithBankuaiFile = open('./jqka/stock.txt', 'r')
# stockWithData = open('./tushare/stock.txt','r')
# stock_code: bankuai_code_List
stockWithBankuai = {}
# bankuai_code: bankuai_name
bankuaiInfo = {}
# bankuai_code: bankuai_data
bankuaiData = {}

for line in stockWithBankuaiFile:
    items = line.replace("\n","").split(' ')
    bankuaiInfo[items[1]] = items[0]
    tp = []
    tp = stockWithBankuai.get(items[2], [])
    # if (stockWithBankuai.has_key(items[3])):
    tp.append(items[1])
    stockWithBankuai[items[2]] = tp
print(bankuaiInfo)
print(stockWithBankuai)

bankuaiWithDataFile = open('./jqka/bankuai.txt','r')
for line in bankuaiWithDataFile:
    items = line.replace("\n","").split(' ')
    data = {}
    data['name'] = items[]
    data['overNum'] = int(items[])
    data['avgRatio'] = float(items[])
    bankuaiData[items[0]] = data

stockWithDataFile = open('','r')
for line in stockWithDataFile:
    