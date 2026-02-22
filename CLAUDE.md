# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Mideas Server 是一个基于 FastAPI 的 Python Web 应用，提供任务管理和智能体定时任务调度功能。使用 SQLite3 作为数据库，支持动态路由加载和速率限制。

## 开发环境设置

```bash
# 激活虚拟环境
source .venv/Scripts/activate  # Windows Git Bash
# 或
.venv\Scripts\activate  # Windows CMD

# 安装依赖
pip install -r requirements.txt

# 配置 GPT Researcher（必需）
# 1. 复制环境变量模板
cp .env.example .env

# 2. 编辑 .env 文件，配置以下必需项：
#    - OPENAI_API_KEY: OpenAI API 密钥
#    - RETRIEVER: 搜索引擎类型（tavily/google/bing/serper/duckduckgo）
#    - 对应搜索引擎的 API Key（如 TAVILY_API_KEY）

# 3. 验证配置
python test_gptr_config.py

# 运行应用
python main.py
```

详细配置说明请参考：[GPT Researcher 配置指南](docs/gpt_researcher_setup.md)

## 常用命令

```bash
# 启动开发服务器（默认端口 18888）
python main.py

# 初始化数据库表
python src/database/init_agent_schedule_task.py  # 初始化定时任务表
python src/database/init_task_execution.py       # 初始化任务执行记录表

# 查看数据库结构
python src/database/inspect_db.py

# 手动执行研究任务（交互式工具）
python run_task.py
```

## 架构设计

### 核心组件

1. **动态路由加载系统** (`src/router_loader.py`)
   - 自动扫描 `src/api/` 目录下的所有 Python 文件
   - 每个文件必须导出名为 `router` 的 `APIRouter` 对象
   - 路由前缀根据文件路径自动生成（如 `src/api/task.py` → `/mideasserver/task`）
   - 支持嵌套目录结构

2. **数据库抽象层** (`src/database/db.py`)
   - 使用线程本地存储管理 SQLite 连接，支持连接复用
   - 启用 WAL 模式提高并发性能
   - 提供通用 CRUD 方法：`insert()`, `update()`, `delete()`, `get_by_id()`, `get_all()`, `count()`
   - 全局单例 `db` 对象可直接导入使用

3. **配置管理** (`src/config.py`)
   - 使用 Pydantic Settings 从 `.env` 文件加载配置
   - 全局单例 `settings` 对象
   - 主要配置项：`app_name`, `host`, `port`, `debug`, `log_dir`

4. **日志系统** (`src/logger.py`)
   - 使用 RotatingFileHandler，单文件最大 10MB，保留 10 个备份
   - 同时输出到文件和控制台
   - 全局单例 `logger` 对象

5. **速率限制**
   - 使用 slowapi 实现基于 IP 的速率限制
   - 默认限制：100 次/分钟
   - 各端点可自定义限制（使用 `@limiter.limit()` 装饰器）

6. **智能体定时任务调度器** (`src/process/agent.py`)
   - 启动后10秒首次执行，之后每分钟检查一次所有启用的定时任务
   - 支持类 cron 语法（4 字段格式：时 日 月 周）
   - 自动执行 GPT Researcher 研究任务，输出中文报告
   - **防重复执行**：**防重复执行**：
     - 如果任务正在执行中，跳过不重复执行
     - 如果任务在同一小时内已执行过，跳过（避免每分钟重复触发）
   - 任务异步执行，不阻塞其他任务的检查和启动
   - 记录任务执行日志到数据库（开始时间、结束时间、状态、结果摘要���
   - 应用启动时自动启动，关闭时自动停止
   - 全局单例 `scheduler` 对象

### API 路由结构

**重要规范**：所有接口统一使用 POST 方法，参数通过 request body 传递。

所有 API 路由前缀为 `/mideasserver`，后跟文件路径。

#### 智能体定时任务接口 (`/mideasserver/task`)
- `POST /agentTasks/list` - 获取所有定时任务（60次/分钟）
- `POST /agentTasks/get` - 获取单个定时任务（60次/分钟），body: `{task_id}`
- `POST /agentTasks/create` - 创建定时任务（20次/分钟），body: `{task_name, task_conf, ...}`
- `POST /agentTasks/update` - 更新定时任务（30次/分钟），body: `{task_id, ...}`
- `POST /agentTasks/delete` - 删除定时任务（20次/分钟），body: `{task_id}`
- `POST /agentTasks/getExecutionList` - 获取任务执行历史列表（60次/分钟），body: `{task_id?, status?, size, start}`
- `POST /agentTasks/getExecutionDetail` - 根据执行ID获取详细信息（60次/分钟），body: `{execution_id}`
- `POST /agentTasks/logs/latest` - 获取任务最新执行日志（60次/分钟），body: `{task_id}`
- `POST /agentTasks/logs/stats` - 获取任务执行统计（60次/分钟），body: `{task_id}`

#### Agent 接口 (`/mideasserver/agent`)
- `POST /gptresearch` - GPT Research 接口（1次/分钟）

#### Embedding 接口 (`/mideasserver/embedding`)
- `POST /embeddings` - 创建文本 embeddings（无限制），body: `{input, model}`
- `GET /models` - 列出可用的 embedding 模型（无限制）
- `GET /health` - 健康检查（无限制）

详细说明：[Embedding API 文档](docs/embedding_api.md)

### 定时任务配置语法

智能体定时任务使用简化的 cron 语法（4 个字段）：

