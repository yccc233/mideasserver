import sys
import os
import importlib.util
from pathlib import Path
from fastapi import APIRouter
from src.logger import logger


def load_routers(base_path: str, prefix: str = "") -> list[APIRouter]:
    """
    动态加载所有路由模块

    Args:
        base_path: 路由模块所在的基础目录
        prefix: 路由前缀

    Returns:
        APIRouter 列表
    """
    routers = []
    base_dir = Path(base_path)

    if not base_dir.exists():
        logger.error(f"路由目录不存在: {base_path}")
        return routers

    # 确保项目根目录在 sys.path 中
    project_root = base_dir.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # 遍历目录中的所有 Python 文件和子目录
    for item in base_dir.rglob("*.py"):
        # 跳过 __init__.py、__pycache__ 和 router_loader.py
        if (item.name == "__init__.py" or
            "__pycache__" in item.parts or
            item.name == "router_loader.py"):
            continue

        # 计算相对路径和路由前缀
        relative_path = item.relative_to(base_dir)
        route_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        route_prefix = "/" + "/".join(route_parts)

        try:
            # 动态导入模块
            spec = importlib.util.spec_from_file_location(
                f"routes.{'.'.join(route_parts)}",
                item
            )
            if spec is None or spec.loader is None:
                logger.warning(f"无法加载模块 {item}")
                continue

            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            # 查找 router 对象
            if hasattr(module, "router") and isinstance(module.router, APIRouter):
                routers.append((prefix + route_prefix, module.router))
                logger.info(f"加载路由: {prefix + route_prefix}")
            else:
                logger.warning(f"模块 {item} 中未找到 router 对象")
        except Exception as e:
            logger.error(f"加载路由失败 {item}: {e}")
            import traceback
            traceback.print_exc()

    return routers
