from langgraph.graph import StateGraph
from app.graph.state import State
# 改为导入具体的函数，不是模块
from app.graph.nodes.planner import planner
from app.graph.nodes.retriever import retriever  # 或 whatever the function name is
from app.graph.nodes.synthesizer import synthesizer

def build_graph():
    workflow = StateGraph(State)
    
    # 添加节点 - 传入的是函数，不是模块
    workflow.add_node("planner", planner)
    workflow.add_node("retriever", retriever) 
    workflow.add_node("synthesizer", synthesizer) 
    
    # 设置入口和边（根据你原来的逻辑）
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "retriever")
    workflow.add_edge("retriever", "synthesizer")
    workflow.add_edge("synthesizer", "__end__")
    
    return workflow.compile()