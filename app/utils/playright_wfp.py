"""
喜马拉雅登录后浏览器访问工具
使用 Playwright 打开浏览器并带上 cookies 访问指定页面
"""

import asyncio
from typing import Dict
from playwright.async_api import async_playwright
from loguru import logger


async def open_browser_with_cookies(
    url: str,
    cookies: Dict[str, str],
    headless: bool = False,
    wait_seconds: int = 30
) -> Dict[str, str]:
    """
    打开浏览器并带上 cookies 访问指定页面
    
    参数:
        url: 要访问的页面URL
        cookies: cookies字典（键值对）
        headless: 是否无头模式（False=显示浏览器）
        wait_seconds: 页面停留时间（秒）
    
    返回:
        Dict[str, str]: 新页面中的所有 cookie（键值对）
    """
    try:
        logger.info(f"正在打开浏览器访问: {url}")
        logger.info(f"Cookies 数量: {len(cookies)}")
        
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(
                headless=headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # 创建浏览器上下文
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
            )
            
            # 添加反爬虫检测绕过脚本
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            # 创建新页面
            page = await context.new_page()
            
            # 先访问域名以设置 cookies
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # 将 cookies 字典转换为 Playwright 格式并添加到上下文
            playwright_cookies = []
            for name, value in cookies.items():
                playwright_cookies.append({
                    'name': name,
                    'value': value,
                    'domain': '.ximalaya.com',  # 喜马拉雅域名
                    'path': '/',
                    'httpOnly': False,
                    'secure': True,
                    'sameSite': 'Lax'
                })
            
            # 添加 cookies 到浏览器上下文
            await context.add_cookies(playwright_cookies)
            logger.info("✓ Cookies 已添加到浏览器")
            
            # 重新加载页面以应用 cookies
            await page.reload(wait_until='domcontentloaded')
            await asyncio.sleep(2)  # 等待页面加载
            
            logger.info(f"✓ 页面加载完成，浏览器将保持打开 {wait_seconds} 秒")
            logger.info("  您可以在浏览器中进行操作...")
            
            # 不展示页面 不保持页面打开一段时间供用户查看/操作
            # await asyncio.sleep(wait_seconds)
            
            # 在关闭浏览器前获取所有 cookies
            all_cookies = await context.cookies()
            new_cookies = {}
            for cookie in all_cookies:
                new_cookies[cookie['name']] = cookie['value']
            
            logger.info(f"✓ 获取到 {len(new_cookies)} 个 Cookie")
            
            # 关闭浏览器
            await browser.close()
            logger.info("✓ 浏览器已关闭")
            
            return new_cookies
            
    except Exception as e:
        logger.error(f"✗ 打开浏览器失败: {e}")
        raise


def open_browser_with_cookies_sync(
    url: str,
    cookies: Dict[str, str],
    headless: bool = False,
    wait_seconds: int = 30
) -> None:
    """
    打开浏览器并带上 cookies 访问指定页面（同步版本）
    
    参数:
        url: 要访问的页面URL
        cookies: cookies字典（键值对）
        headless: 是否无头模式（False=显示浏览器）
        wait_seconds: 页面停留时间（秒）
    """
    asyncio.run(open_browser_with_cookies(url, cookies, headless, wait_seconds))


# 测试代码
async def main():
    """测试函数"""
    test_cookies = {
        '1&remember_me': 'true',
        'web_login_1684588034048': 'NzI2NTg0NjIx',
        # 这里放置实际的测试 cookies
    }
    
    await open_browser_with_cookies(
        url="https://www.ximalaya.com/",
        cookies=test_cookies,
        headless=False,
        wait_seconds=30
    )


if __name__ == "__main__":
    asyncio.run(main())
