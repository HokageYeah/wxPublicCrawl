import os
import sys
import platform

# ⚠️ 第一步：立即设置日志文件重定向
def setup_stdout_logging():
    """设置标准输出到日志文件"""
    if platform.system() == 'Darwin':  # Mac
        log_dir = os.path.expanduser('~/Library/Logs/wx公众号工具')
    elif platform.system() == 'Windows':
        log_dir = os.path.expanduser('~/AppData/Local/wx公众号工具/Logs')
    else:  # Linux
        log_dir = os.path.expanduser('~/.local/share/wx公众号工具/logs')
    
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建日志文件
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'app_{timestamp}.log')
    
    # 重定向 stdout 和 stderr
    sys.stdout = open(log_file, 'w', buffering=1)  # 行缓冲
    sys.stderr = sys.stdout
    
    print(f"日志文件: {log_file}")
    return log_file

# 立即设置日志
log_file = setup_stdout_logging()

# ⚠️ 关键：必须在导入 app 之前设置环境变量！
os.environ['ENV'] = 'desktop'

# ⚠️ 关键防护：阻止重复执行
if hasattr(sys, '_wx_crawler_running'):
    print(f"⚠️  检测到重复执行！PID: {os.getpid()}, 父进程: {os.getppid()}")
    sys.exit(0)
sys._wx_crawler_running = True

print(f"🔵 主程序启动 - PID: {os.getpid()}, 父进程: {os.getppid()}")

import threading
import socket
import time
import webview
import uvicorn
import signal

# 固定端口
PORT = 18000
# ✅ 全局变量保存服务器实例
uvicorn_server = None

def get_resource_path(relative_path):
    """获取资源文件的绝对路径(支持打包后)"""
    # 判断 是否有 _MEIPASS 属性，如果有则获取
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_lock_file_path():
    """获取锁文件路径"""
    if platform.system() == 'Darwin':
        lock_dir = os.path.expanduser('~/Library/Application Support/wx公众号工具')
    elif platform.system() == 'Windows':
        lock_dir = os.path.expanduser('~/AppData/Local/wx公众号工具')
    else:
        lock_dir = os.path.expanduser('~/.local/share/wx公众号工具')
    
    os.makedirs(lock_dir, exist_ok=True)
    return os.path.join(lock_dir, 'app.lock')

