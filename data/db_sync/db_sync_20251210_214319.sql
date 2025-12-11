-- 数据库结构同步SQL
-- 生成时间: 2025-12-10 21:43:19
-- 本地数据库: stock_data
-- 远端数据库: stock_data

-- 差异列表:
-- column_different: stock_basic.float_share
-- column_different: stock_basic.business_scope
-- column_different: stock_basic.industry
-- column_different: stock_basic.province
-- column_different: stock_basic.pre_close
-- column_different: stock_basic.website
-- column_different: stock_basic.area
-- column_different: stock_basic.employees
-- column_different: stock_basic.introduction
-- column_different: stock_basic.updated_at
-- column_different: stock_basic.com_id
-- column_different: stock_basic.reg_capital
-- column_different: stock_basic.total_share
-- column_different: stock_basic.main_business
-- column_different: stock_basic.chairman
-- column_different: stock_basic.up_limit
-- column_different: stock_basic.com_name
-- column_different: stock_basic.created_at
-- column_different: stock_basic.email
-- column_different: stock_basic.secretary
-- column_different: stock_basic.setup_date
-- column_different: stock_basic.ts_code
-- column_different: stock_basic.down_limit
-- column_different: stock_basic.symbol
-- column_different: stock_basic.city
-- column_different: stock_basic.id
-- column_different: stock_basic.manager
-- column_different: stock_basic.office
-- column_different: stock_basic.name
-- column_different: stock_basic.list_date
-- column_different: stock_basic.market
-- index_missing_local: stock_basic.PRIMARY
-- column_different: stock_selection.reason
-- column_different: stock_selection.trade_date
-- column_different: stock_selection.ts_code
-- column_different: stock_selection.score
-- column_different: stock_selection.id
-- column_different: stock_selection.created_at
-- column_different: stock_selection.strategy_name
-- index_missing_local: stock_selection.PRIMARY
-- column_different: user_sessions.expires_at
-- column_different: user_sessions.refresh_token
-- column_different: user_sessions.id
-- column_different: user_sessions.created_at
-- column_different: user_sessions.last_used_at
-- column_different: user_sessions.user_id
-- column_different: user_sessions.token
-- index_missing_local: user_sessions.PRIMARY
-- column_different: stock_moneyflow.sell_lg_amount
-- column_different: stock_moneyflow.sell_md_amount
-- column_different: stock_moneyflow.trade_date
-- column_different: stock_moneyflow.ts_code
-- column_different: stock_moneyflow.buy_sm_amount
-- column_different: stock_moneyflow.net_mf_amount
-- column_different: stock_moneyflow.sell_elg_amount
-- column_different: stock_moneyflow.id
-- column_different: stock_moneyflow.created_at
-- column_different: stock_moneyflow.buy_lg_amount
-- column_different: stock_moneyflow.buy_elg_amount
-- column_different: stock_moneyflow.sell_sm_amount
-- column_different: stock_moneyflow.buy_md_amount
-- index_missing_local: stock_moneyflow.PRIMARY
-- column_different: stock_monthly.open
-- column_different: stock_monthly.trade_date
-- column_different: stock_monthly.ts_code
-- column_different: stock_monthly.vol
-- column_different: stock_monthly.close
-- column_different: stock_monthly.id
-- column_different: stock_monthly.pct_chg
-- column_different: stock_monthly.high
-- column_different: stock_monthly.pre_close
-- column_different: stock_monthly.created_at
-- column_different: stock_monthly.amount
-- column_different: stock_monthly.change
-- column_different: stock_monthly.low
-- index_missing_local: stock_monthly.PRIMARY
-- column_different: stock_daily.buy_elg_vol
-- column_different: stock_daily.pre_close
-- column_different: stock_daily.buy_elg_amount
-- column_different: stock_daily.buy_md_vol
-- column_different: stock_daily.change
-- column_different: stock_daily.low
-- column_different: stock_daily.close
-- column_different: stock_daily.rzrqye
-- column_different: stock_daily.buy_lg_vol
-- column_different: stock_daily.rqchl
-- column_different: stock_daily.rzche
-- column_different: stock_daily.rqyl
-- column_different: stock_daily.sell_elg_vol
-- column_different: stock_daily.buy_sm_vol
-- column_different: stock_daily.rzye
-- column_different: stock_daily.vol
-- column_different: stock_daily.buy_sm_amount
-- column_different: stock_daily.pct_chg
-- column_different: stock_daily.high
-- column_different: stock_daily.created_at
-- column_different: stock_daily.amount
-- column_different: stock_daily.buy_lg_amount
-- column_different: stock_daily.sell_sm_amount
-- column_different: stock_daily.rqmcl
-- column_different: stock_daily.sell_sm_vol
-- column_different: stock_daily.sell_lg_vol
-- column_different: stock_daily.sell_lg_amount
-- column_different: stock_daily.open
-- column_different: stock_daily.trade_date
-- column_different: stock_daily.ts_code
-- column_different: stock_daily.sell_md_amount
-- column_different: stock_daily.net_mf_amount
-- column_different: stock_daily.sell_elg_amount
-- column_different: stock_daily.id
-- column_different: stock_daily.rzmre
-- column_different: stock_daily.rqye
-- column_different: stock_daily.buy_md_amount
-- column_different: stock_daily.sell_md_vol
-- index_missing_local: stock_daily.PRIMARY
-- column_different: stock_indicator.pb
-- column_different: stock_indicator.trade_date
-- column_different: stock_indicator.ts_code
-- column_different: stock_indicator.total_mv
-- column_different: stock_indicator.circ_mv
-- column_different: stock_indicator.id
-- column_different: stock_indicator.created_at
-- column_different: stock_indicator.pe
-- column_different: stock_indicator.dv_ttm
-- column_different: stock_indicator.ps
-- index_missing_local: stock_indicator.PRIMARY
-- column_different: stock_weekly.open
-- column_different: stock_weekly.trade_date
-- column_different: stock_weekly.ts_code
-- column_different: stock_weekly.vol
-- column_different: stock_weekly.close
-- column_different: stock_weekly.id
-- column_different: stock_weekly.pct_chg
-- column_different: stock_weekly.high
-- column_different: stock_weekly.pre_close
-- column_different: stock_weekly.created_at
-- column_different: stock_weekly.amount
-- column_different: stock_weekly.change
-- column_different: stock_weekly.low
-- index_missing_local: stock_weekly.PRIMARY
-- column_different: stock_favorite.ts_code
-- column_different: stock_favorite.id
-- column_different: stock_favorite.created_at
-- column_different: stock_favorite.user_id
-- column_different: stock_favorite.notes
-- index_missing_local: stock_favorite.PRIMARY
-- column_different: users.avatar
-- column_different: users.gender
-- column_different: users.openid
-- column_different: users.updated_at
-- column_different: users.unionid
-- column_different: users.country
-- column_different: users.city
-- column_different: users.id
-- column_different: users.last_login_at
-- column_different: users.province
-- column_different: users.created_at
-- column_different: users.nickname
-- column_different: users.language
-- index_missing_local: users.PRIMARY
-- column_different: stock_ipo.issue_date
-- column_different: stock_ipo.funds
-- column_different: stock_ipo.ts_code
-- column_different: stock_ipo.sub_code
-- column_different: stock_ipo.updated_at
-- column_different: stock_ipo.ballot
-- column_different: stock_ipo.id
-- column_different: stock_ipo.created_at
-- column_different: stock_ipo.amount
-- column_different: stock_ipo.market_amount
-- column_different: stock_ipo.ipo_date
-- column_different: stock_ipo.name
-- column_different: stock_ipo.pe
-- column_different: stock_ipo.price
-- column_different: stock_ipo.limit_amount
-- index_missing_local: stock_ipo.PRIMARY

