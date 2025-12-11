# 快速开始指南

## 完整工作流程

### 1. 生成SQL同步文件

```bash
cd data/db_sync

# 方式1: 使用交互式模式（推荐，不存储密码）
python db_sync.py --interactive

# 方式2: 使用配置文件
python db_sync.py --config db_sync_config.json
```

这会生成一个SQL文件，例如：`db_sync_20240101_120000.sql`

### 2. 预览SQL（强烈推荐）

在执行SQL之前，先预览一下将要执行的SQL语句：

```bash
python apply_sync.py db_sync_20240101_120000.sql --target local --dry-run
```

这会显示所有将要执行的SQL语句，但不会实际执行。

### 3. 执行SQL同步

**更新本地数据库：**
```bash
python apply_sync.py db_sync_20240101_120000.sql --target local
```

**更新远端数据库：**
```bash
python apply_sync.py db_sync_20240101_120000.sql --target remote
```

## 常用场景

### 场景1：本地开发环境同步到远端生产环境

```bash
# 1. 对比本地和生产环境的差异
python db_sync.py --interactive --output prod_sync.sql

# 2. 预览SQL
python apply_sync.py prod_sync.sql --target remote --dry-run

# 3. 执行同步
python apply_sync.py prod_sync.sql --target remote
```

### 场景2：快速同步本地数据库

```bash
# 1. 生成SQL（使用本地配置）
python db_sync.py --output local_sync.sql

# 2. 直接执行（跳过确认）
python apply_sync.py local_sync.sql --target local --yes
```

### 场景3：批量处理多个环境

```bash
# 生成SQL文件
python db_sync.py --output sync.sql

# 同步到测试环境
python apply_sync.py sync.sql --target remote --config test_config.json

# 同步到生产环境
python apply_sync.py sync.sql --target remote --config prod_config.json
```

## 安全建议

1. **始终先预览**：使用 `--dry-run` 预览SQL
2. **备份数据库**：执行前备份数据库
3. **测试环境验证**：先在测试环境验证SQL
4. **审查SQL文件**：执行前仔细检查生成的SQL文件
5. **使用交互式模式**：避免在配置文件中存储密码

## 故障排除

### SQL执行失败

如果某些SQL语句执行失败：

1. 查看错误信息
2. 检查SQL文件中的对应语句
3. 手动执行失败的SQL语句
4. 修复问题后重新执行

### 连接问题

- 检查网络连接
- 验证SSH配置
- 确认数据库服务正在运行
- 检查用户权限

## 提示

- 使用 `--dry-run` 可以安全地预览SQL
- 使用 `--yes` 可以跳过确认（适合自动化脚本）
- 使用 `--interactive` 可以避免在配置文件中存储密码
- SQL文件可以手动编辑，删除不需要的语句
