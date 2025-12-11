-- 添加用户查询表（custom_query）
-- 使用方法: mysql -u root -p stock_data < add_custom_query_table.sql

USE stock_data;

-- 用户查询表（存储查询条件和生成的SQL）
CREATE TABLE IF NOT EXISTS `custom_query` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` int(11) DEFAULT NULL COMMENT '用户ID（可选）',
  `query_description` text NOT NULL COMMENT '查询条件描述',
  `generated_sql` text NOT NULL COMMENT '生成的SQL查询语句',
  `missing_tables` text COMMENT '缺失的数据表（JSON格式）',
  `missing_fields` text COMMENT '缺失的字段（JSON格式）',
  `status` varchar(20) DEFAULT 'pending' COMMENT '状态：pending-待执行，success-成功，failed-失败',
  `error_message` text COMMENT '错误信息',
  `execution_count` int(11) DEFAULT 0 COMMENT '执行次数',
  `last_executed_at` datetime DEFAULT NULL COMMENT '最后执行时间',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_at` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户查询表';

