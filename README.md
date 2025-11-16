# Red-Stock

基于Tushare的股票数据获取、存储和展示系统。

## 功能特性

### 核心功能
- 📊 **数据获取**：通过Tushare API获取全市场股票数据
- 💾 **数据存储**：MySQL数据库存储股票基本信息、K线数据、资金流向等
- ⏰ **定时任务**：自动定时更新股票数据
- 🔍 **股票筛选**：支持按行业、市值、市盈率等条件筛选股票
- 📈 **K线图表**：支持日线、周线、月线K线图展示
- 💰 **资金流向**：展示股票资金流入流出情况

### 新增功能
- 📉 **技术指标**：自动计算MA、MACD、RSI、KDJ、布林带、OBV、ATR等技术指标
- 🎯 **技术信号**：自动识别金叉、死叉、超买、超卖等技术信号
- ⚖️ **股票对比**：支持同时对比多只股票（最多10只）
- 📥 **数据导出**：支持导出CSV和Excel格式的股票数据
- ⭐ **股票收藏**：收藏关注的股票，方便快速查看
- 📊 **行业统计**：按行业统计股票数量、平均市值、PE等指标

## 项目结构

```
red/
├── config.py              # 配置文件
├── database.py            # 数据库模型和连接
├── requirements.txt       # Python依赖包
├── init_database.py       # 数据库初始化脚本
├── start_web.sh           # Web服务启动脚本
├── start_scheduler.sh     # 定时任务启动脚本
├── server/                # 后端服务目录
│   ├── data_fetcher.py    # 数据获取模块
│   └── scheduler.py       # 定时任务调度器
├── web/                   # 后端API服务
│   └── app.py             # Flask后端API（仅提供API接口）
└── frontend/              # 前端项目（前后端分离）
    ├── index.html         # 主页面
    ├── config.js          # 前端配置
    ├── api.js             # API封装（支持小程序）
    └── README.md          # 前端说明文档
```

## 环境要求

- Python 3.7+
- MySQL 5.7+
- Tushare账号和Token

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 配置MySQL数据库

#### 方式1：使用SQL脚本（推荐）

直接执行SQL脚本创建数据库和表：

```bash
mysql -u root -p < database.sql
```

或者登录MySQL后执行：

```sql
source database.sql;
```

#### 方式2：手动创建

创建MySQL数据库：

```sql
CREATE DATABASE stock_data CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

然后使用Python脚本初始化表结构：

```bash
python init_database.py
```

### 3. 配置文件

复制配置文件模板并修改配置：

```bash
cp config.json.example config.json
```

编辑 `config.json` 文件，修改以下配置：

```json
{
  "tushare": {
    "token": "your_tushare_token_here"
  },
  "mysql": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "your_password",
    "database": "stock_data",
    "charset": "utf8mb4"
  },
  "flask": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false
  }
}
```

**注意**：`config.json` 文件包含敏感信息，请勿提交到版本控制系统。

### 4. 首次获取数据（可选）

如果需要立即获取所有数据，可以运行：

```bash
python server/data_fetcher.py
```

**注意**：首次获取全市场数据可能需要较长时间，建议在非交易时间运行。

## 使用方法

### 启动后端API服务

```bash
# 方式1：使用启动脚本
chmod +x start_web.sh
./start_web.sh

# 方式2：直接运行
python web/app.py
```

后端API服务将在 `http://localhost:5000` 启动。

**注意**：后端现在只提供API接口，不再提供前端页面。

### 启动服务（单端口部署）

#### 方式1：生产模式（推荐）

1. **构建前端**：
```bash
cd frontend
npm install
npm run build
```

2. **启动后端服务**（会自动服务前端文件）：
```bash
# 方式1：直接运行
python web/app.py

# 方式2：使用启动脚本
chmod +x start_web.sh
./start_web.sh
```

3. **访问**：http://localhost:5000

前端页面和API接口都在同一个端口（5000）。

#### 方式2：开发模式（前后端分离）

**终端1 - 启动后端：**
```bash
python web/app.py
```

**终端2 - 启动前端开发服务器：**
```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:3000（前端开发服务器，API代理到5000端口）

### 启动定时任务

```bash
# 方式1：使用启动脚本
chmod +x start_scheduler.sh
./start_scheduler.sh

