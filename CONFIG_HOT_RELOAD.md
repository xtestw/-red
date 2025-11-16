# 配置热重载说明

## 功能说明

系统支持配置文件的**热重载**功能，修改 `config.json` 后无需重启服务即可生效。

## 工作原理

1. **自动检测**：系统通过检查配置文件的修改时间（mtime）来判断是否需要重新加载
2. **线程安全**：使用锁机制确保并发访问时的安全性
3. **按需加载**：每次访问配置时自动检查文件是否被修改

## 支持的配置项

以下配置支持热重载：

- ✅ **Tushare Token** - 修改后立即生效（下次API调用时使用新token）
- ✅ **MySQL配置** - 修改后立即生效（下次数据库连接时使用新配置）
- ✅ **Flask配置** - 部分支持（host/port需要重启，debug可以热重载）

## 使用方法

### 方式1：自动重载（推荐）

直接修改 `config.json` 文件，系统会在下次访问配置时自动检测并重新加载。

**示例**：
```json
{
  "tushare": {
    "token": "new_token_here"  // 修改后，下次API调用会自动使用新token
  },
  "mysql": {
    "password": "new_password"  // 修改后，下次数据库连接会自动使用新密码
  }
}
```

### 方式2：手动触发重载

通过API接口手动触发配置重载：

```bash
curl -X POST http://localhost:5000/api/config/reload
```

**响应示例**：
```json
{
  "code": 0,
  "message": "配置已重新加载",
  "data": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false
  }
}
```

## 注意事项

1. **Flask配置限制**：
   - `host` 和 `port` 修改后需要重启Web服务才能生效
   - `debug` 模式可以热重载，但建议重启服务以确保完全生效

2. **数据库连接**：
   - 修改MySQL配置后，新的数据库连接会使用新配置
   - 已建立的连接池中的连接不会立即更新，会在连接回收后使用新配置

3. **Tushare API**：
   - Token修改后，下次调用API时会自动使用新token
   - 如果当前有正在进行的API调用，会继续使用旧的token

4. **配置文件格式**：
   - 确保JSON格式正确，否则重载会失败
   - 建议使用文本编辑器修改，避免格式错误

## 日志输出

配置重载时会在控制台输出日志：

```
[配置] 配置文件已重新加载: 2024-01-01 12:00:00
```

如果重载失败，会输出错误信息：

```
[配置] 重新加载配置失败: [错误信息]
```

## 开发建议

在代码中使用配置时，建议使用函数方式获取配置值，而不是直接使用模块级变量：

**推荐方式**：
```python
from config import get_tushare_token, get_mysql_config

# 获取最新配置
token = get_tushare_token()
mysql_config = get_mysql_config()
```

**不推荐方式**：
```python
from config import TUSHARE_TOKEN, MYSQL_CONFIG

# 这种方式获取的是模块加载时的值，不会自动更新
token = TUSHARE_TOKEN
```

## 测试热重载

1. 启动服务：
```bash
python web-server/app.py
```

2. 修改 `config.json` 中的某个配置项

3. 触发一次API请求或调用重载接口

4. 检查日志，确认配置已重新加载

5. 验证新配置是否生效