-- SQL语句:

-- modify_column: stock_basic.float_share
ALTER TABLE `stock_basic` MODIFY COLUMN `float_share` FLOAT NULL  COMMENT '流通股本（万股）';

-- modify_column: stock_basic.business_scope
ALTER TABLE `stock_basic` MODIFY COLUMN `business_scope` TEXT NULL  COMMENT '经营范围';

-- modify_column: stock_basic.industry
ALTER TABLE `stock_basic` MODIFY COLUMN `industry` VARCHAR(50) NULL  COMMENT '所属行业';

-- modify_column: stock_basic.province
ALTER TABLE `stock_basic` MODIFY COLUMN `province` VARCHAR(50) NULL  COMMENT '所在省份';

-- modify_column: stock_basic.pre_close
ALTER TABLE `stock_basic` MODIFY COLUMN `pre_close` FLOAT NULL  COMMENT '昨日收盘价';

-- modify_column: stock_basic.website
ALTER TABLE `stock_basic` MODIFY COLUMN `website` VARCHAR(200) NULL  COMMENT '公司主页';

-- modify_column: stock_basic.area
ALTER TABLE `stock_basic` MODIFY COLUMN `area` VARCHAR(50) NULL  COMMENT '地域';

-- modify_column: stock_basic.employees
ALTER TABLE `stock_basic` MODIFY COLUMN `employees` INTEGER NULL  COMMENT '员工人数';

-- modify_column: stock_basic.introduction
ALTER TABLE `stock_basic` MODIFY COLUMN `introduction` TEXT NULL  COMMENT '公司介绍';

-- modify_column: stock_basic.updated_at
ALTER TABLE `stock_basic` MODIFY COLUMN `updated_at` DATETIME NULL  COMMENT '更新时间';

-- modify_column: stock_basic.com_id
ALTER TABLE `stock_basic` MODIFY COLUMN `com_id` VARCHAR(50) NULL  COMMENT '统一社会信用代码';

-- modify_column: stock_basic.reg_capital
ALTER TABLE `stock_basic` MODIFY COLUMN `reg_capital` FLOAT NULL  COMMENT '注册资本(万元)';

