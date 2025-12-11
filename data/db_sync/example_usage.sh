#!/bin/bash
# 数据库同步工具使用示例

# 示例1: 使用配置文件
python db_sync.py --config db_sync_config.json

# 示例2: 交互式密码输入（推荐，不在配置文件中存储密码）
python db_sync.py --interactive \
  --ssh-host your-server.com \
  --remote-db-name stock_data

# 示例3: 使用命令行参数
python db_sync.py \
  --ssh-user root \
  --ssh-host your-server.com \
  --ssh-key ~/.ssh/id_rsa \
  --remote-db-host localhost \
  --remote-db-port 3306 \
  --remote-db-user root \
  --remote-db-password your_password \
  --remote-db-name stock_data \
  --output sync.sql

# 示例4: 混合使用（配置文件 + 命令行覆盖）
python db_sync.py \
  --config db_sync_config.json \
  --ssh-host different-server.com \
  --output custom_sync.sql

# 示例5: 交互式模式 + 部分参数
python db_sync.py --interactive \
  --ssh-user deploy \
  --ssh-host prod.example.com \
  --remote-db-name production_db \
  --output prod_sync.sql

# ============================================================
# 执行SQL同步脚本 (apply_sync.py)
# ============================================================

# 示例6: 预览SQL（不执行）
python apply_sync.py db_sync_20240101_120000.sql --target local --dry-run

# 示例7: 执行本地数据库同步
python apply_sync.py db_sync_20240101_120000.sql --target local

# 示例8: 执行远端数据库同步
python apply_sync.py db_sync_20240101_120000.sql --target remote

# 示例9: 直接执行（跳过确认）
python apply_sync.py db_sync_20240101_120000.sql --target local --yes

# 示例10: 使用自定义配置执行远端同步
python apply_sync.py db_sync_20240101_120000.sql --target remote --config custom_config.json
