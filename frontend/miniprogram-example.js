/**
 * 小程序使用示例
 * 适用于微信小程序、支付宝小程序等
 */

// 引入API封装（需要根据小程序框架调整）
// const API = require('./api.js');

// 或者直接在小程序中使用
const API_BASE = 'https://your-api-domain.com/api';

/**
 * 小程序API封装示例（微信小程序）
 */
const miniProgramAPI = {
    // 获取股票列表
    getStocks: function(params) {
        return new Promise((resolve, reject) => {
            wx.request({
                url: `${API_BASE}/stocks`,
                method: 'GET',
                data: params,
                success: (res) => {
                    if (res.statusCode === 200 && res.data.code === 0) {
                        resolve(res.data.data);
                    } else {
                        reject(new Error(res.data.message || '请求失败'));
                    }
                },
                fail: reject
            });
        });
    },

    // 获取股票详情
    getStockDetail: function(tsCode) {
        return new Promise((resolve, reject) => {
            wx.request({
                url: `${API_BASE}/stocks/${tsCode}`,
                method: 'GET',
                success: (res) => {
                    if (res.statusCode === 200 && res.data.code === 0) {
                        resolve(res.data.data);
                    } else {
                        reject(new Error(res.data.message || '请求失败'));
                    }
                },
                fail: reject
            });
        });
    },

    // 获取K线数据
    getKlineData: function(tsCode, type = 'daily', params = {}) {
        return new Promise((resolve, reject) => {
            wx.request({
                url: `${API_BASE}/stocks/${tsCode}/${type}`,
                method: 'GET',
                data: params,
                success: (res) => {
                    if (res.statusCode === 200 && res.data.code === 0) {
                        resolve(res.data.data);
                    } else {
                        reject(new Error(res.data.message || '请求失败'));
                    }
                },
                fail: reject
            });
        });
    },

    // 获取技术指标
    getIndicators: function(tsCode, params = {}) {
        return new Promise((resolve, reject) => {
            wx.request({
                url: `${API_BASE}/stocks/${tsCode}/indicators`,
                method: 'GET',
                data: params,
                success: (res) => {
                    if (res.statusCode === 200 && res.data.code === 0) {
                        resolve(res.data.data);
                    } else {
                        reject(new Error(res.data.message || '请求失败'));
                    }
                },
                fail: reject
            });
        });
    },

    // 股票对比
    compareStocks: function(tsCodes) {
        return new Promise((resolve, reject) => {
            wx.request({
                url: `${API_BASE}/stocks/compare`,
                method: 'POST',
                data: { ts_codes: tsCodes },
                header: {
                    'Content-Type': 'application/json'
                },
                success: (res) => {
                    if (res.statusCode === 200 && res.data.code === 0) {
                        resolve(res.data.data);
                    } else {
                        reject(new Error(res.data.message || '请求失败'));
                    }
                },
                fail: reject
            });
        });
    },

    // 添加收藏
    addFavorite: function(tsCode, userId = 'default') {
        return new Promise((resolve, reject) => {
            wx.request({
                url: `${API_BASE}/favorites`,
                method: 'POST',
                data: {
                    ts_code: tsCode,
                    user_id: userId
                },
                header: {
                    'Content-Type': 'application/json'
                },
                success: (res) => {
                    if (res.statusCode === 200 && res.data.code === 0) {
                        resolve(res.data);
                    } else {
                        reject(new Error(res.data.message || '请求失败'));
                    }
                },
                fail: reject
            });
        });
    },

    // 获取收藏列表
    getFavorites: function(userId = 'default') {
        return new Promise((resolve, reject) => {
            wx.request({
                url: `${API_BASE}/favorites`,
                method: 'GET',
                data: { user_id: userId },
                success: (res) => {
                    if (res.statusCode === 200 && res.data.code === 0) {
                        resolve(res.data.data);
                    } else {
                        reject(new Error(res.data.message || '请求失败'));
                    }
                },
                fail: reject
            });
        });
    },

    // 获取行业统计
    getIndustryStats: function() {
        return new Promise((resolve, reject) => {
            wx.request({
                url: `${API_BASE}/industries/statistics`,
                method: 'GET',
                success: (res) => {
                    if (res.statusCode === 200 && res.data.code === 0) {
                        resolve(res.data.data);
                    } else {
                        reject(new Error(res.data.message || '请求失败'));
                    }
                },
                fail: reject
            });
        });
    }
};

// 使用示例
/*
// 在页面中使用
Page({
    data: {
        stocks: []
    },
    
    onLoad() {
        this.loadStocks();
    },
    
    async loadStocks() {
        try {
            const data = await miniProgramAPI.getStocks({
                page: 1,
                per_page: 20
            });
            this.setData({
                stocks: data.stocks
            });
        } catch (error) {
            wx.showToast({
                title: error.message,
                icon: 'none'
            });
        }
    }
});
*/

module.exports = miniProgramAPI;



