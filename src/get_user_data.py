#!/usr/bin/env python3
"""
获取多维表格中特定填写人的所有字段数据

使用方法：
1. 直接调用函数获取数据
2. 从命令行获取用户输入

返回格式：JSON对象，key为字段名，value为该用户的填写内容
"""

import os
import json
import logging
from query import get_user_filled_data_from_env, save_json_to_file

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_user_data_interactive():
    """
    交互式获取提交人数据
    """
    print("=== 多维表格提交人数据获取工具 ===")
    print("请确保已设置以下环境变量：")
    print("- FEISHU_READ_APP_TOKEN")
    print("- FEISHU_READ_TABLE_ID") 
    print("- FEISHU_READ_VIEW_ID")
    print("- FEISHU_APP_ID")
    print("- FEISHU_APP_SECRET")
    print()
    
    # 检查环境变量
    required_env_vars = [
        "FEISHU_READ_APP_TOKEN",
        "FEISHU_READ_TABLE_ID", 
        "FEISHU_READ_VIEW_ID",
        "FEISHU_APP_ID",
        "FEISHU_APP_SECRET"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        return
    
    print("✅ 环境变量检查通过")
    print()
    
    # 获取用户输入
    target_submitter = input("请输入要查询的提交人名称: ").strip()
    if not target_submitter:
        print("❌ 提交人名称不能为空")
        return
    
    print(f"正在获取提交人 '{target_submitter}' 的数据...")
    
    # 获取数据
    user_data = get_user_filled_data_from_env(target_submitter)
    
    if not user_data:
        print(f"❌ 未找到提交人 '{target_submitter}' 的数据")
        return
    
    print(f"✅ 成功获取提交人 '{target_submitter}' 的数据")
    print(f"📊 共包含 {len(user_data)} 个字段")
    
    # 统计填写情况
    filled_count = sum(1 for v in user_data.values() if v is not None)
    empty_count = len(user_data) - filled_count
    
    print(f"📝 已填写字段: {filled_count}")
    print(f"📋 未填写字段: {empty_count}")
    print()
    
    # 询问是否保存
    save_option = input("是否保存到文件？(y/n): ").strip().lower()
    if save_option == 'y':
        filename = input(f"请输入文件名（默认: {target_submitter}_data.json）: ").strip()
        if not filename:
            filename = f"{target_submitter}_data.json"
        
        save_json_to_file(user_data, filename)
        print(f"✅ 数据已保存到 {filename}")
    
    # 询问是否显示详细数据
    show_option = input("是否显示详细数据？(y/n): ").strip().lower()
    if show_option == 'y':
        print("\n=== 详细数据 ===")
        for key, value in user_data.items():
            if value is not None:
                print(f"✅ {key}: {value}")
            else:
                print(f"❌ {key}: (未填写)")

def get_user_data_by_name(submitter_name: str, output_file: str = None) -> dict:
    """
    根据提交人名称获取数据
    
    Args:
        submitter_name: 提交人名称
        output_file: 可选的输出文件名
    
    Returns:
        dict: 提交人填写的数据
    """
    user_data = get_user_filled_data_from_env(submitter_name)
    
    if user_data and output_file:
        save_json_to_file(user_data, output_file)
        print(f"提交人 '{submitter_name}' 的数据已保存到 {output_file}")
    
    return user_data

def main():
    """
    主函数：交互式获取提交人数据
    """
    try:
        get_user_data_interactive()
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        logging.error(f"程序异常: {e}", exc_info=True)

if __name__ == "__main__":
    main() 