# MCP-LLM连接器快速开始

## 🎯 5分钟上手

### 第1步: 初始化MCP管理器

```python
from app.ai.mcp.mcp_client.client_manager import MCPClientManager

# 创建管理器（需要llm_conn对象）
mcp_manager = MCPClientManager(llm_conn)

# 初始化所有MCP客户端
await mcp_manager.init_mcp_clients()
```

### 第2步: 创建连接器

```python
from app.ai.llm.mcp_llm_connect import MCPLLMConnect

# 创建连接器
connector = MCPLLMConnect(mcp_manager)
```

### 第3步: 发送查询

```python
# AI会自动调用需要的工具
response = await connector.query("帮我翻到第5页")

print(response)
# 输出: "已成功翻到第5页"
```

## 🎓 核心概念

### Function Calling

AI可以：
- 自动决定是否需要工具
- 自动选择合适的工具
- 自动生成工具参数
- 处理工具结果并回复

### 工作流程

```
用户输入
  ↓
AI分析意图
  ↓
需要工具? → 否 → 直接回复
  ↓ 是
调用工具
  ↓
获取结果
  ↓
AI处理结果
  ↓
返回用户
```

## 📖 常用操作

### 1. 基础查询

```python
response = await connector.query("查询天气")
```

### 2. 带系统提示

```python
response = await connector.query(
    user_message="查询数据",
    system_message="你是一个专业的数据分析师"
)
```

### 3. 查看统计

```python
stats = connector.get_stats()
print(f"工具调用次数: {stats['tool_calls']['total_calls']}")
```

### 4. 清空历史

```python
connector.clear_history()
```

## 🔍 调试

### 启用详细日志

```python
from loguru import logger

logger.add(
    "debug.log",
    level="DEBUG",
    filter=lambda r: "MCP" in r["extra"].get("tag", "")
)
```

### 查看对话历史

```python
history = connector.get_conversation_history()
for msg in history:
    print(f"[{msg['role']}] {msg.get('content', '[工具调用]')}")
```

## ⚡ 实际应用

### 场景: 公众号自动翻页

```python
# 用户只需要说自然语言
response = await connector.query(
    "帮我翻到第10页，并统计每页有多少篇文章"
)

# AI会自动：
# 1. 循环调用 next_page 工具
# 2. 调用 get_article_count 工具
# 3. 汇总结果
# 4. 返回报告
```

## 📚 完整文档

- **详细文档**: `README_MCP_LLM.md`
- **使用示例**: `example_mcp_usage.py`
- **实现说明**: `MCP_LLM实现总结.md`

## 💡 提示

1. **明确指令**: "使用工具查询..." 比 "查询..." 更好
2. **合理限制**: 设置 `max_tool_calls` 防止无限循环
3. **查看日志**: 日志记录了完整的执行过程
4. **统计分析**: 定期查看 `get_stats()` 了解工具使用情况

## ⚠️ 注意事项

1. ✅ 确保MCP服务已启动
2. ✅ 确保已配置 `AI_API_KEY`
3. ✅ 流式模式不支持工具调用
4. ✅ 工具调用有次数限制（默认10次）

---

**快速开始指南** | 更新时间: 2025-12-29

