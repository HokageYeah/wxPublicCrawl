"""
Playwright 浏览器管理基类
提供通用的 Playwright 浏览器操作功能
"""

import os
import sys
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from loguru import logger


class PlaywrightManager:
    """
    Playwright 浏览器管理基类
    
    提供通用的浏览器操作功能，包括：
    - 浏览器路径管理（开发/打包环境）
    - 浏览器启动配置
    - 上下文创建
    - 反爬虫脚本注入
    """
    
    # 默认配置常量
    DEFAULT_VIEWPORT = {'width': 1920, 'height': 1080}
    DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    DEFAULT_BROWSER_ARGS = ['--disable-blink-features=AutomationControlled']
    
    # 反爬虫检测绕过脚本
    ANTI_DETECTION_SCRIPT = """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """
    
    def __init__(self, headless: bool = False):
        """
        初始化 Playwright 管理器
        
        参数:
            headless: 是否使用无头模式（False=显示浏览器）
        """
        self.headless = headless
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        
    @staticmethod
    def setup_browser_path() -> Optional[str]:
        """
        设置 Playwright 浏览器路径
        
        在打包环境中，使用内置的浏览器
        在开发环境中，使用系统安装的浏览器
        
        返回:
            str: 浏览器路径（开发环境返回 None）
        """
        # 检测是否在 PyInstaller 打包环境中
        if getattr(sys, 'frozen', False):
            # 打包环境
            bundle_dir = sys._MEIPASS
            browsers_path = os.path.join(bundle_dir, 'playwright_browsers')
            
            logger.info(f"🔧 打包环境 - Playwright 浏览器路径: {browsers_path}")
            
            # 检查目录是否存在
            if os.path.exists(browsers_path):
                # 设置 Playwright 浏览器路径环境变量
                os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_path
                logger.info(f"✅ 已设置 Playwright 浏览器路径")
                return browsers_path
            else:
                logger.error(f"❌ 打包的 Playwright 浏览器不存在: {browsers_path}")
                return None
        else:
            # 开发环境，使用默认路径
            logger.info("🔧 开发环境 - 使用系统 Playwright 浏览器")
            return None
    
    async def launch_browser(
        self,
        headless: Optional[bool] = None,
        args: Optional[list] = None
    ) -> Browser:
        """
        启动浏览器
        
        参数:
            headless: 是否无头模式（None=使用初始化时的设置）
            args: 浏览器启动参数（None=使用默认参数）
        
        返回:
            Browser: 浏览器实例
        """
        # 设置浏览器路径
        self.setup_browser_path()
        
        # 使用传入的参数或默认值
        if headless is None:
            headless = self.headless
        if args is None:
            args = self.DEFAULT_BROWSER_ARGS
        
        # 启动 Playwright
        self._playwright = await async_playwright().start()
        
        # 启动浏览器
        self._browser = await self._playwright.chromium.launch(
            headless=headless,
            args=args
        )
        
        logger.info(f"✅ 浏览器已启动 (headless={headless})")
        return self._browser
    
    async def create_context(
        self,
        viewport: Optional[Dict[str, int]] = None,
        user_agent: Optional[str] = None,
        extra_options: Optional[Dict[str, Any]] = None
    ) -> BrowserContext:
        """
        创建浏览器上下文
        
        参数:
            viewport: 视口大小（None=使用默认值）
            user_agent: 用户代理（None=使用默认值）
            extra_options: 额外的上下文选项
        
        返回:
            BrowserContext: 浏览器上下文
        """
        if not self._browser:
            raise RuntimeError("浏览器未启动，请先调用 launch_browser()")
        
        # 使用传入的参数或默认值
        if viewport is None:
            viewport = self.DEFAULT_VIEWPORT
        if user_agent is None:
            user_agent = self.DEFAULT_USER_AGENT
        
        # 合并选项
        options = {
            'viewport': viewport,
            'user_agent': user_agent
        }
        if extra_options:
            options.update(extra_options)
        
        # 创建上下文
        self._context = await self._browser.new_context(**options)
        
        # 注入反爬虫检测绕过脚本
        await self._context.add_init_script(self.ANTI_DETECTION_SCRIPT)
        
        logger.info("✅ 浏览器上下文已创建")
        return self._context
    
    async def new_page(self) -> Page:
        """
        创建新页面
        
        返回:
            Page: 页面实例
        """
        if not self._context:
            raise RuntimeError("浏览器上下文未创建，请先调用 create_context()")
        
        page = await self._context.new_page()
        logger.info("✅ 新页面已创建")
        return page
    
    async def close(self):
        """关闭浏览器和 Playwright"""
        if self._browser:
            await self._browser.close()
            logger.info("✅ 浏览器已关闭")
        
        if self._playwright:
            await self._playwright.stop()
            logger.info("✅ Playwright 已停止")
    
    async def get_cookies(self) -> list:
        """
        获取当前上下文的所有 cookies
        
        返回:
            list: Playwright cookies 列表
        """
        if not self._context:
            raise RuntimeError("浏览器上下文未创建")
        
        cookies = await self._context.cookies()
        logger.info(f"✅ 获取到 {len(cookies)} 个 Cookie")
        return cookies
    
    @staticmethod
    def cookies_to_dict(cookies: list) -> Dict[str, str]:
        """
        将 Playwright cookies 列表转换为字典格式
        
        参数:
            cookies: Playwright cookies 列表
        
        返回:
            Dict[str, str]: cookies 字典
        """
        return {cookie['name']: cookie['value'] for cookie in cookies}
    
    @staticmethod
    def dict_to_playwright_cookies(
        cookies_dict: Dict[str, str],
        domain: str = '.ximalaya.com'
    ) -> list:
        """
        将 cookies 字典转换为 Playwright 格式
        
        参数:
            cookies_dict: cookies 字典
            domain: cookie 的域名
        
        返回:
            list: Playwright cookies 列表
        """
        playwright_cookies = []
        for name, value in cookies_dict.items():
            playwright_cookies.append({
                'name': name,
                'value': value,
                'domain': domain,
                'path': '/',
                'httpOnly': False,
                'secure': True,
                'sameSite': 'Lax'
            })
        return playwright_cookies
    
    @staticmethod
    def cookies_dict_to_string(cookies_dict: Dict[str, str]) -> str:
        """
        将 cookies 字典转换为 Cookie 请求头字符串
        
        参数:
            cookies_dict: cookies 字典
        
        返回:
            str: Cookie 字符串（如：'name1=value1; name2=value2'）
        """
        return '; '.join([f"{k}={v}" for k, v in cookies_dict.items()])
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.launch_browser()
        await self.create_context()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
