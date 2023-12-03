#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import time
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
    data['name'] = items[2]
    data['overNum'] = int(items[3])
    data['avgRatio'] = float(items[4])
    bankuaiData[items[0]] = data
print (bankuaiData)
stockWithDataFile = open('./tushare/stock_detail.txt','r')
out = open('./out.csv','w')
result = ""
for line in stockWithDataFile:
    items = line.replace("\n","").split(' ')
    code = items[0].split(".")[0]
    name = items[1].decode('utf-8')
    day = items[2]
    print(line)
    if code in stockWithBankuai:
        print (stockWithBankuai[code])
        for bankuai in stockWithBankuai[code]:
            if bankuai in bankuaiData:
                r = name + ", " + code + ", " + str(day) +", "+ bankuaiData[bankuai]['name'].decode('utf-8') + ", "+ str(bankuaiData[bankuai]['overNum'])
                result = result+r+"\n"
                print(r)
out.write("股票名称,股票代码,多少天内最高量(20/60/120/240),板块名称,板块进3天涨幅超过1.5%天数\n")
out.write(result.encode('utf-8'))


    