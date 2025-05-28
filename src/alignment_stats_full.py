"""
文件：alignment_stats_full.py

功能说明：
------------------
本脚本用于对飞书多维表格的评估数据进行"全字段一致性统计"（alignment stats），并可扩展为main stats。

1. alignment stats（主功能）：
   - 读取飞书表格所有字段（通过feishu_full_fetch.py的fetch_all_fields_from_bitable函数）
   - 按"编号"分组，按"提交人"区分"人类专家"和"AI评估者"
   - 对指定字段（COMPARISON_FIELDS）进行详细一致性比对，输出：
     * 总体匹配率
     * 每个对话的匹配率
     * 每个字段的匹配率
     * 不一致明细
     * 全量详细对比

2. main stats（可扩展）：
   - 可在此基础上增加总条数、每个提交人数量、字段覆盖率等主统计信息
   - 如有需要可随时补充

入口：
-----
直接运行本文件即可：
    python src/alignment_stats_full.py

会自动读取环境变量配置，按提示输入"人类专家"和"AI评估者"的"提交人"名称。

依赖：
-----
- feishu_full_fetch.py（全字段读取）
- utils/feishu_client.py（token获取）
"""
import os
import logging
from typing import List, Dict, Tuple, Any
from feishu_full_fetch import fetch_all_fields_from_bitable
from utils.feishu_client import get_tenant_access_token

# 需要比对的字段列表（可根据实际表格调整）
COMPARISON_FIELDS = [
    "第5轮是否存在共情？",
    "第5轮回复共情程度是？",
    "第5轮共情对象是？",
    "第5轮共情是否匹配",
    "第5轮共情不匹配原因",
    "第5轮共情程度是否准确？",
    "第5轮共情程度不准确原因",
    "第5轮共情对象是否准确？",
    "第5轮共情对象错误原因",
    "第10轮是否存在共情？",
    "第10轮共情程度是？",
    "第10轮共情程度是否准确？",
    "第10轮共情程度不准确原因",
    "第10轮共情对象是？",
    "第10轮教练共情对象是否准确？",
    "第10轮共情对象错误原因",
    "第10轮共情是否匹配",
    "第10轮共情不匹配原因",
    "第5轮积极关注是否使用",
    "第5轮积极关注的对象是？",
    "第5轮积极关注对象是否准确？",
    "第5轮积极关注对象错误原因",
    "第10轮积极关注是否使用",
    "第10轮中积极关注的对象是？",
    "第10轮积极关注对象是否准确？",
    "第10轮积极关注对象错误原因"
]

def alignment_check(field_name: str, human_eval: Dict, ai_eval: Dict) -> bool:
    """
    检查某个字段在两份评估中的一致性。
    """
    human_value = human_eval.get(field_name)
    ai_value = ai_eval.get(field_name)
    if human_value is None and ai_value is None:
        return True
    if human_value is None or ai_value is None:
        return False
    return human_value == ai_value

def calculate_alignment_stats_full(
    records: List[Dict[str, Any]],
    human_expert_name: str,
    ai_evaluator_name: str
) -> Tuple[float, Dict[str, float], Dict[str, float], List[Tuple[Any, str, Any, Any]], Dict]:
    """
    基于全量字段数据，计算一致性统计。
    """
    # 按编号分组
    dialog_data = {}
    for record in records:
        dialog_id = record.get("编号")
        if dialog_id is None:
            continue
        if dialog_id not in dialog_data:
            dialog_data[dialog_id] = {"human": {}, "ai": {}}
        if record.get("提交人") == human_expert_name:
            dialog_data[dialog_id]["human"] = record
        elif record.get("提交人") == ai_evaluator_name:
            dialog_data[dialog_id]["ai"] = record

    total_comparisons = 0
    total_matches = 0
    dialog_matches = {}
    field_matches = {field: 0 for field in COMPARISON_FIELDS}
    mismatches = []

    for dialog_id, data in dialog_data.items():
        if not data["human"] or not data["ai"]:
            continue
        dialog_matches[dialog_id] = 0
        dialog_comparisons = 0
        for field in COMPARISON_FIELDS:
            if alignment_check(field, data["human"], data["ai"]):
                total_matches += 1
                dialog_matches[dialog_id] += 1
                field_matches[field] += 1
            else:
                mismatches.append((dialog_id, field, data["human"].get(field, "N/A"), data["ai"].get(field, "N/A")))
            total_comparisons += 1
            dialog_comparisons += 1
        if dialog_comparisons > 0:
            dialog_matches[dialog_id] = round(dialog_matches[dialog_id] / dialog_comparisons * 100, 2)

    overall_match_rate = round(total_matches / total_comparisons * 100, 2) if total_comparisons > 0 else 0
    field_match_rates = {field: round(field_matches[field] / len(dialog_data) * 100, 2) if len(dialog_data) > 0 else 0 for field in COMPARISON_FIELDS}
    return overall_match_rate, dialog_matches, field_match_rates, mismatches, dialog_data

