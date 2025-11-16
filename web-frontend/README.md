# 前端项目

Red-Stock 前端应用，支持Web浏览器和小程序。

## 项目结构

```
frontend/
├── index.html          # 主页面
├── config.js          # 配置文件
├── static/            # 静态资源目录
└── src/               # 源代码目录（未来可扩展）
```

## 配置说明

### API地址配置

编辑 `config.js` 文件，修改API基础地址：

```javascript
const CONFIG = {
    API_BASE: 'http://localhost:5000/api',  // 修改为你的后端API地址
    // ... 其他配置
};
```

### 环境变量配置（可选）

如果使用构建工具，可以通过环境变量配置：

```bash
# 开发环境
API_BASE=http://localhost:5000/api npm start

# 生产环境
API_BASE=https://api.example.com/api npm build
```

## 使用方法

### 方式1：直接打开HTML文件

1. 修改 `config.js` 中的 `API_BASE` 为后端地址
2. 使用浏览器直接打开 `index.html`

**注意**：由于浏览器安全限制，直接打开文件可能无法访问API，建议使用HTTP服务器。

### 方式2：使用HTTP服务器（推荐）

#### Python HTTP服务器

```bash
cd frontend
python3 -m http.server 8080
```

访问：http://localhost:8080

#### Node.js HTTP服务器

```bash
# 安装http-server
npm install -g http-server

# 启动服务器
cd frontend
http-server -p 8080
```

访问：http://localhost:8080

#### Nginx配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API代理（可选）
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 小程序集成

### 微信小程序

1. 在微信开发者工具中创建小程序项目
2. 将前端代码复制到小程序项目目录
3. 修改 `config.js` 中的API地址为小程序后端地址
4. 在小程序的 `app.json` 中配置网络请求域名

### 小程序配置示例

```javascript
// config.js (小程序版本)
const CONFIG = {
    API_BASE: 'https://your-api-domain.com/api',
    // 小程序特有配置
    MINI_PROGRAM: true
};

// app.js
const CONFIG = require('./config.js');
wx.request({
    url: CONFIG.API_BASE + '/stocks',
    // ...
});
```

## 开发建议

### 未来扩展

1. **使用Vue/React框架**：
   - 可以逐步迁移到Vue 3或React
   - 使用Vite或Webpack进行构建
   - 支持组件化开发

2. **状态管理**：
   - Vue: 使用Pinia或Vuex
   - React: 使用Redux或Zustand

3. **UI组件库**：
   - Vue: Element Plus, Vant
   - React: Ant Design, Material-UI
   - 小程序: Vant Weapp, Taro UI

4. **API封装**：
   - 创建统一的API请求封装
   - 支持请求拦截和响应拦截
   - 统一错误处理

## 跨域配置

如果前端和后端不在同一域名，需要确保后端已配置CORS。

后端已默认配置允许所有来源，生产环境建议修改为具体域名：

```python
# web/app.py
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your-frontend-domain.com"],  # 指定前端域名
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

## 部署

### 静态文件部署

前端可以部署到任何静态文件服务器：

- GitHub Pages
- Netlify
- Vercel
- 阿里云OSS
- 腾讯云COS
- 自建Nginx服务器

### 构建优化

1. **压缩资源**：
   - 压缩HTML/CSS/JS
   - 图片优化
   - 使用CDN加速

2. **代码分割**：
   - 按路由分割
   - 按组件分割
   - 懒加载

3. **缓存策略**：
   - 静态资源长期缓存
   - API数据合理缓存
   - Service Worker支持

## 注意事项

1. **API地址配置**：确保 `config.js` 中的API地址正确
2. **跨域问题**：确保后端已配置CORS
3. **HTTPS**：生产环境建议使用HTTPS
4. **小程序限制**：小程序需要配置合法域名



