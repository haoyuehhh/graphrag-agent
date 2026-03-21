"""
Browser Skill：封装浏览器自动化能力
"""
import asyncio
import os
import logging
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page
from pydantic import BaseModel, Field
from ..base import Skill

logger = logging.getLogger(__name__)

class BrowserSkill(Skill):
    """Browser Skill：封装浏览器自动化能力"""
    
    def __init__(self):
        super().__init__(
            name="browser_navigate",
            description="Navigate to URL and extract structured content from competitor websites",
            parameters={
                "url": {
                    "type": "string", 
                    "description": "Target URL"
                },
                "action": {
                    "type": "string", 
                    "enum": ["navigate", "screenshot", "extract"], 
                    "description": "Browser action"
                },
                "selector": {
                    "type": "string", 
                    "description": "CSS selector for extraction (optional)"
                }
            },
            timeout=60  # 增加超时时间以适应浏览器操作
        )
        
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        self._screenshots_dir = os.path.join(os.path.dirname(__file__), "../../../../data/screenshots")
        
        # 确保截图目录存在
        os.makedirs(self._screenshots_dir, exist_ok=True)
    
    async def _initialize_browser(self) -> None:
        """初始化浏览器"""
        if self._browser is None:
            try:
                playwright = await async_playwright().start()
                self._browser = await playwright.chromium.launch()
                logger.info("Browser initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize browser: {str(e)}")
                raise
    
    async def _cleanup(self) -> None:
        """清理浏览器资源"""
        if self._browser:
            await self._browser.close()
            self._browser = None
            self._page = None
            logger.info("Browser cleaned up")
    
    async def execute(self, **kwargs) -> str:
        """
        执行浏览器操作
        
        Args:
            **kwargs: 技能参数
            
        Returns:
            str: 执行结果
        """
        url = kwargs.get("url")
        action = kwargs.get("action", "navigate")
        selector = kwargs.get("selector")
        
        if not url:
            return "Error: URL parameter is required"
        
        try:
            # 初始化浏览器
            await self._initialize_browser()
            
            # 创建新页面
            if self._browser:
                self._page = await self._browser.new_page()
            
            # 执行指定操作
            if action == "navigate":
                return await self._navigate(url)
            elif action == "screenshot":
                return await self._screenshot(url)
            elif action == "extract":
                return await self._extract(url, selector)
            else:
                return f"Error: Unknown action '{action}'"
                
        except ImportError:
            return "Error: playwright is not installed. Please install it with: pip install playwright && playwright install"
        except Exception as e:
            error_msg = f"Browser operation failed: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        finally:
            # 注意：为了保持浏览器会话，我们不在这里关闭浏览器
            # 而是在单独的清理方法中处理
            pass
    
    async def _navigate(self, url: str) -> str:
        """导航到URL并提取内容"""
        if not self._page:
            return "Error: Browser page not initialized"
        
        try:
            await self._page.goto(url, wait_until="networkidle")
            title = await self._page.title()
            content = await self._page.content()
            
            # 提取文本内容（限制长度）
            text = await self._page.text_content("body")
            if text:
                text = text[:500]  # 限制为前500字符
            
            return f"Title: {title}\n\nContent:\n{text}"
        except Exception as e:
            return f"Navigation failed: {str(e)}"
    
    async def _screenshot(self, url: str) -> str:
        """截取网页截图"""
        if not self._page:
            return "Error: Browser page not initialized"
        
        try:
            await self._page.goto(url, wait_until="networkidle")
            
            # 生成唯一文件名
            import uuid
            filename = f"screenshot_{uuid.uuid4().hex[:8]}.png"
            filepath = os.path.join(self._screenshots_dir, filename)
            
            await self._page.screenshot(path=filepath)
            return f"Screenshot saved to: {filepath}"
        except Exception as e:
            return f"Screenshot failed: {str(e)}"
    
    async def _extract(self, url: str, selector: str) -> str:
        """提取指定选择器的文本内容"""
        if not self._page or not selector:
            return "Error: Browser page not initialized or selector not provided"
        
        try:
            await self._page.goto(url, wait_until="networkidle")
            
            # 提取文本内容
            elements = await self._page.query_selector_all(selector)
            extracted_data = []
            
            for element in elements:
                text = await element.text_content()
                if text:
                    extracted_data.append(text.strip())
            
            # 返回JSON格式结果
            import json
            return json.dumps({
                "selector": selector,
                "extracted_content": extracted_data,
                "count": len(extracted_data)
            }, ensure_ascii=False)
        except Exception as e:
            return f"Extraction failed: {str(e)}"
    
    async def cleanup(self) -> None:
        """清理浏览器资源"""
        await self._cleanup()
    
    def get_browser_status(self) -> str:
        """获取浏览器状态"""
        if self._browser:
            return "Browser is running"
        return "Browser is not running"