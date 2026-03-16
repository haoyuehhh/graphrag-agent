from typing import Dict, Any
from app.graph.builder import build_graph
from langgraph.checkpoint.memory import MemorySaver
import asyncio
from app.core.config import settings

class RAGService:
    def __init__(self):
        # 构建 Graph 并使用内存检查点
        self.graph = build_graph()
        self.checkpointer = MemorySaver()
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_requests)
    
    async def analyze(self, query: str, streaming: bool = False) -> Dict[str, Any]:
        """
        分析查询并返回结果
        """
        async with self.semaphore:
            config = {
                "configurable": {
                    "thread_id": str(hash(query))  # 使用查询的哈希作为线程ID
                }
            }
            
            if streaming:
                # 流式模式
                result = await self._stream_analysis(query, config)
            else:
                # 非流式模式
                result = await self.graph.ainvoke({"query": query}, config=config)
            
            return result
    
    async def _stream_analysis(self, query: str, config: Dict) -> Dict[str, Any]:
        """
        流式分析实现
        """
        full_answer = ""
        sources = []
        graph_path = []
        
        async for event in self.graph.astream_events({"query": query}, config=config, version="v2"):
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                full_answer += chunk.content
                yield {"type": "token", "content": chunk.content}
            elif event["event"] == "on_chain_end" and event["name"] == "retriever":
                # 获取检索结果
                retriever_output = event["data"]["output"]
                sources = retriever_output.get("sources", [])
                graph_path = retriever_output.get("graph_path", [])
            elif event["event"] == "on_chain_end" and event["name"] == "synthesizer":
                # 获取最终答案
                synthesizer_output = event["data"]["output"]
                full_answer = synthesizer_output.get("answer", "")
        
        yield {"type": "final", "state": {
            "answer": full_answer,
            "sources": sources,
            "graph_path": graph_path
        }}
        
        