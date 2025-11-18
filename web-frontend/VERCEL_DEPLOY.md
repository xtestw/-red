# Vercel 部署指南

本文档说明如何将 Red-Stock 前端项目部署到 Vercel。

## 前置要求

1. 拥有 Vercel 账号（可通过 GitHub 账号登录）
2. 项目已推送到 Git 仓库（GitHub、GitLab 或 Bitbucket）
3. 后端 API 已部署并可访问

## 部署步骤

### 方法一：通过 Vercel Dashboard（推荐）

1. **登录 Vercel**
   - 访问 [vercel.com](https://vercel.com)
   - 使用 GitHub/GitLab/Bitbucket 账号登录

2. **导入项目**
   - 点击 "Add New Project"
   - 选择你的 Git 仓库
   - 选择 `web-frontend` 目录作为根目录

3. **配置项目**
   - **Framework Preset**: 选择 `Vite`（Vercel 会自动检测）
   - **Root Directory**: `web-frontend`
   - **Build Command**: `npm run build`（默认）
   - **Output Directory**: `dist`（默认）
   - **Install Command**: `npm install`（默认）

4. **配置环境变量**
   在 "Environment Variables" 中添加：
   ```
   VITE_API_BASE = https://stockapi.xtestw.com/api
   ```
   这是后端API的完整地址。

5. **部署**
   - 点击 "Deploy"
   - 等待构建完成

### 方法二：通过 Vercel CLI

1. **安装 Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **登录 Vercel**
   ```bash
   vercel login
   ```

3. **进入项目目录**
   ```bash
   cd web-frontend
   ```

4. **部署**
   ```bash
   vercel
   ```
   首次部署会提示配置，按提示操作即可。

5. **配置环境变量**
   ```bash
   vercel env add VITE_API_BASE
   ```
   输入后端 API 地址：`https://stockapi.xtestw.com/api`

6. **生产环境部署**
   ```bash
   vercel --prod
   ```

## 配置文件说明

### vercel.json

项目已包含 `vercel.json` 配置文件，包含以下配置：

- **rewrites**: 将所有路由重写到 `index.html`，支持 Vue Router 的 history 模式
- **headers**: 配置静态资源缓存策略
- **framework**: 指定为 Vite

### 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `VITE_API_BASE` | 后端 API 基础地址 | `https://stockapi.xtestw.com/api` |

## 后端 API 配置

### 选项 1：后端独立部署（推荐）

后端已部署在 `stockapi.xtestw.com`：

1. 在 Vercel 环境变量中设置 `VITE_API_BASE = https://stockapi.xtestw.com/api`
2. 确保后端已配置 CORS，允许 Vercel 域名访问

### 选项 2：使用 Vercel Rewrites 代理（不推荐）

如果需要通过 Vercel 代理 API 请求，可以修改 `vercel.json`：

```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://stockapi.xtestw.com/api/$1"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

然后设置 `VITE_API_BASE=/api`。

**注意**：推荐直接使用选项1，直接指向后端API地址。

## 自定义域名

1. 在 Vercel 项目设置中，进入 "Domains"
2. 添加你的域名（如 `red-stock.online`）
3. 按照提示配置 DNS 记录
4. 等待 DNS 生效（通常几分钟到几小时）

## 持续部署

Vercel 会自动监听 Git 仓库的推送：

- **主分支推送** → 自动部署到生产环境
- **其他分支推送** → 创建预览部署
- **Pull Request** → 创建预览部署

## 环境变量管理

### 开发环境变量
```bash
vercel env add VITE_API_BASE development
```

### 预览环境变量
```bash
vercel env add VITE_API_BASE preview
```

### 生产环境变量
```bash
vercel env add VITE_API_BASE production
```

## 常见问题

### 1. 路由 404 错误

确保 `vercel.json` 中的 `rewrites` 配置正确，所有路由都应重写到 `index.html`。

### 2. API 请求失败

- 检查 `VITE_API_BASE` 环境变量是否正确设置为 `https://stockapi.xtestw.com/api`
- 检查后端 CORS 配置是否允许 Vercel 域名
- 检查后端服务 `stockapi.xtestw.com` 是否正常运行
- 在浏览器开发者工具的Network标签中查看API请求的完整URL

### 3. 构建失败

- 检查 Node.js 版本（Vercel 默认使用 Node.js 18）
- 检查 `package.json` 中的依赖是否正确
- 查看构建日志中的错误信息

### 4. 静态资源加载失败

- 检查 `vite.config.js` 中的 `base` 配置
- 确保 `public` 目录中的文件正确复制

## 性能优化

### 1. 启用 Edge Functions（可选）

对于需要边缘计算的场景，可以使用 Vercel Edge Functions。

### 2. 图片优化

使用 Vercel 的图片优化功能，在 `vercel.json` 中添加：

```json
{
  "images": {
    "domains": ["your-image-domain.com"]
  }
}
```

### 3. 缓存策略

`vercel.json` 中已配置静态资源缓存策略，生产环境会自动应用。

## 监控和分析

1. **Vercel Analytics**: 在项目设置中启用
2. **Web Vitals**: 自动监控页面性能
3. **错误追踪**: 集成 Sentry 等错误追踪服务

## 回滚部署

如果新部署有问题，可以在 Vercel Dashboard 中：

1. 进入 "Deployments"
2. 找到之前的稳定版本
3. 点击 "..." → "Promote to Production"

## 参考链接

- [Vercel 文档](https://vercel.com/docs)
- [Vite 部署指南](https://vitejs.dev/guide/static-deploy.html#vercel)
- [Vue Router 部署](https://router.vuejs.org/guide/essentials/history-mode.html)

