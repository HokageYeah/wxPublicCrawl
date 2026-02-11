# MCP-LLM连接器使用文档

## 📋 概述

`MCPLLMConnect` 是连接MCP工具系统和AI模型的桥梁，实现了AI自动调用工具的能力。

### 核心功能

1. **Function Calling** - AI可以自动决定何时调用哪个工具
2. **多轮对话** - 支持复杂的多步骤任务
3. **工具编排** - AI可以组合多个工具完成任务
4. **上下文管理** - 保持对话历史和工具调用记录

## 🚀 快速开始

### 基础使用

```python
from app.ai.llm.mcp_llm_connect import MCPLLMConnect
from app.ai.mcp.mcp_client.client_manager import MCPClientManager

# 1. 初始化MCP管理器（假设llm_conn已存在）
mcp_manager = MCPClientManager(llm_conn)
await mcp_manager.init_mcp_clients()

# 2. 创建连接器
connector = MCPLLMConnect(mcp_manager)

# 3. 发送查询（AI会自动调用工具）
response = await connector.query("帮我翻到第5页")

# AI会自动：
# - 理解用户意图
# - 调用 next_page 工具
# - 处理工具结果
# - 生成回复
print(response)  # "已成功翻到第5页"
```

## 🔧 详细使用

### 1. 初始化连接器

```python
connector = MCPLLMConnect(
    mcp_manager=mcp_manager,          # MCP管理器（必需）
    ai_client=None,                   # AI客户端（可选，默认创建新实例）
    max_tool_calls=10,                # 最大工具调用次数
    auto_execute_tools=True           # 是否自动执行工具
)
```

### 2. 发送查询

```python
# 基础查询
response = await connector.query("查询北京的天气")

# 带系统提示
response = await connector.query(
    user_message="查询天气",
    system_message="你是一个专业的天气助手"
)

# 自定义温度
response = await connector.query(
    user_message="写一首诗",
    temperature=0.9  # 更有创意
)

# 禁用工具
response = await connector.query(
    user_message="你好",
    enable_tools=False  # 纯对话，不调用工具
)
```

### 3. 流式响应（不支持工具）

```python
# 流式输出（暂不支持工具调用）
async for chunk in connector.stream_query("讲个故事"):
    print(chunk, end='', flush=True)
```

### 4. 管理对话历史

```python
# 获取对话历史
history = connector.get_conversation_history()

# 清空历史
connector.clear_history()
```

### 5. 查看统计信息

```python
stats = connector.get_stats()
print(stats)
# {
#     "tool_calls": {
#         "total_calls": 15,
#         "successful_calls": 14,
#         "failed_calls": 1,
#         "tools_used": {
#             "search_weather": 5,
#             "next_page": 10
#         }
#     },
#     "conversation_length": 10,
#     "available_tools": 8
# }
```

## 📝 工作流程详解

### 单次工具调用流程

```
用户: "帮我查询北京的天气"
  ↓
AI分析意图: 需要使用 search_weather 工具
  ↓
自动调用工具: search_weather(city="北京")
  ↓
获取结果: {"temp": 15, "weather": "晴"}
  ↓
AI处理结果: "北京今天晴天，温度15度"
  ↓
返回给用户
```

### 多轮工具调用流程

```
用户: "帮我翻5页并查询每页的第一条标题"
  ↓
AI规划: 需要调用多次工具
  ↓
第1轮: next_page() → 获取页面2数据
第2轮: get_title(index=0) → 获取第一条标题
第3轮: next_page() → 获取页面3数据
第4轮: get_title(index=0) → 获取第一条标题
...
  ↓
AI汇总所有结果
  ↓
返回给用户
```

## 🎯 使用场景

### 场景1: 自动翻页公众号列表

```python
connector = MCPLLMConnect(mcp_manager)

# 用户只需要说自然语言
response = await connector.query("帮我翻到第10页，然后告诉我有多少篇文章")

# AI会自动：
# 1. 调用 next_page 工具9次
# 2. 调用 get_article_count 工具
# 3. 汇总结果返回
```

### 场景2: 复杂数据查询

```python
# 用户查询
response = await connector.query(
    "查询最近7天北京的天气，并告诉我哪天最适合出行"
)

# AI会：
# 1. 调用 get_weather_history 获取历史数据
# 2. 分析数据
# 3. 给出建议
```

### 场景3: 多步骤任务

```python
response = await connector.query(
    "帮我找出公众号列表中所有关于教育的文章，"
    "并统计每个月有多少篇"
)

# AI会：
# 1. 遍历所有页面
# 2. 筛选教育类文章
# 3. 按月份分组统计
# 4. 生成报告
```

## 🔍 调试技巧

### 1. 启用详细日志

