# MCP服务启动方式优化 - 从线程改为进程

## 🐛 问题分析

### 原始问题

桌面端打包后，MCP服务无法正常启动，客户端连接超时。

### 错误日志

```
ERROR: [Errno 48] error while attempting to bind on address ('127.0.0.1', 8008): [errno 48] address already in use
✗  服务器启动超时
```

### 根本原因

**Uvicorn 实例冲突**：

1. **主应用** (`run_desktop.py`) 使用 Uvicorn 运行 FastAPI
2. **MCP Server** (`fastmcp_server.py`) 的 `run()` 方法内部也启动了 Uvicorn
3. **在同一进程中**，两个 Uvicorn 尝试绑定同一个端口 8008 → 冲突

#### 为什么开发环境没问题？

- 开发环境运行 `python run_app.py` 时，主应用和 MCP Server 不在同一个进程
- 打包后，所有代码运行在同一个进程中，导致冲突

### 架构问题

```
原有架构（线程）:
┌─────────────────────────────────────┐
│  主进程 (PID: 58923)                │
│                                     │
│  ┌─────────────────┐                │
│  │ 主应用 Uvicorn  │                │
│  │ Port: 18000     │                │
│  └─────────────────┘                │
│                                     │
│  ┌─────────────────┐                │
│  │ MCP Server 线程 │                │
│  │ 尝试启动 Uvicorn│  ❌ 冲突！     │
│  │ Port: 8008      │                │
│  └─────────────────┘                │
│                                     │
└─────────────────────────────────────┘

问题：同一进程中不能启动两个 Uvicorn 实例
```

## ✅ 解决方案

### 核心思路

**将 MCP Server 从线程改为独立进程启动**

```
新架构（进程）:
┌─────────────────────────────────────┐
│  主进程 (PID: 58923)                │
│                                     │
│  ┌─────────────────┐                │
│  │ 主应用 Uvicorn  │                │
│  │ Port: 18000     │                │
│  └─────────────────┘                │
│                                     │
│  创建子进程 ↓                       │
└─────────────┼───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  子进程 (PID: 59001)                │
│                                     │
│  ┌─────────────────┐                │
│  │ MCP Server      │                │
│  │ 独立 Uvicorn    │  ✅ 独立进程  │
│  │ Port: 8008      │                │
│  └─────────────────┘                │
│                                     │
└─────────────────────────────────────┘

优势：完全隔离，无冲突
```

### 具体修改

#### 1. 修改 `server_manager.py`

**修改前（线程方式）：**
```python
import threading
from app.ai.mcp.mcp_server.fastmcp_server import FastmcpServer

class MCPServerManager:
    def __init__(self):
        self.server: Optional[FastmcpServer] = None
        self.server_thread: Optional[threading.Thread] = None
    
    def start_server(self, ...):
        self.server = FastmcpServer()
        self.server_thread = threading.Thread(
            target=self._run_server_in_thread,
            daemon=True
        )
        self.server_thread.start()
    
    def _run_server_in_thread(self, ...):
        self.server.run(...)  # ❌ 在主进程中启动 Uvicorn
```

**修改后（进程方式）：**
```python
import subprocess
from pathlib import Path

class MCPServerManager:
    def __init__(self):
        self.server_process: Optional[subprocess.Popen] = None
    
    def start_server(self, ...):
        # 获取 run_server.py 脚本路径
        if getattr(sys, '_MEIPASS', None):
            # 打包环境
            base_path = Path(sys._MEIPASS)
            server_script = base_path / "app" / "ai" / "mcp" / "mcp_server" / "run_server.py"
        else:
            # 开发环境
            server_script = Path(__file__).parent / "run_server.py"
        
        # 启动子进程 ✅
        self.server_process = subprocess.Popen(
            [sys.executable, str(server_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True  # 独立会话
        )
```

#### 2. 停止方式变更

**修改前（线程）：**
```python
def stop_server(self):
    if self.server_thread and self.server_thread.is_alive():
        self.server_thread.join(timeout=5.0)
```

**修改后（进程）：**
```python
def stop_server(self):
    if self.server_process and self.server_process.poll() is None:
        self.server_process.terminate()  # 优雅终止
        try:
            self.server_process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            self.server_process.kill()  # 强制杀死
```

#### 3. 状态检查变更

**修改前：**
```python
def get_server_status(self):
    return {
        "thread_alive": self.server_thread.is_alive(),
        "server_name": self.server.server.name
    }
```

**修改后：**
```python
def get_server_status(self):
    process_running = False
    if self.server_process:
        process_running = self.server_process.poll() is None
    
    return {
        "process_alive": process_running,
        "process_pid": self.server_process.pid
    }
```

## 🎯 优势对比

| 特性 | 线程方式 | 进程方式（新） |
|------|---------|--------------|
| **隔离性** | ❌ 共享内存空间 | ✅ 完全隔离 |
| **Uvicorn冲突** | ❌ 会冲突 | ✅ 不会冲突 |
| **崩溃影响** | ❌ 影响主进程 | ✅ 不影响主进程 |
| **资源管理** | ❌ 难以控制 | ✅ 易于管理 |
| **调试** | ❌ 难以调试 | ✅ 独立日志 |
| **打包兼容** | ❌ 不兼容 | ✅ 完全兼容 |

