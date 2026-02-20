import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name: str = "mideasserver", log_dir: str = None) -> logging.Logger:
    """
    配置日志记录器

    Args:
        name: 日志记录器名称
        log_dir: 日志目录路径，如果为 None 则从配置读取

    Returns:
        配置好的日志记录器
    """
    # 延迟导入避免循环依赖
    if log_dir is None:
        from src.config import settings
        log_dir = settings.log_dir

    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 创建滚动文件处理器
    # maxBytes=10MB, backupCount=10
    log_file = log_path / "mideasserver.log"
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 设置日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# 创建全局日志记录器实例
logger = setup_logger()
