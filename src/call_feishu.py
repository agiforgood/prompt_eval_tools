import os
import json
import logging
from typing import List, Dict, Any, Optional
import argparse
import requests

# lark-oapi SDK 相关导入
import lark_oapi as lark
from lark_oapi import LogLevel
from lark_oapi.api.bitable.v1 import ListAppTableRecordRequest, ListAppTableRecordResponse, BatchCreateAppTableRecordRequest, BatchCreateAppTableRecordRequestBody
from lark_oapi.api.auth.v3 import InternalTenantAccessTokenRequest, InternalTenantAccessTokenRequestBody, InternalTenantAccessTokenResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_tenant_access_token(app_id: str, app_secret: str) -> Optional[str]:
    """
    用App ID和App Secret获取飞书tenant_access_token。
    返回token字符串，失败返回None。
    增强错误打印，便于排查问题。
    """
    client = lark.Client.builder().log_level(LogLevel.WARNING).build()
    request_body = InternalTenantAccessTokenRequestBody.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .build()
    request = InternalTenantAccessTokenRequest.builder().request_body(request_body).build()
    try:
        response: InternalTenantAccessTokenResponse = client.auth.v3.tenant_access_token.internal(request)
        # 打印原始响应内容，便于排查
        logging.error(f"[DEBUG] tenant_access_token接口原始响应: {getattr(response, '__dict__', str(response))}")
        if response.success():
            token = getattr(response, 'tenant_access_token', None)
            if token:
                logging.info("成功获取tenant_access_token")
                return token
            else:
                logging.error(f"响应中未找到tenant_access_token，app_id={app_id}, 原始响应内容: {getattr(response, '__dict__', str(response))}")
        else:
            logging.error(f"获取tenant_access_token失败: code={response.code}, msg={response.msg}, app_id={app_id}, 原始响应内容: {getattr(response, '__dict__', str(response))}")
    except Exception as e:
        logging.error(f"获取tenant_access_token异常: {e}, app_id={app_id}")
    return None

def get_feishu_bearer_token() -> Optional[str]:
    """
    用 requests 直接获取 tenant_access_token，兼容所有飞书版本。
    """
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    if app_id and app_secret:
        resp = requests.post(url, json={"app_id": app_id, "app_secret": app_secret})
        try:
            data = resp.json()
            if "tenant_access_token" in data:
                logging.info("成功获取tenant_access_token")
                return data["tenant_access_token"]
            else:
                logging.error(f"未获取到tenant_access_token，返回内容: {data}")
        except Exception as e:
            logging.error(f"解析token响应异常: {e}, 原始内容: {resp.text}")
    bearer_token = os.getenv("FEISHU_BEARER_TOKEN")
    if bearer_token:
        logging.info("使用环境变量FEISHU_BEARER_TOKEN作为token")
        return bearer_token
    logging.error("无法获取任何可用的飞书token，请检查环境变量配置")
    return None

