# GPT Researcher 快速开始

## 最简配置（5分钟上手）

### 1. 获取 API Keys

**OpenAI API Key（必需）**
- 访问：https://platform.openai.com/api-keys
- 创建新的 API Key
- 复制保存

**Tavily API Key（推荐，免费 1000 次/月）**
- 访问：https://tavily.com/
- 注册账号
- 获取 API Key

### 2. 配置环境变量

编辑 `.env` 文件：

```bash
# 最简配置
OPENAI_API_KEY=sk-your-openai-key-here
TAVILY_API_KEY=tvly-your-tavily-key-here
RETRIEVER=tavily
```

### 3. 验证配置

```bash
python test_gptr_config.py
```

### 4. 创建第一个研究任务

```bash
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "测试研究任务",
    "task_info": "测试 GPT Researcher 功能",
    "task_conf": "* * * *",
    "task_prompt": "什么是大语言模型？请简要介绍其原理和应用。",
    "task_status": 1
  }'
```

### 5. 手动触发执行

创建 `run_task.py`：

```python
import asyncio
from src.process.agent import AgentScheduler
from src.database import db

async def run():
    # 获取最新任务
    tasks = db.get_all("tbl_agent_schedule_task", order_by="task_id DESC", limit=1)
    if not tasks:
        print("没有找到任务")
        return

    task = tasks[0]
    print(f"执行任务: {task['task_name']}")

    # 执行研究
    scheduler = AgentScheduler()
    await scheduler.execute_gpt_research(task)

    print("任务执行完成！")

if __name__ == "__main__":
    asyncio.run(run())
```

运行：

```bash
python run_task.py
```

### 6. 查看结果

```bash
# 查看最新日志
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/logs \
  -H "Content-Type: application/json" \
  -d '{"limit": 1}'
```

## 免费方案（无需付费 API）

如果暂时不想付费，可以使用 DuckDuckGo（完全免费）：

```bash
# .env 配置
OPENAI_API_KEY=sk-your-openai-key-here
RETRIEVER=duckduckgo
```

注意：DuckDuckGo 搜索质量和速度不如 Tavily，但完全免费。

## 成本估算

### 单次研究成本

使用 GPT-4 + Tavily：
- OpenAI API: ~$0.03-0.06
- Tavily API: ~$0.005
- **总计: ~$0.035-0.065**

使用 GPT-3.5-turbo + Tavily：
- OpenAI API: ~$0.01-0.02
- Tavily API: ~$0.005
- **总计: ~$0.015-0.025**

### 免费额度

- Tavily: 1000 次/月免费
- OpenAI: 新用户有 $5 免费额度

## 常见问题

**Q: 研究需要多长时间？**
A: 通常 30-90 秒，取决于查询复杂度和网络速度。

**Q: 如何降低成本？**
A: 使用 `gpt-3.5-turbo` 模型，减少 `MAX_SEARCH_RESULTS`。

**Q: 支持中文吗？**
A: 完全支持，可以用中文提问和生成中文报告。

**Q: 可以指定搜索来源吗？**
A: 可以，修改 `src/process/agent.py` 中的 `source_urls` 参数。

## 下一步

- 阅读完整配置指南：[docs/gpt_researcher_setup.md](gpt_researcher_setup.md)
- 查看 API 文档：[docs/task_log_api.md](task_log_api.md)
- 了解定时任务配置：查看 `src/api/task.py` 中的 `task_conf` 格式说明
