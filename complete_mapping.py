#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的字段映射关系配置
基于提供的JSON数据分析得出
"""

# 完整的字段映射关系（新字段名 -> 旧字段名）
COMPLETE_FIELD_MAPPING = {
    # 基本信息字段
    "id": "编号",
    "text_id": "Q1文本编号", 
    "submitter": "提交人",
    
    # 第5轮对话 - 积极关注
    "round5_need_positive_attention": "Q2您觉得这组对话中，教练在第5轮对话中是否需要使用积极关注的技术？",
    "round5_used_positive_attention": "Q3您觉得这组对话中，教练在第5轮中的回复，是否使用了积极关注的技术？",
    "round5_positive_attention_example": "Q3-1您觉得这组对话里，教练在第5轮对话中应该如何从正向角度反馈来访者提及的感受，想法或者行为？请根据该角度提供一个正向反馈的范例。",
    
    # 第5轮对话 - 共情
    "round5_empathy_target_needed": "Q4-1您觉得这组对话中，教练在第5轮对话中需要共情的对象是？",
    "round5_has_empathy": "Q5您觉得这组对话中，教练在第5轮中的回复，是否存在共情？",
    "round5_empathy_target_accuracy": "Q5-2请问教练在第5轮中，共情对象是否准确？",
    "round5_empathy_improvement": "Q5-5请问教练在第5轮中应该如何回复，共情程度才是合适的？请提供一个您认为合适的回复范例。",
    
    # 第10轮对话 - 积极关注
    "round10_need_positive_attention": "Q6您觉得这组对话中，教练在第10轮对话中是否需要使用积极关注的技术？",
    "round10_used_positive_attention": "Q7您觉得这组对话中，教练在第10轮中的回复，是否使用了积极关注的技术？",
    "round10_positive_attention_example": "Q7-1您觉得这组对话里，教练在第10轮对话中应该如何从正向角度反馈来访者提及的感受，想法或者行为？请根据该角度提供一个正向反馈的范例。",
    
    # 第10轮对话 - 共情
    "round10_need_empathy": "Q8您觉得这组对话中，教练在第10轮对话中是否需要共情？",
    "round10_empathy_target_needed": "Q8-1您觉得这组对话中，教练在第10轮对话中需要共情的对象是？",
    "round10_has_empathy": "Q9您觉得这组对话中，教练在第10轮中的回复，是否存在共情？",
    "round10_empathy_target_actual": "Q9-1请问教练在第10轮中，实际回复的共情对象是？",
    "round10_empathy_target_accuracy": "Q9-2请问教练在第10轮中，共情对象是否准确？",
    "round10_empathy_consistency": "Q9-3请问教练在第10轮中的回复，教练的共情回复和来访者情绪是否一致？",
    "round10_empathy_consistency_supplement": "Q9-3请问教练在第10轮中的回复，教练的共情回复和来访者情绪是否一致？-不一致-补充内容",
    "round10_empathy_depth": "Q9-4请问教练在第10轮中的回复，教练回复的共情程度是？",
    "round10_empathy_improvement": "Q9-5请问教练在第10轮中应该如何回复，共情程度才是合适的？请提供一个您认为合适的回复范例。"
}

# 您原始的映射关系（用于对比验证）
ORIGINAL_MAPPING = {
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

def compare_mappings():
    """
    比较原始映射和实际数据中的字段，找出差异
    """
    print("🔍 映射关系分析：")
    print("="*50)
    
    # 实际数据中的字段（从您提供的JSON数据中提取）
    actual_fields_in_data = [
        "编号", "Q1文本编号", "提交人",
        "Q2您觉得这组对话中，教练在第5轮对话中是否需要使用积极关注的技术？",
        "Q3您觉得这组对话中，教练在第5轮中的回复，是否使用了积极关注的技术？",
        "Q3-1您觉得这组对话里，教练在第5轮对话中应该如何从正向角度反馈来访者提及的感受，想法或者行为？请根据该角度提供一个正向反馈的范例。",
        "Q4-1您觉得这组对话中，教练在第5轮对话中需要共情的对象是？",
        "Q5您觉得这组对话中，教练在第5轮中的回复，是否存在共情？",
        "Q5-2请问教练在第5轮中，共情对象是否准确？",
        "Q5-5请问教练在第5轮中应该如何回复，共情程度才是合适的？请提供一个您认为合适的回复范例。",
        "Q6您觉得这组对话中，教练在第10轮对话中是否需要使用积极关注的技术？",
        "Q7您觉得这组对话中，教练在第10轮中的回复，是否使用了积极关注的技术？",
        "Q7-1您觉得这组对话里，教练在第10轮对话中应该如何从正向角度反馈来访者提及的感受，想法或者行为？请根据该角度提供一个正向反馈的范例。",
        "Q8您觉得这组对话中，教练在第10轮对话中是否需要共情？",
        "Q8-1您觉得这组对话中，教练在第10轮对话中需要共情的对象是？",
        "Q9您觉得这组对话中，教练在第10轮中的回复，是否存在共情？",
        "Q9-1请问教练在第10轮中，实际回复的共情对象是？",
        "Q9-2请问教练在第10轮中，共情对象是否准确？",
        "Q9-3请问教练在第10轮中的回复，教练的共情回复和来访者情绪是否一致？",
        "Q9-3请问教练在第10轮中的回复，教练的共情回复和来访者情绪是否一致？-不一致-补充内容",
        "Q9-4请问教练在第10轮中的回复，教练回复的共情程度是？",
        "Q9-5请问教练在第10轮中应该如何回复，共情程度才是合适的？请提供一个您认为合适的回复范例。"
    ]
    
    # 您原始映射中的字段
    original_mapped_fields = set(ORIGINAL_MAPPING.values())
    actual_fields_set = set(actual_fields_in_data)
    
    # 找出您映射中不存在的字段
    missing_in_mapping = actual_fields_set - original_mapped_fields
    # 找出您映射中多余的字段
    extra_in_mapping = original_mapped_fields - actual_fields_set
    
    print(f"📊 数据中实际字段数量: {len(actual_fields_in_data)}")
    print(f"📊 您的映射字段数量: {len(ORIGINAL_MAPPING)}")
    
    if missing_in_mapping:
        print(f"\n⚠️  您的映射中缺少的字段 ({len(missing_in_mapping)} 个):")
        for field in missing_in_mapping:
            print(f"  - {field}")
    
    if extra_in_mapping:
        print(f"\n❓ 您的映射中多余的字段 ({len(extra_in_mapping)} 个):")
        for field in extra_in_mapping:
            print(f"  - {field}")
    
    if not missing_in_mapping and not extra_in_mapping:
        print("✅ 映射关系完全匹配!")

if __name__ == "__main__":
    compare_mappings() 