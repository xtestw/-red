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

def add_column_if_not_exists(session, table_name, field_name, field_type, comment, after_field, columns):
    """添加字段（如果不存在）"""
    if field_name in columns:
        return False, 'skipped'
    
    try:
        sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{field_name}` {field_type} DEFAULT NULL COMMENT '{comment}' AFTER `{after_field}`"
        session.execute(text(sql))
        session.commit()
        return True, 'added'
    except Exception as e:
        session.rollback()
        error_msg = str(e)
        if 'Duplicate column name' in error_msg or 'already exists' in error_msg.lower():
            return False, 'skipped'
        else:
            raise


def upgrade_stock_basic_table():
    """升级 stock_basic 表，添加公司信息和premarket字段"""
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
        
        print(f"当前表字段数: {len(columns)}")
        
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
            # stk_premarket 接口补充字段（每日盘前股本信息）
            ('total_share', 'float', '总股本（万股）', 'business_scope'),
            ('float_share', 'float', '流通股本（万股）', 'total_share'),
            ('pre_close', 'float', '昨日收盘价', 'float_share'),
            ('up_limit', 'float', '今日涨停价', 'pre_close'),
            ('down_limit', 'float', '今日跌停价', 'up_limit'),
        ]
        
        added_count = 0
        skipped_count = 0
        
        for field_name, field_type, comment, after_field in fields_to_add:
            success, status = add_column_if_not_exists(session, 'stock_basic', field_name, field_type, comment, after_field, columns)
            if status == 'added':
                print(f"  ✓ 成功添加字段: {field_name} ({comment})")
                added_count += 1
                columns.append(field_name)  # 更新列列表
            elif status == 'skipped':
                print(f"  ✓ 字段 {field_name} 已存在，跳过")
                skipped_count += 1
        
        print("=" * 60)
        print(f"升级完成:")
        print(f"  新增字段: {added_count}")
        print(f"  跳过字段: {skipped_count}")
        print(f"  总计字段: {len(fields_to_add)}")
        print("=" * 60)
        
        if added_count > 0:
            print("\n✓ stock_basic 表结构已成功升级！")
        else:
            print("\n✓ stock_basic 表所有字段已存在，无需升级。")
        
    except Exception as e:
        print(f"\n✗ 升级失败: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def upgrade_stock_daily_table():
    """升级 stock_daily 表，添加资金流向和两融数据字段"""
    print("\n" + "=" * 60)
    print("开始升级 stock_daily 表...")
    print("=" * 60)
    
    session = get_session()
    engine = get_engine()
    
    try:
        # 检查表结构
        inspector = inspect(engine)
        try:
            columns = [col['name'] for col in inspector.get_columns('stock_daily')]
        except Exception:
            # 如果 inspect 失败，使用原始 SQL 查询
            result = session.execute(text("SHOW COLUMNS FROM stock_daily"))
            columns = [row[0] for row in result]
        
        print(f"当前表字段数: {len(columns)}")
        
        # 需要添加的字段定义（资金流向字段）
        moneyflow_fields = [
            ('buy_sm_vol', 'float', '小单买入量（手）', 'amount'),
            ('buy_sm_amount', 'float', '小单买入金额（万元）', 'buy_sm_vol'),
            ('sell_sm_vol', 'float', '小单卖出量（手）', 'buy_sm_amount'),
            ('sell_sm_amount', 'float', '小单卖出金额（万元）', 'sell_sm_vol'),
            ('buy_md_vol', 'float', '中单买入量（手）', 'sell_sm_amount'),
            ('buy_md_amount', 'float', '中单买入金额（万元）', 'buy_md_vol'),
            ('sell_md_vol', 'float', '中单卖出量（手）', 'buy_md_amount'),
            ('sell_md_amount', 'float', '中单卖出金额（万元）', 'sell_md_vol'),
            ('buy_lg_vol', 'float', '大单买入量（手）', 'sell_md_amount'),
            ('buy_lg_amount', 'float', '大单买入金额（万元）', 'buy_lg_vol'),
            ('sell_lg_vol', 'float', '大单卖出量（手）', 'buy_lg_amount'),
            ('sell_lg_amount', 'float', '大单卖出金额（万元）', 'sell_lg_vol'),
            ('buy_elg_vol', 'float', '特大单买入量（手）', 'sell_lg_amount'),
            ('buy_elg_amount', 'float', '特大单买入金额（万元）', 'buy_elg_vol'),
            ('sell_elg_vol', 'float', '特大单卖出量（手）', 'buy_elg_amount'),
            ('sell_elg_amount', 'float', '特大单卖出金额（万元）', 'sell_elg_vol'),
            ('net_mf_amount', 'float', '净流入额（万元）', 'sell_elg_amount'),
        ]
        
        # 两融数据字段
        margin_fields = [
            ('rzye', 'float', '融资余额(元)', 'net_mf_amount'),
            ('rqye', 'float', '融券余量(股)', 'rzye'),
            ('rqyl', 'float', '融券余额(元)', 'rqye'),
            ('rzrqye', 'float', '融资融券余额(元)', 'rqyl'),
            ('rzmre', 'float', '融资买入额(元)', 'rzrqye'),
            ('rqmcl', 'float', '融券卖出量(股)', 'rzmre'),
            ('rzche', 'float', '融资偿还额(元)', 'rqmcl'),
            ('rqchl', 'float', '融券偿还量(股)', 'rzche'),
        ]
        
        fields_to_add = moneyflow_fields + margin_fields
        
        added_count = 0
        skipped_count = 0
        
        for field_name, field_type, comment, after_field in fields_to_add:
            success, status = add_column_if_not_exists(session, 'stock_daily', field_name, field_type, comment, after_field, columns)
            if status == 'added':
                print(f"  ✓ 成功添加字段: {field_name} ({comment})")
                added_count += 1
                columns.append(field_name)  # 更新列列表
            elif status == 'skipped':
                print(f"  ✓ 字段 {field_name} 已存在，跳过")
                skipped_count += 1
        
        print("=" * 60)
        print(f"升级完成:")
        print(f"  新增字段: {added_count}")
        print(f"  跳过字段: {skipped_count}")
        print(f"  总计字段: {len(fields_to_add)}")
        print("=" * 60)
        
        if added_count > 0:
            print("\n✓ stock_daily 表结构已成功升级！")
        else:
            print("\n✓ stock_daily 表所有字段已存在，无需升级。")
        
    except Exception as e:
        print(f"\n✗ 升级失败: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    try:
        print("=" * 60)
        print("数据库升级脚本")
        print("=" * 60)
        
        # 升级 stock_basic 表
        upgrade_stock_basic_table()
        
        # 升级 stock_daily 表
        upgrade_stock_daily_table()
        
        print("\n" + "=" * 60)
        print("所有表升级完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

