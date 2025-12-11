#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
数据库表结构同步工具
对比本地数据库和远端服务器数据库的表结构差异，生成对应的SQL语句
"""
import sys
import os
import json
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import pymysql
    from sqlalchemy import create_engine, inspect, text
except ImportError as e:
    print(f"错误: 缺少必要的依赖包: {e}")
    print("请运行: pip install pymysql sqlalchemy")
    sys.exit(1)

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False
    print("警告: paramiko未安装，将使用subprocess调用ssh命令")
    print("如需更好的SSH支持，请运行: pip install paramiko")


class DatabaseStructure:
    """数据库表结构信息"""
    
    def __init__(self, connection_config: Dict):
        self.config = connection_config
        self.engine = None
        self.tables = {}
        self.indexes = {}
        
    def connect(self):
        """连接数据库"""
        try:
            connection_string = (
                f"mysql+pymysql://{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
                f"?charset={self.config.get('charset', 'utf8mb4')}"
            )
            self.engine = create_engine(connection_string, pool_pre_ping=True)
            return True
        except Exception as e:
            print(f"连接数据库失败: {e}")
            return False
    
    def get_table_structure(self, table_name: str) -> Dict:
        """获取表结构"""
        if not self.engine:
            return {}
        
        inspector = inspect(self.engine)
        columns = {}
        
        # 获取列信息
        for column in inspector.get_columns(table_name):
            col_info = {
                'name': column['name'],
                'type': str(column['type']),
                'nullable': column['nullable'],
                'default': column.get('default'),
                'autoincrement': column.get('autoincrement', False),
                'comment': column.get('comment', '')
            }
            columns[column['name']] = col_info
        
        # 获取主键
        pk_constraint = inspector.get_pk_constraint(table_name)
        primary_keys = pk_constraint.get('constrained_columns', [])
        
        # 获取索引
        indexes = {}
        for index in inspector.get_indexes(table_name):
            index_name = index['name']
            indexes[index_name] = {
                'columns': index['column_names'],
                'unique': index['unique'],
                'name': index_name
            }
        
        # 获取外键
        foreign_keys = []
        for fk in inspector.get_foreign_keys(table_name):
            foreign_keys.append({
                'name': fk.get('name', ''),
                'constrained_columns': fk['constrained_columns'],
                'referred_table': fk['referred_table'],
                'referred_columns': fk['referred_columns']
            })
        
        return {
            'columns': columns,
            'primary_keys': primary_keys,
            'indexes': indexes,
            'foreign_keys': foreign_keys
        }
    
    def get_all_tables(self) -> List[str]:
        """获取所有表名"""
        if not self.engine:
            return []
        
        inspector = inspect(self.engine)
        return inspector.get_table_names()
    
    def load_structure(self):
        """加载所有表结构"""
        tables = self.get_all_tables()
        for table in tables:
            self.tables[table] = self.get_table_structure(table)
        return self.tables


class RemoteDatabaseStructure:
    """远端数据库表结构（通过SSH连接）"""
    
    def __init__(self, ssh_config: Dict, db_config: Dict):
        self.ssh_config = ssh_config
        self.db_config = db_config
        self.tables = {}
        
    def get_structure_via_ssh_command(self) -> Dict:
        """通过SSH命令获取数据库结构（使用INFORMATION_SCHEMA）"""
        # 使用INFORMATION_SCHEMA查询表结构，更可靠
        sql_script = f"""
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = '{self.db_config['database']}' 
AND TABLE_TYPE = 'BASE TABLE';
"""
        
        # 将SQL保存到临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(sql_script)
            temp_sql_file = f.name
        
        try:
            # 构建MySQL命令
            password = self.db_config['password'].replace("'", "'\"'\"'") if self.db_config.get('password') else ''
            mysql_cmd = (
                f"mysql -h{self.db_config['host']} -P{self.db_config['port']} "
                f"-u{self.db_config['user']} -p'{password}' "
                f"{self.db_config['database']} < {temp_sql_file}"
            )
            
            # 构建SSH命令
            ssh_cmd = [
                'ssh',
                f"{self.ssh_config['user']}@{self.ssh_config['host']}",
                '-p', str(self.ssh_config.get('port', 22)),
                '-o', 'StrictHostKeyChecking=no',  # 跳过主机密钥检查
                mysql_cmd
            ]
            
            # 如果使用密钥认证（检查文件是否存在）
            key_file = self.ssh_config.get('key_file')
            if key_file:
                # 检查是否是示例路径或文件不存在
                if '/path/to/your/private_key' in key_file or 'your/private_key' in key_file:
                    # 示例路径，忽略
                    key_file = None
                elif not os.path.exists(key_file) or not os.path.isfile(key_file):
                    # 文件不存在，忽略
                    key_file = None
                
                if key_file:
                    ssh_cmd.extend(['-i', key_file])
            
            # 如果使用密码认证，尝试使用sshpass（如果可用）
            if not key_file and self.ssh_config.get('password'):
                # 检查是否有sshpass
                try:
                    subprocess.run(['which', 'sshpass'], capture_output=True, check=True)
                    # 使用sshpass传递密码
                    ssh_cmd = [
                        'sshpass', '-p', self.ssh_config['password'],
                        'ssh',
                        f"{self.ssh_config['user']}@{self.ssh_config['host']}",
                        '-p', str(self.ssh_config.get('port', 22)),
                        '-o', 'StrictHostKeyChecking=no',
                        mysql_cmd
                    ]
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print("错误: 使用密码认证需要安装sshpass或paramiko")
                    print("安装sshpass: brew install sshpass (macOS) 或 apt-get install sshpass (Linux)")
                    print("或安装paramiko: pip install paramiko")
                    return {}
            
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"SSH命令执行失败: {result.stderr}")
                return {}
            
            # 解析表名（从输出中提取）
            lines = result.stdout.strip().split('\n')
            table_names = [line.strip() for line in lines if line.strip() and not line.startswith('TABLE_NAME')]
            
            # 对每个表获取结构
            tables = {}
            for table_name in table_names:
                if table_name:
                    table_structure = self._get_table_structure_via_ssh(table_name)
                    if table_structure:
                        tables[table_name] = table_structure
            
            return tables
            
        except subprocess.TimeoutExpired:
            print("SSH连接超时")
            return {}
        except Exception as e:
            print(f"通过SSH获取数据库结构失败: {e}")
            return {}
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_sql_file)
            except:
                pass
    
    def _get_table_structure_via_ssh(self, table_name: str) -> Dict:
        """通过SSH获取单个表的结构（使用INFORMATION_SCHEMA）"""
        # 查询列信息
        columns_sql = f"""
