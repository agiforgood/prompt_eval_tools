#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Goal Consistency 数据批量重命名和结构转换脚本
用于将原始的中文字段名转换为英文字段名，并重新组织数据结构
"""

import json
import os
from typing import Dict, List, Any

def load_json_file(file_path: str) -> List[Dict[str, Any]]:
    """
    加载JSON文件
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        解析后的数据列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        print(f"✅ 成功加载文件: {file_path}")
        print(f"📊 数据记录数: {len(data)}")
        
        return data
        
    except FileNotFoundError:
        print(f"❌ 文件未找到: {file_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        raise
    except Exception as e:
        print(f"❌ 加载文件时出错: {e}")
        raise

def create_field_mapping() -> Dict[str, str]:
    """
    创建字段映射关系
    
    Returns:
        字段映射字典 {原字段名: 新字段名}
    """
    # 基础字段映射
    base_mapping = {
        "编号": "DELETE_FIELD",  # 删除此字段
        "Q1文本编号": "dialog_id",
        "提交人": "user_id"
    }
    
    # 评估内容字段映射
    content_mapping = {
        "Q2请问前 15 轮对话中，教练和家长的目标是否属于心理学范畴（情绪、认知、行为、心理功能与社会功能）": "psychological_scope",
        "Q3请问前 15 轮对话中，教练是否努力和家长就咨询目标达成共识？": "consensus_effort",
        "Q3-1如果有，请尝试写出体现的具体轮次。": "consensus_rounds",
        "Q4请问前 15 轮对话中，教练有没有和家长确认具体的咨询目标？": "goal_confirmation",
        "Q4-1如果有，请尝试写出体现的具体轮次。": "goal_confirmation_rounds",
        "Q4-2教练与家长确认的目标是否是客观且可评估的？": "goal_objectivity",
        "Q4-2教练与家长确认的目标是否是客观且可评估的？-目标无法评估，没有具体的行为指标-补充内容": "goal_objectivity_supplement",
        "Q4-3请问前 15 轮对话中，教练和家长确定的目标能否在一定时间内达成？": "goal_achievability",
        "Q5请问前 15 轮对话中，教练有没有成功聚焦收窄目标": "goal_focus",
        "Q5-1如果有，请尝试写出体现的具体轮次。": "goal_focus_rounds",
        "Q5-2您觉得这组对话里，教练应该如何聚焦收窄目标？请根据该角度提供成功聚焦收窄目标的范例。": "goal_focus_example",
        "Q6请问前 15 轮对话中，教练和家长的目标是否发生变化？": "goal_change",
        "Q6-1当目标变化时，教练能否和来访者动态协商，及时调整咨询目标？": "dynamic_adjustment",
        "Q6-2 如果有，请尝试写出体现的具体轮次。": "dynamic_adjustment_rounds",
        "Q7请评价前 15 轮对话中来访者的参与程度": "client_participation"
    }
    
    # 合并所有映射
    all_mapping = {**base_mapping, **content_mapping}
    
    print(f"📋 字段映射关系已创建，共 {len(all_mapping)} 个字段")
    return all_mapping

def transform_record_structure(record: Dict[str, Any], field_mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    转换单条记录的结构
    
    Args:
        record: 原始记录
        field_mapping: 字段映射关系
        
    Returns:
        转换后的记录
    """
    # 创建新的记录结构
    new_record = {
        "eval_schema_id": "goal_consistency",  # 固定值
        "dialog_id": None,
        "user_id": None,
        "content": {}
    }
    
    # 处理每个字段
    for old_key, value in record.items():
        if old_key in field_mapping:
            new_key = field_mapping[old_key]
            
            # 跳过要删除的字段
            if new_key == "DELETE_FIELD":
                continue
            
            # 基础字段直接赋值
            if new_key in ["dialog_id", "user_id"]:
                new_record[new_key] = value
            else:
                # 评估内容字段放入content对象
                new_record["content"][new_key] = value
        else:
            # 未映射的字段保留原名，放入content
            print(f"⚠️  未映射的字段: {old_key}")
            new_record["content"][old_key] = value
    
    return new_record

def batch_transform_records(data: List[Dict[str, Any]], field_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    批量转换记录
    
    Args:
        data: 原始数据列表
        field_mapping: 字段映射关系
        
    Returns:
        转换后的数据列表
    """
    transformed_data = []
    
    print(f"\n🔄 开始批量转换 {len(data)} 条记录...")
    
    for i, record in enumerate(data):
        try:
            transformed_record = transform_record_structure(record, field_mapping)
            transformed_data.append(transformed_record)
            
            # 每处理10条记录显示进度
            if (i + 1) % 10 == 0:
                print(f"📈 已处理 {i + 1}/{len(data)} 条记录")
                
        except Exception as e:
            print(f"❌ 处理第 {i + 1} 条记录时出错: {e}")
            continue
    
    print(f"✅ 批量转换完成!")
    print(f"📊 成功转换 {len(transformed_data)}/{len(data)} 条记录")
    
    return transformed_data

def save_transformed_data(data: List[Dict[str, Any]], output_path: str) -> None:
    """
    保存转换后的数据
    
    Args:
        data: 转换后的数据
        output_path: 输出文件路径
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        
        print(f"✅ 成功保存到: {output_path}")
        
    except Exception as e:
        print(f"❌ 保存文件时出错: {e}")
        raise

def print_sample_data(data: List[Dict[str, Any]], sample_count: int = 2) -> None:
    """
    打印转换后的数据示例
    
    Args:
        data: 转换后的数据
        sample_count: 要显示的示例数量
    """
    print("\n" + "="*80)
    print("📋 转换后的数据结构示例")
    print("="*80)
    
    for i in range(min(sample_count, len(data))):
        print(f"\n🔸 示例 {i+1}:")
        sample = data[i]
        
        # 显示基础信息
        print(f"  eval_schema_id: {sample.get('eval_schema_id')}")
        print(f"  dialog_id: {sample.get('dialog_id')}")
        print(f"  user_id: {sample.get('user_id')}")
        
        # 显示content中的前几个字段
        content = sample.get('content', {})
        print(f"  content字段数: {len(content)}")
        
        # 显示前5个content字段作为示例
        content_items = list(content.items())[:5]
        for key, value in content_items:
            display_value = str(value)[:50] + "..." if value and len(str(value)) > 50 else value
            print(f"    {key}: {display_value}")
        
        if len(content) > 5:
            print(f"    ... 还有 {len(content) - 5} 个字段")

def main():
    """
    主函数 - 执行Goal Consistency数据转换流程
    """
    print("🚀 开始Goal Consistency数据转换")
    print("="*50)
    
    # 配置文件路径
    INPUT_FILE = "zhang-junjie-goalconsistency.json"
    OUTPUT_FILE = "zhang-junjie-goalconsistency-transformed.json"
    
    try:
        # 1. 加载原始数据
        print("📂 步骤1: 加载原始数据")
        data = load_json_file(INPUT_FILE)
        
        # 2. 创建字段映射
        print("\n🗺️  步骤2: 创建字段映射")
        field_mapping = create_field_mapping()
        
        # 3. 批量转换数据结构
        print("\n🔄 步骤3: 转换数据结构")
        transformed_data = batch_transform_records(data, field_mapping)
        
        # 4. 显示转换结果示例
        print_sample_data(transformed_data)
        
        # 5. 保存转换后的数据
        print(f"\n💾 步骤4: 保存转换后的数据")
        save_transformed_data(transformed_data, OUTPUT_FILE)
        
        print("\n" + "="*50)
        print("🎉 Goal Consistency数据转换完成!")
        print(f"📁 输入文件: {INPUT_FILE}")
        print(f"📁 输出文件: {OUTPUT_FILE}")
        print(f"📊 处理记录数: {len(transformed_data)}")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ 执行过程中出现错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 