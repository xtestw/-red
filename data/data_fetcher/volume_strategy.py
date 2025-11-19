#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
放量策略选股
近3天成交量最大值，是近240天、120天、60天、30天最大的
"""
import sys
import os
from datetime import datetime, timedelta
import logging

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_session, StockBasic, StockDaily, StockSelection
from sqlalchemy import func, and_

# 配置日志
logger = logging.getLogger(__name__)


def calculate_volume_strategy(trade_date=None):
    """
    计算放量策略选股
    
    策略逻辑：
    - 近3天成交量最大值
    - 是近240天、120天、60天、30天最大的
    
    Args:
        trade_date: 选股日期，格式YYYYMMDD，如果为None则使用最新交易日
    
    Returns:
        list: 选中的股票列表，每个元素包含 ts_code, score, reason
    """
    session = get_session()
    try:
        # 如果没有指定日期，使用最新交易日
        if not trade_date:
            latest_date = session.query(func.max(StockDaily.trade_date)).scalar()
            if not latest_date:
                logger.warning("没有找到交易数据")
                return []
            trade_date = latest_date
        
        logger.info(f"开始执行放量策略选股，日期: {trade_date}")
        
        # 将日期字符串转换为datetime对象，方便计算
        trade_dt = datetime.strptime(trade_date, '%Y%m%d')
        
        # 计算各个时间段的起始日期
        # 近3天
        days_3_start = trade_dt - timedelta(days=5)  # 多取几天，确保有3个交易日
        days_3_start_str = days_3_start.strftime('%Y%m%d')
        
        # 近30天
        days_30_start = trade_dt - timedelta(days=45)  # 多取几天，确保有30个交易日
        days_30_start_str = days_30_start.strftime('%Y%m%d')
        
        # 近60天
        days_60_start = trade_dt - timedelta(days=90)
        days_60_start_str = days_60_start.strftime('%Y%m%d')
        
        # 近120天
        days_120_start = trade_dt - timedelta(days=180)
        days_120_start_str = days_120_start.strftime('%Y%m%d')
        
        # 近240天
        days_240_start = trade_dt - timedelta(days=360)
        days_240_start_str = days_240_start.strftime('%Y%m%d')
        
        # 获取所有股票代码
        stocks = session.query(StockBasic.ts_code).all()
        stock_codes = [stock[0] for stock in stocks]
        
        logger.info(f"开始筛选 {len(stock_codes)} 只股票")
        
        selected_stocks = []
        processed = 0
        
        for ts_code in stock_codes:
            processed += 1
            if processed % 500 == 0:
                logger.info(f"已处理 {processed}/{len(stock_codes)} 只股票")
            
            try:
                # 获取近3天的数据
                recent_3_days = session.query(StockDaily).filter(
                    and_(
                        StockDaily.ts_code == ts_code,
                        StockDaily.trade_date >= days_3_start_str,
                        StockDaily.trade_date <= trade_date
                    )
                ).order_by(StockDaily.trade_date.desc()).limit(3).all()
                
                if not recent_3_days or len(recent_3_days) < 3:
                    continue
                
                # 计算近3天成交量最大值，并记录对应的日期
                max_vol_3_days = 0
                max_vol_3_date = None
                for d in recent_3_days:
                    if d.vol and d.vol > 0:
                        if d.vol > max_vol_3_days:
                            max_vol_3_days = d.vol
                            max_vol_3_date = d.trade_date
                
                if max_vol_3_days == 0 or not max_vol_3_date:
                    continue
                
                # 获取近30天的数据
                recent_30_days = session.query(StockDaily).filter(
                    and_(
                        StockDaily.ts_code == ts_code,
                        StockDaily.trade_date >= days_30_start_str,
                        StockDaily.trade_date <= trade_date
                    )
                ).all()
                
                if not recent_30_days:
                    continue
                
                vol_30_days = [d.vol for d in recent_30_days if d.vol and d.vol > 0]
                if not vol_30_days:
                    continue
                max_vol_30_days = max(vol_30_days)
                
                # 获取近60天的数据
                recent_60_days = session.query(StockDaily).filter(
                    and_(
                        StockDaily.ts_code == ts_code,
                        StockDaily.trade_date >= days_60_start_str,
                        StockDaily.trade_date <= trade_date
                    )
                ).all()
                
                if not recent_60_days:
                    continue
                
                vol_60_days = [d.vol for d in recent_60_days if d.vol and d.vol > 0]
                if not vol_60_days:
                    continue
                max_vol_60_days = max(vol_60_days)
                
                # 获取近120天的数据
                recent_120_days = session.query(StockDaily).filter(
                    and_(
                        StockDaily.ts_code == ts_code,
                        StockDaily.trade_date >= days_120_start_str,
                        StockDaily.trade_date <= trade_date
                    )
                ).all()
                
                if not recent_120_days:
                    continue
                
                vol_120_days = [d.vol for d in recent_120_days if d.vol and d.vol > 0]
                if not vol_120_days:
                    continue
                max_vol_120_days = max(vol_120_days)
                
                # 获取近240天的数据
                recent_240_days = session.query(StockDaily).filter(
                    and_(
                        StockDaily.ts_code == ts_code,
                        StockDaily.trade_date >= days_240_start_str,
                        StockDaily.trade_date <= trade_date
                    )
                ).all()
                
                if not recent_240_days:
                    continue
                
                vol_240_days = [d.vol for d in recent_240_days if d.vol and d.vol > 0]
                if not vol_240_days:
                    continue
                max_vol_240_days = max(vol_240_days)
                
                # 检查条件：近3天成交量最大值是近240天、120天、60天、30天最大的
                # 这意味着近3天的最大成交量必须 >= 近30/60/120/240天的最大成交量
                if (max_vol_3_days >= max_vol_30_days and 
                    max_vol_3_days >= max_vol_60_days and 
                    max_vol_3_days >= max_vol_120_days and 
                    max_vol_3_days >= max_vol_240_days):
                    
                    # 计算评分：基于放量倍数
                    score_30 = max_vol_3_days / max_vol_30_days if max_vol_30_days > 0 else 0
                    score_60 = max_vol_3_days / max_vol_60_days if max_vol_60_days > 0 else 0
                    score_120 = max_vol_3_days / max_vol_120_days if max_vol_120_days > 0 else 0
                    score_240 = max_vol_3_days / max_vol_240_days if max_vol_240_days > 0 else 0
                    
                    # 综合评分（加权平均）
                    score = (score_30 * 0.1 + score_60 * 0.2 + score_120 * 0.3 + score_240 * 0.4) * 100
                    
                    # 判断是哪个时间段的最大量（找出倍数最大的）
                    periods = [
                        ('30天', score_30, max_vol_30_days),
                        ('60天', score_60, max_vol_60_days),
                        ('120天', score_120, max_vol_120_days),
                        ('240天', score_240, max_vol_240_days)
                    ]
                    
                    # 找出倍数最大的时间段
                    max_period = max(periods, key=lambda x: x[1])
                    max_period_name = max_period[0]
                    max_period_score = max_period[1]
                    
                    # 找出所有达到最大量的时间段
                    max_periods = [p[0] for p in periods if p[1] >= 1.0]
                    
                    # 格式化日期显示（YYYYMMDD -> YYYY-MM-DD）
                    max_vol_date_str = max_vol_3_date
                    if len(max_vol_3_date) == 8:
                        max_vol_date_str = f"{max_vol_3_date[:4]}-{max_vol_3_date[4:6]}-{max_vol_3_date[6:8]}"
                    
                    # 判断是哪个时间段的最高成交量（优先级：240天 > 120天 > 60天 > 30天）
                    is_240_max = score_240 >= 1.0
                    is_120_max = score_120 >= 1.0 and not is_240_max
                    is_60_max = score_60 >= 1.0 and not is_240_max and not is_120_max
                    is_30_max = score_30 >= 1.0 and not is_240_max and not is_120_max and not is_60_max
                    
                    # 生成选股理由，明确标注是哪个时间段的最大量，并显示具体日期
                    if is_240_max:
                        reason = (
                            f"{max_vol_date_str}成交量{max_vol_3_days:.0f}手，"
                            f"是240天最高成交量({score_240:.2f}倍)"
                        )
                    elif is_120_max:
                        reason = (
                            f"{max_vol_date_str}成交量{max_vol_3_days:.0f}手，"
                            f"是120天最高成交量({score_120:.2f}倍)"
                        )
                    elif is_60_max:
                        reason = (
                            f"{max_vol_date_str}成交量{max_vol_3_days:.0f}手，"
                            f"是60天最高成交量({score_60:.2f}倍)"
                        )
                    elif is_30_max:
                        reason = (
                            f"{max_vol_date_str}成交量{max_vol_3_days:.0f}手，"
                            f"是30天最高成交量({score_30:.2f}倍)"
                        )
                    elif len(max_periods) == 4:
                        reason = (
                            f"{max_vol_date_str}成交量{max_vol_3_days:.0f}手，"
                            f"同时是近30天/60天/120天/240天的最大量，"
                            f"分别是{score_30:.2f}/{score_60:.2f}/{score_120:.2f}/{score_240:.2f}倍"
                        )
                    elif len(max_periods) > 1:
                        periods_str = '/'.join(max_periods)
                        reason = (
                            f"{max_vol_date_str}成交量{max_vol_3_days:.0f}手，"
                            f"是近{periods_str}的最大量，"
                            f"其中{max_period_name}倍数最高({max_period_score:.2f}倍)"
                        )
                    else:
                        reason = (
                            f"{max_vol_date_str}成交量{max_vol_3_days:.0f}手，"
                            f"是近{max_period_name}的最大量({max_period_score:.2f}倍)，"
                            f"同时超过近30天/60天/120天/240天的最大值"
                        )
                    
                    selected_stocks.append({
                        'ts_code': ts_code,
                        'score': score,
                        'reason': reason
                    })
                    
            except Exception as e:
                logger.debug(f"处理股票 {ts_code} 时出错: {e}")
                continue
        
        # 按评分排序
        selected_stocks.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"放量策略选股完成，共选出 {len(selected_stocks)} 只股票")
        
        return selected_stocks
        
    except Exception as e:
        logger.error(f"放量策略选股失败: {e}", exc_info=True)
        raise
    finally:
        session.close()


def save_volume_strategy_selections(trade_date=None):
    """
    执行放量策略选股并保存到数据库
    
    Args:
        trade_date: 选股日期，格式YYYYMMDD，如果为None则使用最新交易日
    
    Returns:
        int: 保存的选股数量
    """
    session = get_session()
    try:
        # 执行选股
        selected_stocks = calculate_volume_strategy(trade_date)
        
        if not selected_stocks:
            logger.warning("没有选出符合条件的股票")
            return 0
        
        # 如果没有指定日期，使用最新交易日
        if not trade_date:
            trade_date = session.query(func.max(StockDaily.trade_date)).scalar()
        
        strategy_name = "放量策略"
        saved_count = 0
        
        for stock in selected_stocks:
            try:
                # 检查是否已存在
                existing = session.query(StockSelection).filter_by(
                    ts_code=stock['ts_code'],
                    strategy_name=strategy_name,
                    trade_date=trade_date
                ).first()
                
                if existing:
                    # 更新现有记录
                    existing.score = stock['score']
                    existing.reason = stock['reason']
                    existing.created_at = datetime.now()
                else:
                    # 创建新记录
                    selection = StockSelection(
                        ts_code=stock['ts_code'],
                        strategy_name=strategy_name,
                        trade_date=trade_date,
                        score=stock['score'],
                        reason=stock['reason'],
                        created_at=datetime.now()
                    )
                    session.add(selection)
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"保存选股结果失败 {stock['ts_code']}: {e}")
                session.rollback()
                continue
        
        session.commit()
        logger.info(f"成功保存 {saved_count} 条放量策略选股结果到数据库")
        
        return saved_count
        
    except Exception as e:
        session.rollback()
        logger.error(f"保存放量策略选股结果失败: {e}", exc_info=True)
        raise
    finally:
        session.close()


if __name__ == '__main__':
    # 测试代码
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("开始执行放量策略选股...")
    count = save_volume_strategy_selections()
    print(f"选股完成，共保存 {count} 条记录")

