from pydantic import BaseModel
from typing import Optional

class DocumentMapping(BaseModel):
    """文档映射关系表，用于关联 ChromaDB 和 NetworkX 的 ID"""
    doc_id: str
    vector_db_id: str  # ChromaDB 中的 ID
    graph_node_id: str  # NetworkX 图谱中的节点 ID
    content_hash: str
    content: Optional[str] = None
    metadata: Optional[dict] = None