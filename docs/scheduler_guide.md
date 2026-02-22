# 智能体定时任务调度器使用说明

## 功能概述

智能体定时任务调度器是一个后台服务，用于定期执行 GPT Research 任务。调度器每分钟检查一次数据库中的任务配置，根据时间规则自动执行符合条件的任务。

## 目录结构

```
src/process/
├── __init__.py          # 模块初始化文件
└── agent.py             # 定时任务调度器实现
```

## 核心组件

### AgentScheduler 类

定时任务调度器的核心类，提供以下功能：

1. **时间配置解析** - 解析类 cron 格式的时间配置
2. **时间匹配判断** - 判断当前时间是否符合任务执行条件
3. **任务调度执行** - 每分钟检查并执行符合条件的任务

### 时间配置格式

使用简化的 cron 语法（4 个字段）：

```
时 日 月 周
```

#### 字段说明

- **时**：0-23（小时）
- **日**：1-31（日期）
- **月**：1-12（月份）
- **周**：0-6（星期，0=周日，1=周一，...，6=周六）

#### 特殊符号

- `*` - 任意值
- `,` - 多个值（如：6,8,10）
- `-` - 范围值（如：1-5）

#### 配置示例

| 配置 | 说明 |
|------|------|
| `* * * *` | 每分钟执行 |
| `6 * * *` | 每天早上 6 点执行 |
| `6,8,10 * * *` | 每天 6 点、8 点、10 点执行 |
| `20 * * 0` | 每周日晚上 8 点执行 |
| `9 1 * *` | 每月 1 号早上 9 点执行 |
| `14 * * 1-5` | 每周一到周五下午 2 点执行 |
| `0 * 1 *` | 每年 1 月每天零点执行 |

## 使用方法

### 1. 启动调度器

调度器会在应用启动时自动启动（在 `main.py` 的 `lifespan` 事件中）：

```python
# main.py 中已集成
from src.process.agent import scheduler
import asyncio

scheduler_task = asyncio.create_task(scheduler.run())
```

### 2. 创建定时任务

通过 API 接口创建定时任务：

```bash
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "每日研究报告",
    "task_info": "生成每日 AI 技术研究报告",
    "task_conf": "6 * * *",
    "task_prompt": "研究最新的 AI 技术发展趋势",
    "task_status": 1
  }'
```

### 3. 管理任务

- **查看所有任务**：`POST /mideasserver/task/agentTasks/list`
- **查看单个任务**：`POST /mideasserver/task/agentTasks/get`
- **更新任务**：`POST /mideasserver/task/agentTasks/update`
- **删除任务**：`POST /mideasserver/task/agentTasks/delete`

### 4. 启用/禁用任务

通过更新 `task_status` 字段控制任务是否执行：

```bash
# 禁用任务
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/update \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 1,
    "task_status": 0
  }'

# 启用任务
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/update \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 1,
    "task_status": 1
  }'
```

## 工作原理

### 调度流程

```
启动应用
    ↓
启动调度器（每分钟执行一次）
    ↓
从数据库获取所有启用的任务（task_status = 1）
    ↓
遍历每个任务
    ↓
解析任务的时间配置（task_conf）
    ↓
判断当前时间是否匹配配置
    ↓
如果匹配，执行 GPT Research 任务
    ↓
等待到下一分钟
    ↓
重复检查
```

### 时间匹配逻辑

1. 解析时间配置字符串为 4 个字段
2. 获取当前时间的小时、日期、月份、星期
3. 逐个字段匹配：
   - `*` 直接匹配
   - 逗号分隔的值：检查当前值是否在列表中
   - 范围值：检查当前值是否在范围内
   - 单个值：检查是否相等
4. 所有字段都匹配才执行任务

## 测试

运行测试脚本验证时间匹配逻辑：

```bash
python test_scheduler.py
```

测试覆盖以下场景：
- 任意时间匹配
- 单个小时匹配
- 多个小时匹配（逗号分隔）
- 特定星期匹配
- 特定日期匹配
- 星期范围匹配
- 月份匹配

## 日志

调度器会记录以下日志：

- 启动/停止信息
- 每次检查的时间
- 任务执行信息
- 错误信息

日志位置：配置文件中的 `LOG_DIR` 目录

## 注意事项

1. **时间精度**：调度器每分钟执行一次，不支持秒级精度
2. **任务状态**：只有 `task_status = 1` 的任务才会被执行
3. **时间配置**：配置格式必须正确（4 个字段，空格分隔）
4. **并发执行**：如果多个任务在同一分钟执行，会按顺序依次执行
5. **GPT Research**：当前版本中 GPT Research 的实际调用需要根据库的使用方式进行实现

## 扩展开发

### 实现 GPT Research 调用

在 `agent.py` 的 `execute_gpt_research` 方法中添加实际的 GPT Researcher 调用：

```python
async def execute_gpt_research(self, task: Dict[str, Any]):
    """执行 GPT Research 任务"""
    try:
        task_prompt = task.get("task_prompt", "")

        # 实际调用 GPT Researcher
        from gpt_researcher import GPTResearcher

        researcher = GPTResearcher(query=task_prompt)
        result = await researcher.conduct_research()
        report = await researcher.write_report()

        # 保存结果到数据库或文件
        logger.info(f"研究报告生成完成: {task.get('task_name')}")

    except Exception as e:
        logger.error(f"执行 GPT Research 任务失败: {e}")
```

### 添加任务执行历史

可以创建新表记录任务执行历史：

```sql
CREATE TABLE tbl_agent_task_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    execute_time TEXT NOT NULL,
    status TEXT NOT NULL,
    result TEXT,
    error_message TEXT
);
```

## 故障排查

### 任务没有执行

1. 检查任务状态是否为启用（`task_status = 1`）
2. 检查时间配置是否正确
3. 查看日志文件确认调度器是否正常运行
4. 使用测试脚本验证时间匹配逻辑

### 调度器未启动

1. 检查应用启动日志
2. 确认 `main.py` 中的 `lifespan` 事件正确配置
3. 检查是否有异常导致调度器停止

### 时间配置错误

使用测试脚本验证配置：

```python
from src.process.agent import AgentScheduler
from datetime import datetime

scheduler = AgentScheduler()
result = scheduler.should_execute("6,8 * * *", datetime(2026, 2, 22, 8, 0))
print(f"是否匹配: {result}")
```
