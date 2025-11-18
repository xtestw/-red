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
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 添加项目根目录到路径（scheduler.py 在 data/data_fetcher/ 中，需要往上两级到项目根目录）
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 由于 scheduler.py 和 data_fetcher.py 在同一个目录中，可以直接导入
from data_fetcher import (
    fetch_stock_basic,
    fetch_stock_company,
    fetch_stock_daily,
    fetch_stock_weekly,
    fetch_stock_monthly,
    fetch_stock_moneyflow,
    fetch_stock_indicator,
    fetch_ipo_stocks
)
from volume_strategy import save_volume_strategy_selections


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


def job_fetch_daily_data(all_data=False):
    """每日更新日线数据（交易日15:30执行）
    
    Args:
        all_data: 如果为True，获取所有历史数据；否则只获取最近5天的数据
    """
    print(f"[{datetime.now()}] 开始执行：更新日线数据")
    try:
        from datetime import timedelta
        end_date = datetime.now().strftime('%Y%m%d')
        
        if all_data:
            # 获取最近4000天的历史数据
            start_date = (datetime.now() - timedelta(days=6000)).strftime('%Y%m%d')
            print(f"[{datetime.now()}] 使用全量模式：获取最近6000天历史数据（{start_date} 至 {end_date}）")
        else:
            # 只获取最近5天的数据
            start_date = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
            print(f"[{datetime.now()}] 使用增量模式：获取最近5天数据（{start_date} 至 {end_date}）")
        
        fetch_stock_daily(start_date=start_date, end_date=end_date)
        print(f"[{datetime.now()}] 完成：更新日线数据")
    except Exception as e:
        print(f"[{datetime.now()}] 错误：更新日线数据失败 - {e}")


def job_fetch_weekly_data(all_data=False):
    """每周更新周线数据（每周日20:00执行）
    
    Args:
        all_data: 如果为True，获取所有历史数据；否则只获取最近30天的数据
    """
    print(f"[{datetime.now()}] 开始执行：更新周线数据")
    try:
        from datetime import timedelta
        end_date = datetime.now().strftime('%Y%m%d')
        
        if all_data:
            # 获取最近10年的历史数据（约2600周）
            start_date = (datetime.now() - timedelta(days=3650)).strftime('%Y%m%d')
            print(f"[{datetime.now()}] 使用全量模式：获取最近10年周线数据（{start_date} 至 {end_date}）")
        else:
            # 只获取最近30天的数据
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            print(f"[{datetime.now()}] 使用增量模式：获取最近30天周线数据（{start_date} 至 {end_date}）")
        
        fetch_stock_weekly(start_date=start_date, end_date=end_date)
        print(f"[{datetime.now()}] 完成：更新周线数据")
    except Exception as e:
        print(f"[{datetime.now()}] 错误：更新周线数据失败 - {e}")


def job_fetch_monthly_data(all_data=False):
    """每月更新月线数据（每月1日20:00执行）
    
    Args:
        all_data: 如果为True，获取所有历史数据；否则只获取最近90天的数据
    """
    print(f"[{datetime.now()}] 开始执行：更新月线数据")
    try:
        from datetime import timedelta
        end_date = datetime.now().strftime('%Y%m%d')
        
        if all_data:
            # 获取最近20年的历史数据（约240个月）
            start_date = (datetime.now() - timedelta(days=7300)).strftime('%Y%m%d')
            print(f"[{datetime.now()}] 使用全量模式：获取最近20年月线数据（{start_date} 至 {end_date}）")
        else:
            # 只获取最近90天的数据
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
            print(f"[{datetime.now()}] 使用增量模式：获取最近90天月线数据（{start_date} 至 {end_date}）")
        
        fetch_stock_monthly(start_date=start_date, end_date=end_date)
        print(f"[{datetime.now()}] 完成：更新月线数据")
    except Exception as e:
        print(f"[{datetime.now()}] 错误：更新月线数据失败 - {e}")


