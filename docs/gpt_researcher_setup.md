# GPT Researcher 配置指南

## 概述

GPT Researcher 是一个自主的 AI 研究助手，可以根据给定的查询进行深度研究并生成详细报告。本文档介绍如何在 Mideas Server 中配置和使用 GPT Researcher。

## 前置要求

1. Python 3.10+
2. OpenAI API 密钥（用于 LLM）
3. 搜索引擎 API 密钥（选择其中一个）

## 配置步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下参数：

#### 必需配置

```bash
# OpenAI API 配置（必需）
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4  # 或 gpt-3.5-turbo（更便宜但效果稍差）
```

#### 搜索引擎配置（选择其中一个）

**选项 1: Tavily（推荐）**

Tavily 是专为 AI 研究设计的搜索 API，提供高质量的搜索结果。

```bash
RETRIEVER=tavily
TAVILY_API_KEY=tvly-your-tavily-api-key-here
```

获取 API Key: https://tavily.com/

**选项 2: Google Custom Search**

```bash
RETRIEVER=google
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_CX=your-custom-search-engine-id-here
```

获取方式：
1. Google API Key: https://console.cloud.google.com/apis/credentials
2. Custom Search Engine ID: https://programmablesearchengine.google.com/

**选项 3: Bing Search**

```bash
RETRIEVER=bing
BING_API_KEY=your-bing-api-key-here
```

获取 API Key: https://www.microsoft.com/en-us/bing/apis/bing-web-search-api

**选项 4: Serper（Google Search 替代）**

```bash
RETRIEVER=serper
SERPER_API_KEY=your-serper-api-key-here
```

获取 API Key: https://serper.dev/

**选项 5: DuckDuckGo（免费，无需 API Key）**

```bash
RETRIEVER=duckduckgo
```

注意：DuckDuckGo 免费但搜索质量和速度可能不如付费选项。

#### 可选配置

```bash
# OpenAI API 端点（可选，用于自定义端点）
OPENAI_API_BASE=https://api.openai.com/v1

# 嵌入模型（用于文档相似度计算）
EMBEDDING_MODEL=openai:text-embedding-3-small

# 搜索结果数量
MAX_SEARCH_RESULTS=5

# 网页内容分块大小
BROWSE_CHUNK_MAX_LENGTH=8192

# 摘要 token 限制
SUMMARY_TOKEN_LIMIT=700
```

### 3. 验证配置

创建测试脚本 `test_gptr_config.py`：

```python
import asyncio
import os
from src.config import settings

async def test_gptr_config():
    """测试 GPT Researcher 配置"""
    print("=" * 80)
    print("GPT Researcher 配置检查")
    print("=" * 80)

    # 检查必需配置
    print("\n[必需配置]")
    print(f"OpenAI API Key: {'✓ 已配置' if settings.openai_api_key else '✗ 未配置'}")
    print(f"OpenAI Model: {settings.openai_model}")
    print(f"Retriever: {settings.retriever}")

    # 检查搜索引擎配置
    print("\n[搜索引擎配置]")
    if settings.retriever == "tavily":
        print(f"Tavily API Key: {'✓ 已配置' if settings.tavily_api_key else '✗ 未配置'}")
    elif settings.retriever == "google":
        print(f"Google API Key: {'✓ 已配置' if settings.google_api_key else '✗ 未配置'}")
        print(f"Google CX: {'✓ 已配置' if settings.google_cx else '✗ 未配置'}")
    elif settings.retriever == "bing":
        print(f"Bing API Key: {'✓ 已配置' if settings.bing_api_key else '✗ 未配置'}")
    elif settings.retriever == "serper":
        print(f"Serper API Key: {'✓ 已配置' if settings.serper_api_key else '✗ 未配置'}")
    elif settings.retriever == "duckduckgo":
        print("DuckDuckGo: ✓ 无需 API Key")

    # 检查可选配置
    print("\n[可选配置]")
    print(f"Embedding Model: {settings.embedding_model}")
    print(f"Max Search Results: {settings.max_search_results}")
    print(f"Browse Chunk Max Length: {settings.browse_chunk_max_length}")
    print(f"Summary Token Limit: {settings.summary_token_limit}")

    # 尝试导入 GPT Researcher
    print("\n[依赖检查]")
    try:
        from gpt_researcher import GPTResearcher
        print("GPT Researcher: ✓ 已安装")
    except ImportError:
        print("GPT Researcher: ✗ 未安装，请运行 pip install gpt-researcher")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(test_gptr_config())
```

