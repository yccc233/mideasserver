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

# 运行应用
python main.py
```

## 常用命令

```bash
# 启动开发服务器（默认端口 18889）
python main.py

# 查看数据库结构
python src/database/inspect_db.py
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

### API 路由结构

**重要规范**：所有接口统一使用 POST 方法，参数通过 request body 传递。

所有 API 路由前缀为 `/mideasserver`，后跟文件路径。

#### 智能体定时任务接口 (`/mideasserver/task`)
- `POST /agentTasks/list` - 获取所有定时任务（60次/分钟）
- `POST /agentTasks/get` - 获取单个定时任务（60次/分钟），body: `{task_id}`
- `POST /agentTasks/create` - 创建定时任务（20次/分钟），body: `{task_name, task_conf, ...}`
- `POST /agentTasks/update` - 更新定时任务（30次/分钟），body: `{task_id, ...}`
- `POST /agentTasks/delete` - 删除定时任务（20次/分钟），body: `{task_id}`

#### Agent 接口 (`/mideasserver/agent`)
- `POST /gptresearch` - GPT Research 接口（1次/分钟）

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

## 注意事项

- Windows 环境下使用 Git Bash，路径使用 Unix 风格（正斜杠）
- `.env` 文件使用 UTF-8 编码
- 数据库文件位于 `src/database/Mideas.db`
- 日志文件默认路径：`/work/logs/MIdeasServer`（需确保目录存在或修改配置）
- slowapi 已禁用自动读取 .env（避免 Windows 编码问题）
- 应用启动时会自动关闭数据库连接（lifespan 事件）