-- modify_column: stock_basic.total_share
ALTER TABLE `stock_basic` MODIFY COLUMN `total_share` FLOAT NULL  COMMENT '总股本（万股）';

-- modify_column: stock_basic.main_business
ALTER TABLE `stock_basic` MODIFY COLUMN `main_business` TEXT NULL  COMMENT '主要业务及产品';

-- modify_column: stock_basic.chairman
ALTER TABLE `stock_basic` MODIFY COLUMN `chairman` VARCHAR(50) NULL  COMMENT '法人代表';

-- modify_column: stock_basic.up_limit
ALTER TABLE `stock_basic` MODIFY COLUMN `up_limit` FLOAT NULL  COMMENT '今日涨停价';

-- modify_column: stock_basic.com_name
ALTER TABLE `stock_basic` MODIFY COLUMN `com_name` VARCHAR(200) NULL  COMMENT '公司全称';

-- modify_column: stock_basic.created_at
ALTER TABLE `stock_basic` MODIFY COLUMN `created_at` DATETIME NULL  COMMENT '创建时间';

-- modify_column: stock_basic.email
ALTER TABLE `stock_basic` MODIFY COLUMN `email` VARCHAR(100) NULL  COMMENT '电子邮件';

-- modify_column: stock_basic.secretary
ALTER TABLE `stock_basic` MODIFY COLUMN `secretary` VARCHAR(50) NULL  COMMENT '董秘';

-- modify_column: stock_basic.setup_date
ALTER TABLE `stock_basic` MODIFY COLUMN `setup_date` VARCHAR(10) NULL  COMMENT '注册日期';

-- modify_column: stock_basic.ts_code
ALTER TABLE `stock_basic` MODIFY COLUMN `ts_code` VARCHAR(20) NOT NULL  COMMENT 'TS代码';

-- modify_column: stock_basic.down_limit
ALTER TABLE `stock_basic` MODIFY COLUMN `down_limit` FLOAT NULL  COMMENT '今日跌停价';

-- modify_column: stock_basic.symbol
ALTER TABLE `stock_basic` MODIFY COLUMN `symbol` VARCHAR(10) NOT NULL  COMMENT '股票代码';

-- modify_column: stock_basic.city
ALTER TABLE `stock_basic` MODIFY COLUMN `city` VARCHAR(50) NULL  COMMENT '所在城市';

-- modify_column: stock_basic.id
ALTER TABLE `stock_basic` MODIFY COLUMN `id` INTEGER NOT NULL  COMMENT '主键ID';

-- modify_column: stock_basic.manager
ALTER TABLE `stock_basic` MODIFY COLUMN `manager` VARCHAR(50) NULL  COMMENT '总经理';

-- modify_column: stock_basic.office
ALTER TABLE `stock_basic` MODIFY COLUMN `office` VARCHAR(200) NULL  COMMENT '办公室';

-- modify_column: stock_basic.name
ALTER TABLE `stock_basic` MODIFY COLUMN `name` VARCHAR(50) NOT NULL  COMMENT '股票名称';

-- modify_column: stock_basic.list_date
ALTER TABLE `stock_basic` MODIFY COLUMN `list_date` VARCHAR(10) NULL  COMMENT '上市日期';

-- modify_column: stock_basic.market
ALTER TABLE `stock_basic` MODIFY COLUMN `market` VARCHAR(20) NULL  COMMENT '市场类型';

-- drop_index: stock_basic.PRIMARY
ALTER TABLE `stock_basic` DROP INDEX `PRIMARY`;

-- modify_column: stock_selection.reason
ALTER TABLE `stock_selection` MODIFY COLUMN `reason` TEXT NULL  COMMENT '选股理由';

-- modify_column: stock_selection.trade_date
ALTER TABLE `stock_selection` MODIFY COLUMN `trade_date` VARCHAR(10) NOT NULL  COMMENT '选股日期';

-- modify_column: stock_selection.ts_code
ALTER TABLE `stock_selection` MODIFY COLUMN `ts_code` VARCHAR(20) NOT NULL  COMMENT 'TS代码';

-- modify_column: stock_selection.score
ALTER TABLE `stock_selection` MODIFY COLUMN `score` FLOAT NULL  COMMENT '策略评分';

-- modify_column: stock_selection.id
ALTER TABLE `stock_selection` MODIFY COLUMN `id` INTEGER NOT NULL  COMMENT '主键ID';

-- modify_column: stock_selection.created_at
ALTER TABLE `stock_selection` MODIFY COLUMN `created_at` DATETIME NULL  COMMENT '创建时间';

-- modify_column: stock_selection.strategy_name
ALTER TABLE `stock_selection` MODIFY COLUMN `strategy_name` VARCHAR(50) NOT NULL  COMMENT '策略名称';

-- drop_index: stock_selection.PRIMARY
ALTER TABLE `stock_selection` DROP INDEX `PRIMARY`;

