
// 自动生成的NPX桥接脚本 for baidu-map
// Package: @baidumap/mcp-server-baidu-map
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('[NPX Bridge] Starting @baidumap/mcp-server-baidu-map...');

// 首先确保包已安装
try {
    // 检查是否已安装
    require.resolve('@baidumap/mcp-server-baidu-map');
    console.log('[NPX Bridge] Package @baidumap/mcp-server-baidu-map is already installed');
} catch (e) {
    // 如果未安装，使用npx安装
    console.log('[NPX Bridge] Installing @baidumap/mcp-server-baidu-map...');
    execSync('npx -y @baidumap/mcp-server-baidu-map', { stdio: 'inherit' });
}

// 导入并运行包
try {
    require('@baidumap/mcp-server-baidu-map');
} catch (e) {
    console.error('[NPX Bridge] Failed to run @baidumap/mcp-server-baidu-map:', e);
    process.exit(1);
}
