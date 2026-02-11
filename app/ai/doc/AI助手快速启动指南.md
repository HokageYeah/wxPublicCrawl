# AI助手快速启动指南 🚀

## ⚡ 一键启动（推荐）

```bash
# 使用启动脚本（自动启动MCP服务和主应用）
bash script/start_ai_assistant.sh
```

## 📋 手动启动

### 终端1: 启动MCP服务

```bash
cd /Users/yuye/YeahWork/Python项目/wxPublicCrawl
source venv/bin/activate
python app/ai/mcp/mcp_server/run_server.py
```

**期望输出：**
```
============================================================
启动FastMCP服务器
============================================================
服务器配置:
  - 地址: http://localhost:8008/mcp
  - 可用工具: weather, calculator
============================================================
```

### 终端2: 启动主应用

```bash
cd /Users/yuye/YeahWork/Python项目/wxPublicCrawl
source venv/bin/activate
python app/main.py
```

**⚠️ 重要**: 需要先在 `app/main.py` 中添加AI助手初始化代码！

参考文档：`app/ai/mcp/应用初始化集成指南.md`

## 🎯 使用AI助手

1. 打开浏览器访问应用（通常是 http://localhost:8000）
2. 进入"搜索公众号"页面
3. 在页面顶部看到AI助手卡片
4. 输入查询并发送

### 示例查询

| 输入 | AI行为 | 输出 |
|------|--------|------|
| 查询北京的天气 | 调用 weather 工具 | 北京天气: 晴朗，气温25°C |
| 计算 10+20*5 | 调用 calculator 工具 | 计算结果: 110 |
| 什么是Python | 调用 knowledge_base | Python是一种高级编程语言... |
| 你好 | 不调用工具 | 你好！我是AI助手... |

## 🔍 验证服务

```bash
# 检查MCP服务
curl http://localhost:8008/mcp

# 检查AI助手状态
curl http://localhost:8000/api/v1/ai/health

# 测试AI查询
curl -X POST http://localhost:8000/api/v1/ai/query \
  -H "Content-Type: application/json" \
  -d '{"query": "你好"}'
```

## 🐛 常见问题

### Q1: 端口被占用

```bash
# 查找占用进程
lsof -i :8008  # MCP服务
lsof -i :8000  # 主应用

# 终止进程
kill -9 <PID>
```

### Q2: AI服务未初始化

**错误**: "AI服务未初始化，请先启动MCP服务"

**解决**:
1. 确保MCP服务在运行
2. 在 `main.py` 中添加初始化代码
3. 重启主应用

### Q3: AI不调用工具

**原因**: 查询不够明确

**解决**: 使用更明确的指令
- ❌ "天气怎么样"
- ✅ "查询北京的天气"

## 📚 完整文档

- **使用指南**: `app/ai/mcp/前端AI助手集成完成.md`
- **启动文档**: `app/ai/mcp/启动MCP服务.md`
- **集成指南**: `app/ai/mcp/应用初始化集成指南.md`
- **总结文档**: `前端AI助手功能完成总结.md`

## 🎉 功能特性

✅ **智能工具选择** - AI自动决定是否调用工具  
✅ **精美UI** - 渐变背景、消息气泡、思考动画  
✅ **完整日志** - 全链路追踪，方便调试  
✅ **错误处理** - 友好的错误提示  
✅ **快捷示例** - 一键发送示例查询  

---

**更新时间**: 2025-12-29  
**状态**: ✅ 完全可用