def job_fetch_moneyflow(all_data=False):
    """每日更新资金流向数据（交易日15:30执行）
    
    Args:
        all_data: 如果为True，获取所有历史数据；否则只获取最近5天的数据
    """
    print(f"[{datetime.now()}] 开始执行：更新资金流向数据")
    try:
        from datetime import timedelta
        end_date = datetime.now().strftime('%Y%m%d')
        
        if all_data:
            # 获取最近3年的历史数据
            start_date = (datetime.now() - timedelta(days=1095)).strftime('%Y%m%d')
            print(f"[{datetime.now()}] 使用全量模式：获取最近3年资金流向数据（{start_date} 至 {end_date}）")
        else:
            # 只获取最近5天的数据
        start_date = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
            print(f"[{datetime.now()}] 使用增量模式：获取最近5天资金流向数据（{start_date} 至 {end_date}）")
        
        fetch_stock_moneyflow(start_date=start_date, end_date=end_date)
        print(f"[{datetime.now()}] 完成：更新资金流向数据")
    except Exception as e:
        print(f"[{datetime.now()}] 错误：更新资金流向数据失败 - {e}")


def job_fetch_indicator(all_data=False):
    """每日更新股票指标数据（交易日15:30执行）
    
    Args:
        all_data: 如果为True，获取所有历史数据；否则只获取最近5天的数据
    """
    print(f"[{datetime.now()}] 开始执行：更新股票指标数据")
    try:
        from datetime import timedelta
        end_date = datetime.now().strftime('%Y%m%d')
        
        if all_data:
            # 获取最近3年的历史数据
            start_date = (datetime.now() - timedelta(days=1095)).strftime('%Y%m%d')
            print(f"[{datetime.now()}] 使用全量模式：获取最近3年指标数据（{start_date} 至 {end_date}）")
        else:
            # 只获取最近5天的数据
        start_date = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
            print(f"[{datetime.now()}] 使用增量模式：获取最近5天指标数据（{start_date} 至 {end_date}）")
        
        fetch_stock_indicator(start_date=start_date, end_date=end_date)
        print(f"[{datetime.now()}] 完成：更新股票指标数据")
    except Exception as e:
        print(f"[{datetime.now()}] 错误：更新股票指标数据失败 - {e}")


def job_fetch_ipo_stocks(all_data=False):
    """每日更新IPO新股数据（交易日15:30执行）
    
    Args:
        all_data: 如果为True，获取所有历史数据；否则只获取最近90天的数据
    """
    print(f"[{datetime.now()}] 开始执行：更新IPO新股数据")
    try:
        from datetime import timedelta
        end_date = datetime.now().strftime('%Y%m%d')
        
        if all_data:
            # 获取最近10年的历史数据
            start_date = (datetime.now() - timedelta(days=3650)).strftime('%Y%m%d')
            print(f"[{datetime.now()}] 使用全量模式：获取最近10年IPO数据（{start_date} 至 {end_date}）")
        else:
            # 获取最近3个月的IPO数据
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
            print(f"[{datetime.now()}] 使用增量模式：获取最近90天IPO数据（{start_date} 至 {end_date}）")
        
        fetch_ipo_stocks(start_date=start_date, end_date=end_date)
        print(f"[{datetime.now()}] 完成：更新IPO新股数据")
    except Exception as e:
        print(f"[{datetime.now()}] 错误：更新IPO新股数据失败 - {e}")


def job_volume_strategy():
    """每日执行放量策略选股（交易日15:35执行，在日线数据更新之后）"""
    print(f"[{datetime.now()}] 开始执行：放量策略选股")
    try:
        count = save_volume_strategy_selections()
        print(f"[{datetime.now()}] 完成：放量策略选股，共选出 {count} 只股票")
    except Exception as e:
        print(f"[{datetime.now()}] 错误：放量策略选股失败 - {e}")


