"""
喜马拉雅登录后浏览器访问工具
使用 Playwright 打开浏览器并带上 cookies 访问指定页面
"""

import asyncio
from typing import Dict
from loguru import logger

from app.utils.playright_manager import PlaywrightManager


class CookieBrowserManager(PlaywrightManager):
    """
    带 Cookie 的浏览器管理器
    
    继承自 PlaywrightManager，提供 cookies 注入和访问功能
    """
    
    async def open_with_cookies(
        self,
        url: str,
        cookies: Dict[str, str],
        wait_seconds: int = 30
    ) -> Dict[str, str]:
        """
        打开浏览器并带上 cookies 访问指定页面
        
        参数:
            url: 要访问的页面URL
            cookies: cookies字典（键值对）
            wait_seconds: 页面停留时间（秒）- 当前未使用
        
        返回:
            Dict[str, str]: 新页面中的所有 cookie（键值对）
        """
        try:
            logger.info(f"正在打开浏览器访问: {url}")
            logger.info(f"Cookies 数量: {len(cookies)}")
            
            # 启动浏览器和创建上下文
            await self.launch_browser()
            await self.create_context()
            
            # 创建新页面
            page = await self.new_page()
            
            # 先访问域名以设置 cookies
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # 将 cookies 字典转换为 Playwright 格式并添加到上下文
            playwright_cookies = self.dict_to_playwright_cookies(
                cookies,
                domain='.ximalaya.com'
            )
            
            # 添加 cookies 到浏览器上下文
            await self._context.add_cookies(playwright_cookies)
            logger.info("✓ Cookies 已添加到浏览器")
            
            # 重新加载页面以应用 cookies
            await page.reload(wait_until='domcontentloaded')
            await asyncio.sleep(2)  # 等待页面加载
            
            logger.info(f"✓ 页面加载完成")
            
            # 获取所有 cookies（更新后的）
            all_cookies = await self.get_cookies()
            new_cookies = self.cookies_to_dict(all_cookies)
            
            logger.info(f"✓ 获取到 {len(new_cookies)} 个 Cookie")
            
            # 关闭浏览器
            await self.close()
            logger.info("✓ 浏览器已关闭")
            
            return new_cookies
            
        except Exception as e:
            logger.error(f"✗ 打开浏览器失败: {e}")
            # 确保浏览器被关闭
            try:
                await self.close()
            except:
                pass
            raise


async def open_browser_with_cookies(
    url: str,
    cookies: Dict[str, str],
    headless: bool = False,
    wait_seconds: int = 30
) -> Dict[str, str]:
    """
    打开浏览器并带上 cookies 访问指定页面（函数式接口）
    
    参数:
        url: 要访问的页面URL
        cookies: cookies字典（键值对）
        headless: 是否无头模式（False=显示浏览器）
        wait_seconds: 页面停留时间（秒）
    
    返回:
        Dict[str, str]: 新页面中的所有 cookie（键值对）
    """
    manager = CookieBrowserManager(headless=headless)
    return await manager.open_with_cookies(url, cookies, wait_seconds)


def open_browser_with_cookies_sync(
    url: str,
    cookies: Dict[str, str],
    headless: bool = False,
    wait_seconds: int = 30
) -> Dict[str, str]:
    """
    打开浏览器并带上 cookies 访问指定页面（同步版本）
    
    参数:
        url: 要访问的页面URL
        cookies: cookies字典（键值对）
        headless: 是否无头模式（False=显示浏览器）
        wait_seconds: 页面停留时间（秒）
    
    返回:
        Dict[str, str]: 新页面中的所有 cookie（键值对）
    """
    return asyncio.run(open_browser_with_cookies(url, cookies, headless, wait_seconds))


# 测试代码
async def main():
    """测试函数"""
    test_cookies = {
        '1&remember_me': 'true',
        'web_login_1684588034048': 'NzI2NTg0NjIx',
        # 这里放置实际的测试 cookies
    }
    
    cookies = await open_browser_with_cookies(
        url="https://www.ximalaya.com/",
        cookies=test_cookies,
        headless=False,
        wait_seconds=30
    )
    
    print(f"获取到的 Cookies: {len(cookies)} 个")
    for name, value in cookies.items():
        print(f"  {name}: {value[:50]}..." if len(value) > 50 else f"  {name}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
