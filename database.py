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
    # stk_premarket 接口补充字段（每日盘前股本信息）
    total_share = Column(Float, comment='总股本（万股）')
    float_share = Column(Float, comment='流通股本（万股）')
    pre_close = Column(Float, comment='昨日收盘价')
    up_limit = Column(Float, comment='今日涨停价')
    down_limit = Column(Float, comment='今日跌停价')
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
    # 资金流向数据（来自moneyflow接口）
    buy_sm_vol = Column(Float, comment='小单买入量（手）')
    buy_sm_amount = Column(Float, comment='小单买入金额（万元）')
    sell_sm_vol = Column(Float, comment='小单卖出量（手）')
    sell_sm_amount = Column(Float, comment='小单卖出金额（万元）')
    buy_md_vol = Column(Float, comment='中单买入量（手）')
    buy_md_amount = Column(Float, comment='中单买入金额（万元）')
    sell_md_vol = Column(Float, comment='中单卖出量（手）')
    sell_md_amount = Column(Float, comment='中单卖出金额（万元）')
    buy_lg_vol = Column(Float, comment='大单买入量（手）')
    buy_lg_amount = Column(Float, comment='大单买入金额（万元）')
    sell_lg_vol = Column(Float, comment='大单卖出量（手）')
    sell_lg_amount = Column(Float, comment='大单卖出金额（万元）')
    buy_elg_vol = Column(Float, comment='特大单买入量（手）')
    buy_elg_amount = Column(Float, comment='特大单买入金额（万元）')
    sell_elg_vol = Column(Float, comment='特大单卖出量（手）')
    sell_elg_amount = Column(Float, comment='特大单卖出金额（万元）')
    net_mf_amount = Column(Float, comment='净流入额（万元）')
    # 两融数据（来自margin接口）
    rzye = Column(Float, comment='融资余额(元)')
    rqye = Column(Float, comment='融券余量(股)')
    rqyl = Column(Float, comment='融券余额(元)')
    rzrqye = Column(Float, comment='融资融券余额(元)')
    rzmre = Column(Float, comment='融资买入额(元)')
    rqmcl = Column(Float, comment='融券卖出量(股)')
    rzche = Column(Float, comment='融资偿还额(元)')
    rqchl = Column(Float, comment='融券偿还量(股)')
    created_at = Column(DateTime, comment='创建时间')
    
    __table_args__ = (
        Index('idx_ts_code_date', 'ts_code', 'trade_date', unique=True),
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
    user_id = Column(Integer, nullable=True, comment='用户ID')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, comment='创建时间')
    
    __table_args__ = (
        Index('idx_ts_code', 'ts_code'),
        Index('idx_user_id', 'user_id'),
        Index('idx_user_ts_code', 'user_id', 'ts_code', unique=True),
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

# 用户表
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    openid = Column(String(100), unique=True, nullable=False, comment='微信OpenID')
    unionid = Column(String(100), comment='微信UnionID')
    nickname = Column(String(100), comment='昵称')
    avatar = Column(String(500), comment='头像URL')
    gender = Column(Integer, comment='性别：0未知，1男，2女')
    country = Column(String(50), comment='国家')
    province = Column(String(50), comment='省份')
    city = Column(String(50), comment='城市')
    language = Column(String(20), comment='语言')
    created_at = Column(DateTime, comment='创建时间')
    updated_at = Column(DateTime, comment='更新时间')
    last_login_at = Column(DateTime, comment='最后登录时间')
    
    __table_args__ = (
        Index('idx_openid', 'openid'),
        Index('idx_unionid', 'unionid'),
    )

# 用户会话表（用于存储JWT token）
class UserSession(Base):
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, comment='用户ID')
    token = Column(String(500), unique=True, nullable=False, comment='JWT Token')
    refresh_token = Column(String(500), comment='刷新Token')
    expires_at = Column(DateTime, nullable=False, comment='过期时间')
    created_at = Column(DateTime, comment='创建时间')
    last_used_at = Column(DateTime, comment='最后使用时间')
    
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_token', 'token'),
        Index('idx_expires_at', 'expires_at'),
    )

# 上市公司管理层信息表
class StockManager(Base):
    __tablename__ = 'stock_manager'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='TS股票代码')
    ann_date = Column(String(10), comment='公告日期')
    name = Column(String(50), nullable=False, comment='姓名')
    gender = Column(String(10), comment='性别')
    lev = Column(String(50), comment='岗位类别')
    title = Column(String(100), nullable=False, comment='岗位')
    edu = Column(String(50), comment='学历')
    national = Column(String(50), comment='国籍')
    birthday = Column(String(20), comment='出生年月')
    begin_date = Column(String(10), comment='上任日期')
    end_date = Column(String(10), comment='离任日期')
    resume = Column(Text, comment='个人简历')
    # 薪酬和持股信息（来自stk_rewards接口）
    salary = Column(Float, comment='薪酬（万元）')
    hold_vol = Column(Float, comment='持股数量（股）')
    reward_date = Column(String(10), comment='薪酬报告期')
    created_at = Column(DateTime, comment='创建时间')
    updated_at = Column(DateTime, comment='更新时间')
    
    __table_args__ = (
        Index('idx_ts_code', 'ts_code'),
        Index('idx_ann_date', 'ann_date'),
        Index('idx_name', 'name'),
        Index('idx_title', 'title'),
        Index('idx_ts_code_name_title', 'ts_code', 'name', 'title'),
    )