## 📊 启动流程

### 新流程图

```
应用启动
    ↓
main.py: lifespan
    ↓
start_local_mcp_server() (异步)
    ↓
MCPServerManager.start_server()
    ↓
1. 检测环境（打包/开发）
    ↓
2. 定位 run_server.py 脚本
    ↓
3. 使用 subprocess.Popen 启动
    ↓
4. 等待 3 秒
    ↓
5. 检查进程状态
    ↓
✅ MCP Server 在独立进程中运行
    ↓
客户端连接 (成功)
```

## 🔍 打包环境路径处理

### 关键代码

```python
if getattr(sys, '_MEIPASS', None):
    # 打包环境：从临时目录读取
    base_path = Path(sys._MEIPASS)
    server_script = base_path / "app" / "ai" / "mcp" / "mcp_server" / "run_server.py"
else:
    # 开发环境：相对路径
    server_script = Path(__file__).parent / "run_server.py"
```

### 为什么这样处理？

PyInstaller 打包后：
- 所有文件解压到 `sys._MEIPASS` 临时目录
- `__file__` 指向的是打包前的路径（不存在）
- 必须使用 `sys._MEIPASS` 来定位资源

## 🧪 测试验证

### 测试步骤

1. **重新打包应用**
   ```bash
   rm -rf dist/ build/
   python build_desktop.py
   ```

2. **启动桌面应用**
   ```bash
   open dist/wx公众号工具.app
   ```

3. **检查日志**
   
   **应该看到：**
   ```
   🚀 启动 MCP Server - streamable-http://127.0.0.1:8008/mcp
   ✅ MCP Server 启动成功 - 地址: http://127.0.0.1:8008/mcp
      进程 PID: 59001
   ✅ MCP客户端管理器初始化成功
   ```
   
   **不应该看到：**
   ```
   ❌ ERROR: [Errno 48] address already in use
   ❌ 服务器启动超时
   ```

4. **测试功能**
   - 在应用中测试 AI 查询
   - 例如："查询北京的天气"
   - 应该能正常调用工具

### 验证点

- [ ] 主应用正常启动（端口 18000）
- [ ] MCP Server 独立进程启动（端口 8008）
- [ ] 客户端成功连接到 MCP Server
- [ ] 工具调用功能正常
- [ ] 应用退出时，子进程正常终止

## 🔧 调试技巧

### 查看进程

```bash
# 查看主进程
ps aux | grep "wx公众号工具"

# 查看 MCP Server 进程
ps aux | grep "run_server.py"

# 查看端口占用
lsof -i :8008
lsof -i :18000
```

### 日志位置

- **主应用日志**: `~/Library/Logs/wx公众号工具/app_YYYYMMDD_HHMMSS.log`
- **MCP Server 日志**: 通过 `subprocess.PIPE` 捕获

### 手动测试 MCP Server

```bash
# 单独启动 MCP Server
cd /path/to/wxPublicCrawl
python app/ai/mcp/mcp_server/run_server.py

# 应该看到
Starting MCP server 'fastmcp_demo_server' with transport 'streamable-http' on http://127.0.0.1:8008/mcp
```

## 🚨 可能的问题

### 问题1: 子进程无法启动

**症状：**
```
❌ MCP Server 启动失败
STDERR: ModuleNotFoundError: No module named 'app'
```

**原因：** 打包环境中，`run_server.py` 找不到 `app` 模块

**解决：** 确保 `run_server.py` 正确设置 `sys.path`

```python
# run_server.py
import sys
from pathlib import Path

# 添加项目根目录到路径
if getattr(sys, '_MEIPASS', None):
    # 打包环境
    project_root = Path(sys._MEIPASS)
else:
    # 开发环境
    project_root = Path(__file__).resolve().parent.parent.parent.parent

sys.path.insert(0, str(project_root))
```

### 问题2: 进程无法终止

**症状：** 关闭应用后，MCP Server 进程仍在运行

**解决：** 使用 `start_new_session=True` 确保子进程在独立会话中

### 问题3: 端口仍然冲突

**症状：** 仍然显示端口被占用

**检查：**
```bash
# 杀死所有占用 8008 的进程
lsof -ti:8008 | xargs kill -9
```

## 📚 相关代码

| 文件 | 修改内容 |
|------|---------|
| `app/ai/mcp/mcp_server/server_manager.py` | ✅ 线程改进程 |
| `app/ai/mcp/mcp_client/mcp_settings.json` | ✅ URL 改为 127.0.0.1 |
| `app/main.py` | 无需修改 |

## ✨ 总结

### 关键修改

1. ✅ **启动方式**: 线程 → 独立进程
2. ✅ **隔离性**: 完全隔离 Uvicorn 实例
3. ✅ **路径处理**: 正确处理打包环境路径
4. ✅ **进程管理**: `subprocess.Popen` + 优雅终止

### 效果

- 解决 Uvicorn 实例冲突
- 解决端口占用问题
- 提高系统稳定性
- 便于调试和监控

---

**修复日期：** 2025-12-31  
**问题类型：** 打包环境进程架构  
**影响范围：** 桌面端 MCP Server 启动

