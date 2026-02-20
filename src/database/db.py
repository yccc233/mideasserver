"""
SQLite 数据库工具类

提供通用的数据库操作方法，无需为每个表单独编写代码
使用线程本地存储优化连接管理
"""
import sqlite3
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

from src.logger import logger


class Database:
    """SQLite 数据库操作类（支持连接复用）"""

    def __init__(self, db_path: str = None):
        """
        初始化数据库

        Args:
            db_path: 数据库文件路径，默认使用 Mideas.db
        """
        if db_path is None:
            db_path = Path(__file__).parent / "Mideas.db"
        self.db_path = str(db_path)
        self._local = threading.local()
        logger.info(f"数据库初始化: {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """获取线程本地连接（复用连接）"""
        if not hasattr(self._local, "connection") or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=10.0  # 10秒超时
            )
            self._local.connection.row_factory = sqlite3.Row
            # 启用 WAL 模式提高并发性能
            self._local.connection.execute("PRAGMA journal_mode=WAL")
            logger.debug(f"创建新的数据库连接 (线程: {threading.current_thread().name})")
        return self._local.connection

    @contextmanager
    def get_connection(self):
        """获取数据库连接（上下文管理器）"""
        conn = self._get_connection()
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            logger.error(f"数据库操作失败: {str(e)}")
            raise
        finally:
            # 不关闭连接，保持复用
            pass

    def close_connection(self):
        """关闭当前线程的数据库连接"""
        if hasattr(self._local, "connection") and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
            logger.debug(f"关闭数据库连接 (线程: {threading.current_thread().name})")

    def query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        执行查询语句

        Args:
            sql: SQL 查询语句
            params: 查询参数

        Returns:
            查询结果列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def execute(self, sql: str, params: tuple = None) -> int:
        """
        执行更新语句（INSERT, UPDATE, DELETE）

        Args:
            sql: SQL 更新语句
            params: 更新参数

        Returns:
            影响的行数
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            conn.commit()
            return cursor.rowcount

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """
        插入数据

        Args:
            table: 表名
            data: 要插入的数据字典

        Returns:
            新插入记录的 ID
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(data.values()))
            conn.commit()
            return cursor.lastrowid

    def update(self, table: str, data: Dict[str, Any], where: str, where_params: tuple = None) -> int:
        """
        更新数据

        Args:
            table: 表名
            data: 要更新的数据字典
            where: WHERE 条件（如 "id = ?"）
            where_params: WHERE 条件参数

        Returns:
            影响的行数
        """
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        params = tuple(data.values()) + (where_params or ())
        return self.execute(sql, params)

    def delete(self, table: str, where: str, where_params: tuple = None) -> int:
        """
        删除数据

        Args:
            table: 表名
            where: WHERE 条件（如 "id = ?"）
            where_params: WHERE 条件参数

        Returns:
            影响的行数
        """
        sql = f"DELETE FROM {table} WHERE {where}"
        return self.execute(sql, where_params)

    def get_by_id(self, table: str, id_column: str, id_value: Any) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取单条记录

        Args:
            table: 表名
            id_column: ID 列名
            id_value: ID 值

        Returns:
            记录字典或 None
        """
        sql = f"SELECT * FROM {table} WHERE {id_column} = ?"
        results = self.query(sql, (id_value,))
        return results[0] if results else None

    def get_all(self, table: str, order_by: str = None) -> List[Dict[str, Any]]:
        """
        获取表中所有记录

        Args:
            table: 表名
            order_by: 排序字段（如 "id DESC"）

        Returns:
            记录列表
        """
        sql = f"SELECT * FROM {table}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        return self.query(sql)

    def count(self, table: str, where: str = None, where_params: tuple = None) -> int:
        """
        统计记录数

        Args:
            table: 表名
            where: WHERE 条件（可选）
            where_params: WHERE 条件参数

        Returns:
            记录数
        """
        sql = f"SELECT COUNT(*) as count FROM {table}"
        if where:
            sql += f" WHERE {where}"
        result = self.query(sql, where_params)
        return result[0]["count"] if result else 0


# 创建全局数据库实例
db = Database()
