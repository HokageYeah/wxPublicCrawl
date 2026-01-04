"""
MCP Server 管理器
负责启动和停止本地 MCP Server
"""
import asyncio
import subprocess
import sys
import os
import socket
import signal
from typing import Optional
from loguru import logger
from pathlib import Path


class MCPServerManager:
    """MCP Server 管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.server_process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.host = "127.0.0.1"
        self.port = 8008
    
    @staticmethod
    def is_port_in_use(host: str, port: int) -> bool:
        """
        检查端口是否被占用
        
        Args:
            host: 主机地址
            port: 端口号
            
        Returns:
            bool: True表示端口被占用
        """
        # 使用 lsof 命令检查端口是否被占用（更准确）
        try:
            import subprocess as sp
            result = sp.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True,
                text=True,
                timeout=2
            )
            # 如果找到进程，说明端口被占用
            if result.returncode == 0 and result.stdout.strip():
                return True
            return False
        except Exception as e:
            logger.debug(f"lsof 检查失败，回退到 socket 检查: {e}")
            # 如果 lsof 失败，回退到 socket 方式
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    s.bind((host, port))
                    return False
                except OSError:
                    return True
    
    @staticmethod
    def kill_process_on_port(port: int) -> bool:
        """
        杀死占用指定端口的进程
        
        Args:
            port: 端口号
            
        Returns:
            bool: True表示成功清理了进程，False表示没有进程或清理失败
        """
        try:
            # 使用 lsof 查找占用端口的进程
            import subprocess as sp
            import time
            result = sp.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                logger.info(f"发现 {len(pids)} 个进程占用端口 {port}: {pids}")
                
                for pid in pids:
                    try:
                        pid_int = int(pid)
                        logger.info(f"正在终止占用端口 {port} 的进程 (PID: {pid_int})")
                        
                        # 先尝试 SIGTERM
                        os.kill(pid_int, signal.SIGTERM)
                        time.sleep(0.3)
                        
                        # 检查进程是否还存在
                        try:
                            os.kill(pid_int, 0)  # 0 信号只检查进程是否存在
                            # 进程还在，强制 SIGKILL
                            logger.warning(f"进程 {pid_int} 未响应 SIGTERM，使用 SIGKILL")
                            os.kill(pid_int, signal.SIGKILL)
                            time.sleep(0.2)
                        except ProcessLookupError:
                            # 进程已经终止
                            logger.info(f"✅ 进程 {pid_int} 已终止")
                            
                    except (ValueError, ProcessLookupError) as e:
                        logger.debug(f"进程 {pid} 已不存在或无效: {e}")
                    except PermissionError as e:
                        logger.error(f"没有权限终止进程 {pid}: {e}")
                        return False
                
                logger.info(f"✅ 已清理端口 {port} 上的所有进程")
                return True
            else:
                logger.debug(f"端口 {port} 当前未被任何进程占用")
                return False
                
        except Exception as e:
            logger.warning(f"清理端口 {port} 失败: {e}")
            return False
        
    def start_server(self, host: str = "127.0.0.1", port: int = 8008, transport: str = "streamable-http"):
        """
        启动 MCP Server（在独立进程中）
        
        Args:
            host: 服务器主机地址（默认使用 127.0.0.1 避免 IPv6 问题）
            port: 服务器端口
            transport: 传输方式
        """
        if self.is_running:
            logger.warning("MCP Server 已经在运行中")
            return
        
        # 保存服务器配置
        self.host = host
        self.port = port
        
        # 检查端口是否被占用
        import time
        if self.is_port_in_use(host, port):
            logger.warning(f"⚠️  端口 {port} 已被占用，尝试清理...")
            self.kill_process_on_port(port)
            
            # 等待端口释放（最多等待5秒）
            for i in range(10):
                time.sleep(0.5)
                if not self.is_port_in_use(host, port):
                    logger.info(f"✅ 端口 {port} 已释放")
                    break
            else:
                # 仍然被占用
                logger.error(f"❌ 端口 {port} 等待 5 秒后仍被占用，无法启动 MCP Server")
                return
        
        logger.info(f"🚀 启动 MCP Server - {transport}://{host}:{port}/mcp")
        
        try:
            # 检测是否在打包环境中
            if getattr(sys, '_MEIPASS', None):
                # 打包环境
                base_path = Path(sys._MEIPASS)
                server_script = base_path / "app" / "ai" / "mcp" / "mcp_server" / "run_server.py"
                python_exe = sys.executable
                logger.debug(f"打包环境 - Python: {python_exe}")
                logger.debug(f"打包环境 - Script: {server_script}")
                logger.debug(f"打包环境 - Script exists: {server_script.exists()}")
            else:
                # 开发环境
                server_script = Path(__file__).parent / "run_server.py"
                python_exe = sys.executable
                logger.debug(f"开发环境 - Python: {python_exe}")
                logger.debug(f"开发环境 - Script: {server_script}")
                logger.debug(f"开发环境 - Script exists: {server_script.exists()}")
            
            # 启动子进程
            self.server_process = subprocess.Popen(
                [python_exe, str(server_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=os.environ.copy(),
                # 在 macOS 打包环境中需要设置
                start_new_session=True
            )
            
            self.is_running = True
            
            # 等待服务器启动
            import time
            time.sleep(3)  # 等待3秒让服务器完全启动
            
            # 检查进程是否还在运行
            if self.server_process.poll() is not None:
                # 进程已退出
                stdout, stderr = self.server_process.communicate()
                logger.error(f"❌ MCP Server 启动失败")
                logger.error(f"STDOUT: {stdout.decode('utf-8', errors='ignore')}")
                logger.error(f"STDERR: {stderr.decode('utf-8', errors='ignore')}")
                self.is_running = False
                return
            
            logger.info(f"✅ MCP Server 启动成功 - 地址: http://{host}:{port}/mcp")
            logger.info(f"   进程 PID: {self.server_process.pid}")
            
        except Exception as e:
            logger.error(f"❌ 启动 MCP Server 失败: {e}", exc_info=True)
            self.is_running = False
    
    def stop_server(self):
        """停止 MCP Server"""
        if not self.is_running:
            logger.warning("MCP Server 未在运行")
            return
        
        logger.info("🛑 停止 MCP Server...")
        
        try:
            import time
            
            # 步骤1：终止进程
            if self.server_process and self.server_process.poll() is None:
                pid = self.server_process.pid
                logger.info(f"正在终止进程: {pid}")
                
                # 由于使用了 start_new_session=True，需要终止整个进程组
                try:
                    pgid = os.getpgid(pid)
                    logger.debug(f"进程组 ID: {pgid}")
                    
                    # 向整个进程组发送 SIGTERM 信号
                    os.killpg(pgid, signal.SIGTERM)
                    logger.info(f"已向进程组 {pgid} 发送 SIGTERM 信号")
                except (ProcessLookupError, PermissionError) as e:
                    logger.warning(f"无法终止进程组，回退到单进程终止: {e}")
                    self.server_process.terminate()
                
                # 等待进程结束（最多等待3秒）
                try:
                    self.server_process.wait(timeout=3.0)
                    logger.info(f"✅ 进程 {pid} 已正常退出")
                except subprocess.TimeoutExpired:
                    # 强制杀死
                    logger.warning(f"进程 {pid} 未响应 SIGTERM，强制终止...")
                    try:
                        pgid = os.getpgid(pid)
                        os.killpg(pgid, signal.SIGKILL)
                        logger.info(f"已向进程组 {pgid} 发送 SIGKILL 信号")
                    except (ProcessLookupError, PermissionError):
                        self.server_process.kill()
                    
                    # 再次等待
                    try:
                        self.server_process.wait(timeout=2.0)
                        logger.info(f"✅ 进程 {pid} 已被强制终止")
                    except subprocess.TimeoutExpired:
                        logger.error(f"❌ 无法终止进程 {pid}")
            else:
                logger.info("进程已经退出")
            
            # 步骤2：等待端口释放（给操作系统一些时间）
            logger.info(f"等待端口 {self.port} 释放...")
            time.sleep(1.0)  # 给系统一些时间释放端口
            
            # 步骤3：检查并清理端口
            port_released = False
            for attempt in range(6):  # 尝试6次，每次间隔0.5秒
                if not self.is_port_in_use(self.host, self.port):
                    logger.info(f"✅ 端口 {self.port} 已释放")
                    port_released = True
                    break
                    
                if attempt == 0:
                    # 第一次发现端口仍被占用，尝试清理
                    logger.warning(f"⚠️  端口 {self.port} 仍被占用，尝试清理...")
                    self.kill_process_on_port(self.port)
                
                # 等待后重试
                if attempt < 5:
                    time.sleep(0.5)
                    logger.debug(f"等待端口释放... (尝试 {attempt + 1}/6)")
            
            if not port_released:
                logger.error(f"❌ 端口 {self.port} 未能释放，可能需要手动清理")
            
            # 重置状态
            self.is_running = False
            self.server_process = None
            
            logger.info("✅ MCP Server 已停止")
            
        except Exception as e:
            logger.error(f"❌ 停止 MCP Server 失败: {e}", exc_info=True)
            # 即使出错也要重置状态
            self.is_running = False
            self.server_process = None
    
    def get_server_status(self) -> dict:
        """
        获取服务器状态
        
        Returns:
            dict: 服务器状态信息
        """
        process_running = False
        if self.server_process:
            process_running = self.server_process.poll() is None
        
        return {
            "is_running": self.is_running,
            "process_alive": process_running,
            "process_pid": self.server_process.pid if self.server_process else None
        }


# 全局单例
_mcp_server_manager: Optional[MCPServerManager] = None


def get_mcp_server_manager() -> MCPServerManager:
    """
    获取 MCP Server 管理器单例
    
    Returns:
        MCPServerManager: 管理器实例
    """
    global _mcp_server_manager
    
    if _mcp_server_manager is None:
        _mcp_server_manager = MCPServerManager()
    
    return _mcp_server_manager


async def start_local_mcp_server():
    """
    启动本地 MCP Server（异步函数，供 FastAPI lifespan 调用）
    """
    manager = get_mcp_server_manager()
    
    # 在后台线程中启动服务器
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,  # 使用默认线程池
        manager.start_server,
        "127.0.0.1",  # host - 使用 IPv4 避免冲突
        8008,         # port
        "streamable-http"  # transport
    )


async def stop_local_mcp_server():
    """
    停止本地 MCP Server（异步函数，供 FastAPI lifespan 调用）
    """
    manager = get_mcp_server_manager()
    
    # 在后台线程中停止服务器（已包含完整的清理逻辑）
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,  # 使用默认线程池
        manager.stop_server
    )
