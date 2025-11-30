#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Flask Web应用主文件
"""
from flask import Flask, jsonify, request, send_from_directory, redirect
from flask_cors import CORS
from datetime import datetime, timedelta
import sys
import os
import logging
import time
import json
import jwt
import requests
from functools import wraps

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_flask_config, reload_config, get_wechat_config, get_jwt_config, get_seo_config
from database import (
    get_session, StockBasic, StockDaily, StockWeekly, StockMonthly,
    StockMoneyflow, StockIndicator, StockFavorite, StockSelection, StockIPO,
    User, UserSession, IndexBasic, IndexDaily, IndexWeekly, IndexMonthly, IndexWeight,
    CustomStrategy
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


# ==================== 认证相关 ====================

def generate_token(user_id, expires_in=None):
    """生成JWT token"""
    jwt_config = get_jwt_config()
    if expires_in is None:
        expires_in = jwt_config['expires_in']
    
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, jwt_config['secret_key'], algorithm='HS256')
    return token


def verify_token(token):
    """验证JWT token"""
    try:
        jwt_config = get_jwt_config()
        payload = jwt.decode(token, jwt_config['secret_key'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user():
    """从请求头获取当前用户"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    try:
        # 支持 "Bearer <token>" 格式
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
        payload = verify_token(token)
        if payload:
            return payload.get('user_id')
    except Exception as e:
        logger.error(f"获取当前用户失败: {e}")
    return None


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_current_user()
        if not user_id:
            return jsonify({'code': -1, 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function


# 临时存储登录状态（实际生产环境应使用Redis等）
_login_sessions = {}
import threading
_login_sessions_lock = threading.Lock()

@app.route('/api/auth/wechat/login', methods=['GET'])
def wechat_login():
    """微信登录 - 生成授权URL和二维码数据"""
    try:
        wechat_config = get_wechat_config()
        app_id = wechat_config.get('app_id')
        redirect_uri = wechat_config.get('redirect_uri')
        
        if not app_id:
            return jsonify({'code': -1, 'message': '微信配置未设置'}), 500
        
        # 生成state参数（用于防止CSRF攻击）
        import secrets
        state = secrets.token_urlsafe(32)
        
        # 微信网页授权URL
        auth_url = (
            f"https://open.weixin.qq.com/connect/oauth2/authorize"
            f"?appid={app_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope=snsapi_userinfo"
            f"&state={state}"
            f"#wechat_redirect"
        )
        
        # 存储登录状态（5分钟过期）
        with _login_sessions_lock:
            _login_sessions[state] = {
                'status': 'pending',  # pending, scanned, success, expired
                'created_at': datetime.now(),
                'token': None,
                'refresh_token': None
            }
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'auth_url': auth_url,
                'state': state,
                'qr_url': auth_url  # 用于生成二维码的URL
            }
        })
    except Exception as e:
        logger.error(f"生成微信登录URL失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/auth/wechat/status/<state>', methods=['GET'])
def check_login_status(state):
    """检查登录状态"""
    try:
        with _login_sessions_lock:
            session_data = _login_sessions.get(state)
            
            if not session_data:
                return jsonify({
                    'code': 0,
                    'message': 'success',
                    'data': {
                        'status': 'expired',
                        'message': '登录会话已过期，请重新扫码'
                    }
                })
            
            # 检查是否过期（5分钟）
            created_at = session_data['created_at']
            # 确保created_at是datetime对象
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    # 如果解析失败，使用当前时间
                    created_at = datetime.now()
            
            if (datetime.now() - created_at).total_seconds() > 300:
                # 过期，删除
                del _login_sessions[state]
                return jsonify({
                    'code': 0,
                    'message': 'success',
                    'data': {
                        'status': 'expired',
                        'message': '登录会话已过期，请重新扫码'
                    }
                })
            
            status = session_data.get('status', 'pending')
            if status == 'success':
                return jsonify({
                    'code': 0,
                    'message': 'success',
                    'data': {
                        'status': 'success',
                        'token': session_data.get('token'),
                        'refresh_token': session_data.get('refresh_token')
                    }
                })
            else:
                return jsonify({
                    'code': 0,
                    'message': 'success',
                    'data': {
                        'status': status,
                        'message': '等待扫码' if status == 'pending' else '已扫码，等待确认'
                    }
                })
    except Exception as e:
        logger.error(f"检查登录状态失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/auth/wechat/callback', methods=['GET'])
def wechat_callback():
    """微信登录回调 - 处理授权码，获取用户信息"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        
        if not code:
            return jsonify({'code': -1, 'message': '缺少授权码'}), 400
        
        wechat_config = get_wechat_config()
        app_id = wechat_config.get('app_id')
        app_secret = wechat_config.get('app_secret')
        
        if not app_id or not app_secret:
            return jsonify({'code': -1, 'message': '微信配置未设置'}), 500
        
        # 第一步：用code换取access_token
        token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        token_params = {
            'appid': app_id,
            'secret': app_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.get(token_url, params=token_params, timeout=10)
        token_data = token_response.json()
        
        if 'errcode' in token_data:
            logger.error(f"获取access_token失败: {token_data}")
            return jsonify({'code': -1, 'message': f"微信授权失败: {token_data.get('errmsg', '未知错误')}"}), 400
        
        access_token = token_data.get('access_token')
        openid = token_data.get('openid')
        unionid = token_data.get('unionid')
        
        if not access_token or not openid:
            return jsonify({'code': -1, 'message': '获取access_token失败'}), 400
        
        # 第二步：用access_token获取用户信息
        userinfo_url = "https://api.weixin.qq.com/sns/userinfo"
        userinfo_params = {
            'access_token': access_token,
            'openid': openid,
            'lang': 'zh_CN'
        }
        
        userinfo_response = requests.get(userinfo_url, params=userinfo_params, timeout=10)
        userinfo_data = userinfo_response.json()
        
        if 'errcode' in userinfo_data:
            logger.error(f"获取用户信息失败: {userinfo_data}")
            return jsonify({'code': -1, 'message': f"获取用户信息失败: {userinfo_data.get('errmsg', '未知错误')}"}), 400
        
        # 第三步：创建或更新用户
        session = get_session()
        try:
            user = session.query(User).filter_by(openid=openid).first()
            now = datetime.now()
            
            if user:
                # 更新用户信息
                user.unionid = unionid or user.unionid
                user.nickname = userinfo_data.get('nickname', user.nickname)
                user.avatar = userinfo_data.get('headimgurl', user.avatar)
                user.gender = userinfo_data.get('sex', user.gender)
                user.country = userinfo_data.get('country', user.country)
                user.province = userinfo_data.get('province', user.province)
                user.city = userinfo_data.get('city', user.city)
                user.language = userinfo_data.get('language', user.language)
                user.updated_at = now
                user.last_login_at = now
            else:
                # 创建新用户
                user = User(
                    openid=openid,
                    unionid=unionid,
                    nickname=userinfo_data.get('nickname', ''),
                    avatar=userinfo_data.get('headimgurl', ''),
                    gender=userinfo_data.get('sex', 0),
                    country=userinfo_data.get('country', ''),
                    province=userinfo_data.get('province', ''),
                    city=userinfo_data.get('city', ''),
                    language=userinfo_data.get('language', 'zh_CN'),
                    created_at=now,
                    updated_at=now,
                    last_login_at=now
                )
                session.add(user)
            
            session.commit()
            session.refresh(user)
            
            # 第四步：生成JWT token
            jwt_config = get_jwt_config()
            token = generate_token(user.id, jwt_config['expires_in'])
            refresh_token = generate_token(user.id, jwt_config['refresh_expires_in'])
            
            # 保存会话到数据库
            expires_at = datetime.utcnow() + timedelta(seconds=jwt_config['expires_in'])
            user_session = UserSession(
                user_id=user.id,
                token=token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                created_at=now,
                last_used_at=now
            )
            session.add(user_session)
            session.commit()
            
            # 如果存在state，更新登录会话状态
            if state:
                with _login_sessions_lock:
                    if state in _login_sessions:
                        _login_sessions[state]['status'] = 'success'
                        _login_sessions[state]['token'] = token
                        _login_sessions[state]['refresh_token'] = refresh_token
            
            # 重定向到前端页面，携带token
            seo_config = get_seo_config()
            frontend_url = seo_config.get('site_url', 'http://localhost:5173')
            if not frontend_url.startswith('http'):
                frontend_url = f"http://{frontend_url}"
            
            # 重定向到前端页面，携带token
            redirect_url = f"{frontend_url}/auth/callback?token={token}&refresh_token={refresh_token}"
            return redirect(redirect_url)
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"微信登录回调失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': f'登录失败: {str(e)}'}), 500


@app.route('/api/auth/user', methods=['GET'])
@login_required
def get_current_user_info():
    """获取当前用户信息"""
    try:
        user_id = get_current_user()
        if not user_id:
            return jsonify({'code': -1, 'message': '未登录'}), 401
        
        session = get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return jsonify({'code': -1, 'message': '用户不存在'}), 404
            
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'id': user.id,
                    'openid': user.openid,
                    'nickname': user.nickname,
                    'avatar': user.avatar,
                    'gender': user.gender,
                    'country': user.country,
                    'province': user.province,
                    'city': user.city,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None
                }
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """退出登录"""
    try:
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
            
            session = get_session()
            try:
                # 删除会话
                user_session = session.query(UserSession).filter_by(token=token).first()
                if user_session:
                    session.delete(user_session)
                    session.commit()
            finally:
                session.close()
        
        return jsonify({'code': 0, 'message': '退出成功'})
    except Exception as e:
        logger.error(f"退出登录失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/auth/refresh', methods=['POST'])
def refresh_token():
    """刷新token"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({'code': -1, 'message': '缺少refresh_token'}), 400
        
        payload = verify_token(refresh_token)
        if not payload:
            return jsonify({'code': -1, 'message': 'refresh_token无效或已过期'}), 401
        
        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({'code': -1, 'message': 'token格式错误'}), 400
        
        # 生成新的token
        jwt_config = get_jwt_config()
        new_token = generate_token(user_id, jwt_config['expires_in'])
        new_refresh_token = generate_token(user_id, jwt_config['refresh_expires_in'])
        
        # 更新会话
        session = get_session()
        try:
            old_session = session.query(UserSession).filter_by(refresh_token=refresh_token).first()
            if old_session:
                old_session.token = new_token
                old_session.refresh_token = new_refresh_token
                old_session.expires_at = datetime.utcnow() + timedelta(seconds=jwt_config['expires_in'])
                old_session.last_used_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()
        
        return jsonify({
            'code': 0,
            'message': '刷新成功',
            'data': {
                'token': new_token,
                'refresh_token': new_refresh_token,
                'expires_in': jwt_config['expires_in']
            }
        })
    except Exception as e:
        logger.error(f"刷新token失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


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
@login_required
def get_favorites():
    """获取收藏的股票列表"""
    try:
        user_id = get_current_user()
        if not user_id:
            return jsonify({'code': -1, 'message': '请先登录'}), 401
        
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
@login_required
def add_favorite():
    """添加收藏"""
    try:
        user_id = get_current_user()
        if not user_id:
            return jsonify({'code': -1, 'message': '请先登录'}), 401
        
        data = request.get_json()
        ts_code = data.get('ts_code')
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
@login_required
def remove_favorite(ts_code):
    """取消收藏"""
    try:
        user_id = get_current_user()
        if not user_id:
            return jsonify({'code': -1, 'message': '请先登录'}), 401
        
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


@app.route('/api/market/overview', methods=['GET'])
def get_market_overview():
    """获取市场概览（主要指数当天数据）"""
    try:
        session = get_session()
        try:
            result = {}
            
            # 尝试获取指数数据（如果表存在）
            try:
                from database import IndexDaily
                # 检查表是否存在
                from sqlalchemy import inspect
                inspector = inspect(session.bind)
                tables = inspector.get_table_names()
                
                if 'index_daily' in tables:
                    # 获取最新交易日期
                    latest_date = session.query(func.max(IndexDaily.trade_date)).scalar()
                    if latest_date:
                        # 获取主要指数代码
                        index_codes = {
                            'sh_index': '000001.SH',  # 上证指数
                            'sz_index': '399001.SZ',   # 深证成指
                            'cyb_index': '399006.SZ'   # 创业板指
                        }
                        
                        for key, ts_code in index_codes.items():
                            index_data = session.query(IndexDaily).filter(
                                and_(
                                    IndexDaily.ts_code == ts_code,
                                    IndexDaily.trade_date == latest_date
                                )
                            ).first()
                            
                            if index_data:
                                result[key] = {
                                    'ts_code': index_data.ts_code,
                                    'trade_date': index_data.trade_date,
                                    'close': float(index_data.close) if index_data.close else None,
                                    'open': float(index_data.open) if index_data.open else None,
                                    'high': float(index_data.high) if index_data.high else None,
                                    'low': float(index_data.low) if index_data.low else None,
                                    'pre_close': float(index_data.pre_close) if index_data.pre_close else None,
                                    'change': float(index_data.change) if index_data.change else None,
                                    'pct_chg': float(index_data.pct_chg) if index_data.pct_chg else None,
                                    'vol': float(index_data.vol) if index_data.vol else None,
                                    'amount': float(index_data.amount) if index_data.amount else None
                                }
            except Exception as e:
                # 如果表不存在或查询失败，记录日志但不影响其他数据
                logger.warning(f"获取指数数据失败（表可能不存在）: {e}")
            
            # 计算市场统计（上涨、下跌、平盘家数）
            try:
                latest_stock_date = session.query(func.max(StockDaily.trade_date)).scalar()
                if latest_stock_date:
                    stocks = session.query(StockDaily).filter(
                        StockDaily.trade_date == latest_stock_date
                    ).all()
                    
                    rise_count = sum(1 for s in stocks if s.pct_chg and s.pct_chg > 0)
                    fall_count = sum(1 for s in stocks if s.pct_chg and s.pct_chg < 0)
                    flat_count = sum(1 for s in stocks if s.pct_chg and s.pct_chg == 0)
                    total_amount = sum(float(s.amount or 0) for s in stocks) / 100000000  # 转换为亿元
                    
                    result['stats'] = {
                        'rise_count': rise_count,
                        'fall_count': fall_count,
                        'flat_count': flat_count,
                        'total_amount': round(total_amount, 2)
                    }
                else:
                    result['stats'] = {
                        'rise_count': 0,
                        'fall_count': 0,
                        'flat_count': 0,
                        'total_amount': 0
                    }
            except Exception as e:
                logger.warning(f"获取市场统计失败: {e}")
                result['stats'] = {
                    'rise_count': 0,
                    'fall_count': 0,
                    'flat_count': 0,
                    'total_amount': 0
                }
            
            return jsonify({'code': 0, 'message': 'success', 'data': result})
        finally:
            session.close()
    except Exception as e:
        logger.error(f"获取市场概览失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/stocks/<ts_code>/sector', methods=['GET'])
def get_stock_sector_analysis(ts_code):
    """获取股票板块分析数据"""
    try:
        session = get_session()
        try:
            # 获取股票基本信息
            stock = session.query(StockBasic).filter_by(ts_code=ts_code).first()
            if not stock:
                return jsonify({'code': -1, 'message': '股票不存在'}), 404
            
            industry = stock.industry
            if not industry:
                return jsonify({'code': -1, 'message': '该股票暂无行业信息'}), 404
            
            # 获取同行业所有股票
            industry_stocks = session.query(StockBasic).filter_by(industry=industry).all()
            industry_ts_codes = [s.ts_code for s in industry_stocks]
            
            # 获取最新交易日期
            latest_date = session.query(func.max(StockDaily.trade_date)).scalar()
            if not latest_date:
                return jsonify({'code': -1, 'message': '暂无交易数据'}), 404
            
            # 获取同行业股票的日线数据
            industry_daily = session.query(StockDaily).filter(
                and_(
                    StockDaily.ts_code.in_(industry_ts_codes),
                    StockDaily.trade_date == latest_date
                )
            ).all()
            
            # 计算板块统计数据
            if not industry_daily:
                return jsonify({'code': -1, 'message': '暂无板块数据'}), 404
            
            # 获取当前股票的数据
            current_stock_daily = next((d for d in industry_daily if d.ts_code == ts_code), None)
            
            # 计算板块涨跌幅分布
            pct_chg_list = [float(d.pct_chg) for d in industry_daily if d.pct_chg is not None]
            rise_count = sum(1 for p in pct_chg_list if p > 0)
            fall_count = sum(1 for p in pct_chg_list if p < 0)
            flat_count = sum(1 for p in pct_chg_list if p == 0)
            
            # 计算板块平均涨跌幅
            avg_pct_chg = sum(pct_chg_list) / len(pct_chg_list) if pct_chg_list else 0
            
            # 计算板块总成交额
            total_amount = sum(float(d.amount or 0) for d in industry_daily) / 100000000  # 转换为亿元
            
            # 获取板块内股票排名（按涨跌幅）
            stock_rankings = []
            for daily in industry_daily:
                stock_info = next((s for s in industry_stocks if s.ts_code == daily.ts_code), None)
                if stock_info and daily.pct_chg is not None:
                    stock_rankings.append({
                        'ts_code': daily.ts_code,
                        'name': stock_info.name,
                        'symbol': stock_info.symbol,
                        'pct_chg': float(daily.pct_chg),
                        'close': float(daily.close) if daily.close else None,
                        'amount': float(daily.amount or 0) / 100000000  # 转换为亿元
                    })
            
            # 按涨跌幅排序
            stock_rankings.sort(key=lambda x: x['pct_chg'], reverse=True)
            
            # 找到当前股票的排名
            current_rank = next((i + 1 for i, s in enumerate(stock_rankings) if s['ts_code'] == ts_code), None)
            
            result = {
                'industry': industry,
                'stock_count': len(industry_stocks),
                'trade_date': latest_date,
                'current_stock': {
                    'ts_code': ts_code,
                    'name': stock.name,
                    'symbol': stock.symbol,
                    'pct_chg': float(current_stock_daily.pct_chg) if current_stock_daily and current_stock_daily.pct_chg else None,
                    'close': float(current_stock_daily.close) if current_stock_daily and current_stock_daily.close else None,
                    'rank': current_rank
                },
                'sector_stats': {
                    'avg_pct_chg': round(avg_pct_chg, 2),
                    'rise_count': rise_count,
                    'fall_count': fall_count,
                    'flat_count': flat_count,
                    'total_amount': round(total_amount, 2)
                },
                'stock_rankings': stock_rankings[:20]  # 只返回前20名
            }
            
            return jsonify({'code': 0, 'message': 'success', 'data': result})
        finally:
            session.close()
    except Exception as e:
        logger.error(f"获取股票板块分析失败: {e}", exc_info=True)
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


@app.route('/api/database/schema', methods=['GET'])
def get_database_schema():
    """获取数据库所有表的结构信息"""
    try:
        from sqlalchemy import inspect, text
        session = get_session()
        engine = session.bind
        
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            result = []
            for table_name in sorted(tables):
                try:
                    # 获取表的所有列信息
                    columns = inspector.get_columns(table_name)
                    
                    # 获取表的主键
                    pk_constraint = inspector.get_pk_constraint(table_name)
                    primary_keys = pk_constraint.get('constrained_columns', []) if pk_constraint else []
                    
                    # 获取表的索引
                    indexes = inspector.get_indexes(table_name)
                    
                    # 获取表的注释
                    table_comment = None
                    try:
                        # MySQL获取表注释
                        result_obj = session.execute(text(f"SHOW TABLE STATUS LIKE '{table_name}'"))
                        row = result_obj.fetchone()
                        if row:
                            # MySQL的SHOW TABLE STATUS返回的注释在Comment字段
                            table_comment = row[10] if len(row) > 10 else None
                    except:
                        pass
                    
                    # 格式化列信息
                    columns_info = []
                    for col in columns:
                        col_info = {
                            'name': col['name'],
                            'type': str(col['type']),
                            'nullable': col.get('nullable', True),
                            'default': str(col.get('default', '')) if col.get('default') is not None else None,
                            'comment': col.get('comment', ''),
                            'primary_key': col['name'] in primary_keys
                        }
                        columns_info.append(col_info)
                    
                    # 格式化索引信息
                    indexes_info = []
                    for idx in indexes:
                        idx_info = {
                            'name': idx['name'],
                            'columns': idx['column_names'],
                            'unique': idx.get('unique', False)
                        }
                        indexes_info.append(idx_info)
                    
                    result.append({
                        'table_name': table_name,
                        'comment': table_comment or '',
                        'columns': columns_info,
                        'primary_keys': primary_keys,
                        'indexes': indexes_info,
                        'column_count': len(columns_info),
                        'index_count': len(indexes_info)
                    })
                except Exception as e:
                    logger.warning(f"获取表 {table_name} 结构失败: {e}")
                    continue
            
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'tables': result,
                    'total_tables': len(result)
                }
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"获取数据库结构失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/database/table/<table_name>/preview', methods=['GET'])
def get_table_preview(table_name):
    """获取表数据预览（前10条）"""
    try:
        from sqlalchemy import inspect, text
        session = get_session()
        engine = session.bind
        
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            # 检查表是否存在
            if table_name not in tables:
                return jsonify({'code': -1, 'message': f'表 {table_name} 不存在'}), 404
            
            # 获取表的前10条数据
            # 使用原始SQL查询，避免SQL注入风险（表名已经验证存在）
            # 注意：这里假设表名是安全的（已经通过inspector验证）
            query = text(f"SELECT * FROM `{table_name}` LIMIT 10")
            result = session.execute(query)
            
            # 获取列名
            columns = list(result.keys())
            
            # 获取数据行
            rows = []
            for row in result:
                # 将行转换为字典
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]  # 使用索引访问
                    # 处理特殊类型
                    if isinstance(value, datetime):
                        value = value.strftime('%Y-%m-%d %H:%M:%S')
                    elif value is None:
                        value = None
                    else:
                        value = str(value)
                    row_dict[col] = value
                rows.append(row_dict)
            
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'table_name': table_name,
                    'columns': list(columns),
                    'rows': rows,
                    'count': len(rows)
                }
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"获取表 {table_name} 数据预览失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/indices', methods=['GET'])
def get_indices():
    """获取指数列表（支持筛选）"""
    try:
        # 获取查询参数
        keyword = request.args.get('keyword', '')
        market = request.args.get('market', '')
        category = request.args.get('category', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 200, type=int)
        
        logger.info(f"查询指数列表 - 关键词: {keyword}, 市场: {market}, 类别: {category}, 页码: {page}")
        
        session = get_session()
        try:
            # 构建查询
            query = session.query(IndexBasic)
            
            # 关键词搜索
            if keyword:
                query = query.filter(
                    or_(
                        IndexBasic.ts_code.like(f'%{keyword}%'),
                        IndexBasic.name.like(f'%{keyword}%'),
                        IndexBasic.fullname.like(f'%{keyword}%')
                    )
                )
            
            # 市场筛选
            if market:
                query = query.filter(IndexBasic.market == market)
            
            # 类别筛选
            if category:
                query = query.filter(IndexBasic.category == category)
            
            # 获取总数
            total = query.count()
            
            # 分页
            indices = query.order_by(IndexBasic.ts_code).offset((page - 1) * per_page).limit(per_page).all()
            
            # 获取最新的日线数据（用于显示最新点位、涨跌幅等）
            latest_date = session.query(func.max(IndexDaily.trade_date)).scalar()
            
            result = []
            for index in indices:
                index_data = {
                    'ts_code': index.ts_code,
                    'name': index.name,
                    'fullname': index.fullname,
                    'market': index.market,
                    'publisher': index.publisher,
                    'index_type': index.index_type,
                    'category': index.category,
                    'base_date': index.base_date,
                    'base_point': float(index.base_point) if index.base_point else None,
                    'list_date': index.list_date,
                    'weight_rule': index.weight_rule,
                    'desc': index.desc,
                    'exp_date': index.exp_date,
                    'close': None,
                    'pct_chg': None,
                    'pe': None,
                    'pb': None,
                    'total_mv': None,
                    'float_mv': None,
                    'turnover_rate': None
                }
                
                # 获取最新的日线数据
                if latest_date:
                    daily = session.query(IndexDaily).filter(
                        IndexDaily.ts_code == index.ts_code,
                        IndexDaily.trade_date == latest_date
                    ).first()
                    
                    if daily:
                        index_data['close'] = float(daily.close) if daily.close else None
                        index_data['pct_chg'] = float(daily.pct_chg) if daily.pct_chg else None
                        index_data['pe'] = float(daily.pe) if daily.pe else None
                        index_data['pb'] = float(daily.pb) if daily.pb else None
                        index_data['total_mv'] = float(daily.total_mv) if daily.total_mv else None
                        index_data['float_mv'] = float(daily.float_mv) if daily.float_mv else None
                        index_data['turnover_rate'] = float(daily.turnover_rate) if daily.turnover_rate else None
                
                result.append(index_data)
            
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'indices': result,
                    'total': total,
                    'page': page,
                    'per_page': per_page
                }
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"获取指数列表失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/indices/<ts_code>', methods=['GET'])
def get_index_detail(ts_code):
    """获取指数详情"""
    try:
        session = get_session()
        try:
            index = session.query(IndexBasic).filter_by(ts_code=ts_code).first()
            
            if not index:
                return jsonify({'code': -1, 'message': '指数不存在'}), 404
            
            result = {
                'ts_code': index.ts_code,
                'name': index.name,
                'fullname': index.fullname,
                'market': index.market,
                'publisher': index.publisher,
                'index_type': index.index_type,
                'category': index.category,
                'base_date': index.base_date,
                'base_point': float(index.base_point) if index.base_point else None,
                'list_date': index.list_date,
                'weight_rule': index.weight_rule,
                'desc': index.desc,
                'exp_date': index.exp_date
            }
            
            return jsonify({'code': 0, 'message': 'success', 'data': result})
        finally:
            session.close()
    except Exception as e:
        logger.error(f"获取指数详情失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/indices/<ts_code>/daily', methods=['GET'])
def get_index_daily(ts_code):
    """获取指数日线数据"""
    try:
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        limit = request.args.get('limit', 100, type=int)
        
        session = get_session()
        try:
            query = session.query(IndexDaily).filter_by(ts_code=ts_code)
            
            if start_date:
                query = query.filter(IndexDaily.trade_date >= start_date)
            if end_date:
                query = query.filter(IndexDaily.trade_date <= end_date)
            
            daily_data = query.order_by(IndexDaily.trade_date.desc()).limit(limit).all()
            
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
                    'amount': float(data.amount) if data.amount else None,
                    'total_mv': float(data.total_mv) if data.total_mv else None,
                    'float_mv': float(data.float_mv) if data.float_mv else None,
                    'turnover_rate': float(data.turnover_rate) if data.turnover_rate else None,
                    'pe': float(data.pe) if data.pe else None,
                    'pb': float(data.pb) if data.pb else None
                })
            
            return jsonify({'code': 0, 'message': 'success', 'data': result})
        finally:
            session.close()
    except Exception as e:
        logger.error(f"获取指数日线数据失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/indices/<ts_code>/weekly', methods=['GET'])
def get_index_weekly(ts_code):
    """获取指数周线数据"""
    try:
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        limit = request.args.get('limit', 100, type=int)
        
        session = get_session()
        try:
            query = session.query(IndexWeekly).filter_by(ts_code=ts_code)
            
            if start_date:
                query = query.filter(IndexWeekly.trade_date >= start_date)
            if end_date:
                query = query.filter(IndexWeekly.trade_date <= end_date)
            
            weekly_data = query.order_by(IndexWeekly.trade_date.desc()).limit(limit).all()
            
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
        logger.error(f"获取指数周线数据失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/indices/<ts_code>/monthly', methods=['GET'])
def get_index_monthly(ts_code):
    """获取指数月线数据"""
    try:
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        limit = request.args.get('limit', 100, type=int)
        
        session = get_session()
        try:
            query = session.query(IndexMonthly).filter_by(ts_code=ts_code)
            
            if start_date:
                query = query.filter(IndexMonthly.trade_date >= start_date)
            if end_date:
                query = query.filter(IndexMonthly.trade_date <= end_date)
            
            monthly_data = query.order_by(IndexMonthly.trade_date.desc()).limit(limit).all()
            
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
        logger.error(f"获取指数月线数据失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/indices/<ts_code>/weight', methods=['GET'])
def get_index_weight(ts_code):
    """获取指数成分股权重"""
    try:
        trade_date = request.args.get('trade_date', '')
        limit = request.args.get('limit', 100, type=int)
        
        session = get_session()
        try:
            query = session.query(IndexWeight).filter_by(index_code=ts_code)
            
            if trade_date:
                query = query.filter(IndexWeight.trade_date == trade_date)
            else:
                # 如果没有指定日期，获取最新的日期
                latest_date = session.query(func.max(IndexWeight.trade_date)).filter(
                    IndexWeight.index_code == ts_code
                ).scalar()
                if latest_date:
                    query = query.filter(IndexWeight.trade_date == latest_date)
            
            weights = query.order_by(IndexWeight.weight.desc()).limit(limit).all()
            
            result = []
            for weight in weights:
                result.append({
                    'con_code': weight.con_code,
                    'trade_date': weight.trade_date,
                    'weight': float(weight.weight) if weight.weight else None
                })
            
            return jsonify({'code': 0, 'message': 'success', 'data': result})
        finally:
            session.close()
    except Exception as e:
        logger.error(f"获取指数成分股权重失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/custom-strategy/generate-sql', methods=['POST'])
def generate_custom_strategy_sql():
    """调用DeepSeek API生成SQL"""
    try:
        data = request.get_json()
        description = data.get('description', '')
        
        if not description:
            return jsonify({'code': -1, 'message': '策略描述不能为空'}), 400
        
        # 获取数据库表结构信息
        from sqlalchemy import inspect
        from database import get_engine
        session = get_session()
        
        try:
            # 使用 get_engine() 获取 engine，更可靠
            try:
                engine = get_engine()
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                if not tables:
                    logger.warning("数据库中没有找到任何表")
            except Exception as e:
                logger.error(f"获取数据库表结构失败: {e}", exc_info=True)
                raise
            
            # 构建表结构信息
            tables_info = []
            for table_name in sorted(tables):
                try:
                    columns = inspector.get_columns(table_name)
                    columns_info = []
                    for col in columns:
                        columns_info.append({
                            'name': col['name'],
                            'type': str(col['type']),
                            'nullable': col.get('nullable', True),
                            'comment': col.get('comment', '')
                        })
                    tables_info.append({
                        'name': table_name,
                        'columns': columns_info
                    })
                except Exception as e:
                    logger.warning(f"获取表 {table_name} 的结构信息失败: {e}")
                    continue
            
            # 构建提示词
            tables_list = []
            for t in tables_info:
                columns_str = ', '.join([f"{c['name']}({c['type']})" for c in t['columns']])
                tables_list.append(f"表名：{t['name']}\n字段：{columns_str}")
            tables_str = '\n'.join(tables_list)
            json_format = """```json
{{
  "sql": "SELECT ...",
  "missing_tables": ["表名1", "表名2"],
  "missing_fields": ["表名.字段名1", "表名.字段名2"]
}}
```"""
            
            prompt = f"""你是一个专业的SQL查询生成专家。根据用户的需求描述，生成一个MySQL查询语句。

数据库表结构：
{tables_str}

用户需求：{description}

要求：
1. 生成的SQL应该能够从股票数据表中筛选出符合条件的股票
2. SQL必须返回以下字段：ts_code（股票代码）、symbol（股票代码）、name（股票名称）、industry（行业）、trade_date（交易日期）、close（收盘价）、pct_chg（涨跌幅）、vol（成交量）、amount（成交额）
3. 如果用户需求中提到了需要某些数据，但数据库表中没有对应的字段，请在响应中明确指出缺失的数据表或字段
4. SQL应该使用最新的交易日期（trade_date）的数据
5. 只返回SQL语句，不要包含其他解释

请生成SQL查询语句，格式如下：
{json_format}
"""
            
            # 调用DeepSeek API
            import json as json_lib
            deepseek_api_key = os.environ.get('DEEPSEEK_API_KEY', '')
            if not deepseek_api_key:
                # 尝试从配置文件读取
                try:
                    from config import get_config
                    config = get_config()
                    deepseek_api_key = config.get('deepseek', {}).get('api_key', '')
                except:
                    pass
            
            if not deepseek_api_key:
                return jsonify({
                    'code': -1,
                    'message': 'DeepSeek API Key未配置，请在环境变量DEEPSEEK_API_KEY或config.json中配置'
                }), 500
            
            # 调用DeepSeek API
            deepseek_url = 'https://api.deepseek.com/v1/chat/completions'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {deepseek_api_key}'
            }
            payload = {
                'model': 'deepseek-chat',
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是一个专业的SQL查询生成专家，能够根据用户需求生成准确的MySQL查询语句。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.3,
                'max_tokens': 2000
            }
            
            response = requests.post(deepseek_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # 解析响应
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # 尝试从响应中提取JSON
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if not json_match:
                json_match = re.search(r'\{.*?"sql".*?\}', content, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1) if json_match.group(1) else json_match.group(0)
                try:
                    parsed = json_lib.loads(json_str)
                    sql = parsed.get('sql', '')
                    missing_tables = parsed.get('missing_tables', [])
                    missing_fields = parsed.get('missing_fields', [])
                except:
                    # 如果解析失败，尝试直接提取SQL
                    sql_match = re.search(r'SELECT.*?;', content, re.DOTALL | re.IGNORECASE)
                    sql = sql_match.group(0) if sql_match else content
                    missing_tables = []
                    missing_fields = []
            else:
                # 如果没有找到JSON，尝试直接提取SQL
                sql_match = re.search(r'SELECT.*?;', content, re.DOTALL | re.IGNORECASE)
                sql = sql_match.group(0) if sql_match else content
                missing_tables = []
                missing_fields = []
            
            # 验证SQL安全性（只允许SELECT语句）
            sql_upper = sql.strip().upper()
            if not sql_upper.startswith('SELECT'):
                return jsonify({
                    'code': -1,
                    'message': '生成的SQL必须是SELECT查询语句'
                }), 400
            
            # 检查是否有危险操作
            dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE']
            for keyword in dangerous_keywords:
                if keyword in sql_upper:
                    return jsonify({
                        'code': -1,
                        'message': f'生成的SQL包含不允许的操作：{keyword}'
                    }), 400
            
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'sql': sql,
                    'missing_tables': missing_tables,
                    'missing_fields': missing_fields
                }
            })
        finally:
            session.close()
    except requests.exceptions.RequestException as e:
        logger.error(f"调用DeepSeek API失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': f'调用DeepSeek API失败: {str(e)}'}), 500
    except Exception as e:
        error_msg = str(e)
        logger.error(f"生成SQL失败: {error_msg}", exc_info=True)
        # 如果是数据库相关错误，提供更友好的提示
        if 'doesn\'t exist' in error_msg or '不存在' in error_msg:
            return jsonify({
                'code': -1,
                'message': f'数据库表不存在，请先创建相关数据表。错误详情: {error_msg}'
            }), 500
        return jsonify({'code': -1, 'message': error_msg}), 500


@app.route('/api/custom-strategy/preview-sql', methods=['POST'])
def preview_custom_strategy_sql():
    """预览SQL查询结果（不保存）"""
    try:
        data = request.get_json()
        sql_query = data.get('sql_query', '').strip()
        
        if not sql_query:
            return jsonify({'code': -1, 'message': 'SQL查询语句不能为空'}), 400
        
        # 验证SQL安全性
        sql_upper = sql_query.strip().upper()
        if not sql_upper.startswith('SELECT'):
            return jsonify({'code': -1, 'message': 'SQL必须是SELECT查询语句'}), 400
        
        # 检查是否有危险操作
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE']
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return jsonify({
                    'code': -1,
                    'message': f'SQL包含不允许的操作：{keyword}'
                }), 400
        
        session = get_session()
        try:
            # 获取最新交易日期
            latest_date = session.query(func.max(StockDaily.trade_date)).scalar()
            if not latest_date:
                return jsonify({'code': -1, 'message': '没有可用的交易数据'}), 400
            
            # 执行SQL查询
            from sqlalchemy import text
            import re
            try:
                # 加强SQL注入防护
                # 1. 检查是否包含注释（可能用于SQL注入）
                if '--' in sql_query or '/*' in sql_query or '*/' in sql_query:
                    return jsonify({
                        'code': -1,
                        'message': 'SQL包含不允许的注释符号'
                    }), 400
                
                # 2. 检查是否包含分号后的其他语句（防止多语句注入）
                sql_parts = sql_query.split(';')
                if len(sql_parts) > 1:
                    # 检查分号后是否有非空白内容
                    for part in sql_parts[1:]:
                        if part.strip():
                            return jsonify({
                                'code': -1,
                                'message': 'SQL包含多个语句，不允许'
                            }), 400
                
                # 3. 检查是否包含UNION注入
                sql_upper = sql_query.upper()
                # 允许UNION但需要严格检查
                if 'UNION' in sql_upper:
                    # 检查UNION后是否跟着SELECT（正常的UNION）
                    union_pattern = r'UNION\s+(?:ALL\s+)?SELECT'
                    if not re.search(union_pattern, sql_upper):
                        return jsonify({
                            'code': -1,
                            'message': 'SQL中的UNION语句格式不正确'
                        }), 400
                
                # 4. 使用参数化查询替换日期占位符
                sql = sql_query
                # 将 {trade_date} 替换为参数化查询
                if '{trade_date}' in sql:
                    # 使用参数化查询，避免SQL注入
                    # 注意：SQLAlchemy的text()支持命名参数绑定
                    sql = sql.replace('{trade_date}', ':trade_date')
                    query = text(sql).bindparams(trade_date=latest_date)
                else:
                    # 如果没有占位符，直接使用text，但已经通过前面的检查
                    # 注意：即使没有占位符，也使用text()来执行，确保安全性
                    query = text(sql)
                
                result = session.execute(query)
                
                # 获取列名
                columns = list(result.keys())
                
                # 检查必需的列
                required_columns = ['ts_code']
                missing_columns = [col for col in required_columns if col not in columns]
                if missing_columns:
                    return jsonify({
                        'code': -1,
                        'message': f'SQL查询结果缺少必需的列：{", ".join(missing_columns)}'
                    }), 400
                
                # 获取数据（限制最多1000条，避免数据过大）
                rows = []
                row_count = 0
                max_rows = 1000
                
                for row in result:
                    if row_count >= max_rows:
                        break
                    
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        if isinstance(value, datetime):
                            value = value.strftime('%Y-%m-%d %H:%M:%S')
                        elif value is None:
                            value = None
                        else:
                            # 保持原始类型，但确保可以JSON序列化
                            value = value
                        row_dict[col] = value
                    rows.append(row_dict)
                    row_count += 1
                
                # 获取股票基本信息（用于显示股票名称等）
                stock_info_map = {}
                if rows:
                    ts_codes = [row.get('ts_code') for row in rows if row.get('ts_code')]
                    if ts_codes:
                        stocks = session.query(StockBasic).filter(
                            StockBasic.ts_code.in_(ts_codes)
                        ).all()
                        for stock in stocks:
                            stock_info_map[stock.ts_code] = {
                                'name': stock.name,
                                'symbol': stock.symbol,
                                'industry': stock.industry
                            }
                
                return jsonify({
                    'code': 0,
                    'message': 'success',
                    'data': {
                        'columns': columns,
                        'rows': rows,
                        'count': len(rows),
                        'stock_info': stock_info_map,
                        'latest_date': latest_date,
                        'has_more': row_count >= max_rows
                    }
                })
            except Exception as e:
                logger.error(f"执行SQL预览失败: {e}", exc_info=True)
                error_msg = str(e)
                # 提供更友好的错误信息
                if 'doesn\'t exist' in error_msg or '不存在' in error_msg:
                    return jsonify({
                        'code': -1,
                        'message': f'SQL执行失败：表或字段不存在。错误详情: {error_msg}'
                    }), 400
                return jsonify({
                    'code': -1,
                    'message': f'SQL执行失败: {error_msg}'
                }), 400
        finally:
            session.close()
    except Exception as e:
        logger.error(f"预览SQL失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/custom-strategy', methods=['GET'])
def get_custom_strategies():
    """获取自定义策略列表"""
    try:
        session = get_session()
        try:
            strategies = session.query(CustomStrategy).order_by(CustomStrategy.created_at.desc()).all()
            
            result = []
            for strategy in strategies:
                missing_tables = []
                try:
                    if strategy.missing_tables:
                        missing_tables = json.loads(strategy.missing_tables)
                except:
                    pass
                
                result.append({
                    'id': strategy.id,
                    'name': strategy.name,
                    'description': strategy.description,
                    'sql_query': strategy.sql_query,
                    'missing_tables': missing_tables,
                    'execution_rule': strategy.execution_rule,
                    'execution_time': strategy.execution_time,
                    'is_active': strategy.is_active == 1,
                    'created_at': strategy.created_at.strftime('%Y-%m-%d %H:%M:%S') if strategy.created_at else None,
                    'updated_at': strategy.updated_at.strftime('%Y-%m-%d %H:%M:%S') if strategy.updated_at else None,
                    'last_executed_at': strategy.last_executed_at.strftime('%Y-%m-%d %H:%M:%S') if strategy.last_executed_at else None
                })
            
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': result
            })
        finally:
            session.close()
    except Exception as e:
        logger.error(f"获取自定义策略列表失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/custom-strategy', methods=['POST'])
def create_custom_strategy():
    """创建自定义策略"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '')
        sql_query = data.get('sql_query', '').strip()
        missing_tables = data.get('missing_tables', [])
        execution_rule = data.get('execution_rule', 'daily')
        execution_time = data.get('execution_time', '15:30')
        
        if not name:
            return jsonify({'code': -1, 'message': '策略名称不能为空'}), 400
        
        if not sql_query:
            return jsonify({'code': -1, 'message': 'SQL查询语句不能为空'}), 400
        
        # 验证SQL安全性
        sql_upper = sql_query.strip().upper()
        if not sql_upper.startswith('SELECT'):
            return jsonify({'code': -1, 'message': 'SQL必须是SELECT查询语句'}), 400
        
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE']
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return jsonify({'code': -1, 'message': f'SQL包含不允许的操作：{keyword}'}), 400
        
        session = get_session()
        try:
            # 检查名称是否已存在
            existing = session.query(CustomStrategy).filter_by(name=name).first()
            if existing:
                return jsonify({'code': -1, 'message': '策略名称已存在'}), 400
            
            # 创建策略
            strategy = CustomStrategy(
                name=name,
                description=description,
                sql_query=sql_query,
                missing_tables=json.dumps(missing_tables) if missing_tables else None,
                execution_rule=execution_rule,
                execution_time=execution_time,
                is_active=1,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(strategy)
            session.commit()
            
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'id': strategy.id,
                    'name': strategy.name
                }
            })
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    except Exception as e:
        logger.error(f"创建自定义策略失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/custom-strategy/<int:strategy_id>', methods=['PUT'])
def update_custom_strategy(strategy_id):
    """更新自定义策略"""
    try:
        data = request.get_json()
        session = get_session()
        try:
            strategy = session.query(CustomStrategy).filter_by(id=strategy_id).first()
            if not strategy:
                return jsonify({'code': -1, 'message': '策略不存在'}), 404
            
            # 更新字段
            if 'name' in data:
                name = data['name'].strip()
                if name and name != strategy.name:
                    # 检查名称是否已被其他策略使用
                    existing = session.query(CustomStrategy).filter(
                        CustomStrategy.name == name,
                        CustomStrategy.id != strategy_id
                    ).first()
                    if existing:
                        return jsonify({'code': -1, 'message': '策略名称已存在'}), 400
                    strategy.name = name
            
            if 'description' in data:
                strategy.description = data['description']
            
            if 'sql_query' in data:
                sql_query = data['sql_query'].strip()
                # 验证SQL安全性
                sql_upper = sql_query.strip().upper()
                if not sql_upper.startswith('SELECT'):
                    return jsonify({'code': -1, 'message': 'SQL必须是SELECT查询语句'}), 400
                
                dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE']
                for keyword in dangerous_keywords:
                    if keyword in sql_upper:
                        return jsonify({'code': -1, 'message': f'SQL包含不允许的操作：{keyword}'}), 400
                strategy.sql_query = sql_query
            
            if 'missing_tables' in data:
                strategy.missing_tables = json.dumps(data['missing_tables']) if data['missing_tables'] else None
            
            if 'execution_rule' in data:
                strategy.execution_rule = data['execution_rule']
            
            if 'execution_time' in data:
                strategy.execution_time = data['execution_time']
            
            if 'is_active' in data:
                strategy.is_active = 1 if data['is_active'] else 0
            
            strategy.updated_at = datetime.now()
            session.commit()
            
            return jsonify({'code': 0, 'message': 'success'})
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    except Exception as e:
        logger.error(f"更新自定义策略失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/custom-strategy/<int:strategy_id>', methods=['DELETE'])
def delete_custom_strategy(strategy_id):
    """删除自定义策略"""
    try:
        session = get_session()
        try:
            strategy = session.query(CustomStrategy).filter_by(id=strategy_id).first()
            if not strategy:
                return jsonify({'code': -1, 'message': '策略不存在'}), 404
            
            session.delete(strategy)
            session.commit()
            
            return jsonify({'code': 0, 'message': 'success'})
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    except Exception as e:
        logger.error(f"删除自定义策略失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/api/custom-strategy/<int:strategy_id>/execute', methods=['POST'])
def execute_custom_strategy(strategy_id):
    """执行自定义策略"""
    try:
        session = get_session()
        try:
            strategy = session.query(CustomStrategy).filter_by(id=strategy_id).first()
            if not strategy:
                return jsonify({'code': -1, 'message': '策略不存在'}), 404
            
            if strategy.is_active != 1:
                return jsonify({'code': -1, 'message': '策略未启用'}), 400
            
            # 获取最新交易日期
            latest_date = session.query(func.max(StockDaily.trade_date)).scalar()
            if not latest_date:
                return jsonify({'code': -1, 'message': '没有可用的交易数据'}), 400
            
            # 执行SQL查询
            from sqlalchemy import text
            try:
                # 替换SQL中的日期占位符（如果有）
                sql = strategy.sql_query
                if '{trade_date}' in sql:
                    sql = sql.replace('{trade_date}', latest_date)
                
                query = text(sql)
                result = session.execute(query)
                
                # 获取列名
                columns = list(result.keys())
                
                # 检查必需的列
                required_columns = ['ts_code']
                missing_columns = [col for col in required_columns if col not in columns]
                if missing_columns:
                    return jsonify({
                        'code': -1,
                        'message': f'SQL查询结果缺少必需的列：{", ".join(missing_columns)}'
                    }), 400
                
                # 获取数据
                rows = []
                for row in result:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        if isinstance(value, datetime):
                            value = value.strftime('%Y-%m-%d %H:%M:%S')
                        row_dict[col] = value
                    rows.append(row_dict)
                
                # 保存选股结果
                saved_count = 0
                for row in rows:
                    ts_code = row.get('ts_code')
                    if not ts_code:
                        continue
                    
                    # 获取股票基本信息
                    stock = session.query(StockBasic).filter_by(ts_code=ts_code).first()
                    if not stock:
                        continue
                    
                    # 获取最新日线数据
                    daily = session.query(StockDaily).filter(
                        StockDaily.ts_code == ts_code,
                        StockDaily.trade_date == latest_date
                    ).first()
                    
                    # 构建选股理由
                    reason_parts = []
                    if daily:
                        if daily.pct_chg:
                            reason_parts.append(f"涨跌幅: {daily.pct_chg:.2f}%")
                        if daily.vol:
                            reason_parts.append(f"成交量: {daily.vol:.0f}")
                    reason = " | ".join(reason_parts) if reason_parts else "自定义策略选股"
                    
                    # 计算评分（可以根据SQL结果中的字段计算，这里简化处理）
                    score = 0.0
                    if 'score' in row and row['score']:
                        try:
                            score = float(row['score'])
                        except:
                            pass
                    
                    # 检查是否已存在
                    existing = session.query(StockSelection).filter_by(
                        ts_code=ts_code,
                        strategy_name=strategy.name,
                        trade_date=latest_date
                    ).first()
                    
                    if existing:
                        existing.score = score
                        existing.reason = reason
                        existing.created_at = datetime.now()
                    else:
                        selection = StockSelection(
                            ts_code=ts_code,
                            strategy_name=strategy.name,
                            trade_date=latest_date,
                            score=score,
                            reason=reason,
                            created_at=datetime.now()
                        )
                        session.add(selection)
                    
                    saved_count += 1
                
                session.commit()
                
                # 更新策略的最后执行时间
                strategy.last_executed_at = datetime.now()
                session.commit()
                
                return jsonify({
                    'code': 0,
                    'message': 'success',
                    'data': {
                        'saved_count': saved_count,
                        'trade_date': latest_date
                    }
                })
            except Exception as e:
                session.rollback()
                logger.error(f"执行SQL失败: {e}", exc_info=True)
                return jsonify({'code': -1, 'message': f'执行SQL失败: {str(e)}'}), 500
        finally:
            session.close()
    except Exception as e:
        logger.error(f"执行自定义策略失败: {e}", exc_info=True)
        return jsonify({'code': -1, 'message': str(e)}), 500


@app.route('/robots.txt', methods=['GET'])
def robots_txt():
    """返回robots.txt文件"""
    import config
    
    # 从配置文件读取域名
    seo_config = config.get_seo_config()
    site_url = seo_config.get('site_url', 'https://your-domain.com')
    sitemap_url = f"{site_url}/sitemap.xml"
    
    robots_content = f"""User-agent: *
Allow: /

# Sitemap
Sitemap: {sitemap_url}

# 禁止爬取的路径
Disallow: /api/
Disallow: /admin/
"""
    return app.response_class(
        robots_content,
        mimetype='text/plain'
    )


@app.route('/sitemap.xml', methods=['GET'])
def sitemap_xml():
    """生成并返回sitemap.xml"""
    from datetime import datetime
    import config
    
    # 优先使用配置文件中的域名
    seo_config = config.get_seo_config()
    base_url = seo_config.get('site_url', 'https://your-domain.com')
    # 如果是本地开发环境且配置为默认值，尝试使用请求的host
    if base_url == 'https://your-domain.com':
        request_url = request.host_url.rstrip('/')
        if 'localhost' not in request_url and '127.0.0.1' not in request_url:
            base_url = request_url
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
  <!-- 首页 -->
  <url>
    <loc>{base_url}/</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  
  <!-- 股票列表页 -->
  <url>
    <loc>{base_url}/stocks</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
  
  <!-- IPO新股页 -->
  <url>
    <loc>{base_url}/ipo</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
  
  <!-- 策略选股页 -->
  <url>
    <loc>{base_url}/strategy/selection</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>
  
  <!-- 外盘跟踪页 -->
  <url>
    <loc>{base_url}/global</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.7</priority>
  </url>
  
  <!-- 大佬追踪页 -->
  <url>
    <loc>{base_url}/bigplayers</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
</urlset>'''
    
    return app.response_class(
        sitemap,
        mimetype='application/xml'
    )


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


@app.route('/favicon.ico')
def favicon():
    """返回favicon"""
    try:
        favicon_path = os.path.join(FRONTEND_DIST, 'favicon.ico')
        if os.path.exists(favicon_path):
            return send_from_directory(FRONTEND_DIST, 'favicon.ico')
    except:
        pass
    return '', 204  # No Content


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