```
时 日 月 周
```

字段说明：
- **时**：0-23（小时）
- **日**：1-31（日期）
- **月**：1-12（月份）
- **周**：0-6（星期，0=周日，1=周一，...，6=周六）

支持的语法：
- `*` - 任意值
- `6,8,10` - 多个值（逗号分隔）
- `1-5` - 范围值

示例：
- `"6,8 * * *"` - 每天 6 点和 8 点执行
- `"20 * * 0"` - 每周日晚 8 点执行
- `"9 1 * *"` - 每月 1 号早 9 点执行
- `"14 * * 1-5"` - 每周一到周五下午 2 点执行

## 开发规范

### 添加新的 API 端点

**重要规范**：所有接口必须使用 POST 方法，参数通过 request body 传递。

1. 在 `src/api/` 下创建新的 Python 文件（或在现有文件中添加）
2. 创建 `APIRouter` 实例并命名为 `router`
3. 导入必要的依赖：
   ```python
   from fastapi import APIRouter, Request
   from slowapi import Limiter
   from slowapi.util import get_remote_address

   router = APIRouter()
   limiter = Limiter(key_func=get_remote_address)
   ```
4. 使用 `@router.post()` 装饰器定义端点（统一使用 POST 方法）
5. 添加 `@limiter.limit()` 装饰器设置速率限制
6. 端点函数第一个参数必须是 `request: Request`（slowapi 要求）
7. 使用 Pydantic BaseModel 定义请求模型，所有参数通过 body 传递
8. 路由会自动加载，无需手动注册

**示例**：
```python
from pydantic import BaseModel

class TaskQuery(BaseModel):
    task_id: int

@router.post("/tasks/get")
@limiter.limit("60/minute")
async def get_task(request: Request, query: TaskQuery):
    """获取单个任务"""
    task = db.get_by_id("table_name", "task_id", query.task_id)
    return {"code": 0, "data": task, "message": "查询成功"}
```

### 数据库操作

```python
from src.database import db

# 插入
task_id = db.insert("table_name", {"field": "value"})

# 查询
task = db.get_by_id("table_name", "id_column", id_value)
tasks = db.get_all("table_name", order_by="id DESC")

# 更新
rows = db.update("table_name", {"field": "new_value"}, "id = ?", (id,))

# 删除
rows = db.delete("table_name", "id = ?", (id,))
```

### 日志记录

```python
from src.logger import logger

logger.info("信息日志")
logger.warning("警告日志")
logger.error("错误日志")
```

### 响应格式

统一使用以下 JSON 格式：
```json
{
  "code": 0,
  "data": {},
  "message": "操作成功"
}
```

错误响应：
```json
{
  "code": 400/404/500,
  "message": "错误描述",
  "detail": "详细信息"
}
```

### 手动执行研究任务

使用 `run_task.py` 工具可以手动执行研究任务，无需等待定时调度：

```bash
python run_task.py
```

功能：
1. 执行已有任务 - 从数据库选择任务执行
2. 自定义研究 - 输入研究主题，创建临时任务并执行
3. 查看任务列表 - 列出所有定时任务

执行结果会自动记录到 `tbl_task_execution` 表中。

## 数据库表结构

### tbl_agent_schedule_task（智能体定时任务表）
- `task_id` - 任务 ID（主键，自增）
- `task_name` - 任务名称
- `task_info` - 任务描述
- `task_conf` - 时间配置（格式：时 日 月 周）
- `task_prompt` - 研究提示词
- `task_status` - 任务状态（0=禁用，1=启用）
- `insert_time` - 创建时间
- `update_time` - 更新时间

### tbl_task_execution（任务执行记录表）
- `execution_id` - 执行记录 ID（主键，自增）
- `task_id` - 关联的任务 ID（外键）
- `task_name` - 任务名称（冗余字段，方便查询）
- `task_prompt` - 任务提示词（冗余字段）
- `status` - 执行状态（0=运行中，1=成功，2=失败）
- `start_time` - 开始时间
- `end_time` - 结束时间
- `execution_duration` - 执行时长（秒）
- `result_summary` - 结果摘要（成功时，前500字符）
- `result_detail` - 完整结果（可选，存储完整报告）
- `error_message` - 错误信息（失败时）
- `error_detail` - 错误详情（失败时，堆栈信息等）
- `created_at` - 创建时间
- `updated_at` - 更新时间

**注意**：已弃用 `tbl_agent_task_log` 表，请使用新的 `tbl_task_execution` 表。

## 注意事项

- Windows 环境下使用 Git Bash，路径使用 Unix 风格（正斜杠）
- `.env` 文件使用 UTF-8 编码
- **slowapi 编码问题**：为避免 Windows 下 slowapi 读取 `.env` 文件时的编码错误，在 `main.py` 中临时重命名 `.env` 文件，初始化 limiter 后恢复。API 路由文件中的 limiter 从 `main.py` 延迟导入。
- 数据库文件位于 `src/database/Mideas.db`
- 日志文件默认路径：`/work/logs/MIdeasServer`（需确保目录存在或修改配置）
- slowapi 已禁用自动读取 .env（避免 Windows 编码问题）
- 应用启动时会自动启动智能体调度器，关闭时自动停止并关闭数据库连接（lifespan 事件）
- 定时任务启动后10秒首次执行，之后每分钟检查一次。如果任务正在执行中，会跳过不重复执行
- GPT Researcher 配置通过环境变量传递，详见 `src/config.py`