SELECT 
    COLUMN_NAME,
    COLUMN_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    EXTRA,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = '{self.db_config['database']}' 
AND TABLE_NAME = '{table_name}'
ORDER BY ORDINAL_POSITION;
"""
        
        # 查询主键
        pk_sql = f"""
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = '{self.db_config['database']}' 
AND TABLE_NAME = '{table_name}'
AND CONSTRAINT_NAME = 'PRIMARY'
ORDER BY ORDINAL_POSITION;
"""
        
        # 查询索引
        index_sql = f"""
SELECT 
    INDEX_NAME,
    GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) as COLUMNS,
    NON_UNIQUE
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = '{self.db_config['database']}' 
AND TABLE_NAME = '{table_name}'
GROUP BY INDEX_NAME, NON_UNIQUE;
"""
        
        columns = {}
        primary_keys = []
        indexes = {}
        
        try:
            # 获取列信息
            columns_result = self._execute_sql_via_ssh(columns_sql)
            for row in columns_result:
                if len(row) >= 6:
                    col_name = row[0]
                    col_type = row[1]
                    is_nullable = row[2] == 'YES'
                    col_default = row[3]
                    extra = row[4]
                    col_comment = row[5] or ''
                    
                    columns[col_name] = {
                        'name': col_name,
                        'type': col_type,
                        'nullable': is_nullable,
                        'default': col_default,
                        'autoincrement': 'auto_increment' in (extra or ''),
                        'comment': col_comment
                    }
            
            # 获取主键
            pk_result = self._execute_sql_via_ssh(pk_sql)
            primary_keys = [row[0] for row in pk_result if row]
            
            # 获取索引
            index_result = self._execute_sql_via_ssh(index_sql)
            for row in index_result:
                if len(row) >= 3:
                    idx_name = row[0]
                    idx_cols = row[1].split(',') if row[1] else []
                    is_unique = row[2] == '0'
                    
                    indexes[idx_name] = {
                        'columns': idx_cols,
                        'unique': is_unique,
                        'name': idx_name
                    }
            
            return {
                'columns': columns,
                'primary_keys': primary_keys,
                'indexes': indexes,
                'foreign_keys': []  # 外键暂时不处理
            }
            
        except Exception as e:
            print(f"获取表 {table_name} 结构失败: {e}")
            return {}
    
    def _execute_sql_via_ssh(self, sql: str) -> List[Tuple]:
        """通过SSH执行SQL并返回结果"""
        # 将SQL保存到临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as f:
            f.write(sql)
            temp_sql_file = f.name
        
        try:
            # 构建SSH命令（转义密码中的特殊字符）
            password = self.db_config['password'].replace("'", "'\"'\"'") if self.db_config.get('password') else ''
            mysql_cmd = (
                f"mysql -h{self.db_config['host']} -P{self.db_config['port']} "
                f"-u{self.db_config['user']} -p'{password}' "
                f"{self.db_config['database']} -N -e \"$(cat {temp_sql_file})\""
            )
            
            ssh_cmd = [
                'ssh',
                f"{self.ssh_config['user']}@{self.ssh_config['host']}",
                '-p', str(self.ssh_config.get('port', 22)),
                mysql_cmd
            ]
            
            if 'key_file' in self.ssh_config:
                ssh_cmd.extend(['-i', self.ssh_config['key_file']])
            
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return []
            
            # 解析结果（制表符分隔）
            rows = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    rows.append(tuple(line.split('\t')))
            
            return rows
            
        except Exception as e:
            print(f"执行SQL失败: {e}")
            return []
        finally:
            try:
                os.unlink(temp_sql_file)
            except:
                pass
    
    def get_structure_via_paramiko(self) -> Dict:
        """通过paramiko获取数据库结构"""
        if not HAS_PARAMIKO:
            return self.get_structure_via_ssh_command()
        
        try:
            # 创建SSH客户端
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 连接SSH
            connect_kwargs = {
                'hostname': self.ssh_config['host'],
                'port': self.ssh_config.get('port', 22),
                'username': self.ssh_config['user'],
                'timeout': 30
            }
            
            # 检查密钥文件是否存在且有效
            key_file = self.ssh_config.get('key_file')
            if key_file and os.path.exists(key_file) and os.path.isfile(key_file):
                # 检查是否是示例路径（不应该使用）
                if '/path/to/your/private_key' not in key_file and 'your/private_key' not in key_file:
                    connect_kwargs['key_filename'] = key_file
                else:
                    # 示例路径，忽略它
                    key_file = None
            
            # 如果没有有效的密钥文件，使用密码认证
            if 'key_filename' not in connect_kwargs:
                if self.ssh_config.get('password'):
                    connect_kwargs['password'] = self.ssh_config['password']
                else:
                    # 如果没有密码，抛出异常，让调用者处理
                    raise ValueError("需要SSH密钥文件或密码来进行认证")
            
            ssh.connect(**connect_kwargs)
            
            # 使用INFORMATION_SCHEMA查询表列表
            password = self.db_config['password'].replace("'", "'\"'\"'") if self.db_config.get('password') else ''
            sql = f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{self.db_config['database']}' AND TABLE_TYPE = 'BASE TABLE';"
            mysql_cmd = (
                f"mysql -h{self.db_config['host']} -P{self.db_config['port']} "
                f"-u{self.db_config['user']} -p'{password}' "
                f"{self.db_config['database']} -N -e \"{sql}\""
            )
            
            stdin, stdout, stderr = ssh.exec_command(mysql_cmd)
            
            if stdout.channel.recv_exit_status() != 0:
                error = stderr.read().decode('utf-8')
                print(f"执行MySQL命令失败: {error}")
                ssh.close()
                return {}
            
            # 解析表名
            output = stdout.read().decode('utf-8')
            table_names = [line.strip() for line in output.strip().split('\n') if line.strip()]
            
            # 对每个表获取结构
            tables = {}
            for table_name in table_names:
                table_structure = self._get_table_structure_via_paramiko(ssh, table_name)
                if table_structure:
                    tables[table_name] = table_structure
            
            ssh.close()
            return tables
            
        except ValueError as e:
            # 需要密码但未提供，让调用者处理
            raise
        except Exception as e:
            error_msg = str(e)
            # 如果是密钥文件不存在的错误，提供更友好的提示
            if 'No such file or directory' in error_msg or 'key_filename' in error_msg.lower():
                print(f"SSH连接失败: 密钥文件不存在或无效")
                print("提示: 请检查配置文件中的key_file路径，或使用密码认证")
                raise ValueError("需要有效的SSH密钥文件或密码")
            else:
                print(f"通过paramiko获取数据库结构失败: {e}")
            return {}
    
    def _get_table_structure_via_paramiko(self, ssh: paramiko.SSHClient, table_name: str) -> Dict:
        """通过paramiko获取单个表的结构（使用INFORMATION_SCHEMA）"""
        columns = {}
        primary_keys = []
        indexes = {}
        
        try:
            # 查询列信息
            columns_sql = f"""
