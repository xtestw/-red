#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Flask Web应用主文件
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import sys
import os
import logging
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_flask_config, reload_config
from database import (
    get_session, StockBasic, StockDaily, StockWeekly, StockMonthly,
    StockMoneyflow, StockIndicator, StockFavorite, StockSelection, StockIPO
)
from sqlalchemy import and_, or_, func, desc, nullslast
import pandas as pd
import io
import csv

# 确保logs目录存在（在配置日志之前）
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(logs_dir, 'web_api.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 添加data/data_fetcher目录到路径
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'data_fetcher'))
# 由于已将 data_fetcher 目录添加到路径，可以直接导入
from technical_indicators import calculate_technical_indicators, get_technical_signals

# 获取前端构建目录路径
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web-frontend', 'dist')

app = Flask(__name__)

# CORS配置 - 支持前后端分离和小程序
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # 生产环境建议指定具体域名
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 请求日志中间件
@app.before_request
def log_request_info():
    """记录API请求信息"""
    if request.path.startswith('/api/'):
        logger.info(f"API请求: {request.method} {request.path}")
        logger.info(f"请求参数: {dict(request.args)}")
        if request.is_json:
            logger.info(f"请求体: {request.get_json()}")

@app.after_request
def log_response_info(response):
    """记录API响应信息"""
    if request.path.startswith('/api/'):
        logger.info(f"API响应: {request.method} {request.path} - 状态码: {response.status_code}")
        if response.status_code >= 400:
            logger.warning(f"API错误响应: {request.method} {request.path} - {response.status_code}")
    return response


@app.route('/api/health', methods=['GET'])
def health():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': '服务运行正常'})


