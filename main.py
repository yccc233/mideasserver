import os
from contextlib import asynccontextmanager
from pathlib import Path

# 设置环境变量禁用 slowapi 自动读取 .env（避免 Windows 编码问题）
os.environ.setdefault("SLOWAPI_DISABLE_DOTENV", "1")

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import traceback

from src.config import settings
from src.logger import logger
from src.router_loader import load_routers


# 应用启动和关闭事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    logger.info(f"{settings.app_name} 启动")
    logger.info(f"服务器地址: {settings.host}:{settings.port}")
    yield
    # 关闭事件
    from src.database import db
    db.close_connection()
    logger.info(f"{settings.app_name} 关闭")


# 初始化速率限制器
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri="memory://"
)


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

    # 记录请求信息
    logger.info(f"请求开始: {request.method} {request.url.path}")

    # 处理请求
    response = await call_next(request)

    # 计算处理时间
    process_time = time.time() - start_time
    logger.info(
        f"请求完成: {request.method} {request.url.path} - "
        f"状态码: {response.status_code} - 耗时: {process_time:.3f}s"
    )

    return response


# 健康检查端点
@app.get("/health")
@limiter.limit("30/minute")
async def health_check(request: Request):
    logger.info("健康检查")
    return {"code": 0, "status": "ok"}


# 根端点
@app.get("/")
@limiter.limit("30/minute")
async def root(request: Request):
    logger.info("访问根端点")
    return {"code": 0, "message": "欢迎使用 Mideas 应用"}


# 动态加载路由
src_path = Path(__file__).parent / "src"
routers = load_routers(str(src_path / "api"))

for route_prefix, router in routers:
    app.include_router(router, prefix="/mideasserver" + route_prefix)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
