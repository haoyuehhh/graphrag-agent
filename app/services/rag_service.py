from typing import Dict, Any, List
from app.services.vector_store import VectorStore
from app.graph.builder import GraphBuilder
from langgraph.checkpoint.memory import MemorySaver
import asyncio
from app.core.config import settings
from app.services.circuit_breaker import CircuitBreaker
from app.models.schemas import DocumentMapping

# 创建全局熔断器实例
breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

class RAGService:
    def __init__(self):
        # 初始化向量存储和图谱构建器
        self.vector_store = VectorStore()
        self.graph_builder = GraphBuilder()
        self.graph = self.graph_builder.build_graph([])  # 初始化空图谱
        
        # 构建 Graph 并使用内存检查点
        self.checkpointer = MemorySaver()
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_requests)
    
    def hybrid_retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Hybrid RAG 检索融合：向量检索 + 图谱检索 + 融合去重
        
        步骤：
        1. 向量检索 - 调用 ChromaDB 的 similarity_search，获取 top_k 个 doc_id 和分数
        2. 图谱检索 - 在 NetworkX 中查找与 query 关键词匹配的节点，获取 doc_id
        3. 融合去重 - 合并两个列表，使用 set 去重，保留前 top_k 个
        4. 通过统一 ID 获取完整文档内容
        """
        # 步骤1：向量检索
        vector_results = self.vector_store.similarity_search(query, k=top_k)
        vector_doc_ids = []
        if vector_results:
            vector_doc_ids = [result["metadata"]["doc_id"] for result in vector_results]
        
        # 步骤2：图谱检索（简单 substring 匹配）
        graph_doc_ids = self.graph_builder.search_nodes_by_keyword(query)
        
        # 步骤3：融合去重
        all_doc_ids = list(set(vector_doc_ids + graph_doc_ids))  # 去重
        all_doc_ids = all_doc_ids[:top_k]  # 保留前 top_k 个
        
        # 步骤4：通过统一 ID 获取完整文档内容
        retrieved_docs = []
        for doc_id in all_doc_ids:
            doc = self.vector_store.get_document_by_id(doc_id)
            if doc:
                # 标记来源
                if doc_id in vector_doc_ids:
                    doc["source"] = "vector"
                elif doc_id in graph_doc_ids:
                    doc["source"] = "graph"
                retrieved_docs.append(doc)
        
        return retrieved_docs
    
    async def _call_deepseek(self, query: str, streaming: bool = False) -> Dict[str, Any]:
        """调用主模型（deepseek）"""
        config = {
            "configurable": {
                "thread_id": str(hash(query))
            }
        }
        
        # 使用 hybrid_retrieve 替代纯向量检索
        retrieved_docs = self.hybrid_retrieve(query)
        
        if streaming:
            result = await self._stream_analysis(query, config, retrieved_docs)
        else:
            result = await self.graph.ainvoke({"query": query, "retrieved_docs": retrieved_docs}, config=config)
        
        return result

    async def _call_glm_flash(self, query: str) -> Dict[str, Any]:
        """调用备用模型（glm-flash）"""
        # 这里实现备用模型的调用逻辑
        # 简单模拟返回
        return {
            "answer": "备用模型返回的结果",
            "sources": [],
            "graph_path": []
        }

    async def analyze(self, query: str, streaming: bool = False) -> Dict[str, Any]:
        """
        分析查询并返回结果
        """
        async with self.semaphore:
            # 使用熔断器调用
            result = await breaker.call(
                self._call_deepseek,
                self._call_glm_flash,
                query,
                streaming=streaming
            )
            return result
    
    async def _stream_analysis(self, query: str, config: Dict, retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        流式分析实现
        """
        full_answer = ""
        sources = []
        graph_path = []
        
        async for event in self.graph.astream_events({"query": query, "retrieved_docs": retrieved_docs}, config=config, version="v2"):
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
            "graph_path": graph_path,
            "retrieved_docs": retrieved_docs
        }}
        
    def process_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process documents and build the knowledge graph with unified ID system."""
        results = {
            "vector_ids": [],
            "graph_nodes": 0,
            "graph_edges": 0,
            "mappings": []
        }
        
        # Process each document individually to maintain consistency
        for doc in documents:
            try:
                # Generate deterministic ID (same as ChromaDB)
                content = doc["content"]
                content_hash = hash(content)
                doc_id = f"doc_{content_hash % 100000}"
                
                # Add custom metadata for tracking
                if "metadata" not in doc:
                    doc["metadata"] = {}
                doc["metadata"].update({
                    "source": "hybrid_rag",
                    "doc_id": doc_id,
                    "content_hash": str(content_hash)
                })
                
                # Store document in vector database with custom ID
                vector_id = self.vector_store.add_documents([doc])[0]
                results["vector_ids"].append(vector_id)
                
                # Build knowledge graph with the same ID
                graph = self.graph_builder.build_graph([doc])
                results["graph_nodes"] = len(graph.nodes)
                results["graph_edges"] = len(graph.edges)
                
                # Create mapping record
                mapping = {
                    "doc_id": doc_id,
                    "vector_db_id": vector_id,
                    "graph_node_id": doc_id,  # Same as document ID
                    "content_hash": str(content_hash),
                    "content": content,
                    "metadata": doc.get("metadata", {})
                }
                results["mappings"].append(mapping)
                
            except Exception as e:
                logger.error(f"Failed to process document: {str(e)}")
                # In a real implementation, you might want to roll back previous operations
                raise
        
        return results
        