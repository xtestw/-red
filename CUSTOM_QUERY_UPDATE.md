# 自定义查询功能更新说明

## 更新内容

### 1. 新增数据库表 `custom_query`

创建了新的数据库表用于存储用户查询条件和生成的SQL：

**表结构：**
- `id` - 主键ID
- `user_id` - 用户ID（可选）
- `query_description` - 查询条件描述
- `generated_sql` - 生成的SQL查询语句
- `missing_tables` - 缺失的数据表（JSON格式）
- `missing_fields` - 缺失的字段（JSON格式）
- `status` - 状态（pending/success/failed）
- `error_message` - 错误信息
- `execution_count` - 执行次数
- `last_executed_at` - 最后执行时间
- `created_at` - 创建时间
- `updated_at` - 更新时间

**创建表SQL：**
```bash
mysql -u root -p stock_data < add_custom_query_table.sql
```

### 2. API接口更新

#### 2.1 生成SQL接口 (`/api/custom-strategy/generate-sql`)

**变更：**
- 现在会将查询条件和生成的SQL保存到数据库
- 返回 `query_id` 而不是直接返回SQL
- 增强了DeepSeek调用的安全指令

**请求：**
```json
POST /api/custom-strategy/generate-sql
{
  "description": "查询涨幅超过5%的股票"
}
```

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "query_id": 123,
    "sql": "SELECT ...",
    "missing_tables": [],
    "missing_fields": []
  }
}
```

#### 2.2 预览SQL接口 (`/api/custom-strategy/preview-sql`)

**变更：**
- 现在接收 `query_id` 而不是 `sql_query`
- 从数据库获取SQL，确保安全性
- 自动更新查询记录的执行状态和统计信息

**请求：**
```json
POST /api/custom-strategy/preview-sql
{
  "query_id": 123
}
```

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "columns": ["ts_code", "name", ...],
    "rows": [...],
    "row_count": 100,
    "latest_date": "20241118",
    "has_more": false
  }
}
```

### 3. DeepSeek调用安全增强

#### 3.1 系统提示词增强

在DeepSeek的系统提示词中增加了严格的安全要求：

```
【重要安全要求 - 必须严格遵守】：
1. 只能生成SELECT查询语句，禁止生成任何修改数据的语句
2. 禁止在SQL中包含注释符号（--、/*、*/）
3. 禁止生成多语句查询
4. 只能访问允许的数据表
5. 禁止访问系统表
6. 禁止使用危险函数
7. 生成的SQL必须符合SQL注入防护规范
8. 如果用户需求存在安全风险，必须拒绝并说明原因
```

#### 3.2 用户提示词增强

在用户提示词中也增加了详细的安全要求说明。

### 4. SQL安全检查

生成的SQL会经过 `sql_security.py` 模块的严格检查：
- SQL注入防护
- 越权访问防护
- 危险操作防护
- 复杂度限制

### 5. 前端API更新

**变更：**
```javascript
// 旧版本
previewSQL: (sqlQuery) => api.post('/custom-strategy/preview-sql', { sql_query: sqlQuery })

// 新版本
previewSQL: (queryId) => api.post('/custom-strategy/preview-sql', { query_id: queryId })
```

## 安全优势

### 1. 防止SQL注入
- 客户端不再直接传递SQL，而是传递ID
- 服务端从数据库获取SQL，确保SQL来源可信
- 所有SQL都经过严格的安全检查

### 2. 审计追踪
- 所有查询条件和SQL都保存在数据库中
- 可以追踪每次查询的执行情况
- 记录执行次数、成功/失败状态

### 3. 权限控制
- 可以基于 `user_id` 进行权限控制
- 可以限制用户只能访问自己的查询记录

## 使用流程

1. **生成SQL**
   ```
   客户端 -> POST /api/custom-strategy/generate-sql
   服务端 -> 调用DeepSeek生成SQL -> 保存到数据库 -> 返回query_id
   ```

2. **预览SQL结果**
   ```
   客户端 -> POST /api/custom-strategy/preview-sql (query_id)
   服务端 -> 从数据库获取SQL -> 安全检查 -> 执行查询 -> 更新状态 -> 返回结果
   ```

## 数据库迁移

执行以下SQL创建新表：

```bash
mysql -u root -p stock_data < add_custom_query_table.sql
```

或者使用Python脚本：

```python
from database import init_database
init_database()  # 会自动创建CustomQuery表
```

## 注意事项

1. **向后兼容**：旧的API接口仍然支持，但建议使用新的基于ID的方式
2. **数据清理**：建议定期清理旧的查询记录，避免数据库过大
3. **性能优化**：可以为 `custom_query` 表添加适当的索引
4. **安全审计**：定期检查查询记录，发现异常模式

## 更新文件列表

1. `database.py` - 添加CustomQuery表定义
2. `web-server/app.py` - 更新API接口
3. `web-frontend/src/api/index.js` - 更新前端API调用
4. `add_custom_query_table.sql` - 数据库迁移脚本
5. `sql_security.py` - SQL安全检查模块（已存在）

## 测试建议

1. 测试生成SQL并获取query_id
2. 测试使用query_id预览SQL结果
3. 测试SQL安全检查是否正常工作
4. 测试DeepSeek生成的安全SQL
5. 测试错误处理和状态更新

