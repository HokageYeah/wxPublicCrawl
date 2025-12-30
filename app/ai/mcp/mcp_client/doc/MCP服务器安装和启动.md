# MCP服务器安装和启动指南

## ❌ 问题诊断

你遇到的错误：
```
ModuleNotFoundError: No module named 'fastmcp'
```

**原因**: 缺少 `fastmcp` 依赖包。

## ✅ 解决方案

### 第1步: 安装依赖包

```bash
cd /Users/yuye/YeahWork/Python项目/wxPublicCrawl

# 激活虚拟环境
source venv/bin/activate

# 安装 fastmcp
pip install fastmcp

# 如果上面的命令失败，尝试升级 pip
pip install --upgrade pip
pip install fastmcp
```

### 第2步: 验证安装

```bash
python -c "import fastmcp; print(fastmcp.__version__)"
```

如果看到版本号（例如 `0.5.0`），说明安装成功！

### 第3步: 启动MCP服务器

现在有**3种方式**启动：

#### 方式1: 直接运行（最简单） ✅

```bash
cd /Users/yuye/YeahWork/Python项目/wxPublicCrawl
python app/ai/mcp/mcp_server/fastmcp_server.py
```

#### 方式2: 使用启动脚本

```bash
cd /Users/yuye/YeahWork/Python项目/wxPublicCrawl
python app/ai/mcp/mcp_server/run_server.py
```

#### 方式3: 使用 Shell 脚本

```bash
cd /Users/yuye/YeahWork/Python项目/wxPublicCrawl
bash script/start_ai_assistant.sh
```

### 期望输出

成功启动后应该看到：

```
============================================================
启动FastMCP服务器
============================================================
项目根目录: /Users/yuye/YeahWork/Python项目/wxPublicCrawl
服务器地址: http://localhost:8008/mcp
可用工具: weather, calculator, knowledge_base
============================================================
```

## 📝 完整的启动流程

```bash
# 1. 进入项目目录
cd /Users/yuye/YeahWork/Python项目/wxPublicCrawl

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装依赖（如果还没安装）
pip install fastmcp

# 4. 启动MCP服务器（终端1）
python app/ai/mcp/mcp_server/fastmcp_server.py

# 5. 在另一个终端启动主应用（终端2）
cd /Users/yuye/YeahWork/Python项目/wxPublicCrawl
source venv/bin/activate
python app/main.py
```

## 🔍 验证服务

### 测试1: 检查端口

```bash
# 检查8008端口是否被占用（说明服务在运行）
lsof -i :8008
```

### 测试2: 测试连接

```bash
# 如果有 curl
curl http://localhost:8008/mcp

# 如果有 Python
python -c "import requests; print(requests.get('http://localhost:8008/mcp').text)"
```

## 🐛 常见问题

### Q1: pip install fastmcp 失败

**错误**: `ERROR: Could not find a version that satisfies the requirement fastmcp`

**解决**:
```bash
# 方法1: 升级 pip
pip install --upgrade pip
pip install fastmcp

# 方法2: 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple fastmcp

# 方法3: 检查 Python 版本（需要 Python 3.8+）
python --version
```

### Q2: 虚拟环境激活失败

**错误**: `venv/bin/activate: Permission denied`

**解决**:
```bash
# 给执行权限
chmod +x venv/bin/activate

# 然后再激活
source venv/bin/activate
```

### Q3: 端口被占用

**错误**: `Address already in use: 8008`

**解决**:
```bash
# 查找占用进程
lsof -i :8008

# 终止进程
kill -9 <PID>

# 或者修改端口（在代码中改为 8009）
```

### Q4: ModuleNotFoundError: No module named 'app'

**解决**: 确保从项目根目录运行：
```bash
# ✅ 正确
cd /Users/yuye/YeahWork/Python项目/wxPublicCrawl
python app/ai/mcp/mcp_server/fastmcp_server.py

# ❌ 错误
cd /Users/yuye/YeahWork/Python项目/wxPublicCrawl/app/ai/mcp/mcp_server
python fastmcp_server.py
```

## 📦 依赖清单

MCP服务器需要的依赖：

```
fastmcp>=0.5.0
fastapi
pydantic
```

如果需要，可以创建 `requirements-mcp.txt`：

```bash
# 创建依赖文件
cat > requirements-mcp.txt << EOF
fastmcp>=0.5.0
fastapi>=0.104.0
pydantic>=2.0.0
EOF

# 安装
pip install -r requirements-mcp.txt
```

## 🎯 快速检查清单

运行前检查：

- [ ] 虚拟环境已激活
- [ ] `fastmcp` 已安装
- [ ] 从项目根目录运行
- [ ] 端口 8008 未被占用
- [ ] Python 版本 >= 3.8

## 🚀 推荐的开发流程

### 终端1: MCP服务器

```bash
cd /Users/yuye/YeahWork/Python项目/wxPublicCrawl
source venv/bin/activate
python app/ai/mcp/mcp_server/fastmcp_server.py
```

保持运行，不要关闭。

### 终端2: 主应用

```bash
cd /Users/yuye/YeahWork/Python项目/wxPublicCrawl
source venv/bin/activate
python app/main.py
```

### 浏览器

访问 `http://localhost:8000`，进入"搜索公众号"页面，测试AI助手。

## 📊 成功标志

MCP服务器成功运行的标志：

1. ✅ 终端显示服务器启动信息
2. ✅ 没有报错
3. ✅ 端口 8008 被占用（`lsof -i :8008`）
4. ✅ 可以通过 curl/浏览器访问 `http://localhost:8008/mcp`
5. ✅ AI助手可以调用工具

## 💡 提示

**自动启动**: 可以将MCP服务器配置为系统服务，开机自动启动（生产环境）。

**调试模式**: 如果遇到问题，在代码中添加更多 `print()` 语句查看执行流程。

**日志记录**: 所有操作都有日志，查看 `logs/` 目录。

---

**更新时间**: 2025-12-29  
**问题**: ✅ 已诊断和解决

