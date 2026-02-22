# 本地 Embedding 接口文档

## 概述

本地 Embedding 接口提供了一个兼容 OpenAI API 格式的文本向量化服务，使用 sentence-transformers 库实现，完全免费且可离线使用。

## 为什么需要 Embedding？

GPT Researcher 可以在没有 embedding 的情况下工作，但使用 embedding 可以：
- 提高文档检索的准确性
- 更好地理解文本语义相似度
- 优化研究结果的相关性

**注意**：当前配置下，GPT Researcher 已经可以正常工作，embedding 是可选功能。

## 安装依赖

```bash
pip install sentence-transformers torch scikit-learn
```

首次使用时会自动下载模型文件（约 400MB），需要网络连接。

## API 接口

### 1. 创建 Embeddings

**接口地址**: `POST /mideasserver/embedding/embeddings`

**速率限制**: 无限制

**请求格式**（兼容 OpenAI API）:

```json
{
  "input": "要生成 embedding 的文本",
  "model": "text-embedding-local"
}
```

或批量处理：

```json
{
  "input": [
    "文本1",
    "文本2",
    "文本3"
  ],
  "model": "text-embedding-local"
}
```

**响应格式**:

```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.123, -0.456, ...],  // 384维向量
      "index": 0
    }
  ],
  "model": "text-embedding-local",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

### 2. 列出可用模型

**接口地址**: `GET /mideasserver/embedding/models`

**响应**:

```json
{
  "object": "list",
  "data": [
    {
      "id": "text-embedding-local",
      "object": "model",
      "created": 1677610602,
      "owned_by": "local"
    }
  ]
}
```

### 3. 健康检查

**接口地址**: `GET /mideasserver/embedding/health`

**响应**:

```json
{
  "status": "healthy",
  "model": "paraphrase-multilingual-MiniLM-L12-v2"
}
```

## 使用示例

### Python 示例

```python
import requests

# 单个文本
response = requests.post(
    "http://localhost:18888/mideasserver/embedding/embeddings",
    json={
        "input": "人工智能是计算机科学的一个分支",
        "model": "text-embedding-local"
    }
)

result = response.json()
embedding = result['data'][0]['embedding']
print(f"Embedding 维度: {len(embedding)}")

# 批量处理
response = requests.post(
    "http://localhost:18888/mideasserver/embedding/embeddings",
    json={
        "input": [
            "人工智能是计算机科学的一个分支",
            "机器学习是人工智能的核心技术",
            "深度学习推动了AI的快速发展"
        ],
        "model": "text-embedding-local"
    }
)

result = response.json()
for i, item in enumerate(result['data']):
    print(f"文本 {i+1} 的 embedding 维度: {len(item['embedding'])}")
```

### cURL 示例

```bash
# 单个文本
curl -X POST http://localhost:18888/mideasserver/embedding/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": "人工智能是计算机科学的一个分支",
    "model": "text-embedding-local"
  }'

# 批量处理
curl -X POST http://localhost:18888/mideasserver/embedding/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": ["文本1", "文本2", "文本3"],
    "model": "text-embedding-local"
  }'
```

### 计算文本相似度

```python
import requests
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# 获取两个文本的 embeddings
response = requests.post(
    "http://localhost:18888/mideasserver/embedding/embeddings",
    json={
        "input": [
            "人工智能是计算机科学的一个分支",
            "机器学习是人工智能的核心技术"
        ],
        "model": "text-embedding-local"
    }
)

result = response.json()
emb1 = np.array(result['data'][0]['embedding']).reshape(1, -1)
emb2 = np.array(result['data'][1]['embedding']).reshape(1, -1)

# 计算余弦相似度
similarity = cosine_similarity(emb1, emb2)[0][0]
print(f"文本相似度: {similarity:.4f}")
```

## 配置 GPT Researcher 使用本地 Embedding

### 方案 1: 不使用 Embedding（推荐，当前配置）

GPT Researcher 可以在没有 embedding 的情况下正常工作，这是最简单的方案。

`.env` 配置：
```bash
# 不设置 EMBEDDING_PROVIDER 即可
```

### 方案 2: 使用本地 Embedding（可选）

如果想使用 embedding 提高检索质量：

1. **安装依赖**：
   ```bash
   pip install sentence-transformers torch
   ```

2. **更新 `.env` 配置**：
   ```bash
   EMBEDDING_PROVIDER=custom
   EMBEDDING_API_URL=http://localhost:18888/mideasserver/embedding/embeddings
   EMBEDDING_MODEL=text-embedding-local
   ```

3. **启动服务器**：
   ```bash
   python main.py
   ```

4. **测试 embedding**：
   ```bash
   python test_embedding.py
   ```

## 模型信息

### 使用的模型

- **模型名称**: `paraphrase-multilingual-MiniLM-L12-v2`
- **维度**: 384
- **语言支持**: 多语言（包括中文、英文等）
- **模型大小**: ~400MB
- **速度**: 快速（CPU 可用）
- **质量**: 适合大多数应用场景

### 性能指标

- **单文本处理**: ~10-50ms（CPU）
- **批量处理（10个文本）**: ~50-200ms（CPU）
- **GPU 加速**: 支持（需要安装 CUDA）

## 与 OpenAI Embedding 对比

| 特性 | 本地 Embedding | OpenAI Embedding |
|------|---------------|------------------|
| 成本 | 免费 | $0.00002/1K tokens |
| 速度 | 快（本地） | 中等（网络延迟） |
| 维度 | 384 | 1536 |
| 离线使用 | ✓ | ✗ |
| 隐私 | 完全本地 | 数据上传 |
| 质量 | 良好 | 优秀 |

## 常见问题

### 1. 首次使用很慢？

首次使用会下载模型文件（约 400MB），之后会缓存到本地。

### 2. 如何使用 GPU 加速？

安装 CUDA 版本的 PyTorch：
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### 3. 可以更换其他模型吗？

可以，编辑 `src/api/embedding.py`，修改模型名称：
```python
_embedding_model = SentenceTransformer('your-model-name')
```

推荐的中文模型：
- `paraphrase-multilingual-MiniLM-L12-v2` - 多语言，384维
- `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` - 多语言，768维
- `shibing624/text2vec-base-chinese` - 中文专用，768维

### 4. 内存占用多少？

- 模型加载: ~500MB
- 单次推理: ~100MB
- 建议最小内存: 2GB

### 5. 支持哪些语言？

当前模型支持 50+ 种语言，包括：
- 中文（简体/繁体）
- 英文
- 日文
- 韩文
- 等等

## 测试

运行测试脚本：

```bash
# 测试 embedding 功能
python test_embedding.py

# 测试 API 接口（需要先启动服务器）
curl http://localhost:18888/mideasserver/embedding/health
```

## 故障排查

### 问题：模型下载失败

**解决方案**：
1. 检查网络连接
2. 使用国内镜像：
   ```bash
   export HF_ENDPOINT=https://hf-mirror.com
   ```
3. 手动下载模型文件

### 问题：内存不足

**解决方案**：
1. 使用更小的模型
2. 减少批量处理的文本数量
3. 增加系统内存

### 问题：速度太慢

**解决方案**：
1. 使用 GPU 加速
2. 减少文本长度
3. 使用更小的模型

## 参考资源

- Sentence Transformers 文档: https://www.sbert.net/
- 模型库: https://huggingface.co/sentence-transformers
- GPT Researcher 文档: https://docs.gptr.dev/
