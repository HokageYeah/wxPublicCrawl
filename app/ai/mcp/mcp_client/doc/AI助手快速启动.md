# AI助手快速启动指南

## 🎯 5分钟快速启动

### 前置条件

- ✅ Python虚拟环境已激活
- ✅ 所有依赖已安装
- ✅ `.env` 文件已配置

### 启动步骤

#### 终端1: 启动MCP服务器

```bash
cd /Users/yuye/YeahWork/Python项目/wxPublicCrawl
source venv/bin/activate
python app/ai/mcp/mcp_server/fastmcp_server.py
```

**期望输出：**
```
============================================================
启动FastMCP服务器
============================================================
服务器地址: http://localhost:8008/mcp
可用工具: weather, calculator, knowledge_base
============================================================
```

#### 终端2: 启动主应用

```bash
cd /Users/yuye/YeahWork/Python项目/wxPublicCrawl
source venv/bin/activate
python app/main.py
```

**期望输出：**
```
============================================================
🚀 应用启动中...
============================================================
📝 初始化日志系统...
✅ 日志系统初始化完成
🗄️  初始化数据库连接...
✅ 数据库连接完成
🤖 初始化AI助手...
🔧 MCP-LLM连接器实例已创建
   AI模型: GLM-4.7
   最大工具调用: 10
   自动执行工具: True
🚀 开始异步初始化MCP-LLM连接器...
🔌 正在初始化MCP客户端管理器...
✅ MCP客户端管理器初始化成功
📦 已加载工具列表:
   - MCP工具数量: 3
   - MCP客户端数量: 1
📦 本地注册函数数量: X
✅ MCP-LLM连接器初始化完成！
   - AI模型: GLM-4.7
   - MCP工具: 3个
   - 本地函数: X个
   - 总可用功能: X个
✅ AI助手初始化完成
============================================================
✅ 应用启动完成
============================================================
```

### 测试AI助手

1. 打开浏览器访问应用
2. 进入"搜索公众号"页面
3. 在AI助手输入框测试：

```
👉 你好
👉 查询北京的天气
👉 计算 123 * 456
👉 什么是Python
```

## 🐛 快速故障排查

### 问题1: "AI助手服务未初始化"

**检查清单：**
- [ ] MCP服务器是否在终端1运行？
- [ ] 主应用是否正常启动？
- [ ] 启动日志中是否有"✅ AI助手初始化完成"？

**快速修复：**
```bash
# 1. 停止所有进程 (Ctrl+C)
# 2. 重新启动MCP服务器
# 3. 重新启动主应用
```

### 问题2: MCP服务器启动失败

**可能原因：** 端口8008被占用

**快速修复：**
```bash
# 查看占用端口的进程
lsof -i :8008

# 结束进程
kill -9 <PID>
```

### 问题3: "配置文件不存在"

**快速修复：**
```bash
# 检查配置文件
ls app/ai/mcp/mcp_client/mcp_settings.json

# 如果不存在，从模板创建
cp app/ai/mcp/mcp_client/mcp_settings.json.example app/ai/mcp/mcp_client/mcp_settings.json
```

### 问题4: API密钥错误

**快速修复：**
```bash
# 编辑 .env 文件
nano .env

# 确保配置正确
AI_API_KEY=your_key_here
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4-turbo-preview
```

## 🔍 诊断工具

### 配置检查工具

```bash
python app/ai/test/check_ai_config.py
```

这个工具会检查：
- ✅ 环境变量配置
- ✅ 依赖包安装
- ✅ MCP配置文件
- ✅ MCP服务器连接

### 初始化测试工具

```bash
python app/ai/test/test_ai_init.py
```

这个工具会测试：
- ✅ 连接器创建
- ✅ 异步初始化
- ✅ 基本对话功能
- ✅ 工具调用功能

## 📊 查看运行状态

### API接口

```bash
# 健康检查
curl http://localhost:8002/api/v1/ai-assistant/health

# 查看统计信息
curl http://localhost:8002/api/v1/ai-assistant/stats

# 测试查询
curl -X POST http://localhost:8002/api/v1/ai-assistant/query \
  -H "Content-Type: application/json" \
  -d '{"query": "你好"}'
```

### 查看日志

日志会实时输出到终端2，关键标签：
- `[AI_ASSISTANT_API]` - API层日志
- `[MCP_LLM_CONNECT]` - 连接器日志
- `[MCP_MANAGER]` - MCP管理器日志
- `[AI_CLIENT]` - AI客户端日志

## 🎉 成功标志

如果看到以下信息，说明一切正常：

**终端1 (MCP服务器):**
```
✅ 服务器地址: http://localhost:8008/mcp
✅ 可用工具: 3个
```

**终端2 (主应用):**
```
✅ AI助手初始化完成
✅ 应用启动完成
```

**浏览器:**
```
AI助手输入框可用
输入"你好"能收到回复
```

## 💡 常用命令

```bash
# 停止所有服务
Ctrl+C (在两个终端中分别按)

# 重启MCP服务器
python app/ai/mcp/mcp_server/fastmcp_server.py

# 重启主应用
python app/main.py

# 查看进程
ps aux | grep python

# 结束所有Python进程 (谨慎使用)
pkill -f "python app"
```

## 📚 更多信息

- 详细架构说明: `app/ai/AI助手架构说明.md`
- 配置检查: `python app/ai/test/check_ai_config.py`
- 初始化测试: `python app/ai/test/test_ai_init.py`

---

**提示：** 遇到问题先查看终端日志，大多数问题都能从日志中找到原因！

