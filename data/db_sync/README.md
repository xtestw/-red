# 数据库表结构同步工具

这个工具用于对比本地数据库和远端服务器数据库的表结构差异，并生成对应的SQL同步语句。

## 功能特性

- ✅ 自动对比本地和远端数据库的表结构
- ✅ 检测表、列、索引、主键的差异
- ✅ 生成SQL同步语句
- ✅ 支持通过SSH连接远端服务器
- ✅ 支持SSH密钥和密码认证
- ✅ 使用INFORMATION_SCHEMA获取准确的表结构信息

## 安装依赖

```bash
# 基础依赖（项目已包含）
pip install pymysql sqlalchemy

# SSH支持（可选，但推荐）
pip install paramiko
```

如果不安装paramiko，工具会使用系统的ssh命令，功能相同但可能稍慢。

## 配置

### 方式1：使用配置文件（推荐）

复制配置文件模板：

```bash
cd data/db_sync
cp db_sync_config.json.example db_sync_config.json
```

编辑 `db_sync_config.json`：

```json
{
  "ssh": {
    "user": "root",
    "host": "your-remote-server.com",
    "port": 22,
    "key_file": "/path/to/your/private_key",
    "password": ""
  },
  "remote_db": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "your_password",
    "database": "stock_data"
  }
}
```

**配置说明：**

- `ssh.user`: SSH登录用户名
- `ssh.host`: 远端服务器地址
- `ssh.port`: SSH端口（默认22）
- `ssh.key_file`: SSH私钥文件路径（推荐使用密钥认证）
  - 如果设置为示例路径（如 `/path/to/your/private_key`）或文件不存在，工具会自动使用密码认证
  - 如果不想使用密钥文件，可以设置为 `null` 或删除该字段
- `ssh.password`: SSH密码（如果使用密钥认证，可以留空）
  - 如果 `key_file` 和 `password` 都未配置，工具会在运行时提示输入密码
- `remote_db.host`: 远端数据库主机（通常是localhost，因为数据库在远端服务器上）
- `remote_db.port`: 远端数据库端口（默认3306）
- `remote_db.user`: 远端数据库用户名
- `remote_db.password`: 远端数据库密码
- `remote_db.database`: 远端数据库名称

### 方式2：使用命令行参数

```bash
python db_sync.py \
  --ssh-user root \
  --ssh-host your-remote-server.com \
  --ssh-port 22 \
  --ssh-key /path/to/private_key \
  --remote-db-host localhost \
  --remote-db-port 3306 \
  --remote-db-user root \
  --remote-db-password your_password \
  --remote-db-name stock_data
```

## 使用方法

### 基本使用

```bash
cd data/db_sync
python db_sync.py
```

工具会自动：
1. 连接本地数据库（使用项目配置文件中的配置）
2. 通过SSH连接远端服务器
3. 获取两个数据库的表结构
4. 对比差异
5. 生成SQL文件

### 交互式密码输入（推荐）

如果你不想在配置文件中存储密码，可以使用交互式模式，在运行时手动输入密码：

```bash
python db_sync.py --interactive
```

或者使用简写：

```bash
python db_sync.py -i
```

在交互式模式下：
- 不会读取配置文件中的SSH密码和密钥
- 不会读取配置文件中的数据库密码
- 会在运行时提示你手动输入密码（密码不会显示在屏幕上）

**注意**：使用交互式密码输入需要安装 `paramiko` 库：
```bash
pip install paramiko
```

如果没有安装paramiko，工具会尝试使用系统的ssh命令，但需要：
- 使用SSH密钥认证，或
- 安装 `sshpass` 工具（不推荐，安全性较低）

### 指定输出文件

```bash
python db_sync.py --output sync.sql
```

### 使用配置文件

```bash
python db_sync.py --config db_sync_config.json
```

### 交互式密码输入（不存储密码）