-- modify_column: user_sessions.expires_at
ALTER TABLE `user_sessions` MODIFY COLUMN `expires_at` DATETIME NOT NULL  COMMENT '过期时间';

-- modify_column: user_sessions.refresh_token
ALTER TABLE `user_sessions` MODIFY COLUMN `refresh_token` VARCHAR(500) NULL  COMMENT '刷新Token';

-- modify_column: user_sessions.id
ALTER TABLE `user_sessions` MODIFY COLUMN `id` INTEGER NOT NULL  COMMENT '主键ID';

-- modify_column: user_sessions.created_at
ALTER TABLE `user_sessions` MODIFY COLUMN `created_at` DATETIME NULL  COMMENT '创建时间';

-- modify_column: user_sessions.last_used_at
ALTER TABLE `user_sessions` MODIFY COLUMN `last_used_at` DATETIME NULL  COMMENT '最后使用时间';

-- modify_column: user_sessions.user_id
ALTER TABLE `user_sessions` MODIFY COLUMN `user_id` INTEGER NOT NULL  COMMENT '用户ID';

-- modify_column: user_sessions.token
ALTER TABLE `user_sessions` MODIFY COLUMN `token` VARCHAR(500) NOT NULL  COMMENT 'JWT Token';

-- drop_index: user_sessions.PRIMARY
ALTER TABLE `user_sessions` DROP INDEX `PRIMARY`;

-- modify_column: stock_moneyflow.sell_lg_amount
ALTER TABLE `stock_moneyflow` MODIFY COLUMN `sell_lg_amount` FLOAT NULL  COMMENT '大单卖出金额（万元）';

-- modify_column: stock_moneyflow.sell_md_amount
ALTER TABLE `stock_moneyflow` MODIFY COLUMN `sell_md_amount` FLOAT NULL  COMMENT '中单卖出金额（万元）';

-- modify_column: stock_moneyflow.trade_date
ALTER TABLE `stock_moneyflow` MODIFY COLUMN `trade_date` VARCHAR(10) NOT NULL  COMMENT '交易日期';

-- modify_column: stock_moneyflow.ts_code
ALTER TABLE `stock_moneyflow` MODIFY COLUMN `ts_code` VARCHAR(20) NOT NULL  COMMENT 'TS代码';

-- modify_column: stock_moneyflow.buy_sm_amount
ALTER TABLE `stock_moneyflow` MODIFY COLUMN `buy_sm_amount` FLOAT NULL  COMMENT '小单买入金额（万元）';

-- modify_column: stock_moneyflow.net_mf_amount
ALTER TABLE `stock_moneyflow` MODIFY COLUMN `net_mf_amount` FLOAT NULL  COMMENT '净流入额（万元）';

-- modify_column: stock_moneyflow.sell_elg_amount
ALTER TABLE `stock_moneyflow` MODIFY COLUMN `sell_elg_amount` FLOAT NULL  COMMENT '特大单卖出金额（万元）';

-- modify_column: stock_moneyflow.id
ALTER TABLE `stock_moneyflow` MODIFY COLUMN `id` INTEGER NOT NULL  COMMENT '主键ID';

-- modify_column: stock_moneyflow.created_at
ALTER TABLE `stock_moneyflow` MODIFY COLUMN `created_at` DATETIME NULL  COMMENT '创建时间';

-- modify_column: stock_moneyflow.buy_lg_amount
ALTER TABLE `stock_moneyflow` MODIFY COLUMN `buy_lg_amount` FLOAT NULL  COMMENT '大单买入金额（万元）';

-- modify_column: stock_moneyflow.buy_elg_amount
ALTER TABLE `stock_moneyflow` MODIFY COLUMN `buy_elg_amount` FLOAT NULL  COMMENT '特大单买入金额（万元）';

-- modify_column: stock_moneyflow.sell_sm_amount
ALTER TABLE `stock_moneyflow` MODIFY COLUMN `sell_sm_amount` FLOAT NULL  COMMENT '小单卖出金额（万元）';

-- modify_column: stock_moneyflow.buy_md_amount
ALTER TABLE `stock_moneyflow` MODIFY COLUMN `buy_md_amount` FLOAT NULL  COMMENT '中单买入金额（万元）';

-- drop_index: stock_moneyflow.PRIMARY
ALTER TABLE `stock_moneyflow` DROP INDEX `PRIMARY`;

-- modify_column: stock_monthly.open
ALTER TABLE `stock_monthly` MODIFY COLUMN `open` FLOAT NULL  COMMENT '开盘价';

-- modify_column: stock_monthly.trade_date
ALTER TABLE `stock_monthly` MODIFY COLUMN `trade_date` VARCHAR(10) NOT NULL  COMMENT '交易日期';

-- modify_column: stock_monthly.ts_code
ALTER TABLE `stock_monthly` MODIFY COLUMN `ts_code` VARCHAR(20) NOT NULL  COMMENT 'TS代码';

