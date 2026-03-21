"""
Skill注册表：管理所有技能的注册和执行
"""
from typing import Dict, Any, List, Optional
from ..mcp.client import MCPClient
from .base import Skill
from ..mcp.protocol import ToolDefinition, ToolResult
import logging

logger = logging.getLogger(__name__)

class SkillRegistry:
    """Skill注册表（单例模式）"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SkillRegistry, cls).__new__(cls)
            cls._instance._skills: Dict[str, Skill] = {}
            cls._instance._mcp_client: Optional[MCPClient] = None
        return cls._instance
    
    @property
    def skills(self) -> Dict[str, Skill]:
        """获取所有已注册的技能"""
        return self._skills
    
    @property
    def mcp_client(self) -> Optional[MCPClient]:
        """获取MCP客户端"""
        return self._mcp_client
    
    def set_mcp_client(self, mcp_client: MCPClient) -> None:
        """
        设置MCP客户端
        
        Args:
            mcp_client: MCP客户端实例
        """
        self._mcp_client = mcp_client
        logger.info("MCP client set for SkillRegistry")
    
    def register(self, skill: Skill) -> None:
        """
        注册技能
        
        Args:
            skill: 要注册的技能实例
        """
        if skill.name in self._skills:
            logger.warning(f"Skill '{skill.name}' already registered, overwriting")
        
        self._skills[skill.name] = skill
        logger.info(f"Registered skill: {skill.name}")
        
        # 如果有MCP客户端，自动注册到MCP Server
        if self._mcp_client:
            self._register_to_mcp_server(skill)
    
    def get(self, name: str) -> Optional[Skill]:
        """
        获取指定技能
        
        Args:
            name: 技能名称
            
        Returns:
            Skill: 技能实例，如果不存在则返回None
        """
        return self._skills.get(name)
    
    def list_skills(self) -> List[ToolDefinition]:
        """
        列出所有技能的MCP格式定义
        
        Returns:
            List[ToolDefinition]: 所有技能的MCP工具定义
        """
        return [skill.to_mcp_tool() for skill in self._skills.values()]
    
    async def execute(self, name: str, arguments: Dict[str, Any]) -> str:
        """
        执行指定技能
        
        Args:
            name: 技能名称
            arguments: 技能参数
            
        Returns:
            str: 执行结果
        """
        skill = self.get(name)
        if not skill:
            error_msg = f"Skill '{name}' not found"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        # 验证参数
        if not skill.validate_parameters(arguments):
            error_msg = f"Invalid parameters for skill '{name}'"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        try:
            # 执行技能
            result = await skill.execute(**arguments)
            return result
        except Exception as e:
            error_msg = f"Error executing skill '{name}': {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    
    def _register_to_mcp_server(self, skill: Skill) -> None:
        """
        将技能注册到MCP Server
        
        Args:
            skill: 要注册的技能
        """
        if not self._mcp_client:
            logger.warning("MCP client not set, cannot register to MCP server")
            return
        
        try:
            # 获取MCP Server（通过客户端）
            # 注意：这里假设MCPClient有访问Server的能力，或者我们需要传递Server实例
            # 由于设计要求Skill系统与MCP层解耦，我们通过MCPClient调用
            pass
            
        except Exception as e:
            logger.error(f"Failed to register skill '{skill.name}' to MCP server: {str(e)}")
    
    def unregister(self, name: str) -> bool:
        """
        注销技能
        
        Args:
            name: 技能名称
            
        Returns:
            bool: 是否成功注销
        """
        if name in self._skills:
            del self._skills[name]
            logger.info(f"Unregistered skill: {name}")
            return True
        return False
    
    def clear(self) -> None:
        """清空所有技能"""
        self._skills.clear()
        logger.info("Cleared all skills")
    
    def get_skill_count(self) -> int:
        """获取技能数量"""
        return len(self._skills)