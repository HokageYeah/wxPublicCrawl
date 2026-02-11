#!/bin/bash

# AI助手快速启动脚本
# 使用方法: bash script/start_ai_assistant.sh

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}          AI助手快速启动脚本${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 错误: 未找到虚拟环境 venv${NC}"
    echo -e "${YELLOW}请先创建虚拟环境: python3 -m venv venv${NC}"
    exit 1
fi

# 激活虚拟环境
echo -e "${BLUE}🔧 激活虚拟环境...${NC}"
source venv/bin/activate

# 检查MCP服务是否已运行
MCP_PID=$(lsof -ti:8008 2>/dev/null)
if [ -n "$MCP_PID" ]; then
    echo -e "${YELLOW}⚠️  端口8008已被占用 (PID: $MCP_PID)${NC}"
    echo -e "${YELLOW}   MCP服务可能已在运行${NC}"
else
    echo -e "${GREEN}✅ 端口8008可用${NC}"
fi

# 启动MCP服务器
echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}第1步: 启动MCP服务器${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

if [ -z "$MCP_PID" ]; then
    echo -e "${BLUE}🚀 正在启动MCP服务器...${NC}"
    python app/ai/mcp/mcp_server/run_server.py &
    MCP_SERVER_PID=$!
    
    # 等待服务启动
    echo -e "${YELLOW}⏳ 等待服务启动（5秒）...${NC}"
    sleep 5
    
    # 验证服务
    if curl -s http://localhost:8008/mcp > /dev/null 2>&1; then
        echo -e "${GREEN}✅ MCP服务器启动成功 (PID: $MCP_SERVER_PID)${NC}"
        echo -e "${GREEN}   地址: http://localhost:8008/mcp${NC}"
        
        # 保存PID到文件
        echo $MCP_SERVER_PID > /tmp/mcp_server.pid
    else
        echo -e "${RED}❌ MCP服务器启动失败${NC}"
        echo -e "${YELLOW}   请手动启动: python app/ai/mcp/mcp_server/run_server.py${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  跳过启动（服务已运行）${NC}"
fi

echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}第2步: 启动主应用${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# 检查主应用是否已运行
APP_PID=$(lsof -ti:8000 2>/dev/null)
if [ -n "$APP_PID" ]; then
    echo -e "${YELLOW}⚠️  端口8000已被占用 (PID: $APP_PID)${NC}"
    echo -e "${YELLOW}   主应用可能已在运行${NC}"
    echo ""
    read -p "是否停止并重启？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🔄 停止现有应用...${NC}"
        kill $APP_PID
        sleep 2
    else
        echo -e "${YELLOW}保持现有应用运行${NC}"
        exit 0
    fi
fi

echo -e "${BLUE}🚀 启动主应用...${NC}"
echo -e "${YELLOW}   注意: 请确保在 main.py 中已添加 AI助手初始化代码${NC}"
echo -e "${YELLOW}   参考文档: app/ai/mcp/应用初始化集成指南.md${NC}"
echo ""

# 启动主应用
python app/main.py

# 或者使用 run_desktop.py
# python run_desktop.py

# 清理函数
cleanup() {
    echo ""
    echo -e "${YELLOW}🔄 清理资源...${NC}"
    
    # 停止MCP服务
    if [ -f /tmp/mcp_server.pid ]; then
        MCP_PID=$(cat /tmp/mcp_server.pid)
        if ps -p $MCP_PID > /dev/null 2>&1; then
            echo -e "${YELLOW}   停止MCP服务器 (PID: $MCP_PID)...${NC}"
            kill $MCP_PID 2>/dev/null
        fi
        rm /tmp/mcp_server.pid
    fi
    
    echo -e "${GREEN}✅ 清理完成${NC}"
}

# 捕获退出信号
trap cleanup EXIT INT TERM

# 如果主应用正常退出，执行清理
cleanup

