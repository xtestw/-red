# Vercel 环境变量配置指南

## 必需的环境变量

在 Vercel 部署时，必须设置以下环境变量：

### VITE_API_BASE

**值**: `https://stockapi.xtestw.com/api`

**说明**: 后端API的完整地址

**配置位置**: 
- Vercel Dashboard → Project Settings → Environment Variables
- 或者通过 CLI: `vercel env add VITE_API_BASE`

**环境**: 
- ✅ Production（生产环境）
- ✅ Preview（预览环境）
- ✅ Development（开发环境，如果需要）

## 配置步骤

### 方法1: Vercel Dashboard

1. 登录 [Vercel Dashboard](https://vercel.com)
2. 选择你的项目
3. 进入 **Settings** → **Environment Variables**
4. 添加新变量：
   - **Key**: `VITE_API_BASE`
   - **Value**: `https://stockapi.xtestw.com/api`
   - **Environment**: 选择 Production, Preview, Development（根据需要）
5. 点击 **Save**
6. 重新部署项目（如果已部署）

### 方法2: Vercel CLI

```bash
# 设置生产环境变量
vercel env add VITE_API_BASE production
# 输入: https://stockapi.xtestw.com/api

# 设置预览环境变量
vercel env add VITE_API_BASE preview
# 输入: https://stockapi.xtestw.com/api

# 设置开发环境变量（可选）
vercel env add VITE_API_BASE development
# 输入: https://stockapi.xtestw.com/api
```

## 验证配置

部署后，在浏览器中：

1. 打开开发者工具（F12）
2. 进入 **Network** 标签
3. 刷新页面
4. 查看API请求，应该指向 `https://stockapi.xtestw.com/api/...`

## 常见问题

### API请求失败（CORS错误）

如果看到CORS错误，检查：
1. 后端服务 `stockapi.xtestw.com` 是否正常运行
2. 后端CORS配置是否允许Vercel域名（当前配置允许所有来源）

### API请求指向错误地址

如果API请求没有指向 `stockapi.xtestw.com`：
1. 检查环境变量 `VITE_API_BASE` 是否正确设置
2. 确认环境变量已应用到正确的环境（Production/Preview）
3. 重新部署项目

### 开发环境与生产环境不一致

- **开发环境**（本地）: 使用 `/api`，通过Vite代理到 `localhost:5001`
- **生产环境**（Vercel）: 使用 `https://stockapi.xtestw.com/api`，直接请求后端

## 相关文件

- `src/api/index.js` - API配置使用 `import.meta.env.VITE_API_BASE`
- `vite.config.js` - 开发环境代理配置
- `vercel.json` - Vercel部署配置

