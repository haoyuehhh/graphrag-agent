from typing import Dict

def route_planner_to_retriever(state: Dict) -> str:
    """从 Planner 节点路由到 Retriever 节点"""
    return "retriever"

def route_retriever_to_synthesizer(state: Dict) -> str:
    """从 Retriever 节点路由到 Synthesizer 节点"""
    return "synthesizer"