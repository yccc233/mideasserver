"""
手动运行研究任务

快速执行指定的研究任务
"""
import asyncio
import sys
from src.process.agent import AgentScheduler
from src.database import db

# 设置控制台编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


async def list_tasks():
    """列出所有任务"""
    tasks = db.get_all("tbl_agent_schedule_task", order_by="task_id DESC")
    if not tasks:
        print("没有找到任务")
        return []

    print("\n可用任务列表：")
    print("-" * 80)
    for task in tasks:
        status = "✓ 启用" if task['task_status'] == 1 else "✗ 禁用"
        print(f"ID: {task['task_id']} | {status} | {task['task_name']}")
        print(f"  配置: {task['task_conf']}")
        print(f"  提示词: {task['task_prompt'][:50]}..." if len(task['task_prompt']) > 50 else f"  提示词: {task['task_prompt']}")
        print("-" * 80)

    return tasks


async def run_task(task_id: int = None):
    """运行指定任务"""
    if task_id is None:
        # 列出所有任务
        tasks = await list_tasks()
        if not tasks:
            return

        # 让用户选择
        print("\n请输入要执行的任务 ID（直接回车执行最新任务）：", end=" ")
        user_input = input().strip()

        if user_input:
            task_id = int(user_input)
        else:
            task_id = tasks[0]['task_id']

    # 获取任务
    task = db.get_by_id("tbl_agent_schedule_task", "task_id", task_id)
    if not task:
        print(f"✗ 未找到任务 ID: {task_id}")
        return

    print(f"\n开始执行任务: {task['task_name']}")
    print(f"提示词: {task['task_prompt']}")
    print("\n执行中，请稍候...\n")

    # 执行研究
    scheduler = AgentScheduler()
    await scheduler.execute_gpt_research(task)

    # 查询执行结果
    executions = db.get_all(
        "tbl_task_execution",
        where="task_id = ?",
        params=(task_id,),
        order_by="start_time DESC",
        limit=1
    )

    if executions:
        execution = executions[0]
        print("\n" + "=" * 80)
        print("执行结果")
        print("=" * 80)
        print(f"状态: {'✓ 成功' if execution['status'] == 1 else '✗ 失败' if execution['status'] == 2 else '执行中'}")
        print(f"开始时间: {execution['start_time']}")
        print(f"结束时间: {execution['end_time']}")
        print(f"执行时长: {execution['execution_duration']}秒")

        if execution['status'] == 1:
            print(f"\n研究报告摘要:")
            print("-" * 80)
            print(execution['result_summary'])
            print("-" * 80)
        elif execution['status'] == 2:
            print(f"\n错误信息:")
            print("-" * 80)
            print(execution['error_message'])
            print("-" * 80)

        print(f"\n执行 ID: {execution['execution_id']}")
        print("=" * 80)


async def run_custom_research():
    """运行自定义研究"""
    print("\n" + "=" * 80)
    print("自定义研究任务")
    print("=" * 80)

    print("\n请输入研究主题：", end=" ")
    query = input().strip()

    if not query:
        print("✗ 研究主题不能为空")
        return

    # 创建临时任务
    from datetime import datetime
    task_data = {
        "task_name": f"临时研究-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "task_info": "手动创建的临时研究任务",
        "task_conf": "* * * *",
        "task_prompt": query,
        "task_status": 0,  # 禁用状态，不会被调度器执行
        "insert_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    task_id = db.insert("tbl_agent_schedule_task", task_data)
    print(f"\n✓ 已创建临时任务 ID: {task_id}")

    # 执行任务
    await run_task(task_id)

    # 询问是否删除临时任务
    print("\n是否删除临时任务？(y/n)：", end=" ")
    delete = input().strip().lower()

    if delete == 'y':
        db.delete("tbl_agent_schedule_task", "task_id = ?", (task_id,))
        print("✓ 已删除临时任务")


async def main():
    """主函数"""
    print("=" * 80)
    print("GPT Researcher 任务执行工具")
    print("=" * 80)

    print("\n请选择操作：")
    print("1. 执行已有任务")
    print("2. 自定义研究")
    print("3. 查看任务列表")
    print("0. 退出")

    print("\n请输入选项（1-3）：", end=" ")
    choice = input().strip()

    if choice == "1":
        await run_task()
    elif choice == "2":
        await run_custom_research()
    elif choice == "3":
        await list_tasks()
    elif choice == "0":
        print("再见！")
    else:
        print("✗ 无效选项")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n✗ 错误: {e}")
