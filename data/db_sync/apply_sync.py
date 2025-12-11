#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
数据库表结构同步脚本执行工具
执行db_sync.py生成的SQL文件，更新数据库表结构
"""
import sys
import os
import re
import json
import argparse
from typing import List, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import pymysql
    from sqlalchemy import create_engine, text
except ImportError as e:
    print(f"错误: 缺少必要的依赖包: {e}")
    print("请运行: pip install pymysql sqlalchemy")
    sys.exit(1)

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False


class SQLExecutor:
    """SQL执行器"""
    
    def __init__(self, db_config: dict, ssh_config: Optional[dict] = None):
        self.db_config = db_config
        self.ssh_config = ssh_config
        self.engine = None
        self.connection = None
        
    def connect_local(self):
        """连接本地数据库"""
        try:
            connection_string = (
                f"mysql+pymysql://{self.db_config['user']}:{self.db_config['password']}"
                f"@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
                f"?charset={self.db_config.get('charset', 'utf8mb4')}"
            )
            self.engine = create_engine(connection_string, pool_pre_ping=True)
            self.connection = self.engine.connect()
            return True
        except Exception as e:
            print(f"连接本地数据库失败: {e}")
            return False
    
    def connect_remote(self):
        """通过SSH连接远端数据库"""
        if not self.ssh_config:
            print("错误: 需要SSH配置来连接远端数据库")
            return False
        
        if HAS_PARAMIKO:
            return self._connect_remote_via_paramiko()
        else:
            print("错误: 连接远端数据库需要paramiko库")
            print("请运行: pip install paramiko")
            return False
    
    def _connect_remote_via_paramiko(self):
        """通过paramiko连接远端数据库"""
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
            
            # 检查密钥文件
            key_file = self.ssh_config.get('key_file')
            if key_file and os.path.exists(key_file) and os.path.isfile(key_file):
                if '/path/to/your/private_key' not in key_file:
                    connect_kwargs['key_filename'] = key_file
            
            if 'key_filename' not in connect_kwargs:
                if self.ssh_config.get('password'):
                    connect_kwargs['password'] = self.ssh_config['password']
                else:
                    raise ValueError("需要SSH密钥文件或密码")
            
            ssh.connect(**connect_kwargs)
            self.ssh = ssh
            return True
            
        except Exception as e:
            print(f"通过SSH连接失败: {e}")
            return False
    
    def execute_sql_file(self, sql_file: str, dry_run: bool = False) -> dict:
        """执行SQL文件"""
        if not os.path.exists(sql_file):
            print(f"错误: SQL文件不存在: {sql_file}")
            return {'success': False, 'executed': 0, 'failed': 0, 'errors': []}
        
        # 读取SQL文件
        with open(sql_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析SQL语句（按分号分割，但要注意注释和字符串中的分号）
        sql_statements = self._parse_sql_statements(content)
        
        if not sql_statements:
            print("警告: 没有找到可执行的SQL语句")
            return {'success': True, 'executed': 0, 'failed': 0, 'errors': []}
        
        print(f"找到 {len(sql_statements)} 条SQL语句")
        
        if dry_run:
            print("\n[DRY RUN模式] 将执行以下SQL语句:")
            print("=" * 60)
            for i, sql in enumerate(sql_statements, 1):
                print(f"\n-- 语句 {i}:")
                print(sql[:200] + "..." if len(sql) > 200 else sql)
            print("=" * 60)
            return {'success': True, 'executed': len(sql_statements), 'failed': 0, 'errors': []}
        
        # 执行SQL
        executed = 0
        failed = 0
        errors = []
        
        for i, sql in enumerate(sql_statements, 1):
            sql = sql.strip()
            if not sql or sql.startswith('--'):
                continue
            
            try:
                if self.ssh_config:
                    # 通过SSH执行
                    self._execute_sql_via_ssh(sql)
                else:
                    # 本地执行
                    with self.connection.begin():
                        self.connection.execute(text(sql))
                
                executed += 1
                print(f"✓ [{i}/{len(sql_statements)}] 执行成功")
                
            except Exception as e:
                failed += 1
                error_msg = f"语句 {i} 执行失败: {str(e)}"
                errors.append(error_msg)
                print(f"✗ [{i}/{len(sql_statements)}] {error_msg}")
                print(f"  SQL: {sql[:100]}...")
        
        return {
            'success': failed == 0,
            'executed': executed,
            'failed': failed,
            'errors': errors
        }
    
    def _parse_sql_statements(self, content: str) -> List[str]:
        """解析SQL语句（处理注释和字符串）"""
        statements = []
        lines = content.split('\n')
        current_statement = ""
        in_string = False
        string_char = None
        in_multiline_comment = False
        
        for line in lines:
            line = line.rstrip()  # 移除行尾空白
            
            # 跳过空行
            if not line.strip():
                if current_statement:
                    current_statement += '\n'
                continue
            
            # 跳过单行注释
            stripped = line.strip()
            if stripped.startswith('--'):
                if current_statement:
                    current_statement += '\n'
                continue
            
            # 处理多行注释
            i = 0
            while i < len(line):
                char = line[i]
                next_char = line[i + 1] if i + 1 < len(line) else ''
                
                # 多行注释开始
                if not in_string and char == '/' and next_char == '*' and not in_multiline_comment:
                    in_multiline_comment = True
                    i += 2
                    continue
                
                # 多行注释结束
                if in_multiline_comment and char == '*' and next_char == '/':
                    in_multiline_comment = False
                    i += 2
                    continue
                
                # 在注释中，跳过字符
                if in_multiline_comment:
                    i += 1
                    continue
                
                # 处理字符串
                if char == '"' or char == "'" or char == '`':
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char and (i == 0 or line[i-1] != '\\'):
                        in_string = False
                        string_char = None
                    current_statement += char
                    i += 1
                    continue
                
                # 处理语句分隔符
                if not in_string and char == ';':
                    current_statement += char
                    stmt = current_statement.strip()
                    if stmt and not stmt.startswith('--'):
                        statements.append(stmt)
                    current_statement = ""
                    i += 1
                    continue
                
                current_statement += char
                i += 1
            
            # 如果不是语句结束，添加换行
            if current_statement and not current_statement.strip().endswith(';'):
                current_statement += '\n'
        
        # 添加最后一个语句（如果没有分号结尾）
        if current_statement.strip() and not current_statement.strip().startswith('--'):
            stmt = current_statement.strip()
            if stmt:
                statements.append(stmt)
        
        return statements
    
    def _execute_sql_via_ssh(self, sql: str):
        """通过SSH执行SQL"""
        # 将SQL保存到临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as f:
            f.write(sql)
            temp_sql_file = f.name
        
        try:
            password = self.db_config['password'].replace("'", "'\"'\"'") if self.db_config.get('password') else ''
            mysql_cmd = (
                f"mysql -h{self.db_config['host']} -P{self.db_config['port']} "
                f"-u{self.db_config['user']} -p'{password}' "
                f"{self.db_config['database']} < {temp_sql_file}"
            )
            
            stdin, stdout, stderr = self.ssh.exec_command(mysql_cmd)
            
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                error = stderr.read().decode('utf-8')
                raise Exception(f"MySQL执行失败: {error}")
                
        finally:
            try:
                os.unlink(temp_sql_file)
            except:
                pass
    
    def close(self):
        """关闭连接"""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
        if hasattr(self, 'ssh'):
            self.ssh.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='执行数据库表结构同步SQL')
    parser.add_argument('sql_file', help='要执行的SQL文件路径')
    parser.add_argument('--target', '-t', choices=['local', 'remote'], default='local',
                       help='目标数据库：local（本地）或 remote（远端）')
    parser.add_argument('--config', '-c', help='配置文件路径', default='db_sync_config.json')
    parser.add_argument('--dry-run', '-d', action='store_true', 
                       help='干运行模式：只显示将要执行的SQL，不实际执行')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='跳过确认提示，直接执行')
    parser.add_argument('--ssh-user', help='SSH用户名（覆盖配置文件）')
    parser.add_argument('--ssh-host', help='SSH主机地址（覆盖配置文件）')
    parser.add_argument('--ssh-port', type=int, help='SSH端口（覆盖配置文件）')
    parser.add_argument('--ssh-key', help='SSH私钥文件路径（覆盖配置文件）')
    parser.add_argument('--db-host', help='数据库主机（覆盖配置文件）')
    parser.add_argument('--db-port', type=int, help='数据库端口（覆盖配置文件）')
    parser.add_argument('--db-user', help='数据库用户名（覆盖配置文件）')
    parser.add_argument('--db-password', help='数据库密码（覆盖配置文件）')
    parser.add_argument('--db-name', help='数据库名称（覆盖配置文件）')
    
    args = parser.parse_args()
    
    # 加载配置
    config_file = os.path.join(os.path.dirname(__file__), args.config)
    config = {}
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    # 获取数据库配置
    if args.target == 'local':
        # 本地数据库配置
        try:
            from config import get_mysql_config
            db_config = get_mysql_config()
        except Exception as e:
            print(f"获取本地数据库配置失败: {e}")
            sys.exit(1)
        
        # 命令行参数覆盖
        if args.db_host:
            db_config['host'] = args.db_host
        if args.db_port:
            db_config['port'] = args.db_port
        if args.db_user:
            db_config['user'] = args.db_user
        if args.db_password:
            db_config['password'] = args.db_password
        if args.db_name:
            db_config['database'] = args.db_name
        
        ssh_config = None
    else:
        # 远端数据库配置
        ssh_config = {
            'user': args.ssh_user or config.get('ssh', {}).get('user', 'root'),
            'host': args.ssh_host or config.get('ssh', {}).get('host', ''),
            'port': args.ssh_port or config.get('ssh', {}).get('port', 22),
            'key_file': args.ssh_key or config.get('ssh', {}).get('key_file'),
            'password': config.get('ssh', {}).get('password')
        }
        
        db_config = {
            'host': args.db_host or config.get('remote_db', {}).get('host', 'localhost'),
            'port': args.db_port or config.get('remote_db', {}).get('port', 3306),
            'user': args.db_user or config.get('remote_db', {}).get('user', 'root'),
            'password': args.db_password or config.get('remote_db', {}).get('password', ''),
            'database': args.db_name or config.get('remote_db', {}).get('database', '')
        }
        
        # 检查必要参数
        if not ssh_config['host']:
            print("错误: 连接远端数据库需要SSH主机地址")
            sys.exit(1)
        if not db_config['database']:
            print("错误: 需要指定数据库名称")
            sys.exit(1)
        
        # 检查密钥文件
        key_file = ssh_config.get('key_file')
        if key_file:
            if '/path/to/your/private_key' in key_file or not os.path.exists(key_file):
                ssh_config['key_file'] = None
        
        # 提示输入密码（如果需要）
        import getpass
        if not ssh_config.get('key_file') and not ssh_config.get('password'):
            print(f"需要SSH密码来连接 {ssh_config['user']}@{ssh_config['host']}")
            ssh_config['password'] = getpass.getpass(f"请输入SSH密码: ")
        
        if not db_config.get('password'):
            print(f"需要数据库密码来连接 {db_config['user']}@{db_config['host']}")
            db_config['password'] = getpass.getpass(f"请输入数据库密码: ")
    
    print("=" * 60)
    print("数据库表结构同步SQL执行工具")
    print("=" * 60)
    print(f"目标: {args.target}")
    print(f"数据库: {db_config['database']} @ {db_config['host']}:{db_config['port']}")
    if ssh_config:
        print(f"SSH: {ssh_config['user']}@{ssh_config['host']}")
    print(f"SQL文件: {args.sql_file}")
    if args.dry_run:
        print("模式: DRY RUN（仅预览，不执行）")
    print("=" * 60)
    
    # 确认执行
    if not args.dry_run and not args.yes:
        print("\n警告: 此操作将修改数据库表结构！")
        confirm = input("确认执行? (yes/no): ")
        if confirm.lower() not in ['yes', 'y']:
            print("已取消执行")
            sys.exit(0)
    
    # 创建执行器
    executor = SQLExecutor(db_config, ssh_config)
    
    try:
        # 连接数据库
        print("\n连接数据库...")
        if args.target == 'local':
            if not executor.connect_local():
                sys.exit(1)
        else:
            if not executor.connect_remote():
                sys.exit(1)
        print("✓ 数据库连接成功")
        
        # 执行SQL
        print(f"\n执行SQL文件: {args.sql_file}")
        result = executor.execute_sql_file(args.sql_file, dry_run=args.dry_run)
        
        # 显示结果
        print("\n" + "=" * 60)
        print("执行结果:")
        print("=" * 60)
        print(f"成功: {result['executed']} 条")
        if result['failed'] > 0:
            print(f"失败: {result['failed']} 条")
            print("\n错误详情:")
            for error in result['errors']:
                print(f"  - {error}")
        
        if result['success']:
            print("\n✓ 所有SQL语句执行成功！")
        else:
            print(f"\n✗ 有 {result['failed']} 条SQL语句执行失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
        sys.exit(1)
    except Exception as e:
        print(f"\n执行失败: {e}")
        sys.exit(1)
    finally:
        executor.close()


if __name__ == '__main__':
    main()
