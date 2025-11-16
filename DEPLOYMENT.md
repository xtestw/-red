# 部署指南

## 前后端分离部署

### 后端部署

#### 方式1：直接运行（开发环境）

```bash
python web/app.py
```

#### 方式2：使用Gunicorn（生产环境）

```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:5000 web.app:app
```

#### 方式3：使用Docker

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "web.app:app"]
```

```bash
# 构建镜像
docker build -t stock-api .

# 运行容器
docker run -d -p 5000:5000 --name stock-api stock-api
```

#### 方式4：使用Nginx反向代理

```nginx
# /etc/nginx/sites-available/stock-api
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 前端部署

#### 方式1：静态文件服务器

将 `frontend` 目录部署到任何静态文件服务器：

```bash
# 复制文件到服务器
scp -r frontend/* user@server:/var/www/html/
```

#### 方式2：Nginx部署

```nginx
# /etc/nginx/sites-available/stock-frontend
server {
    listen 80;
    server_name www.example.com;
    root /var/www/stock-frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API代理（可选，也可以直接配置CORS）
    location /api {
        proxy_pass http://api.example.com;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 方式3：使用CDN

- 上传到阿里云OSS/腾讯云COS
- 配置CDN加速
- 设置缓存策略

#### 方式4：使用GitHub Pages/Vercel/Netlify

1. 将前端代码推送到Git仓库
2. 在GitHub Pages/Vercel/Netlify中配置项目
3. 设置构建命令和输出目录
4. 配置环境变量（API地址）

### 小程序部署

1. 在微信开发者工具中打开小程序项目
2. 修改API地址配置
3. 在微信公众平台配置服务器域名
4. 上传代码并提交审核

## 环境配置

### 后端环境变量

通过 `config.json` 配置：

```json
{
  "tushare": {
    "token": "your_token"
  },
  "mysql": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "stock_data"
  },
  "flask": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false
  }
}
```

### 前端环境配置

修改 `frontend/config.js`：

```javascript
const CONFIG = {
    API_BASE: 'https://api.example.com/api',  // 生产环境API地址
    // ...
};
```

## 安全建议

1. **HTTPS**：生产环境必须使用HTTPS
2. **CORS配置**：限制允许的域名
3. **API限流**：防止API被滥用
4. **数据验证**：后端验证所有输入数据
5. **敏感信息**：不要在前端代码中暴露敏感信息

## 性能优化

### 后端优化

1. 使用Gunicorn多进程
2. 配置数据库连接池
3. 使用Redis缓存
4. 启用Gzip压缩

### 前端优化

1. 压缩静态资源
2. 使用CDN加速
3. 启用浏览器缓存
4. 代码分割和懒加载

## 监控和日志

### 后端日志

```python
# 使用Python logging
import logging
logging.basicConfig(level=logging.INFO)
```

### 前端监控

- 使用Sentry监控错误
- 使用Google Analytics统计访问
- 监控API响应时间

## 备份和恢复

### 数据库备份

```bash
# 备份
mysqldump -u root -p stock_data > backup.sql

# 恢复
mysql -u root -p stock_data < backup.sql
```

### 配置文件备份

定期备份 `config.json` 和数据库配置。