@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """获取股票列表（支持筛选）"""
    start_time = time.time()
    try:
        # 获取查询参数
        stock_type = request.args.get('stock_type', 'all')  # all: 所有股票, ipo: IPO股票
        industry = request.args.get('industry', '')
        market = request.args.get('market', '')
        min_market_value = request.args.get('min_market_value', type=float)
        max_market_value = request.args.get('max_market_value', type=float)
        min_pe = request.args.get('min_pe', type=float)
        max_pe = request.args.get('max_pe', type=float)
        keyword = request.args.get('keyword', '')  # 股票代码或名称搜索
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 200, type=int)
        
        logger.info(f"查询股票列表 - 类型: {stock_type}, 关键词: {keyword}, 行业: {industry}, "
                   f"市场: {market}, 市值: {min_market_value}-{max_market_value}, "
                   f"PE: {min_pe}-{max_pe}, 页码: {page}, 每页: {per_page}")
        
        # 如果是IPO股票，使用不同的查询逻辑
        if stock_type == 'ipo':
            return get_ipo_stocks()
        
        session = get_session()
        try:
            # 构建查询
            query = session.query(StockBasic)
            
            # 行业筛选
            if industry:
                query = query.filter(StockBasic.industry == industry)
            
            # 市场筛选
            if market:
                query = query.filter(StockBasic.market == market)
            
            # 关键词搜索（股票代码或名称）
            if keyword:
                query = query.filter(
                    or_(
                        StockBasic.ts_code.like(f'%{keyword}%'),
                        StockBasic.name.like(f'%{keyword}%'),
                        StockBasic.symbol.like(f'%{keyword}%')
                    )
                )
            
            # 如果涉及市值或市盈率筛选，需要关联指标表
            if min_market_value or max_market_value or min_pe or max_pe:
                # 获取最新的交易日期
                latest_date = session.query(func.max(StockIndicator.trade_date)).scalar()
                if latest_date:
                    query = query.join(
                        StockIndicator,
                        and_(
                            StockBasic.ts_code == StockIndicator.ts_code,
                            StockIndicator.trade_date == latest_date
                        )
                    )
                    
                    if min_market_value:
                        query = query.filter(StockIndicator.total_mv >= min_market_value)
                    if max_market_value:
                        query = query.filter(StockIndicator.total_mv <= max_market_value)
                    if min_pe:
                        query = query.filter(StockIndicator.pe >= min_pe)
                    if max_pe:
                        query = query.filter(StockIndicator.pe <= max_pe)
            
            # 分页
            total = query.count()
            stocks = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 获取最新的指标数据
            latest_date = session.query(func.max(StockIndicator.trade_date)).scalar()
            result = []
            for stock in stocks:
                stock_data = {
                    'ts_code': stock.ts_code,
                    'symbol': stock.symbol,
                    'name': stock.name,
                    'area': stock.area,
                    'industry': stock.industry,
                    'market': stock.market,
                    'list_date': stock.list_date
                }
                
                # 获取最新指标
                if latest_date:
                    indicator = session.query(StockIndicator).filter_by(
                        ts_code=stock.ts_code,
                        trade_date=latest_date
                    ).first()
                    if indicator:
                        stock_data['total_mv'] = indicator.total_mv
                        stock_data['circ_mv'] = indicator.circ_mv
                        stock_data['pe'] = indicator.pe
                        stock_data['pb'] = indicator.pb
                        stock_data['ps'] = indicator.ps
                
                result.append(stock_data)
            
            elapsed_time = time.time() - start_time
            logger.info(f"股票列表查询完成 - 总数: {total}, 返回: {len(result)} 条, 耗时: {elapsed_time:.2f}秒")
            
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'stocks': result,
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total + per_page - 1) // per_page
                }
            })
        finally:
            session.close()
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"股票列表查询失败 - 耗时: {elapsed_time:.2f}秒, 错误: {str(e)}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/stocks/<ts_code>', methods=['GET'])
def get_stock_detail(ts_code):
    """获取单个股票的详细信息"""
    try:
        session = get_session()
        try:
            stock = session.query(StockBasic).filter_by(ts_code=ts_code).first()
            if not stock:
                return jsonify({'code': -1, 'message': '股票不存在'}), 404
            
            result = {
                'ts_code': stock.ts_code,
                'symbol': stock.symbol,
                'name': stock.name,
                'area': stock.area,
                'industry': stock.industry,
                'market': stock.market,
                'list_date': stock.list_date
            }
            
            # 获取最新指标
            latest_date = session.query(func.max(StockIndicator.trade_date)).scalar()
            if latest_date:
                indicator = session.query(StockIndicator).filter_by(
                    ts_code=ts_code,
                    trade_date=latest_date
                ).first()
                if indicator:
                    result['total_mv'] = indicator.total_mv
                    result['circ_mv'] = indicator.circ_mv
                    result['pe'] = indicator.pe
                    result['pb'] = indicator.pb
                    result['ps'] = indicator.ps
                    result['dv_ttm'] = indicator.dv_ttm
            
            return jsonify({'code': 0, 'message': 'success', 'data': result})
        finally:
            session.close()
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/stocks/<ts_code>/daily', methods=['GET'])
def get_stock_daily(ts_code):
    """获取股票日线数据"""
    try:
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        limit = request.args.get('limit', 100, type=int)
        
        session = get_session()
        try:
            query = session.query(StockDaily).filter_by(ts_code=ts_code)
            
            if start_date:
                query = query.filter(StockDaily.trade_date >= start_date)
            if end_date:
                query = query.filter(StockDaily.trade_date <= end_date)
            
            daily_data = query.order_by(StockDaily.trade_date.desc()).limit(limit).all()
            
            result = []
            for data in daily_data:
                result.append({
                    'trade_date': data.trade_date,
                    'open': float(data.open) if data.open else None,
                    'high': float(data.high) if data.high else None,
                    'low': float(data.low) if data.low else None,
                    'close': float(data.close) if data.close else None,
                    'pre_close': float(data.pre_close) if data.pre_close else None,
                    'change': float(data.change) if data.change else None,
                    'pct_chg': float(data.pct_chg) if data.pct_chg else None,
                    'vol': float(data.vol) if data.vol else None,
                    'amount': float(data.amount) if data.amount else None
                })
            
            return jsonify({'code': 0, 'message': 'success', 'data': result})
        finally:
            session.close()
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/stocks/<ts_code>/weekly', methods=['GET'])
def get_stock_weekly(ts_code):
    """获取股票周线数据"""
    try:
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        limit = request.args.get('limit', 100, type=int)
        
        session = get_session()
        try:
            query = session.query(StockWeekly).filter_by(ts_code=ts_code)
            
            if start_date:
                query = query.filter(StockWeekly.trade_date >= start_date)
            if end_date:
                query = query.filter(StockWeekly.trade_date <= end_date)
            
            weekly_data = query.order_by(StockWeekly.trade_date.desc()).limit(limit).all()
            
            result = []
            for data in weekly_data:
                result.append({
                    'trade_date': data.trade_date,
                    'open': float(data.open) if data.open else None,
                    'high': float(data.high) if data.high else None,
                    'low': float(data.low) if data.low else None,
                    'close': float(data.close) if data.close else None,
                    'pre_close': float(data.pre_close) if data.pre_close else None,
                    'change': float(data.change) if data.change else None,
                    'pct_chg': float(data.pct_chg) if data.pct_chg else None,
                    'vol': float(data.vol) if data.vol else None,
                    'amount': float(data.amount) if data.amount else None
                })
            
            return jsonify({'code': 0, 'message': 'success', 'data': result})
        finally:
            session.close()
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/stocks/<ts_code>/monthly', methods=['GET'])
def get_stock_monthly(ts_code):
    """获取股票月线数据"""
    try:
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        limit = request.args.get('limit', 100, type=int)
        
        session = get_session()
        try:
            query = session.query(StockMonthly).filter_by(ts_code=ts_code)
            
            if start_date:
                query = query.filter(StockMonthly.trade_date >= start_date)
            if end_date:
                query = query.filter(StockMonthly.trade_date <= end_date)
            
            monthly_data = query.order_by(StockMonthly.trade_date.desc()).limit(limit).all()
            
            result = []
            for data in monthly_data:
                result.append({
                    'trade_date': data.trade_date,
                    'open': float(data.open) if data.open else None,
                    'high': float(data.high) if data.high else None,
                    'low': float(data.low) if data.low else None,
                    'close': float(data.close) if data.close else None,
                    'pre_close': float(data.pre_close) if data.pre_close else None,
                    'change': float(data.change) if data.change else None,
                    'pct_chg': float(data.pct_chg) if data.pct_chg else None,
                    'vol': float(data.vol) if data.vol else None,
                    'amount': float(data.amount) if data.amount else None
                })
            
            return jsonify({'code': 0, 'message': 'success', 'data': result})
        finally:
            session.close()
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/stocks/<ts_code>/moneyflow', methods=['GET'])
def get_stock_moneyflow(ts_code):
    """获取股票资金流向数据"""
    try:
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        limit = request.args.get('limit', 30, type=int)
        
        session = get_session()
        try:
            query = session.query(StockMoneyflow).filter_by(ts_code=ts_code)
            
            if start_date:
                query = query.filter(StockMoneyflow.trade_date >= start_date)
            if end_date:
                query = query.filter(StockMoneyflow.trade_date <= end_date)
            
            moneyflow_data = query.order_by(StockMoneyflow.trade_date.desc()).limit(limit).all()
            
            result = []
            for data in moneyflow_data:
                result.append({
                    'trade_date': data.trade_date,
                    'buy_sm_amount': float(data.buy_sm_amount) if data.buy_sm_amount else None,
                    'sell_sm_amount': float(data.sell_sm_amount) if data.sell_sm_amount else None,
                    'buy_md_amount': float(data.buy_md_amount) if data.buy_md_amount else None,
                    'sell_md_amount': float(data.sell_md_amount) if data.sell_md_amount else None,
                    'buy_lg_amount': float(data.buy_lg_amount) if data.buy_lg_amount else None,
                    'sell_lg_amount': float(data.sell_lg_amount) if data.sell_lg_amount else None,
                    'buy_elg_amount': float(data.buy_elg_amount) if data.buy_elg_amount else None,
                    'sell_elg_amount': float(data.sell_elg_amount) if data.sell_elg_amount else None,
                    'net_mf_amount': float(data.net_mf_amount) if data.net_mf_amount else None
                })
            
            return jsonify({'code': 0, 'message': 'success', 'data': result})
        finally:
            session.close()
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/industries', methods=['GET'])
def get_industries():
    """获取所有行业列表"""
    try:
        session = get_session()
        try:
            industries = session.query(StockBasic.industry).distinct().all()
            industry_list = [ind[0] for ind in industries if ind[0]]
            return jsonify({'code': 0, 'message': 'success', 'data': sorted(industry_list)})
        finally:
            session.close()
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/markets', methods=['GET'])
def get_markets():
    """获取所有市场列表"""
    try:
        session = get_session()
        try:
            markets = session.query(StockBasic.market).distinct().all()
            market_list = [mkt[0] for mkt in markets if mkt[0]]
            return jsonify({'code': 0, 'message': 'success', 'data': sorted(market_list)})
        finally:
            session.close()
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/stocks/<ts_code>/indicators', methods=['GET'])
def get_stock_indicators(ts_code):
    """获取股票技术指标"""
    try:
        period = request.args.get('period', 'daily')  # daily, weekly, monthly
        limit = request.args.get('limit', 100, type=int)
        
        session = get_session()
        try:
            # 根据周期选择表
            if period == 'daily':
                table = StockDaily
            elif period == 'weekly':
                table = StockWeekly
            else:
                table = StockMonthly
            
            data = session.query(table).filter_by(ts_code=ts_code)\
                .order_by(table.trade_date.asc()).limit(limit).all()
            
            if not data:
                return jsonify({'code': -1, 'message': '暂无数据'}), 404
            
            # 转换为DataFrame
            df_data = []
            for d in data:
                df_data.append({
                    'trade_date': d.trade_date,
                    'open': float(d.open) if d.open else None,
                    'high': float(d.high) if d.high else None,
                    'low': float(d.low) if d.low else None,
                    'close': float(d.close) if d.close else None,
                    'vol': float(d.vol) if d.vol else None
                })
            
            df = pd.DataFrame(df_data)
            
            # 计算技术指标
            df = calculate_technical_indicators(df)
            
            # 获取技术信号
            signals = get_technical_signals(df)
            
            # 转换为字典格式
            result = []
            for _, row in df.iterrows():
                item = {
                    'trade_date': row['trade_date'],
                    'close': float(row['close']) if pd.notna(row['close']) else None,
                    'ma5': float(row['ma5']) if 'ma5' in row and pd.notna(row['ma5']) else None,
                    'ma10': float(row['ma10']) if 'ma10' in row and pd.notna(row['ma10']) else None,
                    'ma20': float(row['ma20']) if 'ma20' in row and pd.notna(row['ma20']) else None,
                    'ma30': float(row['ma30']) if 'ma30' in row and pd.notna(row['ma30']) else None,
                    'ma60': float(row['ma60']) if 'ma60' in row and pd.notna(row['ma60']) else None,
                    'macd': float(row['macd']) if 'macd' in row and pd.notna(row['macd']) else None,
                    'macd_signal': float(row['macd_signal']) if 'macd_signal' in row and pd.notna(row['macd_signal']) else None,
                    'macd_hist': float(row['macd_hist']) if 'macd_hist' in row and pd.notna(row['macd_hist']) else None,
                    'rsi': float(row['rsi']) if 'rsi' in row and pd.notna(row['rsi']) else None,
                    'kdj_k': float(row['kdj_k']) if 'kdj_k' in row and pd.notna(row['kdj_k']) else None,
                    'kdj_d': float(row['kdj_d']) if 'kdj_d' in row and pd.notna(row['kdj_d']) else None,
                    'kdj_j': float(row['kdj_j']) if 'kdj_j' in row and pd.notna(row['kdj_j']) else None,
                    'bb_upper': float(row['bb_upper']) if 'bb_upper' in row and pd.notna(row['bb_upper']) else None,
                    'bb_middle': float(row['bb_middle']) if 'bb_middle' in row and pd.notna(row['bb_middle']) else None,
                    'bb_lower': float(row['bb_lower']) if 'bb_lower' in row and pd.notna(row['bb_lower']) else None,
                }
                result.append(item)
            
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'indicators': result,
                    'signals': signals
                }
            })
        finally:
            session.close()
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/stocks/compare', methods=['POST'])
def compare_stocks():
    """对比多只股票"""
    try:
        data = request.get_json()
        ts_codes = data.get('ts_codes', [])
        if not ts_codes or len(ts_codes) > 10:
            return jsonify({'code': -1, 'message': '请选择1-10只股票进行对比'}), 400
        
        session = get_session()
        try:
            result = []
            for ts_code in ts_codes:
                stock = session.query(StockBasic).filter_by(ts_code=ts_code).first()
                if not stock:
                    continue
                
                # 获取最新指标
                latest_date = session.query(func.max(StockIndicator.trade_date)).scalar()
                indicator = None
                if latest_date:
                    indicator = session.query(StockIndicator).filter_by(
                        ts_code=ts_code,
                        trade_date=latest_date
                    ).first()
                
                # 获取最新价格
                latest_daily = session.query(StockDaily).filter_by(ts_code=ts_code)\
                    .order_by(StockDaily.trade_date.desc()).first()
                
                stock_data = {
                    'ts_code': stock.ts_code,
                    'symbol': stock.symbol,
                    'name': stock.name,
                    'industry': stock.industry,
                    'close': float(latest_daily.close) if latest_daily and latest_daily.close else None,
                    'pct_chg': float(latest_daily.pct_chg) if latest_daily and latest_daily.pct_chg else None,
                    'total_mv': float(indicator.total_mv) if indicator and indicator.total_mv else None,
                    'pe': float(indicator.pe) if indicator and indicator.pe else None,
                    'pb': float(indicator.pb) if indicator and indicator.pb else None,
                }
                result.append(stock_data)
            
            return jsonify({'code': 0, 'message': 'success', 'data': result})
        finally:
            session.close()
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/stocks/<ts_code>/export', methods=['GET'])
def export_stock_data(ts_code):
    """导出股票数据为CSV"""
    try:
        period = request.args.get('period', 'daily')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        format_type = request.args.get('format', 'csv')  # csv or excel
        
        session = get_session()
        try:
            if period == 'daily':
                table = StockDaily
            elif period == 'weekly':
                table = StockWeekly
            else:
                table = StockMonthly
            
            query = session.query(table).filter_by(ts_code=ts_code)
            if start_date:
                query = query.filter(table.trade_date >= start_date)
            if end_date:
                query = query.filter(table.trade_date <= end_date)
            
            data = query.order_by(table.trade_date.asc()).all()
            
            if not data:
                return jsonify({'code': -1, 'message': '暂无数据'}), 404
            
            # 获取股票名称
            stock = session.query(StockBasic).filter_by(ts_code=ts_code).first()
            stock_name = stock.name if stock else ts_code
            
            # 转换为DataFrame
            df_data = []
            for d in data:
                df_data.append({
                    '交易日期': d.trade_date,
                    '开盘价': d.open,
                    '最高价': d.high,
                    '最低价': d.low,
                    '收盘价': d.close,
                    '昨收价': d.pre_close,
                    '涨跌额': d.change,
                    '涨跌幅': d.pct_chg,
                    '成交量': d.vol,
                    '成交额': d.amount
                })
            
            df = pd.DataFrame(df_data)
            
            if format_type == 'excel':
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='股票数据')
                output.seek(0)
                return app.response_class(
                    output.getvalue(),
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={'Content-Disposition': f'attachment; filename={stock_name}_{period}_{datetime.now().strftime("%Y%m%d")}.xlsx'}
                )
            else:
                output = io.StringIO()
                df.to_csv(output, index=False, encoding='utf-8-sig')
                output.seek(0)
                return app.response_class(
                    output.getvalue(),
                    mimetype='text/csv',
                    headers={'Content-Disposition': f'attachment; filename={stock_name}_{period}_{datetime.now().strftime("%Y%m%d")}.csv'}
                )
        finally:
            session.close()
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """获取收藏的股票列表"""
    try:
        user_id = request.args.get('user_id', 'default')
        session = get_session()
        try:
            favorites = session.query(StockFavorite).filter_by(user_id=user_id).all()
            ts_codes = [f.ts_code for f in favorites]
            
            if not ts_codes:
                return jsonify({'code': 0, 'message': 'success', 'data': []})
            
            stocks = session.query(StockBasic).filter(StockBasic.ts_code.in_(ts_codes)).all()
            result = []
            for stock in stocks:
                result.append({
                    'ts_code': stock.ts_code,
                    'symbol': stock.symbol,
                    'name': stock.name,
                    'industry': stock.industry
                })
            
            return jsonify({'code': 0, 'message': 'success', 'data': result})
        finally:
            session.close()
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    """添加收藏"""
    try:
        data = request.get_json()
        ts_code = data.get('ts_code')
        user_id = data.get('user_id', 'default')
        notes = data.get('notes', '')
        
        if not ts_code:
            return jsonify({'code': -1, 'message': '股票代码不能为空'}), 400
        
        session = get_session()
        try:
            # 检查是否已收藏
            existing = session.query(StockFavorite).filter_by(
                ts_code=ts_code,
                user_id=user_id
            ).first()
            
            if existing:
                return jsonify({'code': -1, 'message': '已收藏'}), 400
            
            favorite = StockFavorite(
                ts_code=ts_code,
                user_id=user_id,
                notes=notes,
                created_at=datetime.now()
            )
            session.add(favorite)
            session.commit()
            
            return jsonify({'code': 0, 'message': '收藏成功'})
        finally:
            session.close()
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/favorites/<ts_code>', methods=['DELETE'])
def remove_favorite(ts_code):
    """取消收藏"""
    try:
        user_id = request.args.get('user_id', 'default')
        session = get_session()
        try:
            favorite = session.query(StockFavorite).filter_by(
                ts_code=ts_code,
                user_id=user_id
            ).first()
            
            if favorite:
                session.delete(favorite)
                session.commit()
                return jsonify({'code': 0, 'message': '取消收藏成功'})
            else:
                return jsonify({'code': -1, 'message': '未收藏'}), 404
        finally:
            session.close()
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/industries/statistics', methods=['GET'])
def get_industry_statistics():
    """获取行业统计数据"""
    try:
        session = get_session()
        try:
            # 获取最新交易日期
            latest_date = session.query(func.max(StockIndicator.trade_date)).scalar()
            if not latest_date:
                return jsonify({'code': -1, 'message': '暂无数据'}), 404
            
            # 按行业统计
            industries = session.query(StockBasic.industry).distinct().all()
            industry_list = [ind[0] for ind in industries if ind[0]]
            
            result = []
            for industry in industry_list:
                stocks = session.query(StockBasic).filter_by(industry=industry).all()
                ts_codes = [s.ts_code for s in stocks]
                
                if not ts_codes:
                    continue
                
                indicators = session.query(StockIndicator).filter(
                    and_(
                        StockIndicator.ts_code.in_(ts_codes),
                        StockIndicator.trade_date == latest_date
                    )
                ).all()
                
                if not indicators:
                    continue
                
                # 计算统计数据
                total_mv_list = [ind.total_mv for ind in indicators if ind.total_mv]
                pe_list = [ind.pe for ind in indicators if ind.pe and ind.pe > 0]
                
                result.append({
                    'industry': industry,
                    'stock_count': len(indicators),
                    'avg_market_value': sum(total_mv_list) / len(total_mv_list) if total_mv_list else None,
                    'total_market_value': sum(total_mv_list) if total_mv_list else None,
                    'avg_pe': sum(pe_list) / len(pe_list) if pe_list else None,
                    'min_pe': min(pe_list) if pe_list else None,
                    'max_pe': max(pe_list) if pe_list else None
                })
            
            # 按总市值排序
            result.sort(key=lambda x: x['total_market_value'] or 0, reverse=True)
            
            return jsonify({'code': 0, 'message': 'success', 'data': result})
        finally:
            session.close()
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/config/reload', methods=['POST'])
def reload_config_api():
    """手动重新加载配置"""
    try:
        if reload_config():
            flask_config = get_flask_config()
            return jsonify({
                'code': 0,
                'message': '配置已重新加载',
                'data': {
                    'host': flask_config['host'],
                    'port': flask_config['port'],
                    'debug': flask_config['debug']
                }
            })
        else:
            return jsonify({'code': 0, 'message': '配置文件未修改，无需重新加载'})
    except Exception as e:
        return jsonify({'code': -1, 'message': f'重新加载配置失败: {str(e)}'}), 500


