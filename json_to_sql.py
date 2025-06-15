#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将JSON数据转换为SQL INSERT语句脚本
用于将转换后的JSON数据生成SQL插入语句
"""

import json
import os
import uuid
import random
import time
from typing import Dict, List, Any

def load_json_file(file_path: str) -> List[Dict[str, Any]]:
    """
    读取JSON文件
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        解析后的JSON数据列表
        
    Raises:
        FileNotFoundError: 文件不存在
        json.JSONDecodeError: JSON格式错误
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"✅ 成功读取文件: {file_path}")
            print(f"📊 数据条数: {len(data)}")
            return data
    except FileNotFoundError:
        print(f"❌ 错误: 文件 {file_path} 不存在")
        raise
    except json.JSONDecodeError as e:
        print(f"❌ 错误: JSON格式错误 - {e}")
        raise

def escape_sql_string(value: str) -> str:
    """
    转义SQL字符串中的特殊字符
    
    Args:
        value: 要转义的字符串
        
    Returns:
        转义后的字符串
    """
    if value is None:
        return 'NULL'
    
    if isinstance(value, str):
        # 转义单引号和反斜杠
        escaped = value.replace("'", "''").replace("\\", "\\\\")
        return f"'{escaped}'"
    else:
        return f"'{str(value)}'"

def generate_unique_id() -> str:
    """
    生成唯一的ID
    
    Returns:
        唯一的ID字符串
    """
    # 使用UUID4生成唯一ID，确保全局唯一性
    return str(uuid.uuid4())

def generate_insert_statement(record: Dict[str, Any], table_name: str = "your_table_name") -> str:
    """
    为单条记录生成SQL INSERT语句
    
    Args:
        record: 记录字典
        table_name: 目标表名
        
    Returns:
        SQL INSERT语句
    """
    # 生成唯一ID
    unique_id = escape_sql_string(generate_unique_id())
    dialog_id = escape_sql_string(record.get('dialog_id'))
    user_id = escape_sql_string(record.get('user_id'))
    eval_schema_id = escape_sql_string(record.get('eval_schema_id'))
    
    # 将content字段序列化为JSON字符串
    content = record.get('content', {})
    content_json = json.dumps(content, ensure_ascii=False, separators=(',', ':'))
    content_escaped = escape_sql_string(content_json)
    
    sql = f"INSERT INTO {table_name} (id, dialog_id, user_id, eval_schema_id, content) VALUES ({unique_id}, {dialog_id}, {user_id}, {eval_schema_id}, {content_escaped});"
    
    return sql

def generate_batch_insert_statements(data: List[Dict[str, Any]], 
                                   table_name: str = "your_table_name",
                                   batch_size: int = 100) -> List[str]:
    """
    批量生成SQL INSERT语句
    
    Args:
        data: 数据列表
        table_name: 目标表名
        batch_size: 每批处理的记录数
        
    Returns:
        SQL INSERT语句列表
    """
    sql_statements = []
    
    for i, record in enumerate(data):
        sql = generate_insert_statement(record, table_name)
        sql_statements.append(sql)
        
        if (i + 1) % batch_size == 0:
            print(f"🔄 已生成 {i + 1}/{len(data)} 条SQL语句")
    
    print(f"✅ 批量SQL语句生成完成!")
    print(f"📊 总共生成了 {len(sql_statements)} 条INSERT语句")
    
    return sql_statements

