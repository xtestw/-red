# SQL安全检查说明

## 概述

`sql_security.py` 模块提供了全面的SQL安全检查和验证功能，用于防止SQL注入和越权访问。

## 主要功能

### 1. SQL注入防护

- **注释检查**：禁止SQL注释（`--`、`/* */`），防止注入攻击
- **多语句检查**：禁止分号后的其他语句，防止多语句注入
- **UNION注入检查**：严格检查UNION语句格式
- **注入模式检测**：检测常见的SQL注入攻击模式

### 2. 越权访问防护

- **表名白名单**：只允许访问预定义的表（股票相关表）
- **系统表保护**：禁止访问系统表（如 `information_schema`、`mysql` 等）
- **数据库隔离**：禁止访问其他数据库

### 3. 危险操作防护

- **危险关键字检查**：禁止 `DROP`、`DELETE`、`UPDATE`、`INSERT` 等操作
- **危险函数检查**：禁止 `LOAD_FILE`、`INTO OUTFILE` 等危险函数
- **只读限制**：只允许 `SELECT` 查询语句

### 4. 查询复杂度限制

- **嵌套深度限制**：限制SQL嵌套层级（最大10层）
- **括号匹配检查**：确保SQL语法正确

## 允许访问的表

以下表可以安全访问：

- `stock_basic` - 股票基本信息
- `stock_daily` - 股票日线数据
- `stock_weekly` - 股票周线数据
- `stock_monthly` - 股票月线数据
- `stock_moneyflow` - 股票资金流向
- `stock_indicator` - 股票指标
- `stock_favorite` - 股票收藏
- `stock_selection` - 选股结果
- `stock_ipo` - IPO新股
- `stock_manager` - 上市公司管理层
- `index_basic` - 指数基本信息
- `index_daily` - 指数日线数据
- `index_weekly` - 指数周线数据
- `index_monthly` - 指数月线数据
- `index_weight` - 指数成分股权重

## 使用方法

### 基本使用

```python
from sql_security import validate_sql_security, sanitize_sql_for_execution

# 验证SQL安全性
try:
    validate_sql_security(sql_query)
    print("SQL安全检查通过")
except SQLSecurityError as e:
    print(f"SQL不安全: {e}")

# 清理SQL并准备执行
sql, params = sanitize_sql_for_execution(sql_query, trade_date='20241118')
```

### 在Flask API中使用

```python
from sqlalchemy import text
from sql_security import validate_sql_security, sanitize_sql_for_execution

@app.route('/api/custom-strategy/preview-sql', methods=['POST'])
def preview_sql():
    sql_query = request.json.get('sql_query')
    
    # 安全检查
    try:
        validate_sql_security(sql_query)
    except SQLSecurityError as e:
        return jsonify({'code': -1, 'message': str(e)}), 400
    
    # 清理并执行
    sql, params = sanitize_sql_for_execution(sql_query, trade_date)
    query = text(sql).bindparams(**params) if params else text(sql)
    result = session.execute(query)
```

## 安全检查项

### 1. 基础检查
- ✅ 必须是SELECT语句
- ✅ 禁止危险关键字（DROP、DELETE等）
- ✅ 禁止危险函数（LOAD_FILE等）
- ✅ 禁止注释符号

### 2. 注入防护
- ✅ 禁止多语句执行
- ✅ UNION语句格式检查
- ✅ 注入模式检测
- ✅ 子查询安全检查

### 3. 越权防护
- ✅ 表名白名单验证
- ✅ 系统表访问禁止
- ✅ 数据库隔离

### 4. 复杂度限制
- ✅ 嵌套深度限制（10层）
- ✅ 括号匹配检查

## 安全建议

1. **始终使用参数化查询**：使用 `bindparams()` 而不是字符串拼接
2. **定期更新白名单**：根据业务需求更新允许访问的表
3. **记录安全日志**：记录所有被拒绝的SQL查询
4. **限制查询结果**：限制返回的行数，防止DoS攻击
5. **定期审计**：定期检查SQL执行日志，发现异常模式

## 示例

### 允许的SQL

```sql
-- ✅ 基本查询
SELECT ts_code, name, close FROM stock_daily WHERE trade_date = '20241118'

-- ✅ 带JOIN的查询
SELECT s.ts_code, s.name, d.close 
FROM stock_basic s 
JOIN stock_daily d ON s.ts_code = d.ts_code 
WHERE d.trade_date = '20241118'

-- ✅ 使用聚合函数
SELECT industry, COUNT(*) as count, AVG(close) as avg_close
FROM stock_basic s
JOIN stock_daily d ON s.ts_code = d.ts_code
WHERE d.trade_date = '20241118'
GROUP BY industry

-- ✅ 使用占位符
SELECT * FROM stock_daily WHERE trade_date = '{trade_date}'
```

### 禁止的SQL

```sql
-- ❌ 非SELECT语句
DELETE FROM stock_daily WHERE trade_date = '20241118'

-- ❌ 访问系统表
SELECT * FROM information_schema.tables

-- ❌ 多语句注入
SELECT * FROM stock_daily; DROP TABLE stock_daily

-- ❌ 注释注入
SELECT * FROM stock_daily -- WHERE 1=1

-- ❌ 访问未授权表
SELECT * FROM users

-- ❌ 危险函数
SELECT LOAD_FILE('/etc/passwd')
```

## 注意事项

1. **性能影响**：安全检查会增加少量性能开销，但这是必要的安全措施
2. **误报可能**：某些复杂的合法SQL可能被误判，需要根据实际情况调整规则
3. **持续更新**：随着新的攻击手段出现，需要持续更新安全检查规则

## 更新日志

- 2024-11-18: 初始版本，实现基础SQL安全检查
- 包含15项安全检查项
- 支持表名白名单
- 支持参数化查询

