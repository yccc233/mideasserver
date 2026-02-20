# Mideas Server

基于 FastAPI 的 Python Web 应用，提供任务管理和智能体定时任务调度功能。

## 功能特性

- 🚀 基于 FastAPI 的高性能异步 Web 框架
- 📦 动态路由加载系统，自动扫描并注册 API 端点
- 🗄️ SQLite3 数据库，支持 WAL 模式和连接复用
- ⏰ 智能体定时任务调度（类 cron 语法）
- 🛡️ 基于 IP 的速率限制（默认 100 次/分钟）
- 📝 完善的日志系统（文件轮转 + 控制台输出）
- 🔧 统一的错误处理和响应格式
- 🌐 CORS 跨域支持

## 快速开始

### 环境要求

- Python 3.8+
- Git Bash（Windows 环境推荐）

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd mideasserver

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/Scripts/activate  # Windows Git Bash
# 或
.venv\Scripts\activate  # Windows CMD

# 安装依赖
pip install -r requirements.txt
```

### 配置

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

主要配置项：
- `APP_NAME`: 应用名称
- `HOST`: 服务器地址（默认 0.0.0.0）
- `PORT`: 服务器端口（默认 18889）
- `DEBUG`: 调试模式
- `LOG_DIR`: 日志目录路径

### 运行

```bash
# 启动开发服务器
python main.py

# 服务将在 http://localhost:18889 启动
```

### 初始化数据库

```bash
# 初始化智能体定时任务表
python src/database/init_agent_schedule_task.py

# 查看数据库结构
python src/database/inspect_db.py
```

## 项目结构

```
mideasserver/
├── main.py                 # 应用入口
├── requirements.txt        # 依赖列表
├── .env                    # 环境配置（不提交到 Git）
├── .env.example            # 配置示例
├── CLAUDE.md               # 项目开发指南
└── src/
    ├── api/                # API 路由目录
    │   ├── task.py         # 任务管理接口
    │   └── agent/          # Agent 相关接口
    ├── database/           # 数据库模块
    │   ├── db.py           # 数据库抽象层
    │   ├── Mideas.db       # SQLite 数据库文件
    │   └── init_*.py       # 数据库初始化脚本
    ├── config.py           # 配置管理
    ├── logger.py           # 日志系统
    └── router_loader.py    # 动态路由加载器
```

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:18889/docs
- ReDoc: http://localhost:18889/redoc

### 主要端点

#### 健康检查
```
GET /health
```

#### 任务管理
```
GET  /mideasserver/task/*          # 查询任务
POST /mideasserver/task/*          # 创建任务
PUT  /mideasserver/task/*          # 更新任务
DELETE /mideasserver/task/*        # 删除任务
```

#### Agent 接口
```
POST /mideasserver/agent/*         # Agent 相关操作
```

### 响应格式

成功响应：
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
  "code": 400,
  "message": "错误描述",
  "detail": "详细信息"
}
```

## 开发指南

### 添加新的 API 端点

1. 在 `src/api/` 下创建 Python 文件
2. 创建 `APIRouter` 实例并命名为 `router`
3. 定义端点函数（第一个参数必须是 `request: Request`）
4. 添加速率限制装饰器

示例：

```python
from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.get("/example")
@limiter.limit("10/minute")
async def example_endpoint(request: Request):
    return {"code": 0, "message": "示例端点"}
```

路由会自动加载，前缀为 `/mideasserver` + 文件路径。

### 数据库操作

```python
from src.database import db

# 插入数据
task_id = db.insert("table_name", {"field": "value"})

# 查询数据
task = db.get_by_id("table_name", "id_column", id_value)
tasks = db.get_all("table_name", order_by="id DESC")

# 更新数据
rows = db.update("table_name", {"field": "new_value"}, "id = ?", (id,))

# 删除数据
rows = db.delete("table_name", "id = ?", (id,))
```

### 定时任务配置

智能体定时任务使用简化的 cron 语法（4 个字段）：

```
时 日 月 周
```

示例：
- `"6,8 * * *"` - 每天 6 点和 8 点执行
- `"20 * * 0"` - 每周日晚 8 点执行
- `"0 1 * *"` - 每月 1 号零点执行

## 技术栈

- **Web 框架**: FastAPI 0.104.1
- **ASGI 服务器**: Uvicorn 0.24.0
- **数据验证**: Pydantic 2.9.0+
- **配置管理**: Pydantic Settings 2.1.0
- **速率限制**: SlowAPI 0.1.9
- **数据库**: SQLite3
- **AI 研究**: GPT Researcher

## 注意事项

- Windows 环境下使用 Git Bash，路径使用 Unix 风格（正斜杠）
- `.env` 文件必须使用 UTF-8 编码
- 数据库文件位于 `src/database/Mideas.db`
- 日志文件默认路径：`/work/logs/MIdeasServer`（需确保目录存在或修改配置）
- slowapi 已禁用自动读取 .env（避免 Windows 编码问题）

## 许可证

MIT License
