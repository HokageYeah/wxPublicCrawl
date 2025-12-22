#!/bin/bash
# ============================================================================
# 脚本名称: test_app.sh  
# 功能说明: 快速测试打包后的桌面应用
# ============================================================================

# ============================================================================
# 自动切换到项目根目录
# ============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "============================================================"
echo "  测试打包后的桌面应用"
echo "============================================================"
echo "项目目录: $PROJECT_ROOT"
echo ""

# 1. 检查打包文件是否存在
if [ ! -f "dist/WxPublicCrawler/WxPublicCrawler" ]; then
    echo "❌ 打包文件不存在！"
    echo "   请先运行: script/desktop/build_mac.sh"
    exit 1
fi

echo "✓ 找到打包文件"
echo ""

# 2. 清理旧实例
echo "[1/3] 清理旧实例..."
"$SCRIPT_DIR/kill_app.sh" > /dev/null 2>&1
echo "✓ 完成"
echo ""

# 3. 启动应用（后台）
echo "[2/3] 启动应用..."
"$PROJECT_ROOT/dist/WxPublicCrawler/WxPublicCrawler" > /tmp/wx_test.log 2>&1 &
APP_PID=$!
echo "✓ 应用已启动 (PID: $APP_PID)"
echo ""

# 4. 等待应用启动
echo "[3/3] 等待应用启动..."
sleep 3

# 5. 检查应用是否在运行
if ps -p $APP_PID > /dev/null; then
    echo "✓ 应用正在运行"
    echo ""
    
    # 显示应用信息
    echo "============================================================"
    echo "  应用信息"
    echo "============================================================"
    echo "进程 ID: $APP_PID"
    echo "访问地址: http://127.0.0.1:18000"
    echo "日志文件: /tmp/wx_test.log"
    echo ""
    
    # 显示日志前20行
    echo "============================================================"
    echo "  启动日志（前20行）"
    echo "============================================================"
    head -20 /tmp/wx_test.log
    echo ""
    echo "============================================================"
    
    echo ""
    echo "📊 查看完整日志："
    echo "   tail -f /tmp/wx_test.log"
    echo ""
    echo "📊 查看标准日志："
    echo "   script/desktop/view_logs.sh"
    echo ""
    echo "🌐 在浏览器打开："
    echo "   open http://127.0.0.1:18000/crawl-desktop/"
    echo ""
    echo "🛑 停止应用："
    echo "   script/desktop/kill_app.sh"
    echo "   或"
    echo "   kill $APP_PID"
    echo ""
else
    echo "❌ 应用启动失败！"
    echo ""
    echo "错误日志："
    echo "----------------------------------------"
    cat /tmp/wx_test.log
    echo "----------------------------------------"
    exit 1
fi

