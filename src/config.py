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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# 创建全局配置实例
settings = Settings()
