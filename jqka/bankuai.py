#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
from requests_html  import HTMLSession
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import json
import sys
# 获取活跃板块信息
chrome_options = Options()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36")

chrome_options.add_experimental_option("useAutomationExtension", False); 
chrome_options.add_experimental_option("excludeSwitches", ['enable-automation']);

chrome_options.add_argument("--disable-blink-features")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# 实例化无界面Chrome浏览器对象
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
})
session = HTMLSession()

def getCode(html):
    soup = BeautifulSoup(html, 'lxml')
    m = soup.find(id ="clid")   
    return m["value"]
def getBankuaiZhangfu(code):
    print(code)
    url = 'https://d.10jqka.com.cn/v4/line/bk_#code/01/last.js'.replace("#code",code)
    print(url)
    r = session.get(url, headers = {
        'sec-ch-ua':'"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"' ,
    'Referer':'https://q.10jqka.com.cn/' ,
    'sec-ch-ua-mobile':'?0' ,
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36' ,
    'sec-ch-ua-platform':'"macOS"'
    })
    rD =eval(r.text.replace("quotebridge_v4_line_bk_#code_01_last(".replace("#code",code),"")[0:-1])
    # rmap = json.loads(rD)
    dailyData = rD['data'].split(";")
    num = 0
    price = ""
    for i in range(-4, -1):
        rate = (float(dailyData[i].split(",")[4]) -float(dailyData[i-1].split(",")[4]))/float(dailyData[i-1].split(",")[4])
        price = price +" "+ dailyData[i].split(",")[4]
        if (rate>= 0.015):
            num = num +1
    avgRate = (float(dailyData[-1].split(",")[4]) -float(dailyData[-4].split(",")[4]))/float(dailyData[-4].split(",")[4]) / 3
    #近三天涨幅>1.5%的天数 平均涨幅 价格
    return str(num) + " " +str(avgRate)+ " " + price


