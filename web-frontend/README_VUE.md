# Vue 3 + Ant Design Vue 前端项目

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API封装
│   │   └── index.js
│   ├── components/        # Vue组件
│   │   ├── Layout.vue              # 布局组件（导航菜单）
│   │   ├── StockDetailModal.vue    # 股票详情模态框
│   │   ├── StockCompareModal.vue   # 股票对比模态框
│   │   ├── IndustryStatsModal.vue  # 行业统计模态框
│   │   ├── KlineChart.vue          # K线图表
│   │   ├── MoneyflowChart.vue      # 资金流向图表
│   │   └── TechnicalIndicators.vue # 技术指标
│   ├── stores/           # Pinia状态管理
│   │   └── stock.js
│   ├── router/           # 路由配置
│   │   └── index.js
│   ├── views/            # 页面组件
│   │   ├── Dashboard.vue          # 首页（网站介绍+大盘情况）
│   │   ├── StockList.vue           # A股股票信息
│   │   ├── GlobalMarket.vue        # 外盘跟踪
│   │   └── BigPlayerTracking.vue   # 知名大佬追踪
│   ├── App.vue           # 根组件
│   ├── main.js           # 入口文件
│   └── style.css         # 全局样式
├── index.html            # HTML模板
├── vite.config.js        # Vite配置
├── package.json          # 依赖配置
└── .env.development      # 开发环境配置
```

## 页面说明

### 1. 首页（Dashboard）
- 网站介绍和功能展示
- 今日大盘情况（上证指数、深证成指、创业板指）
- 市场统计（上涨/下跌/平盘家数、总成交额）
- 热门板块

### 2. A股股票信息（StockList）
- 股票筛选（关键词、行业、市场、市值、市盈率）
- 股票列表展示
- 股票详情（K线图、资金流向、技术指标）
- 股票对比
- 收藏功能

### 3. 外盘跟踪（GlobalMarket）
- 主要市场指数（美股、港股、A50等）
- 热门外盘股票（美股、港股）
- 外汇市场数据

### 4. 知名大佬追踪（BigPlayerTracking）
- 大佬列表
- 持仓详情
- 最新动态

## 安装依赖

```bash
cd frontend
npm install
```

## 开发

```bash
npm run dev
```

访问：http://localhost:3000

## 构建

```bash
npm run build
```

构建产物在 `dist/` 目录。

## 环境变量

### 开发环境 (.env.development)

```env
VITE_API_BASE=http://localhost:5000/api
```

### 生产环境 (.env.production)

```env
VITE_API_BASE=/api
```

## 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **Ant Design Vue 4** - 企业级UI组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **ECharts** - 图表库
- **Axios** - HTTP客户端
- **Vite** - 构建工具

## API接口

### 大盘相关
- `GET /api/market/overview` - 获取大盘概览
- `GET /api/market/hot-sectors` - 获取热门板块

### 外盘市场
- `GET /api/global/indices` - 获取市场指数
- `GET /api/global/stocks/{market}` - 获取股票列表（market: us/hk）
- `GET /api/global/forex` - 获取外汇数据

### 知名大佬
- `GET /api/bigplayers` - 获取大佬列表
- `GET /api/bigplayers/{id}/holdings` - 获取持仓详情
- `GET /api/bigplayers/activities` - 获取最新动态

## 部署

### 开发环境

```bash
npm run dev
```

### 生产环境

```bash
npm run build
# 将 dist/ 目录部署到静态服务器
```

### Vercel 部署（推荐）

项目已配置支持 Vercel 部署，详细说明请参考 [VERCEL_DEPLOY.md](./VERCEL_DEPLOY.md)

快速部署步骤：

1. **通过 Vercel Dashboard**
   - 访问 [vercel.com](https://vercel.com) 并登录
   - 导入 Git 仓库，选择 `web-frontend` 目录
   - 配置环境变量 `VITE_API_BASE = https://stockapi.xtestw.com/api`
   - 点击部署

2. **通过 Vercel CLI**
   ```bash
   npm install -g vercel
   cd web-frontend
   vercel login
   vercel env add VITE_API_BASE
   # 输入: https://stockapi.xtestw.com/api
   vercel --prod
   ```

### Nginx配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
