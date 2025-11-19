-- 添加所有缺失的字段到数据库表
-- 使用方法: mysql -u root -p stock_data < add_all_missing_columns.sql
-- 注意：如果字段已存在，会报错，可以忽略错误继续执行

USE stock_data;

-- ============================================
-- 1. 添加 stock_basic 表的 premarket 字段
-- ============================================
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

-- ============================================
-- 2. 添加 stock_daily 表的资金流向字段
-- ============================================
ALTER TABLE `stock_daily` 
  ADD COLUMN `buy_sm_vol` float DEFAULT NULL COMMENT '小单买入量（手）' AFTER `amount`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `buy_sm_amount` float DEFAULT NULL COMMENT '小单买入金额（万元）' AFTER `buy_sm_vol`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `sell_sm_vol` float DEFAULT NULL COMMENT '小单卖出量（手）' AFTER `buy_sm_amount`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `sell_sm_amount` float DEFAULT NULL COMMENT '小单卖出金额（万元）' AFTER `sell_sm_vol`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `buy_md_vol` float DEFAULT NULL COMMENT '中单买入量（手）' AFTER `sell_sm_amount`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `buy_md_amount` float DEFAULT NULL COMMENT '中单买入金额（万元）' AFTER `buy_md_vol`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `sell_md_vol` float DEFAULT NULL COMMENT '中单卖出量（手）' AFTER `buy_md_amount`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `sell_md_amount` float DEFAULT NULL COMMENT '中单卖出金额（万元）' AFTER `sell_md_vol`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `buy_lg_vol` float DEFAULT NULL COMMENT '大单买入量（手）' AFTER `sell_md_amount`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `buy_lg_amount` float DEFAULT NULL COMMENT '大单买入金额（万元）' AFTER `buy_lg_vol`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `sell_lg_vol` float DEFAULT NULL COMMENT '大单卖出量（手）' AFTER `buy_lg_amount`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `sell_lg_amount` float DEFAULT NULL COMMENT '大单卖出金额（万元）' AFTER `sell_lg_vol`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `buy_elg_vol` float DEFAULT NULL COMMENT '特大单买入量（手）' AFTER `sell_lg_amount`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `buy_elg_amount` float DEFAULT NULL COMMENT '特大单买入金额（万元）' AFTER `buy_elg_vol`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `sell_elg_vol` float DEFAULT NULL COMMENT '特大单卖出量（手）' AFTER `buy_elg_amount`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `sell_elg_amount` float DEFAULT NULL COMMENT '特大单卖出金额（万元）' AFTER `sell_elg_vol`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `net_mf_amount` float DEFAULT NULL COMMENT '净流入额（万元）' AFTER `sell_elg_amount`;

-- ============================================
-- 3. 添加 stock_daily 表的两融数据字段
-- ============================================
ALTER TABLE `stock_daily` 
  ADD COLUMN `rzye` float DEFAULT NULL COMMENT '融资余额(元)' AFTER `net_mf_amount`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `rqye` float DEFAULT NULL COMMENT '融券余量(股)' AFTER `rzye`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `rqyl` float DEFAULT NULL COMMENT '融券余额(元)' AFTER `rqye`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `rzrqye` float DEFAULT NULL COMMENT '融资融券余额(元)' AFTER `rqyl`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `rzmre` float DEFAULT NULL COMMENT '融资买入额(元)' AFTER `rzrqye`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `rqmcl` float DEFAULT NULL COMMENT '融券卖出量(股)' AFTER `rzmre`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `rzche` float DEFAULT NULL COMMENT '融资偿还额(元)' AFTER `rqmcl`;

ALTER TABLE `stock_daily` 
  ADD COLUMN `rqchl` float DEFAULT NULL COMMENT '融券偿还量(股)' AFTER `rzche`;


