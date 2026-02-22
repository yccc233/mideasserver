# DeepSeek API 配置问题排查

## 当前问题

DeepSeek API Key 认证失败，错误信息：
```
Authentication Fails, Your api key: ****851a is invalid
```

## 排查步骤

### 1. 验证 API Key

请检查以下内容：

1. **登录 DeepSeek 平台**
   - 访问：https://platform.deepseek.com/
   - 登录您的账号

2. **检查 API Key**
   - 进入 API Keys 管理页面
   - 确认 API Key 是否有效
   - 检查是否有使用限制或余额不足

3. **重新生成 API Key**
   - 如果 API Key 已过期或无效，重新生成一个新的
   - 复制新的 API Key

### 2. 更新配置

编辑 `.env` 文件，更新 API Key：

```bash
OPENAI_API_KEY=sk-your-new-deepseek-api-key-here
```

### 3. 重新测试

```bash
python test_deepseek_api.py
```

## 备用方案

如果 DeepSeek API 暂时无法使用，可以切换到其他 LLM 提供商：

### 方案 1: 使用 OpenAI（推荐）

```bash
# .env 配置
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini  # 或 gpt-3.5-turbo（更便宜）

TAVILY_API_KEY=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
RETRIEVER=tavily
```

获取 OpenAI API Key: https://platform.openai.com/api-keys

### 方案 2: 使用 Moonshot（国内）

```bash
# .env 配置
OPENAI_API_KEY=sk-your-moonshot-api-key-here
OPENAI_API_BASE=https://api.moonshot.cn/v1
OPENAI_MODEL=moonshot-v1-8k

TAVILY_API_KEY=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
RETRIEVER=tavily
```

获取 Moonshot API Key: https://platform.moonshot.cn/

### 方案 3: 使用 Zhipu AI（智谱清言）

```bash
# .env 配置
OPENAI_API_KEY=your-zhipu-api-key-here
OPENAI_API_BASE=https://open.bigmodel.cn/api/paas/v4
OPENAI_MODEL=glm-4

TAVILY_API_KEY=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
RETRIEVER=tavily
```

获取 Zhipu API Key: https://open.bigmodel.cn/

### 方案 4: 使用 Ollama（本地部署，免费）

如果有本地 GPU，可以使用 Ollama 部署本地模型：

```bash
# 安装 Ollama
# 访问 https://ollama.ai/ 下载安装

# 拉取模型
ollama pull qwen2:7b

# .env 配置
OPENAI_API_KEY=ollama
OPENAI_API_BASE=http://localhost:11434/v1
OPENAI_MODEL=qwen2:7b

TAVILY_API_KEY=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
RETRIEVER=tavily
```

## 成本对比

| 提供商 | 模型 | 价格（每百万 tokens） | 质量 |
|--------|------|---------------------|------|
| OpenAI | gpt-4o-mini | $0.15 / $0.60 | ⭐⭐⭐⭐⭐ |
| OpenAI | gpt-3.5-turbo | $0.50 / $1.50 | ⭐⭐⭐⭐ |
| DeepSeek | deepseek-chat | $0.14 / $0.28 | ⭐⭐⭐⭐ |
| Moonshot | moonshot-v1-8k | ¥12 / ¥12 | ⭐⭐⭐⭐ |
| Zhipu | glm-4 | ¥50 / ¥50 | ⭐⭐⭐⭐ |
| Ollama | qwen2:7b | 免费（本地） | ⭐⭐⭐ |

## 推荐配置

### 最佳性价比（国际）
```bash
OPENAI_API_KEY=sk-your-openai-key
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
RETRIEVER=tavily
```

### 最佳性价比（国内）
```bash
OPENAI_API_KEY=sk-your-moonshot-key
OPENAI_API_BASE=https://api.moonshot.cn/v1
OPENAI_MODEL=moonshot-v1-8k
RETRIEVER=tavily
```

### 完全免费（需要本地 GPU）
```bash
OPENAI_API_KEY=ollama
OPENAI_API_BASE=http://localhost:11434/v1
OPENAI_MODEL=qwen2:7b
RETRIEVER=duckduckgo  # 免费搜索引擎
```

## 测试新配置

更新 `.env` 后，运行测试：

```bash
# 1. 测试 API 连接
python test_deepseek_api.py  # 修改脚本中的配置

# 2. 测试 GPT Researcher
python test_gptr_quick.py
```

## 联系支持

如果问题持续存在：

1. **DeepSeek 支持**
   - 官网：https://www.deepseek.com/
   - 文档：https://platform.deepseek.com/docs

2. **项目支持**
   - 查看日志：`/work/logs/MIdeasServer/`
   - 提交 Issue：项目 GitHub 仓库
