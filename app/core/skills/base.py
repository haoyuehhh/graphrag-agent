"""
Skill基础定义：抽象基类和工具转换
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from ..mcp.protocol import ToolDefinition, ToolCall, ToolResult

class Skill(ABC):
    """Skill抽象基类"""
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        timeout: int = 30
    ):
        """
        初始化Skill
        
        Args:
            name: 技能名称
            description: 技能描述
            parameters: 参数定义（JSON Schema格式）
            timeout: 执行超时时间（秒）
        """
        self.name = name
        self.description = description
        self.parameters = parameters
        self.timeout = timeout
    
    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """
        执行技能
        
        Args:
            **kwargs: 技能参数
            
        Returns:
            执行结果字符串
        """
        pass
    
    def to_mcp_tool(self) -> ToolDefinition:
        """
        将Skill转换为MCP工具定义
        
        Returns:
            ToolDefinition: MCP工具定义
        """
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters=self.parameters
        )
    
    def validate_parameters(self, arguments: Dict[str, Any]) -> bool:
        """
        验证参数
        
        Args:
            arguments: 参数字典
            
        Returns:
            bool: 参数是否有效
        """
        # 简单验证：检查必需参数是否存在
        required_params = [param for param, schema in self.parameters.items() 
                         if schema.get("required", False)]
        
        for param in required_params:
            if param not in arguments:
                return False
        
        return True
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """
        获取参数Schema
        
        Returns:
            Dict[str, Any]: 参数Schema
        """
        return self.parameters