# GraphRAG Multi-Agent 竞品分析系统

> 基于 **MCP (Model Context Protocol)** + LangGraph + FastAPI 的智能竞品情报分析 API  
> 支持知识图谱增强检索、多 Agent 协作与标准化工具协议。

## 在线演示

- **健康检查**: http://120.26.140.131/health  
- **API 文档**: http://120.26.140.131/docs (Swagger UI)
- **竞品矩阵**: http://120.26.140.131/api/v1/competitors/matrix/features
- **源码**: https://github.com/haoyuehhh/graphrag-agent  

## 核心亮点

- **🔧 MCP 协议层**: 自研 `tools/list` 与 `tools/call` 接口，解耦 Agent 与工具实现（对比 LangChain Tool 的框架锁定）
- **🧩 Skill 插件系统**: BrowserSkill 支持 **Playwright 实机 / Mock 降级** 双模式，无环境时自动切换确保可用性
- **🕸️ GraphRAG 检索**: NetworkX 知识图谱 + ChromaDB 向量 Hybrid 检索
- **🚀 Multi-Agent 编排**: Planner → Retriever → Synthesizer 三节点协作，支持流式响应
- **⚡ 生产级健壮性**: 熔断降级（SiliconFlow API 故障自动切换）、限流、Systemd 守护

## 技术架构

```
User Query
    ↓
[FastAPI] → [Planner Agent] → [MCP Client] → [BrowserSkill/Other Skills]
                ↓
        [Retriever Agent] → [ChromaDB] ↔ [NetworkX Graph]
                ↓
        [Synthesizer Agent] → [SiliconFlow LLM]
                ↓
        Streaming Response / Structured JSON
```

**协议层设计**: MCP Server 作为标准化工具网关，支持热插拔 Skill 注册，新增竞品维度无需修改核心代码。

## 🛠️ 技术栈

| 层级 | 技术 | 选型理由 |
|------|------|----------|
| **协议层** | MCP Protocol, JSON-RPC 2.0 | 标准化工具调用，跨语言兼容，解耦实现 |
| **框架** | FastAPI, Uvicorn, Gunicorn | 异步高性能，自动生成文档 |
| **AI/ML** | LangGraph, LangChain | 复杂工作流编排，支持循环与条件分支 |
| **数据库** | ChromaDB (向量), NetworkX (图谱) | Hybrid RAG：语义相似度 + 图关系遍历 |
| **部署** | Ubuntu, Nginx, Systemd | 生产级守护进程，故障自恢复 |
| **监控** | 健康检查, 限流, 熔断 | 2核2G 服务器优化配置 |

## 快速开始

### 本地开发

```bash
# 1. 克隆
git clone https://github.com/haoyuehhh/graphrag-agent.git  
cd graphrag-agent

# 2. 环境
python -m venv venv && source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

pip install -r requirements-prod.txt

# 3. 配置
cp .env.example .env
# 编辑 .env: SILICONFLOW_API_KEY=sk-xxxx

# 4. 启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 生产部署

```bash
# 服务器部署（Ubuntu）
sudo apt update && apt install -y python3-pip nginx
git clone https://github.com/haoyuehhh/graphrag-agent.git 
cd graphrag-agent
python3 -m venv venv && source venv/bin/activate
pip install -r requirements-prod.txt

# 配置 systemd + nginx
sudo cp deploy/graphrag.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now graphrag
```

## 🔌 API 端点

### 健康检查

```http
GET /health
```

**响应**:

```json
{
  "status": "healthy",
  "agents_ready": true,
  "mcp_server_ready": true
}
```

### 竞品分析（非流式）

```http
POST /api/v1/analyze
Content-Type: application/json

{
  "query": "分析 Notion 与 Obsidian 的技术差异",
  "streaming": false
}
```

### 竞品分析（流式）

```http
POST /api/v1/analyze/stream
Content-Type: application/json

{
  "query": "分析 Notion 与 Obsidian 的技术差异"
}
```

### Skill 注册查询（MCP协议）

```http
GET /api/v1/skills
```

**响应**: 返回已注册 Skills 列表及运行模式（实机/Mock）

## 项目结构

```
app/
├── api/              # API 路由层 (FastAPI)
├── core/             # 配置、事件、限流、MCP协议实现
├── skills/           # Skill插件目录 (BrowserSkill等)
├── graph/            # LangGraph 节点与状态定义
├── services/         # 业务逻辑（RAGService, MCPClient）
└── utils/            # 工具函数
deploy/               # 部署配置 (systemd, nginx)
```

## 常见问题 (FAQ)

**Q: 为什么自研MCP协议而不是直接用 LangChain Tool？**  
A: LangChain Tool 是框架锁定（只能 LangChain 用），MCP 是开放协议。我实现的 MCP Server 遵循 Anthropic 标准，任何支持 MCP 的 Client 都能调用，真正实现工具的标准化复用，且支持 Skill 热插拔。

**Q: 如果竞品网站改版或爬虫失败怎么办？**  
A: Skill 层设计了**降级策略**。BrowserSkill 初始化时检测 Playwright 环境，不存在时自动切换 Mock 模式，返回模拟数据并标记 `status: "mock_mode"`，确保服务可用性而非直接崩溃。

**Q: 如何新增一个分析维度？**  
A: 三步：① 继承 BaseSkill 实现新 Skill；② 注册到 SkillRegistry；③ 无需修改 Planner 核心代码，API 自动暴露新能力。符合开闭原则。

## 📄 License

MIT © 2026 haoyuehhh