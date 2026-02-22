"""
Agent 相关接口

包含：
- GPT Research 接口
"""
from fastapi import APIRouter, Request
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


@router.post("/gptresearch")
@limiter.limit("1/minute")
async def gptresearch(request: Request):
    """GPT Research 接口"""
    logger.info("调用 GPT Research 接口")
    return {"code": 0, "message": "GPT Research 接口"}
