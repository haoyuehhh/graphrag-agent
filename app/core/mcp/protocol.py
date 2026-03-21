"""
MCP协议定义：基础消息类型和工具定义
"""
from typing import List, Optional, Callable, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, Json
from dataclasses import dataclass

class MCPMethod(str, Enum):
    """MCP方法枚举"""
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"

class MCPMessage(BaseModel):
    """MCP基础消息结构"""
    jsonrpc: str = "2.0"
    id: str
    method: MCPMethod
    params: Optional[Dict[str, Any]] = None

class ToolCall(BaseModel):
    """工具调用请求"""
    name: str
    arguments: Dict[str, Any]

class ToolResult(BaseModel):
    """工具调用结果"""
    content: str
    is_error: bool = False
    error_message: Optional[str] = None

class ToolDefinition(BaseModel):
    """工具定义"""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

class ToolListResponse(BaseModel):
    """工具列表响应"""
    tools: List[ToolDefinition]