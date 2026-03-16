from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    chroma_persist_dir: str = "./chroma_db"
    siliconflow_api_key: Optional[str] = None
    rate_limit: str = "10/minute"
    max_concurrent_requests: int = 3
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    siliconflow_base_url: str = "https://api.siliconflow.cn/v1"
    llm_model: str = "deepseek-ai/DeepSeek-V3"

    class Config:
        env_file = ".env"
        env_prefix = "APP_"

settings = Settings()