import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import traceback

from src.config import settings
from src.logger import logger
from src.router_loader import load_routers


# 初始化速率限制器（延迟导入，避免读取 .env 文件时的编码问题）
# 临时重命名 .env 文件
env_file = Path(__file__).parent / ".env"
env_backup = Path(__file__).parent / ".env.backup"
env_exists = env_file.exists()

if env_exists:
    env_file.rename(env_backup)

try:
    from slowapi import Limiter

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["100/minute"],
        storage_uri="memory://"
    )
finally:
    # 恢复 .env 文件
    if env_exists:
        env_backup.rename(env_file)


# 应用启动和关闭事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    logger.info(f"{settings.app_name} 启动")
    logger.info(f"服务器地址: {settings.host}:{settings.port}")

    # 启动智能体定时任务调度器
    from src.process.agent import scheduler
    import asyncio
    scheduler_task = asyncio.create_task(scheduler.run())
    logger.info("智能体定时任务调度器已启动")

    yield

    # 关闭事件
    # 停止调度器
    scheduler.stop()
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass
    logger.info("智能体定时任务调度器已停止")

    # 关闭数据库连接
    from src.database import db
    db.close_connection()
    logger.info(f"{settings.app_name} 关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    description="FastAPI 接口级应用",
    version=settings.app_version,
    lifespan=lifespan
)

# 将速率限制器绑定到应用
app.state.limiter = limiter


# 自定义速率限制异常处理器
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """处理速率限制超出异常"""
    logger.warning(f"速率限制触发: {request.client.host} - {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "code": 429,
            "message": "请求过于频繁，请稍后再试",
            "detail": "已超出速率限制"
        }
    )


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """捕获所有未处理的异常"""
    error_detail = str(exc)
    error_type = type(exc).__name__

    # 记录详细错误信息
    logger.error(
        f"全局异常捕获: {error_type} - {error_detail}\n"
        f"请求路径: {request.method} {request.url.path}\n"
        f"堆栈跟踪:\n{traceback.format_exc()}"
    )

    # 返回统一的错误响应
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "detail": error_detail if settings.debug else "请联系管理员"
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """处理值错误（通常是参数验证错误）"""
    logger.warning(f"参数验证错误: {str(exc)} - 路径: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": 400,
            "message": "请求参数错误",
            "detail": str(exc)
        }
    )

# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # 处理请求
    response = await call_next(request)

    # 计算处理时间
    process_time = time.time() - start_time

    # 只记录非健康检查的请求
    if request.url.path not in ["/health", "/"]:
        logger.info(
            f"{request.method} {request.url.path} - "
            f"状态: {response.status_code} - 耗时: {process_time:.3f}s"
        )

    return response


# 健康检查端点
@app.get("/health")
@limiter.limit("30/minute")
async def health_check(request: Request):
    return {"code": 0, "status": "ok"}


# 根端点
@app.get("/")
@limiter.limit("30/minute")
async def root(request: Request):
    return {"code": 0, "message": "欢迎使用 Mideas 应用"}


# 动态加载路由
src_path = Path(__file__).parent / "src"
routers = load_routers(str(src_path / "api"))

for route_prefix, router in routers:
    app.include_router(router, prefix="/mideasserver" + route_prefix)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
