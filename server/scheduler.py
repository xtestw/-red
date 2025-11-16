#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
定时任务调度器
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import sys
import os
import argparse

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.data_fetcher import (
    fetch_stock_basic,
    fetch_stock_company,
    fetch_stock_daily,
    fetch_stock_weekly,
    fetch_stock_monthly,
    fetch_stock_moneyflow,
    fetch_stock_indicator,
    fetch_ipo_stocks
)


def job_fetch_stock_basic():
    """每日更新股票基本信息（交易日15:30执行）"""
    print(f"[{datetime.now()}] 开始执行：更新股票基本信息")
    try:
        fetch_stock_basic()
        print(f"[{datetime.now()}] 完成：更新股票基本信息")
    except Exception as e:
        print(f"[{datetime.now()}] 错误：更新股票基本信息失败 - {e}")


def job_fetch_stock_company():
    """更新上市公司详细信息（启动时和每周执行）"""
    print(f"[{datetime.now()}] 开始执行：更新上市公司详细信息")
    try:
        fetch_stock_company()
        print(f"[{datetime.now()}] 完成：更新上市公司详细信息")
    except Exception as e:
        print(f"[{datetime.now()}] 错误：更新上市公司详细信息失败 - {e}")


def job_fetch_daily_data():
    """每日更新日线数据（交易日15:30执行）"""
    print(f"[{datetime.now()}] 开始执行：更新日线数据")
    try:
        # 只获取最近5天的数据
        from datetime import timedelta
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
        fetch_stock_daily(start_date=start_date, end_date=end_date)
        print(f"[{datetime.now()}] 完成：更新日线数据")
    except Exception as e:
        print(f"[{datetime.now()}] 错误：更新日线数据失败 - {e}")


def job_fetch_weekly_data():
    """每周更新周线数据（每周日20:00执行）"""
    print(f"[{datetime.now()}] 开始执行：更新周线数据")
    try:
        from datetime import timedelta
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        fetch_stock_weekly(start_date=start_date, end_date=end_date)
        print(f"[{datetime.now()}] 完成：更新周线数据")
    except Exception as e:
        print(f"[{datetime.now()}] 错误：更新周线数据失败 - {e}")


def job_fetch_monthly_data():
    """每月更新月线数据（每月1日20:00执行）"""
    print(f"[{datetime.now()}] 开始执行：更新月线数据")
    try:
        from datetime import timedelta
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
        fetch_stock_monthly(start_date=start_date, end_date=end_date)
        print(f"[{datetime.now()}] 完成：更新月线数据")
    except Exception as e:
        print(f"[{datetime.now()}] 错误：更新月线数据失败 - {e}")


def job_fetch_moneyflow():
    """每日更新资金流向数据（交易日15:30执行）"""
    print(f"[{datetime.now()}] 开始执行：更新资金流向数据")
    try:
        from datetime import timedelta
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
        fetch_stock_moneyflow(start_date=start_date, end_date=end_date)
        print(f"[{datetime.now()}] 完成：更新资金流向数据")
    except Exception as e:
        print(f"[{datetime.now()}] 错误：更新资金流向数据失败 - {e}")


def job_fetch_indicator():
    """每日更新股票指标数据（交易日15:30执行）"""
    print(f"[{datetime.now()}] 开始执行：更新股票指标数据")
    try:
        from datetime import timedelta
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
        fetch_stock_indicator(start_date=start_date, end_date=end_date)
        print(f"[{datetime.now()}] 完成：更新股票指标数据")
    except Exception as e:
        print(f"[{datetime.now()}] 错误：更新股票指标数据失败 - {e}")


def job_fetch_ipo_stocks():
    """每日更新IPO新股数据（交易日15:30执行）"""
    print(f"[{datetime.now()}] 开始执行：更新IPO新股数据")
    try:
        from datetime import timedelta
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')  # 获取最近3个月的IPO数据
        fetch_ipo_stocks(start_date=start_date, end_date=end_date)
        print(f"[{datetime.now()}] 完成：更新IPO新股数据")
    except Exception as e:
        print(f"[{datetime.now()}] 错误：更新IPO新股数据失败 - {e}")


