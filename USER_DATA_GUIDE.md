# 获取特定提交人数据的使用指南

## 功能概述

此功能允许您从飞书多维表格中获取特定提交人的所有字段数据，返回格式为 JSON 对象，其中：
- **key** 是字段名（问题名称）
- **value** 是该提交人的实际填写内容
- 如果某个字段未填写，则 value 为 `null`

## 返回格式示例

```json
{
  "编号": 1,
  "Q1-文本编号": "TEST001",
  "Q2：您觉得这组对话中，教练在第5轮对话中是否需要使用积极关注的技术？": "需要积极关注",
  "Q3：您觉得这组对话中，教练在第5轮中的回复，是否使用了积极关注的技术？": null,
  "提交人": "qwen-max-latest",
  "提交时间": "2024-01-01",
  "备注": null
}
```

## 使用方法

### 方法1：使用命令行工具

```bash
# 获取特定提交人数据
cd src
python query.py --get-user-data "提交人名称" --user-output "output.json"

# 示例：获取 "qwen-max-latest" 提交人的数据
python query.py --get-user-data "qwen-max-latest" --user-output "qwen_data.json"
```

### 方法2：使用交互式脚本

```bash
# 运行交互式脚本
cd src
python get_user_data.py
```

然后按提示输入提交人名称即可。

### 方法3：在代码中调用函数

```python
from src.query import get_user_filled_data_from_env, get_user_filled_data

# 方法A：从环境变量获取配置
user_data = get_user_filled_data_from_env("提交人名称")

# 方法B：直接传递参数
user_data = get_user_filled_data(
    app_token="your_app_token",
    table_id="your_table_id", 
    view_id="your_view_id",
    target_submitter="提交人名称"
)

# 处理返回的数据
if user_data:
    print(f"获取到 {len(user_data)} 个字段")
    for field_name, value in user_data.items():
        if value is not None:
            print(f"{field_name}: {value}")
        else:
            print(f"{field_name}: (未填写)")
```

## 环境变量设置

使用前请确保设置了以下环境变量：

```bash
export FEISHU_READ_APP_TOKEN="your_app_token"
export FEISHU_READ_TABLE_ID="your_table_id"
export FEISHU_READ_VIEW_ID="your_view_id"
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
```

## 主要函数说明

### `get_user_filled_data()`

```python
def get_user_filled_data(
    app_token: str, 
    table_id: str, 
    view_id: str, 
    target_submitter: str, 
    bearer_token: str = None
) -> dict:
```

**参数：**
- `app_token`: 飞书应用token
- `table_id`: 表格ID
- `view_id`: 视图ID
- `target_submitter`: 目标填写人名称
- `bearer_token`: 可选的token，不传则自动获取

**返回值：**
- `dict`: 包含该填写人所有字段信息的JSON对象

### `get_user_filled_data_from_env()`

```python
def get_user_filled_data_from_env(target_submitter: str) -> dict:
```

**参数：**
- `target_submitter`: 目标填写人名称

**返回值：**
- `dict`: 包含该填写人所有字段信息的JSON对象

## 特性

1. **完整性**：返回表格中的所有字段，包括未填写的字段（值为null）
2. **多记录合并**：如果同一用户有多条记录，会自动合并（后面的记录覆盖前面的记录）
3. **空值处理**：智能处理空字符串、空数组等情况，统一转换为null
4. **错误处理**：包含完整的错误处理和日志记录

## 使用场景

1. **数据导出**：将特定提交人的填写数据导出为JSON文件
2. **数据分析**：分析某个提交人的填写完整性
3. **数据对比**：对比不同提交人的填写情况
4. **报告生成**：为特定提交人生成个性化报告

## 注意事项

1. 确保已正确设置飞书应用的权限
2. 提交人名称必须与飞书表格中的"提交人"字段完全匹配
3. 返回的JSON对象中的字段名与飞书表格中的字段名完全一致
4. 空值统一用 `null` 表示，而不是空字符串或其他值

## 示例运行

```bash
# 运行完整示例
python example_usage.py
```

这将展示如何使用新功能获取提交人数据，并与空白模板进行对比。 