"""
智能体定时任务调度器

功能：
- 每分钟执行一次检查
- 从数据库获取所有启用的定时任务
- 根据任务配置的时间判断是否需要执行
- 执行 GPT Researcher 研究任务
- 跳过正在执行中的任务，避免重复执行
"""
import asyncio
import os
from datetime import datetime
from typing import Dict, Any

from src.config import settings
from src.database import db
from src.logger import logger


class AgentScheduler:
    """智能体定时任务调度器"""

    def __init__(self):
        self.running = False
        self.task = None
        self.executing_tasks = set()  # 记录正在执行的任务ID
        self.last_execution_time = {}  # 记录每个任务最后执行的时间（小时级别）格式：{task_id: "YYYY-MM-DD-HH"}

    def parse_time_config(self, task_conf: str) -> Dict[str, Any]:
        """
        解析任务时间配置

        格式：时 日 月 周
        示例：
        - "6,8 * * *" - 每天6点和8点
        - "20 * * 0" - 每周日晚8点
        - "9 1 * *" - 每月1号早9点
        - "14 * * 1-5" - 每周一到周五下午2点

        Args:
            task_conf: 时间配置字符串

        Returns:
            解析后的配置字典
        """
        try:
            parts = task_conf.strip().split()
            if len(parts) != 4:
                logger.error(f"时间配置格式错误: {task_conf}")
                return None

            return {
                "hour": parts[0],  # 时 (0-23)
                "day": parts[1],  # 日 (1-31)
                "month": parts[2],  # 月 (1-12)
                "weekday": parts[3]  # 周 (0-6, 0=周日)
            }
        except Exception as e:
            logger.error(f"解析时间配置失败: {task_conf}, 错误: {e}")
            return None

    def match_value(self, config_value: str, current_value: int) -> bool:
        """
        匹配单个时间字段

        Args:
            config_value: 配置值（如 "*", "6", "6,8", "1-5"）
            current_value: 当前值

        Returns:
            是否匹配
        """
        # * 表示任意值
        if config_value == "*":
            return True

        # 逗号分隔的多个值（如 6,8,10）
        if "," in config_value:
            values = [int(v.strip()) for v in config_value.split(",")]
            return current_value in values

        # 范围值（如 1-5）
        if "-" in config_value:
            start, end = map(int, config_value.split("-"))
            return start <= current_value <= end

        # 单个值
        return int(config_value) == current_value

    def should_execute(self, task_conf: str, now: datetime = None) -> bool:
        """
        判断任务是否应该在当前时间执行

        Args:
            task_conf: 任务时间配置
            now: 当前时间（用于测试）

        Returns:
            是否应该执行
        """
        if now is None:
            now = datetime.now()

        config = self.parse_time_config(task_conf)
        if not config:
            return False

        # 匹配小时
        if not self.match_value(config["hour"], now.hour):
            return False

        # 匹配日期
        if not self.match_value(config["day"], now.day):
            return False

        # 匹配月份
        if not self.match_value(config["month"], now.month):
            return False

        # 匹配星期（0=周日, 1=周一, ..., 6=周六）
        weekday = (now.weekday() + 1) % 7  # Python: 0=周一, 转换为 0=周日
        if not self.match_value(config["weekday"], weekday):
            return False

        return True

    async def execute_gpt_research(self, task: Dict[str, Any]):
        """
        执行 GPT Research 任务

        Args:
            task: 任务信息
        """
        task_id = task.get("task_id")
        task_name = task.get("task_name")
        task_prompt = task.get("task_prompt", "")

        # 标记任务开始执行
        self.executing_tasks.add(task_id)

        try:
            # 记录任务开始时间
            start_time = datetime.now()
            start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")

            # 插入执行记录（状态：0=运行中）
            execution_id = db.insert("tbl_task_execution", {
                "task_id": task_id,
                "task_name": task_name,
                "task_prompt": task_prompt,
                "start_time": start_time_str,
                "status": 0,
                "created_at": start_time_str,
                "updated_at": start_time_str
            })

            logger.info(f"[执行ID: {execution_id}] 开始执行任务: {task_name}")

            # 设置 GPT Researcher 环境变量
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key
            os.environ["OPENAI_API_BASE"] = settings.openai_api_base
            os.environ["RETRIEVER"] = settings.retriever
            os.environ["SMART_LLM_MODEL"] = settings.openai_model  # 设置主 LLM 模型
            os.environ["FAST_LLM_MODEL"] = settings.openai_model  # 设置快速 LLM 模型
            os.environ["REPORT_FORMAT"] = "markdown"  # 报告格式
            os.environ["LANGUAGE"] = "chinese"  # 设置输出语言为中文

            # 设置 Embedding 配置
            if settings.embedding_provider:
                os.environ["EMBEDDING_PROVIDER"] = settings.embedding_provider
            if settings.embedding_api_url:
                os.environ["OPENAI_EMBEDDING_API_BASE"] = settings.embedding_api_url
            if settings.embedding_model:
                os.environ["EMBEDDING_MODEL"] = settings.embedding_model

            # 根据配置的搜索引擎设置对应的 API Key
            if settings.retriever == "tavily" and settings.tavily_api_key:
                os.environ["TAVILY_API_KEY"] = settings.tavily_api_key
            elif settings.retriever == "google" and settings.google_api_key:
                os.environ["GOOGLE_API_KEY"] = settings.google_api_key
                os.environ["GOOGLE_CX"] = settings.google_cx
            elif settings.retriever == "bing" and settings.bing_api_key:
                os.environ["BING_API_KEY"] = settings.bing_api_key
            elif settings.retriever == "serper" and settings.serper_api_key:
                os.environ["SERPER_API_KEY"] = settings.serper_api_key

            # 导入 GPT Researcher
            from gpt_researcher import GPTResearcher

            logger.info(f"[执行ID: {execution_id}] 使用模型: {settings.openai_model}")
            logger.info(f"[执行ID: {execution_id}] API 端点: {settings.openai_api_base}")
            logger.info(f"[执行ID: {execution_id}] 搜索引擎: {settings.retriever}")

            # 创建研究器实例
            researcher = GPTResearcher(
                query=task_prompt,
                report_type="research_report",  # 研究报告类型
                config_path=None  # 使用环境变量配置
            )

            # 执行研究
            logger.info(f"[执行ID: {execution_id}] 开始进行研究...")
            await researcher.conduct_research()

            # 生成报告
            logger.info(f"[执行ID: {execution_id}] 生成研究报告...")
            report = await researcher.write_report()

            # 截取报告摘要（前500字符）
            result_summary = report[:500] + "..." if len(report) > 500 else report

            # 计算执行时长
            end_time = datetime.now()
            end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
            duration = int((end_time - start_time).total_seconds())

            # 更新执行记录（状态：1=成功）
            db.update("tbl_task_execution", {
                "end_time": end_time_str,
                "status": 1,
                "result_summary": result_summary,
                "result_detail": report,
                "execution_duration": duration,
                "updated_at": end_time_str
            }, "execution_id = ?", (execution_id,))

            logger.info(f"[执行ID: {execution_id}] 任务完成: {task_name}, 耗时: {duration}秒")

        except Exception as e:
            # 计算执行时长
            end_time = datetime.now()
            end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
            duration = int((end_time - start_time).total_seconds())

            error_msg = str(e)

            # 获取详细错误信息
            import traceback
            error_detail = traceback.format_exc()

            # 更新执行记录（状态：2=失败）
            db.update("tbl_task_execution", {
                "end_time": end_time_str,
                "status": 2,
                "error_message": error_msg,
                "error_detail": error_detail,
                "execution_duration": duration,
                "updated_at": end_time_str
            }, "execution_id = ?", (execution_id,))

            logger.error(f"[执行ID: {execution_id}] 任务失败: {task_name}, 错误: {error_msg}")
            logger.debug(f"[执行ID: {execution_id}] 错误详情: {error_detail}")
        finally:
            # 无论成功或失败，都要移除执行标记
            self.executing_tasks.discard(task_id)

    async def check_and_execute_tasks(self):
        """检查并执行符合条件的任务"""
        try:
            # 获取所有启用的任务（task_status = 1）
            tasks = db.get_all(
                "tbl_agent_schedule_task",
                where="task_status = 1",
                order_by="task_id ASC"
            )

            if not tasks:
                logger.debug("扫描完成：没有启用的定时任务")
                return

            now = datetime.now()
            current_time_str = now.strftime('%Y-%m-%d %H:%M:%S')
            current_hour_key = now.strftime("%Y-%m-%d-%H")

            # 扫描统计
            total_tasks = len(tasks)
            executed_count = 0
            skipped_count = 0

            logger.info(f"========== 开始扫描定时任务 ==========")
            logger.info(f"扫描时间: {current_time_str}")
            logger.info(f"启用任务数: {total_tasks}")

            # 检查每个任务
            for task in tasks:
                task_id = task.get("task_id")
                task_name = task.get("task_name")
                task_conf = task.get("task_conf")

                logger.debug(f"检查任务: {task_name} (ID: {task_id}), 配置: {task_conf}")

                if not task_conf:
                    logger.warning(f"任务 {task_name} (ID: {task_id}) 缺少时间配置，跳过")
                    skipped_count += 1
                    continue

                # 检查任务是否正在执行中
                if task_id in self.executing_tasks:
                    logger.info(f"跳过任务 {task_name} (ID: {task_id}): 正在执行中")
                    skipped_count += 1
                    continue

                # 判断是否应该执行
                if self.should_execute(task_conf, now):
                    # 检查是否在同一小时内已经执行过
                    last_exec_time = self.last_execution_time.get(task_id)

                    if last_exec_time == current_hour_key:
                        logger.info(f"跳过任务 {task_name} (ID: {task_id}): 当前小时 {current_hour_key} 已执行过")
                        skipped_count += 1
                        continue

                    # 记录本次执行的小时
                    self.last_execution_time[task_id] = current_hour_key

                    logger.info(f"✓ 触发任务: {task_name} (ID: {task_id}), 配置: {task_conf}")
                    executed_count += 1
                    # 使用 asyncio.create_task 异步执行，不阻塞其他任务检查
                    asyncio.create_task(self.execute_gpt_research(task))
                else:
                    logger.debug(f"跳过任务 {task_name} (ID: {task_id}): 不符合时间条件")
                    skipped_count += 1

            # 输出扫描统计
            logger.info(f"========== 扫描完成 ==========")
            logger.info(f"检查任务数: {total_tasks}, 触发执行: {executed_count}, 跳过: {skipped_count}")
            logger.info(f"正在执行的任务数: {len(self.executing_tasks)}")

        except Exception as e:
            logger.error(f"检查定时任务失败: {e}")

    async def run(self):
        """启动定时任务调度器（启动后10秒首次执行，之后每分钟执行一次）"""
        self.running = True
        logger.info("智能体定时任务调度器已启动（10秒后首次执行，之后每分钟扫描一次）")

        # 首次启动延迟10秒
        logger.debug("等待 10 秒后首次执行任务检查")
        await asyncio.sleep(10)

        while self.running:
            try:
                # 执行任务检查
                await self.check_and_execute_tasks()

                # 等待1分钟
                logger.debug(f"等待 60 秒（1分钟）到下次扫描")
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"定时任务调度器运行错误: {e}")
                # 出错后等待 60 秒再继续
                await asyncio.sleep(60)

    def stop(self):
        """停止定时任务调度器"""
        self.running = False
        logger.info("智能体定时任务调度器已停止")


# 全局调度器实例
scheduler = AgentScheduler()


async def start_scheduler():
    """启动调度器"""
    await scheduler.run()


def stop_scheduler():
    """停止调度器"""
    scheduler.stop()
