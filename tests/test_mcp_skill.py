"""
MCP和Skill集成测试
"""
import pytest
from app.core.mcp.protocol import ToolCall, ToolResult, ToolDefinition
from app.core.mcp.server import MCPServer
from app.core.skills import SkillRegistry
from app.core.skills.implementations import BrowserSkill
import json

def test_mcp_protocol_serialization():
    """测试MCP协议序列化和反序列化"""
    tool_call = ToolCall(name="test", arguments={"url": "https://example.com"})
    json_str = tool_call.json()
    assert "test" in json_str
    assert "https://example.com" in json_str
    
    # 测试反序列化
    parsed = ToolCall.parse_raw(json_str)
    assert parsed.name == "test"
    assert parsed.arguments["url"] == "https://example.com"

def test_tool_result_serialization():
    """测试ToolResult序列化"""
    result = ToolResult(
        content="Test result",
        is_error=False
    )
    json_str = result.json()
    assert "Test result" in json_str
    assert "false" in json_str  # is_error为false

def test_skill_registry():
    """测试Skill注册表"""
    registry = SkillRegistry()
    browser_skill = BrowserSkill()
    registry.register(browser_skill)
    
    # 检查技能是否注册
    assert "browser_navigate" in [s.name for s in registry.list_skills()]
    
    # 测试转换为MCP格式
    mcp_def = browser_skill.to_mcp_tool()
    assert mcp_def.name == "browser_navigate"
    assert mcp_def.description == "Navigate to URL and extract structured content from competitor websites"
    assert "url" in mcp_def.parameters["properties"]

def test_tool_definition_parameters():
    """测试工具定义参数"""
    browser_skill = BrowserSkill()
    params = browser_skill.parameters
    
    # 检查必需参数
    assert "url" in params["properties"]
    assert params["properties"]["url"]["type"] == "string"
    assert params["properties"]["url"]["description"] == "Target URL"
    
    # 检查action参数
    assert "action" in params["properties"]
    assert params["properties"]["action"]["type"] == "string"
    assert "enum" in params["properties"]["action"]
    assert "navigate" in params["properties"]["action"]["enum"]

def test_mcp_server_basic():
    """测试MCP服务器基本功能"""
    server = MCPServer()
    
    # 测试工具注册
    class TestTool:
        def __init__(self):
            self.name = "test_tool"
        
        def to_mcp_tool(self):
            return ToolDefinition(
                name=self.name,
                description="Test tool",
                parameters={}
            )
    
    test_tool = TestTool()
    server.register_tool(test_tool.to_mcp_tool(), lambda x: ToolResult(content="test"))
    
    # 测试工具列表
    response = server.handle_message(
        ToolCall(name="test_tool", arguments={}).to_mcp_message("test")
    )
    assert response is not None
    assert "test_tool" in str(response.json())

@pytest.mark.asyncio
async def test_browser_skill_mock():
    """测试BrowserSkill（模拟）"""
    # 使用mock测试，避免真实启动浏览器
    skill = BrowserSkill()
    
    # 测试参数schema正确性
    assert "url" in skill.parameters["properties"]
    assert "action" in skill.parameters["properties"]
    assert "selector" in skill.parameters["properties"]
    
    # 测试参数验证
    assert skill.validate_parameters({"url": "https://example.com", "action": "navigate"})
    assert not skill.validate_parameters({"action": "navigate"})  # 缺少url参数

if __name__ == "__main__":
    pytest.main([__file__])