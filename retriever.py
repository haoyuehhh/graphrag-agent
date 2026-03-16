"""
向量检索器：ChromaDB 向量检索 + Hybrid RAG
"""
import os
import re
from typing import List, Dict, Optional, Tuple, Any
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
import numpy as np
from dataclasses import dataclass
from config import APIConfig, SystemConfig

@dataclass
class DocumentChunk:
    """文档片段类"""
    id: str
    content: str
    metadata: Dict[str, Any]
    source: str
    chunk_index: int

@dataclass
class SearchResult:
    """搜索结果类"""
    chunk: DocumentChunk
    similarity: float
    rank: int

class ChromaRetriever:
    """ChromaDB 向量检索器"""
    
    def __init__(self, 
                 db_path: str = APIConfig.CHROMA_DB_PATH,
                 collection_name: str = APIConfig.CHROMA_COLLECTION_NAME,
                 embedding_model: str = "all-MiniLM-L6-v2"):
        self.db_path = db_path
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.client = None
        self.collection = None
        self.embedder = None
        self._initialize_retriever()
    
    def _initialize_retriever(self):
        """初始化检索器"""
        try:
            # 初始化 ChromaDB 客户端
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # 获取或创建集合
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Product documents for RAG"}
            )
            
            # 初始化嵌入模型
            self.embedder = OpenAIEmbeddings(
                model=APIConfig.EMBEDDING_MODEL,
                openai_api_key=APIConfig.get_api_key(),
                openai_api_base=APIConfig.SILICONFLOW_BASE_URL
            )
            print(f"检索器初始化成功，使用模型: {APIConfig.EMBEDDING_MODEL}")
            
        except Exception as e:
            print(f"检索器初始化失败: {e}")
            raise
    
    def add_documents(self, documents: List[DocumentChunk]):
        """添加文档到 ChromaDB"""
        try:
            if not documents:
                print("没有文档可添加")
                return
            
            # 准备数据
            ids = [doc.id for doc in documents]
            contents = [doc.content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            # 生成嵌入
            embeddings = self.embedder.encode(contents).tolist()
            
            # 添加到 ChromaDB
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas
            )
            
            print(f"成功添加 {len(documents)} 个文档片段")
            
        except Exception as e:
            print(f"添加文档失败: {e}")
            raise
    
    def search(self, query: str, top_k: int = SystemConfig.RETRIEVE_TOP_K) -> List[SearchResult]:
        """向量搜索"""
        try:
            # 生成查询嵌入
            query_embedding = self.embedder.encode([query]).tolist()
            
            # 执行搜索
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # 处理结果
            search_results = []
            for i, (doc_id, content, metadata, distance) in enumerate(zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                # 将距离转换为相似度（余弦相似度）
                similarity = 1 - distance
                
                # 过滤低相似度结果
                if similarity < SystemConfig.SIMILARITY_THRESHOLD:
                    continue
                
                chunk = DocumentChunk(
                    id=doc_id,
                    content=content,
                    metadata=metadata or {},
                    source=metadata.get("source", "unknown"),
                    chunk_index=metadata.get("chunk_index", 0)
                )
                
                search_results.append(SearchResult(
                    chunk=chunk,
                    similarity=similarity,
                    rank=i + 1
                ))
            
            return search_results
            
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def hybrid_search(self, query: str, top_k: int = SystemConfig.RETRIEVE_TOP_K) -> List[SearchResult]:
        """混合搜索：向量搜索 + 关键词匹配"""
        try:
            # 1. 向量搜索
            vector_results = self.search(query, top_k * 2)  # 获取更多结果用于混合
            
            # 2. 关键词匹配
            keyword_results = self._keyword_search(query, top_k)
            
            # 3. 合并和重排序
            combined_results = self._combine_and_rerank(vector_results, keyword_results, top_k)
            
            return combined_results
            
        except Exception as e:
            print(f"混合搜索失败: {e}")
            return []
    
    def _keyword_search(self, query: str, top_k: int) -> List[SearchResult]:
        """关键词搜索"""
        try:
            # 获取所有文档
            all_docs = self.collection.get(include=["documents", "metadatas"])
            
            results = []
            query_lower = query.lower()
            
            # 简单的关键词匹配
            for i, (doc_id, content, metadata) in enumerate(zip(
                all_docs["ids"],
                all_docs["documents"],
                all_docs["metadatas"]
            )):
                # 计算关键词匹配度
                query_words = set(re.findall(r'\w+', query_lower))
                content_words = set(re.findall(r'\w+', content.lower()))
                
                if query_words:
                    match_ratio = len(query_words.intersection(content_words)) / len(query_words)
                    
                    if match_ratio > 0.1:  # 至少匹配10%的关键词
                        chunk = DocumentChunk(
                            id=doc_id,
                            content=content,
                            metadata=metadata or {},
                            source=metadata.get("source", "unknown"),
                            chunk_index=metadata.get("chunk_index", 0)
                        )
                        
                        results.append(SearchResult(
                            chunk=chunk,
                            similarity=match_ratio,
                            rank=len(results) + 1
                        ))
            
            # 按相似度排序并返回前 top_k 个结果
            results.sort(key=lambda x: x.similarity, reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"关键词搜索失败: {e}")
            return []
    
    def _combine_and_rerank(self, 
                           vector_results: List[SearchResult], 
                           keyword_results: List[SearchResult],
                           top_k: int) -> List[SearchResult]:
        """合并和重排序搜索结果"""
        try:
            # 创建结果字典，避免重复
            result_dict = {}
            
            # 添加向量搜索结果
            for result in vector_results:
                result_dict[result.chunk.id] = result
            
            # 添加关键词搜索结果（如果不存在）
            for result in keyword_results:
                if result.chunk.id not in result_dict:
                    result_dict[result.chunk.id] = result
            
            # 混合评分：向量相似度 70% + 关键词匹配度 30%
            for result in result_dict.values():
                if hasattr(result, 'vector_similarity'):
                    # 如果是向量搜索结果
                    final_score = result.vector_similarity * 0.7
                else:
                    # 如果是关键词搜索结果
                    final_score = result.similarity * 0.3
                
                # 如果结果同时来自两种搜索，取最高分
                if hasattr(result, 'final_score'):
                    result.final_score = max(result.final_score, final_score)
                else:
                    result.final_score = final_score
            
            # 按混合分数排序
            sorted_results = sorted(result_dict.values(), key=lambda x: x.final_score, reverse=True)
            
            # 重新分配排名
            for i, result in enumerate(sorted_results):
                result.rank = i + 1
            
            return sorted_results[:top_k]
            
        except Exception as e:
            print(f"合并重排序失败: {e}")
            return vector_results[:top_k]
    
    def get_document_by_id(self, doc_id: str) -> Optional[DocumentChunk]:
        """根据 ID 获取文档"""
        try:
            result = self.collection.get(ids=[doc_id], include=["documents", "metadatas"])
            
            if result["ids"]:
                return DocumentChunk(
                    id=result["ids"][0],
                    content=result["documents"][0],
                    metadata=result["metadatas"][0] or {},
                    source=result["metadatas"][0].get("source", "unknown"),
                    chunk_index=result["metadatas"][0].get("chunk_index", 0)
                )
            return None
            
        except Exception as e:
            print(f"获取文档失败: {e}")
            return None
    
    def delete_document(self, doc_id: str):
        """删除文档"""
        try:
            self.collection.delete(ids=[doc_id])
            print(f"文档 {doc_id} 已删除")
        except Exception as e:
            print(f"删除文档失败: {e}")
    
    def get_collection_stats(self) -> Dict:
        """获取集合统计信息"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "db_path": self.db_path
            }
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {}
    
    def clear_collection(self):
        """清空集合"""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(self.collection_name)
            print("集合已清空")
        except Exception as e:
            print(f"清空集合失败: {e}")