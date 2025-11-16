#!/bin/sh
cd data/data_analysis/jqka
# python3 bankuai.py
cd ../tushare
python3 liangjia.py
cd ../../..
python strategy_zhc.py