# 方式2：直接运行
python server/scheduler.py
```

定时任务配置：
- **每日15:30**：更新股票基本信息、日线数据、资金流向、指标数据
- **每周日20:00**：更新周线数据
- **每月1日20:00**：更新月线数据

## API接口说明

### 1. 获取股票列表（支持筛选）

```
GET /api/stocks
```

查询参数：
- `keyword`: 关键词搜索（股票代码或名称）
- `industry`: 行业筛选
- `market`: 市场筛选
- `min_market_value`: 最小市值（万元）
- `max_market_value`: 最大市值（万元）
- `min_pe`: 最小市盈率
- `max_pe`: 最大市盈率
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认50）

### 2. 获取股票详情

```
GET /api/stocks/<ts_code>
```

### 3. 获取日线数据

```
GET /api/stocks/<ts_code>/daily?start_date=20240101&end_date=20241231&limit=100
```

### 4. 获取周线数据

```
GET /api/stocks/<ts_code>/weekly?start_date=20240101&end_date=20241231&limit=100
```

### 5. 获取月线数据

```
GET /api/stocks/<ts_code>/monthly?start_date=20240101&end_date=20241231&limit=100
```

### 6. 获取资金流向数据

```
GET /api/stocks/<ts_code>/moneyflow?start_date=20240101&end_date=20241231&limit=30
```

### 7. 获取技术指标数据

```
GET /api/stocks/<ts_code>/indicators?period=daily&limit=100
```

返回包含MA、MACD、RSI、KDJ、布林带等技术指标数据和技术信号。

### 8. 股票对比

```
POST /api/stocks/compare
Content-Type: application/json

{
  "ts_codes": ["000001.SZ", "600000.SH"]
}
```

### 9. 导出股票数据

```
GET /api/stocks/<ts_code>/export?period=daily&format=csv
GET /api/stocks/<ts_code>/export?period=daily&format=excel
```

### 10. 股票收藏

```
# 获取收藏列表
GET /api/favorites?user_id=default

# 添加收藏
POST /api/favorites
Content-Type: application/json
{
  "ts_code": "000001.SZ",
  "user_id": "default",
  "notes": "备注"
}

# 取消收藏
DELETE /api/favorites/<ts_code>?user_id=default
```

### 11. 行业统计

```
GET /api/industries/statistics
```

### 12. 获取行业列表

```
GET /api/industries
```

### 13. 获取市场列表

```
GET /api/markets
```

## 数据库表结构

### stock_basic
股票基本信息表

### stock_daily
股票日线数据表

### stock_weekly
股票周线数据表

### stock_monthly
股票月线数据表

### stock_moneyflow
股票资金流向表

### stock_indicator
股票指标表（市值、市盈率等）

### stock_favorite
股票收藏表

## 注意事项

1. **Tushare API限制**：
   - 免费版有请求频率限制，代码中已加入延时处理
   - 建议在非交易时间进行大批量数据获取

2. **数据库性能**：
   - 建议为常用查询字段添加索引
   - 定期清理历史数据以保持数据库性能

3. **定时任务**：
   - 定时任务需要在后台持续运行
   - 建议使用 `nohup` 或 `systemd` 管理定时任务进程

4. **数据更新**：
   - 首次运行建议手动执行数据获取
   - 定时任务会在交易日收盘后自动更新数据

## 技术指标说明

系统支持以下技术指标：

- **MA（移动平均线）**：MA5、MA10、MA20、MA30、MA60
- **MACD（指数平滑异同移动平均线）**：MACD线、信号线、柱状图
- **RSI（相对强弱指标）**：14日RSI
- **KDJ（随机指标）**：K值、D值、J值
- **布林带（Bollinger Bands）**：上轨、中轨、下轨
- **OBV（能量潮）**：成交量指标
- **ATR（平均真实波幅）**：波动性指标

## 小程序支持

系统已支持小程序开发，提供了完整的API封装：

### 微信小程序

1. 将 `frontend/miniprogram-example.js` 复制到小程序项目
2. 修改API地址配置
3. 在小程序管理后台配置合法域名
4. 使用提供的API方法进行开发

### 小程序配置

在小程序的 `app.json` 中配置网络请求域名：

```json
{
  "networkTimeout": {
    "request": 10000
  }
}
```

在微信公众平台配置服务器域名：
- request合法域名：`https://your-api-domain.com`

## 前后端分离说明

系统采用前后端分离架构：

- **后端**：只提供RESTful API接口，不包含前端页面
- **前端**：独立的前端项目，可以部署到任何静态服务器
- **小程序**：使用相同的API接口，提供小程序专用封装

### 优势

1. **独立部署**：前后端可以独立部署和扩展
2. **多端支持**：同一套API支持Web、小程序、移动App
3. **开发效率**：前后端可以并行开发
4. **技术选型**：前端可以选择任意框架（Vue、React等）

## 后续扩展

系统已预留扩展接口，可以方便地添加：
- 更多市场数据源
- 更多技术指标（如CCI、DMI等）
- 策略回测功能
- 股票预警功能
- 更多图表类型
- 用户系统（多用户支持）
- 移动App（React Native、Flutter等）

## 许可证

MIT License
