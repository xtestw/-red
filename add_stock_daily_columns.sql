-- 添加缺失的资金流向和两融数据字段到 stock_daily 表
-- 使用方法: mysql -u root -p stock_data < add_stock_daily_columns.sql
-- 注意：如果字段已存在，会报错，可以忽略错误继续执行

USE stock_data;

-- 在 stock_daily 表中添加资金流向字段
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

-- 在 stock_daily 表中添加两融数据字段
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





