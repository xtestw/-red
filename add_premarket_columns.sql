-- 添加缺失的 premarket 字段到 stock_basic 表
-- 使用方法: mysql -u root -p stock_data < add_premarket_columns.sql
-- 注意：如果字段已存在，会报错，可以忽略错误继续执行

USE stock_data;

-- 添加 stk_premarket 接口字段（每日盘前股本信息）
ALTER TABLE `stock_basic` 
  ADD COLUMN `total_share` float DEFAULT NULL COMMENT '总股本（万股）' AFTER `business_scope`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `float_share` float DEFAULT NULL COMMENT '流通股本（万股）' AFTER `total_share`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `pre_close` float DEFAULT NULL COMMENT '昨日收盘价' AFTER `float_share`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `up_limit` float DEFAULT NULL COMMENT '今日涨停价' AFTER `pre_close`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `down_limit` float DEFAULT NULL COMMENT '今日跌停价' AFTER `up_limit`;

