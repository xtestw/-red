#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
从Tushare获取数据并写入MySQL数据库
"""
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
import os
import logging

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_tushare_token
from database import (
    get_session, StockBasic, StockDaily, StockWeekly, StockMonthly,
    StockMoneyflow, StockIndicator, StockIPO
)

# 配置日志
# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志格式
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# 配置日志处理器
handlers = [
    logging.FileHandler(
        os.path.join(LOG_DIR, 'data_fetcher.log'),
        encoding='utf-8',
        mode='a'  # 追加模式
    ),
    logging.StreamHandler()
]

logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    datefmt=date_format,
    handlers=handlers
)

logger = logging.getLogger(__name__)

# 使用函数获取token，支持热重载
def get_pro_api():
    """获取Tushare API对象（支持配置热重载）"""
    return ts.pro_api(get_tushare_token())


def call_tushare_api(api_func, api_name, **kwargs):
    """
    调用Tushare API并记录详细日志
    
    Args:
        api_func: Tushare API函数
        api_name: API名称（用于日志）
        **kwargs: API调用参数
    
    Returns:
        DataFrame: API返回的数据
    """
    start_time = time.time()
    params_str = ', '.join([f"{k}={v}" for k, v in kwargs.items() if v])
    
    logger.info(f"[Tushare API] 开始调用: {api_name}")
    logger.info(f"[Tushare API] 请求参数: {params_str}")
    
    try:
        df = api_func(**kwargs)
        elapsed_time = time.time() - start_time
        
        if df is not None and not df.empty:
            logger.info(f"[Tushare API] 调用成功: {api_name} | 返回数据: {len(df)} 条 | 耗时: {elapsed_time:.2f}秒")
            if len(df) > 0:
                logger.debug(f"[Tushare API] 数据列: {list(df.columns)}")
                # 记录前几条数据示例（仅DEBUG级别）
                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    logger.debug(f"[Tushare API] 数据示例（前3条）:\n{df.head(3).to_string()}")
        else:
            logger.warning(f"[Tushare API] 调用成功但无数据: {api_name} | 耗时: {elapsed_time:.2f}秒")
        
        return df
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"[Tushare API] 调用失败: {api_name} | 错误: {str(e)} | 耗时: {elapsed_time:.2f}秒")
        logger.error(f"[Tushare API] 请求参数: {params_str}")
        raise


def fetch_stock_basic():
    """获取股票基本信息"""
    logger.info("=" * 60)
    logger.info("开始获取股票基本信息")
    print("开始获取股票基本信息...")
    try:
        pro = get_pro_api()
        df = call_tushare_api(
            pro.stock_basic,
            'stock_basic',
            exchange='',
            list_status='L',
            fields='ts_code,symbol,name,area,industry,market,list_date'
        )
        
        session = get_session()
        try:
            for _, row in df.iterrows():
                stock = session.query(StockBasic).filter_by(ts_code=row['ts_code']).first()
                if stock:
                    # 更新现有记录
                    stock.symbol = row['symbol']
                    stock.name = row['name']
                    stock.area = row.get('area', '')
                    stock.industry = row.get('industry', '')
                    stock.market = row.get('market', '')
                    stock.list_date = row.get('list_date', '')
                    stock.updated_at = datetime.now()
                else:
                    # 创建新记录
                    stock = StockBasic(
                        ts_code=row['ts_code'],
                        symbol=row['symbol'],
                        name=row['name'],
                        area=row.get('area', ''),
                        industry=row.get('industry', ''),
                        market=row.get('market', ''),
                        list_date=row.get('list_date', ''),
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    session.add(stock)
            
            session.commit()
            logger.info(f"成功更新 {len(df)} 条股票基本信息到数据库")
            print(f"成功更新 {len(df)} 条股票基本信息")
        except Exception as e:
            session.rollback()
            logger.error(f"保存股票基本信息失败: {e}", exc_info=True)
            print(f"保存股票基本信息失败: {e}")
            raise
        finally:
            session.close()
    except Exception as e:
        logger.error(f"获取股票基本信息失败: {e}", exc_info=True)
        print(f"获取股票基本信息失败: {e}")
        raise


def fetch_stock_company(ts_code=None, exchange=None):
    """
    获取上市公司基本信息（stock_company接口）
    参考: https://tushare.pro/document/2?doc_id=112
    
    Args:
        ts_code: 股票代码，如果为None则获取所有股票
        exchange: 交易所代码，SSE上交所 SZSE深交所 BSE北交所，如果为None则获取所有
    """
    logger.info("=" * 60)
    logger.info(f"开始获取上市公司基本信息 (ts_code={ts_code}, exchange={exchange})")
    logger.info("参考文档: https://tushare.pro/document/2?doc_id=112")
    print("开始获取上市公司基本信息...")
    print("参考文档: https://tushare.pro/document/2?doc_id=112")
    
    session = get_session()
    try:
        # 获取需要更新的股票列表
        if ts_code:
            stocks = session.query(StockBasic).filter_by(ts_code=ts_code).all()
        else:
            # 获取所有股票，优先更新没有公司信息的股票
            stocks = session.query(StockBasic).all()
        
        if not stocks:
            print("没有找到需要更新的股票")
            return
        
        # 按交易所分组处理（stock_company接口支持按交易所批量获取）
        exchanges = ['SSE', 'SZSE', 'BSE'] if not exchange else [exchange]
        
        total_updated = 0
        total_requests = 0
        
        for exch in exchanges:
            try:
                print(f"\n处理 {exch} 交易所...")
                pro = get_pro_api()
                
                # 按交易所批量获取（单次最多4500条）
                df = call_tushare_api(
                    pro.stock_company,
                    f'stock_company (exchange={exch})',
                    exchange=exch,
                    fields='ts_code,com_name,com_id,exchange,chairman,manager,secretary,reg_capital,setup_date,province,city,introduction,website,email,office,employees,main_business,business_scope'
                )
                
                total_requests += 1
                
                if df.empty:
                    print(f"{exch} 交易所没有数据")
                    continue
                
                print(f"{exch} 交易所获取到 {len(df)} 条公司信息")
                
                # 更新数据库
                for _, row in df.iterrows():
                    stock = session.query(StockBasic).filter_by(ts_code=row['ts_code']).first()
                    if stock:
                        # 更新公司信息字段
                        stock.com_name = row.get('com_name', '') if pd.notna(row.get('com_name')) else None
                        stock.com_id = row.get('com_id', '') if pd.notna(row.get('com_id')) else None
                        stock.chairman = row.get('chairman', '') if pd.notna(row.get('chairman')) else None
                        stock.manager = row.get('manager', '') if pd.notna(row.get('manager')) else None
                        stock.secretary = row.get('secretary', '') if pd.notna(row.get('secretary')) else None
                        stock.reg_capital = float(row.get('reg_capital')) if pd.notna(row.get('reg_capital')) else None
                        stock.setup_date = str(row.get('setup_date', '')) if pd.notna(row.get('setup_date')) else None
                        stock.province = row.get('province', '') if pd.notna(row.get('province')) else None
                        stock.city = row.get('city', '') if pd.notna(row.get('city')) else None
                        stock.introduction = row.get('introduction', '') if pd.notna(row.get('introduction')) else None
                        stock.website = row.get('website', '') if pd.notna(row.get('website')) else None
                        stock.email = row.get('email', '') if pd.notna(row.get('email')) else None
                        stock.office = row.get('office', '') if pd.notna(row.get('office')) else None
                        stock.employees = int(row.get('employees')) if pd.notna(row.get('employees')) else None
                        stock.main_business = row.get('main_business', '') if pd.notna(row.get('main_business')) else None
                        stock.business_scope = row.get('business_scope', '') if pd.notna(row.get('business_scope')) else None
                        stock.updated_at = datetime.now()
                        total_updated += 1
                    else:
                        print(f"警告: 股票 {row['ts_code']} 在 stock_basic 表中不存在，跳过")
                
                session.commit()
                print(f"{exch} 交易所更新完成，共更新 {len(df)} 条记录")
                
                # 控制请求频率（stock_company接口限速较宽松，但也要控制）
                time.sleep(0.5)
                
            except Exception as e:
                print(f"获取 {exch} 交易所公司信息失败: {e}")
                session.rollback()
                continue
        
        logger.info("=" * 60)
        logger.info(f"上市公司基本信息更新完成:")
        logger.info(f"  总请求次数: {total_requests}")
        logger.info(f"  更新记录数: {total_updated}")
        print(f"\n" + "=" * 50)
        print(f"上市公司基本信息更新完成:")
        print(f"  总请求次数: {total_requests}")
        print(f"  更新记录数: {total_updated}")
        print(f"=" * 50)
        
    except Exception as e:
        logger.error(f"获取上市公司基本信息失败: {e}", exc_info=True)
        print(f"获取上市公司基本信息失败: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def fetch_stock_daily(ts_code=None, start_date=None, end_date=None, batch_by_date=False):
    """
    获取股票日线数据
    限速要求：每分钟50次，每次6000条数据
    
    Args:
        ts_code: 股票代码，如果为None则获取所有股票
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD
        batch_by_date: 是否按日期批量获取（不传ts_code，按日期获取所有股票）
                       True: 按日期批量获取，更高效但需要确保每天数据不超过6000条
                       False: 按股票逐个获取（默认）
    """
    if not end_date:
        end_date = datetime.now().strftime('%Y%m%d')
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
    
    logger.info("=" * 60)
    logger.info(f"开始获取日线数据: {ts_code or '全部股票'}, {start_date} 至 {end_date}")
    logger.info(f"限速策略: 每分钟最多50次请求，每次最多6000条数据")
    logger.info(f"获取模式: {'按日期批量获取' if batch_by_date and not ts_code else '按股票逐个获取'}")
    print(f"开始获取日线数据: {ts_code or '全部股票'}, {start_date} 至 {end_date}")
    print(f"限速策略: 每分钟最多50次请求，每次最多6000条数据")
    print(f"获取模式: {'按日期批量获取' if batch_by_date and not ts_code else '按股票逐个获取'}")
    
    session = get_session()
    try:
        # 限速控制：每分钟50次 = 每次请求间隔约 60/50 = 1.2秒
        # 为了安全，设置为1.3秒，每分钟约46次
        REQUEST_INTERVAL = 1.3  # 秒
        MAX_REQUESTS_PER_MINUTE = 50
        MAX_RECORDS_PER_REQUEST = 6000
        
        # 请求计数器（用于每分钟重置）
        request_count = 0
        minute_start_time = time.time()
        
        total_count = 0
        total_requests = 0
        
        if batch_by_date and not ts_code:
            # 按日期批量获取模式（更高效）
            print("使用按日期批量获取模式...")
            current_date = datetime.strptime(start_date, '%Y%m%d')
            end_dt = datetime.strptime(end_date, '%Y%m%d')
            
            while current_date <= end_dt:
                trade_date = current_date.strftime('%Y%m%d')
                
                # 检查是否需要等待（每分钟50次限制）
                current_time = time.time()
                elapsed = current_time - minute_start_time
                
                if elapsed >= 60:
                    request_count = 0
                    minute_start_time = current_time
                    print(f"限速窗口重置，当前日期: {trade_date}")
                elif request_count >= MAX_REQUESTS_PER_MINUTE:
                    wait_time = 60 - elapsed + 1
                    logger.warning(f"达到每分钟请求限制({MAX_REQUESTS_PER_MINUTE}次)，等待 {wait_time:.1f} 秒...")
                    print(f"达到每分钟请求限制({MAX_REQUESTS_PER_MINUTE}次)，等待 {wait_time:.1f} 秒...")
                    time.sleep(wait_time)
                    request_count = 0
                    minute_start_time = time.time()
                    logger.info("限速等待完成，继续请求")
                
                try:
                    pro = get_pro_api()
                    df = call_tushare_api(
                        pro.daily,
                        f'daily (trade_date={trade_date})',
                        trade_date=trade_date,  # 按日期获取所有股票
                        fields='ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount'
                    )
                    
                    request_count += 1
                    total_requests += 1
                    
                    if df.empty:
                        time.sleep(REQUEST_INTERVAL)
                        current_date += timedelta(days=1)
                        continue
                    
                    # 检查返回数据量
                    if len(df) > MAX_RECORDS_PER_REQUEST:
                        print(f"警告: {trade_date} 返回 {len(df)} 条数据，超过单次限制 {MAX_RECORDS_PER_REQUEST} 条")
                        print(f"建议：该日期数据量较大，可能需要分批获取")
                    
                    # 批量插入数据
                    new_records = []
                    for _, row in df.iterrows():
                        daily = session.query(StockDaily).filter_by(
                            ts_code=row['ts_code'],
                            trade_date=row['trade_date']
                        ).first()
                        
                        if not daily:
                            daily = StockDaily(
                                ts_code=row['ts_code'],
                                trade_date=row['trade_date'],
                                open=row.get('open'),
                                high=row.get('high'),
                                low=row.get('low'),
                                close=row.get('close'),
                                pre_close=row.get('pre_close'),
                                change=row.get('change'),
                                pct_chg=row.get('pct_chg'),
                                vol=row.get('vol'),
                                amount=row.get('amount'),
                                created_at=datetime.now()
                            )
                            new_records.append(daily)
                            total_count += 1
                    
                    if new_records:
                        session.add_all(new_records)
                        session.commit()
                        print(f"[{trade_date}] 新增 {len(new_records)} 条数据 (共 {len(df)} 条)")
                    
                    time.sleep(REQUEST_INTERVAL)
                    current_date += timedelta(days=1)
                    
                except Exception as e:
                    print(f"获取 {trade_date} 日线数据失败: {e}")
                    session.rollback()
                    time.sleep(REQUEST_INTERVAL)
                    current_date += timedelta(days=1)
                    continue
        else:
            # 按股票逐个获取模式（原有逻辑）
            if ts_code:
                codes = [ts_code]
            else:
                stocks = session.query(StockBasic).all()
                codes = [stock.ts_code for stock in stocks]
            
            for i, code in enumerate(codes):
                try:
                    # 检查是否需要等待（每分钟50次限制）
                    current_time = time.time()
                    elapsed = current_time - minute_start_time
                    
                    if elapsed >= 60:
                        # 重置计数器
                        request_count = 0
                        minute_start_time = current_time
                        print(f"限速窗口重置，已处理 {i}/{len(codes)} 个股票")
                    elif request_count >= MAX_REQUESTS_PER_MINUTE:
                        # 等待到下一分钟
                        wait_time = 60 - elapsed + 1
                        logger.warning(f"达到每分钟请求限制({MAX_REQUESTS_PER_MINUTE}次)，等待 {wait_time:.1f} 秒...")
                        print(f"达到每分钟请求限制({MAX_REQUESTS_PER_MINUTE}次)，等待 {wait_time:.1f} 秒...")
                        time.sleep(wait_time)
                        request_count = 0
                        minute_start_time = time.time()
                        logger.info("限速等待完成，继续请求")
                    
                    pro = get_pro_api()
                    df = call_tushare_api(
                        pro.daily,
                        f'daily (ts_code={code})',
                        ts_code=code,
                        start_date=start_date,
                        end_date=end_date,
                        fields='ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount'
                    )
                    
                    request_count += 1
                    total_requests += 1
                    
                    if df.empty:
                        # 即使没有数据，也要等待间隔
                        time.sleep(REQUEST_INTERVAL)
                        continue
                    
                    # 检查返回数据量
                    if len(df) > MAX_RECORDS_PER_REQUEST:
                        print(f"警告: {code} 返回 {len(df)} 条数据，超过单次限制 {MAX_RECORDS_PER_REQUEST} 条")
                    
                    # 批量插入数据
                    new_records = []
                    for _, row in df.iterrows():
                        daily = session.query(StockDaily).filter_by(
                            ts_code=row['ts_code'],
                            trade_date=row['trade_date']
                        ).first()
                        
                        if not daily:
                            daily = StockDaily(
                                ts_code=row['ts_code'],
                                trade_date=row['trade_date'],
                                open=row.get('open'),
                                high=row.get('high'),
                                low=row.get('low'),
                                close=row.get('close'),
                                pre_close=row.get('pre_close'),
                                change=row.get('change'),
                                pct_chg=row.get('pct_chg'),
                                vol=row.get('vol'),
                                amount=row.get('amount'),
                                created_at=datetime.now()
                            )
                            new_records.append(daily)
                            total_count += 1
                    
                    if new_records:
                        session.add_all(new_records)
                        session.commit()
                        print(f"[{i+1}/{len(codes)}] {code}: 新增 {len(new_records)} 条数据")
                    
                    # 控制请求频率
                    time.sleep(REQUEST_INTERVAL)
                        
                except Exception as e:
                    print(f"获取 {code} 日线数据失败: {e}")
                    session.rollback()
                    # 即使失败也要等待，避免过快重试
                    time.sleep(REQUEST_INTERVAL)
                    continue
        
        logger.info("=" * 60)
        logger.info(f"日线数据获取完成:")
        logger.info(f"  总请求次数: {total_requests}")
        logger.info(f"  新增数据条数: {total_count}")
        print(f"=" * 50)
        print(f"日线数据获取完成:")
        print(f"  总请求次数: {total_requests}")
        print(f"  新增数据条数: {total_count}")
        print(f"=" * 50)
    finally:
        session.close()


def fetch_stock_weekly(ts_code=None, start_date=None, end_date=None):
    """获取股票周线数据"""
    if not end_date:
        end_date = datetime.now().strftime('%Y%m%d')
    if not start_date:
        start_date = (datetime.now() - timedelta(days=730)).strftime('%Y%m%d')
    
    print(f"开始获取周线数据: {ts_code or '全部股票'}, {start_date} 至 {end_date}")
    
    session = get_session()
    try:
        if ts_code:
            codes = [ts_code]
        else:
            stocks = session.query(StockBasic).all()
            codes = [stock.ts_code for stock in stocks]
        
        total_count = 0
        for i, code in enumerate(codes):
            try:
                pro = get_pro_api()
                df = call_tushare_api(
                    pro.weekly,
                    f'weekly (ts_code={code})',
                    ts_code=code,
                    start_date=start_date,
                    end_date=end_date,
                    fields='ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount'
                )
                
                if df.empty:
                    continue
                
                for _, row in df.iterrows():
                    weekly = session.query(StockWeekly).filter_by(
                        ts_code=row['ts_code'],
                        trade_date=row['trade_date']
                    ).first()
                    
                    if not weekly:
                        weekly = StockWeekly(
                            ts_code=row['ts_code'],
                            trade_date=row['trade_date'],
                            open=row.get('open'),
                            high=row.get('high'),
                            low=row.get('low'),
                            close=row.get('close'),
                            pre_close=row.get('pre_close'),
                            change=row.get('change'),
                            pct_chg=row.get('pct_chg'),
                            vol=row.get('vol'),
                            amount=row.get('amount'),
                            created_at=datetime.now()
                        )
                        session.add(weekly)
                        total_count += 1
                
                session.commit()
                
                if (i + 1) % 200 == 0:
                    print(f"已处理 {i + 1}/{len(codes)} 个股票，暂停60秒...")
                    time.sleep(60)
                else:
                    time.sleep(0.2)
                    
            except Exception as e:
                print(f"获取 {code} 周线数据失败: {e}")
                session.rollback()
                continue
        
        print(f"成功获取 {total_count} 条周线数据")
    finally:
        session.close()


def fetch_stock_monthly(ts_code=None, start_date=None, end_date=None):
    """获取股票月线数据"""
    if not end_date:
        end_date = datetime.now().strftime('%Y%m%d')
    if not start_date:
        start_date = (datetime.now() - timedelta(days=3650)).strftime('%Y%m%d')
    
    print(f"开始获取月线数据: {ts_code or '全部股票'}, {start_date} 至 {end_date}")
    
    session = get_session()
    try:
        if ts_code:
            codes = [ts_code]
        else:
            stocks = session.query(StockBasic).all()
            codes = [stock.ts_code for stock in stocks]
        
        total_count = 0
        for i, code in enumerate(codes):
            try:
                pro = get_pro_api()
                df = call_tushare_api(
                    pro.monthly,
                    f'monthly (ts_code={code})',
                    ts_code=code,
                    start_date=start_date,
                    end_date=end_date,
                    fields='ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount'
                )
                
                if df.empty:
                    continue
                
                for _, row in df.iterrows():
                    monthly = session.query(StockMonthly).filter_by(
                        ts_code=row['ts_code'],
                        trade_date=row['trade_date']
                    ).first()
                    
                    if not monthly:
                        monthly = StockMonthly(
                            ts_code=row['ts_code'],
                            trade_date=row['trade_date'],
                            open=row.get('open'),
                            high=row.get('high'),
                            low=row.get('low'),
                            close=row.get('close'),
                            pre_close=row.get('pre_close'),
                            change=row.get('change'),
                            pct_chg=row.get('pct_chg'),
                            vol=row.get('vol'),
                            amount=row.get('amount'),
                            created_at=datetime.now()
                        )
                        session.add(monthly)
                        total_count += 1
                
                session.commit()
                
                if (i + 1) % 200 == 0:
                    print(f"已处理 {i + 1}/{len(codes)} 个股票，暂停60秒...")
                    time.sleep(60)
                else:
                    time.sleep(0.2)
                    
            except Exception as e:
                print(f"获取 {code} 月线数据失败: {e}")
                session.rollback()
                continue
        
        print(f"成功获取 {total_count} 条月线数据")
    finally:
        session.close()


def fetch_stock_moneyflow(ts_code=None, start_date=None, end_date=None):
    """获取股票资金流向数据"""
    if not end_date:
        end_date = datetime.now().strftime('%Y%m%d')
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
    
    print(f"开始获取资金流向数据: {ts_code or '全部股票'}, {start_date} 至 {end_date}")
    
    session = get_session()
    try:
        if ts_code:
            codes = [ts_code]
        else:
            stocks = session.query(StockBasic).all()
            codes = [stock.ts_code for stock in stocks]
        
        total_count = 0
        for i, code in enumerate(codes):
            try:
                pro = get_pro_api()
                df = call_tushare_api(
                    pro.moneyflow,
                    f'moneyflow (ts_code={code})',
                    ts_code=code,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if df.empty:
                    continue
                
                for _, row in df.iterrows():
                    moneyflow = session.query(StockMoneyflow).filter_by(
                        ts_code=row['ts_code'],
                        trade_date=row['trade_date']
                    ).first()
                    
                    if not moneyflow:
                        moneyflow = StockMoneyflow(
                            ts_code=row['ts_code'],
                            trade_date=row['trade_date'],
                            buy_sm_amount=row.get('buy_sm_amount'),
                            sell_sm_amount=row.get('sell_sm_amount'),
                            buy_md_amount=row.get('buy_md_amount'),
                            sell_md_amount=row.get('sell_md_amount'),
                            buy_lg_amount=row.get('buy_lg_amount'),
                            sell_lg_amount=row.get('sell_lg_amount'),
                            buy_elg_amount=row.get('buy_elg_amount'),
                            sell_elg_amount=row.get('sell_elg_amount'),
                            net_mf_amount=row.get('net_mf_amount'),
                            created_at=datetime.now()
                        )
                        session.add(moneyflow)
                        total_count += 1
                
                session.commit()
                
                if (i + 1) % 200 == 0:
                    print(f"已处理 {i + 1}/{len(codes)} 个股票，暂停60秒...")
                    time.sleep(60)
                else:
                    time.sleep(0.2)
                    
            except Exception as e:
                print(f"获取 {code} 资金流向数据失败: {e}")
                session.rollback()
                continue
        
        print(f"成功获取 {total_count} 条资金流向数据")
    finally:
        session.close()


def fetch_stock_indicator(ts_code=None, start_date=None, end_date=None):
    """获取股票指标数据（市值、市盈率等）"""
    if not end_date:
        end_date = datetime.now().strftime('%Y%m%d')
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
    
    print(f"开始获取股票指标数据: {ts_code or '全部股票'}, {start_date} 至 {end_date}")
    
    session = get_session()
    try:
        if ts_code:
            codes = [ts_code]
        else:
            stocks = session.query(StockBasic).all()
            codes = [stock.ts_code for stock in stocks]
        
        total_count = 0
        for i, code in enumerate(codes):
            try:
                pro = get_pro_api()
                df = call_tushare_api(
                    pro.daily_basic,
                    f'daily_basic (ts_code={code})',
                    ts_code=code,
                    start_date=start_date,
                    end_date=end_date,
                    fields='ts_code,trade_date,total_mv,circ_mv,pe,pb,ps,dv_ttm'
                )
                
                if df.empty:
                    continue
                
                for _, row in df.iterrows():
                    indicator = session.query(StockIndicator).filter_by(
                        ts_code=row['ts_code'],
                        trade_date=row['trade_date']
                    ).first()
                    
                    if not indicator:
                        indicator = StockIndicator(
                            ts_code=row['ts_code'],
                            trade_date=row['trade_date'],
                            total_mv=row.get('total_mv'),
                            circ_mv=row.get('circ_mv'),
                            pe=row.get('pe'),
                            pb=row.get('pb'),
                            ps=row.get('ps'),
                            dv_ttm=row.get('dv_ttm'),
                            created_at=datetime.now()
                        )
                        session.add(indicator)
                        total_count += 1
                
                session.commit()
                
                if (i + 1) % 200 == 0:
                    print(f"已处理 {i + 1}/{len(codes)} 个股票，暂停60秒...")
                    time.sleep(60)
                else:
                    time.sleep(0.2)
                    
            except Exception as e:
                print(f"获取 {code} 指标数据失败: {e}")
                session.rollback()
                continue
        
        print(f"成功获取 {total_count} 条指标数据")
    finally:
        session.close()


def fetch_ipo_stocks(start_date=None, end_date=None):
    """
    获取IPO新股列表数据
    参考: https://tushare.pro/document/2?doc_id=123
    
    Args:
        start_date: 上网发行开始日期，格式YYYYMMDD，如果为None则获取最近一年
        end_date: 上网发行结束日期，格式YYYYMMDD，如果为None则为今天
    """
    if not end_date:
        end_date = datetime.now().strftime('%Y%m%d')
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
    
    logger.info(f"开始获取IPO新股列表数据: {start_date} 至 {end_date}")
    logger.info("参考文档: https://tushare.pro/document/2?doc_id=123")
    
    try:
        pro = get_pro_api()
        logger.info(f"调用Tushare API: new_share(start_date={start_date}, end_date={end_date})")
        start_time = time.time()
        df = pro.new_share(start_date=start_date, end_date=end_date)
        elapsed_time = time.time() - start_time
        logger.info(f"Tushare API调用完成，耗时: {elapsed_time:.2f}秒，返回 {len(df)} 条数据")
        
        if df.empty:
            logger.warning("没有获取到IPO数据")
            return
        
        session = get_session()
        try:
            total_updated = 0
            total_inserted = 0
            
            for _, row in df.iterrows():
                # 检查是否已存在
                existing = session.query(StockIPO).filter_by(ts_code=row['ts_code']).first()
                
                if existing:
                    # 更新现有记录
                    existing.sub_code = row.get('sub_code', '') if pd.notna(row.get('sub_code')) else None
                    existing.name = row.get('name', '')
                    existing.ipo_date = str(row.get('ipo_date', '')) if pd.notna(row.get('ipo_date')) else None
                    existing.issue_date = str(row.get('issue_date', '')) if pd.notna(row.get('issue_date')) else None
                    existing.amount = float(row.get('amount')) if pd.notna(row.get('amount')) else None
                    existing.market_amount = float(row.get('market_amount')) if pd.notna(row.get('market_amount')) else None
                    existing.price = float(row.get('price')) if pd.notna(row.get('price')) else None
                    existing.pe = float(row.get('pe')) if pd.notna(row.get('pe')) else None
                    existing.limit_amount = float(row.get('limit_amount')) if pd.notna(row.get('limit_amount')) else None
                    existing.funds = float(row.get('funds')) if pd.notna(row.get('funds')) else None
                    existing.ballot = float(row.get('ballot')) if pd.notna(row.get('ballot')) else None
                    existing.updated_at = datetime.now()
                    total_updated += 1
                else:
                    # 创建新记录
                    ipo = StockIPO(
                        ts_code=row['ts_code'],
                        sub_code=row.get('sub_code', '') if pd.notna(row.get('sub_code')) else None,
                        name=row.get('name', ''),
                        ipo_date=str(row.get('ipo_date', '')) if pd.notna(row.get('ipo_date')) else None,
                        issue_date=str(row.get('issue_date', '')) if pd.notna(row.get('issue_date')) else None,
                        amount=float(row.get('amount')) if pd.notna(row.get('amount')) else None,
                        market_amount=float(row.get('market_amount')) if pd.notna(row.get('market_amount')) else None,
                        price=float(row.get('price')) if pd.notna(row.get('price')) else None,
                        pe=float(row.get('pe')) if pd.notna(row.get('pe')) else None,
                        limit_amount=float(row.get('limit_amount')) if pd.notna(row.get('limit_amount')) else None,
                        funds=float(row.get('funds')) if pd.notna(row.get('funds')) else None,
                        ballot=float(row.get('ballot')) if pd.notna(row.get('ballot')) else None,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    session.add(ipo)
                    total_inserted += 1
            
            session.commit()
            logger.info(f"成功处理 {len(df)} 条IPO数据: 新增 {total_inserted} 条，更新 {total_updated} 条")
        except Exception as e:
            session.rollback()
            logger.error(f"保存IPO数据失败: {e}", exc_info=True)
            raise
        finally:
            session.close()
    except Exception as e:
        logger.error(f"获取IPO数据失败: {e}", exc_info=True)
        raise


def fetch_all_data():
    """获取所有数据（首次运行使用）"""
    print("=" * 50)
    print("开始获取所有股票数据")
    print("=" * 50)
    
    # 1. 获取股票基本信息
    fetch_stock_basic()
    
    # 2. 获取日线数据（最近一年）
    fetch_stock_daily()
    
    # 3. 获取周线数据（最近两年）
    fetch_stock_weekly()
    
    # 4. 获取月线数据（最近十年）
    fetch_stock_monthly()
    
    # 5. 获取资金流向数据（最近一个月）
    fetch_stock_moneyflow()
    
    # 6. 获取指标数据（最近一个月）
    fetch_stock_indicator()
    
    # 7. 获取IPO新股数据（最近一年）
    fetch_ipo_stocks()
    
    print("=" * 50)
    print("所有数据获取完成！")
    print("=" * 50)


if __name__ == '__main__':
    # 可以单独测试某个功能
    # fetch_stock_basic()
    # fetch_stock_daily()
    fetch_all_data()

