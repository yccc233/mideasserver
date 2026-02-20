"""
查看现有数据库结构的脚本
"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "Mideas.db"

if not db_path.exists():
    print(f"数据库文件不存在: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 获取所有表名
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("=" * 60)
print(f"数据库: {db_path}")
print("=" * 60)
print(f"\n共有 {len(tables)} 个表:\n")

for table in tables:
    table_name = table[0]
    print(f"\n表名: {table_name}")
    print("-" * 60)

    # 获取表结构
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()

    print(f"{'序号':<6} {'字段名':<20} {'类型':<15} {'非空':<6} {'默认值':<10} {'主键':<6}")
    print("-" * 60)
    for col in columns:
        cid, name, type_, notnull, default, pk = col
        print(f"{cid:<6} {name:<20} {type_:<15} {notnull:<6} {str(default):<10} {pk:<6}")

    # 获取记录数
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    print(f"\n记录数: {count}")

    # 显示前3条记录
    if count > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
        rows = cursor.fetchall()
        print(f"\n前 {len(rows)} 条记录示例:")
        for i, row in enumerate(rows, 1):
            print(f"  {i}. {row}")

conn.close()
print("\n" + "=" * 60)