def is_port_in_use(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return False
        except socket.error:
            return True

def try_acquire_lock():
    """尝试获取单实例锁(跨平台)"""
    lock_file_path = get_lock_file_path()
    
    if os.path.exists(lock_file_path):
        try:
            with open(lock_file_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    os.remove(lock_file_path)
                else:
                    old_pid = int(content)
                    try:
                        os.kill(old_pid, 0)
                        return None
                    except (OSError, ProcessLookupError):
                        print(f"    清理僵尸锁文件(PID: {old_pid} 已不存在)")
                        os.remove(lock_file_path)
        except (ValueError, IOError) as e:
            print(f"    锁文件损坏,正在删除: {e}")
            try:
                os.remove(lock_file_path)
            except:
                pass
    
    try:
        with open(lock_file_path, 'w') as f:
            f.write(str(os.getpid()))
        return lock_file_path
    except Exception as e:
        print(f"⚠️  无法创建锁文件: {e}")
        return None

def start_server():
    """启动 FastAPI 服务器"""
    global uvicorn_server
    try:
        print(f"🔵 服务器线程启动 - 线程ID: {threading.current_thread().ident}")
        # 在这里导入，避免顶层导入触发问题
        from app.main import app
        
        # ✅ 创建 uvicorn 配置
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=PORT,
            log_level="info"
        )
        uvicorn_server = uvicorn.Server(config)
        uvicorn_server.run()
        
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()

def shutdown_server():
    """关闭 FastAPI 服务器"""
    global uvicorn_server
    
    print("正在关闭 FastAPI 服务器...")
    
    if uvicorn_server is not None:
        try:
            # ✅ 正确的关闭方式：设置 should_exit 标志
            uvicorn_server.should_exit = True
            print("✓ FastAPI 服务器关闭信号已发送")
        except Exception as e:
            print(f"⚠️  关闭服务器时出错: {e}")
    else:
        print("⚠️  服务器实例不存在")

def on_closed():
    """窗口关闭事件"""
    print("\n" + "=" * 60)
    print("应用窗口已关闭,正在清理...")
    print("=" * 60)
    
    # ✅ 关闭 FastAPI 服务器
    shutdown_server()
    
    # 清理锁文件
    lock_file_path = get_lock_file_path()
    if os.path.exists(lock_file_path):
        try:
            os.remove(lock_file_path)
            print("✓ 锁文件已清理")
        except Exception as e:
            print(f"⚠️  清理锁文件失败: {e}")
    
    print("正在退出...")
    
    # 确保日志文件被刷新
    sys.stdout.flush()
    sys.stderr.flush()
    
    # 等待一小段时间，让服务器完成关闭
    time.sleep(0.5)
    
    print("=" * 60)
    print("✓ 应用已完全关闭")
    print("=" * 60)
    
    # 强制退出
    os._exit(0)

def main():
    """主函数"""
    print("=" * 60)
    print("公众号爬虫助手 - 桌面版")
    print("=" * 60)
    print(f"日志文件位置: {log_file}")
    print("")
    
    # 1. 检查是否已有实例在运行
    print("\n[1/4] 检查应用实例...")
    lock_file_path = try_acquire_lock()
    
    if lock_file_path is None:
        print("⚠️  检测到应用已在运行")
        
        if is_port_in_use(PORT):
            print(f"✓  服务器正在运行在 http://127.0.0.1:{PORT}")
            print("\n⚠️  应用已经在运行,请检查任务栏或停靠栏。")
            print("    如果看不到窗口,请尝试以下操作:")
            print(f"    1. 关闭其他实例")
            print(f"    2. 使用命令终止: lsof -ti:{PORT} | xargs kill -9")
            time.sleep(5)  # 给用户时间看到消息
            sys.exit(0)
        else:
            print("✗  锁文件检测异常,请手动清理")
            print(f"    运行: rm '{get_lock_file_path()}'")
            time.sleep(5)
            sys.exit(1)
    
    print("✓  没有其他实例在运行")
    
    # 2. 检查端口是否可用
    print("\n[2/4] 检查端口可用性...")
    if is_port_in_use(PORT):
        print(f"✗  端口 {PORT} 已被占用")
        print(f"\n请关闭占用端口的程序,或使用以下命令:")
        print(f"    lsof -ti:{PORT} | xargs kill -9")
        time.sleep(5)
        sys.exit(1)
    
    print(f"✓  端口 {PORT} 可用")
    
    # 3. 启动 FastAPI 服务器
    print("\n[3/4] 启动后端服务器...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    max_wait = 30
    waited = 0
    while waited < max_wait:
        if is_port_in_use(PORT):
            print(f"✓  服务器启动成功 (http://127.0.0.1:{PORT})")
            break
        time.sleep(0.5)
        waited += 0.5
    else:
        print("✗  服务器启动超时")
        time.sleep(5)
        sys.exit(1)
    
    # 4. 创建并启动 WebView 窗口
    print("\n[4/4] 启动应用窗口...")
    try:
        window = webview.create_window(
            '公众号爬虫助手', 
            f'http://127.0.0.1:{PORT}/crawl-desktop/',
            width=1280,
            height=1000,
            resizable=True
        )
        
        window.events.closed += on_closed
        
        print("✓  应用窗口已创建")
        print("\n" + "=" * 60)
        print("应用已启动,欢迎使用!")
        print("=" * 60 + "\n")
        
        # 刷新日志
        sys.stdout.flush()
        sys.stderr.flush()
        
        webview.start()
        
    except Exception as e:
        print(f"✗  窗口创建失败: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(5)
        sys.exit(1)
    finally:
        if lock_file_path and os.path.exists(lock_file_path):
            try:
                os.remove(lock_file_path)
                print("\n✓ 锁文件已清理（finally 块）")
            except:
                pass
        
        # 确保日志被写入
        sys.stdout.flush()
        sys.stderr.flush()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断,正在退出...")
        shutdown_server()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(10)  # 给用户时间看到错误
        sys.exit(1)
    finally:
        # 确保所有输出都被写入
        sys.stdout.flush()
        sys.stderr.flush()