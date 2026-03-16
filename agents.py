"""
智能代理：Planner / Retriever / Synthesizer 三个 Agent
"""
import json
import re
from typing import Dict, List, Optional, Any, TypedDict
from dataclasses import dataclass
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from config import APIConfig, SystemConfig
from graph_store import GraphStore, Entity, Relation
from retriever import ChromaRetriever, DocumentChunk, SearchResult

# State 定义
class AgentState(TypedDict):
    """Agent 状态"""
    query: str
    context: str
    answer: str
    entities: List[Dict[str, Any]]
    plan: Optional[Dict[str, Any]]
    retrieved_docs: List[DocumentChunk]
    graph_context: Optional[str]

@dataclass
class PlannerAgent:
    """规划 Agent：负责分析查询并制定检索计划"""
    
    def __init__(self):
        self.llm = self._get_llm()
        self.prompt = self._get_planner_prompt()
    
    def _get_llm(self):
        """获取 LLM 实例"""
        return ChatOpenAI(
            model=APIConfig.LLM_MODEL,
            api_key=APIConfig.get_api_key(),
            base_url=APIConfig.SILICONFLOW_BASE_URL,
            temperature=0.3
        )
    
    def _get_planner_prompt(self):
        """获取规划提示词"""
        return ChatPromptTemplate.from_messages([
            ("system", """你是一个智能查询规划助手。你的任务是分析用户查询，识别关键实体，并制定检索计划。

分析要求：
1. 识别查询中的关键实体（产品、功能、价格等）
2. 确定查询意图（比较、查询、分析等）
3. 制定检索策略（知识图谱检索、文档检索、混合检索）
4. 输出结构化的检索计划

输出格式：
{
    "entities": [
        {
            "name": "实体名称",
            "type": "实体类型",
            "description": "实体描述"
        }
    ],
    "intent": "查询意图",
    "strategy": "检索策略",
    "keywords": ["关键词1", "关键词2"]
}"""),
            ("user", "用户查询：{query}")
        ])
    
    def plan(self, query: str) -> Dict[str, Any]:
        """制定检索计划"""
        try:
            chain = self.prompt | self.llm | JsonOutputParser()
            result = chain.invoke({"query": query})
            
            # 确保输出格式正确
            if "entities" not in result:
                result["entities"] = []
            if "intent" not in result:
                result["intent"] = "unknown"
            if "strategy" not in result:
                result["strategy"] = "hybrid"
            if "keywords" not in result:
                result["keywords"] = []
            
            return result
            
        except Exception as e:
            print(f"规划失败: {e}")
            return {
                "entities": [],
                "intent": "unknown",
                "strategy": "hybrid",
                "keywords": []
            }

