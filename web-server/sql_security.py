#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
SQL安全检查和验证模块
用于防止SQL注入和越权访问
"""
import re
import logging

logger = logging.getLogger(__name__)

# 允许访问的表白名单（只允许查询股票相关的表）
ALLOWED_TABLES = {
    'stock_basic',
    'stock_daily',
    'stock_weekly',
    'stock_monthly',
    'stock_moneyflow',
    'stock_indicator',
    'stock_favorite',
    'stock_selection',
    'stock_ipo',
    'stock_manager',
    'index_basic',
    'index_daily',
    'index_weekly',
    'index_monthly',
    'index_weight'
}

# 禁止的危险关键字
DANGEROUS_KEYWORDS = [
    'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE',
    'EXEC', 'EXECUTE', 'EXECUTE IMMEDIATE', 'CALL', 'DECLARE', 'CURSOR',
    'GRANT', 'REVOKE', 'LOCK', 'UNLOCK', 'SHOW', 'DESCRIBE', 'DESC',
    'USE', 'SET', 'SHUTDOWN', 'KILL', 'LOAD_FILE', 'INTO OUTFILE',
    'INTO DUMPFILE', 'LOAD DATA', 'SELECT INTO', 'BULK INSERT',
    'XP_CMDSHELL', 'SP_', 'OPENROWSET', 'OPENDATASOURCE'
]

# 禁止的危险函数
DANGEROUS_FUNCTIONS = [
    'LOAD_FILE', 'INTO OUTFILE', 'INTO DUMPFILE', 'BENCHMARK',
    'SLEEP', 'WAITFOR', 'PG_SLEEP', 'USER', 'CURRENT_USER',
    'SYSTEM_USER', 'SESSION_USER', 'DATABASE', 'SCHEMA',
    'VERSION', 'CONNECTION_ID', 'FOUND_ROWS', 'ROW_COUNT'
]

# 禁止访问的系统表/数据库
FORBIDDEN_PATTERNS = [
    r'information_schema',
    r'mysql\.',
    r'sys\.',
    r'performance_schema',
    r'pg_',
    r'pg_catalog',
    r'master\.',
    r'tempdb\.',
    r'msdb\.'
]


class SQLSecurityError(Exception):
    """SQL安全检查错误"""
    pass


def validate_sql_security(sql_query):
    """
    验证SQL查询的安全性
    
    Args:
        sql_query: SQL查询字符串
        
    Returns:
        tuple: (is_valid, error_message)
        
    Raises:
        SQLSecurityError: 如果SQL不安全
    """
    if not sql_query or not sql_query.strip():
        raise SQLSecurityError('SQL查询不能为空')
    
    sql_original = sql_query.strip()
    sql_upper = sql_original.upper()
    
    # 1. 检查必须是SELECT语句
    if not sql_upper.startswith('SELECT'):
        raise SQLSecurityError('只允许SELECT查询语句')
    
    # 2. 检查危险关键字
    for keyword in DANGEROUS_KEYWORDS:
        # 使用单词边界匹配，避免误判（如SELECT中的SELECT）
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, sql_upper):
            raise SQLSecurityError(f'SQL包含不允许的操作：{keyword}')
    
    # 3. 检查危险函数
    for func in DANGEROUS_FUNCTIONS:
        pattern = r'\b' + re.escape(func) + r'\b'
        if re.search(pattern, sql_upper):
            raise SQLSecurityError(f'SQL包含不允许的函数：{func}')
    
    # 4. 检查注释（SQL注入常用手段）
    if '--' in sql_original or '/*' in sql_original or '*/' in sql_original:
        raise SQLSecurityError('SQL包含不允许的注释符号')
    
    # 5. 检查多语句注入（分号后的其他语句）
    sql_parts = sql_original.split(';')
    if len(sql_parts) > 1:
        for i, part in enumerate(sql_parts[1:], 1):
            if part.strip():
                raise SQLSecurityError(f'SQL包含多个语句（第{i+1}个语句），不允许')
    
    # 6. 检查禁止访问的系统表/数据库
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, sql_upper, re.IGNORECASE):
            raise SQLSecurityError(f'禁止访问系统表或数据库：{pattern}')
    
    # 7. 检查表名白名单
    # 提取FROM和JOIN后的表名
    table_pattern = r'\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
    matches = re.findall(table_pattern, sql_upper)
    
    for table_name in matches:
        table_lower = table_name.lower()
        # 检查是否在白名单中
        if table_lower not in ALLOWED_TABLES:
            raise SQLSecurityError(f'不允许访问表：{table_name}。只允许访问以下表：{", ".join(sorted(ALLOWED_TABLES))}')
    
    # 8. 检查UNION注入
    if 'UNION' in sql_upper:
        # 只允许正常的UNION SELECT
        union_pattern = r'UNION\s+(?:ALL\s+)?SELECT'
        if not re.search(union_pattern, sql_upper):
            raise SQLSecurityError('SQL中的UNION语句格式不正确')
        
        # 检查UNION后的SELECT是否也符合安全要求
        # 这里可以进一步检查，但基本格式检查已经完成
    
    # 9. 检查子查询中的危险操作
    # 提取子查询（括号内的SELECT）
    subquery_pattern = r'\([^)]*SELECT[^)]*\)'
    subqueries = re.findall(subquery_pattern, sql_upper, re.IGNORECASE)
    for subquery in subqueries:
        # 检查子查询中是否有危险关键字
        for keyword in DANGEROUS_KEYWORDS:
            if keyword in subquery:
                raise SQLSecurityError(f'子查询中包含不允许的操作：{keyword}')
    
    # 10. 检查是否有字符串拼接注入（如CONCAT、+等）
    # 允许正常的字符串函数，但需要检查是否有可疑的模式
    # 这里主要检查是否有明显的注入模式
    
    # 11. 检查是否有十六进制编码注入
    if re.search(r'0x[0-9a-fA-F]+', sql_original):
        # 允许十六进制，但记录警告
        logger.warning('SQL中包含十六进制编码，需要谨慎检查')
    
    # 12. 检查是否有CHAR函数注入（CHAR(65)等）
    char_pattern = r'CHAR\s*\(\s*\d+\s*\)'
    if re.search(char_pattern, sql_upper):
        logger.warning('SQL中包含CHAR函数，需要谨慎检查')
    
    # 13. 限制查询复杂度（防止DoS攻击）
    # 检查嵌套层级
    open_parens = sql_original.count('(')
    close_parens = sql_original.count(')')
    if open_parens != close_parens:
        raise SQLSecurityError('SQL括号不匹配')
    
    # 限制嵌套深度
    max_depth = 10
    depth = 0
    max_depth_found = 0
    for char in sql_original:
        if char == '(':
            depth += 1
            max_depth_found = max(max_depth_found, depth)
        elif char == ')':
            depth -= 1
            if depth < 0:
                raise SQLSecurityError('SQL括号不匹配')
    
    if max_depth_found > max_depth:
        raise SQLSecurityError(f'SQL嵌套层级过深（{max_depth_found}层），最大允许{max_depth}层')
    
    # 14. 检查是否有明显的注入模式
    injection_patterns = [
        r"'\s*OR\s*'1'\s*=\s*'1",  # ' OR '1'='1
        r"'\s*OR\s*1\s*=\s*1",      # ' OR 1=1
        r"'\s*UNION\s*SELECT",      # ' UNION SELECT
        r"'\s*;\s*DROP",            # '; DROP
        r"'\s*;\s*DELETE",         # '; DELETE
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, sql_upper):
            raise SQLSecurityError('检测到SQL注入攻击模式')
    
    # 15. 检查是否有可疑的字符串操作
    # 允许正常的字符串函数，但需要检查是否有明显的注入意图
    
    # 所有检查通过
    return True, None


def sanitize_sql_for_execution(sql_query, trade_date=None):
    """
    清理SQL查询，准备执行
    
    Args:
        sql_query: SQL查询字符串
        trade_date: 交易日期（可选，用于替换占位符）
        
    Returns:
        tuple: (cleaned_sql, params_dict)
    """
    # 先进行安全检查
    validate_sql_security(sql_query)
    
    # 替换日期占位符（使用参数化查询）
    sql = sql_query.strip()
    params = {}
    
    if '{trade_date}' in sql and trade_date:
        # 使用参数化查询，避免SQL注入
        sql = sql.replace('{trade_date}', ':trade_date')
        params['trade_date'] = trade_date
    
    return sql, params


def check_table_access(table_name):
    """
    检查是否允许访问指定的表
    
    Args:
        table_name: 表名
        
    Returns:
        bool: 是否允许访问
    """
    return table_name.lower() in ALLOWED_TABLES


def get_allowed_tables():
    """
    获取允许访问的表列表
    
    Returns:
        list: 允许访问的表名列表
    """
    return sorted(ALLOWED_TABLES)

