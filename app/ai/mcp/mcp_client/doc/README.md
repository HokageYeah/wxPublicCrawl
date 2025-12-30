# MCP客户端模块使用文档

## 📋 模块概述

MCP（Model Context Protocol）客户端模块用于连接和管理MCP服务器，实现AI与外部工具的集成。

### 核心功能

1. **多客户端管理** - 同时管理多个MCP服务连接
2. **工具自动注册** - 自动将MCP工具注册到LLM函数系统
3. **统一调用接口** - 提供统一的工具调用方式
4. **资源管理** - 自动管理连接和资源清理

## 📁 目录结构

```
app/ai/mcp/
├── mcp_client/
│   ├── client_manager.py      # MCP客户端管理器
│   ├── fastmcp_client.py      # FastMCP客户端实现
│   └── mcp_settings.json      # MCP服务配置文件
└── README.md                  # 本文档
```

## 🚀 快速开始

### 1. 配置MCP服务

编辑 `mcp_settings.json`:

```json
{
    "mcp_server_url": "http://localhost:8008/mcp",
    "mcpServer": {
        "my-service": {
            "transport": "streamable-http",
            "url": "http://localhost:8008/mcp",
            "description": "我的MCP服务"
        }
    }
}
```

### 2. 初始化客户端管理器

```python
from app.ai.mcp.mcp_client.client_manager import MCPClientManager

# 初始化管理器（需要LLM连接对象）
manager = MCPClientManager(llm_conn)

# 初始化所有MCP客户端
await manager.init_mcp_clients()
```

### 3. 调用MCP工具

```python
# 执行工具
result = await manager.execute_tool(
    tool_name="search_weather",
    tool_args={"city": "北京"}
)
```

## 📝 配置说明

### HTTP传输方式

```json
{
    "my-http-service": {
        "transport": "streamable-http",
        "url": "http://localhost:8008/mcp",
        "description": "HTTP方式连接"
    }
}
```

### stdio传输方式（Python）

```json
{
    "my-python-service": {
        "transport": "stdio",
        "command": "python",
        "args": ["path/to/server.py"],
        "description": "Python脚本"
    }
}
```

### stdio传输方式（Node.js）

```json
{
    "my-node-service": {
        "transport": "stdio",
        "command": "node",
        "args": ["path/to/server.js"],
        "description": "Node.js脚本"
    }
}
```

### stdio传输方式（npx）

```json
{
    "my-npx-service": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@package/mcp-server"],
        "env": {
            "API_KEY": "your-api-key"
        },
        "description": "NPX包"
    }
}
```

## 🔧 API参考

### MCPClientManager

#### `__init__(llm_conn)`

初始化MCP客户端管理器

**参数:**
- `llm_conn`: LLM连接对象

#### `async init_mcp_clients() -> bool`

初始化所有MCP客户端

**返回:**
- `bool`: 是否至少有一个客户端初始化成功

**日志输出:**
```
[MCP_MANAGER] 开始初始化 3 个MCP客户端...
[MCP_MANAGER] 📡 正在初始化MCP服务: fastmcp-demo-tools
[MCP_MANAGER] ✅ 服务 fastmcp-demo-tools 初始化成功，获取到 5 个工具
...
[MCP_MANAGER] MCP客户端初始化完成
  成功: 2/3
  失败: 1/3
  工具总数: 10
```

#### `get_all_tools() -> List[Dict[str, Any]]`

获取所有已注册的工具

#### `is_mcp_tool(tool_name: str) -> bool`

判断工具是否为MCP工具

#### `async execute_tool(tool_name: str, tool_args: Dict) -> Any`

执行MCP工具调用

**参数:**
- `tool_name`: 工具名称（可带 `mcp_` 前缀）
- `tool_args`: 工具参数字典

**返回:**
- 工具执行结果

**日志输出:**
```
[MCP_MANAGER] 🔧 执行MCP工具: search_weather
   参数: {'city': '北京'}
[MCP_MANAGER]   ✓ 在客户端 [weather-service] 中找到工具
[MCP_MANAGER]   ✅ 工具执行成功: search_weather
```

#### `async cleanup()`

清理所有客户端资源

#### `get_client_status() -> Dict`

获取所有客户端状态（用于调试）

### FastMCPClient

#### `__init__(name: str, config: Dict)`

初始化FastMCP客户端

**参数:**
- `name`: 客户端名称
- `config`: 配置字典

#### `async init_client()`

初始化客户端连接

