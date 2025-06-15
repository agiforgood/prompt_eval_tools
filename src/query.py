import os
import argparse
import json
import logging
from call_feishu import get_feishu_bearer_token, fetch_bitable_records_auto_token
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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

def save_json_to_file(data, filename: str):
    """
    将数据保存为json文件，支持中文。
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logging.info(f"已保存字段信息到 {filename}")

def generate_bitable_blank_template(fields_json):
    """
    根据字段结构生成空白模板schema，字段名为key，value为类型默认值。
    """
    schema = {}
    for field in fields_json:
        name = field['field_name']
        ui_type = field.get('ui_type')
        prop = field.get('property')
        if ui_type == 'Number':
            schema[name] = 0
        elif ui_type == 'Text':
            schema[name] = ''
        elif ui_type == 'SingleSelect':
            options = prop.get('options', []) if prop else []
            schema[name] = options[0]['name'] if options else ''
        elif ui_type == 'MultiSelect':
            options = prop.get('options', []) if prop else []
            schema[name] = [options[0]['name']] if options else []
        elif ui_type == 'Date':
            schema[name] = '2024-01-01'
        elif ui_type == 'Checkbox':
            schema[name] = False
        else:
            schema[name] = None
    return schema

def debug_tenant_access_token():
    """
    用 requests 直接调试 tenant_access_token 获取接口，打印原始HTTP响应。
    """
    app_id = os.getenv('FEISHU_APP_ID')
    app_secret = os.getenv('FEISHU_APP_SECRET')
    url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
    resp = requests.post(url, json={'app_id': app_id, 'app_secret': app_secret})
    print(f"HTTP状态码: {resp.status_code}")
    print(f"原始响应内容: {resp.text}")
    try:
        data = resp.json()
        if 'tenant_access_token' in data:
            print(f"\033[92m获取tenant_access_token成功: {data['tenant_access_token']}\033[0m")
        else:
            print(f"\033[91m未获取到tenant_access_token，返回内容: {data}\033[0m")
    except Exception as e:
        print(f"\033[91m响应内容不是合法JSON: {e}\033[0m")

def get_user_filled_data(app_token: str, table_id: str, view_id: str, target_submitter: str, bearer_token: str = None) -> dict:
    """
    获取特定填写人填写的所有字段信息，返回JSON格式
    
    Args:
        app_token: 飞书应用token
        table_id: 表格ID
        view_id: 视图ID
        target_submitter: 目标填写人名称
        bearer_token: 可选的bearer token，不传则自动获取
    
    Returns:
        dict: 包含该填写人所有字段信息的JSON对象
              {
                  "字段名1": "填写内容1",
                  "字段名2": "填写内容2",
                  "未填写字段": null,
                  ...
              }
    """
    # 获取所有记录
    if not bearer_token:
        bearer_token = get_feishu_bearer_token()
    if not bearer_token:
        logging.error("无法获取bearer token")
        return {}
    
    # 读取所有记录
    records = fetch_bitable_records_auto_token(app_token, table_id, view_id)
    if not records:
        logging.warning("未获取到任何记录")
        return {}
    
    # 获取字段信息以生成完整的字段列表
    all_fields = fetch_bitable_fields_with_token(app_token, table_id, bearer_token)
    field_names = [field['field_name'] for field in all_fields]
    
    # 查找目标填写人的记录
    user_records = []
    for record in records:
        submitter = record.get("提交人")
        if submitter == target_submitter:
            user_records.append(record)
    
    if not user_records:
        logging.warning(f"未找到填写人 '{target_submitter}' 的记录")
        return {}
    
    # 如果有多条记录，合并所有记录的数据（后面的覆盖前面的）
    merged_data = {}
    
    # 首先用null初始化所有字段
    for field_name in field_names:
        merged_data[field_name] = None
    
    # 然后填入用户实际填写的数据
    for record in user_records:
        for field_name, value in record.items():
            # 处理空值的情况
            if value is None or value == "" or value == []:
                merged_data[field_name] = None
            else:
                merged_data[field_name] = value
    
    logging.info(f"成功获取填写人 '{target_submitter}' 的数据，共 {len(user_records)} 条记录")
    return merged_data

def get_user_filled_data_from_env(target_submitter: str) -> dict:
    """
    从环境变量读取配置，获取特定提交人的数据
    
    Args:
        target_submitter: 目标提交人名称
    
    Returns:
        dict: 包含该提交人所有字段信息的JSON对象
    """
    app_token = os.getenv("FEISHU_READ_APP_TOKEN")
    table_id = os.getenv("FEISHU_READ_TABLE_ID")
    view_id = os.getenv("FEISHU_READ_VIEW_ID")
    
    if not app_token or not table_id:
        logging.error("请设置FEISHU_READ_APP_TOKEN和FEISHU_READ_TABLE_ID环境变量")
        return {}
    
    # 首先尝试使用view_id
    if view_id:
        logging.info(f"尝试使用view_id: {view_id}")
        user_data = get_user_filled_data(app_token, table_id, view_id, target_submitter)
        if user_data:
            return user_data
        else:
            logging.warning(f"使用view_id '{view_id}' 获取数据失败，尝试不使用view_id")
    
    # 如果没有view_id或使用view_id失败，则不使用view_id
    logging.info("不使用view_id获取数据")
    return get_user_filled_data(app_token, table_id, "", target_submitter)

def get_user_all_records(app_token: str, table_id: str, view_id: str, target_submitter: str, bearer_token: str = None) -> list:
    """
    获取特定提交人的所有记录，返回记录数组
    
    Args:
        app_token: 飞书应用token
        table_id: 表格ID
        view_id: 视图ID（如果为空字符串或None，则读取所有视图）
        target_submitter: 目标提交人名称
        bearer_token: 可选的bearer token，不传则自动获取
    
    Returns:
        list: 包含该提交人所有记录的数组，每个元素是一条完整记录
              [
                  {"编号": 1, "Q1文本编号": "1", "提交人": "张俊杰", ...},
                  {"编号": 2, "Q1文本编号": "2", "提交人": "张俊杰", ...},
                  ...
              ]
    """
    # 获取所有记录
    if not bearer_token:
        bearer_token = get_feishu_bearer_token()
    if not bearer_token:
        logging.error("无法获取bearer token")
        return []
    
    # 读取所有记录 - 如果view_id为空，则使用修改后的函数
    if not view_id:
        logging.info("未指定view_id，将尝试读取所有记录")
        records = fetch_bitable_records_with_token(app_token, table_id, "", bearer_token)
    else:
        try:
            records = fetch_bitable_records_auto_token(app_token, table_id, view_id)
        except Exception as e:
            logging.warning(f"使用view_id获取数据失败: {e}，尝试不使用view_id")
            records = fetch_bitable_records_with_token(app_token, table_id, "", bearer_token)
    
    if not records:
        logging.warning("未获取到任何记录")
        return []
    
    # 获取字段信息以生成完整的字段列表
    all_fields = fetch_bitable_fields_with_token(app_token, table_id, bearer_token)
    field_names = [field['field_name'] for field in all_fields]
    
    # 查找目标提交人的所有记录
    user_records = []
    for record in records:
        submitter = record.get("提交人")
        if submitter == target_submitter:
            # 为每条记录补全所有字段（未填写的设为null）
            complete_record = {}
            for field_name in field_names:
                value = record.get(field_name)
                if value is None or value == "" or value == []:
                    complete_record[field_name] = None
                else:
                    complete_record[field_name] = value
            user_records.append(complete_record)
    
    if not user_records:
        logging.warning(f"未找到提交人 '{target_submitter}' 的记录")
        return []
    
    # 按编号排序
    user_records.sort(key=lambda x: int(x.get("编号", 0)) if str(x.get("编号", "")).isdigit() else 0)
    
    logging.info(f"成功获取提交人 '{target_submitter}' 的数据，共 {len(user_records)} 条记录")
    return user_records

def get_user_all_records_from_env(target_submitter: str) -> list:
    """
    从环境变量读取配置，获取特定提交人的所有记录数组
    
    Args:
        target_submitter: 目标提交人名称
    
    Returns:
        list: 包含该提交人所有记录的数组
    """
    app_token = os.getenv("FEISHU_READ_APP_TOKEN")
    table_id = os.getenv("FEISHU_READ_TABLE_ID")
    view_id = os.getenv("FEISHU_READ_VIEW_ID")
    
    if not app_token or not table_id:
        logging.error("请设置FEISHU_READ_APP_TOKEN和FEISHU_READ_TABLE_ID环境变量")
        return []
    
    # 首先尝试使用view_id
    if view_id:
        logging.info(f"尝试使用view_id: {view_id}")
        user_records = get_user_all_records(app_token, table_id, view_id, target_submitter)
        if user_records:
            return user_records
        else:
            logging.warning(f"使用view_id '{view_id}' 获取数据失败，尝试不使用view_id")
    
    # 如果没有view_id或使用view_id失败，则不使用view_id
    logging.info("不使用view_id获取数据")
    return get_user_all_records(app_token, table_id, "", target_submitter)

def main():
    """
    主流程：获取token，读取env中的app_token和table_id，分页获取所有字段，保存为json文件。
    支持 --gen-template 参数，自动生成空白模板schema。
    支持 --get-user-data 参数，获取特定用户的填写数据。
    """
    parser = argparse.ArgumentParser(description="飞书多维表格字段导出工具（只导出字段信息）")
    parser.add_argument("--output", "-o", type=str, default="fields.json", help="输出json文件名，默认fields.json")
    parser.add_argument("--gen-template", type=str, help="生成空白模板schema的json文件名")
    parser.add_argument("--debug-token", action="store_true", help="调试tenant_access_token获取，打印原始HTTP响应")
    parser.add_argument("--get-user-data", type=str, help="获取特定提交人的数据（合并格式），参数为提交人名称")
    parser.add_argument("--get-user-records", type=str, help="获取特定提交人的所有记录（数组格式），参数为提交人名称")
    parser.add_argument("--user-output", type=str, help="指定用户数据输出文件名，配合--get-user-data或--get-user-records使用")
    args = parser.parse_args()

    if args.debug_token:
        debug_tenant_access_token()
        return

    # 获取特定提交人数据（合并格式）
    if args.get_user_data:
        user_data = get_user_filled_data_from_env(args.get_user_data)
        if user_data:
            output_file = args.user_output or f"{args.get_user_data}_data.json"
            save_json_to_file(user_data, output_file)
            print(f"提交人 '{args.get_user_data}' 的数据已保存到 {output_file}")
        else:
            print(f"未找到提交人 '{args.get_user_data}' 的数据")
        return

    # 获取特定提交人的所有记录（数组格式）
    if args.get_user_records:
        user_records = get_user_all_records_from_env(args.get_user_records)
        if user_records:
            output_file = args.user_output or f"{args.get_user_records}_records.json"
            save_json_to_file(user_records, output_file)
            print(f"提交人 '{args.get_user_records}' 的所有记录已保存到 {output_file}")
            print(f"共包含 {len(user_records)} 条记录")
        else:
            print(f"未找到提交人 '{args.get_user_records}' 的记录")
        return

    app_token = os.getenv("FEISHU_READ_APP_TOKEN")
    table_id = os.getenv("FEISHU_READ_TABLE_ID")
    if not app_token or not table_id:
        logging.error("请设置FEISHU_READ_APP_TOKEN和FEISHU_READ_TABLE_ID环境变量")
        exit(1)

    token = get_feishu_bearer_token()
    if not token:
        logging.error("无法获取tenant_access_token，无法查询字段信息")
        exit(1)

    fields = fetch_bitable_fields_with_token(app_token, table_id, token)
    if not fields:
        logging.error("未获取到任何字段信息")
        exit(1)

    save_json_to_file(fields, args.output)
    print(f"字段信息已保存到 {args.output}")

    # 如果指定了 --gen-template，则生成空白模板
    if args.gen_template:
        blank_schema = generate_bitable_blank_template(fields)
        save_json_to_file(blank_schema, args.gen_template)
        print(f"空白模板已保存到 {args.gen_template}")

if __name__ == "__main__":
    main()