def run_job_with_logging(job_name, job_func, job_args, lock):
    """在单独线程中执行任务并记录日志"""
    thread_id = threading.current_thread().name
    start_time = datetime.now()
    
    with lock:
        print(f"[{start_time}] [{thread_id}] 开始执行：{job_name}")
    
    try:
        job_func(*job_args)  # 执行任务
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        with lock:
            print(f"[{end_time}] [{thread_id}] ✓ 完成：{job_name} (耗时: {duration:.1f}秒)")
        
        return {
            'job_name': job_name,
            'status': 'success',
            'duration': duration,
            'start_time': start_time,
            'end_time': end_time
        }
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        with lock:
            print(f"[{end_time}] [{thread_id}] ✗ 错误：{job_name}失败 - {e} (耗时: {duration:.1f}秒)")
        
        return {
            'job_name': job_name,
            'status': 'error',
            'error': str(e),
            'duration': duration,
            'start_time': start_time,
            'end_time': end_time
        }


def run_all_jobs_now(all_data=False, parallel=True):
    """立即执行所有任务（支持并行执行）
    
    Args:
        all_data: 如果为True，所有数据获取任务将获取所有历史数据
        parallel: 如果为True，不同接口并行执行；如果为False，串行执行
    """
    print("=" * 60)
    print("立即执行所有任务")
    if all_data:
        print("⚠️  全量模式：所有数据获取任务将获取所有历史数据，可能需要较长时间")
        print("   - 日线数据：最近6000天")
        print("   - 周线数据：最近10年")
        print("   - 月线数据：最近20年")
        print("   - 资金流向：最近3年")
        print("   - 指标数据：最近3年")
        print("   - IPO数据：最近10年")
    if parallel:
        print("🚀 并行模式：不同接口将并行执行，提高效率")
    else:
        print("📋 串行模式：任务将按顺序执行")
    print("=" * 60)
    
    jobs = [
        ("更新股票基本信息", job_fetch_stock_basic, []),
        ("更新上市公司详细信息", job_fetch_stock_company, []),
        ("更新日线数据", job_fetch_daily_data, [all_data]),
        ("更新资金流向数据", job_fetch_moneyflow, [all_data]),
        ("更新股票指标数据", job_fetch_indicator, [all_data]),
        ("更新周线数据", job_fetch_weekly_data, [all_data]),
        ("更新月线数据", job_fetch_monthly_data, [all_data]),
        ("更新IPO新股数据", job_fetch_ipo_stocks, [all_data]),
        ("放量策略选股", job_volume_strategy, []),
    ]
    
    # 用于线程安全的打印
    print_lock = threading.Lock()
    
    if parallel:
        # 并行执行模式
        overall_start = datetime.now()
        results = []
        executor = None
        future_to_job = {}
        shutdown_called = False
        
        try:
            # 使用线程池执行所有任务
            executor = ThreadPoolExecutor(max_workers=len(jobs), thread_name_prefix="Job")
            # 提交所有任务
            future_to_job = {
                executor.submit(run_job_with_logging, job_name, job_func, job_args, print_lock): job_name
                for job_name, job_func, job_args in jobs
            }
            
            # 等待所有任务完成
            for future in as_completed(future_to_job):
                job_name = future_to_job[future]
                try:
                    result = future.result(timeout=None)
                    results.append(result)
                except KeyboardInterrupt:
                    with print_lock:
                        print(f"\n[{datetime.now()}] ⚠️  收到中断信号，正在停止所有任务...")
                    # 取消所有未完成的任务
                    for f in future_to_job:
                        if not f.done():
                            f.cancel()
                    shutdown_called = True
                    # 关闭线程池，不等待正在执行的任务完成
                    if executor:
                        try:
                            executor.shutdown(wait=False, cancel_futures=True)
                        except TypeError:
                            # Python 3.8 及以下版本不支持 cancel_futures 参数
                            executor.shutdown(wait=False)
                    raise
                except Exception as e:
                    with print_lock:
                        print(f"[{datetime.now()}] ✗ 任务 {job_name} 执行异常: {e}")
                    results.append({
                        'job_name': job_name,
                        'status': 'exception',
                        'error': str(e)
                    })
        except KeyboardInterrupt:
            with print_lock:
                print(f"\n[{datetime.now()}] ⚠️  收到中断信号，正在清理线程池...")
            if not shutdown_called and executor:
                # 取消所有未完成的任务
                for f in future_to_job:
                    if not f.done():
                        f.cancel()
                # 关闭线程池，不等待正在执行的任务完成
                try:
                    executor.shutdown(wait=False, cancel_futures=True)
                except TypeError:
                    # Python 3.8 及以下版本不支持 cancel_futures 参数
                    executor.shutdown(wait=False)
                shutdown_called = True
            raise
        finally:
            # 确保线程池正确关闭
            if executor and not shutdown_called:
                try:
                    executor.shutdown(wait=True)
                except Exception:
                    pass  # 如果已经关闭，忽略错误
        
        overall_end = datetime.now()
        overall_duration = (overall_end - overall_start).total_seconds()
        
        # 打印汇总信息
        print("\n" + "=" * 60)
        print("所有任务执行完成（并行模式）")
        print("=" * 60)
        print(f"总耗时: {overall_duration:.1f}秒")
        print("\n任务执行结果:")
        
        success_count = sum(1 for r in results if r.get('status') == 'success')
        error_count = len(results) - success_count
        
        for result in results:
            status_icon = "✓" if result.get('status') == 'success' else "✗"
            duration = result.get('duration', 0)
            print(f"  {status_icon} {result['job_name']}: {result.get('status', 'unknown')} (耗时: {duration:.1f}秒)")
            if result.get('status') == 'error':
                print(f"    错误: {result.get('error', 'Unknown error')}")
        
        print(f"\n成功: {success_count} 个 | 失败: {error_count} 个")
        print("=" * 60)
    else:
        # 串行执行模式（原有逻辑）
        for job_name, job_func, job_args in jobs:
            print(f"\n[{datetime.now()}] 开始执行：{job_name}")
            try:
                job_func(*job_args)
                print(f"[{datetime.now()}] 完成：{job_name}")
            except Exception as e:
                print(f"[{datetime.now()}] 错误：{job_name}失败 - {e}")
        
        print("\n" + "=" * 60)
        print("所有任务执行完成（串行模式）")
        print("=" * 60)


