"""
Agent 相关接口

包含：
- GPT Research 接口
"""
from fastapi import APIRouter
from src.logger import logger

router = APIRouter()


@router.get("/gptresearch")
async def gptresearch():
    """GPT Research 接口"""
    logger.info("调用 GPT Research 接口")
    return {"code": 0, "message": "GPT Research 接口"}
