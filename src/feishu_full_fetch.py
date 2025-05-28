import os
import logging
from typing import List, Dict, Any, Optional
import lark_oapi as lark
from lark_oapi import LogLevel
from lark_oapi.api.bitable.v1 import ListAppTableRecordRequest, ListAppTableRecordResponse
from utils.feishu_client import get_tenant_access_token  # 复用原有token获取逻辑

def fetch_all_fields_from_bitable(app_token: str, table_id: str, view_id: str, bearer_token: str) -> List[Dict[str, Any]]:
    """
    全量读取飞书多维表格所有字段。
    """
    client = lark.Client.builder() \
        .enable_set_token(True) \
        .log_level(LogLevel.WARNING) \
        .build()
    all_items = []
    page_token = None
    page_size = 100
    while True:
        request_builder = ListAppTableRecordRequest.builder() \
            .app_token(app_token) \
            .table_id(table_id) \
            .view_id(view_id) \
            .page_size(page_size) \
            .user_id_type("open_id")
        if page_token:
            request_builder = request_builder.page_token(page_token)
        request = request_builder.build()
        option = lark.RequestOption.builder().tenant_access_token(bearer_token).build()
        response: ListAppTableRecordResponse = client.bitable.v1.app_table_record.list(request, option)
        if response.success():
            data = response.data
            items = data.items if data and data.items else []
            all_items.extend(items)
            has_more = data.has_more if data else False
            page_token = data.page_token if data else None
            if not has_more or not page_token:
                break
        else:
            logging.error(f"Feishu API Error: {response.code}, {response.msg}")
            break
    # 返回所有原始fields
    result_list = []
    for item in all_items:
        record_dict = item.fields if hasattr(item, 'fields') else {}
        result_list.append(record_dict)
    return result_list

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
    logging.info(f"共获取{len(records)}条记录。前3条示例：")
    for i, rec in enumerate(records[:3]):
        logging.info(f"记录{i+1}: {rec}")
    # 也可以输出所有字段名合集
    all_fields = set()
    for rec in records:
        all_fields.update(rec.keys())
    logging.info(f"所有字段名: {sorted(list(all_fields))}")

if __name__ == "__main__":
    main()