def start_scheduler(run_now=False, all_data=False, parallel=True):
    """启动定时任务调度器
    
    Args:
        run_now: 是否在启动时立即执行所有任务
        all_data: 如果为True，所有数据获取任务将获取所有历史数据
        parallel: 如果为True，不同接口并行执行；如果为False，串行执行
    """
    # 如果设置了立即执行，先执行所有任务
    if run_now:
        run_all_jobs_now(all_data=all_data, parallel=parallel)
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
    
    # 每日15:35执行放量策略选股（在日线数据更新之后）
    scheduler.add_job(
        job_volume_strategy,
        trigger=CronTrigger(hour=15, minute=35),
        id='volume_strategy',
        name='放量策略选股',
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
    parser.add_argument(
        '--all-data',
        action='store_true',
        dest='all_data',
        help='全量模式：日线数据任务将获取最近4000天的历史数据，而不是只获取最近5天。需要与 --run-now 一起使用'
    )
    parser.add_argument(
        '--serial',
        action='store_true',
        dest='serial',
        help='串行模式：任务按顺序执行，不使用并行（默认使用并行模式）'
    )
    
    args = parser.parse_args()
    
    if args.all_data and not args.run_now:
        print("警告: --all-data 参数需要与 --run-now 一起使用")
        print("使用示例: python scheduler.py --run-now --all-data")
        parser.print_help()
        exit(1)
    
    # 默认使用并行模式，除非指定了 --serial
    parallel = not args.serial
    
    start_scheduler(run_now=args.run_now, all_data=args.all_data, parallel=parallel)


