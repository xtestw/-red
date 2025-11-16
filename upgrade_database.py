#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
数据库升级脚本：自动添加缺失的字段
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_session, get_engine
from sqlalchemy import text, inspect
from config import get_mysql_config

def upgrade_stock_basic_table():
    """升级 stock_basic 表，添加公司信息字段"""
    print("=" * 60)
    print("开始升级 stock_basic 表...")
    print("=" * 60)
    
    session = get_session()
    engine = get_engine()
    
    try:
        # 检查表结构
        inspector = inspect(engine)
        try:
            columns = [col['name'] for col in inspector.get_columns('stock_basic')]
        except Exception:
            # 如果 inspect 失败，使用原始 SQL 查询
            result = session.execute(text("SHOW COLUMNS FROM stock_basic"))
            columns = [row[0] for row in result]
        
        print(f"当前表字段: {', '.join(columns)}")
        
        # 需要添加的字段定义
        fields_to_add = [
            ('com_name', 'varchar(200)', '公司全称', 'list_date'),
            ('com_id', 'varchar(50)', '统一社会信用代码', 'com_name'),
            ('chairman', 'varchar(50)', '法人代表', 'com_id'),
            ('manager', 'varchar(50)', '总经理', 'chairman'),
            ('secretary', 'varchar(50)', '董秘', 'manager'),
            ('reg_capital', 'float', '注册资本(万元)', 'secretary'),
            ('setup_date', 'varchar(10)', '注册日期', 'reg_capital'),
            ('province', 'varchar(50)', '所在省份', 'setup_date'),
            ('city', 'varchar(50)', '所在城市', 'province'),
            ('introduction', 'text', '公司介绍', 'city'),
            ('website', 'varchar(200)', '公司主页', 'introduction'),
            ('email', 'varchar(100)', '电子邮件', 'website'),
            ('office', 'varchar(200)', '办公室', 'email'),
            ('employees', 'int(11)', '员工人数', 'office'),
            ('main_business', 'text', '主要业务及产品', 'employees'),
            ('business_scope', 'text', '经营范围', 'main_business'),
        ]
        
        added_count = 0
        skipped_count = 0
        
        for field_name, field_type, comment, after_field in fields_to_add:
            if field_name in columns:
                print(f"  ✓ 字段 {field_name} 已存在，跳过")
                skipped_count += 1
                continue
            
            try:
                # 构建 ALTER TABLE 语句
                sql = f"ALTER TABLE `stock_basic` ADD COLUMN `{field_name}` {field_type} DEFAULT NULL COMMENT '{comment}' AFTER `{after_field}`"
                session.execute(text(sql))
                session.commit()
                print(f"  ✓ 成功添加字段: {field_name} ({comment})")
                added_count += 1
            except Exception as e:
                session.rollback()
                error_msg = str(e)
                if 'Duplicate column name' in error_msg or 'already exists' in error_msg.lower():
                    print(f"  ⚠ 字段 {field_name} 已存在（可能在其他会话中添加），跳过")
                    skipped_count += 1
                else:
                    print(f"  ✗ 添加字段 {field_name} 失败: {e}")
                    raise
        
        print("=" * 60)
        print(f"升级完成:")
        print(f"  新增字段: {added_count}")
        print(f"  跳过字段: {skipped_count}")
        print(f"  总计字段: {len(fields_to_add)}")
        print("=" * 60)
        
        if added_count > 0:
            print("\n✓ 数据库表结构已成功升级！")
        else:
            print("\n✓ 所有字段已存在，无需升级。")
        
    except Exception as e:
        print(f"\n✗ 升级失败: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    try:
        upgrade_stock_basic_table()
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)

