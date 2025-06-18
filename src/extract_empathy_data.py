#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取张俊杰关于第5轮共情问题的答案
从all_records.json中提取指定用户对Q4问题的回答
"""

import json
import os
from typing import List, Dict, Any, Optional

def load_all_records(file_path: str = "all_records.json") -> List[Dict[str, Any]]:
    """
    加载所有记录的JSON文件
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        所有记录的列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        print(f"✅ 成功加载文件: {file_path}")
        print(f"📊 总记录数: {len(data)}")
        return data
        
    except FileNotFoundError:
        print(f"❌ 文件未找到: {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        return []
    except Exception as e:
        print(f"❌ 加载文件时出错: {e}")
        return []

def extract_submitter_name(submitter_data: Any) -> Optional[str]:
    """
    从提交人字段中提取姓名
    
    Args:
        submitter_data: 提交人数据（可能是字典、字符串或其他）
        
    Returns:
        提交人姓名字符串，如果无法提取则返回None
    """
    if submitter_data is None:
        return None
    
    if isinstance(submitter_data, dict):
        # 尝试多种可能的键名
        for key in ['name', 'Name', '姓名', 'display_name']:
            if key in submitter_data and submitter_data[key]:
                return str(submitter_data[key])
        # 如果找不到常见键名，返回字典的字符串表示
        return str(submitter_data)
    
    if isinstance(submitter_data, str):
        return submitter_data
    
    # 其他类型转为字符串
    return str(submitter_data)

def extract_empathy_answers(records: List[Dict[str, Any]], target_name: str = "张俊杰") -> List[Dict[str, str]]:
    """
    提取指定用户关于第5轮共情问题的答案
    
    Args:
        records: 所有记录列表
        target_name: 目标用户姓名
        
    Returns:
        提取的结果列表，格式为 [{"dialog_id": "xxx", "round5_need_empathy": "xxx"}]
    """
    # 可能的Q4问题字段名
    q4_field_names = [
        "Q4：您觉得这组对话中，教练在第5轮对话中是否需要共情?",
        "Q4：您觉得这组对话中，教练在第5轮对话中是否需要共情？",
        "Q4",
        "第5轮共情",
        "共情问题"
    ]
    
    # 对话ID字段名（优先使用Q1-文本编号）
    dialog_id_fields = [
        "Q1-文本编号",
        "Q1文本编号",
        "Q1_文本编号",
        "对话编号", 
        "文本编号",
        "dialog_id"
    ]
    
    results = []
    zhang_junjie_records = []
    
    # 首先筛选出张俊杰的记录
    for record in records:
        submitter_raw = record.get("提交人")
        submitter_name = extract_submitter_name(submitter_raw)
        
        if submitter_name and target_name in submitter_name:
            zhang_junjie_records.append(record)
    
    print(f"🔍 找到 {len(zhang_junjie_records)} 条张俊杰的记录")
    
    # 提取每条记录的答案
    for record in zhang_junjie_records:
        # 查找对话ID
        dialog_id = None
        for field_name in dialog_id_fields:
            if field_name in record and record[field_name] is not None:
                dialog_id = str(record[field_name])
                break
        
        if not dialog_id:
            dialog_id = "unknown"
        
        # 查找Q4答案
        empathy_answer = None
        found_field = None
        
        for field_name in q4_field_names:
            if field_name in record and record[field_name] is not None:
                empathy_answer = str(record[field_name])
                found_field = field_name
                break
        
        # 如果没找到，尝试模糊匹配
        if empathy_answer is None:
            for field_name, value in record.items():
                if ("Q4" in field_name or "共情" in field_name or "第5轮" in field_name) and value is not None:
                    empathy_answer = str(value)
                    found_field = field_name
                    break
        
        if empathy_answer is None:
            empathy_answer = "未找到答案"
            print(f"⚠️  对话ID {dialog_id} 未找到Q4答案")
        else:
            print(f"✅ 对话ID {dialog_id} 找到答案，字段名: {found_field}")
        
        results.append({
            "dialog_id": dialog_id,
            "round5_need_empathy": empathy_answer
        })
    
    return results

def save_extraction_results(results: List[Dict[str, str]], output_file: str = "zhang_junjie_empathy_answers.json"):
    """
    保存提取结果到JSON文件
    
    Args:
        results: 提取的结果列表
        output_file: 输出文件名
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=2)
        
        print(f"✅ 结果已保存到: {output_file}")
        print(f"📊 共提取 {len(results)} 条记录")
        
    except Exception as e:
        print(f"❌ 保存文件时出错: {e}")

def print_sample_results(results: List[Dict[str, str]], sample_count: int = 3):
    """
    打印结果示例
    
    Args:
        results: 结果列表
        sample_count: 显示的示例数量
    """
    print(f"\n📋 提取结果示例 (前{min(sample_count, len(results))}条):")
    print("=" * 60)
    
    for i, result in enumerate(results[:sample_count]):
        print(f"🔸 记录 {i+1}:")
        print(f"  Dialog ID: {result['dialog_id']}")
        print(f"  第5轮共情答案: {result['round5_need_empathy']}")
        print()

def main():
    """
    主函数 - 执行提取流程
    """
    print("🚀 开始提取张俊杰关于第5轮共情问题的答案")
    print("=" * 60)
    
    # 配置文件路径
    INPUT_FILE = "all_records.json"
    OUTPUT_FILE = "zhang_junjie_empathy_answers.json"
    TARGET_NAME = "张俊杰"
    
    try:
        # 1. 加载所有记录
        all_records = load_all_records(INPUT_FILE)
        
        if not all_records:
            print("❌ 没有加载到任何记录，请检查文件路径")
            return 1
        
        # 2. 提取张俊杰的共情答案
        results = extract_empathy_answers(all_records, TARGET_NAME)
        
        if not results:
            print(f"❌ 未找到用户 '{TARGET_NAME}' 的任何记录")
            return 1
        
        # 3. 显示示例结果
        print_sample_results(results)
        
        # 4. 保存结果
        save_extraction_results(results, OUTPUT_FILE)
        
        # 5. 显示统计信息
        print("\n" + "=" * 60)
        print("📊 提取统计:")
        print(f"  - 目标用户: {TARGET_NAME}")
        print(f"  - 总记录数: {len(all_records)}")
        print(f"  - 提取记录数: {len(results)}")
        print(f"  - 输出文件: {OUTPUT_FILE}")
        
        # 显示答案分布
        answer_counts = {}
        for result in results:
            answer = result['round5_need_empathy']
            answer_counts[answer] = answer_counts.get(answer, 0) + 1
        
        print(f"\n📈 答案分布:")
        for answer, count in sorted(answer_counts.items()):
            print(f"  - '{answer}': {count} 次")
        
        print("=" * 60)
        print("🎉 提取完成!")
        
    except Exception as e:
        print(f"\n❌ 执行过程中出现错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 