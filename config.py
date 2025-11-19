#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
配置文件 - 从JSON文件读取配置，支持热重载
"""
import json
import os
import time
import threading

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

# 配置缓存
_config_cache = None
_config_mtime = 0
_config_lock = threading.Lock()


def load_config():
    """加载配置文件"""
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"配置文件不存在: {CONFIG_FILE}")
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config


def reload_config():
    """重新加载配置（如果文件被修改）"""
    global _config_cache, _config_mtime
    
    try:
        current_mtime = os.path.getmtime(CONFIG_FILE)
        
        # 如果文件被修改，重新加载
        if current_mtime != _config_mtime:
            with _config_lock:
                # 双重检查，避免并发问题
                if current_mtime != _config_mtime:
                    _config_cache = load_config()
                    _config_mtime = current_mtime
                    print(f"[配置] 配置文件已重新加载: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    return True
        return False
    except Exception as e:
        print(f"[配置] 重新加载配置失败: {e}")
        return False


def get_config():
    """获取配置（自动检查是否需要重新加载）"""
    global _config_cache, _config_mtime
    
    # 检查是否需要重新加载
    reload_config()
    
    # 如果缓存为空，首次加载
    if _config_cache is None:
        with _config_lock:
            if _config_cache is None:
                _config_cache = load_config()
                _config_mtime = os.path.getmtime(CONFIG_FILE)
    
    return _config_cache


# 初始化配置
_config = get_config()

# Tushare配置（使用函数获取，支持热重载）
def get_tushare_token():
    """获取Tushare Token（支持热重载）"""
    config = get_config()
    return config.get('tushare', {}).get('token', '')

TUSHARE_TOKEN = get_tushare_token()

# MySQL数据库配置（使用函数获取，支持热重载）
def get_mysql_config():
    """获取MySQL配置（支持热重载）"""
    config = get_config()
    mysql_config = config.get('mysql', {})
    return {
        'host': mysql_config.get('host', 'localhost'),
        'port': int(mysql_config.get('port', 3306)),
        'user': mysql_config.get('user', 'root'),
        'password': mysql_config.get('password', ''),
        'database': mysql_config.get('database', 'stock_data'),
        'charset': mysql_config.get('charset', 'utf8mb4')
    }

MYSQL_CONFIG = get_mysql_config()

# Flask配置（使用函数获取，支持热重载）
def get_flask_config():
    """获取Flask配置（支持热重载）"""
    config = get_config()
    flask_config = config.get('flask', {})
    return {
        'host': flask_config.get('host', '0.0.0.0'),
        'port': int(flask_config.get('port', 5000)),
        'debug': flask_config.get('debug', False)
    }

_flask_config = get_flask_config()
FLASK_HOST = _flask_config['host']
FLASK_PORT = _flask_config['port']
FLASK_DEBUG = _flask_config['debug']

# SEO配置（使用函数获取，支持热重载）
def get_seo_config():
    """获取SEO配置（支持热重载）"""
    config = get_config()
    seo_config = config.get('seo', {})
    return {
        'site_url': seo_config.get('site_url', 'https://your-domain.com'),
        'site_name': seo_config.get('site_name', 'Red-Stock'),
        'site_description': seo_config.get('site_description', '专业的A股数据分析平台')
    }

_seo_config = get_seo_config()
SEO_SITE_URL = _seo_config['site_url']
SEO_SITE_NAME = _seo_config['site_name']
SEO_SITE_DESCRIPTION = _seo_config['site_description']

# 微信配置（使用函数获取，支持热重载）
def get_wechat_config():
    """获取微信配置（支持热重载）"""
    config = get_config()
    wechat_config = config.get('wechat', {})
    return {
        'app_id': wechat_config.get('app_id', ''),
        'app_secret': wechat_config.get('app_secret', ''),
        'redirect_uri': wechat_config.get('redirect_uri', '')
    }

# JWT配置（使用函数获取，支持热重载）
def get_jwt_config():
    """获取JWT配置（支持热重载）"""
    config = get_config()
    jwt_config = config.get('jwt', {})
    return {
        'secret_key': jwt_config.get('secret_key', 'change_me_in_production'),
        'expires_in': int(jwt_config.get('expires_in', 86400)),  # 默认24小时
        'refresh_expires_in': int(jwt_config.get('refresh_expires_in', 604800))  # 默认7天
    }


# 注意：以下变量在模块加载时初始化，如需支持热重载，请使用对应的get_*函数
# TUSHARE_TOKEN - 使用 get_tushare_token() 获取最新值
# MYSQL_CONFIG - 使用 get_mysql_config() 获取最新值  
# FLASK_HOST, FLASK_PORT, FLASK_DEBUG - 使用 get_flask_config() 获取最新值
# SEO_SITE_URL, SEO_SITE_NAME, SEO_SITE_DESCRIPTION - 使用 get_seo_config() 获取最新值
# 微信和JWT配置 - 使用 get_wechat_config() 和 get_jwt_config() 获取最新值

