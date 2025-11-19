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

-- 添加上市公司管理层信息表
CREATE TABLE IF NOT EXISTS `stock_manager` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `ts_code` varchar(20) NOT NULL COMMENT 'TS股票代码',
  `ann_date` varchar(10) DEFAULT NULL COMMENT '公告日期',
  `name` varchar(50) NOT NULL COMMENT '姓名',
  `gender` varchar(10) DEFAULT NULL COMMENT '性别',
  `lev` varchar(50) DEFAULT NULL COMMENT '岗位类别',
  `title` varchar(100) NOT NULL COMMENT '岗位',
  `edu` varchar(50) DEFAULT NULL COMMENT '学历',
  `national` varchar(50) DEFAULT NULL COMMENT '国籍',
  `birthday` varchar(20) DEFAULT NULL COMMENT '出生年月',
  `begin_date` varchar(10) DEFAULT NULL COMMENT '上任日期',
  `end_date` varchar(10) DEFAULT NULL COMMENT '离任日期',
  `resume` text COMMENT '个人简历',
  `salary` float DEFAULT NULL COMMENT '薪酬（万元）',
  `hold_vol` float DEFAULT NULL COMMENT '持股数量（股）',
  `reward_date` varchar(10) DEFAULT NULL COMMENT '薪酬报告期',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_at` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_ts_code` (`ts_code`),
  KEY `idx_ann_date` (`ann_date`),
  KEY `idx_name` (`name`),
  KEY `idx_title` (`title`),
  KEY `idx_ts_code_name_title` (`ts_code`, `name`, `title`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='上市公司管理层信息表';

-- 添加上市公司管理层变更历史表
CREATE TABLE IF NOT EXISTS `stock_manager_change` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `ts_code` varchar(20) NOT NULL COMMENT 'TS股票代码',
  `change_type` varchar(20) NOT NULL COMMENT '变更类型：新增/离职/岗位变更/信息更新',
  `name` varchar(50) NOT NULL COMMENT '姓名',
  `title` varchar(100) DEFAULT NULL COMMENT '岗位',
  `old_value` text COMMENT '旧值（JSON格式）',
  `new_value` text COMMENT '新值（JSON格式）',
  `change_date` varchar(10) DEFAULT NULL COMMENT '变更日期',
  `ann_date` varchar(10) DEFAULT NULL COMMENT '公告日期',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_ts_code` (`ts_code`),
  KEY `idx_change_type` (`change_type`),
  KEY `idx_change_date` (`change_date`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='上市公司管理层变更历史表';

-- 添加指数基本信息表
CREATE TABLE IF NOT EXISTS `index_basic` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `ts_code` varchar(20) NOT NULL COMMENT 'TS代码',
  `name` varchar(100) NOT NULL COMMENT '简称',
  `fullname` varchar(200) DEFAULT NULL COMMENT '指数全称',
  `market` varchar(20) DEFAULT NULL COMMENT '市场',
  `publisher` varchar(50) DEFAULT NULL COMMENT '发布方',
  `index_type` varchar(50) DEFAULT NULL COMMENT '指数风格',
  `category` varchar(50) DEFAULT NULL COMMENT '指数类别',
  `base_date` varchar(10) DEFAULT NULL COMMENT '基期',
  `base_point` float DEFAULT NULL COMMENT '基点',
  `list_date` varchar(10) DEFAULT NULL COMMENT '发布日期',
  `weight_rule` varchar(50) DEFAULT NULL COMMENT '加权方式',
  `desc` text COMMENT '描述',
  `exp_date` varchar(10) DEFAULT NULL COMMENT '终止日期',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_at` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ts_code` (`ts_code`),
  KEY `idx_market` (`market`),
  KEY `idx_category` (`category`),
  KEY `idx_publisher` (`publisher`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='指数基本信息表';

-- 添加指数日线行情表
CREATE TABLE IF NOT EXISTS `index_daily` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `ts_code` varchar(20) NOT NULL COMMENT 'TS代码',
  `trade_date` varchar(10) NOT NULL COMMENT '交易日期',
  `close` float DEFAULT NULL COMMENT '收盘点位',
  `open` float DEFAULT NULL COMMENT '开盘点位',
  `high` float DEFAULT NULL COMMENT '最高点位',
  `low` float DEFAULT NULL COMMENT '最低点位',
  `pre_close` float DEFAULT NULL COMMENT '昨收点位',
  `change` float DEFAULT NULL COMMENT '涨跌点位',
  `pct_chg` float DEFAULT NULL COMMENT '涨跌幅（%）',
  `vol` float DEFAULT NULL COMMENT '成交量（手）',
  `amount` float DEFAULT NULL COMMENT '成交额（千元）',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_ts_code_date` (`ts_code`, `trade_date`),
  KEY `idx_trade_date` (`trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='指数日线行情表';

-- 添加指数周线行情表
CREATE TABLE IF NOT EXISTS `index_weekly` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `ts_code` varchar(20) NOT NULL COMMENT 'TS代码',
  `trade_date` varchar(10) NOT NULL COMMENT '交易日期',
  `close` float DEFAULT NULL COMMENT '收盘点位',
  `open` float DEFAULT NULL COMMENT '开盘点位',
  `high` float DEFAULT NULL COMMENT '最高点位',
  `low` float DEFAULT NULL COMMENT '最低点位',
  `pre_close` float DEFAULT NULL COMMENT '昨收点位',
  `change` float DEFAULT NULL COMMENT '涨跌点位',
  `pct_chg` float DEFAULT NULL COMMENT '涨跌幅（%）',
  `vol` float DEFAULT NULL COMMENT '成交量（手）',
  `amount` float DEFAULT NULL COMMENT '成交额（千元）',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_ts_code_date` (`ts_code`, `trade_date`),
  KEY `idx_trade_date` (`trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='指数周线行情表';

-- 添加指数月线行情表
CREATE TABLE IF NOT EXISTS `index_monthly` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `ts_code` varchar(20) NOT NULL COMMENT 'TS代码',
  `trade_date` varchar(10) NOT NULL COMMENT '交易日期',
  `close` float DEFAULT NULL COMMENT '收盘点位',
  `open` float DEFAULT NULL COMMENT '开盘点位',
  `high` float DEFAULT NULL COMMENT '最高点位',
  `low` float DEFAULT NULL COMMENT '最低点位',
  `pre_close` float DEFAULT NULL COMMENT '昨收点位',
  `change` float DEFAULT NULL COMMENT '涨跌点位',
  `pct_chg` float DEFAULT NULL COMMENT '涨跌幅（%）',
  `vol` float DEFAULT NULL COMMENT '成交量（手）',
  `amount` float DEFAULT NULL COMMENT '成交额（千元）',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_ts_code_date` (`ts_code`, `trade_date`),
  KEY `idx_trade_date` (`trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='指数月线行情表';

-- 添加指数成分股权重表
CREATE TABLE IF NOT EXISTS `index_weight` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `index_code` varchar(20) NOT NULL COMMENT '指数代码',
  `con_code` varchar(20) NOT NULL COMMENT '成分代码（股票代码）',
  `trade_date` varchar(10) NOT NULL COMMENT '交易日期',
  `weight` float DEFAULT NULL COMMENT '权重',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_index_code_con_code_date` (`index_code`, `con_code`, `trade_date`),
  KEY `idx_index_code_date` (`index_code`, `trade_date`),
  KEY `idx_con_code` (`con_code`),
  KEY `idx_trade_date` (`trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='指数成分股权重表';

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