-- modify_column: stock_monthly.vol
ALTER TABLE `stock_monthly` MODIFY COLUMN `vol` FLOAT NULL  COMMENT '成交量（手）';

-- modify_column: stock_monthly.close
ALTER TABLE `stock_monthly` MODIFY COLUMN `close` FLOAT NULL  COMMENT '收盘价';

-- modify_column: stock_monthly.id
ALTER TABLE `stock_monthly` MODIFY COLUMN `id` INTEGER NOT NULL  COMMENT '主键ID';

-- modify_column: stock_monthly.pct_chg
ALTER TABLE `stock_monthly` MODIFY COLUMN `pct_chg` FLOAT NULL  COMMENT '涨跌幅';

-- modify_column: stock_monthly.high
ALTER TABLE `stock_monthly` MODIFY COLUMN `high` FLOAT NULL  COMMENT '最高价';

-- modify_column: stock_monthly.pre_close
ALTER TABLE `stock_monthly` MODIFY COLUMN `pre_close` FLOAT NULL  COMMENT '昨收价';

-- modify_column: stock_monthly.created_at
ALTER TABLE `stock_monthly` MODIFY COLUMN `created_at` DATETIME NULL  COMMENT '创建时间';

-- modify_column: stock_monthly.amount
ALTER TABLE `stock_monthly` MODIFY COLUMN `amount` FLOAT NULL  COMMENT '成交额（千元）';

-- modify_column: stock_monthly.change
ALTER TABLE `stock_monthly` MODIFY COLUMN `change` FLOAT NULL  COMMENT '涨跌额';

-- modify_column: stock_monthly.low
ALTER TABLE `stock_monthly` MODIFY COLUMN `low` FLOAT NULL  COMMENT '最低价';

-- drop_index: stock_monthly.PRIMARY
ALTER TABLE `stock_monthly` DROP INDEX `PRIMARY`;

-- modify_column: stock_daily.buy_elg_vol
ALTER TABLE `stock_daily` MODIFY COLUMN `buy_elg_vol` FLOAT NULL  COMMENT '特大单买入量（手）';

-- modify_column: stock_daily.pre_close
ALTER TABLE `stock_daily` MODIFY COLUMN `pre_close` FLOAT NULL  COMMENT '昨收价';

-- modify_column: stock_daily.buy_elg_amount
ALTER TABLE `stock_daily` MODIFY COLUMN `buy_elg_amount` FLOAT NULL  COMMENT '特大单买入金额（万元）';

-- modify_column: stock_daily.buy_md_vol
ALTER TABLE `stock_daily` MODIFY COLUMN `buy_md_vol` FLOAT NULL  COMMENT '中单买入量（手）';

-- modify_column: stock_daily.change
ALTER TABLE `stock_daily` MODIFY COLUMN `change` FLOAT NULL  COMMENT '涨跌额';

-- modify_column: stock_daily.low
ALTER TABLE `stock_daily` MODIFY COLUMN `low` FLOAT NULL  COMMENT '最低价';

-- modify_column: stock_daily.close
ALTER TABLE `stock_daily` MODIFY COLUMN `close` FLOAT NULL  COMMENT '收盘价';

-- modify_column: stock_daily.rzrqye
ALTER TABLE `stock_daily` MODIFY COLUMN `rzrqye` FLOAT NULL  COMMENT '融资融券余额(元)';

-- modify_column: stock_daily.buy_lg_vol
ALTER TABLE `stock_daily` MODIFY COLUMN `buy_lg_vol` FLOAT NULL  COMMENT '大单买入量（手）';

-- modify_column: stock_daily.rqchl
ALTER TABLE `stock_daily` MODIFY COLUMN `rqchl` FLOAT NULL  COMMENT '融券偿还量(股)';

-- modify_column: stock_daily.rzche
ALTER TABLE `stock_daily` MODIFY COLUMN `rzche` FLOAT NULL  COMMENT '融资偿还额(元)';

-- modify_column: stock_daily.rqyl
ALTER TABLE `stock_daily` MODIFY COLUMN `rqyl` FLOAT NULL  COMMENT '融券余额(元)';

-- modify_column: stock_daily.sell_elg_vol
ALTER TABLE `stock_daily` MODIFY COLUMN `sell_elg_vol` FLOAT NULL  COMMENT '特大单卖出量（手）';

-- modify_column: stock_daily.buy_sm_vol
ALTER TABLE `stock_daily` MODIFY COLUMN `buy_sm_vol` FLOAT NULL  COMMENT '小单买入量（手）';

-- modify_column: stock_daily.rzye
ALTER TABLE `stock_daily` MODIFY COLUMN `rzye` FLOAT NULL  COMMENT '融资余额(元)';

-- modify_column: stock_daily.vol
ALTER TABLE `stock_daily` MODIFY COLUMN `vol` FLOAT NULL  COMMENT '成交量（手）';

-- modify_column: stock_daily.buy_sm_amount
ALTER TABLE `stock_daily` MODIFY COLUMN `buy_sm_amount` FLOAT NULL  COMMENT '小单买入金额（万元）';

