#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 获取股票板块信息 

import requests
from requests_html  import HTMLSession
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

url = "https://q.10jqka.com.cn/gn/"

session = HTMLSession()

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
r = session.get(url,headers = headers_list[0])
# print(r.html.find(".cate_items a"))
f = open('./stock.txt', 'w')
content = ""
for item in r.html.find(".cate_items a"):
    code = item.attrs.get("href").split("/")[-2]
    url = "https://q.10jqka.com.cn/gn/detail/field/199112/order/desc/page/#page/ajax/1/code/#code".replace("#code", code)
    print(item.text +" "+item.attrs.get("href") +  " " + code + " " + url)
    name = item.text
    i = 1
    for i in range(2,5):
        pUrl = url.replace("#page", str(i))
        # time.sleep(5)
        print(pUrl)
        print (session.headers)
        if (session.headers.get("Cookie")==''):
            print("empty")
        itemr = session.get(pUrl, headers= {
              'Accept-Language': 'zh-CN,zh;q=0.9' ,
             'Cookie': 'v=A0AtRS4xMUvVB81m2m43eQ9JF8UXySfTxq545rrTDU_une77Ytn0Ixa9SEYJ' ,
             'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'})
        print(itemr.status_code)
        print(itemr.content)
        m = itemr.html.find("tbody tr")    
        print(len(m))     
        for tr in m:
            print (tr.find("td")[1].text + " "+tr.find("td")[2].text)
            content = content + name+ " "+code+" "+ tr.find("td")[1].text + tr.find("td")[2].text +"\n"
        if (len(m)!=10):
            break
        print (itemr.html.find(".page_info")[0].text)
        print (itemr.html.find(".page_info")[0].text.split("/")[-1])
        totalPage = int(itemr.html.find(".page_info")[0].text.split("/")[-1])
        if (i == totalPage):
            break
    break
f.write(content)
    # itemr = session.get(item.attrs.get("href"))
    # print(itemr.content)
    # break