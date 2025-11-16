-- 数据库升级脚本：添加 stock_company 接口字段
-- 执行前请先备份数据库
-- 使用方法: mysql -u root -p stock_data < upgrade_database.sql

USE stock_data;

-- 检查并添加新字段（MySQL 不支持 IF NOT EXISTS，需要手动检查）
-- 如果字段已存在，会报错，可以忽略

ALTER TABLE `stock_basic` 
  ADD COLUMN `com_name` varchar(200) DEFAULT NULL COMMENT '公司全称' AFTER `list_date`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `com_id` varchar(50) DEFAULT NULL COMMENT '统一社会信用代码' AFTER `com_name`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `chairman` varchar(50) DEFAULT NULL COMMENT '法人代表' AFTER `com_id`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `manager` varchar(50) DEFAULT NULL COMMENT '总经理' AFTER `chairman`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `secretary` varchar(50) DEFAULT NULL COMMENT '董秘' AFTER `manager`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `reg_capital` float DEFAULT NULL COMMENT '注册资本(万元)' AFTER `secretary`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `setup_date` varchar(10) DEFAULT NULL COMMENT '注册日期' AFTER `reg_capital`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `province` varchar(50) DEFAULT NULL COMMENT '所在省份' AFTER `setup_date`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `city` varchar(50) DEFAULT NULL COMMENT '所在城市' AFTER `province`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `introduction` text COMMENT '公司介绍' AFTER `city`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `website` varchar(200) DEFAULT NULL COMMENT '公司主页' AFTER `introduction`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `email` varchar(100) DEFAULT NULL COMMENT '电子邮件' AFTER `website`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `office` varchar(200) DEFAULT NULL COMMENT '办公室' AFTER `email`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `employees` int(11) DEFAULT NULL COMMENT '员工人数' AFTER `office`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `main_business` text COMMENT '主要业务及产品' AFTER `employees`;

ALTER TABLE `stock_basic` 
  ADD COLUMN `business_scope` text COMMENT '经营范围' AFTER `main_business`;

