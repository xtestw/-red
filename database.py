#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
数据库连接和表结构定义
"""
from sqlalchemy import create_engine, Column, String, Integer, Float, Date, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import MYSQL_CONFIG
import pymysql

Base = declarative_base()

# 股票基本信息表
class StockBasic(Base):
    __tablename__ = 'stock_basic'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), unique=True, nullable=False, comment='TS代码')
    symbol = Column(String(10), nullable=False, comment='股票代码')
    name = Column(String(50), nullable=False, comment='股票名称')
    area = Column(String(50), comment='地域')
    industry = Column(String(50), comment='所属行业')
    market = Column(String(20), comment='市场类型')
    list_date = Column(String(10), comment='上市日期')
    # stock_company 接口补充字段
    com_name = Column(String(200), comment='公司全称')
    com_id = Column(String(50), comment='统一社会信用代码')
    chairman = Column(String(50), comment='法人代表')
    manager = Column(String(50), comment='总经理')
    secretary = Column(String(50), comment='董秘')
    reg_capital = Column(Float, comment='注册资本(万元)')
    setup_date = Column(String(10), comment='注册日期')
    province = Column(String(50), comment='所在省份')
    city = Column(String(50), comment='所在城市')
    introduction = Column(Text, comment='公司介绍')
    website = Column(String(200), comment='公司主页')
    email = Column(String(100), comment='电子邮件')
    office = Column(String(200), comment='办公室')
    employees = Column(Integer, comment='员工人数')
    main_business = Column(Text, comment='主要业务及产品')
    business_scope = Column(Text, comment='经营范围')
    created_at = Column(DateTime, comment='创建时间')
    updated_at = Column(DateTime, comment='更新时间')
    
    __table_args__ = (
        Index('idx_industry', 'industry'),
        Index('idx_market', 'market'),
    )

# 股票日线数据表
class StockDaily(Base):
    __tablename__ = 'stock_daily'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='TS代码')
    trade_date = Column(String(10), nullable=False, comment='交易日期')
    open = Column(Float, comment='开盘价')
    high = Column(Float, comment='最高价')
    low = Column(Float, comment='最低价')
    close = Column(Float, comment='收盘价')
    pre_close = Column(Float, comment='昨收价')
    change = Column(Float, comment='涨跌额')
    pct_chg = Column(Float, comment='涨跌幅')
    vol = Column(Float, comment='成交量（手）')
    amount = Column(Float, comment='成交额（千元）')
    created_at = Column(DateTime, comment='创建时间')
    
    __table_args__ = (
        Index('idx_ts_code_date', 'ts_code', 'trade_date'),
        Index('idx_trade_date', 'trade_date'),
    )

# 股票周线数据表
class StockWeekly(Base):
    __tablename__ = 'stock_weekly'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='TS代码')
    trade_date = Column(String(10), nullable=False, comment='交易日期')
    open = Column(Float, comment='开盘价')
    high = Column(Float, comment='最高价')
    low = Column(Float, comment='最低价')
    close = Column(Float, comment='收盘价')
    pre_close = Column(Float, comment='昨收价')
    change = Column(Float, comment='涨跌额')
    pct_chg = Column(Float, comment='涨跌幅')
    vol = Column(Float, comment='成交量（手）')
    amount = Column(Float, comment='成交额（千元）')
    created_at = Column(DateTime, comment='创建时间')
    
    __table_args__ = (
        Index('idx_ts_code_date', 'ts_code', 'trade_date'),
    )

# 股票月线数据表
class StockMonthly(Base):
    __tablename__ = 'stock_monthly'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='TS代码')
    trade_date = Column(String(10), nullable=False, comment='交易日期')
    open = Column(Float, comment='开盘价')
    high = Column(Float, comment='最高价')
    low = Column(Float, comment='最低价')
    close = Column(Float, comment='收盘价')
    pre_close = Column(Float, comment='昨收价')
    change = Column(Float, comment='涨跌额')
    pct_chg = Column(Float, comment='涨跌幅')
    vol = Column(Float, comment='成交量（手）')
    amount = Column(Float, comment='成交额（千元）')
    created_at = Column(DateTime, comment='创建时间')
    
    __table_args__ = (
        Index('idx_ts_code_date', 'ts_code', 'trade_date'),
    )

# 股票资金流向表
class StockMoneyflow(Base):
    __tablename__ = 'stock_moneyflow'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='TS代码')
    trade_date = Column(String(10), nullable=False, comment='交易日期')
    buy_sm_amount = Column(Float, comment='小单买入金额（万元）')
    sell_sm_amount = Column(Float, comment='小单卖出金额（万元）')
    buy_md_amount = Column(Float, comment='中单买入金额（万元）')
    sell_md_amount = Column(Float, comment='中单卖出金额（万元）')
    buy_lg_amount = Column(Float, comment='大单买入金额（万元）')
    sell_lg_amount = Column(Float, comment='大单卖出金额（万元）')
    buy_elg_amount = Column(Float, comment='特大单买入金额（万元）')
    sell_elg_amount = Column(Float, comment='特大单卖出金额（万元）')
    net_mf_amount = Column(Float, comment='净流入额（万元）')
    created_at = Column(DateTime, comment='创建时间')
    
    __table_args__ = (
        Index('idx_ts_code_date', 'ts_code', 'trade_date'),
        Index('idx_trade_date', 'trade_date'),
    )

# 股票指标表（市值、市盈率等）
class StockIndicator(Base):
    __tablename__ = 'stock_indicator'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='TS代码')
    trade_date = Column(String(10), nullable=False, comment='交易日期')
    total_mv = Column(Float, comment='总市值（万元）')
    circ_mv = Column(Float, comment='流通市值（万元）')
    pe = Column(Float, comment='市盈率')
    pb = Column(Float, comment='市净率')
    ps = Column(Float, comment='市销率')
    dv_ttm = Column(Float, comment='股息率')
    created_at = Column(DateTime, comment='创建时间')
    
    __table_args__ = (
        Index('idx_ts_code_date', 'ts_code', 'trade_date'),
        Index('idx_trade_date', 'trade_date'),
    )

# 股票收藏表
class StockFavorite(Base):
    __tablename__ = 'stock_favorite'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='TS代码')
    user_id = Column(String(50), default='default', comment='用户ID（预留）')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, comment='创建时间')
    
    __table_args__ = (
        Index('idx_ts_code', 'ts_code'),
        Index('idx_user_id', 'user_id'),
    )

# 选股结果表
class StockSelection(Base):
    __tablename__ = 'stock_selection'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='TS代码')
    strategy_name = Column(String(50), nullable=False, comment='策略名称')
    trade_date = Column(String(10), nullable=False, comment='选股日期')
    score = Column(Float, comment='策略评分')
    reason = Column(Text, comment='选股理由')
    created_at = Column(DateTime, comment='创建时间')
    
    __table_args__ = (
        Index('idx_strategy_date_code', 'strategy_name', 'trade_date', 'ts_code', unique=True),
        Index('idx_strategy_name', 'strategy_name'),
        Index('idx_trade_date', 'trade_date'),
        Index('idx_ts_code', 'ts_code'),
    )

# IPO新股列表表
class StockIPO(Base):
    __tablename__ = 'stock_ipo'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='TS股票代码')
    sub_code = Column(String(20), comment='申购代码')
    name = Column(String(50), nullable=False, comment='名称')
    ipo_date = Column(String(10), comment='上网发行日期')
    issue_date = Column(String(10), comment='上市日期')
    amount = Column(Float, comment='发行总量（万股）')
    market_amount = Column(Float, comment='上网发行总量（万股）')
    price = Column(Float, comment='发行价格')
    pe = Column(Float, comment='市盈率')
    limit_amount = Column(Float, comment='个人申购上限（万股）')
    funds = Column(Float, comment='募集资金（亿元）')
    ballot = Column(Float, comment='中签率')
    created_at = Column(DateTime, comment='创建时间')
    updated_at = Column(DateTime, comment='更新时间')
    
    __table_args__ = (
        Index('idx_ts_code', 'ts_code'),
        Index('idx_ipo_date', 'ipo_date'),
        Index('idx_issue_date', 'issue_date'),
    )


def get_engine():
    """获取数据库引擎（支持配置热重载）"""
    from config import get_mysql_config
    mysql_config = get_mysql_config()
    connection_string = (
        f"mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}"
        f"@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}"
        f"?charset={mysql_config['charset']}"
    )
    return create_engine(connection_string, pool_pre_ping=True, pool_recycle=3600)


def get_session():
    """获取数据库会话"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_database():
    """初始化数据库表"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("数据库表创建成功！")


if __name__ == '__main__':
    init_database()

