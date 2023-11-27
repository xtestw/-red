#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import time
import tushare
import requests

pro = tushare.pro_api('d0b0a50d2b28203748bf441b7dd72dc70b050edb52f8a771db0770ce')

def getAllStockCode() :
    # 拉取数据  
    df = pro.stock_basic(**{
        "ts_code": "",
        "name": "",
        "exchange": "",
        "market": "",
        "is_hs": "",
        "list_status": "",
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "symbol",
        "name",
        "area",
        "industry",
        "market",
        "list_date"
    ])
    return df

def getHistoryData(ts_code):
    df = pro.daily(**{
        "ts_code": ts_code,
        "trade_date": "",
        "start_date": "",
        "end_date": "",
        "offset": "",
        "limit": ""
    }, fields=[
        "ts_code",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "pre_close",
        "change",
        "pct_chg",
        "vol",
        "amount"
    ])
    return df
day_20 = []
day_60 = []
day_120 = []
day_240 = []
history = []
## 计算 近5天成交量
def judgeVol(ts_code, df, rowData):
    cur = 0
    tianshu = 0
    maxT = 0
    for row in df.itertuples():
        if cur == 0:
            cur = getattr(row, 'vol')
            continue
        if getattr(row, 'vol') > cur:
            if (tianshu < 5):
                cur = getattr(row, 'vol')
                maxT = tianshu
            else:
                break
        tianshu = tianshu + 1
    ret = 0
    if (tianshu>360):
        history.append(ts_code + "(" + str(maxT) +","+getattr(rowData, 'industry')+")")
        ret = 360
    elif tianshu>240:
        day_240.append(ts_code + "(" + str(maxT)+","+getattr(rowData, 'industry') +")")
        ret = 240
    elif tianshu>120:
        day_120.append(ts_code + "(" + str(maxT)+","+getattr(rowData, 'industry') +")")
        ret = 120
    elif tianshu>60:
        day_60.append(ts_code + "(" + str(maxT)+","+getattr(rowData, 'industry') +")")
        ret = 60
    elif tianshu>20:
        day_20.append(ts_code + "(" + str(maxT)+","+getattr(rowData, 'industry') +")")
        ret = 20
    return ret

# 计算连板天数
def judgeLianBan(ts_code, df):
    cur = 0
    tianshu = 0
    maxT = 0
    for row in df.itertuples():
        print(row)
        print(getattr(row, 'pct_chg'))
        if (getattr(row, 'pct_chg')>=9.9):
            cur = cur+1
        else:
            break
    return cur
# 计算 A 在120天前-200天之间选择最高价Y，X/Y
def calPriceRatio(ts_code, df):
    listItems = list(df.itertuples())
    cur = getattr(listItems[0], "close")
    print(listItems[0])
    print(cur)
    maxPrice = 0
    for i in range(120, 200):
        if (getattr(listItems[i], 'close')>maxPrice):
            maxPrice = getattr(listItems[i], 'close')
        print(getattr(listItems[i], 'trade_date') +" "+ str(maxPrice) +" " +str(getattr(listItems[i], 'close')))
    return cur / maxPrice

# history = getHistoryData('600178.SH')
# print(len(list(history.itertuples())))
# print(history.itertuples())
# ratio = calPriceRatio(601318,history)
# print(ratio)
# lianban = judgeLianBan('xx',history)
# print(lianban)
# highVolDay = judgeVol('xx', history, row)
# print(highVolDay)
df = getAllStockCode()
cur = int(time.time())
cnt = 0
f = open('./stock_detail.txt', 'w')
content = ''
for row in df.itertuples():
    try:
        history = getHistoryData(getattr(row,'ts_code'))
        # print(history)
        ratio = calPriceRatio(getattr(row,'name'),history)
        highVolDay = judgeVol(getattr(row, 'name'), history, row)
        lianban = judgeLianBan(getattr(row, 'name'),history)
        content = content + getattr(row,'ts_code')+" "+ getattr(row, 'name') + " " + str(highVolDay)+" "+str(lianban)+" "+str(ratio) + "\n"
        cnt = cnt + 1
        if (cnt % 450  == 0):
            print("history")
            print(history)
            print("day_240")
            print(day_240)
            print("day_120")
            print(day_120)
            print("day_60")
            print(day_60)
            print("day_20")
            print(day_20)
            dif = int(time.time()) - cur
            if (dif<60):
                time.sleep(60 - dif)
            cur = int(time.time()) 
            print(cnt)
    except BaseException:
        tb = sys.exc_info()[2]
        print (tb)

f.write(content)
msg = "放量股票代码:\n 历史天量: "
for id in history:
    msg = msg + id + ", "

msg = msg + "\n 240日天量: "
for id in day_240:
    msg = msg + id + ", "
msg = msg + "\n 120日天量: "
for id in day_120:
    msg = msg + id + ", "
msg = msg + "\n 60日天量: "
for id in day_60:
    msg = msg + id + ", "
msg = msg + "\n 20日天量: "
for id in day_20:
    msg = msg + id + ", "

data = {
   "touser" : "@all",
   "toparty" : "",
   "totag" : "",
   "msgtype" : "text",
   "agentid" : 1000002,
   "text" : {
       "content" : msg
   },
   "safe":0,
   "enable_id_trans": 0,
   "enable_duplicate_check": 0,
   "duplicate_check_interval": 1800
}
token = requests.get("https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wwcccce70c1b1aad24&corpsecret=5AbDlpQiu9AFQb9na3DjbvVFe3OBDk9GHJhx8FpCVoU")
print(token.json())
print(token.json()['access_token'])
r = requests.post("https://qyapi.weixin.qq.com/cgi-bin/message/send?debug=1&&access_token="+token.json()['access_token'],json = data)
print(r.json())