def save_sql_file(sql_statements: List[str], output_path: str) -> None:
    """
    保存SQL语句到文件
    
    Args:
        sql_statements: SQL语句列表
        output_path: 输出文件路径
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            # 写入SQL文件头部注释
            file.write("-- ===============================================\n")
            file.write("-- 批量插入SQL语句文件\n")
            file.write(f"-- 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"-- 记录数量: {len(sql_statements)}\n")
            file.write("-- ===============================================\n\n")
            
            # 写入创建表的SQL语句（示例）
            file.write("-- 创建表结构（如果表不存在）\n")
            file.write("CREATE TABLE IF NOT EXISTS your_table_name (\n")
            file.write("    id VARCHAR(36) NOT NULL PRIMARY KEY,  -- UUID格式\n")
            file.write("    dialog_id VARCHAR(50) NOT NULL,\n")
            file.write("    user_id VARCHAR(100) NOT NULL,\n")
            file.write("    eval_schema_id VARCHAR(50) NOT NULL,\n")
            file.write("    content JSON NOT NULL,\n")
            file.write("    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n")
            file.write("    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP\n")
            file.write(");\n\n")
            
            # 写入所有INSERT语句
            file.write("-- 批量插入数据\n")
            for i, sql in enumerate(sql_statements):
                file.write(sql + "\n")
                
                # 每10条语句添加一个空行，便于阅读
                if (i + 1) % 10 == 0:
                    file.write("\n")
        
        print(f"✅ 成功保存到: {output_path}")
        
    except Exception as e:
        print(f"❌ 保存文件时出错: {e}")
        raise

def print_sample_sql(sql_statements: List[str], sample_count: int = 3) -> None:
    """
    打印SQL语句示例
    
    Args:
        sql_statements: SQL语句列表
        sample_count: 要显示的示例数量
    """
    print("\n" + "="*80)
    print("📋 生成的SQL语句示例")
    print("="*80)
    
    for i in range(min(sample_count, len(sql_statements))):
        print(f"\n🔸 示例 {i+1}:")
        # 格式化显示SQL语句，便于阅读
        sql = sql_statements[i]
        if len(sql) > 200:
            print(f"  {sql[:200]}...")
            print(f"  [语句长度: {len(sql)} 字符]")
        else:
            print(f"  {sql}")
    
    print(f"\n📊 统计信息:")
    print(f"  - 总SQL语句数: {len(sql_statements)}")
    print(f"  - 平均语句长度: {sum(len(sql) for sql in sql_statements) // len(sql_statements)} 字符")

def generate_optimized_batch_insert(data: List[Dict[str, Any]], 
                                  table_name: str = "your_table_name",
                                  values_per_statement: int = 50) -> List[str]:
    """
    生成优化的批量INSERT语句（单个INSERT包含多个VALUES）
    
    Args:
        data: 数据列表
        table_name: 目标表名
        values_per_statement: 每个INSERT语句包含的VALUES数量
        
    Returns:
        优化的SQL INSERT语句列表
    """
    optimized_statements = []
    
    for i in range(0, len(data), values_per_statement):
        batch = data[i:i + values_per_statement]
        
        # 构建批量INSERT语句的开头
        sql_parts = [f"INSERT INTO {table_name} (id, dialog_id, user_id, eval_schema_id, content) VALUES"]
        
        # 构建所有VALUES子句
        values_list = []
        for record in batch:
            # 为每条记录生成唯一ID
            unique_id = escape_sql_string(generate_unique_id())
            dialog_id = escape_sql_string(record.get('dialog_id'))
            user_id = escape_sql_string(record.get('user_id'))
            eval_schema_id = escape_sql_string(record.get('eval_schema_id'))
            
            content = record.get('content', {})
            content_json = json.dumps(content, ensure_ascii=False, separators=(',', ':'))
            content_escaped = escape_sql_string(content_json)
            
            values_list.append(f"({unique_id}, {dialog_id}, {user_id}, {eval_schema_id}, {content_escaped})")
        
        # 组合成完整的SQL语句
        sql = sql_parts[0] + "\n" + ",\n".join(values_list) + ";"
        optimized_statements.append(sql)
        
        print(f"🔄 已生成批量语句 {len(optimized_statements)}, 包含 {len(batch)} 条记录")
    
    print(f"✅ 优化批量SQL语句生成完成!")
    print(f"📊 生成了 {len(optimized_statements)} 个批量INSERT语句，覆盖 {len(data)} 条记录")
    
    return optimized_statements

def main():
    """
    主函数 - 执行JSON到SQL转换流程
    """
    print("🚀 开始将JSON数据转换为SQL INSERT语句")
    print("="*50)
    
    # 配置文件路径
    INPUT_FILE = "zhang-junjie-sympathy-transformed.json"
    OUTPUT_FILE_SINGLE = "insert_statements_single.sql"
    OUTPUT_FILE_BATCH = "insert_statements_batch.sql"
    TABLE_NAME = "sympathy_evaluations"  # 您可以修改表名
    
    try:
        # 1. 读取转换后的JSON文件
        data = load_json_file(INPUT_FILE)
        
        print("\n🔧 选择生成模式:")
        print("1️⃣  生成单条INSERT语句（每条记录一个INSERT）")
        print("2️⃣  生成批量INSERT语句（每个INSERT包含多条记录，性能更好）")
        print("3️⃣  同时生成两种模式")
        
        choice = input("\n请选择模式 (1/2/3): ").strip()
        
        if choice in ['1', '3']:
            # 2. 生成单条INSERT语句
            print(f"\n🔄 生成单条INSERT语句...")
            single_statements = generate_batch_insert_statements(data, TABLE_NAME)
            
            # 3. 显示示例
            print_sample_sql(single_statements)
            
            # 4. 保存单条INSERT文件
            save_sql_file(single_statements, OUTPUT_FILE_SINGLE)
        
        if choice in ['2', '3']:
            # 5. 生成优化的批量INSERT语句
            print(f"\n🔄 生成优化批量INSERT语句...")
            batch_statements = generate_optimized_batch_insert(data, TABLE_NAME, values_per_statement=20)
            
            # 6. 保存批量INSERT文件
            save_sql_file(batch_statements, OUTPUT_FILE_BATCH)
        
        print("\n" + "="*50)
        print("🎉 JSON到SQL转换完成!")
        print(f"📁 输入文件: {INPUT_FILE}")
        
        if choice in ['1', '3']:
            print(f"📁 单条INSERT输出: {OUTPUT_FILE_SINGLE}")
        if choice in ['2', '3']:
            print(f"📁 批量INSERT输出: {OUTPUT_FILE_BATCH}")
            
        print(f"🏷️  表名: {TABLE_NAME}")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ 执行过程中出现错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 