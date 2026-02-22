"""
创建任务执行记录表

替代原有的 tbl_agent_task_log 表，提供更完善的任务执行记录功能
"""
import sqlite3
import sys
import io
from pathlib import Path
from datetime import datetime

# 设置控制台编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

db_path = Path(__file__).parent / "Mideas.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 创建任务执行记录表
create_table_sql = """
CREATE TABLE IF NOT EXISTS tbl_task_execution (
    execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    task_name TEXT NOT NULL,
    task_prompt TEXT,
    status INTEGER DEFAULT 0,
    start_time TEXT NOT NULL,
    end_time TEXT,
    execution_duration INTEGER,
    result_summary TEXT,
    result_detail TEXT,
    error_message TEXT,
    error_detail TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tbl_agent_schedule_task(task_id)
);
"""

cursor.execute(create_table_sql)
conn.commit()

print("✓ 表 tbl_task_execution 创建成功！")

# 创建索引以提高查询性能
indexes = [
    "CREATE INDEX IF NOT EXISTS idx_task_id ON tbl_task_execution(task_id);",
    "CREATE INDEX IF NOT EXISTS idx_status ON tbl_task_execution(status);",
    "CREATE INDEX IF NOT EXISTS idx_start_time ON tbl_task_execution(start_time DESC);",
]

for index_sql in indexes:
    cursor.execute(index_sql)

conn.commit()
print("✓ 索引创建成功！")

# 显示表结构
cursor.execute("PRAGMA table_info(tbl_task_execution);")
columns = cursor.fetchall()

print("\n表结构：")
print(f"{'序号':<6} {'字段名':<20} {'类型':<15} {'非空':<6} {'默认值':<10} {'主键':<6}")
print("-" * 80)
for col in columns:
    cid, name, type_, notnull, default, pk = col
    print(f"{cid:<6} {name:<20} {type_:<15} {notnull:<6} {str(default):<10} {pk:<6}")

# 显示字段说明
print("\n字段说明：")
print("-" * 80)
field_descriptions = [
    ("execution_id", "执行记录ID（主键，自增）"),
    ("task_id", "关联的任务ID"),
    ("task_name", "任务名称（冗余字段，方便查询）"),
    ("task_prompt", "任务提示词（冗余字段）"),
    ("status", "执行状态（0=运行中，1=成功，2=失败）"),
    ("start_time", "开始时间"),
    ("end_time", "结束时间"),
    ("execution_duration", "执行时长（秒）"),
    ("result_summary", "结果摘要（成功时，前500字符）"),
    ("result_detail", "完整结果（可选，存储完整报告）"),
    ("error_message", "错误信息（失败时）"),
    ("error_detail", "错误详情（失败时，堆栈信息等）"),
    ("created_at", "创建时间"),
    ("updated_at", "更新时间"),
]

for field, desc in field_descriptions:
    print(f"{field:<20} - {desc}")

# 检查是否存在旧表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tbl_agent_task_log';")
old_table = cursor.fetchone()

if old_table:
    print("\n" + "=" * 80)
    print("⚠ 检测到旧表 tbl_agent_task_log")
    print("建议：")
    print("1. 如需迁移数据，请手动执行数据迁移脚本")
    print("2. 确认数据迁移完成后，可删除旧表：DROP TABLE tbl_agent_task_log;")
    print("=" * 80)

conn.close()
print("\n✓ 初始化完成！")
