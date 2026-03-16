"""
配置文件：包含 API 配置和系统设置
"""
import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API 配置
class APIConfig:
    # SiliconFlow 配置
    SILICONFLOW_API_KEY: Optional[str] = os.getenv("SILICONFLOW_API_KEY") or "sk-spgaedwstfoynlbhwefwdrthhsstimobmesytdxxnfdjadae"
    SILICONFLOW_BASE_URL: str = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
    LLM_MODEL: str = "Qwen/Qwen2.5-Coder-32B-Instruct"
    EMBEDDING_MODEL: str = "BAAI/bge-large-zh-v1.5"
    
    # ChromaDB 配置
    CHROMA_DB_PATH: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "product_documents"
    
    # GraphRAG 配置
    GRAPH_DB_PATH: str = "./graph_db"
    
    # 文档配置
    DATA_DIR: str = "./data"
    
    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """获取 API Key"""
        return cls.SILICONFLOW_API_KEY
    
    @classmethod
    def get_llm_config(cls) -> dict:
        """获取 LLM 配置"""
        return {
            "model": cls.LLM_MODEL,
            "api_key": cls.get_api_key(),
            "base_url": cls.SILICONFLOW_BASE_URL,
            "temperature": 0.7,
            "max_tokens": 2000
        }

# 系统配置
class SystemConfig:
    MAX_ENTITIES: int = 20
    MAX_CONTEXT_LENGTH: int = 4000
    SIMILARITY_THRESHOLD: float = 0.7
    RETRIEVE_TOP_K: int = 5