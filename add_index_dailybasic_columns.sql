-- 为指数日线行情表添加 index_dailybasic 接口的字段
-- 参考: https://tushare.pro/document/2?doc_id=128

USE stock_data;

-- 添加指数每日指标字段到 index_daily 表
ALTER TABLE `index_daily` 
  ADD COLUMN `total_mv` float DEFAULT NULL COMMENT '总市值（万元）' AFTER `amount`,
  ADD COLUMN `float_mv` float DEFAULT NULL COMMENT '流通市值（万元）' AFTER `total_mv`,
  ADD COLUMN `turnover_rate` float DEFAULT NULL COMMENT '换手率（%）' AFTER `float_mv`,
  ADD COLUMN `pe` float DEFAULT NULL COMMENT '市盈率' AFTER `turnover_rate`,
  ADD COLUMN `pb` float DEFAULT NULL COMMENT '市净率' AFTER `pe`;

-- 添加索引以提高查询性能
ALTER TABLE `index_daily` 
  ADD INDEX `idx_pe` (`pe`),
  ADD INDEX `idx_pb` (`pb`);


