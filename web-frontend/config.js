// 前端配置文件
const CONFIG = {
    // API基础地址
    API_BASE: process.env.API_BASE || 'http://localhost:5000/api',
    
    // 分页配置
    PAGE_SIZE: 50,
    
    // 图表配置
    CHART_HEIGHT: 450,
    
    // 主题配置
    THEME: {
        primaryColor: '#667eea',
        successColor: '#28a745',
        dangerColor: '#dc3545',
        warningColor: '#ffc107',
        infoColor: '#17a2b8'
    }
};

// 如果是浏览器环境，使用全局变量
if (typeof window !== 'undefined') {
    window.CONFIG = CONFIG;
}

// 如果是Node.js环境（小程序等），导出配置
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}



