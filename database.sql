-- Red-Stock 数据库表结构
-- 创建数据库
CREATE DATABASE IF NOT EXISTS stock_data CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE stock_data;

-- 股票基本信息表
CREATE TABLE IF NOT EXISTS `stock_basic` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `ts_code` varchar(20) NOT NULL COMMENT 'TS代码',
  `symbol` varchar(10) NOT NULL COMMENT '股票代码',
  `name` varchar(50) NOT NULL COMMENT '股票名称',
  `area` varchar(50) DEFAULT NULL COMMENT '地域',
  `industry` varchar(50) DEFAULT NULL COMMENT '所属行业',
  `market` varchar(20) DEFAULT NULL COMMENT '市场类型',
  `list_date` varchar(10) DEFAULT NULL COMMENT '上市日期',
  -- stock_company 接口补充字段
  `com_name` varchar(200) DEFAULT NULL COMMENT '公司全称',
  `com_id` varchar(50) DEFAULT NULL COMMENT '统一社会信用代码',
  `chairman` varchar(50) DEFAULT NULL COMMENT '法人代表',
  `manager` varchar(50) DEFAULT NULL COMMENT '总经理',
  `secretary` varchar(50) DEFAULT NULL COMMENT '董秘',
  `reg_capital` float DEFAULT NULL COMMENT '注册资本(万元)',
  `setup_date` varchar(10) DEFAULT NULL COMMENT '注册日期',
  `province` varchar(50) DEFAULT NULL COMMENT '所在省份',
  `city` varchar(50) DEFAULT NULL COMMENT '所在城市',
  `introduction` text COMMENT '公司介绍',
  `website` varchar(200) DEFAULT NULL COMMENT '公司主页',
  `email` varchar(100) DEFAULT NULL COMMENT '电子邮件',
  `office` varchar(200) DEFAULT NULL COMMENT '办公室',
  `employees` int(11) DEFAULT NULL COMMENT '员工人数',
  `main_business` text COMMENT '主要业务及产品',
  `business_scope` text COMMENT '经营范围',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_at` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ts_code` (`ts_code`),
  KEY `idx_industry` (`industry`),
  KEY `idx_market` (`market`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票基本信息表';

-- 注意：如果表已存在，需要使用 upgrade_database.sql 来添加新字段
-- 执行前请先备份数据库

-- 股票日线数据表
CREATE TABLE IF NOT EXISTS `stock_daily` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `ts_code` varchar(20) NOT NULL COMMENT 'TS代码',
  `trade_date` varchar(10) NOT NULL COMMENT '交易日期',
  `open` float DEFAULT NULL COMMENT '开盘价',
  `high` float DEFAULT NULL COMMENT '最高价',
  `low` float DEFAULT NULL COMMENT '最低价',
  `close` float DEFAULT NULL COMMENT '收盘价',
  `pre_close` float DEFAULT NULL COMMENT '昨收价',
  `change` float DEFAULT NULL COMMENT '涨跌额',
  `pct_chg` float DEFAULT NULL COMMENT '涨跌幅',
  `vol` float DEFAULT NULL COMMENT '成交量（手）',
  `amount` float DEFAULT NULL COMMENT '成交额（千元）',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_ts_code_date` (`ts_code`, `trade_date`),
  KEY `idx_trade_date` (`trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票日线数据表';

-- 股票周线数据表
CREATE TABLE IF NOT EXISTS `stock_weekly` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `ts_code` varchar(20) NOT NULL COMMENT 'TS代码',
  `trade_date` varchar(10) NOT NULL COMMENT '交易日期',
  `open` float DEFAULT NULL COMMENT '开盘价',
  `high` float DEFAULT NULL COMMENT '最高价',
  `low` float DEFAULT NULL COMMENT '最低价',
  `close` float DEFAULT NULL COMMENT '收盘价',
  `pre_close` float DEFAULT NULL COMMENT '昨收价',
  `change` float DEFAULT NULL COMMENT '涨跌额',
  `pct_chg` float DEFAULT NULL COMMENT '涨跌幅',
  `vol` float DEFAULT NULL COMMENT '成交量（手）',
  `amount` float DEFAULT NULL COMMENT '成交额（千元）',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_ts_code_date` (`ts_code`, `trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票周线数据表';

-- 股票月线数据表
CREATE TABLE IF NOT EXISTS `stock_monthly` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `ts_code` varchar(20) NOT NULL COMMENT 'TS代码',
  `trade_date` varchar(10) NOT NULL COMMENT '交易日期',
  `open` float DEFAULT NULL COMMENT '开盘价',
  `high` float DEFAULT NULL COMMENT '最高价',
  `low` float DEFAULT NULL COMMENT '最低价',
  `close` float DEFAULT NULL COMMENT '收盘价',
  `pre_close` float DEFAULT NULL COMMENT '昨收价',
  `change` float DEFAULT NULL COMMENT '涨跌额',
  `pct_chg` float DEFAULT NULL COMMENT '涨跌幅',
  `vol` float DEFAULT NULL COMMENT '成交量（手）',
  `amount` float DEFAULT NULL COMMENT '成交额（千元）',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_ts_code_date` (`ts_code`, `trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票月线数据表';

-- 股票资金流向表
CREATE TABLE IF NOT EXISTS `stock_moneyflow` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `ts_code` varchar(20) NOT NULL COMMENT 'TS代码',
  `trade_date` varchar(10) NOT NULL COMMENT '交易日期',
  `buy_sm_amount` float DEFAULT NULL COMMENT '小单买入金额（万元）',
  `sell_sm_amount` float DEFAULT NULL COMMENT '小单卖出金额（万元）',
  `buy_md_amount` float DEFAULT NULL COMMENT '中单买入金额（万元）',
  `sell_md_amount` float DEFAULT NULL COMMENT '中单卖出金额（万元）',
  `buy_lg_amount` float DEFAULT NULL COMMENT '大单买入金额（万元）',
  `sell_lg_amount` float DEFAULT NULL COMMENT '大单卖出金额（万元）',
  `buy_elg_amount` float DEFAULT NULL COMMENT '特大单买入金额（万元）',
  `sell_elg_amount` float DEFAULT NULL COMMENT '特大单卖出金额（万元）',
  `net_mf_amount` float DEFAULT NULL COMMENT '净流入额（万元）',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_ts_code_date` (`ts_code`, `trade_date`),
  KEY `idx_trade_date` (`trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票资金流向表';

-- 股票指标表（市值、市盈率等）
CREATE TABLE IF NOT EXISTS `stock_indicator` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `ts_code` varchar(20) NOT NULL COMMENT 'TS代码',
  `trade_date` varchar(10) NOT NULL COMMENT '交易日期',
  `total_mv` float DEFAULT NULL COMMENT '总市值（万元）',
  `circ_mv` float DEFAULT NULL COMMENT '流通市值（万元）',
  `pe` float DEFAULT NULL COMMENT '市盈率',
  `pb` float DEFAULT NULL COMMENT '市净率',
  `ps` float DEFAULT NULL COMMENT '市销率',
  `dv_ttm` float DEFAULT NULL COMMENT '股息率',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_ts_code_date` (`ts_code`, `trade_date`),
  KEY `idx_trade_date` (`trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票指标表';

-- 股票收藏表
CREATE TABLE IF NOT EXISTS `stock_favorite` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `ts_code` varchar(20) NOT NULL COMMENT 'TS代码',
  `user_id` varchar(50) DEFAULT 'default' COMMENT '用户ID（预留）',
  `notes` text COMMENT '备注',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_ts_code` (`ts_code`),
  KEY `idx_user_id` (`user_id`),
  UNIQUE KEY `idx_user_ts_code` (`user_id`, `ts_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票收藏表';

-- 选股结果表（存储每天选出来的股票）
CREATE TABLE IF NOT EXISTS `stock_selection` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `ts_code` varchar(20) NOT NULL COMMENT 'TS代码',
  `strategy_name` varchar(50) NOT NULL COMMENT '策略名称',
  `trade_date` varchar(10) NOT NULL COMMENT '选股日期',
  `score` float DEFAULT NULL COMMENT '策略评分',
  `reason` text COMMENT '选股理由',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_strategy_date_code` (`strategy_name`, `trade_date`, `ts_code`),
  KEY `idx_strategy_name` (`strategy_name`),
  KEY `idx_trade_date` (`trade_date`),
  KEY `idx_ts_code` (`ts_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='选股结果表';

-- IPO新股列表表
CREATE TABLE IF NOT EXISTS `stock_ipo` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `ts_code` varchar(20) NOT NULL COMMENT 'TS股票代码',
  `sub_code` varchar(20) DEFAULT NULL COMMENT '申购代码',
  `name` varchar(50) NOT NULL COMMENT '名称',
  `ipo_date` varchar(10) DEFAULT NULL COMMENT '上网发行日期',
  `issue_date` varchar(10) DEFAULT NULL COMMENT '上市日期',
  `amount` float DEFAULT NULL COMMENT '发行总量（万股）',
  `market_amount` float DEFAULT NULL COMMENT '上网发行总量（万股）',
  `price` float DEFAULT NULL COMMENT '发行价格',
  `pe` float DEFAULT NULL COMMENT '市盈率',
  `limit_amount` float DEFAULT NULL COMMENT '个人申购上限（万股）',
  `funds` float DEFAULT NULL COMMENT '募集资金（亿元）',
  `ballot` float DEFAULT NULL COMMENT '中签率',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_at` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_ts_code` (`ts_code`),
  KEY `idx_ipo_date` (`ipo_date`),
  KEY `idx_issue_date` (`issue_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='IPO新股列表表';



