#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
技术指标计算模块
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional


def calculate_ma(data: pd.Series, period: int) -> pd.Series:
    """计算移动平均线（MA）"""
    return data.rolling(window=period).mean()


def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """计算指数移动平均线（EMA）"""
    return data.ewm(span=period, adjust=False).mean()


def calculate_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
    """计算MACD指标
    
    Returns:
        {
            'macd': MACD线,
            'signal': 信号线,
            'hist': 柱状图
        }
    """
    ema_fast = calculate_ema(close, fast)
    ema_slow = calculate_ema(close, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    hist = macd_line - signal_line
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'hist': hist
    }


def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """计算RSI指标（相对强弱指标）"""
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_kdj(high: pd.Series, low: pd.Series, close: pd.Series, 
                  period: int = 9, k_period: int = 3, d_period: int = 3) -> Dict:
    """计算KDJ指标
    
    Returns:
        {
            'k': K值,
            'd': D值,
            'j': J值
        }
    """
    low_min = low.rolling(window=period).min()
    high_max = high.rolling(window=period).max()
    
    rsv = (close - low_min) / (high_max - low_min) * 100
    
    k = rsv.ewm(com=k_period - 1, adjust=False).mean()
    d = k.ewm(com=d_period - 1, adjust=False).mean()
    j = 3 * k - 2 * d
    
    return {
        'k': k,
        'd': d,
        'j': j
    }


def calculate_bollinger_bands(close: pd.Series, period: int = 20, std_dev: int = 2) -> Dict:
    """计算布林带（Bollinger Bands）
    
    Returns:
        {
            'upper': 上轨,
            'middle': 中轨（MA）,
            'lower': 下轨
        }
    """
    middle = calculate_ma(close, period)
    std = close.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    
    return {
        'upper': upper,
        'middle': middle,
        'lower': lower
    }


def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """计算OBV指标（能量潮）"""
    obv = pd.Series(index=close.index, dtype=float)
    obv.iloc[0] = volume.iloc[0]
    
    for i in range(1, len(close)):
        if close.iloc[i] > close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
        elif close.iloc[i] < close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i-1]
    
    return obv


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """计算ATR指标（平均真实波幅）"""
    high_low = high - low
    high_close = np.abs(high - close.shift())
    low_close = np.abs(low - close.shift())
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    
    atr = true_range.rolling(window=period).mean()
    
    return atr


def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """计算所有技术指标
    
    Args:
        df: 包含 open, high, low, close, vol 列的DataFrame，按日期升序排列
    
    Returns:
        添加了技术指标的DataFrame
    """
    df = df.copy()
    df = df.sort_values('trade_date')
    
    close = df['close']
    high = df['high']
    low = df['low']
    volume = df['vol']
    
    # MA均线
    df['ma5'] = calculate_ma(close, 5)
    df['ma10'] = calculate_ma(close, 10)
    df['ma20'] = calculate_ma(close, 20)
    df['ma30'] = calculate_ma(close, 30)
    df['ma60'] = calculate_ma(close, 60)
    
    # MACD
    macd_data = calculate_macd(close)
    df['macd'] = macd_data['macd']
    df['macd_signal'] = macd_data['signal']
    df['macd_hist'] = macd_data['hist']
    
    # RSI
    df['rsi'] = calculate_rsi(close)
    
    # KDJ
    kdj_data = calculate_kdj(high, low, close)
    df['kdj_k'] = kdj_data['k']
    df['kdj_d'] = kdj_data['d']
    df['kdj_j'] = kdj_data['j']
    
    # 布林带
    bb_data = calculate_bollinger_bands(close)
    df['bb_upper'] = bb_data['upper']
    df['bb_middle'] = bb_data['middle']
    df['bb_lower'] = bb_data['lower']
    
    # OBV
    df['obv'] = calculate_obv(close, volume)
    
    # ATR
    df['atr'] = calculate_atr(high, low, close)
    
    return df


def get_technical_signals(df: pd.DataFrame) -> Dict:
    """获取技术指标信号
    
    Returns:
        包含各种技术信号的字典
    """
    if len(df) < 2:
        return {}
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    signals = {}
    
    # MA信号
    if 'ma5' in df.columns and 'ma20' in df.columns:
        if latest['ma5'] > latest['ma20'] and prev['ma5'] <= prev['ma20']:
            signals['ma_golden_cross'] = True  # 金叉
        elif latest['ma5'] < latest['ma20'] and prev['ma5'] >= prev['ma20']:
            signals['ma_death_cross'] = True  # 死叉
    
    # MACD信号
    if 'macd' in df.columns and 'macd_signal' in df.columns:
        if latest['macd'] > latest['macd_signal'] and prev['macd'] <= prev['macd_signal']:
            signals['macd_buy'] = True
        elif latest['macd'] < latest['macd_signal'] and prev['macd'] >= prev['macd_signal']:
            signals['macd_sell'] = True
    
    # RSI信号
    if 'rsi' in df.columns:
        if latest['rsi'] < 30:
            signals['rsi_oversold'] = True  # 超卖
        elif latest['rsi'] > 70:
            signals['rsi_overbought'] = True  # 超买
    
    # KDJ信号
    if 'kdj_k' in df.columns and 'kdj_d' in df.columns:
        if latest['kdj_k'] > latest['kdj_d'] and prev['kdj_k'] <= prev['kdj_d']:
            signals['kdj_golden_cross'] = True
        elif latest['kdj_k'] < latest['kdj_d'] and prev['kdj_k'] >= prev['kdj_d']:
            signals['kdj_death_cross'] = True
    
    return signals



