"""
智能体定时任务管理接口
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.database import db
from src.logger import logger

router = APIRouter()

# 延迟导入 limiter（避免重复创建导致编码问题）
limiter = None

def _get_limiter():
    global limiter
    if limiter is None:
        from main import limiter as main_limiter
        limiter = main_limiter
    return limiter

# 确保 limiter 在模块加载时可用
limiter = _get_limiter()


# ==================== 数据模型 ====================

class AgentScheduleTaskCreate(BaseModel):
    """创建智能体定时任务请求"""
    task_name: str = Field(..., description="任务名称")
    task_info: Optional[str] = Field(None, description="任务信息")
    task_conf: str = Field(..., description="任务执行时间配置（格式：时 日 月 周，如：'6,8 * * *' 表示每天6点和8点，'20 * * 0' 表示每周日晚8点）")
    task_prompt: Optional[str] = Field(None, description="任务提示词")
    task_status: int = Field(1, description="任务状态（0:关闭 1:开启）")


class AgentScheduleTaskUpdate(BaseModel):
    """更新智能体定时任务请求"""
    task_id: int = Field(..., description="任务ID")
    task_name: Optional[str] = Field(None, description="任务名称")
    task_info: Optional[str] = Field(None, description="任务信息")
    task_conf: Optional[str] = Field(None, description="任务执行时间配置")
    task_prompt: Optional[str] = Field(None, description="任务提示词")
    task_status: Optional[int] = Field(None, description="任务状态（0:关闭 1:开启）")


class AgentScheduleTaskQuery(BaseModel):
    """查询智能体定时任务请求"""
    task_id: int = Field(..., description="任务ID")


class AgentScheduleTaskDelete(BaseModel):
    """删除智能体定时任务请求"""
    task_id: int = Field(..., description="任务ID")


class AgentTaskLogQuery(BaseModel):
    """查询任务执行日志请求"""
    task_id: Optional[int] = Field(None, description="任务ID（可选，不传则查询所有）")
    status: Optional[int] = Field(None, description="执行状态（0:执行中 1:成功 2:失败）")
    size: int = Field(100, description="每页数量")
    start: int = Field(0, description="起始位置（从0开始）")


class TaskExecutionQuery(BaseModel):
    """查询任务执行记录详情请求"""
    execution_id: int = Field(..., description="执行记录ID")


# ==================== 智能体定时任务接口 ====================

@router.post("/agentTasks/create")
@limiter.limit("20/minute")
async def create_agent_task(request: Request, task: AgentScheduleTaskCreate):
    """
    添加智能体定时任务

    task_conf 格式说明（类似 cron，但简化为4个字段）：
    - 格式：时 日 月 周（用空格分隔）
    - 示例：
      - "6,8 * * *" - 每天6点和8点执行
      - "20 * * 0" - 每周日晚8点执行
      - "9 1 * *" - 每月1号早9点执行
      - "14 * * 1-5" - 每周一到周五下午2点执行
    - 字段说明：
      - 时：0-23
      - 日：1-31
      - 月：1-12
      - 周：0-6（0表示周日）
      - * 表示任意值
      - , 表示多个值（如：6,8,10）
      - - 表示范围（如：1-5）
    """
    logger.info(f"创建智能体定时任务: {task.task_name}")

    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 准备插入数据
    task_data = {
        "task_name": task.task_name,
        "task_info": task.task_info,
        "task_conf": task.task_conf,
        "task_prompt": task.task_prompt,
        "task_status": task.task_status,
        "insert_time": current_time,
        "update_time": current_time
    }

    # 插入数据库
    task_id = db.insert("tbl_agent_schedule_task", task_data)

    logger.info(f"智能体定时任务创建成功，任务ID: {task_id}")

    return {
        "code": 0,
        "data": {
            "task_id": task_id,
            **task_data
        },
        "message": "定时任务创建成功"
    }


@router.post("/agentTasks/list")
@limiter.limit("60/minute")
async def get_agent_tasks(request: Request):
    """获取所有智能体定时任务"""
    logger.info("查询所有智能体定时任务")
    tasks = db.get_all("tbl_agent_schedule_task", order_by="task_id DESC")
    total = db.count("tbl_agent_schedule_task")
    return {
        "code": 0,
        "data": {
            "list": tasks,
            "total": total
        },
        "message": "查询成功"
    }


@router.post("/agentTasks/get")
@limiter.limit("60/minute")
async def get_agent_task(request: Request, query: AgentScheduleTaskQuery):
    """获取单个智能体定时任务"""
    logger.info(f"查询智能体定时任务 ID: {query.task_id}")
    task = db.get_by_id("tbl_agent_schedule_task", "task_id", query.task_id)
    if not task:
        return {"code": 404, "message": "任务不存在"}
    return {"code": 0, "data": task, "message": "查询成功"}


@router.post("/agentTasks/update")
@limiter.limit("30/minute")
async def update_agent_task(request: Request, task: AgentScheduleTaskUpdate):
    """更新智能体定时任务"""
    logger.info(f"更新智能体定时任务 ID: {task.task_id}")

    # 只更新提供的字段（排除 task_id）
    update_data = {k: v for k, v in task.model_dump(exclude_unset=True).items() if k != "task_id"}
    if not update_data:
        return {"code": 400, "message": "没有提供更新字段"}

    # 添加更新时间
    update_data["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    rows = db.update(
        "tbl_agent_schedule_task",
        update_data,
        "task_id = ?",
        (task.task_id,)
    )

    if rows == 0:
        return {"code": 404, "message": "任务不存在"}
    return {"code": 0, "message": "更新成功"}


@router.post("/agentTasks/delete")
@limiter.limit("20/minute")
async def delete_agent_task(request: Request, task: AgentScheduleTaskDelete):
    """删除智能体定时任务"""
    logger.info(f"删除智能体定时任务 ID: {task.task_id}")
    rows = db.delete("tbl_agent_schedule_task", "task_id = ?", (task.task_id,))
    if rows == 0:
        return {"code": 404, "message": "任务不存在"}
    return {"code": 0, "message": "删除成功"}


# ==================== 任务执行日志接口 ====================

@router.post("/agentTasks/getExecutionList")
@limiter.limit("60/minute")
async def get_agent_task_logs(request: Request, query: AgentTaskLogQuery):
    """
    获取任务执行历史列表

    支持按任务ID和执行状态筛选，支持分页
    """
    logger.info(f"查询任务执行日志: task_id={query.task_id}, status={query.status}")

    # 构建查询条件
    where_clauses = []
    params = []

    if query.task_id is not None:
        where_clauses.append("task_id = ?")
        params.append(query.task_id)

    if query.status is not None:
        where_clauses.append("status = ?")
        params.append(query.status)

    where = " AND ".join(where_clauses) if where_clauses else None

    # 查询日志（使用新表 tbl_task_execution）
    logs = db.get_all(
        "tbl_task_execution",
        where=where,
        params=tuple(params) if params else None,
        order_by="start_time DESC",
        limit=query.size,
        offset=query.start
    )

    # 统计总数
    total = db.count("tbl_task_execution", where=where, params=tuple(params) if params else None)

    return {
        "code": 0,
        "data": {
            "list": logs,
            "total": total,
            "size": query.size,
            "start": query.start
        },
        "message": "查询成功"
    }


@router.post("/agentTasks/logs/latest")
@limiter.limit("60/minute")
async def get_latest_task_log(request: Request, query: AgentScheduleTaskQuery):
    """获取指定任务的最新执行日志"""
    logger.info(f"查询任务最新执行日志 ID: {query.task_id}")

    logs = db.get_all(
        "tbl_task_execution",
        where="task_id = ?",
        params=(query.task_id,),
        order_by="start_time DESC",
        limit=1
    )

    if not logs:
        return {"code": 404, "message": "未找到执行日志"}

    return {"code": 0, "data": logs[0], "message": "查询成功"}


@router.post("/agentTasks/getExecutionDetail")
@limiter.limit("60/minute")
async def get_task_execution_detail(request: Request, query: TaskExecutionQuery):
    """
    根据执行ID获取任务执行记录详情

    返回完整的执行记录信息，包括完整报告内容（result_detail）
    """
    logger.info(f"查询任务执行记录详情 execution_id: {query.execution_id}")

    execution = db.get_by_id("tbl_task_execution", "execution_id", query.execution_id)

    if not execution:
        return {"code": 404, "message": "执行记录不存在"}

    return {"code": 0, "data": execution, "message": "查询成功"}


@router.post("/agentTasks/logs/stats")
@limiter.limit("60/minute")
async def get_task_log_stats(request: Request, query: AgentScheduleTaskQuery):
    """获取指定任务的执行统计信息"""
    logger.info(f"查询任务执行统计 ID: {query.task_id}")

    # 查询所有日志（使用新表 tbl_task_execution）
    logs = db.get_all(
        "tbl_task_execution",
        where="task_id = ?",
        params=(query.task_id,)
    )

    if not logs:
        return {
            "code": 0,
            "data": {
                "total_executions": 0,
                "success_count": 0,
                "failure_count": 0,
                "running_count": 0,
                "avg_duration": 0,
                "last_execution": None
            },
            "message": "暂无执行记录"
        }

    # 统计数据
    total = len(logs)
    success = sum(1 for log in logs if log.get("status") == 1)
    failure = sum(1 for log in logs if log.get("status") == 2)
    running = sum(1 for log in logs if log.get("status") == 0)

    # 计算平均执行时长（仅统计已完成的任务）
    completed_logs = [log for log in logs if log.get("execution_duration") is not None]
    avg_duration = sum(log.get("execution_duration", 0) for log in completed_logs) / len(completed_logs) if completed_logs else 0

    # 最后一次执行
    last_log = logs[0] if logs else None

    return {
        "code": 0,
        "data": {
            "total_executions": total,
            "success_count": success,
            "failure_count": failure,
            "running_count": running,
            "avg_duration": round(avg_duration, 2),
            "last_execution": {
                "execution_id": last_log.get("execution_id"),
                "start_time": last_log.get("start_time"),
                "status": last_log.get("status"),
                "duration": last_log.get("execution_duration")
            } if last_log else None
        },
        "message": "查询成功"
    }