-- modify_column: stock_daily.pct_chg
ALTER TABLE `stock_daily` MODIFY COLUMN `pct_chg` FLOAT NULL  COMMENT '涨跌幅';

-- modify_column: stock_daily.high
ALTER TABLE `stock_daily` MODIFY COLUMN `high` FLOAT NULL  COMMENT '最高价';

-- modify_column: stock_daily.created_at
ALTER TABLE `stock_daily` MODIFY COLUMN `created_at` DATETIME NULL  COMMENT '创建时间';

-- modify_column: stock_daily.amount
ALTER TABLE `stock_daily` MODIFY COLUMN `amount` FLOAT NULL  COMMENT '成交额（千元）';

-- modify_column: stock_daily.buy_lg_amount
ALTER TABLE `stock_daily` MODIFY COLUMN `buy_lg_amount` FLOAT NULL  COMMENT '大单买入金额（万元）';

-- modify_column: stock_daily.sell_sm_amount
ALTER TABLE `stock_daily` MODIFY COLUMN `sell_sm_amount` FLOAT NULL  COMMENT '小单卖出金额（万元）';

-- modify_column: stock_daily.rqmcl
ALTER TABLE `stock_daily` MODIFY COLUMN `rqmcl` FLOAT NULL  COMMENT '融券卖出量(股)';

-- modify_column: stock_daily.sell_sm_vol
ALTER TABLE `stock_daily` MODIFY COLUMN `sell_sm_vol` FLOAT NULL  COMMENT '小单卖出量（手）';

-- modify_column: stock_daily.sell_lg_vol
ALTER TABLE `stock_daily` MODIFY COLUMN `sell_lg_vol` FLOAT NULL  COMMENT '大单卖出量（手）';

-- modify_column: stock_daily.sell_lg_amount
ALTER TABLE `stock_daily` MODIFY COLUMN `sell_lg_amount` FLOAT NULL  COMMENT '大单卖出金额（万元）';

-- modify_column: stock_daily.open
ALTER TABLE `stock_daily` MODIFY COLUMN `open` FLOAT NULL  COMMENT '开盘价';

-- modify_column: stock_daily.trade_date
ALTER TABLE `stock_daily` MODIFY COLUMN `trade_date` VARCHAR(10) NOT NULL  COMMENT '交易日期';

-- modify_column: stock_daily.ts_code
ALTER TABLE `stock_daily` MODIFY COLUMN `ts_code` VARCHAR(20) NOT NULL  COMMENT 'TS代码';

-- modify_column: stock_daily.sell_md_amount
ALTER TABLE `stock_daily` MODIFY COLUMN `sell_md_amount` FLOAT NULL  COMMENT '中单卖出金额（万元）';

-- modify_column: stock_daily.net_mf_amount
ALTER TABLE `stock_daily` MODIFY COLUMN `net_mf_amount` FLOAT NULL  COMMENT '净流入额（万元）';

-- modify_column: stock_daily.sell_elg_amount
ALTER TABLE `stock_daily` MODIFY COLUMN `sell_elg_amount` FLOAT NULL  COMMENT '特大单卖出金额（万元）';

-- modify_column: stock_daily.id
ALTER TABLE `stock_daily` MODIFY COLUMN `id` INTEGER NOT NULL  COMMENT '主键ID';

-- modify_column: stock_daily.rzmre
ALTER TABLE `stock_daily` MODIFY COLUMN `rzmre` FLOAT NULL  COMMENT '融资买入额(元)';

-- modify_column: stock_daily.rqye
ALTER TABLE `stock_daily` MODIFY COLUMN `rqye` FLOAT NULL  COMMENT '融券余量(股)';

-- modify_column: stock_daily.buy_md_amount
ALTER TABLE `stock_daily` MODIFY COLUMN `buy_md_amount` FLOAT NULL  COMMENT '中单买入金额（万元）';

-- modify_column: stock_daily.sell_md_vol
ALTER TABLE `stock_daily` MODIFY COLUMN `sell_md_vol` FLOAT NULL  COMMENT '中单卖出量（手）';

-- drop_index: stock_daily.PRIMARY
ALTER TABLE `stock_daily` DROP INDEX `PRIMARY`;

-- modify_column: stock_indicator.pb
ALTER TABLE `stock_indicator` MODIFY COLUMN `pb` FLOAT NULL  COMMENT '市净率';

-- modify_column: stock_indicator.trade_date
ALTER TABLE `stock_indicator` MODIFY COLUMN `trade_date` VARCHAR(10) NOT NULL  COMMENT '交易日期';

-- modify_column: stock_indicator.ts_code
ALTER TABLE `stock_indicator` MODIFY COLUMN `ts_code` VARCHAR(20) NOT NULL  COMMENT 'TS代码';

-- modify_column: stock_indicator.total_mv
ALTER TABLE `stock_indicator` MODIFY COLUMN `total_mv` FLOAT NULL  COMMENT '总市值（万元）';

