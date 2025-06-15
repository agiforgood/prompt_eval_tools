#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量替换JSON文件中的字段名脚本
用于将长中文字段名替换为简洁的英文字段名
"""

import json
import os
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

def create_reverse_mapping(field_mapping: Dict[str, str]) -> Dict[str, str]:
    """
    创建反向映射（从旧字段名到新字段名）
    
    Args:
        field_mapping: 新字段名到旧字段名的映射
        
    Returns:
        旧字段名到新字段名的映射
    """
    reverse_mapping = {old_key: new_key for new_key, old_key in field_mapping.items()}
    print(f"🔄 创建了 {len(reverse_mapping)} 个字段映射关系")
    return reverse_mapping

def transform_record_structure(record: Dict[str, Any], content_field_mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    转换单条记录的结构，实现嵌套化和字段重命名
    
    Args:
        record: 原始记录字典
        content_field_mapping: 内容字段映射关系（旧->新）
        
    Returns:
        转换后的新记录结构
    """
    new_record = {}
    content = {}
    renamed_count = 0
    
    for old_key, value in record.items():
        # 1. 删除"编号"字段
        if old_key == "编号":
            continue
            
        # 2. 基本信息字段处理
        elif old_key == "Q1文本编号":
            new_record["dialog_id"] = value
            renamed_count += 1
        elif old_key == "提交人":
            new_record["user_id"] = value
            renamed_count += 1
            
        # 3. 内容相关字段放入content中
        elif old_key in content_field_mapping:
            new_key = content_field_mapping[old_key]
            content[new_key] = value
            renamed_count += 1
        else:
            # 4. 其他未映射的字段也放入content中（保险起见）
            content[old_key] = value
    
    # 5. 添加固定的eval_schema_id
    new_record["eval_schema_id"] = "sympathy_positive"
    
    # 6. 添加content字段
    if content:
        new_record["content"] = content
    
    return new_record, renamed_count