```bash
# 交互式输入SSH和数据库密码
python db_sync.py --interactive

# 或者指定部分参数，其他交互式输入
python db_sync.py --interactive \
  --ssh-host your-server.com \
  --remote-db-name stock_data
```

### 混合使用（命令行参数会覆盖配置文件）

```bash
python db_sync.py \
  --config db_sync_config.json \
  --ssh-host different-server.com \
  --output custom_sync.sql
```

## 执行SQL同步

生成SQL文件后，可以使用 `apply_sync.py` 脚本来执行SQL，更新数据库表结构。

### 基本使用

**执行本地数据库同步：**
```bash
python apply_sync.py db_sync_20240101_120000.sql --target local
```

**执行远端数据库同步：**
```bash
python apply_sync.py db_sync_20240101_120000.sql --target remote
```

### 常用选项

- `--target, -t`: 目标数据库（`local` 或 `remote`），默认是 `local`
- `--dry-run, -d`: 干运行模式，只显示将要执行的SQL，不实际执行
- `--yes, -y`: 跳过确认提示，直接执行
- `--config, -c`: 配置文件路径（默认 `db_sync_config.json`）

### 示例

**预览SQL（不执行）：**
```bash
python apply_sync.py db_sync_20240101_120000.sql --target local --dry-run
```

**直接执行（跳过确认）：**
```bash
python apply_sync.py db_sync_20240101_120000.sql --target local --yes
```

**执行远端数据库同步：**
```bash
python apply_sync.py db_sync_20240101_120000.sql --target remote
```

**使用自定义配置：**
```bash
python apply_sync.py db_sync_20240101_120000.sql --target remote --config custom_config.json
```

### 安全提示

- 执行SQL前会要求确认（除非使用 `--yes` 参数）
- 建议先使用 `--dry-run` 预览将要执行的SQL
- 建议在测试环境先验证SQL的正确性
- 执行前建议备份数据库

## 输出说明

工具会生成一个SQL文件，包含所有需要同步的SQL语句。文件格式如下：

```sql
-- 数据库结构同步SQL
-- 生成时间: 2024-01-01 12:00:00
-- 本地数据库: stock_data
-- 远端数据库: stock_data

-- 差异列表:
-- column_missing_remote: stock_basic.new_column
-- index_missing_remote: stock_daily.idx_new_index

-- SQL语句:

-- add_column: stock_basic.new_column
ALTER TABLE `stock_basic` ADD COLUMN `new_column` VARCHAR(50) NULL DEFAULT NULL COMMENT '新列';

-- add_index: stock_daily.idx_new_index
ALTER TABLE `stock_daily` ADD INDEX `idx_new_index` (`ts_code`);
```

## 差异类型

工具会检测以下类型的差异：

- `table_missing_remote`: 表在本地存在但远端不存在（需要创建表）
- `table_missing_local`: 表在远端存在但本地不存在（需要删除表）
- `column_missing_remote`: 列在本地存在但远端不存在（需要添加列）
- `column_missing_local`: 列在远端存在但本地不存在（需要删除列）
- `column_different`: 列的类型或属性不同（需要修改列）
- `index_missing_remote`: 索引在本地存在但远端不存在（需要添加索引）
- `index_missing_local`: 索引在远端存在但本地不存在（需要删除索引）
- `primary_key_different`: 主键不同（需要修改主键）

## 注意事项

1. **SSH连接**: 确保能够通过SSH连接到远端服务器
2. **数据库权限**: 确保SSH用户能够在远端服务器上执行MySQL命令
3. **数据库访问**: 远端数据库应该允许从localhost连接（因为是在远端服务器上执行MySQL命令）
4. **密码安全**: 
   - 配置文件包含敏感信息，不要提交到版本控制系统
   - 推荐使用交互式模式（`--interactive`）手动输入密码，避免在配置文件中存储密码
   - 推荐使用SSH密钥认证而不是密码认证
