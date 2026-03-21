from typing import List, Dict, Any, Optional
import chromadb
import logging
import hashlib
import copy
import os
import time

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, collection_name: str = "documents"):
        # 初始化 ChromaDB 客户端（持久化到磁盘，重启后数据不丢）
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(name=collection_name)
        logger.info(f"VectorStore initialized with collection: {collection_name}")
        
        # 竞品文档加载相关
        self.competitor_metadata = {}
        self.last_load_time = 0

    def _generate_deterministic_id(self, content: str) -> str:
        """基于内容生成确定性 ID（跨进程稳定）"""
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:12]
        return f"doc_{content_hash}"
    
    def _get_file_hash(self, file_path: str) -> str:
        """计算文件的哈希值用于检测文件是否修改"""
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
                return hashlib.md5(file_content).hexdigest()
        except Exception as e:
            logger.error(f"计算文件哈希失败 {file_path}: {e}")
            return ""

    def _should_load_file(self, file_path: str, file_hash: str) -> bool:
        """检查文件是否需要重新加载"""
        if file_path not in self.competitor_metadata:
            return True
        
        last_hash = self.competitor_metadata[file_path].get('hash')
        last_load = self.competitor_metadata[file_path].get('load_time', 0)
        
        # 如果文件哈希变化或超过1小时未加载，则重新加载
        return file_hash != last_hash or (time.time() - last_load) > 3600

    def load_competitor_documents(self, base_path: str = "data/competitors") -> List[Dict[str, Any]]:
        """
        加载竞品文档数据
        
        Args:
            base_path: 竞品数据基础路径
            
        Returns:
            List[Dict[str, Any]]: 加载的文档列表，每个文档包含内容、元数据和哈希信息
        """
        documents = []
        current_time = time.time()
        
        if not os.path.exists(base_path):
            logger.warning(f"竞品数据路径不存在: {base_path}")
            return documents
            
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    file_hash = self._get_file_hash(file_path)
                    
                    if self._should_load_file(file_path, file_hash):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            # 提取产品名称（从路径中获取）
                            rel_path = os.path.relpath(root, base_path)
                            product_name = rel_path.split(os.sep)[0] if rel_path != '.' else 'unknown'
                            
                            # 创建文档元数据
                            metadata = {
                                'source': file_path,
                                'product': product_name,
                                'file_type': 'competitor_analysis',
                                'category': os.path.basename(root),
                                'filename': file,
                                'load_time': current_time,
                                'hash': file_hash
                            }
                            
                            documents.append({
                                'content': content,
                                'metadata': metadata,
                                'file_hash': file_hash
                            })
                            
                            # 更新元数据记录
                            self.competitor_metadata[file_path] = {
                                'hash': file_hash,
                                'load_time': current_time
                            }
                            
                            logger.info(f"加载竞品文档: {file_path}")
                            
                        except Exception as e:
                            logger.error(f"加载文件失败 {file_path}: {e}")
                    else:
                        logger.debug(f"跳过未修改的文件: {file_path}")
        
        logger.info(f"总共加载 {len(documents)} 个竞品文档")
        return documents

    def get_competitor_metadata(self) -> Dict[str, Dict[str, Any]]:
        """获取竞品文档元数据"""
        return self.competitor_metadata

    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Add documents to the vector store with custom deterministic IDs."""
        if not documents:
            return []
        
        texts = []
        metadatas = []
        ids = []
        
        for doc in documents:
            # 深拷贝避免修改原始数据
            doc_copy = copy.deepcopy(doc)
            content = doc_copy["content"]
            
            # 生成确定性 ID
            doc_id = self._generate_deterministic_id(content)
            ids.append(doc_id)
            
            # 构建非空 metadata
            metadata = doc_copy.get("metadata", {}) or {}
            metadata.update({
                "source": "hybrid_rag",
                "doc_id": doc_id,
                "content_hash": hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
            })
            metadatas.append(metadata)
            texts.append(content)
        
        # 批量写入 ChromaDB
        try:
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Successfully added {len(ids)} documents")
            return ids
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            raise
    
    def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                include=["documents", "metadatas", "distances"]
            )
            
            retrieved_docs = []
            if results and results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    doc = {
                        "id": doc_id,
                        "content": results["documents"][0][i] if results["documents"] else "",
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results.get("distances") else None
                    }
                    retrieved_docs.append(doc)
            
            return retrieved_docs
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document by its custom ID."""
        try:
            results = self.collection.get(
                ids=[doc_id],
                include=["documents", "metadatas"]
            )
            
            if results and results["documents"] and len(results["documents"]) > 0:
                return {
                    "id": doc_id,
                    "content": results["documents"][0],
                    "metadata": results["metadatas"][0] if results["metadatas"] else {}
                }
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve document by ID {doc_id}: {str(e)}")
            return None
    
    def delete_collection(self):
        """清空整个集合（调试用）"""
        try:
            self.client.delete_collection(self.collection.name)
            logger.info(f"Deleted collection: {self.collection.name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")