def batch_transform_data(data: List[Dict[str, Any]], content_field_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    批量转换所有记录的数据结构
    
    Args:
        data: 原始数据列表
        content_field_mapping: 内容字段映射关系（旧->新）
        
    Returns:
        结构已转换的数据列表
    """
    new_data = []
    total_transformed = 0
    
    for i, record in enumerate(data):
        new_record, transformed_count = transform_record_structure(record, content_field_mapping)
        new_data.append(new_record)
        total_transformed += transformed_count
        
        if (i + 1) % 5 == 0:  # 每5条记录显示一次进度
            print(f"🔄 已处理 {i + 1}/{len(data)} 条记录")
    
    print(f"✅ 批量数据转换完成!")
    print(f"📊 总共转换了 {total_transformed} 个字段")
    print(f"📋 添加了 {len(data)} 个 eval_schema_id 字段")
    return new_data

def save_json_file(data: List[Dict[str, Any]], output_path: str) -> None:
    """
    保存JSON文件
    
    Args:
        data: 要保存的数据
        output_path: 输出文件路径
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        print(f"✅ 成功保存到: {output_path}")
    except Exception as e:
        print(f"❌ 保存文件时出错: {e}")
        raise

def print_sample_comparison(original_data: List[Dict[str, Any]], 
                          new_data: List[Dict[str, Any]], 
                          sample_index: int = 0) -> None:
    """
    打印样本对比，显示数据结构转换前后的差异
    
    Args:
        original_data: 原始数据
        new_data: 转换后的数据
        sample_index: 要显示的样本索引
    """
    if sample_index >= len(original_data):
        return
        
    print("\n" + "="*50)
    print("📋 数据结构转换对比示例")
    print("="*50)
    
    original_sample = original_data[sample_index]
    new_sample = new_data[sample_index]
    
    print("🔸 原始数据结构:")
    print(f"  - 总字段数: {len(original_sample)}")
    print(f"  - 包含字段: {list(original_sample.keys())[:3]}... (显示前3个)")
    
    print("\n🔹 转换后数据结构:")
    print(f"  - eval_schema_id: {new_sample.get('eval_schema_id')}")
    print(f"  - dialog_id: {new_sample.get('dialog_id')}")
    print(f"  - user_id: {new_sample.get('user_id')}")
    
    if 'content' in new_sample:
        content_keys = list(new_sample['content'].keys())
        print(f"  - content字段包含 {len(content_keys)} 个子字段:")
        print(f"    {content_keys[:3]}... (显示前3个)")
    
    print("\n✨ 主要变化:")
    print("  ✅ 删除了 '编号' 字段")
    print("  ✅ 添加了 'eval_schema_id' 字段")
    print("  ✅ 'Q1文本编号' → 'dialog_id'")
    print("  ✅ '提交人' → 'user_id'")
    print("  ✅ 评估相关字段嵌套到 'content' 中")

def main():
    """
    主函数 - 执行批量数据结构转换流程
    """
    print("🚀 开始批量转换JSON数据结构")
    print("="*50)
    
    # 内容字段映射关系（严格按照您提供的映射 - 新字段名 -> 旧字段名）
    CONTENT_FIELD_MAPPING = {
        "round5_need_positive_attention": "Q2您觉得这组对话中，教练在第5轮对话中是否需要使用积极关注的技术？",
        "round5_used_positive_attention": "Q3您觉得这组对话中，教练在第5轮中的回复，是否使用了积极关注的技术？",
        "round5_positive_attention_example": "Q3-1您觉得这组对话里，教练在第5轮对话中应该如何从正向角度反馈来访者提及的感受，想法或者行为？请根据该角度提供一个正向反馈的范例。",
        "round5_need_empathy": "Q4您觉得这组对话中，教练在第5轮对话中是否需要共情？",
        "round5_empathy_target_needed": "Q4-1您觉得这组对话中，教练在第5轮对话中需要共情的对象是？",
        "round5_has_empathy": "Q5您觉得这组对话中，教练在第5轮中的回复，是否存在共情？",
        "round5_empathy_target_actual": "第5轮共情对象是？",
        "round5_empathy_target_accuracy": "Q5-2请问教练在第5轮中，共情对象是否准确？",
        "round5_empathy_consistency": "第5轮共情是否匹配",
        "round5_empathy_mismatch_reason": "第5轮共情不匹配原因",
        "round5_empathy_depth": "第5轮共情程度是否准确？",
        "round5_empathy_improvement": "Q5-5请问教练在第5轮中应该如何回复，共情程度才是合适的？请提供一个您认为合适的回复范例。",
        "round10_need_positive_attention": "Q6您觉得这组对话中，教练在第10轮对话中是否需要使用积极关注的技术？",
        "round10_used_positive_attention": "Q7您觉得这组对话中，教练在第10轮中的回复，是否使用了积极关注的技术？",
        "round10_positive_attention_example": "Q7-1您觉得这组对话里，教练在第10轮对话中应该如何从正向角度反馈来访者提及的感受，想法或者行为？请根据该角度提供一个正向反馈的范例。",
        "round10_need_empathy": "Q8您觉得这组对话中，教练在第10轮对话中是否需要共情？",
        "round10_empathy_target_needed": "Q8-1您觉得这组对话中，教练在第10轮对话中需要共情的对象是？",
        "round10_has_empathy": "Q9您觉得这组对话中，教练在第10轮中的回复，是否存在共情？",
        "round10_empathy_target_actual": "Q9-1请问教练在第10轮中，实际回复的共情对象是？",
        "round10_empathy_target_accuracy": "Q9-2请问教练在第10轮中，共情对象是否准确？",
        "round10_empathy_consistency": "Q9-3请问教练在第10轮中的回复，教练的共情回复和来访者情绪是否一致？",
        "round10_empathy_consistency_supplement": "Q9-3请问教练在第10轮中的回复，教练的共情回复和来访者情绪是否一致？-不一致-补充内容",
        "round10_empathy_depth": "Q9-4请问教练在第10轮中的回复，教练回复的共情程度是？",
        "round10_empathy_depth_supplement": "如果共情程度选择其他，请补充说明",
        "round10_empathy_improvement": "Q9-5请问教练在第10轮中应该如何回复，共情程度才是合适的？请提供一个您认为合适的回复范例。",
        "remarks": "备注"
    }
    
    # 配置文件路径
    INPUT_FILE = "zhang-junjie-sympathy.json"
    OUTPUT_FILE = "zhang-junjie-sympathy-transformed.json"
    
    try:
        # 1. 读取原始JSON文件
        original_data = load_json_file(INPUT_FILE)
        
        # 2. 创建反向映射（旧字段名->新字段名）
        content_mapping = create_reverse_mapping(CONTENT_FIELD_MAPPING)
        
        # 3. 批量转换数据结构
        new_data = batch_transform_data(original_data, content_mapping)
        
        # 4. 显示转换对比示例
        print_sample_comparison(original_data, new_data)
        
        # 5. 保存新文件
        save_json_file(new_data, OUTPUT_FILE)
        
        print("\n" + "="*50)
        print("🎉 批量数据结构转换完成!")
        print(f"📁 输入文件: {INPUT_FILE}")
        print(f"📁 输出文件: {OUTPUT_FILE}")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ 执行过程中出现错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 