5. **SQL执行**: 生成的SQL文件需要手动审查后再执行，确保不会丢失数据
6. **交互式密码输入**: 
   - 需要安装 `paramiko` 库：`pip install paramiko`
   - 如果没有paramiko，可以使用SSH密钥认证或安装sshpass工具

## 手动SSH登录方式

如果自动SSH连接有问题，可以手动登录远端服务器，然后执行以下命令获取表结构：

```bash
# SSH登录
ssh user@remote-server.com

# 连接数据库
mysql -h localhost -u root -p database_name

# 查看所有表
SHOW TABLES;

# 查看表结构
SHOW CREATE TABLE table_name;

# 或者使用INFORMATION_SCHEMA
SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'database_name' 
AND TABLE_NAME = 'table_name';
```

## 故障排除

### SSH连接失败

- 检查SSH配置是否正确
- 检查网络连接
- 检查SSH密钥权限（应该是600）
- 如果配置文件中使用了示例密钥路径（如 `/path/to/your/private_key`），工具会自动使用密码认证
- 如果密钥文件不存在，工具会自动回退到密码认证，并提示输入密码
- 尝试手动SSH连接测试

### 数据库连接失败

- 检查远端数据库配置
- 确认数据库服务正在运行
- 检查数据库用户权限
- 确认数据库名称正确

### 无法获取表结构

- 检查MySQL命令是否可用
- 检查数据库用户是否有INFORMATION_SCHEMA访问权限
- 查看错误信息，可能需要调整SQL查询

## 完整工作流程示例

### 步骤1：生成SQL同步文件

```bash
cd data/db_sync
python db_sync.py --interactive
```

这会生成一个SQL文件，例如：`db_sync_20240101_120000.sql`

### 步骤2：预览SQL（可选）

```bash
python apply_sync.py db_sync_20240101_120000.sql --target local --dry-run
```

### 步骤3：执行SQL同步

**本地数据库：**
```bash
python apply_sync.py db_sync_20240101_120000.sql --target local
```

**远端数据库：**
```bash
python apply_sync.py db_sync_20240101_120000.sql --target remote
```

## 示例

### 示例1：基本同步

```bash
# 配置好db_sync_config.json后
python db_sync.py

# 输出：
# ============================================================
# 数据库表结构同步工具
# ============================================================
# 本地数据库: stock_data @ localhost
# 远端数据库: stock_data @ remote-server.com:localhost
# ============================================================
# 
# [1/4] 连接本地数据库...
# ✓ 本地数据库连接成功
# 
# [2/4] 加载本地数据库表结构...
# ✓ 找到 20 个表
# 
# [3/4] 连接远端数据库（通过SSH）...
# ✓ 找到 18 个表
# 
# [4/4] 对比数据库结构...
# ✓ 发现 5 处差异
# 
# ✓ SQL文件已生成: db_sync_20240101_120000.sql
```

### 示例2：指定输出文件

```bash
python db_sync.py --output my_sync.sql
```

### 示例3：使用命令行参数

```bash
python db_sync.py \
  --ssh-user deploy \
  --ssh-host prod.example.com \
  --ssh-key ~/.ssh/id_rsa \
  --remote-db-user dbuser \
  --remote-db-password secret \
  --remote-db-name production_db \
  --output prod_sync.sql
```

### 示例4：交互式密码输入（推荐用于生产环境）

```bash
# 交互式输入密码，不在配置文件中存储
python db_sync.py --interactive \
  --ssh-host prod.example.com \
  --remote-db-name production_db

# 运行时会提示输入：
# - SSH密码
# - 远端数据库密码
```

## 安全建议

1. 使用SSH密钥认证而不是密码
2. 限制SSH密钥的权限：`chmod 600 ~/.ssh/id_rsa`
3. 不要将配置文件提交到Git
4. 在生产环境使用前，先在测试环境验证
5. 执行SQL前仔细审查生成的SQL文件
