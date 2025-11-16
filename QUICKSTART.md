# 快速开始指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

## 2. 配置数据库

### 方式1：使用SQL脚本（推荐）

直接执行SQL脚本创建数据库和表：

```bash
mysql -u root -p < database.sql
```

### 方式2：手动创建

确保MySQL已安装并运行，然后创建数据库：

```sql
CREATE DATABASE stock_data CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 3. 配置文件

复制配置文件模板并修改：

```bash
cp config.json.example config.json
```

编辑 `config.json` 文件，修改以下配置：

- `tushare.token`: 你的Tushare Token
- `mysql.host`: MySQL主机地址
- `mysql.port`: MySQL端口
- `mysql.user`: MySQL用户名
- `mysql.password`: MySQL密码
- `mysql.database`: 数据库名称

## 4. 初始化数据库（如果使用方式2）

```bash
python init_database.py
```

这将创建所有必需的数据表。

**注意**：如果使用方式1（SQL脚本），可以跳过此步骤。

## 5. 首次获取数据（可选）

如果需要立即获取数据，运行：

```bash
python data/data_fetcher/data_fetcher.py
```

**注意**：首次获取全市场数据需要较长时间，建议在非交易时间运行。

## 6. 启动服务

### 启动Web服务（终端1）

```bash
python web-server/app.py
```

或使用脚本：

```bash
./start_web.sh
```

访问 `http://localhost:5000` 查看Web界面。

### 启动定时任务（终端2）

```bash
python data/data_fetcher/scheduler.py
```

或使用脚本：

```bash
./start_scheduler.sh
```

定时任务将在后台运行，自动更新数据。

## 使用说明

1. **Web界面**：
   - 打开浏览器访问 `http://localhost:5000`
   - 使用筛选条件搜索股票
   - 点击"查看详情"查看股票的K线图和资金流向

2. **API接口**：
   - 所有API接口以 `/api/` 开头
   - 支持RESTful风格的数据查询
   - 详细API文档见 README.md

## 常见问题

### 1. 数据库连接失败

检查：
- MySQL服务是否运行
- 数据库配置是否正确
- 数据库是否已创建

### 2. Tushare API调用失败

检查：
- Token是否有效
- 是否超过API调用频率限制
- 网络连接是否正常

### 3. 定时任务不执行

检查：
- 定时任务进程是否在运行
- 系统时间是否正确
- 日志中是否有错误信息

## 下一步

- 查看 `README.md` 了解详细功能
- 根据需要修改定时任务执行时间
- 扩展更多数据源和分析功能

