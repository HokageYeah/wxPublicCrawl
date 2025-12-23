#!/bin/bash
set -e

echo "======================================"
echo "  公众号爬虫助手 - Mac 打包脚本"
echo "======================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 检查 Python 版本
echo -e "${YELLOW}[1/8] 检查 Python 版本...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 python3，请先安装 Python 3.9+${NC}"
    exit 1
fi
python3 --version
echo -e "${GREEN}✓ Python 版本检查通过${NC}"
echo ""

# 2. 检查 Node.js
echo -e "${YELLOW}[2/8] 检查 Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: 未找到 node，请先安装 Node.js${NC}"
    exit 1
fi
node --version
npm --version
echo -e "${GREEN}✓ Node.js 检查通过${NC}"
echo ""

# 3. 检查虚拟环境
echo -e "${YELLOW}[3/8] 检查 Python 虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
else
    echo -e "${GREEN}✓ 虚拟环境已存在${NC}"
fi
echo ""

# 4. 激活虚拟环境并安装 Python 依赖
echo -e "${YELLOW}[4/8] 安装 Python 依赖...${NC}"
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install pyinstaller pywebview -q
echo -e "${GREEN}✓ Python 依赖安装完成${NC}"
echo ""

# 5. 构建前端
echo -e "${YELLOW}[5/8] 构建前端...${NC}"
cd web

if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

echo "构建前端项目..."
npm run build:only

if [ ! -d "dist" ]; then
    echo -e "${RED}错误: 前端构建失败，dist 目录不存在${NC}"
    cd ..
    exit 1
fi

cd ..
echo -e "${GREEN}✓ 前端构建完成${NC}"
echo ""

# 6. 清理旧的打包文件
echo -e "${YELLOW}[6/8] 清理旧的打包文件...${NC}"
# 先尝试修改权限再删除
if [ -d "dist" ]; then
    chmod -R 755 dist 2>/dev/null || true
fi
rm -rf build dist 2>/dev/null || {
    echo -e "${YELLOW}警告: 无法完全删除旧文件，请手动删除 dist 目录后重试${NC}"
    echo "  手动删除: chmod -R 755 dist && rm -rf dist"
    exit 1
}
echo -e "${GREEN}✓ 清理完成${NC}"
echo ""

# 7. 打包应用
echo -e "${YELLOW}[7/8] 开始打包应用...${NC}"
echo "这可能需要几分钟时间，请耐心等待..."
pyinstaller wx_crawler.spec

if [ ! -d "dist/wx公众号工具.app " ]; then
    echo -e "${RED}错误: 打包失败，应用文件不存在${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 应用打包完成${NC}"
echo ""

# 8. 移除隔离属性（避免 Mac 安全警告）
echo -e "${YELLOW}[8/8] 处理 Mac 安全属性...${NC}"
xattr -cr dist/wx公众号工具.app  2>/dev/null || true
echo -e "${GREEN}✓ 安全属性处理完成${NC}"
echo ""

# 完成
echo "======================================"
echo -e "${GREEN}  ✓ 打包成功！${NC}"
echo "======================================"
echo ""
echo "应用位置: dist/wx公众号工具.app "
echo ""
echo "测试运行:"
echo "  open dist/wx公众号工具.app "
echo ""
echo "创建分发包:"
echo "  # 方式 1: ZIP 压缩包"
echo "  cd dist && zip -r wx公众号工具-mac.zip wx公众号工具.app "
echo ""
echo "  # 方式 2: DMG 安装包（需要安装 create-dmg）"
echo "  create-dmg --volname 'wx公众号工具' --window-pos 200 120 --window-size 800 400 --icon-size 100 --icon 'wx公众号工具.app ' 200 190 --hide-extension 'wx公众号工具.app ' --app-drop-link 600 185 'wx公众号工具.dmg' 'dist/'"
echo ""

