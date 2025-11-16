/**
 * API请求封装
 * 支持Web浏览器和小程序环境
 */

// 检测运行环境
const isMiniProgram = typeof wx !== 'undefined';
const isBrowser = typeof window !== 'undefined';

// API基础地址
const API_BASE = (typeof CONFIG !== 'undefined' && CONFIG.API_BASE) 
    ? CONFIG.API_BASE 
    : 'http://localhost:5001/api';

/**
 * 统一请求方法
 */
function request(url, options = {}) {
    const fullUrl = url.startsWith('http') ? url : `${API_BASE}${url}`;
    
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    };

    const config = { ...defaultOptions, ...options };

    // 处理请求体
    if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
    }

    // 小程序环境
    if (isMiniProgram) {
        return new Promise((resolve, reject) => {
            wx.request({
                url: fullUrl,
                method: config.method,
                data: config.body ? JSON.parse(config.body) : {},
                header: config.headers,
                success: (res) => {
                    if (res.statusCode >= 200 && res.statusCode < 300) {
                        resolve(res.data);
                    } else {
                        reject(new Error(res.data?.message || '请求失败'));
                    }
                },
                fail: (err) => {
                    reject(err);
                }
            });
        });
    }

    // 浏览器环境
    if (isBrowser) {
        return fetch(fullUrl, config)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.message || `HTTP error! status: ${response.status}`);
                    });
                }
                return response.json();
            })
            .catch(error => {
                console.error('API请求失败:', error);
                throw error;
            });
    }

    throw new Error('不支持的运行环境');
}

/**
 * GET请求
 */
function get(url, params = {}) {
    const queryString = Object.keys(params)
        .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
        .join('&');
    
    const fullUrl = queryString ? `${url}?${queryString}` : url;
    
    return request(fullUrl, {
        method: 'GET',
    });
}

/**
 * POST请求
 */
function post(url, data = {}) {
    return request(url, {
        method: 'POST',
        body: data,
    });
}

/**
 * PUT请求
 */
function put(url, data = {}) {
    return request(url, {
        method: 'PUT',
        body: data,
    });
}

/**
 * DELETE请求
 */
function del(url) {
    return request(url, {
        method: 'DELETE',
    });
}

/**
 * 股票相关API
 */
const stockAPI = {
    // 获取股票列表
    getStocks: (params) => get('/stocks', params),
    
    // 获取股票详情
    getStockDetail: (tsCode) => get(`/stocks/${tsCode}`),
    
    // 获取日线数据
    getDaily: (tsCode, params) => get(`/stocks/${tsCode}/daily`, params),
    
    // 获取周线数据
    getWeekly: (tsCode, params) => get(`/stocks/${tsCode}/weekly`, params),
    
    // 获取月线数据
    getMonthly: (tsCode, params) => get(`/stocks/${tsCode}/monthly`, params),
    
    // 获取K线数据（统一接口，根据type参数）
    getKlineData: (tsCode, type = 'daily', params = {}) => {
        const endpoint = type === 'daily' ? 'daily' : type === 'weekly' ? 'weekly' : 'monthly';
        return get(`/stocks/${tsCode}/${endpoint}`, params);
    },
    
    // 获取资金流向
    getMoneyflow: (tsCode, params) => get(`/stocks/${tsCode}/moneyflow`, params),
    
    // 获取技术指标
    getIndicators: (tsCode, params) => get(`/stocks/${tsCode}/indicators`, params),
    
    // 股票对比
    compare: (tsCodes) => post('/stocks/compare', { ts_codes: tsCodes }),
    
    // 导出数据
    export: (tsCode, params = {}) => {
        const queryString = Object.keys(params)
            .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
            .join('&');
        const url = `${API_BASE}/stocks/${tsCode}/export${queryString ? '?' + queryString : ''}`;
        
        if (isBrowser) {
            window.open(url, '_blank');
        } else if (isMiniProgram) {
            // 小程序下载文件
            wx.downloadFile({
                url: url,
                success: (res) => {
                    wx.openDocument({
                        filePath: res.tempFilePath,
                    });
                }
            });
        }
    },
};

/**
 * 收藏相关API
 */
const favoriteAPI = {
    // 获取收藏列表
    getFavorites: (userId = 'default') => {
        return get('/favorites', { user_id: userId });
    },
    
    // 添加收藏
    addFavorite: (tsCode, userId = 'default', notes = '') => {
        return post('/favorites', { ts_code: tsCode, user_id: userId, notes });
    },
    
    // 取消收藏
    removeFavorite: (tsCode, userId = 'default') => {
        return del(`/favorites/${tsCode}?user_id=${userId}`);
    },
};

/**
 * 行业相关API
 */
const industryAPI = {
    // 获取行业列表
    getIndustries: () => get('/industries'),
    
    // 获取市场列表
    getMarkets: () => get('/markets'),
    
    // 获取行业统计
    getStatistics: () => get('/industries/statistics'),
};

/**
 * 系统相关API
 */
const systemAPI = {
    // 健康检查
    health: () => get('/health'),
    
    // 重载配置
    reloadConfig: () => post('/config/reload'),
};

// 导出API
if (typeof module !== 'undefined' && module.exports) {
    // Node.js/小程序环境
    module.exports = {
        request,
        get,
        post,
        put,
        del,
        stockAPI,
        favoriteAPI,
        industryAPI,
        systemAPI,
        API_BASE,
    };
} else {
    // 浏览器环境
    window.API = {
        request,
        get,
        post,
        put,
        del,
        stockAPI,
        favoriteAPI,
        industryAPI,
        systemAPI,
        API_BASE,
    };
}

