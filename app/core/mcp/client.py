"""
MCP客户端实现：用于Agent调用MCP工具
"""
from typing import List, Optional, Callable, Dict, Any
from .protocol import (
    MCPMessage, 
    ToolDefinition, 
    ToolCall, 
    ToolResult, 
    MCPMethod,
    ToolListResponse
)
from pydantic import BaseModel
import logging
import json

logger = logging.getLogger(__name__)

class MCPClient:
    """MCP客户端类，用于调用MCP工具"""
    
    def __init__(self, send_message: Callable[[MCPMessage], Optional[MCPMessage]]):
        """
        初始化MCP客户端
        
        Args:
            send_message: 发送消息的回调函数，接收MCPMessage并返回响应MCPMessage
        """
        self.send_message = send_message
        self._tools: Dict[str, ToolDefinition] = {}
        self._initialized = False
    
    def initialize(self) -> bool:
        """初始化客户端，获取工具列表"""
        try:
            # 发送工具列表请求
            request = MCPMessage(
                id="init",
                method=MCPMethod.TOOLS_LIST
            )
            
            response = self.send_message(request)
            if not response:
                logger.error("No response received for tools list request")
                return False
            
            # 解析工具列表响应
            if response.method == MCPMethod.TOOLS_LIST and response.params:
                tool_list = ToolListResponse(**response.params)
                self._tools = {tool.name: tool for tool in tool_list.tools}
                self._initialized = True
                logger.info(f"Initialized with {len(self._tools)} tools")
                return True
            else:
                logger.error("Invalid response for tools list request")
                return False
                
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            return False
    
    def list_tools(self) -> List[ToolDefinition]:
        """获取可用工具列表"""
        if not self._initialized:
            if not self.initialize():
                return []
        return list(self._tools.values())
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResult:
        """
        调用指定工具
        
        Args:
            name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具调用结果
        """
        if not self._initialized:
            if not self.initialize():
                return ToolResult(
                    content="Client not initialized",
                    is_error=True
                )
        
        if name not in self._tools:
            return ToolResult(
                content=f"Tool '{name}' not found",
                is_error=True
            )
        
        try:
            # 创建工具调用请求
            tool_call = ToolCall(name=name, arguments=arguments)
            request = MCPMessage(
                id=f"call_{name}_{hash(json.dumps(arguments))}",
                method=MCPMethod.TOOLS_CALL,
                params={"tool_call": tool_call.dict()}
            )
            
            # 发送请求并获取响应
            response = self.send_message(request)
            if not response:
                return ToolResult(
                    content="No response from server",
                    is_error=True
                )
            
            # 解析响应
            if response.method == MCPMethod.TOOLS_CALL and response.params:
                result_data = response.params.get("result", {})
                return ToolResult(**result_data)
            else:
                error_msg = response.params.get("error", "Unknown error")
                return ToolResult(
                    content=error_msg,
                    is_error=True
                )
                
        except Exception as e:
            logger.error(f"Error calling tool {name}: {str(e)}")
            return ToolResult(
                content=f"Error calling tool: {str(e)}",
                is_error=True
            )
    
    def get_tool_definition(self, name: str) -> Optional[ToolDefinition]:
        """获取指定工具的定义"""
        if not self._initialized:
            if not self.initialize():
                return None
        return self._tools.get(name)
    
    def is_tool_available(self, name: str) -> bool:
        """检查工具是否可用"""
        if not self._initialized:
            if not self.initialize():
                return False
        return name in self._tools