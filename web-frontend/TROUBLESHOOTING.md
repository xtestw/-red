# 故障排查指南

## 空白页问题

如果访问 http://localhost:3001 显示空白页，请按以下步骤排查：

### 1. 检查浏览器控制台

打开浏览器开发者工具（F12），查看 Console 标签页是否有错误信息。

常见错误：
- `Failed to resolve import` - 依赖未安装或路径错误
- `Cannot read property` - 组件初始化错误
- `Network Error` - API请求失败

### 2. 检查依赖是否安装

```bash
cd frontend
npm install
```

### 3. 检查后端服务是否运行

前端需要后端API服务，确保后端已启动：

```bash
python web/app.py
```

后端应该在 http://localhost:5000 运行。

### 4. 检查端口是否被占用

```bash
# macOS/Linux
lsof -i :3001

# 如果端口被占用，修改 vite.config.js 中的 port
```

### 5. 清除缓存重新启动

```bash
cd frontend
rm -rf node_modules
rm -rf dist
npm install
npm run dev
```

### 6. 检查文件结构

确保以下文件存在：
- `frontend/index.html`
- `frontend/src/main.js`
- `frontend/src/App.vue`
- `frontend/src/router/index.js`
- `frontend/src/components/Layout.vue`
- `frontend/src/views/Dashboard.vue`

### 7. 检查Vite配置

确保 `vite.config.js` 配置正确：

```javascript
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3001,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  }
})
```

### 8. 查看网络请求

在浏览器开发者工具的 Network 标签页，检查：
- 是否有资源加载失败（红色）
- API请求是否正常（可能返回404，这是正常的，因为部分API还未实现）

### 9. 临时禁用错误组件

如果某个组件导致页面无法渲染，可以临时注释掉：

在 `src/views/Dashboard.vue` 中，可以临时注释掉 API 调用：

```javascript
onMounted(() => {
  // loadMarketData()  // 临时注释
  // loadHotSectors()  // 临时注释
})
```

### 10. 检查Ant Design Vue版本

确保使用正确的版本：

```bash
npm list ant-design-vue
```

应该是 4.x 版本。

## 常见问题

### 问题：页面显示但API调用失败

**原因**：后端API未实现

**解决**：这是正常的，前端会显示加载状态。需要实现后端API接口。

### 问题：路由跳转404

**原因**：Vue Router配置问题

**解决**：检查 `src/router/index.js` 中的路由配置。

### 问题：样式不显示

**原因**：CSS未正确加载

**解决**：检查 `src/style.css` 和 Ant Design Vue 的样式导入。

## 获取帮助

如果以上方法都无法解决问题，请提供：
1. 浏览器控制台的完整错误信息
2. Network标签页的请求详情
3. 终端中 `npm run dev` 的输出信息