@app.route('/api/strategy/selections', methods=['GET'])
def get_strategy_selections():
    """获取选股结果"""
    try:
        strategy_name = request.args.get('strategy_name', '')
        trade_date = request.args.get('trade_date', '')
        
        # 安全地解析 page 参数
        try:
            page_str = request.args.get('page', '1')
            # 如果是字符串且包含 'object'，说明传递了错误的对象
            if isinstance(page_str, str) and ('object' in page_str.lower() or 'PointerEvent' in page_str):
                logger.warning(f"收到错误的 page 参数: {page_str}，使用默认值 1")
                page = 1
            else:
                page = int(page_str) if page_str else 1
        except (ValueError, TypeError):
            logger.warning(f"无法解析 page 参数: {request.args.get('page')}，使用默认值 1")
            page = 1
        
        # 安全地解析 per_page 参数
        try:
            per_page_str = request.args.get('per_page', '100')
            per_page = int(per_page_str) if per_page_str else 100
        except (ValueError, TypeError):
            logger.warning(f"无法解析 per_page 参数: {request.args.get('per_page')}，使用默认值 100")
            per_page = 100
        
        # 确保 page 和 per_page 是有效的正整数
        page = max(1, page)
        per_page = max(1, min(200, per_page))  # 限制每页最多200条
        
        session = get_session()
        try:
            query = session.query(StockSelection)
            
            if strategy_name:
                query = query.filter(StockSelection.strategy_name == strategy_name)
            
            if trade_date:
                query = query.filter(StockSelection.trade_date == trade_date)
            else:
                # 如果没有指定日期，获取最新的选股日期
                latest_date = session.query(func.max(StockSelection.trade_date)).scalar()
                if latest_date:
                    query = query.filter(StockSelection.trade_date == latest_date)
            
            # 分页
            total = query.count()
            logger.info(f"查询选股结果 - 策略: {strategy_name}, 日期: {trade_date}, 总数: {total}, 页码: {page}, 每页: {per_page}")
            
            # 排序：MySQL不支持NULLS LAST，使用ISNULL函数将NULL值排到最后
            # 使用 func.isnull 将 NULL 值转换为 1，非 NULL 为 0，这样 NULL 值会排在最后
            selections = query.order_by(
                func.isnull(StockSelection.score),
                desc(StockSelection.score)
            ).offset((page - 1) * per_page).limit(per_page).all()
            
            logger.info(f"获取到 {len(selections)} 条选股结果")
            
            # 获取股票基本信息
            result = []
            for selection in selections:
                try:
                    stock = session.query(StockBasic).filter_by(ts_code=selection.ts_code).first()
                    if not stock:
                        logger.warning(f"未找到股票基本信息: {selection.ts_code}")
                        continue
                    
                    # 获取最新价格信息
                    latest_daily = session.query(StockDaily).filter_by(ts_code=selection.ts_code)\
                        .order_by(StockDaily.trade_date.desc()).first()
                    
                    stock_data = {
                        'ts_code': selection.ts_code,
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'industry': stock.industry,
                        'strategy_name': selection.strategy_name,
                        'trade_date': selection.trade_date,
                        'score': float(selection.score) if selection.score is not None else None,
                        'reason': selection.reason,
                        'close': float(latest_daily.close) if latest_daily and latest_daily.close is not None else None,
                        'pct_chg': float(latest_daily.pct_chg) if latest_daily and latest_daily.pct_chg is not None else None,
                        'vol': float(latest_daily.vol) if latest_daily and latest_daily.vol is not None else None,
                        'amount': float(latest_daily.amount) if latest_daily and latest_daily.amount is not None else None,
                    }
                    result.append(stock_data)
                except Exception as e:
                    logger.error(f"处理选股结果 {selection.ts_code} 时出错: {e}", exc_info=True)
                    continue
            
            logger.info(f"成功处理 {len(result)} 条选股结果")
            
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'selections': result,
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total + per_page - 1) // per_page if per_page > 0 else 0
                }
            })
        except Exception as e:
            logger.error(f"查询选股结果失败: {e}", exc_info=True)
            session.rollback()
            raise
        finally:
            session.close()
    except Exception as e:
        logger.error(f"获取选股结果API失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': f'获取选股结果失败: {str(e)}'}), 500


@app.route('/api/strategy/dates', methods=['GET'])
def get_strategy_dates():
    """获取有选股结果的日期列表"""
    try:
        strategy_name = request.args.get('strategy_name', '')
        
        session = get_session()
        try:
            query = session.query(StockSelection.trade_date).distinct()
            
            if strategy_name:
                query = query.filter(StockSelection.strategy_name == strategy_name)
            
            dates = query.order_by(StockSelection.trade_date.desc()).all()
            date_list = [d[0] for d in dates]
            
            return jsonify({'code': 0, 'message': 'success', 'data': date_list})
        finally:
            session.close()
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/stocks/ipo', methods=['GET'])
def get_ipo_stocks():
    """获取IPO股票列表（支持筛选）"""
    start_time = time.time()
    try:
        # 获取查询参数
        keyword = request.args.get('keyword', '')  # 股票代码或名称搜索
        start_date = request.args.get('start_date', '')  # 上网发行开始日期
        end_date = request.args.get('end_date', '')  # 上网发行结束日期
        min_price = request.args.get('min_price', type=float)  # 最小发行价格
        max_price = request.args.get('max_price', type=float)  # 最大发行价格
        min_pe = request.args.get('min_pe', type=float)  # 最小市盈率
        max_pe = request.args.get('max_pe', type=float)  # 最大市盈率
        min_funds = request.args.get('min_funds', type=float)  # 最小募集资金（亿元）
        max_funds = request.args.get('max_funds', type=float)  # 最大募集资金（亿元）
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 200, type=int)
        
        logger.info(f"查询IPO股票列表 - 关键词: {keyword}, 日期范围: {start_date} 至 {end_date}, "
                   f"价格: {min_price}-{max_price}, PE: {min_pe}-{max_pe}, "
                   f"募集资金: {min_funds}-{max_funds}, 页码: {page}, 每页: {per_page}")
        
        session = get_session()
        try:
            # 构建查询
            query = session.query(StockIPO)
            
            # 关键词搜索（股票代码或名称）
            if keyword:
                query = query.filter(
                    or_(
                        StockIPO.ts_code.like(f'%{keyword}%'),
                        StockIPO.name.like(f'%{keyword}%'),
                        StockIPO.sub_code.like(f'%{keyword}%')
                    )
                )
            
            # 日期筛选
            if start_date:
                query = query.filter(StockIPO.ipo_date >= start_date)
            if end_date:
                query = query.filter(StockIPO.ipo_date <= end_date)
            
            # 价格筛选
            if min_price:
                query = query.filter(StockIPO.price >= min_price)
            if max_price:
                query = query.filter(StockIPO.price <= max_price)
            
            # 市盈率筛选
            if min_pe:
                query = query.filter(StockIPO.pe >= min_pe)
            if max_pe:
                query = query.filter(StockIPO.pe <= max_pe)
            
            # 募集资金筛选
            if min_funds:
                query = query.filter(StockIPO.funds >= min_funds)
            if max_funds:
                query = query.filter(StockIPO.funds <= max_funds)
            
            # 分页
            total = query.count()
            # 按上网发行日期倒序排列
            ipo_stocks = query.order_by(StockIPO.ipo_date.desc()).offset((page - 1) * per_page).limit(per_page).all()
            
            # 转换为字典格式
            result = []
            for stock in ipo_stocks:
                stock_data = {
                    'ts_code': stock.ts_code,
                    'sub_code': stock.sub_code,
                    'name': stock.name,
                    'ipo_date': stock.ipo_date,
                    'issue_date': stock.issue_date,
                    'amount': float(stock.amount) if stock.amount else None,
                    'market_amount': float(stock.market_amount) if stock.market_amount else None,
                    'price': float(stock.price) if stock.price else None,
                    'pe': float(stock.pe) if stock.pe else None,
                    'limit_amount': float(stock.limit_amount) if stock.limit_amount else None,
                    'funds': float(stock.funds) if stock.funds else None,
                    'ballot': float(stock.ballot) if stock.ballot else None
                }
                result.append(stock_data)
            
            elapsed_time = time.time() - start_time
            logger.info(f"IPO股票列表查询完成 - 总数: {total}, 返回: {len(result)} 条, 耗时: {elapsed_time:.2f}秒")
            
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'stocks': result,
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total + per_page - 1) // per_page
                }
            })
        finally:
            session.close()
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"IPO股票列表查询失败 - 耗时: {elapsed_time:.2f}秒, 错误: {str(e)}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


# 静态文件路由（用于前端资源）
@app.route('/assets/<path:filename>')
def assets(filename):
    """服务前端静态资源"""
    return send_from_directory(os.path.join(FRONTEND_DIST, 'assets'), filename)


# 前端路由（Vue Router history模式支持）
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def frontend(path):
    """服务前端页面（支持Vue Router history模式）"""
    # 如果是API请求，不处理
    if path.startswith('api/'):
        return jsonify({'code': -1, 'message': 'API endpoint not found'}), 404
    
    # 如果是静态资源请求，尝试从dist目录返回
    if path.startswith('assets/'):
        try:
            return send_from_directory(FRONTEND_DIST, path)
        except:
            pass
    
    # 其他请求返回index.html（Vue Router会处理路由）
    index_path = os.path.join(FRONTEND_DIST, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(FRONTEND_DIST, 'index.html')
    else:
        return jsonify({
            'code': -1,
            'message': '前端文件未找到，请先运行 npm run build 构建前端'
        }), 404


if __name__ == '__main__':
    flask_config = get_flask_config()
    app.run(host=flask_config['host'], port=flask_config['port'], debug=flask_config['debug'])

