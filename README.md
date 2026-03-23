

```markdown
# Tech Radar Agent

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-Protocol-8A2BE2)](https://modelcontextprotocol.io)

> 基于 **MCP (Model Context Protocol)** 协议的竞品情报分析系统  
> 针对知识管理赛道（Notion/Obsidian），实现"协议层-技能层-数据层"三层架构的 Multi-Agent 系统

🌐 **在线演示**: http://120.26.140.131:8000/api/v1/competitors/matrix/features

---

## 🎯 核心亮点

- **🔧 MCP 协议自研**: 参考 Anthropic 标准实现 `tools/list` 与 `tools/call` 接口，解耦 Agent 与工具实现，比 LangChain Tool 更具扩展性
- **🧩 Skill 插件系统**: 热插拔架构，BrowserSkill 封装浏览器自动化，支持 **Playwright/Mock 降级模式**（无环境时自动切换 Mock 数据）
- **🕸️ GraphRAG 分析**: LangGraph 编排 Planner/Retriever/Analyzer 三节点，构建竞品关系图谱，支持"本地优先的 Notion 替代品"复杂查询
- **🚀 生产级部署**: FastAPI 异步架构，Docker 镜像仅 1.2G，阿里云 ECS 限流部署，稳定 700 QPS（继承实习优化经验）

---

## 🏗️ 系统架构

**三层架构设计**:

**1. API Layer (FastAPI)**
- RESTful API 接口层
- 端点: `/competitors/compare`, `/competitors/matrix/features`, `/skills`
- 异步处理，Pydantic 数据校验

**2. Skill System (技能系统)**
- **BrowserSkill**: 浏览器自动化（Playwright），支持降级 Mock 模式
- **Skill Registry**: 热插拔注册中心，动态发现与管理
- 新增分析维度只需注册新 Skill，无需修改核心代码

**3. MCP Protocol Layer (协议层)**
- **MCP Server**: 实现 `tools/list` 和 `tools/call` 标准接口
- **MCP Client**: 标准化工具调用客户端
- JSON-RPC 2.0 消息格式，跨语言兼容

**4. Data Layer (数据层)**
- **GraphRAG**: NetworkX 构建竞品关系图谱（Notion ←竞品→ Obsidian）
- **ChromaDB**: 向量数据库存储文档 Embedding
- 混合检索: 向量相似度 + 图关系遍历

---

## 🚀 快速开始

### 环境准备

```bash
# 克隆项目
git clone https://github.com/haoyuehhh/graphrag-agent.git
cd graphrag-agent

# 安装依赖
pip install -r requirements.txt

# 可选：安装 Playwright（完整爬虫功能）
pip install playwright
playwright install chromium
```

### 启动服务

```bash
# 本地开发
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产部署（阿里云）
docker build -t tech-radar .
docker run -d -p 8000:8000 tech-radar
```

### 验证安装

```bash
# 测试健康检查
curl http://localhost:8000/api/v1/health/health

# 测试竞品矩阵（核心功能）
curl http://localhost:8000/api/v1/competitors/matrix/features
```

---

## 📡 API 文档

### 竞品分析端点

| 端点                                  | 方法 | 描述             | 示例响应                               |
| ------------------------------------- | ---- | ---------------- | -------------------------------------- |
| `/api/v1/competitors/matrix/features` | GET  | 获取功能对标矩阵 | `{"Notion": {...}, "Obsidian": {...}}` |
| `/api/v1/competitors/compare`         | POST | 对比指定竞品     | 传入 `competitor_names` 和 `dimension` |
| `/api/v1/competitors/{name}/profile`  | GET  | 获取单个竞品画像 | 返回画像详情                           |

**POST /compare 请求示例**:
```json
{
  "competitor_names": ["Notion", "Obsidian"],
  "dimension": "pricing"
}
```

### Skill 管理端点

| 端点             | 方法 | 描述                  |
| ---------------- | ---- | --------------------- |
| `/api/v1/skills` | GET  | 列出所有已注册 Skills |

---

## 🛠️ 技术栈

| 层级         | 技术                       | 选型理由                             |
| ------------ | -------------------------- | ------------------------------------ |
| **协议层**   | MCP Protocol, JSON-RPC 2.0 | 标准化工具调用，解耦实现，支持跨语言 |
| **API 层**   | FastAPI, Pydantic          | 异步高性能，自动生成文档，类型安全   |
| **Agent 层** | LangGraph, StateGraph      | 复杂工作流编排，支持循环、条件、并行 |
| **存储层**   | ChromaDB, NetworkX         | 向量检索 + 图关系分析双引擎          |
| **采集层**   | Playwright (Optional)      | 浏览器自动化，支持 SPA 动态内容      |
| **部署**     | Docker, Gunicorn, 阿里云   | 容器化，限流，生产级稳定             |

---

## 💡 面试要点（技术深挖准备）

### 1. 协议层设计
**Q: 为什么自研 MCP 而不是用 LangChain Tool？**  
**A**: LangChain Tool 是框架锁定（只能 LangChain 用），MCP 是开放协议。我实现的 MCP Server 遵循 Anthropic 标准，任何支持 MCP 的 Client（Claude Desktop、其他语言 Agent）都能调用，真正实现工具的标准化复用。

### 2. 工程健壮性
**Q: 如果竞品网站改版或爬虫失败怎么办？**  
**A**: Skill 层设计了**降级策略**。BrowserSkill 初始化时检测 Playwright 环境，不存在时自动切换 Mock 模式，返回模拟数据并标记 `status: "mock_mode"`，确保服务可用性，而非直接崩溃。

### 3. 架构扩展性
**Q: 如何新增一个赛道（如 AI 编程工具）？**  
**A**: 三步：① 在 `data/` 添加新竞品 Markdown 文档（冷启动）；② 注册新 Skill（如 `CodeAnalysisSkill`）到 Skill Registry；③ 无需修改核心代码，API 自动暴露新能力。符合开闭原则。

### 4. 性能优化
**Q: 长任务（爬虫 5-10 秒）如何处理？**  
**A**:  FastAPI 异步接口接收请求，实际分析任务提交 Celery 异步队列（继承实习经验），支持后台执行 + 状态轮询，避免 API 超时。

---

## 📝 数据说明

**当前覆盖赛道**: 知识管理工具  
- **Notion**: All-in-one，Database 强，云端协作  
- **Obsidian**: 本地优先，双向链接，插件生态  
- **Logseq**: 开源大纲，PDF 标注  

**可扩展至**: AI 编程工具（Cursor/Windsurf）、低代码平台等。

---

## 📄 License

MIT License - 用于学习和面试展示

---
**🌟 项目状态**: 核心功能已完成，LangSmith 可观测性、前端 Dashboard 开发中

```

```