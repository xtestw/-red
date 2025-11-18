# SEO配置说明

本文档说明如何配置Red-Stock项目的SEO优化功能。

## 配置文件

SEO相关配置位于 `config.json` 文件中的 `seo` 部分：

```json
{
  "seo": {
    "site_url": "https://your-domain.com",
    "site_name": "Red-Stock",
    "site_description": "专业的A股数据分析平台，提供实时股票行情、技术指标分析、资金流向追踪、智能策略选股等功能"
  }
}
```

## 配置项说明

### site_url
- **类型**: 字符串
- **说明**: 网站的完整URL（包含协议，如 https://）
- **示例**: `"https://www.example.com"`
- **注意**: 请将 `your-domain.com` 替换为你的实际域名

### site_name
- **类型**: 字符串
- **说明**: 网站名称，用于Open Graph和Twitter Card
- **默认值**: `"Red-Stock"`

### site_description
- **类型**: 字符串
- **说明**: 网站描述，用于meta description、Open Graph和Twitter Card
- **建议**: 控制在150-160个字符以内，包含主要关键词

## SEO功能

### 1. Meta标签优化

在 `web-frontend/index.html` 中已添加以下SEO meta标签：

- **基础SEO标签**: title, description, keywords, robots, language
- **Open Graph标签**: 用于Facebook等社交平台分享
- **Twitter Card标签**: 用于Twitter分享
- **Canonical URL**: 防止重复内容

### 2. Sitemap.xml

- **路径**: `/sitemap.xml`
- **功能**: 自动生成包含所有主要页面的sitemap
- **更新频率**: 每天自动更新lastmod日期
- **包含页面**:
  - 首页 (/)
  - 股票列表 (/stocks)
  - IPO新股 (/ipo)
  - 策略选股 (/strategy/selection)
  - 外盘跟踪 (/global)
  - 大佬追踪 (/bigplayers)

### 3. Robots.txt

- **路径**: `/robots.txt`
- **功能**: 指导搜索引擎爬虫
- **配置**: 
  - 允许所有爬虫访问
  - 禁止访问 `/api/` 和 `/admin/` 路径
  - 指向sitemap.xml位置

### 4. Favicon支持

- **路径**: `/favicon.ico`
- **说明**: 如果 `web-frontend/dist/favicon.ico` 存在，会自动提供服务

## 部署前检查清单

1. ✅ 更新 `config.json` 中的 `site_url` 为实际域名
2. ✅ 更新 `web-frontend/index.html` 中的 Open Graph 和 Twitter Card 图片URL
3. ✅ 准备并放置 favicon.ico 到 `web-frontend/public/` 目录
4. ✅ 准备 Open Graph 图片（建议尺寸：1200x630px）
5. ✅ 准备 Twitter Card 图片（建议尺寸：1200x675px）
6. ✅ 验证 sitemap.xml 可访问：`https://your-domain.com/sitemap.xml`
7. ✅ 验证 robots.txt 可访问：`https://your-domain.com/robots.txt`

## 验证SEO配置

### 检查Sitemap
```bash
curl https://your-domain.com/sitemap.xml
```

### 检查Robots.txt
```bash
curl https://your-domain.com/robots.txt
```

### 使用Google Search Console
1. 访问 [Google Search Console](https://search.google.com/search-console)
2. 添加网站属性
3. 提交sitemap: `https://your-domain.com/sitemap.xml`

### 使用Bing Webmaster Tools
1. 访问 [Bing Webmaster Tools](https://www.bing.com/webmasters)
2. 添加网站
3. 提交sitemap: `https://your-domain.com/sitemap.xml`

## 进一步优化建议

1. **结构化数据**: 考虑添加JSON-LD结构化数据（Schema.org）
2. **页面级SEO**: 为每个页面添加独特的title和description（需要前端路由支持）
3. **图片优化**: 为所有图片添加alt属性
4. **性能优化**: 确保页面加载速度快（影响SEO排名）
5. **移动端优化**: 确保网站在移动设备上表现良好
6. **HTTPS**: 确保网站使用HTTPS协议
7. **内容质量**: 定期更新高质量内容

## 注意事项

- 修改 `config.json` 后，后端会自动重新加载配置（支持热重载）
- Sitemap中的日期会自动更新为当前日期
- 如果域名配置为默认值 `https://your-domain.com`，sitemap会尝试使用请求的host