运行测试：

```bash
python test_gptr_config.py
```

## 使用方式

### 1. 通过 API 创建定时任务

```bash
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "每日 AI 新闻摘要",
    "task_info": "每天早上 8 点生成 AI 领域的新闻摘要",
    "task_conf": "8 * * *",
    "task_prompt": "请研究并总结今天人工智能领域的最新进展和重要新闻",
    "task_status": 1
  }'
```

### 2. 手动触发研究任务

```python
import asyncio
from src.process.agent import AgentScheduler
from src.database import db

async def manual_research():
    """手动执行研究任务"""
    # 获取任务
    task = db.get_by_id("tbl_agent_schedule_task", "task_id", 1)

    # 执行研究
    scheduler = AgentScheduler()
    await scheduler.execute_gpt_research(task)

if __name__ == "__main__":
    asyncio.run(manual_research())
```

### 3. 查看执行日志

```bash
# 查询任务执行日志
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/logs \
  -H "Content-Type: application/json" \
  -d '{"task_id": 1, "limit": 10}'

# 查看最新执行日志
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/logs/latest \
  -H "Content-Type: application/json" \
  -d '{"task_id": 1}'

# 查看执行统计
curl -X POST http://localhost:18888/mideasserver/task/agentTasks/logs/stats \
  -H "Content-Type: application/json" \
  -d '{"task_id": 1}'
```

## 报告类型

GPT Researcher 支持多种报告类型，可以在代码中修改 `report_type` 参数：

- `research_report` - 详细研究报告（默认）
- `quick_report` - 快速摘要报告
- `outline_report` - 大纲式报告
- `resource_report` - 资源列表报告
- `custom_report` - 自定义报告

修改位置：`src/process/agent.py` 的 `execute_gpt_research` 方法。

## 成本估算

### OpenAI API 成本

- GPT-4: ~$0.03-0.06 每次研究（取决于查询复杂度）
- GPT-3.5-turbo: ~$0.01-0.02 每次研究

### 搜索 API 成本

- Tavily: 免费套餐 1000 次/月，付费 $0.001/次
- Google Custom Search: 免费 100 次/天，付费 $5/1000 次
- Bing Search: 免费套餐 1000 次/月
- Serper: 免费 2500 次，付费 $0.001/次
- DuckDuckGo: 完全免费

## 常见问题

### 1. 报错：`No API key found for OpenAI`

确保在 `.env` 文件中配置了 `OPENAI_API_KEY`。

### 2. 报错：`No API key found for [搜索引擎]`

确保配置了对应搜索引擎的 API Key，或者切换到 DuckDuckGo（无需 API Key）。

### 3. 研究速度慢

- 减少 `MAX_SEARCH_RESULTS` 的值
- 使用 `gpt-3.5-turbo` 替代 `gpt-4`
- 使用 `quick_report` 报告类型

### 4. 研究质量不高

- 增加 `MAX_SEARCH_RESULTS` 的值
- 使用 `gpt-4` 模型
- 优化 `task_prompt`，提供更具体的研究方向
- 使用 Tavily 或 Google 搜索引擎（质量优于 DuckDuckGo）

### 5. 自定义 OpenAI 端点

如果使用 Azure OpenAI 或其他兼容端点：

```bash
OPENAI_API_BASE=https://your-custom-endpoint.com/v1
OPENAI_API_KEY=your-custom-api-key
```

## 高级配置

### 自定义研究流程

编辑 `src/process/agent.py`，修改 `execute_gpt_research` 方法：

```python
# 自定义研究参数
researcher = GPTResearcher(
    query=task_prompt,
    report_type="research_report",
    source_urls=["https://example.com"],  # 指定搜索来源
    config_path=None
)

# 自定义研究深度
researcher.max_iterations = 3  # 研究迭代次数
researcher.max_subtopics = 5   # 子主题数量
```

### 保存研究报告

可以将生成的报告保存到文件或数据库：

```python
# 保存到文件
report_path = f"reports/{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
with open(report_path, "w", encoding="utf-8") as f:
    f.write(report)

# 或保存到数据库
db.update("tbl_agent_task_log", {
    "result_summary": report  # 完整报告
}, "log_id = ?", (log_id,))
```

## 参考资源

- GPT Researcher 官方文档: https://docs.gptr.dev/
- GPT Researcher GitHub: https://github.com/assafelovic/gpt-researcher
- Tavily API 文档: https://docs.tavily.com/
