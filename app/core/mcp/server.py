"""
MCP服务器实现：处理工具注册和消息路由
"""
from typing import Callable, Dict, Any, List, Optional
from .protocol import (
    MCPMessage, 
    ToolDefinition, 
    ToolCall, 
    ToolResult, 
    MCPMethod,
    ToolListResponse
)
from pydantic import BaseModel
import json
import logging

logger = logging.getLogger(__name__)

class MCPServer:
    """MCP服务器类，维护工具注册和消息处理"""
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self.tool_handlers: Dict[str, Callable] = {}
    
    def register_tool(
        self, 
        tool_def: ToolDefinition, 
        handler: Callable[[Dict[str, Any]], ToolResult]
    ) -> None:
        """
        注册工具
        
        Args:
            tool_def: 工具定义
            handler: 工具处理函数，接收参数并返回ToolResult
        """
        self.tools[tool_def.name] = tool_def
        self.tool_handlers[tool_def.name] = handler
        logger.info(f"Registered tool: {tool_def.name}")
    
    def handle_message(self, message: MCPMessage) -> Optional[MCPMessage]:
        """
        处理MCP消息
        
        Args:
            message: 接收到的MCP消息
            
        Returns:
            响应消息或None（如果不需要响应）
        """
        try:
            if message.method == MCPMethod.TOOLS_LIST:
                return self._handle_tools_list(message)
            elif message.method == MCPMethod.TOOLS_CALL:
                return self._handle_tools_call(message)
            else:
                logger.warning(f"Unknown method: {message.method}")
                return None
                
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            return None
    
    def _handle_tools_list(self, message: MCPMessage) -> MCPMessage:
        """处理工具列表请求"""
        response = ToolListResponse(tools=list(self.tools.values()))
        return MCPMessage(
            id=message.id,
            method=MCPMethod.TOOLS_LIST,
            params={"tools": [tool.dict() for tool in response.tools]}
        )
    
    def _handle_tools_call(self, message: MCPMessage) -> MCPMessage:
        """处理工具调用请求"""
        if not message.params or "tool_call" not in message.params:
            error_msg = "Missing tool_call in params"
            logger.error(error_msg)
            return MCPMessage(
                id=message.id,
                method=MCPMethod.TOOLS_CALL,
                params={"error": error_msg, "is_error": True}
            )
        
        tool_call = ToolCall(**message.params["tool_call"])
        
        if tool_call.name not in self.tool_handlers:
            error_msg = f"Tool not found: {tool_call.name}"
            logger.error(error_msg)
            return MCPMessage(
                id=message.id,
                method=MCPMethod.TOOLS_CALL,
                params={
                    "error": error_msg,
                    "is_error": True,
                    "tool_name": tool_call.name
                }
            )
        
        try:
            # 调用工具处理函数
            result = self.tool_handlers[tool_call.name](tool_call.arguments)
            return MCPMessage(
                id=message.id,
                method=MCPMethod.TOOLS_CALL,
                params={"result": result.dict()}
            )
        except Exception as e:
            error_msg = f"Error executing tool {tool_call.name}: {str(e)}"
            logger.error(error_msg)
            return MCPMessage(
                id=message.id,
                method=MCPMethod.TOOLS_CALL,
                params={
                    "error": error_msg,
                    "is_error": True,
                    "tool_name": tool_call.name
                }
            )
    
    def get_tool_definitions(self) -> List[ToolDefinition]:
        """获取所有已注册的工具定义"""
        return list(self.tools.values())
    
    def get_tool_handler(self, tool_name: str) -> Optional[Callable]:
        """获取指定工具的处理函数"""
        return self.tool_handlers.get(tool_name)