# MCP Server 日志查看指南

## 概述

MCP Server 的日志已经全面集成到项目的 loguru 日志系统中，所有日志都会统一输出到应用的日志文件和控制台。

## 修改内容

### 1. 日志统一化（`fastmcp_server.py`）

所有 `print()` 语句已替换为 `logger` 调用：

- **工具调用日志**：使用 `logger.info(f"[MCP工具] ...")` 格式
- **错误日志**：使用 `logger.error(f"[MCP工具] ...")` 格式
- **警告日志**：使用 `logger.warning(f"[MCP工具] ...")` 格式

示例：
```python
# 天气查询工具
logger.info(f"[MCP工具] 天气查询: {location}")

# 计算器工具
logger.info(f"[MCP工具] 计算器: {expression}")

# 公众号文章获取
logger.info(f"[MCP工具] 开始获取公众号文章: wx_public_id={wx_public_id}")
```

### 2. 子进程日志捕获（`server_manager.py`）

**开发环境（子进程模式）**：
- 创建两个守护线程分别读取 stdout 和 stderr
- stdout 输出为 `logger.info(f"[MCP-Server-stdout] ...")`
- stderr 输出为 `logger.warning(f"[MCP-Server-stderr] ...")`

**打包环境（线程模式）**：
- 日志直接通过 logger 输出，无需额外处理

### 3. 启动脚本日志优化（`run_server.py`）

- 移除了 print 语句
- 使用 `logger.bind(tag="MCP_SERVER")` 标记所有日志
- 添加了更详细的启动信息

## 日志查看方式

### 方式1：实时控制台输出

启动应用后，MCP Server 的所有日志会实时显示在控制台：

```bash
# 开发环境启动
python run_app.py

# 或使用 uvicorn 直接启动
uvicorn app.main:app --reload
```

**控制台日志示例**：
```
2026-01-07 10:30:45.123 | INFO     | [MCP_SERVER] 启动FastMCP服务器
2026-01-07 10:30:45.234 | INFO     | [MCP_SERVER] 服务器配置:
2026-01-07 10:30:45.345 | INFO     | [MCP_SERVER]   - 传输方式: streamable-http
2026-01-07 10:30:45.456 | INFO     | [MCP_SERVER]   - 地址: http://127.0.0.1:8008/mcp
2026-01-07 10:30:50.123 | INFO     | [MCP工具] 天气查询: 北京
2026-01-07 10:31:00.234 | INFO     | [MCP工具] 开始获取公众号文章: wx_public_id=123456
```

### 方式2：日志文件查看

所有日志会写入到项目的日志文件中：

**日志文件位置**：
- 运行日志：`logs/app_run/app_run_YYYY-MM-DD.log`
- 错误日志：`logs/app_error/app_error_YYYY-MM-DD.log`

**实时查看日志**：
```bash
# 查看今天的运行日志
tail -f logs/app_run/app_run_$(date +%Y-%m-%d).log

# 过滤 MCP 相关日志
tail -f logs/app_run/app_run_$(date +%Y-%m-%d).log | grep -i "mcp"

# 查看错误日志
tail -f logs/app_error/app_error_$(date +%Y-%m-%d).log
```

**搜索特定日志**：
```bash
# 搜索所有 MCP 工具调用
grep "[MCP工具]" logs/app_run/*.log

# 搜索天气查询日志
grep "天气查询" logs/app_run/*.log

# 搜索公众号文章获取日志
grep "获取公众号文章" logs/app_run/*.log
```

### 方式3：使用日志查看脚本

如果项目有日志查看脚本：
```bash
# 查看最新日志
./script/desktop/view_logs.sh

# 或直接查看日志目录
ls -lh logs/app_run/
ls -lh logs/app_error/
```

## 日志标签说明

| 标签 | 来源 | 说明 |
|------|------|------|
| `[MCP_SERVER]` | run_server.py | MCP Server 主进程日志 |
| `[MCP工具]` | fastmcp_server.py | MCP 工具调用日志 |
| `[MCP-Server-stdout]` | server_manager.py | 子进程标准输出（开发环境） |
| `[MCP-Server-stderr]` | server_manager.py | 子进程标准错误（开发环境） |

## 调试技巧

### 1. 查看 MCP Server 启动状态

```bash
# 检查端口是否被占用
lsof -ti :8008

# 查看最近的启动日志
grep "启动FastMCP服务器" logs/app_run/app_run_$(date +%Y-%m-%d).log | tail -5
```

### 2. 监控工具调用情况

```bash
# 实时监控所有工具调用
tail -f logs/app_run/app_run_$(date +%Y-%m-%d).log | grep "\[MCP工具\]"

# 统计今天的工具调用次数
grep -c "[MCP工具]" logs/app_run/app_run_$(date +%Y-%m-%d).log
```

### 3. 排查错误

```bash
# 查看所有 MCP 相关错误
grep -i "mcp" logs/app_error/*.log

# 查看最近的错误
tail -50 logs/app_error/app_error_$(date +%Y-%m-%d).log
```

## 打包环境说明

在打包后的可执行文件中：
- MCP Server 以**线程模式**运行在主进程中
- 所有日志直接通过 loguru 输出
- 日志位置与开发环境相同

## 注意事项

1. **日志级别**：默认为 INFO，可以在 `app/core/logging_uru.py` 中调整
2. **日志轮转**：日志文件按天分割，避免单个文件过大
3. **性能影响**：日志捕获使用守护线程，对性能影响极小
4. **编码问题**：使用 `utf-8` 解码，`errors='ignore'` 避免编码错误

## 相关文件

- `app/ai/mcp/mcp_server/server_manager.py` - MCP Server 管理器
- `app/ai/mcp/mcp_server/fastmcp_server.py` - MCP Server 实现
- `app/ai/mcp/mcp_server/run_server.py` - MCP Server 启动脚本
- `app/core/logging_uru.py` - 日志配置文件

