# Mideas Server API 文档

## 基本信息

- **Base URL**: `http://localhost:18888/mideasserver`
- **请求方法**: 所有接口统一使用 `POST` 方法
- **参数传递**: 所有参数通过 request body（JSON 格式）传递
- **响应格式**: JSON

## 通用响应格式

### 成功响应
```json
{
  "code": 0,
  "data": {},
  "message": "操作成功"
}
```

### 错误响应
```json
{
  "code": 400/404/500,
  "message": "错误描述",
  "detail": "详细信息"
}
```

## 接口列表

### 1. 智能体定时任务管理

#### 1.1 创建定时任务

**接口地址**: `POST /mideasserver/task/agentTasks/create`

**速率限制**: 20次/分钟

**请求参数**:
```json
{
  "task_name": "string (必填)",
  "task_info": "string (可选)",
  "task_conf": "string (必填)",
  "task_prompt": "string (可选)",
  "task_status": 1
}
```

**参数说明**:
- `task_name`: 任务名称
- `task_info`: 任务信息描述
- `task_conf`: 任务执行时间配置（格式：时 日 月 周）
  - 格式：`时 日 月 周`（用空格分隔）
  - 示例：
    - `"6,8 * * *"` - 每天6点和8点执行
    - `"20 * * 0"` - 每周日晚8点执行
    - `"9 1 * *"` - 每月1号早9点执行
    - `"14 * * 1-5"` - 每周一到周五下午2点执行
  - 字段说明：
    - 时：0-23
    - 日：1-31
    - 月：1-12
    - 周：0-6（0表示周日）
    - `*` 表示任意值
    - `,` 表示多个值（如：6,8,10）
    - `-` 表示范围（如：1-5）
- `task_prompt`: 任务提示词
- `task_status`: 任务状态（0:关闭 1:开启，默认为1）

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "task_id": 1,
    "task_name": "每日报告",
    "task_info": "生成每日数据报告",
    "task_conf": "6,8 * * *",
    "task_prompt": "生成昨日数据统计报告",
    "task_status": 1,
    "insert_time": "2026-02-21 10:30",
    "update_time": "2026-02-21 10:30"
  },
  "message": "定时任务创建成功"
}
```

---

#### 1.2 获取所有定时任务

**接口地址**: `POST /mideasserver/task/agentTasks/list`

**速率限制**: 60次/分钟

**请求参数**: 无需参数（空 body 或 `{}`）

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "task_id": 1,
        "task_name": "每日报告",
        "task_info": "生成每日数据报告",
        "task_conf": "6,8 * * *",
        "task_prompt": "生成昨日数据统计报告",
        "task_status": 1,
        "insert_time": "2026-02-21 10:30",
        "update_time": "2026-02-21 10:30"
      }
    ],
    "total": 1
  },
  "message": "查询成功"
}
```

---

#### 1.3 获取单个定时任务

**接口地址**: `POST /mideasserver/task/agentTasks/get`

**速率限制**: 60次/分钟

**请求参数**:
```json
{
  "task_id": 1
}
```

**参数说明**:
- `task_id`: 任务ID（必填）

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "task_id": 1,
    "task_name": "每日报告",
    "task_info": "生成每日数据报告",
    "task_conf": "6,8 * * *",
    "task_prompt": "生成昨日数据统计报告",
    "task_status": 1,
    "insert_time": "2026-02-21 10:30",
    "update_time": "2026-02-21 10:30"
  },
  "message": "查询成功"
}
```

**错误响应**:
```json
{
  "code": 404,
  "message": "任务不存在"
}
```

---

#### 1.4 更新定时任务

**接口地址**: `POST /mideasserver/task/agentTasks/update`

**速率限制**: 30次/分钟

**请求参数**:
```json
{
  "task_id": 1,
  "task_name": "string (可选)",
  "task_info": "string (可选)",
  "task_conf": "string (可选)",
  "task_prompt": "string (可选)",
  "task_status": 0
}
```

**参数说明**:
- `task_id`: 任务ID（必填）
- 其他字段均为可选，只更新提供的字段

**响应示例**:
```json
{
  "code": 0,
  "message": "更新成功"
}
```

**错误响应**:
```json
{
  "code": 404,
  "message": "任务不存在"
}
```

或

```json
{
  "code": 400,
  "message": "没有提供更新字段"
}
```

---

#### 1.5 删除定时任务

**接口地址**: `POST /mideasserver/task/agentTasks/delete`

**速率限制**: 20次/分钟

**请求参数**:
```json
{
  "task_id": 1
}
```

**参数说明**:
- `task_id`: 任务ID（必填）

**响应示例**:
```json
{
  "code": 0,
  "message": "删除成功"
}
```

**错误响应**:
```json
{
  "code": 404,
  "message": "任务不存在"
}
```

---

### 2. Agent 接口

#### 2.1 GPT Research

**接口地址**: `POST /mideasserver/agent/gptresearch`

**速率限制**: 1次/分钟

**请求参数**: 无需参数（空 body 或 `{}`）

**响应示例**:
```json
{
  "code": 0,
  "message": "GPT Research 接口"
}
```

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 429 | 超过速率限制 |
| 500 | 服务器内部错误 |

## 调用示例

### cURL 示例

```bash
# 创建定时任务
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "每日报告",
    "task_info": "生成每日数据报告",
    "task_conf": "6,8 * * *",
    "task_prompt": "生成昨日数据统计报告",
    "task_status": 1
  }'

# 获取所有定时任务
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/list \
  -H "Content-Type: application/json" \
  -d '{}'

# 获取单个定时任务
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/get \
  -H "Content-Type: application/json" \
  -d '{"task_id": 1}'

# 更新定时任务
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/update \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 1,
    "task_status": 0
  }'

# 删除定时任务
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/delete \
  -H "Content-Type: application/json" \
  -d '{"task_id": 1}'
```

### Python 示例

```python
import requests

base_url = "http://localhost:18888/mideasserver"

# 创建定时任务
response = requests.post(
    f"{base_url}/task/agentTasks/create",
    json={
        "task_name": "每日报告",
        "task_info": "生成每日数据报告",
        "task_conf": "6,8 * * *",
        "task_prompt": "生成昨日数据统计报告",
        "task_status": 1
    }
)
print(response.json())

# 获取所有定时任务
response = requests.post(f"{base_url}/task/agentTasks/list", json={})
print(response.json())

# 获取单个定时任务
response = requests.post(
    f"{base_url}/task/agentTasks/get",
    json={"task_id": 1}
)
print(response.json())

# 更新定时任务
response = requests.post(
    f"{base_url}/task/agentTasks/update",
    json={"task_id": 1, "task_status": 0}
)
print(response.json())

# 删除定时任务
response = requests.post(
    f"{base_url}/task/agentTasks/delete",
    json={"task_id": 1}
)
print(response.json())
```

## 注意事项

1. 所有接口统一使用 POST 方法
2. 请求头必须包含 `Content-Type: application/json`
3. 所有参数通过 request body 传递
4. 注意各接口的速率限制，超过限制会返回 429 错误
5. `task_conf` 配置格式必须正确，否则定时任务可能无法正常执行
6. 时间格式统一为 `YYYY-MM-DD HH:MM`
