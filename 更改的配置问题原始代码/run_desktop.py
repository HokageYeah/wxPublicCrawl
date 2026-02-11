import os
import sys

# ⚠️ 关键：必须在导入 app 之前设置环境变量！
# 否则 config.py 已经被加载，环境变量不会生效
os.environ['DB_DRIVER'] = 'sqlite'
os.environ['ENV'] = 'desktop'

import threading
import socket
import time
import webview
import uvicorn
from app.main import app
import platform
import multiprocessing

# ⚠️ 关键：PyInstaller 多进程支持
# 防止子进程重复执行主程序
multiprocessing.freeze_support()

# 固定端口
PORT = 18000

def get_lock_file_path():
    """获取锁文件路径"""
    if platform.system() == 'Darwin':  # Mac
        lock_dir = os.path.expanduser('~/Library/Application Support/wx公众号工具')
    elif platform.system() == 'Windows':
        lock_dir = os.path.expanduser('~/AppData/Local/wx公众号工具')
    else:  # Linux
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
    """尝试获取单实例锁（跨平台）"""
    lock_file_path = get_lock_file_path()
    
    # 如果锁文件存在，检查进程是否还在运行
    if os.path.exists(lock_file_path):
        try:
            with open(lock_file_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    # 空文件，删除它
                    os.remove(lock_file_path)
                else:
                    old_pid = int(content)
                    
                    # 检查进程是否还在运行
                    try:
                        os.kill(old_pid, 0)  # 发送信号 0 只检查不杀死
                        # 进程存在，说明已有实例在运行
                        return None
                    except (OSError, ProcessLookupError):
                        # 进程不存在，删除旧的锁文件
                        print(f"    清理僵尸锁文件（PID: {old_pid} 已不存在）")
                        os.remove(lock_file_path)
        except (ValueError, IOError) as e:
            # 锁文件损坏，删除它
            print(f"    锁文件损坏，正在删除: {e}")
            try:
                os.remove(lock_file_path)
            except:
                pass
    
    # 创建新的锁文件
    try:
        with open(lock_file_path, 'w') as f:
            f.write(str(os.getpid()))
        return lock_file_path
    except Exception as e:
        print(f"⚠️  无法创建锁文件: {e}")
        return None

def start_server():
    """启动 FastAPI 服务器"""
    try:
        uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
    except Exception as e:
        print(f"服务器启动失败: {e}")
        # 不要在这里调用 os._exit()，让主线程处理

def on_closed():
    """窗口关闭事件"""
    print("应用窗口已关闭，正在清理...")
    
    # 清理锁文件
    lock_file_path = get_lock_file_path()
    if os.path.exists(lock_file_path):
        try:
            os.remove(lock_file_path)
            print("锁文件已清理")
        except:
            pass
    
    print("正在退出...")
    os._exit(0)

def main():
    """主函数"""
    print("=" * 60)
    print("公众号爬虫助手 - 桌面版")
    print("=" * 60)
    
    # 1. 检查是否已有实例在运行
    print("\n[1/4] 检查应用实例...")
    lock_file_path = try_acquire_lock()
    
    if lock_file_path is None:
        print("⚠️  检测到应用已在运行")
        
        # 检查端口是否被占用
        if is_port_in_use(PORT):
            print(f"✓  服务器正在运行在 http://127.0.0.1:{PORT}")
            print("\n⚠️  应用已经在运行，请检查任务栏或停靠栏。")
            print("    如果看不到窗口，请尝试以下操作：")
            print(f"    1. 关闭其他实例")
            print(f"    2. 使用命令终止: lsof -ti:{PORT} | xargs kill -9")
            print(f"    3. 或运行清理脚本: ./kill_app.sh")
            input("\n按回车键退出...")
            sys.exit(0)
        else:
            # 端口没有被占用，但lock返回None，说明清理失败
            print("✗  锁文件检测异常，请手动清理")
            print(f"    运行: rm '{get_lock_file_path()}'")
            input("\n按回车键退出...")
            sys.exit(1)
    
    print("✓  没有其他实例在运行")
    
    # 2. 检查端口是否可用
    print("\n[2/4] 检查端口可用性...")
    if is_port_in_use(PORT):
        print(f"✗  端口 {PORT} 已被占用")
        print(f"\n请关闭占用端口的程序，或使用以下命令查找并关闭:")
        print(f"    lsof -ti:{PORT} | xargs kill -9")
        input("\n按回车键退出...")
        sys.exit(1)
    
    print(f"✓  端口 {PORT} 可用")
    
    # 3. 启动 FastAPI 服务器
    print("\n[3/4] 启动后端服务器...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    max_wait = 10  # 最多等待10秒
    waited = 0
    while waited < max_wait:
        if is_port_in_use(PORT):
            print(f"✓  服务器启动成功 (http://127.0.0.1:{PORT})")
            break
        time.sleep(0.5)
        waited += 0.5
    else:
        print("✗  服务器启动超时")
        sys.exit(1)
    
    # 4. 创建并启动 WebView 窗口
    print("\n[4/4] 启动应用窗口...")
    try:
        window = webview.create_window(
            '公众号爬虫助手', 
            f'http://127.0.0.1:{PORT}/crawl-desktop/',
            width=1280,
            height=800,
            resizable=True
        )
        
        window.events.closed += on_closed
        
        print("✓  应用窗口已创建")
        print("\n" + "=" * 60)
        print("应用已启动，欢迎使用！")
        print("=" * 60 + "\n")
        
        webview.start()
        
    except Exception as e:
        print(f"✗  窗口创建失败: {e}")
        sys.exit(1)
    finally:
        # 清理锁文件
        if lock_file_path and os.path.exists(lock_file_path):
            try:
                os.remove(lock_file_path)
                print("\n锁文件已清理")
            except:
                pass

if __name__ == '__main__':
    # ⚠️ 重要：设置多进程启动方法为 'spawn'
    # 这对于 PyInstaller 打包的应用很重要
    if platform.system() == 'Darwin':  # macOS
        try:
            multiprocessing.set_start_method('spawn', force=True)
        except RuntimeError:
            pass  # 已经设置过了
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断，正在退出...")
        sys.exit(0)
    except Exception as e:
        print(f"\n应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
        sys.exit(1)
