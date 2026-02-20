"""
创建智能体定时任务表
"""
import sqlite3
from pathlib import Path
from datetime import datetime

db_path = Path(__file__).parent / "Mideas.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 创建智能体定时任务表
create_table_sql = """
CREATE TABLE IF NOT EXISTS tbl_agent_schedule_task (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT NOT NULL,
    task_info TEXT,
    task_conf TEXT NOT NULL,
    task_prompt TEXT,
    task_status INTEGER DEFAULT 1,
    insert_time TEXT NOT NULL,
    update_time TEXT NOT NULL
);
"""

cursor.execute(create_table_sql)
conn.commit()

print("表 tbl_agent_schedule_task 创建成功！")

# 显示表结构
cursor.execute("PRAGMA table_info(tbl_agent_schedule_task);")
columns = cursor.fetchall()

print("\n表结构：")
print(f"{'序号':<6} {'字段名':<20} {'类型':<15} {'非空':<6} {'默认值':<10} {'主键':<6}")
print("-" * 70)
for col in columns:
    cid, name, type_, notnull, default, pk = col
    print(f"{cid:<6} {name:<20} {type_:<15} {notnull:<6} {str(default):<10} {pk:<6}")

conn.close()
