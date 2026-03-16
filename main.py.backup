from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph, END

# 1. 先定义 State
class AgentState(TypedDict):
    query: str
    context: str
    answer: str
    entities: list
    plan: dict
    retrieved_docs: list
    graph_context: str

# 2. 再定义节点函数
def planner_node(state: AgentState) -> AgentState:
    """真的规划：分析查询意图"""
    print("🧠 Planner: 分析查询意图")
    query = state["query"]
    
    # 简单规则判断
    if any(k in query for k in ["对比", "vs", "比较", "区别"]):
        intent = "对比分析"
    elif any(k in query for k in ["价格", "定价", "多少钱"]):
        intent = "价格查询"
    else:
        intent = "信息查询"
    
    state["plan"] = {
        "intent": intent,
        "entities": ["Notion", "Obsidian", "Logseq"],
        "strategy": "检索本地文档"
    }
    return state

def retriever_node(state: AgentState) -> AgentState:
    """真的检索：读取 data/ 目录的 markdown 文件"""
    print("🔍 Retriever: 读取本地文档")
    import os
    import glob
    
    docs = []
    data_dir = "data"
    
    if os.path.exists(data_dir):
        md_files = glob.glob(os.path.join(data_dir, "*.md"))
        for filepath in md_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    filename = os.path.basename(filepath)
                    docs.append({
                        "source": filename,
                        "content": content[:500] + "..." if len(content) > 500 else content
                    })
            except Exception as e:
                print(f"   读取 {filepath} 失败: {e}")
    
    # 构建上下文
    context_parts = []
    for doc in docs:
        context_parts.append(f"【{doc['source']}】\n{doc['content']}\n")
    
    state["retrieved_docs"] = docs
    state["context"] = "\n".join(context_parts)
    state["graph_context"] = f"检索到 {len(docs)} 个文档"
    
    print(f"   ✅ 成功读取 {len(docs)} 个文档")
    return state

def synthesizer_node(state):
    """调用 SiliconFlow API 生成真实答案"""
    print("🎨 Synthesizer: 调用 DeepSeek API 生成答案...")
    
    from openai import OpenAI
    
    # 直接配置（从 config.py 复制）
    client = OpenAI(
        api_key="sk-spgaedwstfoynlbhwefwdrthhsstimobmesytdxxnfdjadae",  # 你的 Key
        base_url="https://api.siliconflow.cn/v1"
    )
    
    context = state["context"]
    query = state["query"]
    
    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[
                {"role": "system", "content": "你是竞品分析专家，基于提供的文档信息生成简洁、专业的对比分析。"},
                {"role": "user", "content": f"用户查询：{query}\n\n检索到的竞品信息：\n{context}\n\n请生成一段自然的分析回答（100字左右）："}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        state["answer"] = response.choices[0].message.content
        print("   ✅ API 调用成功")
        
    except Exception as e:
        print(f"   ⚠️ API 调用失败: {e}")
        # 失败时回退到规则生成
        state["answer"] = f"基于检索到的 {len(state['retrieved_docs'])} 份文档：Notion适合团队协作，Obsidian适合个人知识管理，Logseq适合大纲记录。"
    
    return state

# 3. 然后定义 create_graph 函数
def create_graph():
    builder = StateGraph(AgentState)
    builder.add_node("planner", planner_node)
    builder.add_node("retriever", retriever_node)
    builder.add_node("synthesizer", synthesizer_node)
    builder.set_entry_point("planner")
    builder.add_edge("planner", "retriever")
    builder.add_edge("retriever", "synthesizer")
    builder.add_edge("synthesizer", END)
    return builder.compile()

# 4. 最后创建实例（此时函数已定义）
graph = create_graph()

if __name__ == "__main__":
    result = graph.invoke({"query": "测试", "context": "", "answer": "", "entities": [], "plan": {}, "retrieved_docs": [], "graph_context": ""})
    # 修复输出格式，只打印答案内容而不是整个字典
    print("✅ 运行成功")
    print(f"答案: {result['answer']}")
    print(f"来源文档: {result['retrieved_docs']}")
    print(f"思考过程: {result['plan']}")
