"""
使用Node.js调用JIMI.JS生成xm-sign
这是最简单、最可靠的方式
"""

import subprocess
import json
import os
from loguru import logger


def parse_node_version(version_string: str) -> tuple[int, int, int]:
    """
    解析 Node.js 版本字符串，返回 (major, minor, patch)
    
    例如: "v20.10.0" -> (20, 10, 0)
    """
    # 移除 'v' 前缀
    version_string = version_string.lstrip('v')
    
    try:
        major, minor, patch = version_string.split('.')
        return int(major), int(minor), int(patch)
    except (ValueError, AttributeError):
        logger.error(f"无法解析 Node.js 版本: {version_string}")
        return (0, 0, 0)


class XimalayaSignNode:
    """通过Node.js调用JIMI.JS生成xm-sign"""

    def __init__(self):
        # 获取JIMI.JS的路径
        self.jimi_js_path = os.path.join(os.path.dirname(__file__), 'JIMI.JS')
        self.is_available = False  # 签名生成器是否可用

        logger.info(f"JIMI.JS路径: {self.jimi_js_path}")

        # 检查JIMI.JS是否存在
        if not os.path.exists(self.jimi_js_path):
            logger.error(f"❌ JIMI.JS文件不存在: {self.jimi_js_path}")
            return

        # 检查Node.js是否安装及版本
        try:
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            version_string = result.stdout.strip()
            self.node_version = parse_node_version(version_string)
            self.node_version_string = version_string
            
            logger.info(f"✅ Node.js 版本: {version_string}")
            
            # 检查版本是否 >= 20
            if self.node_version[0] < 20:
                logger.warning("⚠️ Node.js 版本低于 20.0")
                logger.warning("⚠️ JIMI.JS 需要 Node.js 20.0 或更高版本")
                logger.warning("⚠️ 签名生成器将被禁用")
                logger.info("💡 升级 Node.js: https://nodejs.org/")
                logger.info("💡 或使用 nvm: nvm install 20 && nvm use 20")
                self.is_available = False
                self.error_message = f"Node.js 版本过低（{version_string}），需要 20.0 或更高版本。请升级 Node.js：https://nodejs.org/"
            else:
                logger.info("✅ Node.js 版本满足要求，签名生成器可用")
                self.is_available = True
                self.error_message = None
                
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error("❌ Node.js 未安装或不在 PATH 中")
            logger.error("💡 请先安装 Node.js: https://nodejs.org/")
            self.is_available = False
            self.error_message = "Node.js 未安装，请先安装 Node.js：https://nodejs.org/"
        except Exception as e:
            logger.error(f"❌ 检查 Node.js 版本时出错: {e}")
            self.is_available = False
            self.error_message = f"检查 Node.js 版本时出错: {e}"

    def get_xm_sign(self):
        """
        生成xm-sign

        返回: (success: bool, xm_sign: str | None, error_message: str | None)
               success: 是否成功生成
               xm_sign: 签名字符串
               error_message: 错误信息
        """
        # 检查签名生成器是否可用
        if not self.is_available:
            error_msg = self.error_message if self.error_message else "签名生成器不可用"
            logger.info(f"ℹ️ {error_msg}")
            return False, None, error_msg

        try:
            print("=" * 60)
            print("通过Node.js调用JIMI.JS生成xm-sign...")
            print("=" * 60)

            # 执行Node.js脚本
            result = subprocess.run(
                ['node', self.jimi_js_path],
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )

            # 解析输出
            output = result.stdout.strip()
            print(f"Node.js输出: {output}")

            # 解析JSON
            data = json.loads(output)
            xm_sign = data.get('sign', '')

            if xm_sign:
                print("=" * 60)
                print("[SUCCESS] xm-sign 生成成功!")

                # 解析browser_id和session_id
                if '&&' in xm_sign:
                    parts = xm_sign.split('&&')
                    browser_id = parts[0]
                    session_id = parts[1]

                    print(f"browser_id: {browser_id}")
                    print(f"session_id: {session_id}")

                print(f"xm-sign: {xm_sign}")
                print("=" * 60)

                return True, xm_sign, None
            else:
                error_msg = "响应中未找到sign字段"
                print(f"[ERROR] {error_msg}")
                return False, None, error_msg

        except subprocess.TimeoutExpired:
            error_msg = "Node.js执行超时"
            print(f"[ERROR] {error_msg}")
            return False, None, error_msg
        except subprocess.CalledProcessError as e:
            error_msg = f"Node.js执行失败: {e.stderr}"
            print(f"[ERROR] {error_msg}")
            return False, None, error_msg
        except json.JSONDecodeError as e:
            error_msg = f"JSON解析失败: {e}"
            print(f"[ERROR] {error_msg}")
            print(f"原始输出: {result.stdout}")
            return False, None, error_msg
        except Exception as e:
            error_msg = f"生成xm-sign失败: {e}"
            print(f"[ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            return False, None, error_msg

    def verify_xm_sign(self, xm_sign):
        """
        验证xm-sign格式是否正确

        参数:
            xm_sign: 待验证的签名
        返回: True/False
        """
        if not xm_sign or "&&" not in xm_sign:
            return False

        parts = xm_sign.split("&&")
        if len(parts) != 2:
            return False

        browser_id, session_id = parts

        # 验证browser_id长度
        if len(browser_id) < 10:
            return False

        # 验证session_id长度
        if len(session_id) < 10:
            return False

        return True


def main():
    """
    主函数 - 演示如何使用
    """
    print("\n" + "=" * 60)
    print("喜马拉雅 xm-sign 签名生成器 (Node.js版本)")
    print("=" * 60 + "\n")

    # 创建签名生成器
    try:
        sign_generator = XimalayaSignNode()
    except Exception as e:
        print(f"[ERROR] 初始化失败: {e}")
        return

    # 生成xm-sign
    xm_sign = sign_generator.get_xm_sign()


if __name__ == "__main__":
    main()
