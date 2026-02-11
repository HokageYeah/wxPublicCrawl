# 启动MCP服务指南

## 🚀 快速启动

### 方法1: 使用Python脚本（推荐）

```bash
# 在项目根目录执行
cd /Users/yuye/YeahWork/Python项目/wxPublicCrawl

# 激活虚拟环境
source venv/bin/activate

# 启动MCP服务器
python app/ai/mcp/mcp_server/run_server.py
```

### 方法2: 直接运行服务器文件

```bash
cd /Users/yuye/YeahWork/Python项目/wxPublicCrawl
source venv/bin/activate
python app/ai/mcp/mcp_server/fastmcp_server.py
```

## 📋 服务信息

启动成功后，MCP服务将运行在：

- **地址**: `http://localhost:8008/mcp`
- **传输方式**: `streamable-http`
- **可用工具**:
  - `weather` - 天气查询工具
  - `calculator` - 计算器工具
  - `knowledge_base` - 知识库资源

## 🔍 验证服务

### 1. 检查服务是否运行

```bash
# 查看进程
ps aux | grep fastmcp_server

# 测试连接（如果有curl）
curl http://localhost:8008/mcp
```

### 2. 查看日志

服务启动后会在终端输出日志：

```
============================================================
启动FastMCP服务器
============================================================
服务器配置:
  - 传输方式: streamable-http
  - 地址: http://localhost:8008/mcp
  - 可用工具: weather, calculator
============================================================
```

## 🔧 配置MCP客户端

确保 `app/ai/mcp/mcp_client/mcp_settings.json` 配置正确：

```json
{
    "mcp_server_url": "http://localhost:8008/mcp",
    "mcpServer": {
        "fastmcp-demo-tools": {
            "transport": "streamable-http",
            "url": "http://localhost:8008/mcp",
            "description": "FastMCP Server 天气、知识库测试"
        }
    }
}
```

## 🎯 在应用中使用

### 1. 确保MCP服务在运行

```bash
# 终端1: 启动MCP服务
python app/ai/mcp/mcp_server/run_server.py
```

### 2. 启动主应用

```bash
# 终端2: 启动主应用
python run_desktop.py
# 或
python app/main.py
```

### 3. 访问前端

打开浏览器访问应用，在"搜索公众号"页面顶部会看到AI助手卡片。

## 💡 使用示例

在AI助手输入框中输入：

1. **天气查询**: "查询北京的天气"
2. **计算**: "计算 10+20*5"
3. **知识查询**: "什么是Python"
4. **普通对话**: "你好"

AI会自动决定是否需要调用MCP工具。

## 🐛 常见问题

### Q1: 端口被占用

**错误**: `Address already in use`

**解决**:
```bash
# 查找占用8008端口的进程
lsof -i :8008

# 杀死进程
kill -9 <PID>
```

### Q2: 连接超时

**错误**: `Connection timeout`

**检查**:
1. MCP服务是否正在运行
2. 端口8008是否被防火墙阻止
3. 配置文件URL是否正确

### Q3: AI不调用工具

**原因**: AI助手未初始化

**解决**: 
1. 确保MCP服务已启动
2. 重启主应用
3. 查看应用日志确认AI助手是否初始化成功

## 📊 监控

### 查看工具使用统计

访问API端点：
```
GET http://localhost:8000/api/v1/ai/stats
```

返回：
```json
{
  "success": true,
  "stats": {
    "tool_calls": {
      "total_calls": 10,
      "successful_calls": 9,
      "failed_calls": 1,
      "tools_used": {
        "weather": 5,
        "calculator": 4
      }
    },
    "conversation_length": 6,
    "available_tools": 2
  }
}
```

## 🔄 后台运行

### 使用nohup

```bash
nohup python app/ai/mcp/mcp_server/run_server.py > mcp_server.log 2>&1 &
```

### 查看日志

```bash
tail -f mcp_server.log
```

### 停止服务

```bash
# 查找进程ID
ps aux | grep fastmcp_server

# 停止
kill <PID>
```

---

**文档更新时间**: 2025-12-29  
**维护者**: AI Assistant