**日志输出:**
```
[FASTMCP_CLIENT] [my-service] 开始初始化MCP客户端 - 传输方式: streamable-http
[FASTMCP_CLIENT] [my-service] 📡 连接HTTP服务: http://localhost:8008/mcp/
[FASTMCP_CLIENT] [my-service] ✅ 连接测试成功
[FASTMCP_CLIENT] [my-service] 🔧 获取到 3 个工具: ['search_weather', 'get_time', 'calculate']
```

#### `has_tool(tool_name: str) -> bool`

检查工具是否存在

#### `get_tool() -> Optional[List[Dict]]`

获取可用工具列表（标准格式）

#### `async call_tool(tool_name: str, tool_args: Dict) -> Any`

调用MCP工具

**日志输出:**
```
[FASTMCP_CLIENT] [my-service] 🔧 调用工具: search_weather
   参数: {'city': '北京'}
[FASTMCP_CLIENT] [my-service] ✅ 工具调用成功: search_weather
```

#### `async cleanup()`

清理客户端资源

#### `get_status() -> Dict`

获取客户端状态

## 🎯 使用场景示例

### 场景1: 自动翻页公众号列表

```python
# 1. 配置MCP服务（mcp_settings.json）
{
    "pagination-tool": {
        "transport": "streamable-http",
        "url": "http://localhost:8008/mcp",
        "description": "翻页工具"
    }
}

# 2. 使用
manager = MCPClientManager(llm_conn)
await manager.init_mcp_clients()

# AI会自动调用工具翻页
result = await manager.execute_tool(
    tool_name="next_page",
    tool_args={"current_page": 1}
)
```

### 场景2: 多服务协同

```python
# 同时连接多个MCP服务
{
    "weather-service": {...},
    "database-service": {...},
    "automation-service": {...}
}

# AI可以自动选择合适的工具
# 例如：先查询数据库，再根据结果调用自动化工具
```

## 📊 日志级别说明

### DEBUG
- 详细的执行流程
- 工具检查和转换
- 参数处理

### INFO
- 客户端初始化
- 工具注册
- 工具调用
- 执行结果

### WARNING
- 工具不存在
- 配置缺失
- 非致命错误

### ERROR
- 初始化失败
- 工具调用失败
- 致命错误

## 🐛 调试技巧

### 1. 查看客户端状态

```python
status = manager.get_client_status()
print(json.dumps(status, indent=2, ensure_ascii=False))
```

输出:
```json
{
  "total_clients": 2,
  "total_tools": 8,
  "clients": {
    "weather-service": {
      "connected": true,
      "tool_count": 3,
      "tools": ["search_weather", "get_forecast", "get_alerts"]
    }
  }
}
```

### 2. 启用详细日志

```python
from loguru import logger

# 设置日志级别
logger.add("mcp_debug.log", level="DEBUG", filter=lambda r: "MCP" in r["extra"].get("tag", ""))
```

### 3. 测试单个工具

```python
# 检查工具是否存在
if manager.is_mcp_tool("search_weather"):
    result = await manager.execute_tool("search_weather", {"city": "北京"})
    print(result)
```

## ⚠️ 常见问题

### Q1: 配置文件找不到

**问题**: `配置文件不存在: app/ai/mcp/mcp_client/mcp_settings.json`

**解决**: 确保配置文件存在，打包时需要包含在 `wx_crawler.spec`:

```python
datas=[
    ('app/ai/mcp/mcp_client/mcp_settings.json', 'app/ai/mcp/mcp_client'),
]
```

### Q2: npx命令失败

**问题**: `npx命令必须包含包名参数`

**解决**: 检查配置中 `args` 必须包含包名:

```json
{
    "command": "npx",
    "args": ["-y", "@package/name"]  // ✓ 正确
    // "args": ["-y"]                 // ✗ 错误
}
```

### Q3: 工具调用超时

**问题**: 工具调用长时间无响应

**解决**: 增加超时时间:

```json
{
    "transport": "stdio",
    "command": "python",
    "args": ["server.py"],
    "timeout": 30.0  // 增加到30秒
}
```

## 🔄 更新记录

### v1.0.0 (2025-12-29)

✅ **优化内容:**
1. 统一使用 `logger` 记录日志，移除所有 `print` 语句
2. 添加完整的类型提示
3. 改进错误处理和异常信息
4. 优化日志输出格式和级别
5. 添加详细的函数文档字符串
6. 支持打包后的配置文件路径（使用 `get_resource_path`）
7. 添加客户端状态查询功能
8. 改进资源清理逻辑

✅ **新增功能:**
- `get_client_status()` - 查看所有客户端状态
- `get_status()` - 查看单个客户端状态
- 更详细的调试日志
- 更友好的错误提示

---

**文档更新时间**: 2025-12-29  
**维护者**: AI Assistant

