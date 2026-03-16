from typing import Dict, Any
from app.graph.state import GraphRAGState

async def planner(state: GraphRAGState) -> Dict[str, Any]:
    """
    Planner 节点：分析查询并规划检索策略
    """
    query = state["query"]
    
    # 这里保留原有的 Planner 逻辑
    # 例如：分析查询类型，确定需要检索的实体和关系
    planned_context = f"Planning for query: {query}"
    
    return {"context": planned_context}