def print_alignment_report_full(
    overall_match_rate: float,
    dialog_matches: Dict[str, float],
    field_match_rates: Dict[str, float],
    mismatches: List[Tuple[Any, str, Any, Any]],
    dialog_data: Dict
):
    """
    打印详细一致性报告。
    """
    logging.info("=== 评估一致性报告 ===")
    logging.info(f"总体匹配率: {overall_match_rate}%")
    logging.info("\n=== 每个对话的匹配率 ===")
    for dialog_id, match_rate in dialog_matches.items():
        logging.info(f"对话 {dialog_id}: {match_rate}%")
    logging.info("\n=== 每个字段的匹配率 ===")
    for field, match_rate in field_match_rates.items():
        logging.info(f"{field}: {match_rate}%")
    logging.info("\n=== 不一致的评估 ===")
    for dialog_id, field, human_value, ai_value in mismatches:
        logging.info(f"对话 {dialog_id} - {field}:")
        logging.info(f"  人类专家: {human_value}")
        logging.info(f"  AI评估者: {ai_value}")
        logging.info("---")
    # 详细对比
    logging.info("\n=== 详细对比（全量） ===")
    for dialog_id, data in dialog_data.items():
        if not data.get("human") or not data.get("ai"):
            continue
        logging.info(f"\n对话 {dialog_id}:")
        for field in COMPARISON_FIELDS:
            human_val = data["human"].get(field, "N/A")
            ai_val = data["ai"].get(field, "N/A")
            is_match = alignment_check(field, data["human"], data["ai"])
            logging.info(f"  字段 [{field}] | 人类: {human_val} | AI: {ai_val} | 一致: {is_match}")

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    app_token = os.getenv("FEISHU_READ_APP_TOKEN")
    table_id = os.getenv("FEISHU_READ_TABLE_ID")
    view_id = os.getenv("FEISHU_READ_VIEW_ID")
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    if not all([app_token, table_id, view_id, app_id, app_secret]):
        logging.error("请设置FEISHU_READ_APP_TOKEN, FEISHU_READ_TABLE_ID, FEISHU_READ_VIEW_ID, FEISHU_APP_ID, FEISHU_APP_SECRET环境变量")
        return
    token = get_tenant_access_token(app_id, app_secret)
    if not token:
        logging.error("获取tenant_access_token失败")
        return
    records = fetch_all_fields_from_bitable(app_token, table_id, view_id, token)
    logging.info(f"共获取{len(records)}条记录。")
    human_expert_name = input("请输入人类专家的名称: ")
    ai_evaluator_name = input("请输入AI评估者的名称: ")
    overall_match_rate, dialog_matches, field_match_rates, mismatches, dialog_data = calculate_alignment_stats_full(
        records,
        human_expert_name,
        ai_evaluator_name
    )
    print_alignment_report_full(
        overall_match_rate,
        dialog_matches,
        field_match_rates,
        mismatches,
        dialog_data
    )

if __name__ == "__main__":
    main() 