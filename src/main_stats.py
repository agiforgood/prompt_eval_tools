import os
import logging
from feishu_full_fetch import fetch_all_fields_from_bitable
from utils.feishu_client import get_tenant_access_token
from collections import Counter, defaultdict

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
    logging.info(f"共获取{len(records)}条记录。\n")

    # 统计所有字段名
    all_fields = set()
    for rec in records:
        all_fields.update(rec.keys())
    logging.info(f"所有字段名: {sorted(list(all_fields))}\n")

    # 统计每个提交人数量
    submitter_counter = Counter()
    for rec in records:
        submitter = rec.get("提交人", "(空)")
        submitter_counter[submitter] += 1
    logging.info("每个提交人记录数：")
    for submitter, count in submitter_counter.most_common():
        logging.info(f"  {submitter}: {count}")
    logging.info("")

    # 统计每个字段的非空率
    field_non_empty = defaultdict(int)
    for rec in records:
        for field in all_fields:
            if rec.get(field) not in [None, "", []]:
                field_non_empty[field] += 1
    logging.info("每个字段的非空率：")
    for field in sorted(all_fields):
        rate = round(field_non_empty[field] / len(records) * 100, 2) if records else 0
        logging.info(f"  {field}: {field_non_empty[field]}/{len(records)} ({rate}%)")

if __name__ == "__main__":
    main() 