#!/bin/bash

echo "========================================"
echo "  终止运行中的应用实例"
echo "========================================"
echo ""

PORT=18000

# 查找占用端口的进程
echo "查找占用端口 ${PORT} 的进程..."
PIDS=$(lsof -ti:${PORT} 2>/dev/null)

if [ -z "$PIDS" ]; then
    echo "✓ 没有发现占用端口 ${PORT} 的进程"
else
    echo "发现以下进程:"
    lsof -i:${PORT}
    echo ""
    
    echo "正在终止进程..."
    echo "$PIDS" | xargs kill -9 2>/dev/null
    
    # 等待一下
    sleep 1
    
    # 再次检查
    if lsof -ti:${PORT} >/dev/null 2>&1; then
        echo "✗ 部分进程可能未能终止，请手动检查"
    else
        echo "✓ 所有进程已终止"
    fi
fi

# 清理锁文件
echo ""
echo "清理锁文件..."
LOCK_FILE="$HOME/Library/Application Support/WxPublicCrawler/app.lock"

if [ -f "$LOCK_FILE" ]; then
    rm "$LOCK_FILE"
    echo "✓ 锁文件已删除"
else
    echo "✓ 没有发现锁文件"
fi

echo ""
echo "========================================"
echo "  清理完成！"
echo "========================================"
echo ""
echo "现在可以重新启动应用了。"

