"""
喜马拉雅滑块验证自动化解决方案
使用 Playwright 完成滑块验证并获取有效 cookies
"""

import asyncio
import random
from playwright.async_api import TimeoutError as PlaywrightTimeout
from loguru import logger

from app.utils.playright_manager import PlaywrightManager


class SliderSolver(PlaywrightManager):
    """
    滑块验证解决器
    
    继承自 PlaywrightManager，提供自动化滑块验证功能
    """

    def __init__(self, headless: bool = False):
        """
        初始化滑块解决器

        参数:
            headless: 是否无头模式运行（False=显示浏览器，方便调试）
        """
        super().__init__(headless=headless)
        self.cookies_file = "ximalaya_cookies.json"

    async def solve_slider(self, album_url: str) -> dict:
        """
        自动化解决滑块验证

        参数:
            album_url: 专辑页面URL
        返回:
            cookies字典
        """
        try:
            # 启动浏览器和创建上下文
            await self.launch_browser()
            await self.create_context()
            
            # 创建新页面
            page = await self.new_page()

            print("=" * 60)
            print("正在访问专辑页面...")
            print(f"URL: {album_url}")
            print("=" * 60)

            # 访问专辑页面，设置60秒超时，使用更宽松的等待条件
            try:
                await page.goto(
                    album_url,
                    wait_until='domcontentloaded',
                    timeout=60000  # 60秒超时
                )
            except PlaywrightTimeout:
                print("⚠️ 页面加载超时，但继续尝试获取cookies...")
            
            # 等待页面加载完成
            await asyncio.sleep(2)

            # 检查是否出现滑块验证
            print("\n检测页面状态...")

            # 方法1: 检查是否有滑块元素
            slider_exists = await page.locator('iframe[src*="verify"]').count() > 0

            if slider_exists:
                print("[检测到滑块验证] 准备自动化处理...")
                await self._handle_slider(page)
            else:
                print("[未检测到滑块] 页面正常加载")

            # 等待验证完成后的页面稳定
            await asyncio.sleep(3)

            # 获取cookies
            cookies = await self.get_cookies()

            # 保存cookies
            self._save_cookies(cookies)

            print("\n" + "=" * 60)
            print(f"[SUCCESS] Cookies 已保存")
            print(f"共 {len(cookies)} 个 cookie")
            for cookie in cookies:
                print(f"Cookie: {cookie['name']}: {cookie['value']}")
            print("=" * 60)

            # 关闭浏览器
            await self.close()

            return self.cookies_to_dict(cookies)
            
        except Exception as e:
            logger.error(f"❌ 滑块验证失败: {e}")
            # 确保浏览器被关闭
            try:
                await self.close()
            except:
                pass
            raise

    async def _handle_slider(self, page):
        """
        处理滑块验证

        参数:
            page: Playwright页面对象
        """
        try:
            print("\n开始滑块验证流程...")

            # 等待iframe加载
            print("1. 等待滑块iframe加载...")
            await page.wait_for_selector('iframe[src*="verify"]', timeout=10000)

            # 获取iframe
            iframe_element = await page.query_selector('iframe[src*="verify"]')
            iframe = await iframe_element.content_frame()

            if not iframe:
                print("[ERROR] 无法获取iframe内容")
                return

            print("2. 定位滑块元素...")

            # 等待滑块按钮出现（根据喜马拉雅实际元素调整选择器）
            slider_button = await iframe.wait_for_selector(
                '.tc-slider-normal, .slider-button, [class*="slider"]',
                timeout=5000
            )

            if not slider_button:
                print("[ERROR] 未找到滑块按钮")
                return

            print("3. 获取滑块边界...")

            # 获取滑块轨道和按钮的位置信息
            button_box = await slider_button.bounding_box()

            if not button_box:
                print("[ERROR] 无法获取滑块位置")
                return

            print(f"   滑块位置: x={button_box['x']}, y={button_box['y']}")

            # 计算滑动距离（通常需要滑到80-95%位置）
            # 这里使用保守的策略：分段滑动，模拟人类行为
            print("4. 开始滑动验证...")

            await self._simulate_human_drag(page, iframe, slider_button, button_box)

            print("5. 等待验证结果...")
            await asyncio.sleep(2)

            # 检查是否验证成功
            success = await self._check_verification_success(iframe)

            if success:
                print("[SUCCESS] 滑块验证成功！")
            else:
                print("[WARNING] 滑块验证可能失败，请手动完成")
                # 给用户30秒时间手动完成
                print("等待30秒，请手动完成滑块验证...")
                await asyncio.sleep(30)

        except PlaywrightTimeout:
            print("[WARNING] 滑块元素加载超时，可能不需要验证或页面结构已变化")
        except Exception as e:
            print(f"[ERROR] 滑块处理异常: {e}")
            print("请手动完成滑块验证，等待30秒...")
            await asyncio.sleep(30)

    async def _simulate_human_drag(self, page, iframe, slider_button, button_box):
        """
        模拟人类拖动行为

        参数:
            page: 主页面
            iframe: 滑块iframe
            slider_button: 滑块按钮元素
            button_box: 滑块位置信息
        """
        # 获取滑块轨道宽度（通常是固定的，如300px）
        # 这里使用保守估计
        track_width = 300  # 根据实际情况调整

        # 计算起始和结束位置
        start_x = button_box['x'] + button_box['width'] / 2
        start_y = button_box['y'] + button_box['height'] / 2

        # 滑动距离（轨道的85-95%）
        slide_distance = track_width * random.uniform(0.85, 0.95)
        end_x = start_x + slide_distance

        # 移动鼠标到滑块
        await page.mouse.move(start_x, start_y)
        await asyncio.sleep(random.uniform(0.1, 0.3))

        # 按下鼠标
        await page.mouse.down()
        await asyncio.sleep(random.uniform(0.1, 0.2))

        # 分段滑动，模拟人类加速-减速行为
        steps = random.randint(15, 25)
        for i in range(steps):
            progress = i / steps

            # 使用贝塞尔曲线模拟加速度变化
            # 开始慢，中间快，结束慢
            if progress < 0.3:
                factor = progress / 0.3 * 0.3
            elif progress > 0.7:
                factor = 0.3 + 0.4 + (progress - 0.7) / 0.3 * 0.3
            else:
                factor = 0.3 + (progress - 0.3) / 0.4 * 0.4

            current_x = start_x + slide_distance * factor

            # 添加随机抖动
            jitter_y = random.uniform(-2, 2)

            await page.mouse.move(current_x, start_y + jitter_y)
            await asyncio.sleep(random.uniform(0.01, 0.03))

        # 最后精确到达终点
        await page.mouse.move(end_x, start_y)
        await asyncio.sleep(random.uniform(0.1, 0.2))

        # 释放鼠标
        await page.mouse.up()

    async def _check_verification_success(self, iframe):
        """
        检查验证是否成功

        参数:
            iframe: 滑块iframe
        返回:
            bool: 是否成功
        """
        try:
            # 检查成功标识（根据喜马拉雅实际元素调整）
            success_elements = [
                '.verify-success',
                '[class*="success"]',
                '.slide-verify-success'
            ]

            for selector in success_elements:
                element = await iframe.query_selector(selector)
                if element:
                    return True

            return False
        except:
            return False

    def _save_cookies(self, cookies):
        """
        保存cookies
        使用的是 app.services.xmly 中的 session 管理机制
        """
        try:
            # 延迟导入以避免循环依赖
            from app.services.xmly import load_xmly_session, save_xmly_session
            
            # 将 Playwright cookies 列表转换为字典
            cookies_dict = self.cookies_to_dict(cookies)
            
            # 尝试加载现有会话
            session = load_xmly_session()
            
            status_data = {}
            if session and session.get('user_info'):
                status_data = session['user_info']

            old_cookies = {}
            # 如果有cookie 则合并
            if session and session.get('cookies'):
                old_cookies = session.get('cookies')

            merged_cookies = {**old_cookies, **cookies_dict}
            
            # 保存会话 (如果存在则更新 cookies，不存在则创建新会话)
            save_xmly_session(status_data, merged_cookies)
            
            print(f"[INFO] Cookies 已通过 save_xmly_session 更新")
            
        except Exception as e:
            print(f"[ERROR] 保存cookies失败: {e}")


async def main():
    """测试函数"""
    solver = SliderSolver(headless=False)  # 显示浏览器，方便调试

    # 测试专辑URL
    test_url = "https://www.ximalaya.com/album/18463126"

    print("\n喜马拉雅滑块验证自动化测试")
    print("=" * 60)

    cookies = await solver.solve_slider(test_url)

    print("\n获取到的Cookies:")
    for name, value in cookies.items():
        print(f"  {name}: {value[:50]}..." if len(value) > 50 else f"  {name}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