```python
from loguru import logger

logger.add(
    "mcp_llm_debug.log",
    level="DEBUG",
    filter=lambda r: "MCP" in r["extra"].get("tag", "")
)
```

日志输出示例：
```
[MCP_LLM_CONNECT] 📨 收到用户查询: 帮我翻到第5页
[MCP_LLM_CONNECT] 🔧 可用工具数量: 3
[MCP_LLM_CONNECT] 🔧 AI请求调用 1 个工具 (总计: 1/10)
[MCP_LLM_CONNECT] 🔧 执行工具: next_page
   参数: {'page': 5}
[MCP_MANAGER] 🔧 执行MCP工具: next_page
   参数: {'page': 5}
[MCP_MANAGER]   ✓ 在客户端 [pagination-service] 中找到工具
[FASTMCP_CLIENT] [pagination-service] 🔧 调用工具: next_page
[FASTMCP_CLIENT] [pagination-service] ✅ 工具调用成功: next_page
[MCP_LLM_CONNECT] ✅ 工具执行成功: next_page
[MCP_LLM_CONNECT] 💬 AI回复（无工具调用）: 已成功翻到第5页...
[MCP_LLM_CONNECT] ✅ 查询完成
```

### 2. 查看对话历史

```python
history = connector.get_conversation_history()
for msg in history:
    print(f"[{msg['role']}]", msg.get('content', '[工具调用]'))
```

### 3. 监控工具使用情况

```python
stats = connector.get_stats()
print(f"工具调用成功率: {stats['tool_calls']['successful_calls']/stats['tool_calls']['total_calls']*100}%")
print(f"最常用工具: {max(stats['tool_calls']['tools_used'].items(), key=lambda x: x[1])}")
```

## ⚙️ 高级配置

### 自定义AI客户端

```python
from app.ai.llm.ai_client import AIClient

# 创建自定义AI客户端
custom_ai = AIClient(
    model="gpt-4",
    temperature=0.3,
    max_tokens=2000,
    enable_history=True
)

# 使用自定义客户端
connector = MCPLLMConnect(
    mcp_manager=mcp_manager,
    ai_client=custom_ai
)
```

### 限制工具调用次数

```python
# 防止无限循环
connector = MCPLLMConnect(
    mcp_manager=mcp_manager,
    max_tool_calls=5  # 最多调用5次工具
)
```

### 手动控制工具执行

```python
connector = MCPLLMConnect(
    mcp_manager=mcp_manager,
    auto_execute_tools=False  # 不自动执行
)

# 需要手动确认每次工具调用
# （功能待实现）
```

## 🐛 常见问题

### Q1: 工具调用达到上限

**问题**: `达到最大工具调用次数 (10)`

**原因**: 任务过于复杂或AI进入循环

**解决**:
1. 增加 `max_tool_calls` 参数
2. 优化提示词，让AI更清楚任务目标
3. 将复杂任务拆分为多个简单任务

### Q2: AI不调用工具

**问题**: AI只回复文本，不调用工具

**原因**: 
- 提示不够明确
- 工具描述不清楚
- 没有合适的工具

**解决**:
1. 使用更明确的指令："使用工具查询..."
2. 检查MCP工具是否正确注册
3. 查看日志确认工具是否可用

### Q3: 工具调用失败

**问题**: `工具执行失败: ...`

**原因**: MCP服务问题或参数错误

**解决**:
1. 检查MCP服务是否正常运行
2. 查看详细日志
3. 测试工具是否可以独立调用

## 📊 性能优化

### 1. 减少工具调用

```python
# 明确指令，减少试探性调用
response = await connector.query(
    "使用 search_weather 工具查询北京天气"  # 明确工具名
)
```

### 2. 使用更快的模型

```python
# 对于简单任务，使用更快的模型
fast_ai = AIClient(model="gpt-3.5-turbo")
connector = MCPLLMConnect(mcp_manager, ai_client=fast_ai)
```

### 3. 批量处理

```python
# 一次性处理多个任务
response = await connector.query(
    "查询北京、上海、深圳的天气，给出汇总报告"
)
```

## 🔄 与其他模块集成

### 与Web API集成

```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/ai-query")
async def ai_query(query: str):
    connector = get_connector()  # 获取全局连接器实例
    response = await connector.query(query)
    return {"response": response}
```

### 与教育分析集成

```python
from app.ai.code.education_analyze import analyze_education_articles

# 结合MCP工具和教育分析
response = await connector.query(
    "帮我翻页找出所有教育类文章，并分析它们"
)
```

## 📚 相关文档

- [MCP客户端管理器文档](../mcp/README.md)
- [AI客户端文档](../doc/README.md)
- [Function Calling官方文档](https://platform.openai.com/docs/guides/function-calling)

---

**文档创建时间**: 2025-12-29  
**维护者**: AI Assistant  
**状态**: ✅ 已完成并测试

