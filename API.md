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

### 2. 任务执行记录管理

#### 2.1 获取任务执行历史列表

**接口地址**: `POST /mideasserver/task/agentTasks/getExecutionList`

**速率限制**: 60次/分钟

**请求参数**:
```json
{
  "task_id": 1,
  "status": 1,
  "size": 10,
  "start": 0
}
```

**参数说明**:
- `task_id`: 任务ID（可选，不传则查询所有任务的执行记录）
- `status`: 执行状态（可选）
  - `0`: 运行中
  - `1`: 成功
  - `2`: 失败
- `size`: 每页数量（必填，默认100）
- `start`: 起始位置，从0开始（必填，默认0）

**分页说明**:
- 第1页：`start=0, size=10`（第1-10条）
- 第2页：`start=10, size=10`（第11-20条）
- 第3页：`start=20, size=10`（第21-30条）

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "execution_id": 1,
        "task_id": 1,
        "task_name": "每日报告",
        "task_prompt": "生成昨日数据统计报告",
        "status": 1,
        "start_time": "2026-02-22 06:00:00",
        "end_time": "2026-02-22 06:05:30",
        "execution_duration": 330,
        "result_summary": "报告生成成功，共分析了1000条数据...",
        "result_detail": "完整的报告内容...",
        "error_message": null,
        "error_detail": null,
        "created_at": "2026-02-22 06:00:00",
        "updated_at": "2026-02-22 06:05:30"
      }
    ],
    "total": 50,
    "size": 10,
    "start": 0
  },
  "message": "查询成功"
}
```

---

#### 2.2 获取任务执行记录详情

**接口地址**: `POST /mideasserver/task/agentTasks/getExecutionDetail`

**速率限制**: 60次/分钟

**请求参数**:
```json
{
  "execution_id": 1
}
```

**参数说明**:
- `execution_id`: 执行记录ID（必填）

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "execution_id": 1,
    "task_id": 1,
    "task_name": "每日报告",
    "task_prompt": "生成昨日数据统计报告",
    "status": 1,
    "start_time": "2026-02-22 06:00:00",
    "end_time": "2026-02-22 06:05:30",
    "execution_duration": 330,
    "result_summary": "报告生成成功，共分析了1000条数据...",
    "result_detail": "# 每日数据统计报告\n\n## 概述\n...\n完整的报告内容（Markdown格式）",
    "error_message": null,
    "error_detail": null,
    "created_at": "2026-02-22 06:00:00",
    "updated_at": "2026-02-22 06:05:30"
  },
  "message": "查询成功"
}
```

**错误响应**:
```json
{
  "code": 404,
  "message": "执行记录不存在"
}
```

---

#### 2.3 获取任务最新执行日志

**接口地址**: `POST /mideasserver/task/agentTasks/logs/latest`

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
    "execution_id": 5,
    "task_id": 1,
    "task_name": "每日报告",
    "task_prompt": "生成昨日数据统计报告",
    "status": 1,
    "start_time": "2026-02-22 08:00:00",
    "end_time": "2026-02-22 08:04:15",
    "execution_duration": 255,
    "result_summary": "报告生成成功...",
    "result_detail": "完整报告内容...",
    "error_message": null,
    "error_detail": null,
    "created_at": "2026-02-22 08:00:00",
    "updated_at": "2026-02-22 08:04:15"
  },
  "message": "查询成功"
}
```

**错误响应**:
```json
{
  "code": 404,
  "message": "未找到执行日志"
}
```

---

#### 2.4 获取任务执行统计

**接口地址**: `POST /mideasserver/task/agentTasks/logs/stats`

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
    "total_executions": 50,
    "success_count": 48,
    "failure_count": 1,
    "running_count": 1,
    "avg_duration": 285.5,
    "last_execution": {
      "execution_id": 50,
      "start_time": "2026-02-22 08:00:00",
      "status": 1,
      "duration": 255
    }
  },
  "message": "查询成功"
}
```

**字段说明**:
- `total_executions`: 总执行次数
- `success_count`: 成功次数
- `failure_count`: 失败次数
- `running_count`: 运行中次数
- `avg_duration`: 平均执行时长（秒）
- `last_execution`: 最后一次执行信息
  - `execution_id`: 执行记录ID
  - `start_time`: 开始时间
  - `status`: 执行状态
  - `duration`: 执行时长（秒）

---

### 3. Agent 接口

#### 3.1 GPT Research

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

# 获取任务执行历史列表
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/getExecutionList \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 1,
    "status": 1,
    "size": 10,
    "start": 0
  }'

# 获取任务执行记录详情
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/getExecutionDetail \
  -H "Content-Type: application/json" \
  -d '{"execution_id": 1}'

# 获取任务最新执行日志
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/logs/latest \
  -H "Content-Type: application/json" \
  -d '{"task_id": 1}'

# 获取任务执行统计
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/logs/stats \
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

# 获取任务执行历史列表（第1页）
response = requests.post(
    f"{base_url}/task/agentTasks/getExecutionList",
    json={
        "task_id": 1,
        "status": 1,
        "size": 10,
        "start": 0
    }
)
print(response.json())

# 获取任务执行历史列表（第2页）
response = requests.post(
    f"{base_url}/task/agentTasks/getExecutionList",
    json={
        "task_id": 1,
        "size": 10,
        "start": 10
    }
)
print(response.json())

# 获取任务执行记录详情
response = requests.post(
    f"{base_url}/task/agentTasks/getExecutionDetail",
    json={"execution_id": 1}
)
print(response.json())

# 获取任务最新执行日志
response = requests.post(
    f"{base_url}/task/agentTasks/logs/latest",
    json={"task_id": 1}
)
print(response.json())

# 获取任务执行统计
response = requests.post(
    f"{base_url}/task/agentTasks/logs/stats",
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
