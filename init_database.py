#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
初始化数据库表结构
"""
from database import init_database

if __name__ == '__main__':
    print("开始初始化数据库...")
    init_database()
    print("数据库初始化完成！")


