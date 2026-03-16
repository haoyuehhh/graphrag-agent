from typing import TypedDict, List, Dict, Optional, Any
from langchain_core.runnables import RunnableConfig

class State(TypedDict):
    """LangGraph State 定义"""
    query: str                    # 用户查询
    context: List[str]            # 检索到的上下文
    sources: List[dict]           # 来源信息
    graph_path: List[str]         # 图谱路径
    answer: Optional[str]         # 最终答案
    streaming: Optional[bool]     # 是否流式

GraphRAGState = State