SELECT 
    COLUMN_NAME,
    COLUMN_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    EXTRA,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = '{self.db_config['database']}' 
AND TABLE_NAME = '{table_name}'
ORDER BY ORDINAL_POSITION;
"""
            
            password = self.db_config['password'].replace("'", "'\"'\"'") if self.db_config.get('password') else ''
            mysql_cmd = (
                f"mysql -h{self.db_config['host']} -P{self.db_config['port']} "
                f"-u{self.db_config['user']} -p'{password}' "
                f"{self.db_config['database']} -N -e \"{columns_sql}\""
            )
            
            stdin, stdout, stderr = ssh.exec_command(mysql_cmd)
            if stdout.channel.recv_exit_status() == 0:
                output = stdout.read().decode('utf-8')
                for line in output.strip().split('\n'):
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 6:
                            col_name, col_type, is_nullable, col_default, extra, col_comment = parts[:6]
                            columns[col_name] = {
                                'name': col_name,
                                'type': col_type,
                                'nullable': is_nullable == 'YES',
                                'default': col_default if col_default != 'NULL' else None,
                                'autoincrement': 'auto_increment' in (extra or ''),
                                'comment': col_comment or ''
                            }
            
            # 查询主键
            password = self.db_config['password'].replace("'", "'\"'\"'") if self.db_config.get('password') else ''
            pk_sql = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = '{self.db_config['database']}' AND TABLE_NAME = '{table_name}' AND CONSTRAINT_NAME = 'PRIMARY' ORDER BY ORDINAL_POSITION;"
            mysql_cmd = (
                f"mysql -h{self.db_config['host']} -P{self.db_config['port']} "
                f"-u{self.db_config['user']} -p'{password}' "
                f"{self.db_config['database']} -N -e \"{pk_sql}\""
            )
            
            stdin, stdout, stderr = ssh.exec_command(mysql_cmd)
            if stdout.channel.recv_exit_status() == 0:
                output = stdout.read().decode('utf-8')
                primary_keys = [line.strip() for line in output.strip().split('\n') if line.strip()]
            
            # 查询索引
            password = self.db_config['password'].replace("'", "'\"'\"'") if self.db_config.get('password') else ''
            index_sql = f"SELECT INDEX_NAME, GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX), NON_UNIQUE FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = '{self.db_config['database']}' AND TABLE_NAME = '{table_name}' GROUP BY INDEX_NAME, NON_UNIQUE;"
            mysql_cmd = (
                f"mysql -h{self.db_config['host']} -P{self.db_config['port']} "
                f"-u{self.db_config['user']} -p'{password}' "
                f"{self.db_config['database']} -N -e \"{index_sql}\""
            )
            
            stdin, stdout, stderr = ssh.exec_command(mysql_cmd)
            if stdout.channel.recv_exit_status() == 0:
                output = stdout.read().decode('utf-8')
                for line in output.strip().split('\n'):
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            idx_name = parts[0]
                            idx_cols = parts[1].split(',') if parts[1] else []
                            is_unique = parts[2] == '0'
                            indexes[idx_name] = {
                                'columns': idx_cols,
                                'unique': is_unique,
                                'name': idx_name
                            }
            
            return {
                'columns': columns,
                'primary_keys': primary_keys,
                'indexes': indexes,
                'foreign_keys': []
            }
            
        except Exception as e:
            print(f"获取表 {table_name} 结构失败: {e}")
            return {}
    
    def load_structure(self):
        """加载所有表结构"""
        # 优先使用paramiko（支持交互式密码输入）
        if HAS_PARAMIKO:
            self.tables = self.get_structure_via_paramiko()
        else:
            # 如果没有paramiko，检查是否有密码认证
            if self.ssh_config.get('password') and not self.ssh_config.get('key_file'):
                print("警告: 使用密码认证需要paramiko库")
                print("请安装paramiko: pip install paramiko")
                print("或者使用SSH密钥认证")
                # 尝试使用sshpass（如果可用）
                self.tables = self.get_structure_via_ssh_command()
            else:
                self.tables = self.get_structure_via_ssh_command()
        return self.tables


class DatabaseComparator:
    """数据库结构对比器"""
    
    def __init__(self, local_db: DatabaseStructure, remote_db: RemoteDatabaseStructure):
        self.local_db = local_db
        self.remote_db = remote_db
        self.differences = []
        
    def compare(self) -> List[Dict]:
        """对比数据库结构"""
        self.differences = []
        
        local_tables = set(self.local_db.tables.keys())
        remote_tables = set(self.remote_db.tables.keys())
        
        # 找出只在本地存在的表
        only_local = local_tables - remote_tables
        for table in only_local:
            self.differences.append({
                'type': 'table_missing_remote',
                'table': table,
                'action': 'create_table',
                'sql': self._generate_create_table_sql(table, self.local_db.tables[table])
            })
        
        # 找出只在远端存在的表
        only_remote = remote_tables - local_tables
        for table in only_remote:
            self.differences.append({
                'type': 'table_missing_local',
                'table': table,
                'action': 'drop_table',
                'sql': f"DROP TABLE IF EXISTS `{table}`;"
            })
        
        # 对比共同存在的表
        common_tables = local_tables & remote_tables
        for table in common_tables:
            self._compare_table(table, self.local_db.tables[table], self.remote_db.tables[table])
        
        return self.differences
    
    def _compare_table(self, table_name: str, local_structure: Dict, remote_structure: Dict):
        """对比单个表的结构"""
        # 对比列
        local_columns = set(local_structure['columns'].keys())
        remote_columns = set(remote_structure['columns'].keys())
        
        # 只在本地存在的列
        only_local_cols = local_columns - remote_columns
        for col_name in only_local_cols:
            col_info = local_structure['columns'][col_name]
            self.differences.append({
                'type': 'column_missing_remote',
                'table': table_name,
                'column': col_name,
                'action': 'add_column',
                'sql': self._generate_add_column_sql(table_name, col_name, col_info)
            })
        
        # 只在远端存在的列
        only_remote_cols = remote_columns - local_columns
        for col_name in only_remote_cols:
            self.differences.append({
                'type': 'column_missing_local',
                'table': table_name,
                'column': col_name,
                'action': 'drop_column',
                'sql': f"ALTER TABLE `{table_name}` DROP COLUMN `{col_name}`;"
            })
        
        # 对比列的属性
        common_cols = local_columns & remote_columns
        for col_name in common_cols:
            local_col = local_structure['columns'][col_name]
            remote_col = remote_structure['columns'].get(col_name, {})
            
            # 对比类型、可空性等
            if local_col.get('type') != remote_col.get('type') or \
               local_col.get('nullable') != remote_col.get('nullable'):
                self.differences.append({
                    'type': 'column_different',
                    'table': table_name,
                    'column': col_name,
                    'action': 'modify_column',
                    'sql': self._generate_modify_column_sql(table_name, col_name, local_col)
                })
        
        # 对比索引
        self._compare_indexes(table_name, local_structure['indexes'], remote_structure['indexes'])
        
        # 对比主键
        if local_structure['primary_keys'] != remote_structure['primary_keys']:
            self.differences.append({
                'type': 'primary_key_different',
                'table': table_name,
                'action': 'modify_primary_key',
                'sql': self._generate_modify_primary_key_sql(table_name, local_structure['primary_keys'])
            })
    
    def _compare_indexes(self, table_name: str, local_indexes: Dict, remote_indexes: Dict):
        """对比索引"""
        local_index_names = set(local_indexes.keys())
        remote_index_names = set(remote_indexes.keys())
        
        # 只在本地存在的索引
        only_local = local_index_names - remote_index_names
        for idx_name in only_local:
            idx_info = local_indexes[idx_name]
            self.differences.append({
                'type': 'index_missing_remote',
                'table': table_name,
                'index': idx_name,
                'action': 'add_index',
                'sql': self._generate_add_index_sql(table_name, idx_name, idx_info)
            })
        
        # 只在远端存在的索引
        only_remote = remote_index_names - local_index_names
        for idx_name in only_remote:
            self.differences.append({
                'type': 'index_missing_local',
                'table': table_name,
                'index': idx_name,
                'action': 'drop_index',
                'sql': f"ALTER TABLE `{table_name}` DROP INDEX `{idx_name}`;"
            })
    
    def _generate_create_table_sql(self, table_name: str, structure: Dict) -> str:
        """生成创建表的SQL"""
        # 获取CREATE TABLE语句
        if not self.local_db.engine:
            return f"-- CREATE TABLE `{table_name}` (无法生成，请手动创建)"
        
        try:
            with self.local_db.engine.connect() as conn:
                result = conn.execute(text(f"SHOW CREATE TABLE `{table_name}`"))
                row = result.fetchone()
                if row and len(row) >= 2:
                    create_sql = row[1]
                    return f"{create_sql};"
        except Exception as e:
            print(f"获取表 {table_name} 的CREATE TABLE语句失败: {e}")
        
        return f"-- CREATE TABLE `{table_name}` (无法生成，请手动创建)"
    
    def _generate_add_column_sql(self, table_name: str, col_name: str, col_info: Dict) -> str:
        """生成添加列的SQL"""
        type_str = col_info['type']
        nullable = "NULL" if col_info['nullable'] else "NOT NULL"
        default = f"DEFAULT {col_info['default']}" if col_info.get('default') is not None else ""
        comment = f"COMMENT '{col_info['comment']}'" if col_info.get('comment') else ""
        
        return f"ALTER TABLE `{table_name}` ADD COLUMN `{col_name}` {type_str} {nullable} {default} {comment};"
    
    def _generate_modify_column_sql(self, table_name: str, col_name: str, col_info: Dict) -> str:
        """生成修改列的SQL"""
        type_str = col_info['type']
        nullable = "NULL" if col_info['nullable'] else "NOT NULL"
        default = f"DEFAULT {col_info['default']}" if col_info.get('default') is not None else ""
        comment = f"COMMENT '{col_info['comment']}'" if col_info.get('comment') else ""
        
        return f"ALTER TABLE `{table_name}` MODIFY COLUMN `{col_name}` {type_str} {nullable} {default} {comment};"
    
    def _generate_modify_primary_key_sql(self, table_name: str, primary_keys: List[str]) -> str:
        """生成修改主键的SQL"""
        if not primary_keys:
            return f"ALTER TABLE `{table_name}` DROP PRIMARY KEY;"
        
        pk_cols = ', '.join([f"`{pk}`" for pk in primary_keys])
        return f"ALTER TABLE `{table_name}` DROP PRIMARY KEY, ADD PRIMARY KEY ({pk_cols});"
    
    def _generate_add_index_sql(self, table_name: str, idx_name: str, idx_info: Dict) -> str:
        """生成添加索引的SQL"""
        unique = "UNIQUE" if idx_info.get('unique') else ""
        cols = ', '.join([f"`{col}`" for col in idx_info['columns']])
        return f"ALTER TABLE `{table_name}` ADD {unique} INDEX `{idx_name}` ({cols});"
    
    def generate_sql_file(self, output_file: str):
        """生成SQL文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"-- 数据库结构同步SQL\n")
            f.write(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- 本地数据库: {self.local_db.config.get('database')}\n")
            f.write(f"-- 远端数据库: {self.remote_db.db_config.get('database')}\n\n")
            
            if not self.differences:
                f.write("-- 没有发现差异\n")
                return
            
            f.write("-- 差异列表:\n")
            for diff in self.differences:
                f.write(f"-- {diff['type']}: {diff.get('table', '')}.{diff.get('column', diff.get('index', ''))}\n")
            
            f.write("\n-- SQL语句:\n\n")
            
            for diff in self.differences:
                f.write(f"-- {diff['action']}: {diff.get('table', '')}.{diff.get('column', diff.get('index', ''))}\n")
                f.write(f"{diff['sql']}\n\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库表结构同步工具')
    parser.add_argument('--config', '-c', help='配置文件路径', default='db_sync_config.json')
    parser.add_argument('--output', '-o', help='输出SQL文件路径', default=None)
    parser.add_argument('--ssh-user', help='SSH用户名')
    parser.add_argument('--ssh-host', help='SSH主机地址')
    parser.add_argument('--ssh-port', type=int, help='SSH端口', default=22)
    parser.add_argument('--ssh-key', help='SSH私钥文件路径')
    parser.add_argument('--remote-db-host', help='远端数据库主机')
    parser.add_argument('--remote-db-port', type=int, help='远端数据库端口', default=3306)
    parser.add_argument('--remote-db-user', help='远端数据库用户名')
    parser.add_argument('--remote-db-password', help='远端数据库密码')
    parser.add_argument('--remote-db-name', help='远端数据库名称')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互式输入密码（不使用配置文件中的密码）')
    
    args = parser.parse_args()
    
    # 加载配置
    config_file = os.path.join(os.path.dirname(__file__), args.config)
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}
    
    # 从命令行参数或配置文件获取SSH配置
    # 如果使用交互式模式，不读取配置文件中的密码和密钥
    if args.interactive:
        ssh_config = {
            'user': args.ssh_user or config.get('ssh', {}).get('user', 'root'),
            'host': args.ssh_host or config.get('ssh', {}).get('host', ''),
            'port': args.ssh_port or config.get('ssh', {}).get('port', 22),
            'key_file': None,  # 交互式模式下不使用密钥
            'password': None   # 交互式模式下不读取配置中的密码
        }
    else:
        ssh_config = {
            'user': args.ssh_user or config.get('ssh', {}).get('user', 'root'),
            'host': args.ssh_host or config.get('ssh', {}).get('host', ''),
            'port': args.ssh_port or config.get('ssh', {}).get('port', 22),
            'key_file': args.ssh_key or config.get('ssh', {}).get('key_file'),
            'password': config.get('ssh', {}).get('password')
        }
    
    # 从命令行参数或配置文件获取远端数据库配置
    # 如果使用交互式模式，不读取配置文件中的密码
    if args.interactive:
        remote_db_config = {
            'host': args.remote_db_host or config.get('remote_db', {}).get('host', 'localhost'),
            'port': args.remote_db_port or config.get('remote_db', {}).get('port', 3306),
            'user': args.remote_db_user or config.get('remote_db', {}).get('user', 'root'),
            'password': '',  # 交互式模式下不读取配置中的密码
            'database': args.remote_db_name or config.get('remote_db', {}).get('database', '')
        }
    else:
        remote_db_config = {
            'host': args.remote_db_host or config.get('remote_db', {}).get('host', 'localhost'),
            'port': args.remote_db_port or config.get('remote_db', {}).get('port', 3306),
            'user': args.remote_db_user or config.get('remote_db', {}).get('user', 'root'),
            'password': args.remote_db_password or config.get('remote_db', {}).get('password', ''),
            'database': args.remote_db_name or config.get('remote_db', {}).get('database', '')
        }
    
    # 获取本地数据库配置
    try:
        from config import get_mysql_config
        local_db_config = get_mysql_config()
    except Exception as e:
        print(f"获取本地数据库配置失败: {e}")
        sys.exit(1)
    
    # 检查必要参数
    if not ssh_config['host']:
        print("错误: 必须指定SSH主机地址 (--ssh-host 或配置文件)")
        sys.exit(1)
    
    if not remote_db_config['database']:
        print("错误: 必须指定远端数据库名称 (--remote-db-name 或配置文件)")
        sys.exit(1)
    
    print("=" * 60)
    print("数据库表结构同步工具")
    print("=" * 60)
    print(f"本地数据库: {local_db_config['database']} @ {local_db_config['host']}")
    print(f"远端数据库: {remote_db_config['database']} @ {ssh_config['host']}:{remote_db_config['host']}")
    print("=" * 60)
    
    # 连接本地数据库
    print("\n[1/4] 连接本地数据库...")
    local_db = DatabaseStructure(local_db_config)
    if not local_db.connect():
        print("连接本地数据库失败")
        sys.exit(1)
    print("✓ 本地数据库连接成功")
    
    # 加载本地数据库结构
    print("\n[2/4] 加载本地数据库表结构...")
    local_db.load_structure()
    print(f"✓ 找到 {len(local_db.tables)} 个表")
    
    # 连接远端数据库
    print("\n[3/4] 连接远端数据库（通过SSH）...")
    remote_db = RemoteDatabaseStructure(ssh_config, remote_db_config)
    
    # 检查密钥文件是否存在
    import getpass
    key_file = ssh_config.get('key_file')
    has_valid_key = False
    
    if key_file:
        # 检查是否是示例路径
        if '/path/to/your/private_key' in key_file or 'your/private_key' in key_file:
            print(f"警告: 配置文件中使用的是示例密钥路径，将使用密码认证")
            ssh_config['key_file'] = None
        elif os.path.exists(key_file) and os.path.isfile(key_file):
            has_valid_key = True
        else:
            print(f"警告: 密钥文件不存在: {key_file}，将使用密码认证")
            ssh_config['key_file'] = None
    
    # 提示用户输入SSH密码（如果没有有效密钥且没有密码）
    if not has_valid_key and not ssh_config.get('password'):
        print(f"需要SSH密码来连接 {ssh_config['user']}@{ssh_config['host']}")
        ssh_config['password'] = getpass.getpass(f"请输入SSH密码: ")
    
    # 提示用户输入远端数据库密码（如果没有配置）
    if not remote_db_config.get('password'):
        print(f"需要数据库密码来连接 {remote_db_config['user']}@{remote_db_config['host']}")
        remote_db_config['password'] = getpass.getpass(f"请输入远端数据库密码: ")
    
    # 更新remote_db的配置
    remote_db.db_config = remote_db_config
    remote_db.ssh_config = ssh_config
    
    try:
        remote_db.load_structure()
    except ValueError as e:
        # 需要密码但未提供，再次提示
        if '需要有效的SSH密钥文件或密码' in str(e) or '需要SSH密钥文件或密码' in str(e):
            if not ssh_config.get('password'):
                print(f"\n需要SSH密码来连接 {ssh_config['user']}@{ssh_config['host']}")
                ssh_config['password'] = getpass.getpass(f"请输入SSH密码: ")
                remote_db.ssh_config = ssh_config
                # 重试
                try:
                    remote_db.load_structure()
                except Exception as retry_e:
                    print(f"重试连接失败: {retry_e}")
                    sys.exit(1)
        else:
            print(f"连接失败: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"连接远端数据库失败: {e}")
        sys.exit(1)
    
    if not remote_db.tables:
        print("警告: 未能获取远端数据库表结构，请检查SSH连接和数据库配置")
        print("提示: 可以通过SSH手动登录服务器，然后运行以下命令获取表结构:")
        print(f"  mysql -h{remote_db_config['host']} -u{remote_db_config['user']} -p {remote_db_config['database']} -e 'SHOW TABLES;'")
        sys.exit(1)
    print(f"✓ 找到 {len(remote_db.tables)} 个表")
    
    # 对比数据库结构
    print("\n[4/4] 对比数据库结构...")
    comparator = DatabaseComparator(local_db, remote_db)
    differences = comparator.compare()
    
    if not differences:
        print("✓ 没有发现差异，数据库结构一致")
        return
    
    print(f"✓ 发现 {len(differences)} 处差异")
    
    # 生成SQL文件
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(os.path.dirname(__file__), f'db_sync_{timestamp}.sql')
    
    comparator.generate_sql_file(output_file)
    print(f"\n✓ SQL文件已生成: {output_file}")
    
    # 显示差异摘要
    print("\n差异摘要:")
    print("-" * 60)
    for diff in differences:
        print(f"  [{diff['type']}] {diff.get('table', '')}.{diff.get('column', diff.get('index', ''))}")
    print("-" * 60)


if __name__ == '__main__':
    main()