headers_list = [{
                    'Accept': 'text/html, */*; q=0.01',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Connection': 'keep-alive',
                    'Cookie':'log=; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1533992361,1533998469,1533998895,1533998953; Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1533998953; user=MDrAz9H9akQ6Ok5vbmU6NTAwOjQ2OTU0MjIzNDo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxLDQwOzIsMSw0MDszLDEsNDA7NSwxLDQwOzgsMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDEsNDA6Ojo6NDU5NTQyMjM0OjE1MzM5OTkwNzU6OjoxNTMzOTk5MDYwOjg2NDAwOjA6MTZmOGFjOTgwMGNhMjFjZjRkMWZlMjk0NDQ4M2FhNDFkOmRlZmF1bHRfMjox; userid=459542234; u_name=%C0%CF%D1%FDjD; escapename=%25u8001%25u5996jD; ticket=7c92fb758f81dfa4399d0983f7ee5e53; v=Ajz6VIblS6HlDX_9PqmhBV0QDdH4NeBfYtn0Ixa9SCcK4daNPkWw77LpxLZl',
                    'hexin-v': 'AiDRI3i0b1qEZNNemO_FOZlE8SXqKQQBpg9Y4Jox7pbOH8oZQjnUg_YdKIHp',
                    'Host': 'q.10jqka.com.cn',
                    'Referer': 'http://q.10jqka.com.cn/',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
                    },{'Accept': 'text/html, */*; q=0.01', 
                    'Accept-Encoding': 'gzip, deflate, sdch', 
                    'Accept-Language': 'zh-CN,zh;q=0.8', 
                    'Connection': 'keep-alive', 
                    'Cookie': 'user=MDq62tH9NUU6Ok5vbmU6NTAwOjQ2OTU0MjA4MDo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxLDQwOzIsMSw0MDszLDEsNDA7NSwxLDQwOzgsMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDEsNDA6Ojo6NDU5NTQyMDgwOjE1MzM5OTg4OTc6OjoxNTMzOTk4ODgwOjg2NDAwOjA6MTEwOTNhMzBkNTAxMWFlOTg0OWM1MzVjODA2NjQyMThmOmRlZmF1bHRfMjox; userid=459542080; u_name=%BA%DA%D1%FD5E; escapename=%25u9ed1%25u59965E; ticket=658289e5730da881ef99b521b65da6af; log=; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1533992361,1533998469,1533998895,1533998953; Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1533998953; v=AibgksC3Qd-feBV7t0kbK7PCd5e-B2rBPEueJRDPEskkk8xLeJe60Qzb7jDj', 'hexin-v': 'AiDRI3i0b1qEZNNemO_FOZlE8SXqKQQBpg9Y4Jox7pbOH8oZQjnUg_YdKIHp', 
                    'Host': 'q.10jqka.com.cn', 
                    'Referer': 'http://q.10jqka.com.cn/', 
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 
                    },
                    {'Accept': 'text/html, */*; q=0.01', 'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'zh-CN,zh;q=0.8', 'Connection': 'keep-alive', 'Cookie': 'user=MDq62sm9wM%2FR%2FVk6Ok5vbmU6NTAwOjQ2OTU0MTY4MTo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxLDQwOzIsMSw0MDszLDEsNDA7NSwxLDQwOzgsMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDEsNDA6Ojo6NDU5NTQxNjgxOjE1MzM5OTg0NjI6OjoxNTMzOTk4NDYwOjg2NDAwOjA6MTAwNjE5YWExNjc2NDQ2MGE3ZGYxYjgxNDZlNzY3ODIwOmRlZmF1bHRfMjox; userid=459541681; u_name=%BA%DA%C9%BD%C0%CF%D1%FDY; escapename=%25u9ed1%25u5c71%25u8001%25u5996Y; ticket=4def626a5a60cc1d998231d7730d2947; log=; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1533992361,1533998469; Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1533998496; v=AvYwAjBHsS9PCEXLZexL20PSRyfuFzpQjFtutWDf4ll0o5zbyKeKYVzrvsAz', 'hexin-v': 'AiDRI3i0b1qEZNNemO_FOZlE8SXqKQQBpg9Y4Jox7pbOH8oZQjnUg_YdKIHp', 'Host': 'q.10jqka.com.cn', 'Referer': 'http://q.10jqka.com.cn/', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 'X-Requested-With': 'XMLHttpRequest'},
                    {'Accept': 'text/html, */*; q=0.01', 'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'zh-CN,zh;q=0.8', 'Connection': 'keep-alive', 'Cookie': 'Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1533992361; Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1533992361; user=MDq62sm9SnpsOjpOb25lOjUwMDo0Njk1NDE0MTM6NywxMTExMTExMTExMSw0MDs0NCwxMSw0MDs2LDEsNDA7NSwxLDQwOzEsMSw0MDsyLDEsNDA7MywxLDQwOzUsMSw0MDs4LDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAxLDQwOjo6OjQ1OTU0MTQxMzoxNTMzOTk4MjA5Ojo6MTUzMzk5ODE2MDo4NjQwMDowOjFlYTE2YTBjYTU4MGNmYmJlZWJmZWExODQ3ODRjOTAxNDpkZWZhdWx0XzI6MQ%3D%3D; userid=459541413; u_name=%BA%DA%C9%BDJzl; escapename=%25u9ed1%25u5c71Jzl; ticket=b909a4542156f3781a86b8aaefce3007; v=ApheKMKxdxX9FluRdtjNUdGcac08gfwLXuXQj9KJ5FOGbTKxepHMm671oBoh', 'hexin-v': 'AiDRI3i0b1qEZNNemO_FOZlE8SXqKQQBpg9Y4Jox7pbOH8oZQjnUg_YdKIHp', 'Host': 'q.10jqka.com.cn', 'Referer': 'http://q.10jqka.com.cn/', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 'X-Requested-With': 'XMLHttpRequest'},

                    ]
url = "https://q.10jqka.com.cn/gn/"
r = session.get(url,headers = headers_list[0])
f = open('./bankuai.txt', 'w')
content = ''
for item in r.html.find(".cate_items a"):
    try:
        link = item.attrs.get("href")
        # link = 'https://q.10jqka.com.cn/gn/detail/code/301531/'
        driver.get(link)
        time.sleep(2)
        html = driver.page_source
        code = getCode(html)
        linkCode = item.attrs.get("href").split("/")[-2]
        print(code)
        name = item.text
        num = getBankuaiZhangfu(code)
        content = content+ linkCode+ " "+code+ " "+name+" "+str(num) +"\n"
        #板块代码 板块代码 板块名称 近三天涨幅>1.5%的天数 平均涨幅 价格
        print (linkCode+ " "+ code+ " "+name+" "+str(num))
        # break
    except BaseException:
        tb = sys.exc_info()[2]
        print (tb)
f.write(content)
print(content)
