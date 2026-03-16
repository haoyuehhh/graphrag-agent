from typing import Dict, Any
from app.graph.state import GraphRAGState
from langchain_openai import ChatOpenAI
from app.core.config import settings
from langchain_core.prompts import ChatPromptTemplate
from app.services.circuit_breaker import circuit_breaker
from app.core.exceptions import LLMTimeoutException

async def synthesizer(state: GraphRAGState) -> Dict[str, Any]:
    """
    Synthesizer 节点：使用 LLM 生成最终答案
    """
    context = state["context"]
    query = state["query"]
    
    # 使用熔断器包装 LLM 调用
    @circuit_breaker
    async def generate_answer():
        # 初始化 SiliconFlow LLM
        llm = ChatOpenAI(
        base_url=settings.siliconflow_base_url,
        api_key=settings.siliconflow_api_key,
        model=settings.llm_model,
        temperature=0.7,
        max_tokens=2048
    )
        
        # 创建提示模板
        prompt = ChatPromptTemplate.from_template(
            "基于以下上下文回答问题：\n\n"
            "上下文：{context}\n\n"
            "问题：{query}\n\n"
            "请提供详细、准确的答案："
        )
        
        # 生成回答
        response = await llm.ainvoke(prompt.format(context=context, query=query))
        return response.content
    
    try:
        answer = await generate_answer()
        return {"answer": answer}
    except Exception as e:
        raise LLMTimeoutException(f"LLM 生成答案失败: {str(e)}")