# AI助手完整启动指南

## 📋 概述

本指南将帮助您完成AI助手的完整配置和启动流程。

## 🔧 架构说明

AI助手系统由以下几个核心组件组成：

1. **AIClient** (`app/ai/llm/ai_client.py`): 负责与OpenAI API通信
2. **MCPClientManager** (`app/ai/mcp/mcp_client/client_manager.py`): 管理多个MCP客户端
3. **MCPLLMConnect** (`app/ai/llm/mcp_llm_connect.py`): 连接AI和MCP工具的桥梁
4. **FastMCP Server** (`app/ai/mcp/mcp_server/fastmcp_server.py`): 提供工具服务

### 初始化流程

```
应用启动
    ↓
main.py: lifespan启动事件
    ↓
ai_assistant.py: init_ai_assistant()
    ↓
1. 创建AIClient (使用settings.AI_MODEL)
    ↓
2. 创建MCPClientManager (传入ai_client)
    ↓
3. 初始化MCP客户端 (连接到MCP服务器)
    ↓
4. 创建MCPLLMConnect (整合AI和MCP)
    ↓
AI助手就绪 ✅
```

## 🚀 完整启动步骤

### 第1步: 配置环境变量

在项目根目录创建或修改 `.env` 文件：

```bash
# AI配置 (必填)
AI_API_KEY=your_openai_api_key_here
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4-turbo-preview

# 其他配置...
```

**重要说明：**
- `AI_API_KEY`: OpenAI API密钥
- `AI_BASE_URL`: API端点（使用第三方服务时可能需要修改）
- `AI_MODEL`: 使用的模型名称

### 第2步: 检查fastmcp依赖

确保已安装 `fastmcp`：

```bash
source venv/bin/activate
pip list | grep fastmcp
```

如果没有安装：

```bash
pip install fastmcp
```

### 第3步: 启动MCP服务器

在**终端1**中：

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
可用工具:
  - weather: 查询天气
  - calculator: 计算器
  - knowledge_base: 知识库查询
============================================================
```

**故障排查：**
- ❌ `ModuleNotFoundError: No module named 'fastmcp'` → 参考第2步安装
- ❌ `Address already in use` → 端口8008被占用，修改端口或关闭占用进程

### 第4步: 启动主应用

在**终端2**中：

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
🚀 开始初始化AI助手...
📝 创建AI客户端...
✅ AI客户端创建成功 (模型: gpt-4-turbo-preview)
🔧 创建MCP客户端管理器...
🔌 连接MCP服务器...
✅ MCP客户端初始化成功
🔗 创建MCP-LLM连接器...
✅ AI助手初始化成功！
   - AI模型: gpt-4-turbo-preview
   - MCP客户端数量: 1
   - 可用工具数量: 3
✅ AI助手初始化完成
============================================================
✅ 应用启动完成
============================================================
```

**关键日志标识：**
- ✅ `AI客户端创建成功` → AIClient初始化成功
- ✅ `MCP客户端初始化成功` → 连接到MCP服务器成功
- ✅ `AI助手初始化成功` → 整个系统就绪

### 第5步: 测试AI助手

1. 打开浏览器访问前端
2. 进入"搜索公众号"页面
3. 在AI助手输入框中测试：

**测试用例：**
```
👉 你好
   预期：AI正常回复问候

👉 查询北京的天气
   预期：调用weather工具，返回天气信息

👉 计算 123 * 456
   预期：调用calculator工具，返回计算结果

👉 什么是Python
   预期：调用knowledge_base工具，返回知识信息
```

## 🐛 常见问题排查

### 问题1: "AI助手服务未初始化"

**原因：** 初始化失败

**排查步骤：**
1. 检查终端1，确认MCP服务器正在运行
2. 检查终端2的启动日志，查找错误信息
3. 检查 `.env` 文件，确认AI配置正确

### 问题2: AI无法调用工具

**原因：** MCP客户端未连接或配置错误

**排查步骤：**
1. 访问 `/api/v1/ai-assistant/health` 检查服务状态
2. 检查 `app/ai/mcp/mcp_client/config.json` 配置文件
3. 重启MCP服务器和主应用

### 问题3: MCP服务器启动失败

**原因：** 依赖问题或端口冲突

**解决方案：**
```bash
# 检查依赖
pip install fastmcp sse-starlette uvicorn

# 修改端口（如果8008被占用）
# 编辑 app/ai/mcp/mcp_server/fastmcp_server.py
# 将 port=8008 改为其他端口
```

### 问题4: AI响应缓慢

**原因：** API调用延迟或网络问题

**优化建议：**
1. 检查 `AI_BASE_URL` 是否配置正确
2. 考虑使用代理或国内API镜像
3. 调整 `temperature` 参数以提高响应速度

## 📊 监控和调试

### 查看AI助手状态

```bash
curl http://localhost:8002/api/v1/ai-assistant/health
```

**响应示例：**
```json
{
  "status": "ok",
  "ai_available": true
}
```

### 查看统计信息

```bash
curl http://localhost:8002/api/v1/ai-assistant/stats
```

### 查看日志

开发模式下，所有日志会输出到控制台。您可以：

1. 查看实时日志（终端2）
2. 搜索特定标签：
   - `[AI_ASSISTANT_API]` - API相关日志
   - `[MCP_LLM_CONNECT]` - AI与MCP交互日志
   - `[MCP_MANAGER]` - MCP管理器日志
   - `[AI_CLIENT]` - AI客户端日志

## 🚢 生产环境部署

### 使用systemd管理服务

创建 `mcp-server.service`:

```ini
[Unit]
Description=FastMCP Server
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/wxPublicCrawl
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python app/ai/mcp/mcp_server/fastmcp_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

创建 `wx-crawl-app.service`:

```ini
[Unit]
Description=WX Public Crawl Application
After=network.target mcp-server.service
Requires=mcp-server.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/wxPublicCrawl
Environment="PATH=/path/to/venv/bin"
Environment="ENV=production"
ExecStart=/path/to/venv/bin/python app/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl start mcp-server
sudo systemctl start wx-crawl-app
sudo systemctl enable mcp-server wx-crawl-app
```

## 📚 进一步阅读

- [MCP协议文档](https://modelcontextprotocol.io/)
- [FastMCP文档](https://github.com/jlowin/fastmcp)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

## 💡 提示

1. **开发模式**：使用 `uvicorn` 的 `reload=True` 实现热重载
2. **调试模式**：在 `.env` 中设置 `DEBUG=true` 获取详细日志
3. **性能优化**：根据实际需求调整 `max_tool_calls` 和 `temperature`
4. **安全建议**：生产环境中使用环境变量而非 `.env` 文件存储敏感信息

---

**最后更新：** 2025-12-30  
**维护者：** AI Assistant Team