-- modify_column: stock_indicator.circ_mv
ALTER TABLE `stock_indicator` MODIFY COLUMN `circ_mv` FLOAT NULL  COMMENT '流通市值（万元）';

-- modify_column: stock_indicator.id
ALTER TABLE `stock_indicator` MODIFY COLUMN `id` INTEGER NOT NULL  COMMENT '主键ID';

-- modify_column: stock_indicator.created_at
ALTER TABLE `stock_indicator` MODIFY COLUMN `created_at` DATETIME NULL  COMMENT '创建时间';

-- modify_column: stock_indicator.pe
ALTER TABLE `stock_indicator` MODIFY COLUMN `pe` FLOAT NULL  COMMENT '市盈率';

-- modify_column: stock_indicator.dv_ttm
ALTER TABLE `stock_indicator` MODIFY COLUMN `dv_ttm` FLOAT NULL  COMMENT '股息率';

-- modify_column: stock_indicator.ps
ALTER TABLE `stock_indicator` MODIFY COLUMN `ps` FLOAT NULL  COMMENT '市销率';

-- drop_index: stock_indicator.PRIMARY
ALTER TABLE `stock_indicator` DROP INDEX `PRIMARY`;

-- modify_column: stock_weekly.open
ALTER TABLE `stock_weekly` MODIFY COLUMN `open` FLOAT NULL  COMMENT '开盘价';

-- modify_column: stock_weekly.trade_date
ALTER TABLE `stock_weekly` MODIFY COLUMN `trade_date` VARCHAR(10) NOT NULL  COMMENT '交易日期';

-- modify_column: stock_weekly.ts_code
ALTER TABLE `stock_weekly` MODIFY COLUMN `ts_code` VARCHAR(20) NOT NULL  COMMENT 'TS代码';

-- modify_column: stock_weekly.vol
ALTER TABLE `stock_weekly` MODIFY COLUMN `vol` FLOAT NULL  COMMENT '成交量（手）';

-- modify_column: stock_weekly.close
ALTER TABLE `stock_weekly` MODIFY COLUMN `close` FLOAT NULL  COMMENT '收盘价';

-- modify_column: stock_weekly.id
ALTER TABLE `stock_weekly` MODIFY COLUMN `id` INTEGER NOT NULL  COMMENT '主键ID';

-- modify_column: stock_weekly.pct_chg
ALTER TABLE `stock_weekly` MODIFY COLUMN `pct_chg` FLOAT NULL  COMMENT '涨跌幅';

-- modify_column: stock_weekly.high
ALTER TABLE `stock_weekly` MODIFY COLUMN `high` FLOAT NULL  COMMENT '最高价';

-- modify_column: stock_weekly.pre_close
ALTER TABLE `stock_weekly` MODIFY COLUMN `pre_close` FLOAT NULL  COMMENT '昨收价';

-- modify_column: stock_weekly.created_at
ALTER TABLE `stock_weekly` MODIFY COLUMN `created_at` DATETIME NULL  COMMENT '创建时间';

-- modify_column: stock_weekly.amount
ALTER TABLE `stock_weekly` MODIFY COLUMN `amount` FLOAT NULL  COMMENT '成交额（千元）';

-- modify_column: stock_weekly.change
ALTER TABLE `stock_weekly` MODIFY COLUMN `change` FLOAT NULL  COMMENT '涨跌额';

-- modify_column: stock_weekly.low
ALTER TABLE `stock_weekly` MODIFY COLUMN `low` FLOAT NULL  COMMENT '最低价';

-- drop_index: stock_weekly.PRIMARY
ALTER TABLE `stock_weekly` DROP INDEX `PRIMARY`;

-- modify_column: stock_favorite.ts_code
ALTER TABLE `stock_favorite` MODIFY COLUMN `ts_code` VARCHAR(20) NOT NULL  COMMENT 'TS代码';

-- modify_column: stock_favorite.id
ALTER TABLE `stock_favorite` MODIFY COLUMN `id` INTEGER NOT NULL  COMMENT '主键ID';

-- modify_column: stock_favorite.created_at
ALTER TABLE `stock_favorite` MODIFY COLUMN `created_at` DATETIME NULL  COMMENT '创建时间';

-- modify_column: stock_favorite.user_id
ALTER TABLE `stock_favorite` MODIFY COLUMN `user_id` INTEGER NULL  COMMENT '用户ID';

-- modify_column: stock_favorite.notes
ALTER TABLE `stock_favorite` MODIFY COLUMN `notes` TEXT NULL  COMMENT '备注';

-- drop_index: stock_favorite.PRIMARY
ALTER TABLE `stock_favorite` DROP INDEX `PRIMARY`;

-- modify_column: users.avatar
ALTER TABLE `users` MODIFY COLUMN `avatar` VARCHAR(500) NULL  COMMENT '头像URL';

-- modify_column: users.gender
ALTER TABLE `users` MODIFY COLUMN `gender` INTEGER NULL  COMMENT '性别：0未知，1男，2女';

