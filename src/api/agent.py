"""
Agent 相关接口

包含：
- GPT Research 接口
"""
from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.logger import logger

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/gptresearch")
@limiter.limit("1/minute")
async def gptresearch(request: Request):
    """GPT Research 接口"""
    logger.info("调用 GPT Research 接口")
    return {"code": 0, "message": "GPT Research 接口"}
