# GraphRAG Multi-Agent 竞品分析系统

> 基于 LangGraph + FastAPI 的智能竞品情报分析 API，支持知识图谱增强检索与多 Agent 协作。

## 🚀 在线演示

- **健康检查**: http://120.26.140.131/health
- **API 文档**: http://120.26.140.131/docs (Swagger UI)
- **源码**: https://github.com/haoyuehhh/graphrag-agent

## ✨ 核心功能

- **Multi-Agent 架构**: Planner → Retriever → Synthesizer 三节点协作
- **GraphRAG 检索**: NetworkX 知识图谱 + ChromaDB 向量检索 Hybrid
- **流式响应**: Server-Sent Events 实时返回分析结果
- **熔断降级**: SiliconFlow API 故障自动切换备用策略

## 🏗️ 技术架构

\\\
User Query
    ↓
[FastAPI] → [Planner Agent] → [Retriever Agent] → [Synthesizer Agent]
                ↓                      ↓
         [ChromaDB] ←→ [NetworkX Graph]
                ↓
         [SiliconFlow LLM]
                ↓
        Streaming Response
\\\

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 框架 | FastAPI, Uvicorn, Gunicorn |
| AI/ML | LangGraph, LangChain, OpenAI API |
| 数据库 | ChromaDB (向量), NetworkX (图谱) |
| 部署 | Ubuntu, Nginx, Systemd |
| 监控 | 健康检查, 限流, 熔断 |

## 📦 快速开始

### 本地开发
\\\ash
# 1. 克隆
git clone https://github.com/haoyuehhh/graphrag-agent.git
cd graphrag-agent

# 2. 环境
python -m venv venv && venv\Scripts\activate
pip install -r requirements-prod.txt

# 3. 配置
cp .env.example .env
# 编辑 .env: SILICONFLOW_API_KEY=sk-xxxx

# 4. 启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
\\\

### 生产部署
\\\ash
# 服务器部署（Ubuntu）
sudo apt update && apt install -y python3-pip nginx
git clone https://github.com/haoyuehhh/graphrag-agent.git
cd graphrag-agent
python3 -m venv venv && source venv/bin/activate
pip install -r requirements-prod.txt

# 配置 systemd + nginx
sudo systemctl enable --now graphrag
\\\

## 🔌 API 端点

### 健康检查
\\\http
GET /health
\\\
\\\json
{
  "status": "healthy",
  "agents_ready": true
}
\\\

### 竞品分析（非流式）
\\\http
POST /api/v1/analyze
Content-Type: application/json

{
  "query": "分析竞品A和B的技术差异",
  "streaming": false
}
\\\

### 竞品分析（流式）
\\\http
POST /api/v1/analyze/stream
Content-Type: application/json

{
  "query": "分析竞品A和B的技术差异"
}
\\\

## 📝 项目结构

\\\
app/
├── api/              # API 路由层
├── core/             # 配置、事件、限流
├── graph/            # LangGraph 节点与状态
├── services/         # 业务逻辑（RAGService）
└── utils/            # 工具函数
deploy/               # 部署配置
\\\

## 🎯 面试亮点

- **架构设计**: Multi-Agent 协作解决单 Agent 上下文局限
- **工程化**: 完整的 FastAPI 生产级结构（配置分离、日志、限流）
- **部署运维**: 阿里云 ECS + Systemd + Nginx 完整链路
- **成本控制**: 2核2G 服务器优化配置（Swap、单 Worker）

## 📄 License

MIT © 2026 haoyuehhh
