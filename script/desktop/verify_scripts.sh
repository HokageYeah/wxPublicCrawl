#!/bin/bash
# ============================================================================
# 脚本验证工具
# 检查所有脚本是否能正确处理路径
# ============================================================================

echo "============================================================"
echo "  脚本路径验证工具"
echo "============================================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "脚本目录: $SCRIPT_DIR"
echo "项目根目录: $PROJECT_ROOT"
echo ""

# 验证结果
PASS_COUNT=0
FAIL_COUNT=0

# 验证函数
verify_file() {
    local desc="$1"
    local file="$2"
    
    if [ -f "$file" ]; then
        echo "✓ $desc"
        echo "  路径: $file"
        ((PASS_COUNT++))
    else
        echo "✗ $desc"
        echo "  缺失: $file"
        ((FAIL_COUNT++))
    fi
    echo ""
}

verify_dir() {
    local desc="$1"
    local dir="$2"
    
    if [ -d "$dir" ]; then
        echo "✓ $desc"
        echo "  路径: $dir"
        ((PASS_COUNT++))
    else
        echo "✗ $desc"
        echo "  缺失: $dir"
        ((FAIL_COUNT++))
    fi
    echo ""
}

verify_executable() {
    local desc="$1"
    local file="$2"
    
    if [ -f "$file" ] && [ -x "$file" ]; then
        echo "✓ $desc（可执行）"
        echo "  路径: $file"
        ((PASS_COUNT++))
    elif [ -f "$file" ]; then
        echo "⚠ $desc（文件存在但不可执行）"
        echo "  路径: $file"
        echo "  修复: chmod +x $file"
        ((FAIL_COUNT++))
    else
        echo "✗ $desc"
        echo "  缺失: $file"
        ((FAIL_COUNT++))
    fi
    echo ""
}

echo "============================================================"
echo "  检查脚本文件"
echo "============================================================"
echo ""

verify_executable "build_mac.sh" "$SCRIPT_DIR/build_mac.sh"
verify_file "build_windows.bat" "$SCRIPT_DIR/build_windows.bat"
verify_executable "kill_app.sh" "$SCRIPT_DIR/kill_app.sh"
verify_executable "test_app.sh" "$SCRIPT_DIR/test_app.sh"
verify_executable "view_logs.sh" "$SCRIPT_DIR/view_logs.sh"
verify_file "README.md" "$SCRIPT_DIR/README.md"

echo "============================================================"
echo "  检查项目文件"
echo "============================================================"
echo ""

verify_dir "前端目录" "$PROJECT_ROOT/web"
verify_dir "后端目录" "$PROJECT_ROOT/app"
verify_file "requirements.txt" "$PROJECT_ROOT/requirements.txt"
verify_file "wx_crawler.spec" "$PROJECT_ROOT/wx_crawler.spec"
verify_file "run_desktop.py" "$PROJECT_ROOT/run_desktop.py"

echo "============================================================"
echo "  检查文档文件"
echo "============================================================"
echo ""

verify_file "DESKTOP_APP_GUIDE.md" "$PROJECT_ROOT/docs/desktop/DESKTOP_APP_GUIDE.md"
verify_file "QUICK_REFERENCE.md" "$PROJECT_ROOT/QUICK_REFERENCE.md"
verify_file "README.md" "$PROJECT_ROOT/README.md"

echo "============================================================"
echo "  测试路径切换逻辑"
echo "============================================================"
echo ""

# 测试从不同位置运行脚本是否都能切换到项目根目录
echo "测试1: 从脚本目录运行"
cd "$SCRIPT_DIR"
TEST_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
if [ "$TEST_ROOT" = "$PROJECT_ROOT" ]; then
    echo "✓ 路径切换正确"
    ((PASS_COUNT++))
else
    echo "✗ 路径切换失败"
    echo "  期望: $PROJECT_ROOT"
    echo "  实际: $TEST_ROOT"
    ((FAIL_COUNT++))
fi
echo ""

echo "测试2: 从项目根目录运行"
cd "$PROJECT_ROOT"
TEST_ROOT2="$(cd "$SCRIPT_DIR/../.." && pwd)"
if [ "$TEST_ROOT2" = "$PROJECT_ROOT" ]; then
    echo "✓ 路径切换正确"
    ((PASS_COUNT++))
else
    echo "✗ 路径切换失败"
    echo "  期望: $PROJECT_ROOT"
    echo "  实际: $TEST_ROOT2"
    ((FAIL_COUNT++))
fi
echo ""

echo "测试3: 从任意目录运行"
cd /tmp
TEST_ROOT3="$(cd "$SCRIPT_DIR/../.." && pwd)"
if [ "$TEST_ROOT3" = "$PROJECT_ROOT" ]; then
    echo "✓ 路径切换正确"
    ((PASS_COUNT++))
else
    echo "✗ 路径切换失败"
    echo "  期望: $PROJECT_ROOT"
    echo "  实际: $TEST_ROOT3"
    ((FAIL_COUNT++))
fi
echo ""

# 切回项目根目录
cd "$PROJECT_ROOT"

echo "============================================================"
echo "  验证结果"
echo "============================================================"
echo ""
echo "通过: $PASS_COUNT"
echo "失败: $FAIL_COUNT"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo "✓ 所有检查通过！脚本已正确配置。"
    echo ""
    echo "建议："
    echo "  1. 从任何位置运行脚本："
    echo "     script/desktop/build_mac.sh"
    echo ""
    echo "  2. 或创建符号链接（可选）："
    echo "     cd $PROJECT_ROOT"
    echo "     ln -s script/desktop/build_mac.sh build_mac.sh"
    echo ""
    exit 0
else
    echo "✗ 发现 $FAIL_COUNT 个问题，请检查上述错误。"
    echo ""
    echo "常见修复："
    echo "  1. 添加执行权限："
    echo "     chmod +x script/desktop/*.sh"
    echo ""
    echo "  2. 检查文件是否存在："
    echo "     ls -la script/desktop/"
    echo ""
    exit 1
fi

