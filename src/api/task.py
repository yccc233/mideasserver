"""
智能体定时任务管理接口
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.database import db
from src.logger import logger

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


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
