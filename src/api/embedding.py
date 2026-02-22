"""
本地 Embedding 接口

使用 sentence-transformers 提供本地 embedding 服务
"""
from typing import List
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.logger import logger

router = APIRouter()

# 全局模型实例（延迟加载）
_embedding_model = None


def get_embedding_model():
    """获取 embedding 模型（延迟加载）"""
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            # 使用轻量级中文模型
            logger.info("正在加载 embedding 模型...")
            _embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("Embedding 模型加载成功")
        except ImportError:
            logger.error("sentence-transformers 未安装，请运行: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"加载 embedding 模型失败: {e}")
            raise
    return _embedding_model


# ==================== 数据模型 ====================

class EmbeddingRequest(BaseModel):
    """Embedding 请求"""
    input: str | List[str] = Field(..., description="要生成 embedding 的文本（单个字符串或字符串列表）")
    model: str = Field("text-embedding-local", description="模型名称")


class EmbeddingData(BaseModel):
    """单个 embedding 数据"""
    object: str = "embedding"
    embedding: List[float]
    index: int


class EmbeddingResponse(BaseModel):
    """Embedding 响应"""
    object: str = "list"
    data: List[EmbeddingData]
    model: str
    usage: dict


# ==================== Embedding 接口 ====================

@router.post("/embeddings")
async def create_embeddings(request: Request, req: EmbeddingRequest):
    """
    创建文本 embedding（兼容 OpenAI API 格式）

    支持单个文本或文本列表
    """
    try:
        # 获取模型
        model = get_embedding_model()

        # 处理输入
        texts = [req.input] if isinstance(req.input, str) else req.input

        logger.info(f"生成 embedding，文本数量: {len(texts)}")

        # 生成 embeddings
        embeddings = model.encode(texts, convert_to_numpy=True)

        # 构建响应
        data = []
        for i, embedding in enumerate(embeddings):
            data.append(EmbeddingData(
                embedding=embedding.tolist(),
                index=i
            ))

        # 计算 token 使用量（估算）
        total_tokens = sum(len(text.split()) for text in texts)

        response = EmbeddingResponse(
            data=data,
            model=req.model,
            usage={
                "prompt_tokens": total_tokens,
                "total_tokens": total_tokens
            }
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"生成 embedding 失败: {e}")
        return {
            "code": 500,
            "message": f"生成 embedding 失败: {str(e)}"
        }


@router.get("/models")
async def list_models(request: Request):
    """
    列出可用的 embedding 模型（兼容 OpenAI API 格式）
    """
    return {
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


@router.get("/health")
async def health_check(request: Request):
    """健康检查"""
    try:
        # 尝试加载模型
        get_embedding_model()
        return {
            "status": "healthy",
            "model": "paraphrase-multilingual-MiniLM-L12-v2"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