# 上市公司管理层变更历史表（用于记录diff）
class StockManagerChange(Base):
    __tablename__ = 'stock_manager_change'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='TS股票代码')
    change_type = Column(String(20), nullable=False, comment='变更类型：新增/离职/岗位变更/信息更新')
    name = Column(String(50), nullable=False, comment='姓名')
    title = Column(String(100), comment='岗位')
    old_value = Column(Text, comment='旧值（JSON格式）')
    new_value = Column(Text, comment='新值（JSON格式）')
    change_date = Column(String(10), comment='变更日期')
    ann_date = Column(String(10), comment='公告日期')
    created_at = Column(DateTime, comment='创建时间')
    
    __table_args__ = (
        Index('idx_ts_code', 'ts_code'),
        Index('idx_change_type', 'change_type'),
        Index('idx_change_date', 'change_date'),
        Index('idx_created_at', 'created_at'),
    )

# 指数基本信息表
class IndexBasic(Base):
    __tablename__ = 'index_basic'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), unique=True, nullable=False, comment='TS代码')
    name = Column(String(100), nullable=False, comment='简称')
    fullname = Column(String(200), comment='指数全称')
    market = Column(String(20), comment='市场')
    publisher = Column(String(50), comment='发布方')
    index_type = Column(String(50), comment='指数风格')
    category = Column(String(50), comment='指数类别')
    base_date = Column(String(10), comment='基期')
    base_point = Column(Float, comment='基点')
    list_date = Column(String(10), comment='发布日期')
    weight_rule = Column(String(50), comment='加权方式')
    desc = Column(Text, comment='描述')
    exp_date = Column(String(10), comment='终止日期')
    created_at = Column(DateTime, comment='创建时间')
    updated_at = Column(DateTime, comment='更新时间')
    
    __table_args__ = (
        Index('idx_market', 'market'),
        Index('idx_category', 'category'),
        Index('idx_publisher', 'publisher'),
    )

# 指数日线行情表
class IndexDaily(Base):
    __tablename__ = 'index_daily'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='TS代码')
    trade_date = Column(String(10), nullable=False, comment='交易日期')
    close = Column(Float, comment='收盘点位')
    open = Column(Float, comment='开盘点位')
    high = Column(Float, comment='最高点位')
    low = Column(Float, comment='最低点位')
    pre_close = Column(Float, comment='昨收点位')
    change = Column(Float, comment='涨跌点位')
    pct_chg = Column(Float, comment='涨跌幅（%）')
    vol = Column(Float, comment='成交量（手）')
    amount = Column(Float, comment='成交额（千元）')
    # index_dailybasic 接口补充字段
    total_mv = Column(Float, comment='总市值（万元）')
    float_mv = Column(Float, comment='流通市值（万元）')
    turnover_rate = Column(Float, comment='换手率（%）')
    pe = Column(Float, comment='市盈率')
    pb = Column(Float, comment='市净率')
    created_at = Column(DateTime, comment='创建时间')
    
    __table_args__ = (
        Index('idx_ts_code_date', 'ts_code', 'trade_date', unique=True),
        Index('idx_trade_date', 'trade_date'),
        Index('idx_pe', 'pe'),
        Index('idx_pb', 'pb'),
    )

# 指数周线行情表
class IndexWeekly(Base):
    __tablename__ = 'index_weekly'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='TS代码')
    trade_date = Column(String(10), nullable=False, comment='交易日期')
    close = Column(Float, comment='收盘点位')
    open = Column(Float, comment='开盘点位')
    high = Column(Float, comment='最高点位')
    low = Column(Float, comment='最低点位')
    pre_close = Column(Float, comment='昨收点位')
    change = Column(Float, comment='涨跌点位')
    pct_chg = Column(Float, comment='涨跌幅（%）')
    vol = Column(Float, comment='成交量（手）')
    amount = Column(Float, comment='成交额（千元）')
    created_at = Column(DateTime, comment='创建时间')
    
    __table_args__ = (
        Index('idx_ts_code_date', 'ts_code', 'trade_date', unique=True),
        Index('idx_trade_date', 'trade_date'),
    )

# 指数月线行情表
class IndexMonthly(Base):
    __tablename__ = 'index_monthly'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='TS代码')
    trade_date = Column(String(10), nullable=False, comment='交易日期')
    close = Column(Float, comment='收盘点位')
    open = Column(Float, comment='开盘点位')
    high = Column(Float, comment='最高点位')
    low = Column(Float, comment='最低点位')
    pre_close = Column(Float, comment='昨收点位')
    change = Column(Float, comment='涨跌点位')
    pct_chg = Column(Float, comment='涨跌幅（%）')
    vol = Column(Float, comment='成交量（手）')
    amount = Column(Float, comment='成交额（千元）')
    created_at = Column(DateTime, comment='创建时间')
    
    __table_args__ = (
        Index('idx_ts_code_date', 'ts_code', 'trade_date', unique=True),
        Index('idx_trade_date', 'trade_date'),
    )

# 指数成分股权重表
class IndexWeight(Base):
    __tablename__ = 'index_weight'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    index_code = Column(String(20), nullable=False, comment='指数代码')
    con_code = Column(String(20), nullable=False, comment='成分代码（股票代码）')
    trade_date = Column(String(10), nullable=False, comment='交易日期')
    weight = Column(Float, comment='权重')
    created_at = Column(DateTime, comment='创建时间')
    
    __table_args__ = (
        Index('idx_index_code_date', 'index_code', 'trade_date'),
        Index('idx_con_code', 'con_code'),
        Index('idx_trade_date', 'trade_date'),
        Index('idx_index_code_con_code_date', 'index_code', 'con_code', 'trade_date', unique=True),
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