def fetch_bitable_records_auto_token(app_token: str, table_id: str, view_id: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    自动获取token（优先App ID/Secret，失败用Bearer Token），读取飞书多维表格。
    可指定fields参数（字段名列表），不指定则读取全部。
    返回记录字典列表。
    """
    token = get_feishu_bearer_token()
    if not token:
        logging.error("飞书token获取失败，无法读取表格")
        return []
    return fetch_bitable_records_with_token(app_token, table_id, view_id, token, fields)

def fetch_bitable_records_with_token(app_token: str, table_id: str, view_id: str, bearer_token: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    用指定token从飞书多维表格读取记录。
    可指定fields参数（字段名列表），不指定则读取全部。
    如果view_id为空字符串或None，则不指定视图（读取所有记录）。
    返回记录字典列表。
    """
    client = lark.Client.builder().enable_set_token(True).log_level(LogLevel.WARNING).build()
    all_items = []
    page_token = None
    page_size = 100
    try:
        while True:
            request_builder = ListAppTableRecordRequest.builder() \
                .app_token(app_token) \
                .table_id(table_id) \
                .page_size(page_size) \
                .user_id_type("open_id")
            
            # 只有当view_id不为空时才设置view_id
            if view_id:
                request_builder = request_builder.view_id(view_id)
            if fields:
                request_builder = request_builder.field_names(json.dumps(fields, ensure_ascii=False))
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
                logging.error(f"飞书API读取失败: code={response.code}, msg={response.msg}")
                break
    except lark.exception.ApiException as e:
        logging.error(f"Lark SDK API异常: code={e.code}, msg={e.msg}, log_id={e.log_id}")
    except Exception as e:
        logging.error(f"飞书表格读取异常: {e}")
    # 返回fields字典
    result_list = []
    for item in all_items:
        record_dict = item.fields if hasattr(item, 'fields') else {}
        result_list.append(record_dict)
    return result_list

def write_records_to_bitable(app_token: str, table_id: str, records: List[Dict[str, Any]], bearer_token: Optional[str] = None) -> dict:
    """
    批量写入记录到飞书多维表格。
    records为字典列表，每个字典为一行，key为字段名。
    bearer_token可不传，自动获取。
    返回写入结果dict。
    """
    if not records:
        logging.warning("没有可写入的记录")
        return {"success": True, "response": None}
    if not bearer_token:
        bearer_token = get_feishu_bearer_token()
    if not bearer_token:
        logging.error("写入飞书表格失败：无法获取token")
        return {"success": False, "response": None, "msg": "token获取失败"}
    client = lark.Client.builder().enable_set_token(True).log_level(LogLevel.WARNING).build()
    formatted_records = [{"fields": record} for record in records]
    request_body = BatchCreateAppTableRecordRequestBody.builder().records(formatted_records).build()
    request = BatchCreateAppTableRecordRequest.builder() \
        .app_token(app_token) \
        .table_id(table_id) \
        .request_body(request_body) \
        .build()
    option = lark.RequestOption.builder().tenant_access_token(bearer_token).build()
    try:
        response = client.bitable.v1.app_table_record.batch_create(request, option)
        if response.success():
            logging.info(f"成功写入{len(records)}条记录到飞书表格")
            return {"success": True, "response": _serialize_response(response)}
        else:
            logging.error(f"写入飞书表格失败: code={response.code}, msg={response.msg}")
            # 字段名校验
            if response.code == 1254045:
                all_field_names = set()
                for record in records:
                    if isinstance(record, dict):
                        all_field_names.update(record.keys())
                logging.error(f"本批次尝试写入的字段名: {sorted(list(all_field_names))}")
                logging.error(f"原始写入数据: {json.dumps(records, indent=2, ensure_ascii=False)}")
            return {"success": False, "response": _serialize_response(response), "code": getattr(response, 'code', None), "msg": getattr(response, 'msg', None)}
    except Exception as e:
        logging.error(f"写入飞书表格异常: {e}")
        return {"success": False, "response": str(e), "code": None, "msg": str(e)}

def _serialize_response(response):
    """
    尝试将lark-oapi的response对象转为可序列化的dict。
    """
    try:
        if hasattr(response, 'to_dict'):
            return response.to_dict()
        elif hasattr(response, '__dict__'):
            return dict(response.__dict__)
        else:
            return str(response)
    except Exception as e:
        return f"无法序列化response: {e}"

def fetch_bitable_fields_with_token(app_token: str, table_id: str, bearer_token: str) -> list:
    """
    用指定token从飞书多维表格获取所有字段信息（自动分页）。
    返回字段信息的列表（含所有详细内容）。
    """
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    all_fields = []
    page_token = None
    while True:
        params = {"page_size": 20}
        if page_token:
            params["page_token"] = page_token
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            logging.error(f"飞书字段API请求失败: {resp.status_code}, {resp.text}")
            break
        data = resp.json().get("data", {})
        fields = data.get("items", [])
        all_fields.extend(fields)
        if data.get("has_more") and data.get("page_token"):
            page_token = data["page_token"]
        else:
            break
    return all_fields

def fetch_all_bitable_fields_auto_token(app_token: str, table_id: str) -> list:
    """
    自动获取token并获取所有字段信息。
    """
    token = get_feishu_bearer_token()
    if not token:
        logging.error("无法获取tenant_access_token，无法查询字段信息")
        return []
    return fetch_bitable_fields_with_token(app_token, table_id, token)

def save_json_to_file(data, filename: str):
    """
    将数据保存为json文件，支持中文。
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logging.info(f"已保存字段信息到 {filename}")

if __name__ == "__main__":
    # 命令行参数解析
    parser = argparse.ArgumentParser(description="飞书多维表格字段导出工具")
    parser.add_argument("--output", "-o", type=str, default="fields.json", help="输出json文件名，默认fields.json")
    args = parser.parse_args()

    # 读取环境变量
    app_token = os.getenv("FEISHU_READ_APP_TOKEN")
    table_id = os.getenv("FEISHU_READ_TABLE_ID")
    if not app_token or not table_id:
        logging.error("请设置FEISHU_READ_APP_TOKEN和FEISHU_READ_TABLE_ID环境变量")
        exit(1)

    # 查询字段
    fields = fetch_all_bitable_fields_auto_token(app_token, table_id)
    if not fields:
        logging.error("未获取到任何字段信息")
        exit(1)

    # 保存为json
    save_json_to_file(fields, args.output)
    print(f"字段信息已保存到 {args.output}") 