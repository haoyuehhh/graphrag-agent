from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict, List
from app.core.mcp.server import MCPServer

router = APIRouter()
# 获取已有的MCP server实例（从app.state或新建）
mcp_server = MCPServer()

class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict = {}

@router.get("/tools")
async def tools_list():
    """MCP标准接口: tools/list 的HTTP封装"""
    message = type('MCPMessage', (), {
        'id': '1',
        'method': 'tools/list',
        'params': {}
    })()
    response = mcp_server._handle_tools_list(message)
    return response.params

@router.post("/tools/call")
async def tools_call(request: ToolCallRequest):
    """MCP标准接口: tools/call 的HTTP封装"""
    message = type('MCPMessage', (), {
        'id': '1',
        'method': 'tools/call',
        'params': {
            'tool_call': {
                'name': request.name,
                'arguments': request.arguments
            }
        }
    })()
    response = mcp_server._handle_tools_call(message)
    return response.params