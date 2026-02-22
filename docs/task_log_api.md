# 定时任务日志 API 文档

## 概述

定时任务日志系统用于追踪后台任务的执行情况，记录每次任务执行的详细信息，包括开始时间、结束时间、执行状态、结果摘要和错误信息等。

## 数据库表结构

### tbl_agent_task_log

| 字段名 | 类型 | 说明 |
|--------|------|------|
| log_id | INTEGER | 日志ID（主键，自增） |
| task_id | INTEGER | 任务ID（外键） |
| task_name | TEXT | 任务名称 |
| start_time | TEXT | 开始时间（格式：YYYY-MM-DD HH:MM:SS） |
| end_time | TEXT | 结束时间（格式：YYYY-MM-DD HH:MM:SS） |
| status | INTEGER | 执行状态（0:执行中 1:成功 2:失败） |
| result_summary | TEXT | 结果摘要 |
| error_message | TEXT | 错误信息 |
| execution_duration | INTEGER | 执行时长（秒） |

## API 接口

### 1. 查询任务执行日志

**接口地址**: `POST /mideasserver/task/agentTasks/logs`

**速率限制**: 60次/分钟

**请求参数**:

```json
{
  "task_id": 1,        // 可选，任务ID（不传则查询所有任务）
  "status": 1,         // 可选，执行状态（0:执行中 1:成功 2:失败）
  "limit": 100,        // 返回记录数量限制，默认100
  "offset": 0          // 偏移量，默认0
}
```

**响应示例**:

```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "log_id": 1,
        "task_id": 1,
        "task_name": "每日新闻摘要",
        "start_time": "2026-02-22 08:00:00",
        "end_time": "2026-02-22 08:05:30",
        "status": 1,
        "result_summary": "成功生成新闻摘要报告",
        "error_message": null,
        "execution_duration": 330
      }
    ],
    "total": 1,
    "limit": 100,
    "offset": 0
  },
  "message": "查询成功"
}
```

### 2. 获取任务最新执行日志

**接口地址**: `POST /mideasserver/task/agentTasks/logs/latest`

**速率限制**: 60次/分钟

**请求参数**:

```json
{
  "task_id": 1         // 必填，任务ID
}
```

**响应示例**:

```json
{
  "code": 0,
  "data": {
    "log_id": 5,
    "task_id": 1,
    "task_name": "每日新闻摘要",
    "start_time": "2026-02-22 08:00:00",
    "end_time": "2026-02-22 08:05:30",
    "status": 1,
    "result_summary": "成功生成新闻摘要报告",
    "error_message": null,
    "execution_duration": 330
  },
  "message": "查询成功"
}
```

### 3. 获取任务执行统计

**接口地址**: `POST /mideasserver/task/agentTasks/logs/stats`

**速率限制**: 60次/分钟

**请求参数**:

```json
{
  "task_id": 1         // 必填，任务ID
}
```

**响应示例**:

```json
{
  "code": 0,
  "data": {
    "total_executions": 10,      // 总执行次数
    "success_count": 8,           // 成功次数
    "failure_count": 2,           // 失败次数
    "running_count": 0,           // 执行中次数
    "avg_duration": 325.5,        // 平均执行时长（秒）
    "last_execution": {           // 最后一次执行
      "start_time": "2026-02-22 08:00:00",
      "status": 1,
      "duration": 330
    }
  },
  "message": "查询成功"
}
```

## 使用示例

### Python 示例

```python
import requests

BASE_URL = "http://localhost:18888/mideasserver/task"

# 1. 查询所有日志
response = requests.post(f"{BASE_URL}/agentTasks/logs", json={
    "limit": 50,
    "offset": 0
})
print(response.json())

# 2. 查询指定任务的成功日志
response = requests.post(f"{BASE_URL}/agentTasks/logs", json={
    "task_id": 1,
    "status": 1,
    "limit": 10
})
print(response.json())

# 3. 获取任务最新执行日志
response = requests.post(f"{BASE_URL}/agentTasks/logs/latest", json={
    "task_id": 1
})
print(response.json())

# 4. 获取任务执行统计
response = requests.post(f"{BASE_URL}/agentTasks/logs/stats", json={
    "task_id": 1
})
print(response.json())
```

### cURL 示例

```bash
# 查询所有日志
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/logs \
  -H "Content-Type: application/json" \
  -d '{"limit": 50, "offset": 0}'

# 查询指定任务的日志
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/logs \
  -H "Content-Type: application/json" \
  -d '{"task_id": 1, "status": 1}'

# 获取最新日志
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/logs/latest \
  -H "Content-Type: application/json" \
  -d '{"task_id": 1}'

# 获取统计信息
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/logs/stats \
  -H "Content-Type: application/json" \
  -d '{"task_id": 1}'
```

## 日志记录机制

### 自动记录

当定时任务调度器执行任务时，会自动记录日志：

1. **任务开始时**：插入日志记录，状态设为 0（执行中）
2. **任务成功时**：更新日志记录，状态设为 1（成功），记录结果摘要和执行时长
3. **任务失败时**：更新日志记录，状态设为 2（失败），记录错误信息和执行时长

### 日志字段说明

- **status**:
  - `0` - 执行中：任务正在运行
  - `1` - 成功：任务执行成功
  - `2` - 失败：任务执行失败

- **execution_duration**: 执行时长（秒），从任务开始到结束的总时间

- **result_summary**: 任务执行成功时的结果摘要

- **error_message**: 任务执行失败时的错误信息

## 性能优化

### 索引

系统已为以下字段创建索引以提高查询性能：

- `task_id` - 用于按任务ID查询
- `start_time DESC` - 用于按时间倒序查询

### 分页查询

建议使用 `limit` 和 `offset` 参数进行分页查询，避免一次性加载大量数据：

```json
{
  "task_id": 1,
  "limit": 50,    // 每页50条
  "offset": 0     // 第一页
}
```

## 注意事项

1. 所有接口统一使用 POST 方法
2. 日志会自动记录，无需手动调用
3. 建议定期清理历史日志，避免数据库过大
4. 执行时长单位为秒
5. 时间格式统一为 `YYYY-MM-DD HH:MM:SS`