@dataclass
class RetrieverAgent:
    """检索 Agent：负责从知识图谱和文档库中检索信息"""
    
    def __init__(self):
        self.graph_store = GraphStore(APIConfig.GRAPH_DB_PATH)
        self.vector_retriever = ChromaRetriever()
        self.llm = self._get_llm()
    
    def _get_llm(self):
        """获取 LLM 实例"""
        return ChatOpenAI(
            model=APIConfig.LLM_MODEL,
            api_key=APIConfig.get_api_key(),
            base_url=APIConfig.SILICONFLOW_BASE_URL,
            temperature=0.3
        )
    
    def retrieve(self, query: str, plan: Dict[str, Any]) -> Dict[str, Any]:
        """执行检索"""
        try:
            # 1. 知识图谱检索
            graph_results = self._retrieve_from_graph(query, plan)
            
            # 2. 文档检索
            doc_results = self._retrieve_from_docs(query, plan)
            
            # 3. 合并结果
            combined_results = self._combine_results(graph_results, doc_results)
            
            return {
                "graph_context": graph_results,
                "retrieved_docs": doc_results,
                "combined_context": combined_results
            }
            
        except Exception as e:
            print(f"检索失败: {e}")
            return {
                "graph_context": "",
                "retrieved_docs": [],
                "combined_context": ""
            }
    
    def _retrieve_from_graph(self, query: str, plan: Dict[str, Any]) -> str:
        """从知识图谱检索"""
        try:
            context_parts = []
            
            # 根据计划中的实体进行检索
            for entity_info in plan.get("entities", []):
                entity_name = entity_info.get("name", "")
                if entity_name:
                    # 搜索实体
                    entities = self.graph_store.search_entities(entity_name)
                    if entities:
                        entity = entities[0]  # 取最匹配的实体
                        context_parts.append(f"实体：{entity.name}")
                        context_parts.append(f"类型：{entity.type}")
                        context_parts.append(f"描述：{entity.description or '无'}")
                        context_parts.append(f"属性：{json.dumps(entity.attributes, ensure_ascii=False)}")
                        
                        # 获取相关实体
                        related = self.graph_store.find_related_entities(entity.id, depth=1)
                        if related:
                            context_parts.append("相关实体：")
                            for item in related[:5]:  # 限制数量
                                context_parts.append(f"- {item['entity'].name} ({item['relation_type']})")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            print(f"知识图谱检索失败: {e}")
            return ""
    
    def _retrieve_from_docs(self, query: str, plan: Dict[str, Any]) -> List[DocumentChunk]:
        """从文档库检索"""
        try:
            # 使用混合搜索
            search_results = self.vector_retriever.hybrid_search(query, SystemConfig.RETRIEVE_TOP_K)
            
            # 转换为 DocumentChunk
            doc_chunks = []
            for result in search_results:
                doc_chunks.append(result.chunk)
            
            return doc_chunks
            
        except Exception as e:
            print(f"文档检索失败: {e}")
            return []
    
    def _combine_results(self, graph_context: str, doc_chunks: List[DocumentChunk]) -> str:
        """合并检索结果"""
        try:
            combined_parts = []
            
            # 添加知识图谱信息
            if graph_context:
                combined_parts.append("=== 知识图谱信息 ===")
                combined_parts.append(graph_context)
                combined_parts.append("\n")
            
            # 添加文档信息
            if doc_chunks:
                combined_parts.append("=== 文档信息 ===")
                for i, chunk in enumerate(doc_chunks[:5]):  # 限制数量
                    combined_parts.append(f"文档 {i+1}：")
                    combined_parts.append(f"来源：{chunk.source}")
                    combined_parts.append(f"内容：{chunk.content}")
                    combined_parts.append("")
            
            return "\n".join(combined_parts)
            
        except Exception as e:
            print(f"合并结果失败: {e}")
            return ""

@dataclass
class SynthesizerAgent:
    """合成 Agent：负责基于检索结果生成最终答案"""
    
    def __init__(self):
        self.llm = self._get_llm()
        self.prompt = self._get_synthesizer_prompt()
    
    def _get_llm(self):
        """获取 LLM 实例"""
        return ChatOpenAI(
            model=APIConfig.LLM_MODEL,
            api_key=APIConfig.get_api_key(),
            base_url=APIConfig.SILICONFLOW_BASE_URL,
            temperature=0.7
        )
    
    def _get_synthesizer_prompt(self):
        """获取合成提示词"""
        return ChatPromptTemplate.from_messages([
            ("system", """你是一个智能答案合成助手。你的任务是基于检索到的信息，为用户查询生成准确、完整的答案。

合成要求：
1. 综合知识图谱和文档信息
2. 确保答案准确性和完整性
3. 保持回答结构清晰
4. 如果信息不足，明确说明

回答格式：
{
    "answer": "详细回答内容",
    "sources": ["信息来源1", "信息来源2"],
    "confidence": "高/中/低",
    "key_entities": ["实体1", "实体2"]
}"""),
            ("user", """用户查询：{query}

检索到的信息：
{context}

请生成答案。""")
        ])
    
    def synthesize(self, query: str, context: str) -> Dict[str, Any]:
        """合成答案"""
        try:
            chain = self.prompt | self.llm | JsonOutputParser()
            result = chain.invoke({"query": query, "context": context})
            
            # 确保输出格式正确
            if "answer" not in result:
                result["answer"] = "无法生成答案"
            if "sources" not in result:
                result["sources"] = []
            if "confidence" not in result:
                result["confidence"] = "中"
            if "key_entities" not in result:
                result["key_entities"] = []
            
            return result
            
        except Exception as e:
            print(f"合成失败: {e}")
            return {
                "answer": "生成答案时出现错误",
                "sources": [],
                "confidence": "低",
                "key_entities": []
            }

# Agent 工厂类
class AgentFactory:
    """Agent 工厂"""
    
    @staticmethod
    def create_planner() -> PlannerAgent:
        """创建规划 Agent"""
        return PlannerAgent()
    
    @staticmethod
    def create_retriever() -> RetrieverAgent:
        """创建检索 Agent"""
        return RetrieverAgent()
    
    @staticmethod
    def create_synthesizer() -> SynthesizerAgent:
        """创建合成 Agent"""
        return SynthesizerAgent()