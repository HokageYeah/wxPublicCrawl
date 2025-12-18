import os
import sys
import threading
import socket
import time
import webview
import uvicorn
from app.main import app

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

# 使用固定端口还是动态端口？目前为了匹配 main.py 中的配置，使用固定端口最简单。
# 但是 main.py 挂载了静态文件，所以只要 webview 知道端口号，使用什么端口并不重要。
PORT = 18000

def start_server():
    # 启动服务器
    # workers=1 因为我们在线程中运行
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")

def on_closed():
    print("Application closed")
    os._exit(0)

if __name__ == '__main__':
    # 在后台线程中启动 API 服务器
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    # 等待一会儿让服务器启动，或者依赖 webview 的重试机制（webview 通常不会自动重试）
    # 简单的等待
    time.sleep(1)

    # 创建窗口
    # URL 应该是 http://127.0.0.1:18000/
    # 如果静态文件挂载在 /，这将服务 index.html
    window = webview.create_window(
        '公众号爬虫助手', 
        f'http://127.0.0.1:{PORT}/crawl-desktop/',
        width=1280,
        height=800,
        resizable=True
    )
    
    # 绑定关闭事件
    window.events.closed += on_closed
    
    webview.start()
