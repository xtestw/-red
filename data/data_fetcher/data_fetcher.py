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
    StockMoneyflow, StockIndicator, StockIPO, StockManager, StockManagerChange,
    IndexBasic, IndexDaily, IndexWeekly, IndexMonthly, IndexWeight
)


class TusharePermissionError(Exception):
    """Tushare API 权限不足异常"""
    def __init__(self, api_name, error_msg):
        self.api_name = api_name
        self.error_msg = error_msg
        super().__init__(f"接口 {api_name} 权限不足: {error_msg}")

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
        error_msg = str(e)
        error_type = type(e).__name__
        
        # 检查是否是权限错误（Tushare 可能抛出包含 '没有接口访问权限' 或 '权限' 的异常）
        is_permission_error = (
            '没有接口访问权限' in error_msg or 
            '权限' in error_msg or
            '接口访问权限' in error_msg or
            'permission' in error_msg.lower() or
            'access denied' in error_msg.lower()
        )
        
        if is_permission_error:
            logger.warning(f"[Tushare API] 权限不足: {api_name} | 错误类型: {error_type} | 错误: {error_msg} | 耗时: {elapsed_time:.2f}秒")
            logger.warning(f"[Tushare API] 请求参数: {params_str}")
            logger.warning(f"[Tushare API] 提示: 该接口需要更高权限，请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
            # 对于权限错误，抛出异常以停止任务
            raise TusharePermissionError(api_name, error_msg)
        else:
            logger.error(f"[Tushare API] 调用失败: {api_name} | 错误类型: {error_type} | 错误: {error_msg} | 耗时: {elapsed_time:.2f}秒")
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
    except TusharePermissionError as e:
        # 权限不足，停止整个任务
        logger.error(f"接口权限不足，停止股票基本信息获取任务: {e.api_name}")
        logger.error(f"错误信息: {e.error_msg}")
        logger.error(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
        print(f"❌ 接口权限不足，停止股票基本信息获取任务: {e.api_name}")
        print(f"错误信息: {e.error_msg}")
        print(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
        return  # 直接返回，停止任务
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
        # 检查表结构，确定哪些字段存在
        from sqlalchemy import inspect, text
        inspector = inspect(session.bind)
        try:
            columns = [col['name'] for col in inspector.get_columns('stock_basic')]
        except Exception:
            # 如果 inspect 失败，使用原始 SQL 查询
            result = session.execute(text("SHOW COLUMNS FROM stock_basic"))
            columns = [row[0] for row in result]
        
        # 检查是否需要升级数据库（如果缺少公司信息字段）
        required_fields = ['com_name', 'com_id', 'chairman', 'manager', 'secretary']
        missing_fields = [f for f in required_fields if f not in columns]
        
        if missing_fields:
            logger.warning(f"检测到表结构缺少字段: {', '.join(missing_fields)}")
            print(f"\n⚠️  警告: 数据库表 stock_basic 缺少以下字段: {', '.join(missing_fields)}")
            print("   建议执行以下命令升级数据库:")
            print("   python upgrade_database.py")
            print("   或者手动执行: mysql -u root -p stock_data < upgrade_database.sql")
            print("   继续执行，将跳过这些字段的更新...\n")
        
        # 获取需要更新的股票代码列表（只查询 ts_code，避免查询不存在的字段）
        if ts_code:
            stock_codes = [ts_code]
        else:
            # 只查询 ts_code 字段，避免加载所有字段
            stock_codes = [row[0] for row in session.query(StockBasic.ts_code).all()]
        
        if not stock_codes:
            print("没有找到需要更新的股票")
            return
        
        print(f"找到 {len(stock_codes)} 只股票需要更新公司信息")
        
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
                
                # 更新数据库（使用原始 SQL 更新，避免查询不存在的字段）
                from sqlalchemy import text
                
                for _, row in df.iterrows():
                    ts_code_val = row['ts_code']
                    if ts_code_val not in stock_codes:
                        continue
                    
                    # 构建更新 SQL，只更新存在的字段
                    update_fields = []
                    update_values = {}
                    
                    field_mapping = {
                        'com_name': ('com_name', str),
                        'com_id': ('com_id', str),
                        'chairman': ('chairman', str),
                        'manager': ('manager', str),
                        'secretary': ('secretary', str),
                        'reg_capital': ('reg_capital', float),
                        'setup_date': ('setup_date', str),
                        'province': ('province', str),
                        'city': ('city', str),
                        'introduction': ('introduction', str),
                        'website': ('website', str),
                        'email': ('email', str),
                        'office': ('office', str),
                        'employees': ('employees', int),
                        'main_business': ('main_business', str),
                        'business_scope': ('business_scope', str),
                    }
                    
                    for field_key, (db_field, field_type) in field_mapping.items():
                        if db_field in columns:  # 只更新存在的字段
                            value = row.get(field_key)
                            if pd.notna(value):
                                if field_type == float:
                                    update_values[db_field] = float(value)
                                elif field_type == int:
                                    update_values[db_field] = int(value)
                                else:
                                    update_values[db_field] = str(value) if value else None
                                update_fields.append(f"`{db_field}` = :{db_field}")
                            else:
                                update_values[db_field] = None
                                update_fields.append(f"`{db_field}` = NULL")
                    
                    if update_fields:
                        # 添加 updated_at
                        update_fields.append("`updated_at` = NOW()")
                        update_values['ts_code'] = ts_code_val
                        
                        # 执行更新
                        sql = f"UPDATE stock_basic SET {', '.join(update_fields)} WHERE ts_code = :ts_code"
                        session.execute(text(sql), update_values)
                        total_updated += 1
                    else:
                        print(f"警告: 股票 {ts_code_val} 的表结构中没有公司信息字段，请先执行 upgrade_database.sql")
                
                session.commit()
                print(f"{exch} 交易所更新完成，共更新 {len(df)} 条记录")
                
                # 控制请求频率（stock_company接口限速较宽松，但也要控制）
                time.sleep(0.5)
                
            except TusharePermissionError as e:
                # 权限不足，停止整个任务
                logger.error(f"接口权限不足，停止公司信息获取任务: {e.api_name}")
                logger.error(f"错误信息: {e.error_msg}")
                logger.error(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
                print(f"❌ 接口权限不足，停止公司信息获取任务: {e.api_name}")
                print(f"错误信息: {e.error_msg}")
                print(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
                return  # 直接返回，停止任务
            except Exception as e:
                logger.error(f"获取 {exch} 交易所公司信息失败: {e}", exc_info=True)
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


def fetch_stock_premarket(trade_date=None):
    """
    获取每日盘前股本信息（stk_premarket接口）
    参考: https://tushare.pro/document/2?doc_id=329
    
    Args:
        trade_date: 交易日期(YYYYMMDD格式)，如果为None则获取当日数据
    """
    logger.info("=" * 60)
    logger.info(f"开始获取每日盘前股本信息 (trade_date={trade_date})")
    logger.info("参考文档: https://tushare.pro/document/2?doc_id=329")
    print("开始获取每日盘前股本信息...")
    print("参考文档: https://tushare.pro/document/2?doc_id=329")
    
    # 如果没有指定日期，使用当前日期
    if trade_date is None:
        trade_date = datetime.now().strftime('%Y%m%d')
    
    session = get_session()
    try:
        # 检查表结构，确定哪些字段存在
        from sqlalchemy import inspect, text
        inspector = inspect(session.bind)
        try:
            columns = [col['name'] for col in inspector.get_columns('stock_basic')]
        except Exception:
            # 如果 inspect 失败，使用原始 SQL 查询
            result = session.execute(text("SHOW COLUMNS FROM stock_basic"))
            columns = [row[0] for row in result]
        
        # 检查是否需要升级数据库（如果缺少股本信息字段）
        required_fields = ['total_share', 'float_share', 'pre_close', 'up_limit', 'down_limit']
        missing_fields = [f for f in required_fields if f not in columns]
        
        if missing_fields:
            logger.warning(f"检测到表结构缺少字段: {', '.join(missing_fields)}")
            print(f"\n⚠️  警告: 数据库表 stock_basic 缺少以下字段: {', '.join(missing_fields)}")
            print("   建议执行以下命令升级数据库:")
            print("   python upgrade_database.py")
            print("   或者手动执行: mysql -u root -p stock_data < upgrade_database.sql")
            print("   继续执行，将跳过这些字段的更新...\n")
        
        # 调用 Tushare API 获取盘前股本信息
        pro = get_pro_api()
        df = call_tushare_api(
            pro.stk_premarket,
            f'stk_premarket (trade_date={trade_date})',
            trade_date=trade_date
        )
        
        if df.empty:
            print(f"日期 {trade_date} 没有盘前股本数据")
            logger.warning(f"日期 {trade_date} 没有盘前股本数据")
            return
        
        print(f"获取到 {len(df)} 条盘前股本信息")
        logger.info(f"获取到 {len(df)} 条盘前股本信息")
        
        # 更新数据库
        from sqlalchemy import text
        total_updated = 0
        total_skipped = 0
        
        for _, row in df.iterrows():
            ts_code_val = row.get('ts_code')
            if not ts_code_val:
                continue
            
            # 构建更新 SQL，只更新存在的字段
            update_fields = []
            update_values = {}
            
            field_mapping = {
                'total_share': ('total_share', float),
                'float_share': ('float_share', float),
                'pre_close': ('pre_close', float),
                'up_limit': ('up_limit', float),
                'down_limit': ('down_limit', float),
            }
            
            for field_key, (db_field, field_type) in field_mapping.items():
                if db_field in columns:  # 只更新存在的字段
                    value = row.get(field_key)
                    if pd.notna(value) and value is not None:
                        try:
                            if field_type == float:
                                update_values[db_field] = float(value)
                            else:
                                update_values[db_field] = str(value) if value else None
                            update_fields.append(f"`{db_field}` = :{db_field}")
                        except (ValueError, TypeError):
                            # 如果转换失败，跳过该字段
                            logger.debug(f"字段 {db_field} 值转换失败: {value}")
                    else:
                        # 如果值为 None 或 NaN，设置为 NULL
                        update_fields.append(f"`{db_field}` = NULL")
            
            if update_fields:
                # 添加 updated_at
                update_fields.append("`updated_at` = NOW()")
                update_values['ts_code'] = ts_code_val
                
                # 执行更新
                sql = f"UPDATE stock_basic SET {', '.join(update_fields)} WHERE ts_code = :ts_code"
                try:
                    result = session.execute(text(sql), update_values)
                    if result.rowcount > 0:
                        total_updated += 1
                    else:
                        # 如果股票不存在，记录但不报错
                        total_skipped += 1
                        logger.debug(f"股票 {ts_code_val} 在 stock_basic 表中不存在，跳过更新")
                except Exception as e:
                    logger.error(f"更新股票 {ts_code_val} 失败: {e}")
                    print(f"警告: 更新股票 {ts_code_val} 失败: {e}")
            else:
                total_skipped += 1
                logger.debug(f"股票 {ts_code_val} 没有可更新的字段")
        
        session.commit()
        
        logger.info("=" * 60)
        logger.info(f"每日盘前股本信息更新完成:")
        logger.info(f"  交易日期: {trade_date}")
        logger.info(f"  获取数据: {len(df)} 条")
        logger.info(f"  更新记录: {total_updated} 条")
        logger.info(f"  跳过记录: {total_skipped} 条")
        print(f"\n" + "=" * 50)
        print(f"每日盘前股本信息更新完成:")
        print(f"  交易日期: {trade_date}")
        print(f"  获取数据: {len(df)} 条")
        print(f"  更新记录: {total_updated} 条")
        print(f"  跳过记录: {total_skipped} 条")
        print(f"=" * 50)
        
    except TusharePermissionError as e:
        # 权限不足，停止整个任务
        logger.error(f"接口权限不足，停止盘前股本信息获取任务: {e.api_name}")
        logger.error(f"错误信息: {e.error_msg}")
        logger.error(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
        print(f"❌ 接口权限不足，停止盘前股本信息获取任务: {e.api_name}")
        print(f"错误信息: {e.error_msg}")
        print(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
        return  # 直接返回，停止任务
    except Exception as e:
        logger.error(f"获取每日盘前股本信息失败: {e}", exc_info=True)
        print(f"获取每日盘前股本信息失败: {e}")
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
                    
                    # 获取该日期的两融数据并更新到日线表
                    try:
                        df_margin = call_tushare_api(
                            pro.margin,
                            f'margin (trade_date={trade_date})',
                            trade_date=trade_date,
                            fields='ts_code,trade_date,rzye,rqye,rqyl,rzrqye,rzmre,rqmcl,rzche,rqchl'
                        )
                        
                        if not df_margin.empty:
                            margin_updated = 0
                            for _, margin_row in df_margin.iterrows():
                                ts_code_margin = margin_row.get('ts_code')
                                if not ts_code_margin:
                                    continue
                                
                                # 查找对应的日线记录
                                daily_record = session.query(StockDaily).filter_by(
                                    ts_code=ts_code_margin,
                                    trade_date=trade_date
                                ).first()
                                
                                if daily_record:
                                    # 更新两融数据
                                    daily_record.rzye = margin_row.get('rzye')
                                    daily_record.rqye = margin_row.get('rqye')
                                    daily_record.rqyl = margin_row.get('rqyl')
                                    daily_record.rzrqye = margin_row.get('rzrqye')
                                    daily_record.rzmre = margin_row.get('rzmre')
                                    daily_record.rqmcl = margin_row.get('rqmcl')
                                    daily_record.rzche = margin_row.get('rzche')
                                    daily_record.rqchl = margin_row.get('rqchl')
                                    margin_updated += 1
                            
                            if margin_updated > 0:
                                session.commit()
                                logger.info(f"[{trade_date}] 更新了 {margin_updated} 条两融数据")
                    except Exception as e:
                        logger.warning(f"获取 {trade_date} 的两融数据失败: {e}")
                        # 两融数据获取失败不影响日线数据，继续执行
                    
                    # 获取该日期的资金流向数据并更新到日线表
                    try:
                        df_moneyflow = call_tushare_api(
                            pro.moneyflow,
                            f'moneyflow (trade_date={trade_date})',
                            trade_date=trade_date,
                            fields='ts_code,trade_date,buy_sm_vol,buy_sm_amount,sell_sm_vol,sell_sm_amount,buy_md_vol,buy_md_amount,sell_md_vol,sell_md_amount,buy_lg_vol,buy_lg_amount,sell_lg_vol,sell_lg_amount,buy_elg_vol,buy_elg_amount,sell_elg_vol,sell_elg_amount,net_mf_amount'
                        )
                        
                        if not df_moneyflow.empty:
                            moneyflow_updated = 0
                            for _, mf_row in df_moneyflow.iterrows():
                                ts_code_mf = mf_row.get('ts_code')
                                if not ts_code_mf:
                                    continue
                                
                                # 查找对应的日线记录
                                daily_record = session.query(StockDaily).filter_by(
                                    ts_code=ts_code_mf,
                                    trade_date=trade_date
                                ).first()
                                
                                if daily_record:
                                    # 更新资金流向数据
                                    daily_record.buy_sm_vol = mf_row.get('buy_sm_vol')
                                    daily_record.buy_sm_amount = mf_row.get('buy_sm_amount')
                                    daily_record.sell_sm_vol = mf_row.get('sell_sm_vol')
                                    daily_record.sell_sm_amount = mf_row.get('sell_sm_amount')
                                    daily_record.buy_md_vol = mf_row.get('buy_md_vol')
                                    daily_record.buy_md_amount = mf_row.get('buy_md_amount')
                                    daily_record.sell_md_vol = mf_row.get('sell_md_vol')
                                    daily_record.sell_md_amount = mf_row.get('sell_md_amount')
                                    daily_record.buy_lg_vol = mf_row.get('buy_lg_vol')
                                    daily_record.buy_lg_amount = mf_row.get('buy_lg_amount')
                                    daily_record.sell_lg_vol = mf_row.get('sell_lg_vol')
                                    daily_record.sell_lg_amount = mf_row.get('sell_lg_amount')
                                    daily_record.buy_elg_vol = mf_row.get('buy_elg_vol')
                                    daily_record.buy_elg_amount = mf_row.get('buy_elg_amount')
                                    daily_record.sell_elg_vol = mf_row.get('sell_elg_vol')
                                    daily_record.sell_elg_amount = mf_row.get('sell_elg_amount')
                                    daily_record.net_mf_amount = mf_row.get('net_mf_amount')
                                    moneyflow_updated += 1
                            
                            if moneyflow_updated > 0:
                                session.commit()
                                logger.info(f"[{trade_date}] 更新了 {moneyflow_updated} 条资金流向数据")
                    except Exception as e:
                        logger.warning(f"获取 {trade_date} 的资金流向数据失败: {e}")
                        # 资金流向数据获取失败不影响日线数据，继续执行
                    
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
            
            total_stocks = len(codes)
            for i, code in enumerate(codes):
                try:
                    # 每处理100个股票显示一次进度（全量模式时）
                    if (i + 1) % 100 == 0 or i == 0:
                        progress = (i + 1) / total_stocks * 100
                        print(f"进度: {i+1}/{total_stocks} ({progress:.1f}%) - 当前处理: {code}")
                    
                    # 检查是否需要等待（每分钟50次限制）
                    current_time = time.time()
                    elapsed = current_time - minute_start_time
                    
                    if elapsed >= 60:
                        # 重置计数器
                        request_count = 0
                        minute_start_time = current_time
                        print(f"限速窗口重置，已处理 {i}/{total_stocks} 个股票 ({i/total_stocks*100:.1f}%)")
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
                        logger.warning(f"{code}: 日期范围 {start_date} 至 {end_date} 内没有数据（可能是非交易日或停牌）")
                        time.sleep(REQUEST_INTERVAL)
                        continue
                    
                    # 检查返回数据量并记录详细信息
                    returned_count = len(df)
                    if returned_count > 0:
                        trade_dates = sorted(df['trade_date'].unique().tolist())
                        logger.info(f"{code}: 返回 {returned_count} 条数据，交易日: {', '.join(trade_dates)}")
                        if returned_count < 5 and (datetime.strptime(end_date, '%Y%m%d') - datetime.strptime(start_date, '%Y%m%d')).days >= 5:
                            logger.info(f"{code}: 注意 - 日期范围 {start_date} 至 {end_date} 包含非交易日或停牌日")
                    
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
                        print(f"[{i+1}/{len(codes)}] {code}: 新增 {len(new_records)} 条数据（API返回 {returned_count} 条，已存在 {returned_count - len(new_records)} 条）")
                    elif returned_count > 0:
                        print(f"[{i+1}/{len(codes)}] {code}: 无新增数据（API返回 {returned_count} 条，但数据库中已存在）")
                    
                    # 获取该股票的两融数据并更新到日线表
                    try:
                        df_margin = call_tushare_api(
                            pro.margin,
                            f'margin (ts_code={code})',
                            ts_code=code,
                            start_date=start_date,
                            end_date=end_date,
                            fields='ts_code,trade_date,rzye,rqye,rqyl,rzrqye,rzmre,rqmcl,rzche,rqchl'
                        )
                        
                        if not df_margin.empty:
                            margin_updated = 0
                            for _, margin_row in df_margin.iterrows():
                                trade_date_margin = margin_row.get('trade_date')
                                if not trade_date_margin:
                                    continue
                                
                                # 查找对应的日线记录
                                daily_record = session.query(StockDaily).filter_by(
                                    ts_code=code,
                                    trade_date=trade_date_margin
                                ).first()
                                
                                if daily_record:
                                    # 更新两融数据
                                    daily_record.rzye = margin_row.get('rzye')
                                    daily_record.rqye = margin_row.get('rqye')
                                    daily_record.rqyl = margin_row.get('rqyl')
                                    daily_record.rzrqye = margin_row.get('rzrqye')
                                    daily_record.rzmre = margin_row.get('rzmre')
                                    daily_record.rqmcl = margin_row.get('rqmcl')
                                    daily_record.rzche = margin_row.get('rzche')
                                    daily_record.rqchl = margin_row.get('rqchl')
                                    margin_updated += 1
                            
                            if margin_updated > 0:
                                session.commit()
                                logger.debug(f"{code}: 更新了 {margin_updated} 条两融数据")
                    except Exception as e:
                        logger.warning(f"获取 {code} 的两融数据失败: {e}")
                        # 两融数据获取失败不影响日线数据，继续执行
                    
                    # 获取该股票的资金流向数据并更新到日线表
                    try:
                        df_moneyflow = call_tushare_api(
                            pro.moneyflow,
                            f'moneyflow (ts_code={code})',
                            ts_code=code,
                            start_date=start_date,
                            end_date=end_date,
                            fields='ts_code,trade_date,buy_sm_vol,buy_sm_amount,sell_sm_vol,sell_sm_amount,buy_md_vol,buy_md_amount,sell_md_vol,sell_md_amount,buy_lg_vol,buy_lg_amount,sell_lg_vol,sell_lg_amount,buy_elg_vol,buy_elg_amount,sell_elg_vol,sell_elg_amount,net_mf_amount'
                        )
                        
                        if not df_moneyflow.empty:
                            moneyflow_updated = 0
                            for _, mf_row in df_moneyflow.iterrows():
                                trade_date_mf = mf_row.get('trade_date')
                                if not trade_date_mf:
                                    continue
                                
                                # 查找对应的日线记录
                                daily_record = session.query(StockDaily).filter_by(
                                    ts_code=code,
                                    trade_date=trade_date_mf
                                ).first()
                                
                                if daily_record:
                                    # 更新资金流向数据
                                    daily_record.buy_sm_vol = mf_row.get('buy_sm_vol')
                                    daily_record.buy_sm_amount = mf_row.get('buy_sm_amount')
                                    daily_record.sell_sm_vol = mf_row.get('sell_sm_vol')
                                    daily_record.sell_sm_amount = mf_row.get('sell_sm_amount')
                                    daily_record.buy_md_vol = mf_row.get('buy_md_vol')
                                    daily_record.buy_md_amount = mf_row.get('buy_md_amount')
                                    daily_record.sell_md_vol = mf_row.get('sell_md_vol')
                                    daily_record.sell_md_amount = mf_row.get('sell_md_amount')
                                    daily_record.buy_lg_vol = mf_row.get('buy_lg_vol')
                                    daily_record.buy_lg_amount = mf_row.get('buy_lg_amount')
                                    daily_record.sell_lg_vol = mf_row.get('sell_lg_vol')
                                    daily_record.sell_lg_amount = mf_row.get('sell_lg_amount')
                                    daily_record.buy_elg_vol = mf_row.get('buy_elg_vol')
                                    daily_record.buy_elg_amount = mf_row.get('buy_elg_amount')
                                    daily_record.sell_elg_vol = mf_row.get('sell_elg_vol')
                                    daily_record.sell_elg_amount = mf_row.get('sell_elg_amount')
                                    daily_record.net_mf_amount = mf_row.get('net_mf_amount')
                                    moneyflow_updated += 1
                            
                            if moneyflow_updated > 0:
                                session.commit()
                                logger.debug(f"{code}: 更新了 {moneyflow_updated} 条资金流向数据")
                    except Exception as e:
                        logger.warning(f"获取 {code} 的资金流向数据失败: {e}")
                        # 资金流向数据获取失败不影响日线数据，继续执行
                    
                    # 控制请求频率
                    time.sleep(REQUEST_INTERVAL)
                        
                except TusharePermissionError as e:
                    # 权限不足，停止整个任务
                    logger.error(f"接口权限不足，停止日线数据获取任务: {e.api_name}")
                    logger.error(f"错误信息: {e.error_msg}")
                    logger.error(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
                    print(f"❌ 接口权限不足，停止日线数据获取任务: {e.api_name}")
                    print(f"错误信息: {e.error_msg}")
                    print(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
                    return  # 直接返回，停止任务
                except Exception as e:
                    logger.error(f"获取 {code} 日线数据失败: {e}", exc_info=True)
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
    """
    获取股票周线数据
    限速要求：每分钟120次
    """
    if not end_date:
        end_date = datetime.now().strftime('%Y%m%d')
    if not start_date:
        start_date = (datetime.now() - timedelta(days=730)).strftime('%Y%m%d')
    
    logger.info("=" * 60)
    logger.info(f"开始获取周线数据: {ts_code or '全部股票'}, {start_date} 至 {end_date}")
    logger.info(f"限速策略: 每分钟最多120次请求")
    print(f"开始获取周线数据: {ts_code or '全部股票'}, {start_date} 至 {end_date}")
    print(f"限速策略: 每分钟最多120次请求")
    
    session = get_session()
    try:
        if ts_code:
            codes = [ts_code]
        else:
            stocks = session.query(StockBasic).all()
            codes = [stock.ts_code for stock in stocks]
        
        # 限速控制：每分钟120次 = 每次请求间隔约 60/120 = 0.5秒
        # 为了安全，设置为0.55秒，每分钟约109次
        REQUEST_INTERVAL = 0.55  # 秒
        MAX_REQUESTS_PER_MINUTE = 120
        
        # 请求计数器（用于每分钟重置）
        request_count = 0
        minute_start_time = time.time()
        
        total_count = 0
        total_requests = 0
        
        for i, code in enumerate(codes):
            try:
                # 检查是否需要等待（每分钟120次限制）
                current_time = time.time()
                elapsed = current_time - minute_start_time
                
                if elapsed >= 60:
                    # 重置计数器
                    request_count = 0
                    minute_start_time = current_time
                    logger.info(f"限速窗口重置，已处理 {i}/{len(codes)} 个股票")
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
                    pro.weekly,
                    f'weekly (ts_code={code})',
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
                
                if (i + 1) % 100 == 0:
                    logger.info(f"已处理 {i + 1}/{len(codes)} 个股票，新增 {total_count} 条数据")
                    print(f"已处理 {i + 1}/{len(codes)} 个股票，新增 {total_count} 条数据")
                
                # 控制请求频率
                time.sleep(REQUEST_INTERVAL)
                    
            except TusharePermissionError as e:
                # 权限不足，停止整个任务
                logger.error(f"接口权限不足，停止周线数据获取任务: {e.api_name}")
                logger.error(f"错误信息: {e.error_msg}")
                logger.error(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
                print(f"❌ 接口权限不足，停止周线数据获取任务: {e.api_name}")
                print(f"错误信息: {e.error_msg}")
                print(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
                return  # 直接返回，停止任务
            except Exception as e:
                logger.error(f"获取 {code} 周线数据失败: {e}", exc_info=True)
                print(f"获取 {code} 周线数据失败: {e}")
                session.rollback()
                # 即使失败也要等待，避免过快重试
                time.sleep(REQUEST_INTERVAL)
                continue
        
        logger.info("=" * 60)
        logger.info(f"周线数据获取完成:")
        logger.info(f"  总请求次数: {total_requests}")
        logger.info(f"  新增数据条数: {total_count}")
        print(f"=" * 50)
        print(f"周线数据获取完成:")
        print(f"  总请求次数: {total_requests}")
        print(f"  新增数据条数: {total_count}")
        print(f"=" * 50)
    finally:
        session.close()


def fetch_stock_monthly(ts_code=None, start_date=None, end_date=None):
    """
    获取股票月线数据
    限速要求：每分钟120次
    """
    if not end_date:
        end_date = datetime.now().strftime('%Y%m%d')
    if not start_date:
        start_date = (datetime.now() - timedelta(days=3650)).strftime('%Y%m%d')
    
    logger.info("=" * 60)
    logger.info(f"开始获取月线数据: {ts_code or '全部股票'}, {start_date} 至 {end_date}")
    logger.info(f"限速策略: 每分钟最多120次请求")
    print(f"开始获取月线数据: {ts_code or '全部股票'}, {start_date} 至 {end_date}")
    print(f"限速策略: 每分钟最多120次请求")
    
    session = get_session()
    try:
        if ts_code:
            codes = [ts_code]
        else:
            stocks = session.query(StockBasic).all()
            codes = [stock.ts_code for stock in stocks]
        
        # 限速控制：每分钟120次 = 每次请求间隔约 60/120 = 0.5秒
        # 为了安全，设置为0.55秒，每分钟约109次
        REQUEST_INTERVAL = 0.55  # 秒
        MAX_REQUESTS_PER_MINUTE = 120
        
        # 请求计数器（用于每分钟重置）
        request_count = 0
        minute_start_time = time.time()
        
        total_count = 0
        total_requests = 0
        
        for i, code in enumerate(codes):
            try:
                # 检查是否需要等待（每分钟120次限制）
                current_time = time.time()
                elapsed = current_time - minute_start_time
                
                if elapsed >= 60:
                    # 重置计数器
                    request_count = 0
                    minute_start_time = current_time
                    logger.info(f"限速窗口重置，已处理 {i}/{len(codes)} 个股票")
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
                    pro.monthly,
                    f'monthly (ts_code={code})',
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
                
                if (i + 1) % 100 == 0:
                    logger.info(f"已处理 {i + 1}/{len(codes)} 个股票，新增 {total_count} 条数据")
                    print(f"已处理 {i + 1}/{len(codes)} 个股票，新增 {total_count} 条数据")
                
                # 控制请求频率
                time.sleep(REQUEST_INTERVAL)
                    
            except TusharePermissionError as e:
                # 权限不足，停止整个任务
                logger.error(f"接口权限不足，停止月线数据获取任务: {e.api_name}")
                logger.error(f"错误信息: {e.error_msg}")
                logger.error(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
                print(f"❌ 接口权限不足，停止月线数据获取任务: {e.api_name}")
                print(f"错误信息: {e.error_msg}")
                print(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
                return  # 直接返回，停止任务
            except Exception as e:
                logger.error(f"获取 {code} 月线数据失败: {e}", exc_info=True)
                print(f"获取 {code} 月线数据失败: {e}")
                session.rollback()
                # 即使失败也要等待，避免过快重试
                time.sleep(REQUEST_INTERVAL)
                continue
        
        logger.info("=" * 60)
        logger.info(f"月线数据获取完成:")
        logger.info(f"  总请求次数: {total_requests}")
        logger.info(f"  新增数据条数: {total_count}")
        print(f"=" * 50)
        print(f"月线数据获取完成:")
        print(f"  总请求次数: {total_requests}")
        print(f"  新增数据条数: {total_count}")
        print(f"=" * 50)
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
                    
            except TusharePermissionError as e:
                # 权限不足，停止整个任务
                logger.error(f"接口权限不足，停止资金流向数据获取任务: {e.api_name}")
                logger.error(f"错误信息: {e.error_msg}")
                logger.error(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
                print(f"❌ 接口权限不足，停止资金流向数据获取任务: {e.api_name}")
                print(f"错误信息: {e.error_msg}")
                print(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
                return  # 直接返回，停止任务
            except Exception as e:
                logger.error(f"获取 {code} 资金流向数据失败: {e}", exc_info=True)
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
    
    logger.info(f"开始获取股票指标数据: {ts_code or '全部股票'}, {start_date} 至 {end_date}")
    print(f"开始获取股票指标数据: {ts_code or '全部股票'}, {start_date} 至 {end_date}")
    
    session = get_session()
    try:
        if ts_code:
            codes = [ts_code]
        else:
            stocks = session.query(StockBasic).all()
            codes = [stock.ts_code for stock in stocks]
        
        logger.info(f"准备获取 {len(codes)} 个股票的指标数据")
        total_count = 0
        updated_count = 0
        
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
                
                if df is None or df.empty:
                    logger.debug(f"股票 {code} 无指标数据")
                    continue
                
                logger.info(f"股票 {code} 获取到 {len(df)} 条指标数据")
                
                for _, row in df.iterrows():
                    indicator = session.query(StockIndicator).filter_by(
                        ts_code=row['ts_code'],
                        trade_date=row['trade_date']
                    ).first()
                    
                    # 处理NaN值，转换为None
                    def safe_float(value):
                        if pd.isna(value) or value is None:
                            return None
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            return None
                    
                    total_mv = safe_float(row.get('total_mv'))
                    circ_mv = safe_float(row.get('circ_mv'))
                    pe = safe_float(row.get('pe'))
                    pb = safe_float(row.get('pb'))
                    ps = safe_float(row.get('ps'))
                    dv_ttm = safe_float(row.get('dv_ttm'))
                    
                    if not indicator:
                        indicator = StockIndicator(
                            ts_code=row['ts_code'],
                            trade_date=row['trade_date'],
                            total_mv=total_mv,
                            circ_mv=circ_mv,
                            pe=pe,
                            pb=pb,
                            ps=ps,
                            dv_ttm=dv_ttm,
                            created_at=datetime.now()
                        )
                        session.add(indicator)
                        total_count += 1
                    else:
                        # 更新已有数据
                        indicator.total_mv = total_mv
                        indicator.circ_mv = circ_mv
                        indicator.pe = pe
                        indicator.pb = pb
                        indicator.ps = ps
                        indicator.dv_ttm = dv_ttm
                        updated_count += 1
                
                session.commit()
                
                if (i + 1) % 200 == 0:
                    logger.info(f"已处理 {i + 1}/{len(codes)} 个股票，暂停60秒...")
                    print(f"已处理 {i + 1}/{len(codes)} 个股票，暂停60秒...")
                    time.sleep(60)
                else:
                    time.sleep(0.2)
                    
            except TusharePermissionError as e:
                # 权限不足，停止整个任务
                logger.error(f"接口权限不足，停止指标数据获取任务: {e.api_name}")
                logger.error(f"错误信息: {e.error_msg}")
                logger.error(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
                print(f"❌ 接口权限不足，停止指标数据获取任务: {e.api_name}")
                print(f"错误信息: {e.error_msg}")
                print(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
                return  # 直接返回，停止任务
            except Exception as e:
                logger.error(f"获取 {code} 指标数据失败: {e}", exc_info=True)
                print(f"获取 {code} 指标数据失败: {e}")
                session.rollback()
                continue
        
        logger.info(f"成功获取 {total_count} 条新指标数据，更新 {updated_count} 条已有数据")
        print(f"成功获取 {total_count} 条新指标数据，更新 {updated_count} 条已有数据")
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
        # 使用 call_tushare_api 统一处理权限错误
        df = call_tushare_api(
            pro.new_share,
            'new_share',
            start_date=start_date,
            end_date=end_date
        )
        
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
    except TusharePermissionError as e:
        # 权限不足，停止整个任务
        logger.error(f"接口权限不足，停止IPO数据获取任务: {e.api_name}")
        logger.error(f"错误信息: {e.error_msg}")
        logger.error(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
        print(f"❌ 接口权限不足，停止IPO数据获取任务: {e.api_name}")
        print(f"错误信息: {e.error_msg}")
        print(f"请访问 https://tushare.pro/document/1?doc_id=108 查看权限详情")
        return  # 直接返回，停止任务
    except Exception as e:
        logger.error(f"获取IPO数据失败: {e}", exc_info=True)
        print(f"获取IPO数据失败: {e}")
        raise


def fetch_stock_managers(ts_code=None, start_date=None, end_date=None):
    """
    获取上市公司管理层信息（stk_managers接口）和薪酬持股信息（stk_rewards接口）
    参考: https://tushare.pro/document/2?doc_id=193
          https://tushare.pro/document/2?doc_id=194
    
    Args:
        ts_code: 股票代码，如果为None则获取所有股票
        start_date: 公告开始日期(YYYYMMDD格式)
        end_date: 公告结束日期(YYYYMMDD格式)
    """
    import json
    
    logger.info("=" * 60)
    logger.info(f"开始获取上市公司管理层信息 (ts_code={ts_code}, start_date={start_date}, end_date={end_date})")
    logger.info("参考文档: https://tushare.pro/document/2?doc_id=193")
    logger.info("参考文档: https://tushare.pro/document/2?doc_id=194")
    print("开始获取上市公司管理层信息...")
    print("参考文档: https://tushare.pro/document/2?doc_id=193")
    print("参考文档: https://tushare.pro/document/2?doc_id=194")
    
    session = get_session()
    try:
        # 获取需要更新的股票代码列表
        if ts_code:
            stock_codes = [ts_code]
        else:
            # 获取所有上市股票代码
            stock_codes = [row[0] for row in session.query(StockBasic.ts_code).all()]
        
        if not stock_codes:
            print("没有找到需要更新的股票")
            return
        
        print(f"找到 {len(stock_codes)} 只股票需要更新管理层信息")
        
        total_updated = 0
        total_new = 0
        total_changes = 0
        total_requests = 0
        
        # 批量处理股票（每次处理一批，避免一次性请求过多）
        batch_size = 50
        for batch_start in range(0, len(stock_codes), batch_size):
            batch_codes = stock_codes[batch_start:batch_start + batch_size]
            batch_codes_str = ','.join(batch_codes)
            
            try:
                # 1. 获取管理层信息（按股票逐个获取，因为stk_managers接口支持多股票但需要控制频率）
                pro = get_pro_api()
                df_managers_list = []
                
                for code in batch_codes:
                    try:
                        df_managers_single = call_tushare_api(
                            pro.stk_managers,
                            f'stk_managers (ts_code={code})',
                            ts_code=code,
                            start_date=start_date,
                            end_date=end_date,
                            fields='ts_code,ann_date,name,gender,lev,title,edu,national,birthday,begin_date,end_date,resume'
                        )
                        if not df_managers_single.empty:
                            df_managers_list.append(df_managers_single)
                        time.sleep(0.3)  # 控制请求频率
                    except Exception as e:
                        logger.warning(f"获取股票 {code} 的管理层信息失败: {e}")
                        continue
                
                if df_managers_list:
                    df_managers = pd.concat(df_managers_list, ignore_index=True)
                else:
                    df_managers = pd.DataFrame()
                
                total_requests += 1
                
                if df_managers.empty:
                    print(f"批次 {batch_start//batch_size + 1} 没有管理层数据")
                    time.sleep(0.5)
                    continue
                
                print(f"批次 {batch_start//batch_size + 1} 获取到 {len(df_managers)} 条管理层信息")
                
                # 2. 获取薪酬持股信息（需要按股票代码逐个获取）
                rewards_dict = {}  # {ts_code: {name: {salary, hold_vol, end_date}}}
                
                for code in batch_codes:
                    try:
                        df_rewards = call_tushare_api(
                            pro.stk_rewards,
                            f'stk_rewards (ts_code={code})',
                            ts_code=code,
                            fields='ts_code,name,title,salary,hold_vol,end_date'
                        )
                        
                        total_requests += 1
                        
                        if not df_rewards.empty:
                            rewards_dict[code] = {}
                            for _, reward_row in df_rewards.iterrows():
                                name = reward_row.get('name', '')
                                if name:
                                    rewards_dict[code][name] = {
                                        'salary': reward_row.get('salary'),
                                        'hold_vol': reward_row.get('hold_vol'),
                                        'end_date': reward_row.get('end_date'),
                                    }
                        
                        time.sleep(0.2)  # 控制请求频率
                    except Exception as e:
                        logger.warning(f"获取股票 {code} 的薪酬信息失败: {e}")
                        continue
                
                # 3. 处理每条管理层信息
                for _, row in df_managers.iterrows():
                    ts_code_val = row.get('ts_code')
                    name_val = row.get('name')
                    title_val = row.get('title')
                    begin_date_val = row.get('begin_date')
                    
                    if not ts_code_val or not name_val or not title_val:
                        continue
                    
                    # 查找现有记录（使用ts_code, name, title, begin_date作为唯一标识）
                    existing_manager = session.query(StockManager).filter(
                        StockManager.ts_code == ts_code_val,
                        StockManager.name == name_val,
                        StockManager.title == title_val,
                        StockManager.begin_date == begin_date_val
                    ).first()
                    
                    # 获取薪酬持股信息
                    salary = None
                    hold_vol = None
                    reward_date = None
                    if ts_code_val in rewards_dict and name_val in rewards_dict[ts_code_val]:
                        reward_info = rewards_dict[ts_code_val][name_val]
                        salary = reward_info.get('salary')
                        hold_vol = reward_info.get('hold_vol')
                        reward_date = reward_info.get('end_date')
                    
                    # 准备新数据
                    new_data = {
                        'ann_date': row.get('ann_date'),
                        'gender': row.get('gender'),
                        'lev': row.get('lev'),
                        'edu': row.get('edu'),
                        'national': row.get('national'),
                        'birthday': row.get('birthday'),
                        'end_date': row.get('end_date'),
                        'resume': row.get('resume'),
                        'salary': salary,
                        'hold_vol': hold_vol,
                        'reward_date': reward_date,
                    }
                    
                    if existing_manager:
                        # 检测变更
                        old_data = {
                            'ann_date': existing_manager.ann_date,
                            'gender': existing_manager.gender,
                            'lev': existing_manager.lev,
                            'edu': existing_manager.edu,
                            'national': existing_manager.national,
                            'birthday': existing_manager.birthday,
                            'end_date': existing_manager.end_date,
                            'resume': existing_manager.resume,
                            'salary': existing_manager.salary,
                            'hold_vol': existing_manager.hold_vol,
                            'reward_date': existing_manager.reward_date,
                        }
                        
                        # 检查是否有变更
                        has_change = False
                        change_type = '信息更新'
                        
                        # 检查是否离职（end_date从None变为有值）
                        if not old_data['end_date'] and new_data['end_date']:
                            change_type = '离职'
                            has_change = True
                        # 检查是否岗位变更（需要单独检查title字段）
                        elif existing_manager.title != title_val:
                            change_type = '岗位变更'
                            has_change = True
                        # 检查其他字段变更
                        else:
                            for key in ['ann_date', 'gender', 'lev', 'edu', 'national', 'birthday', 'resume', 'salary', 'hold_vol', 'reward_date']:
                                if old_data.get(key) != new_data.get(key):
                                    has_change = True
                                    break
                        
                        if has_change:
                            # 记录变更
                            change_record = StockManagerChange(
                                ts_code=ts_code_val,
                                change_type=change_type,
                                name=name_val,
                                title=title_val,
                                old_value=json.dumps(old_data, ensure_ascii=False),
                                new_value=json.dumps(new_data, ensure_ascii=False),
                                change_date=datetime.now().strftime('%Y%m%d'),
                                ann_date=new_data.get('ann_date'),
                                created_at=datetime.now()
                            )
                            session.add(change_record)
                            total_changes += 1
                        
                        # 更新现有记录
                        existing_manager.ann_date = new_data['ann_date']
                        existing_manager.gender = new_data['gender']
                        existing_manager.lev = new_data['lev']
                        existing_manager.title = title_val  # 更新岗位
                        existing_manager.edu = new_data['edu']
                        existing_manager.national = new_data['national']
                        existing_manager.birthday = new_data['birthday']
                        existing_manager.end_date = new_data['end_date']
                        existing_manager.resume = new_data['resume']
                        existing_manager.salary = new_data['salary']
                        existing_manager.hold_vol = new_data['hold_vol']
                        existing_manager.reward_date = new_data['reward_date']
                        existing_manager.updated_at = datetime.now()
                        total_updated += 1
                    else:
                        # 新增记录
                        new_manager = StockManager(
                            ts_code=ts_code_val,
                            ann_date=new_data['ann_date'],
                            name=name_val,
                            gender=new_data['gender'],
                            lev=new_data['lev'],
                            title=title_val,
                            edu=new_data['edu'],
                            national=new_data['national'],
                            birthday=new_data['birthday'],
                            begin_date=begin_date_val,
                            end_date=new_data['end_date'],
                            resume=new_data['resume'],
                            salary=new_data['salary'],
                            hold_vol=new_data['hold_vol'],
                            reward_date=new_data['reward_date'],
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        session.add(new_manager)
                        total_new += 1
                        
                        # 记录新增变更
                        change_record = StockManagerChange(
                            ts_code=ts_code_val,
                            change_type='新增',
                            name=name_val,
                            title=title_val,
                            old_value=None,
                            new_value=json.dumps(new_data, ensure_ascii=False),
                            change_date=datetime.now().strftime('%Y%m%d'),
                            ann_date=new_data.get('ann_date'),
                            created_at=datetime.now()
                        )
                        session.add(change_record)
                        total_changes += 1
                
                session.commit()
                print(f"批次 {batch_start//batch_size + 1} 处理完成")
                
                # 控制请求频率
                time.sleep(1)
                
            except TusharePermissionError as e:
                logger.error(f"接口权限不足: {e.api_name}")
                print(f"❌ 接口权限不足: {e.api_name}")
                print(f"错误信息: {e.error_msg}")
                break
            except Exception as e:
                logger.error(f"处理批次 {batch_start//batch_size + 1} 失败: {e}", exc_info=True)
                print(f"处理批次 {batch_start//batch_size + 1} 失败: {e}")
                session.rollback()
                continue
        
        logger.info("=" * 60)
        logger.info(f"上市公司管理层信息更新完成:")
        logger.info(f"  总请求次数: {total_requests}")
        logger.info(f"  新增记录: {total_new} 条")
        logger.info(f"  更新记录: {total_updated} 条")
        logger.info(f"  变更记录: {total_changes} 条")
        print(f"\n" + "=" * 50)
        print(f"上市公司管理层信息更新完成:")
        print(f"  总请求次数: {total_requests}")
        print(f"  新增记录: {total_new} 条")
        print(f"  更新记录: {total_updated} 条")
        print(f"  变更记录: {total_changes} 条")
        print(f"=" * 50)
        
    except TusharePermissionError as e:
        logger.error(f"接口权限不足，停止管理层信息获取任务: {e.api_name}")
        logger.error(f"错误信息: {e.error_msg}")
        print(f"❌ 接口权限不足，停止管理层信息获取任务: {e.api_name}")
        print(f"错误信息: {e.error_msg}")
        return
    except Exception as e:
        logger.error(f"获取上市公司管理层信息失败: {e}", exc_info=True)
        print(f"获取上市公司管理层信息失败: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def fetch_index_basic(market=None):
    """
    获取指数基本信息（index_basic接口）
    参考: https://tushare.pro/document/2?doc_id=94
    
    Args:
        market: 交易所或服务商，如SSE、SZSE、CSI、SW等，如果为None则获取所有
    """
    logger.info("=" * 60)
    logger.info(f"开始获取指数基本信息 (market={market})")
    logger.info("参考文档: https://tushare.pro/document/2?doc_id=94")
    print("开始获取指数基本信息...")
    print("参考文档: https://tushare.pro/document/2?doc_id=94")
    
    session = get_session()
    try:
        pro = get_pro_api()
        df = call_tushare_api(
            pro.index_basic,
            f'index_basic (market={market})',
            market=market if market else None,
            fields='ts_code,name,fullname,market,publisher,index_type,category,base_date,base_point,list_date,weight_rule,desc,exp_date'
        )
        
        if df.empty:
            print("没有获取到指数基本信息")
            return
        
        print(f"获取到 {len(df)} 条指数基本信息")
        
        total_new = 0
        total_updated = 0
        
        for _, row in df.iterrows():
            ts_code_val = row.get('ts_code')
            if not ts_code_val:
                continue
            
            existing_index = session.query(IndexBasic).filter_by(ts_code=ts_code_val).first()
            
            if existing_index:
                # 更新现有记录
                existing_index.name = row.get('name', '')
                existing_index.fullname = row.get('fullname')
                existing_index.market = row.get('market')
                existing_index.publisher = row.get('publisher')
                existing_index.index_type = row.get('index_type')
                existing_index.category = row.get('category')
                existing_index.base_date = row.get('base_date')
                existing_index.base_point = row.get('base_point')
                existing_index.list_date = row.get('list_date')
                existing_index.weight_rule = row.get('weight_rule')
                existing_index.desc = row.get('desc')
                existing_index.exp_date = row.get('exp_date')
                existing_index.updated_at = datetime.now()
                total_updated += 1
            else:
                # 新增记录
                new_index = IndexBasic(
                    ts_code=ts_code_val,
                    name=row.get('name', ''),
                    fullname=row.get('fullname'),
                    market=row.get('market'),
                    publisher=row.get('publisher'),
                    index_type=row.get('index_type'),
                    category=row.get('category'),
                    base_date=row.get('base_date'),
                    base_point=row.get('base_point'),
                    list_date=row.get('list_date'),
                    weight_rule=row.get('weight_rule'),
                    desc=row.get('desc'),
                    exp_date=row.get('exp_date'),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                session.add(new_index)
                total_new += 1
        
        session.commit()
        
        logger.info("=" * 60)
        logger.info(f"指数基本信息更新完成:")
        logger.info(f"  新增记录: {total_new} 条")
        logger.info(f"  更新记录: {total_updated} 条")
        print(f"\n" + "=" * 50)
        print(f"指数基本信息更新完成:")
        print(f"  新增记录: {total_new} 条")
        print(f"  更新记录: {total_updated} 条")
        print(f"=" * 50)
        
    except TusharePermissionError as e:
        logger.error(f"接口权限不足: {e.api_name}")
        print(f"❌ 接口权限不足: {e.api_name}")
        return
    except Exception as e:
        logger.error(f"获取指数基本信息失败: {e}", exc_info=True)
        print(f"获取指数基本信息失败: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def fetch_index_daily(ts_code=None, start_date=None, end_date=None):
    """
    获取指数日线行情（index_daily接口）
    参考: https://tushare.pro/document/2?doc_id=95
    
    Args:
        ts_code: 指数代码，如果为None则获取所有指数
        start_date: 开始日期(YYYYMMDD格式)
        end_date: 结束日期(YYYYMMDD格式)
    """
    logger.info("=" * 60)
    logger.info(f"开始获取指数日线行情 (ts_code={ts_code}, start_date={start_date}, end_date={end_date})")
    logger.info("参考文档: https://tushare.pro/document/2?doc_id=95")
    print("开始获取指数日线行情...")
    
    session = get_session()
    try:
        # 获取需要更新的指数代码列表
        if ts_code:
            index_codes = [ts_code]
        else:
            # 获取所有指数代码
            index_codes = [row[0] for row in session.query(IndexBasic.ts_code).all()]
        
        if not index_codes:
            print("没有找到需要更新的指数")
            return
        
        print(f"找到 {len(index_codes)} 个指数需要更新日线行情")
        
        total_new = 0
        total_updated = 0
        total_requests = 0
        
        for i, code in enumerate(index_codes):
            try:
                pro = get_pro_api()
                df = call_tushare_api(
                    pro.index_daily,
                    f'index_daily (ts_code={code})',
                    ts_code=code,
                    start_date=start_date,
                    end_date=end_date,
                    fields='ts_code,trade_date,close,open,high,low,pre_close,change,pct_chg,vol,amount'
                )
                
                total_requests += 1
                
                if df.empty:
                    time.sleep(0.2)
                    continue
                
                for _, row in df.iterrows():
                    trade_date = row.get('trade_date')
                    if not trade_date:
                        continue
                    
                    existing = session.query(IndexDaily).filter(
                        IndexDaily.ts_code == code,
                        IndexDaily.trade_date == trade_date
                    ).first()
                    
                    if existing:
                        existing.close = row.get('close')
                        existing.open = row.get('open')
                        existing.high = row.get('high')
                        existing.low = row.get('low')
                        existing.pre_close = row.get('pre_close')
                        existing.change = row.get('change')
                        existing.pct_chg = row.get('pct_chg')
                        existing.vol = row.get('vol')
                        existing.amount = row.get('amount')
                        total_updated += 1
                    else:
                        new_record = IndexDaily(
                            ts_code=code,
                            trade_date=trade_date,
                            close=row.get('close'),
                            open=row.get('open'),
                            high=row.get('high'),
                            low=row.get('low'),
                            pre_close=row.get('pre_close'),
                            change=row.get('change'),
                            pct_chg=row.get('pct_chg'),
                            vol=row.get('vol'),
                            amount=row.get('amount'),
                            created_at=datetime.now()
                        )
                        session.add(new_record)
                        total_new += 1
                
                session.commit()
                
                if (i + 1) % 50 == 0:
                    print(f"已处理 {i + 1}/{len(index_codes)} 个指数")
                
                time.sleep(0.2)  # 控制请求频率
                
            except Exception as e:
                logger.warning(f"获取指数 {code} 的日线行情失败: {e}")
                session.rollback()
                continue
        
        logger.info("=" * 60)
        logger.info(f"指数日线行情更新完成:")
        logger.info(f"  总请求次数: {total_requests}")
        logger.info(f"  新增记录: {total_new} 条")
        logger.info(f"  更新记录: {total_updated} 条")
        print(f"\n" + "=" * 50)
        print(f"指数日线行情更新完成:")
        print(f"  总请求次数: {total_requests}")
        print(f"  新增记录: {total_new} 条")
        print(f"  更新记录: {total_updated} 条")
        print(f"=" * 50)
        
    except Exception as e:
        logger.error(f"获取指数日线行情失败: {e}", exc_info=True)
        print(f"获取指数日线行情失败: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def fetch_index_weekly(ts_code=None, start_date=None, end_date=None):
    """
    获取指数周线行情（index_weekly接口）
    参考: https://tushare.pro/document/2?doc_id=171
    
    Args:
        ts_code: 指数代码，如果为None则获取所有指数
        start_date: 开始日期(YYYYMMDD格式)
        end_date: 结束日期(YYYYMMDD格式)
    """
    logger.info("=" * 60)
    logger.info(f"开始获取指数周线行情 (ts_code={ts_code}, start_date={start_date}, end_date={end_date})")
    logger.info("参考文档: https://tushare.pro/document/2?doc_id=171")
    print("开始获取指数周线行情...")
    
    session = get_session()
    try:
        if ts_code:
            index_codes = [ts_code]
        else:
            index_codes = [row[0] for row in session.query(IndexBasic.ts_code).all()]
        
        if not index_codes:
            print("没有找到需要更新的指数")
            return
        
        print(f"找到 {len(index_codes)} 个指数需要更新周线行情")
        
        total_new = 0
        total_updated = 0
        
        for i, code in enumerate(index_codes):
            try:
                pro = get_pro_api()
                df = call_tushare_api(
                    pro.index_weekly,
                    f'index_weekly (ts_code={code})',
                    ts_code=code,
                    start_date=start_date,
                    end_date=end_date,
                    fields='ts_code,trade_date,close,open,high,low,pre_close,change,pct_chg,vol,amount'
                )
                
                if df.empty:
                    time.sleep(0.2)
                    continue
                
                for _, row in df.iterrows():
                    trade_date = row.get('trade_date')
                    if not trade_date:
                        continue
                    
                    existing = session.query(IndexWeekly).filter(
                        IndexWeekly.ts_code == code,
                        IndexWeekly.trade_date == trade_date
                    ).first()
                    
                    if existing:
                        existing.close = row.get('close')
                        existing.open = row.get('open')
                        existing.high = row.get('high')
                        existing.low = row.get('low')
                        existing.pre_close = row.get('pre_close')
                        existing.change = row.get('change')
                        existing.pct_chg = row.get('pct_chg')
                        existing.vol = row.get('vol')
                        existing.amount = row.get('amount')
                        total_updated += 1
                    else:
                        new_record = IndexWeekly(
                            ts_code=code,
                            trade_date=trade_date,
                            close=row.get('close'),
                            open=row.get('open'),
                            high=row.get('high'),
                            low=row.get('low'),
                            pre_close=row.get('pre_close'),
                            change=row.get('change'),
                            pct_chg=row.get('pct_chg'),
                            vol=row.get('vol'),
                            amount=row.get('amount'),
                            created_at=datetime.now()
                        )
                        session.add(new_record)
                        total_new += 1
                
                session.commit()
                
                if (i + 1) % 50 == 0:
                    print(f"已处理 {i + 1}/{len(index_codes)} 个指数")
                
                time.sleep(0.2)
                
            except Exception as e:
                logger.warning(f"获取指数 {code} 的周线行情失败: {e}")
                session.rollback()
                continue
        
        logger.info(f"指数周线行情更新完成: 新增 {total_new} 条, 更新 {total_updated} 条")
        print(f"指数周线行情更新完成: 新增 {total_new} 条, 更新 {total_updated} 条")
        
    except Exception as e:
        logger.error(f"获取指数周线行情失败: {e}", exc_info=True)
        print(f"获取指数周线行情失败: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def fetch_index_monthly(ts_code=None, start_date=None, end_date=None):
    """
    获取指数月线行情（index_monthly接口）
    参考: https://tushare.pro/document/2?doc_id=172
    
    Args:
        ts_code: 指数代码，如果为None则获取所有指数
        start_date: 开始日期(YYYYMMDD格式)
        end_date: 结束日期(YYYYMMDD格式)
    """
    logger.info("=" * 60)
    logger.info(f"开始获取指数月线行情 (ts_code={ts_code}, start_date={start_date}, end_date={end_date})")
    logger.info("参考文档: https://tushare.pro/document/2?doc_id=172")
    print("开始获取指数月线行情...")
    
    session = get_session()
    try:
        if ts_code:
            index_codes = [ts_code]
        else:
            index_codes = [row[0] for row in session.query(IndexBasic.ts_code).all()]
        
        if not index_codes:
            print("没有找到需要更新的指数")
            return
        
        print(f"找到 {len(index_codes)} 个指数需要更新月线行情")
        
        total_new = 0
        total_updated = 0
        
        for i, code in enumerate(index_codes):
            try:
                pro = get_pro_api()
                df = call_tushare_api(
                    pro.index_monthly,
                    f'index_monthly (ts_code={code})',
                    ts_code=code,
                    start_date=start_date,
                    end_date=end_date,
                    fields='ts_code,trade_date,close,open,high,low,pre_close,change,pct_chg,vol,amount'
                )
                
                if df.empty:
                    time.sleep(0.2)
                    continue
                
                for _, row in df.iterrows():
                    trade_date = row.get('trade_date')
                    if not trade_date:
                        continue
                    
                    existing = session.query(IndexMonthly).filter(
                        IndexMonthly.ts_code == code,
                        IndexMonthly.trade_date == trade_date
                    ).first()
                    
                    if existing:
                        existing.close = row.get('close')
                        existing.open = row.get('open')
                        existing.high = row.get('high')
                        existing.low = row.get('low')
                        existing.pre_close = row.get('pre_close')
                        existing.change = row.get('change')
                        existing.pct_chg = row.get('pct_chg')
                        existing.vol = row.get('vol')
                        existing.amount = row.get('amount')
                        total_updated += 1
                    else:
                        new_record = IndexMonthly(
                            ts_code=code,
                            trade_date=trade_date,
                            close=row.get('close'),
                            open=row.get('open'),
                            high=row.get('high'),
                            low=row.get('low'),
                            pre_close=row.get('pre_close'),
                            change=row.get('change'),
                            pct_chg=row.get('pct_chg'),
                            vol=row.get('vol'),
                            amount=row.get('amount'),
                            created_at=datetime.now()
                        )
                        session.add(new_record)
                        total_new += 1
                
                session.commit()
                
                if (i + 1) % 50 == 0:
                    print(f"已处理 {i + 1}/{len(index_codes)} 个指数")
                
                time.sleep(0.2)
                
            except Exception as e:
                logger.warning(f"获取指数 {code} 的月线行情失败: {e}")
                session.rollback()
                continue
        
        logger.info(f"指数月线行情更新完成: 新增 {total_new} 条, 更新 {total_updated} 条")
        print(f"指数月线行情更新完成: 新增 {total_new} 条, 更新 {total_updated} 条")
        
    except Exception as e:
        logger.error(f"获取指数月线行情失败: {e}", exc_info=True)
        print(f"获取指数月线行情失败: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def fetch_index_weight(index_code=None, trade_date=None, start_date=None, end_date=None):
    """
    获取指数成分股权重（index_weight接口）
    参考: https://tushare.pro/document/2?doc_id=96
    
    Args:
        index_code: 指数代码，如果为None则获取所有主要指数
        trade_date: 交易日期(YYYYMMDD格式)，如果为None则获取最新日期
        start_date: 开始日期(YYYYMMDD格式)
        end_date: 结束日期(YYYYMMDD格式)
    """
    logger.info("=" * 60)
    logger.info(f"开始获取指数成分股权重 (index_code={index_code}, trade_date={trade_date}, start_date={start_date}, end_date={end_date})")
    logger.info("参考文档: https://tushare.pro/document/2?doc_id=96")
    print("开始获取指数成分股权重...")
    print("参考文档: https://tushare.pro/document/2?doc_id=96")
    
    session = get_session()
    try:
        # 获取需要更新的指数代码列表
        if index_code:
            index_codes = [index_code]
        else:
            # 获取主要指数代码（沪深300、中证500、上证50等）
            main_indices = ['399300.SZ', '000300.SH', '399905.SZ', '000905.SH', '000016.SH']
            # 也可以从数据库获取所有指数
            all_indices = [row[0] for row in session.query(IndexBasic.ts_code).all()]
            # 优先使用主要指数，如果没有则使用数据库中的指数
            index_codes = main_indices if all_indices else all_indices[:10]  # 限制数量避免请求过多
        
        if not index_codes:
            print("没有找到需要更新的指数")
            return
        
        print(f"找到 {len(index_codes)} 个指数需要更新成分股权重")
        
        # 如果没有指定日期，使用当前日期
        if not trade_date and not start_date:
            trade_date = datetime.now().strftime('%Y%m%d')
        
        total_new = 0
        total_updated = 0
        total_requests = 0
        
        for i, code in enumerate(index_codes):
            try:
                pro = get_pro_api()
                
                # 如果指定了trade_date，使用单日期查询
                if trade_date:
                    df = call_tushare_api(
                        pro.index_weight,
                        f'index_weight (index_code={code}, trade_date={trade_date})',
                        index_code=code,
                        trade_date=trade_date
                    )
                else:
                    # 使用日期范围查询
                    if not start_date:
                        # 默认获取最近一个月的数据
                        from datetime import timedelta
                        end_date = datetime.now().strftime('%Y%m%d')
                        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
                    
                    df = call_tushare_api(
                        pro.index_weight,
                        f'index_weight (index_code={code}, start_date={start_date}, end_date={end_date})',
                        index_code=code,
                        start_date=start_date,
                        end_date=end_date
                    )
                
                total_requests += 1
                
                if df.empty:
                    logger.warning(f"指数 {code} 没有成分股权重数据")
                    time.sleep(0.3)
                    continue
                
                print(f"指数 {code} 获取到 {len(df)} 条成分股权重数据")
                
                for _, row in df.iterrows():
                    trade_date_val = row.get('trade_date')
                    con_code_val = row.get('con_code')
                    weight_val = row.get('weight')
                    
                    if not trade_date_val or not con_code_val:
                        continue
                    
                    # 查找现有记录
                    existing = session.query(IndexWeight).filter(
                        IndexWeight.index_code == code,
                        IndexWeight.con_code == con_code_val,
                        IndexWeight.trade_date == trade_date_val
                    ).first()
                    
                    if existing:
                        # 更新权重
                        existing.weight = weight_val
                        total_updated += 1
                    else:
                        # 新增记录
                        new_record = IndexWeight(
                            index_code=code,
                            con_code=con_code_val,
                            trade_date=trade_date_val,
                            weight=weight_val,
                            created_at=datetime.now()
                        )
                        session.add(new_record)
                        total_new += 1
                
                session.commit()
                
                if (i + 1) % 10 == 0:
                    print(f"已处理 {i + 1}/{len(index_codes)} 个指数")
                
                time.sleep(0.5)  # 控制请求频率（该接口需要2000积分，限速较严格）
                
            except TusharePermissionError as e:
                logger.error(f"接口权限不足: {e.api_name}")
                print(f"❌ 接口权限不足: {e.api_name}")
                print(f"提示: index_weight接口需要至少2000积分")
                break
            except Exception as e:
                logger.warning(f"获取指数 {code} 的成分股权重失败: {e}")
                session.rollback()
                continue
        
        logger.info("=" * 60)
        logger.info(f"指数成分股权重更新完成:")
        logger.info(f"  总请求次数: {total_requests}")
        logger.info(f"  新增记录: {total_new} 条")
        logger.info(f"  更新记录: {total_updated} 条")
        print(f"\n" + "=" * 50)
        print(f"指数成分股权重更新完成:")
        print(f"  总请求次数: {total_requests}")
        print(f"  新增记录: {total_new} 条")
        print(f"  更新记录: {total_updated} 条")
        print(f"=" * 50)
        
    except TusharePermissionError as e:
        logger.error(f"接口权限不足: {e.api_name}")
        print(f"❌ 接口权限不足: {e.api_name}")
        return
    except Exception as e:
        logger.error(f"获取指数成分股权重失败: {e}", exc_info=True)
        print(f"获取指数成分股权重失败: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def fetch_index_dailybasic(ts_code=None, start_date=None, end_date=None):
    """
    获取指数每日指标（index_dailybasic接口）并更新到index_daily表
    参考: https://tushare.pro/document/2?doc_id=128
    
    Args:
        ts_code: 指数代码，如果为None则获取所有指数
        start_date: 开始日期(YYYYMMDD格式)
        end_date: 结束日期(YYYYMMDD格式)
    """
    logger.info("=" * 60)
    logger.info(f"开始获取指数每日指标 (ts_code={ts_code}, start_date={start_date}, end_date={end_date})")
    logger.info("参考文档: https://tushare.pro/document/2?doc_id=128")
    print("开始获取指数每日指标...")
    print("参考文档: https://tushare.pro/document/2?doc_id=128")
    
    session = get_session()
    try:
        # 获取需要更新的指数代码列表
        if ts_code:
            index_codes = [ts_code]
        else:
            # 获取所有指数代码
            index_codes = [row[0] for row in session.query(IndexBasic.ts_code).all()]
        
        if not index_codes:
            print("没有找到需要更新的指数")
            return
        
        print(f"找到 {len(index_codes)} 个指数需要更新每日指标")
        
        total_updated = 0
        total_requests = 0
        
        # Tushare限速：每分钟120次
        MAX_REQUESTS_PER_MINUTE = 120
        REQUEST_INTERVAL = 0.5  # 基础请求间隔（秒）
        request_count = 0
        minute_start_time = time.time()
        
        for i, code in enumerate(index_codes):
            try:
                # 检查是否需要等待（每分钟120次限制）
                current_time = time.time()
                elapsed = current_time - minute_start_time
                
                if elapsed >= 60:
                    # 重置计数器
                    request_count = 0
                    minute_start_time = current_time
                    logger.info(f"限速窗口重置，已处理 {i}/{len(index_codes)} 个指数")
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
                    pro.index_dailybasic,
                    f'index_dailybasic (ts_code={code})',
                    ts_code=code,
                    start_date=start_date,
                    end_date=end_date,
                    fields='ts_code,trade_date,total_mv,float_mv,turnover_rate,pe,pb'
                )
                
                request_count += 1
                total_requests += 1
                
                if df.empty:
                    time.sleep(REQUEST_INTERVAL)
                    continue
                
                # 更新index_daily表中的每日指标字段
                for _, row in df.iterrows():
                    trade_date = row.get('trade_date')
                    if not trade_date:
                        continue
                    
                    # 查找对应的index_daily记录
                    existing = session.query(IndexDaily).filter(
                        IndexDaily.ts_code == code,
                        IndexDaily.trade_date == trade_date
                    ).first()
                    
                    if existing:
                        # 更新每日指标字段
                        existing.total_mv = row.get('total_mv')
                        existing.float_mv = row.get('float_mv')
                        existing.turnover_rate = row.get('turnover_rate')
                        existing.pe = row.get('pe')
                        existing.pb = row.get('pb')
                        total_updated += 1
                    else:
                        # 如果index_daily表中没有该记录，记录警告但不创建新记录
                        # （因为index_daily应该先通过fetch_index_daily获取基础行情数据）
                        logger.warning(f"指数 {code} 在 {trade_date} 的日线行情数据不存在，跳过每日指标更新")
                
                session.commit()
                
                if (i + 1) % 50 == 0:
                    print(f"已处理 {i + 1}/{len(index_codes)} 个指数")
                
                time.sleep(REQUEST_INTERVAL)
                
            except TusharePermissionError as e:
                logger.error(f"接口权限不足: {e.api_name}")
                print(f"❌ 接口权限不足: {e.api_name}")
                break
            except Exception as e:
                logger.warning(f"获取指数 {code} 的每日指标失败: {e}")
                session.rollback()
                continue
        
        logger.info("=" * 60)
        logger.info(f"指数每日指标更新完成:")
        logger.info(f"  总请求次数: {total_requests}")
        logger.info(f"  更新记录: {total_updated} 条")
        print(f"\n" + "=" * 50)
        print(f"指数每日指标更新完成:")
        print(f"  总请求次数: {total_requests}")
        print(f"  更新记录: {total_updated} 条")
        print(f"=" * 50)
        
    except TusharePermissionError as e:
        logger.error(f"接口权限不足: {e.api_name}")
        print(f"❌ 接口权限不足: {e.api_name}")
        return
    except Exception as e:
        logger.error(f"获取指数每日指标失败: {e}", exc_info=True)
        print(f"获取指数每日指标失败: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def fetch_all_data():
    """获取所有数据（首次运行使用）"""
    print("=" * 50)
    print("开始获取所有股票数据")
    print("=" * 50)
    
    # 1. 获取股票基本信息
    fetch_stock_basic()
    
    # 2. 获取上市公司详细信息（补充到 stock_basic）
    fetch_stock_company()
    
    # 3. 获取盘前股本信息（补充到 stock_basic）
    fetch_stock_premarket()
    
    # 4. 获取日线数据（最近一年）
    fetch_stock_daily()
    
    # 5. 获取周线数据（最近两年）
    fetch_stock_weekly()
    
    # 6. 获取月线数据（最近十年）
    fetch_stock_monthly()
    
    # 7. 获取资金流向数据（最近一个月）
    fetch_stock_moneyflow()
    
    # 8. 获取指标数据（最近一个月）
    fetch_stock_indicator()
    
    # 9. 获取IPO新股数据（最近一年）
    fetch_ipo_stocks()
    
    print("=" * 50)
    print("所有数据获取完成！")
    print("=" * 50)


if __name__ == '__main__':
    # 可以单独测试某个功能
    # fetch_stock_basic()
    # fetch_stock_daily()
    fetch_all_data()

