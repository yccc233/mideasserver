from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    app_name: str = "FastAPI应用"
    app_version: str = "1.0.0"
    debug: bool = True

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000

    # 数据库配置
    database_echo: bool = False  # 是否打印 SQL 语句

    # 日志配置
    log_dir: str = "/work/logs/MIdeasServer"

    # ==================== GPT Researcher 配置 ====================
    # OpenAI API 配置
    openai_api_key: str = ""
    openai_api_base: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4"

    # 搜索引擎配置
    tavily_api_key: str = ""
    google_api_key: str = ""
    google_cx: str = ""
    bing_api_key: str = ""
    serper_api_key: str = ""

    # Embedding 配置
    embedding_provider: str = ""  # custom 表示使用自定义 embedding
    embedding_api_url: str = ""
    embedding_model: str = "text-embedding-local"

    # GPT Researcher 其他配置
    retriever: str = "tavily"  # 搜索引擎类型
    max_search_results: int = 5
    browse_chunk_max_length: int = 8192
    summary_token_limit: int = 700

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# 创建全局配置实例
settings = Settings()