-- modify_column: users.openid
ALTER TABLE `users` MODIFY COLUMN `openid` VARCHAR(100) NOT NULL  COMMENT '微信OpenID';

-- modify_column: users.updated_at
ALTER TABLE `users` MODIFY COLUMN `updated_at` DATETIME NULL  COMMENT '更新时间';

-- modify_column: users.unionid
ALTER TABLE `users` MODIFY COLUMN `unionid` VARCHAR(100) NULL  COMMENT '微信UnionID';

-- modify_column: users.country
ALTER TABLE `users` MODIFY COLUMN `country` VARCHAR(50) NULL  COMMENT '国家';

-- modify_column: users.city
ALTER TABLE `users` MODIFY COLUMN `city` VARCHAR(50) NULL  COMMENT '城市';

-- modify_column: users.id
ALTER TABLE `users` MODIFY COLUMN `id` INTEGER NOT NULL  COMMENT '主键ID';

-- modify_column: users.last_login_at
ALTER TABLE `users` MODIFY COLUMN `last_login_at` DATETIME NULL  COMMENT '最后登录时间';

-- modify_column: users.province
ALTER TABLE `users` MODIFY COLUMN `province` VARCHAR(50) NULL  COMMENT '省份';

-- modify_column: users.created_at
ALTER TABLE `users` MODIFY COLUMN `created_at` DATETIME NULL  COMMENT '创建时间';

-- modify_column: users.nickname
ALTER TABLE `users` MODIFY COLUMN `nickname` VARCHAR(100) NULL  COMMENT '昵称';

-- modify_column: users.language
ALTER TABLE `users` MODIFY COLUMN `language` VARCHAR(20) NULL  COMMENT '语言';

-- drop_index: users.PRIMARY
ALTER TABLE `users` DROP INDEX `PRIMARY`;

-- modify_column: stock_ipo.issue_date
ALTER TABLE `stock_ipo` MODIFY COLUMN `issue_date` VARCHAR(10) COLLATE "utf8mb4_unicode_ci" NULL  COMMENT '上市日期';

-- modify_column: stock_ipo.funds
ALTER TABLE `stock_ipo` MODIFY COLUMN `funds` FLOAT NULL  COMMENT '募集资金（亿元）';

-- modify_column: stock_ipo.ts_code
ALTER TABLE `stock_ipo` MODIFY COLUMN `ts_code` VARCHAR(20) COLLATE "utf8mb4_unicode_ci" NOT NULL  COMMENT 'TS股票代码';

-- modify_column: stock_ipo.sub_code
ALTER TABLE `stock_ipo` MODIFY COLUMN `sub_code` VARCHAR(20) COLLATE "utf8mb4_unicode_ci" NULL  COMMENT '申购代码';

-- modify_column: stock_ipo.updated_at
ALTER TABLE `stock_ipo` MODIFY COLUMN `updated_at` DATETIME NULL  COMMENT '更新时间';

-- modify_column: stock_ipo.ballot
ALTER TABLE `stock_ipo` MODIFY COLUMN `ballot` FLOAT NULL  COMMENT '中签率';

-- modify_column: stock_ipo.id
ALTER TABLE `stock_ipo` MODIFY COLUMN `id` INTEGER NOT NULL  ;

-- modify_column: stock_ipo.created_at
ALTER TABLE `stock_ipo` MODIFY COLUMN `created_at` DATETIME NULL  COMMENT '创建时间';

-- modify_column: stock_ipo.amount
ALTER TABLE `stock_ipo` MODIFY COLUMN `amount` FLOAT NULL  COMMENT '发行总量（万股）';

-- modify_column: stock_ipo.market_amount
ALTER TABLE `stock_ipo` MODIFY COLUMN `market_amount` FLOAT NULL  COMMENT '上网发行总量（万股）';

-- modify_column: stock_ipo.ipo_date
ALTER TABLE `stock_ipo` MODIFY COLUMN `ipo_date` VARCHAR(10) COLLATE "utf8mb4_unicode_ci" NULL  COMMENT '上网发行日期';

-- modify_column: stock_ipo.name
ALTER TABLE `stock_ipo` MODIFY COLUMN `name` VARCHAR(50) COLLATE "utf8mb4_unicode_ci" NOT NULL  COMMENT '名称';

-- modify_column: stock_ipo.pe
ALTER TABLE `stock_ipo` MODIFY COLUMN `pe` FLOAT NULL  COMMENT '市盈率';

-- modify_column: stock_ipo.price
ALTER TABLE `stock_ipo` MODIFY COLUMN `price` FLOAT NULL  COMMENT '发行价格';

-- modify_column: stock_ipo.limit_amount
ALTER TABLE `stock_ipo` MODIFY COLUMN `limit_amount` FLOAT NULL  COMMENT '个人申购上限（万股）';

-- drop_index: stock_ipo.PRIMARY
ALTER TABLE `stock_ipo` DROP INDEX `PRIMARY`;