def run_all_jobs_now():
    """立即执行所有任务"""
    print("=" * 50)
    print("立即执行所有任务")
    print("=" * 50)
    
    jobs = [
        ("更新股票基本信息", job_fetch_stock_basic),
        ("更新上市公司详细信息", job_fetch_stock_company),
        ("更新日线数据", job_fetch_daily_data),
        ("更新资金流向数据", job_fetch_moneyflow),
        ("更新股票指标数据", job_fetch_indicator),
        ("更新周线数据", job_fetch_weekly_data),
        ("更新月线数据", job_fetch_monthly_data),
        ("更新IPO新股数据", job_fetch_ipo_stocks),
    ]
    
    for job_name, job_func in jobs:
        print(f"\n[{datetime.now()}] 开始执行：{job_name}")
        try:
            job_func()
            print(f"[{datetime.now()}] 完成：{job_name}")
        except Exception as e:
            print(f"[{datetime.now()}] 错误：{job_name}失败 - {e}")
    
    print("\n" + "=" * 50)
    print("所有任务执行完成")
    print("=" * 50)


def start_scheduler(run_now=False):
    """启动定时任务调度器
    
    Args:
        run_now: 是否在启动时立即执行所有任务
    """
    # 如果设置了立即执行，先执行所有任务
    if run_now:
        run_all_jobs_now()
        print("\n任务执行完成，开始启动定时调度器...\n")
    else:
        # 即使不立即执行所有任务，也先更新公司信息（补充完善数据库字段）
        print("启动时自动补充完善数据库字段（上市公司详细信息）...")
        try:
            job_fetch_stock_company()
            print("数据库字段补充完成\n")
        except Exception as e:
            print(f"数据库字段补充失败: {e}\n")
    
    scheduler = BlockingScheduler()
    
    # 每日15:30执行（交易日数据更新）
    scheduler.add_job(
        job_fetch_stock_basic,
        trigger=CronTrigger(hour=15, minute=30),
        id='fetch_stock_basic',
        name='更新股票基本信息',
        replace_existing=True
    )
    
    # 每周日21:00执行（更新上市公司详细信息，频率较低因为变化不大）
    scheduler.add_job(
        job_fetch_stock_company,
        trigger=CronTrigger(day_of_week='sun', hour=21, minute=0),
        id='fetch_stock_company',
        name='更新上市公司详细信息',
        replace_existing=True
    )
    
    scheduler.add_job(
        job_fetch_daily_data,
        trigger=CronTrigger(hour=15, minute=30),
        id='fetch_daily_data',
        name='更新日线数据',
        replace_existing=True
    )
    
    scheduler.add_job(
        job_fetch_moneyflow,
        trigger=CronTrigger(hour=15, minute=30),
        id='fetch_moneyflow',
        name='更新资金流向数据',
        replace_existing=True
    )
    
    scheduler.add_job(
        job_fetch_indicator,
        trigger=CronTrigger(hour=15, minute=30),
        id='fetch_indicator',
        name='更新股票指标数据',
        replace_existing=True
    )
    
    scheduler.add_job(
        job_fetch_ipo_stocks,
        trigger=CronTrigger(hour=15, minute=30),
        id='fetch_ipo_stocks',
        name='更新IPO新股数据',
        replace_existing=True
    )
    
    # 每周日20:00执行
    scheduler.add_job(
        job_fetch_weekly_data,
        trigger=CronTrigger(day_of_week='sun', hour=20, minute=0),
        id='fetch_weekly_data',
        name='更新周线数据',
        replace_existing=True
    )
    
    # 每月1日20:00执行
    scheduler.add_job(
        job_fetch_monthly_data,
        trigger=CronTrigger(day=1, hour=20, minute=0),
        id='fetch_monthly_data',
        name='更新月线数据',
        replace_existing=True
    )
    
    print("=" * 50)
    print("定时任务调度器已启动")
    print("=" * 50)
    print("已配置的任务：")
    for job in scheduler.get_jobs():
        print(f"  - {job.name} (ID: {job.id})")
    print("=" * 50)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n定时任务调度器已停止")
        scheduler.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='股票数据定时任务调度器')
    parser.add_argument(
        '--run-now',
        action='store_true',
        help='启动时立即执行所有任务，然后再进行自动调度'
    )
    parser.add_argument(
        '--immediate',
        action='store_true',
        dest='run_now',
        help='启动时立即执行所有任务（--run-now的别名）'
    )
    
    args = parser.parse_args()
    start_scheduler(run_now=args.run_now)


