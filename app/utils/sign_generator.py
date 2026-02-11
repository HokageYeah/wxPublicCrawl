"""
使用Node.js调用JIMI.JS生成xm-sign
这是最简单、最可靠的方式
"""

import subprocess
import platform
import json
import os
import sys
from loguru import logger


def get_node_executable():
    """
    获取 Node.js 可执行文件路径
    
    在打包环境中，使用内置的 Node.js
    在开发环境中，使用系统的 node 命令
    """
    # 检测是否在 PyInstaller 打包环境中
    if getattr(sys, 'frozen', False):
        # 打包环境
        if platform.system() == 'Darwin':
            # macOS: .app/Contents/Frameworks/nodejs/node
            bundle_dir = sys._MEIPASS
            node_path = os.path.join(bundle_dir, 'nodejs', 'node')
        elif platform.system() == 'Windows':
            # Windows: 应用目录/nodejs/node.exe
            bundle_dir = sys._MEIPASS
            node_path = os.path.join(bundle_dir, 'nodejs', 'node.exe')
        else:
            # Linux
            bundle_dir = sys._MEIPASS
            node_path = os.path.join(bundle_dir, 'nodejs', 'node')
        
        logger.info(f"🔧 打包环境 - Node.js 路径: {node_path}")
        logger.info(f"🔧 Bundle 目录: {bundle_dir}")
        
        # 列出 bundle_dir 中的文件（用于调试）
        try:
            if os.path.exists(bundle_dir):
                logger.info(f"🔍 Bundle 目录内容:")
                for item in os.listdir(bundle_dir):
                    logger.info(f"  - {item}")
                
                # 检查 nodejs 目录是否存在
                nodejs_dir = os.path.join(bundle_dir, 'nodejs')
                if os.path.exists(nodejs_dir):
                    logger.info(f"🔍 nodejs 目录内容:")
                    for item in os.listdir(nodejs_dir):
                        logger.info(f"  - {item}")
        except Exception as e:
            logger.warning(f"⚠️ 无法列出目录内容: {e}")
        
        # 检查文件是否存在
        if os.path.exists(node_path):
            # 在 macOS/Linux 上，确保可执行权限
            if platform.system() != 'Windows':
                try:
                    os.chmod(node_path, 0o755)
                    logger.info(f"✅ 已设置 Node.js 可执行权限")
                except Exception as e:
                    logger.warning(f"⚠️ 无法设置可执行权限: {e}")
            return node_path
        else:
            logger.error(f"❌ 打包的 Node.js 不存在: {node_path}")
            logger.error(f"❌ 请检查打包配置是否正确")
            return 'node'  # 回退到系统 node
    else:
        # 开发环境，使用系统的 node 命令
        logger.info("🔧 开发环境 - 使用系统 Node.js")
        return 'node'


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
        # 获取 Node.js 可执行文件路径
        self.node_executable = get_node_executable()
        logger.info(f"Node.js 可执行文件: {self.node_executable}")
        
        # 获取JIMI.JS的路径
        # 在打包环境中，JS 文件会被打包到 _MEIPASS 目录
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
            self.jimi_js_path = os.path.join(base_dir, 'app', 'utils', 'js-code', 'JIMI.JS')
            logger.info(f"🔧 打包环境 - JIMI.JS 路径: {self.jimi_js_path}")
        else:
            self.jimi_js_path = os.path.join(os.path.dirname(__file__),'js-code' ,'JIMI.JS')
            logger.info(f"🔧 开发环境 - JIMI.JS 路径: {self.jimi_js_path}")
        
        self.is_available = False  # 签名生成器是否可用

        # 检查JIMI.JS是否存在
        if not os.path.exists(self.jimi_js_path):
            logger.error(f"❌ JIMI.JS文件不存在: {self.jimi_js_path}")
            self.error_message = f"JIMI.JS 文件不存在: {self.jimi_js_path}"
            return

        # 检查Node.js是否安装及版本
        try:
            # 首先检查 Node.js 可执行文件是否存在
            if not os.path.exists(self.node_executable) and self.node_executable != 'node':
                logger.error(f"❌ Node.js 可执行文件不存在: {self.node_executable}")
                self.is_available = False
                self.error_message = f"Node.js 可执行文件不存在: {self.node_executable}"
                return
            
            # 检测架构是否匹配（仅 macOS）
            is_packaged = getattr(sys, 'frozen', False)
            if is_packaged and platform.system() == 'Darwin':
                import subprocess as sp
                try:
                    # 检查 node 二进制文件的架构
                    file_result = sp.run(
                        ['file', self.node_executable],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if file_result.returncode == 0:
                        logger.info(f"📋 Node.js 二进制架构: {file_result.stdout.strip()}")
                        
                        # 检查系统架构
                        system_arch = platform.machine()
                        logger.info(f"📋 系统架构: {system_arch}")
                        
                        # 如果是 x86_64 node 在 arm64 系统上，给出警告并增加超时
                        if system_arch == 'arm64' and 'x86_64' in file_result.stdout:
                            logger.warning("⚠️ Node.js 架构不匹配（x86_64 vs arm64）")
                            logger.warning("⚠️ 将通过 Rosetta 2 运行，首次执行可能较慢")
                except Exception as e:
                    logger.debug(f"无法检测架构: {e}")
            
            # 增加超时时间，特别是对于打包环境的首次执行
            # x86_64 在 arm64 上通过 Rosetta 2 首次运行可能需要 15-20 秒
            timeout_seconds = 30 if is_packaged else 5
            
            logger.info(f"🔍 检查 Node.js 版本（超时: {timeout_seconds}秒）...")
            result = subprocess.run(
                [self.node_executable, '--version'],
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout_seconds
            )
            version_string = result.stdout.strip()
            self.node_version = parse_node_version(version_string)
            self.node_version_string = version_string
            
            logger.info(f"✅ Node.js 版本: {version_string}")
            
            # 检查版本是否满足要求
            system = platform.system().lower()
            min_version = 20  # 默认 (Linux/macOS) 需要 20+
            
            if system == 'windows':
                min_version = 14
            
            if self.node_version[0] < min_version:
                logger.warning(f"⚠️ Node.js 版本低于 {min_version}.0")
                logger.warning(f"⚠️ 当前系统 ({system}) JIMI.JS 需要 Node.js {min_version}.0 或更高版本")
                logger.warning("⚠️ 签名生成器将被禁用")
                logger.info("💡 升级 Node.js: https://nodejs.org/")
                if min_version == 18:
                    logger.info(f"💡 或使用 nvm: nvm install {min_version} && nvm use {min_version}")
                self.is_available = False
                self.error_message = f"Node.js 版本过低（{version_string}），当前系统需要 {min_version}.0 或更高版本。请升级 Node.js：https://nodejs.org/"
            else:
                logger.info("✅ Node.js 版本满足要求，签名生成器可用")
                self.is_available = True
                self.error_message = None
                
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            is_packaged = getattr(sys, 'frozen', False)
            if is_packaged:
                logger.error("❌ 打包的 Node.js 不可用")
                logger.error(f"❌ Node.js 路径: {self.node_executable}")
                logger.error("❌ 这可能是打包配置问题，请联系开发者")
                self.error_message = f"打包的 Node.js 不可用 ({self.node_executable})"
            else:
                logger.error("❌ Node.js 未安装或不在 PATH 中")
                logger.error("💡 请先安装 Node.js: https://nodejs.org/")
                self.error_message = "Node.js 未安装，请先安装 Node.js：https://nodejs.org/"
            self.is_available = False
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
            print(f"Node.js: {self.node_executable}")
            print(f"JIMI.JS: {self.jimi_js_path}")
            print("=" * 60)

            # 在打包环境且架构不匹配时，增加超时时间
            is_packaged = getattr(sys, 'frozen', False)
            timeout_seconds = 60 if is_packaged else 30
            
            logger.info(f"⏱️  执行超时设置: {timeout_seconds}秒")

            # 执行Node.js脚本
            result = subprocess.run(
                [self.node_executable, self.jimi_js_path],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
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
