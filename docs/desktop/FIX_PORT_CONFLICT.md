# 修复端口冲突和循环启动问题

## 问题描述

打包后的应用出现循环启动，错误信息：
```
ERROR: [Errno 48] error while attempting to bind on address ('127.0.0.1', 18000): address already in use
```

## 根本原因

1. **端口被占用**: 第一次启动后服务器已占用端口 18000
2. **无单实例检测**: 应用允许多个实例同时启动
3. **循环启动**: 新实例启动失败后又触发新的启动

## ✅ 解决方案

### 1. 修复 `run_desktop.py`

添加了以下功能：

#### a) 单实例锁机制

```python
def try_acquire_lock():
    """尝试获取单实例锁（跨平台）"""
    # 检查锁文件和进程是否存在
    # 防止多个实例同时运行
```

**锁文件位置**:
- Mac: `~/Library/Application Support/wx公众号工具/app.lock`
- Windows: `%APPDATA%\Local\wx公众号工具\app.lock`

#### b) 端口检测

```python
def is_port_in_use(port):
    """检查端口是否被占用"""
```

在启动前检查端口 18000 是否可用。

#### c) 智能启动逻辑

```python
def main():
    # 1. 检查是否已有实例在运行
    # 2. 检查端口可用性
    # 3. 启动服务器
    # 4. 创建窗口
```

#### d) 清理机制

- 窗口关闭时自动清理锁文件
- 应用退出时释放端口

### 2. 创建清理脚本 `kill_app.sh`

用于手动终止运行中的实例和清理锁文件。

## 🚀 立即修复步骤

### 步骤 1: 终止现有实例

```bash
cd "/Users/yuye/YeahWork/Python项目/wxPublicCrawl"

# 运行清理脚本
./kill_app.sh

# 或手动终止
lsof -ti:18000 | xargs kill -9
rm ~/Library/Application\ Support/wx公众号工具/app.lock
```

### 步骤 2: 清理并重新打包

```bash
# 清理旧的打包文件
chmod -R 755 dist 2>/dev/null || true
rm -rf dist build

# 重新打包
./build_mac.sh
```

### 步骤 3: 测试新版本

```bash
# 方式 1: 查看详细日志（推荐）
./dist/wx公众号工具/wx公众号工具

# 方式 2: 打开应用
open dist/wx公众号工具.app 
```

## ✅ 预期的成功输出

如果修复成功，你应该看到：

```
============================================================
公众号爬虫助手 - 桌面版
============================================================

[1/4] 检查应用实例...
✓  没有其他实例在运行

[2/4] 检查端口可用性...
✓  端口 18000 可用

[3/4] 启动后端服务器...
当前环境: development
配置文件 .env 不存在，使用默认配置
...
数据库连接成功 - 数据库类型: SQLite
SQLite 数据库表结构已创建
INFO:     Uvicorn running on http://127.0.0.1:18000
✓  服务器启动成功 (http://127.0.0.1:18000)

[4/4] 启动应用窗口...
✓  应用窗口已创建

============================================================
应用已启动，欢迎使用！
============================================================
```

然后浏览器窗口打开显示应用界面。

## 🔍 新功能说明

### 1. 单实例保护

- **第一次启动**: 正常启动服务器和窗口
- **重复启动**: 检测到已有实例，显示提示并退出
- **异常退出**: 自动清理遗留的锁文件，允许重新启动

### 2. 端口冲突检测

- 启动前检查端口是否被占用
- 如果被占用，显示清理命令并退出
- 避免循环启动

### 3. 优雅退出

- 窗口关闭时自动清理锁文件
- 确保下次可以正常启动

## 🐛 故障排除

### 问题 1: "应用已在运行"但看不到窗口

**原因**: 上次异常退出留下了锁文件或进程

**解决**:
```bash
# 运行清理脚本
./kill_app.sh

# 或手动清理
lsof -ti:18000 | xargs kill -9
rm ~/Library/Application\ Support/wx公众号工具/app.lock
```

### 问题 2: 端口被其他程序占用

**查找占用端口的程序**:
```bash
lsof -i:18000
```

**终止占用端口的程序**:
```bash
lsof -ti:18000 | xargs kill -9
```

**或更改端口**（修改 `run_desktop.py` 中的 `PORT` 变量）

### 问题 3: 锁文件无法删除

```bash
# 检查权限
ls -la ~/Library/Application\ Support/wx公众号工具/

# 强制删除
sudo rm ~/Library/Application\ Support/wx公众号工具/app.lock
```

### 问题 4: 窗口打开后立即关闭

**查看详细日志**:
```bash
./dist/wx公众号工具/wx公众号工具
```

检查是否有错误信息（数据库、权限等）

## 📋 测试清单

重新打包后测试：

- [ ] 应用可以正常启动
- [ ] 窗口正确显示
- [ ] 尝试再次启动，应显示"已在运行"提示
- [ ] 关闭窗口，应用正常退出
- [ ] 可以再次启动（锁文件已清理）
- [ ] 端口 18000 在退出后被释放

## 🔧 手动清理命令速查

```bash
# 查看占用端口 18000 的进程
lsof -i:18000

# 终止占用端口的进程
lsof -ti:18000 | xargs kill -9

# 删除锁文件 (Mac)
rm ~/Library/Application\ Support/wx公众号工具/app.lock

# 删除锁文件 (Windows PowerShell)
Remove-Item "$env:LOCALAPPDATA\wx公众号工具\app.lock"

# 查看所有相关进程
ps aux | grep wx公众号工具

# 终止所有相关进程
pkill -f wx公众号工具
```

## 📚 技术细节

### 单实例锁实现

**跨平台方案**:
- 使用 PID 文件而不是文件锁（避免 Windows/Mac 差异）
- 检查进程是否存在（`os.kill(pid, 0)`）
- 自动清理僵尸锁文件

**优点**:
- ✅ 跨平台兼容（Mac, Windows, Linux）
- ✅ 可靠性高
- ✅ 自动恢复（处理异常退出）

### 端口检测

使用 socket 绑定测试：
```python
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.bind(('127.0.0.1', port))
        return False  # 端口可用
    except socket.error:
        return True   # 端口被占用
```

## 📝 代码改进总结

| 改进项 | 修复前 | 修复后 |
|--------|--------|--------|
| 多实例检测 | ❌ 无 | ✅ 单实例锁 |
| 端口检测 | ❌ 无 | ✅ 启动前检测 |
| 错误处理 | ❌ 循环启动 | ✅ 友好提示并退出 |
| 清理机制 | ❌ 无 | ✅ 自动清理锁文件 |
| 用户体验 | ❌ 混乱 | ✅ 清晰的启动步骤 |

## ✅ 验证修复

运行以下命令验证修改：

```bash
# 1. 查看 run_desktop.py 是否包含新功能
grep "try_acquire_lock" run_desktop.py
grep "is_port_in_use" run_desktop.py

# 2. 检查清理脚本
ls -la kill_app.sh
./kill_app.sh  # 测试清理功能

# 3. 重新打包并测试
./build_mac.sh
./dist/wx公众号工具/wx公众号工具
```

---

**修复时间**: 2025-12-19  
**修复内容**: 
1. 添加单实例锁机制
2. 添加端口冲突检测
3. 改进启动和退出逻辑
4. 创建清理工具脚本

